#
# MIT License
#
# Copyright (c) 2018 WillQ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import asyncio
import ssl
from typing import TYPE_CHECKING, Dict, List, Optional, TypeVar, ValuesView

import pandas
from aiohttp import ClientSession, TCPConnector, TraceConfig  # type:ignore
from aiohttp.helpers import sentinel
from logbook import Logger
from monkq.assets.account import FutureAccount, RealFutureAccount
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.assets.order import ORDER_T, FutureLimitOrder, FutureMarketOrder
from monkq.exchange.base import BaseExchange, BaseSimExchange
from monkq.exchange.base.info import ExchangeInfo
from monkq.exchange.bitmex.const import (
    BITMEX_TESTNET_WEBSOCKET_URL, BITMEX_WEBSOCKET_URL,
)
from monkq.exchange.bitmex.data.loader import BitmexDataloader
from monkq.exchange.bitmex.data.utils import kline_from_list_of_dict
from monkq.exchange.bitmex.http import BitMexHTTPInterface
from monkq.exchange.bitmex.websocket import BitmexWebsocket
from monkq.tradecounter import TradeCounter
from monkq.utils.as_dict import base_order_to_dict
from monkq.utils.id import gen_unique_id

from .log import logger_group

if TYPE_CHECKING:
    from monkq.context import Context


logger = Logger('exchange.bitmex.exchange')
logger_group.add_logger(logger)
T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")

bitmex_info = ExchangeInfo(name="bitmex",
                           location="unknown",
                           info="famous exchange")


class BitmexSimulateExchange(BaseSimExchange):
    def __init__(self, context: "Context", name: str, exchange_setting: dict) -> None:
        super(BitmexSimulateExchange, self).__init__(context, name, exchange_setting)
        data_dir = context.settings.DATA_DIR  # type:ignore
        self._data = BitmexDataloader(self, context, data_dir)
        self._trade_counter: TradeCounter = context.trade_counter

    def all_data(self, instrument: Instrument) -> pandas.DataFrame:
        return self._data.all_data(instrument)

    async def setup(self) -> None:
        return

    async def get_last_price(self, instrument: FutureInstrument) -> float:
        return self._data.get_last_price(instrument)

    def last_price(self, instrument: FutureInstrument) -> float:
        return self._data.get_last_price(instrument)

    def exchange_info(self) -> ExchangeInfo:
        return bitmex_info

    async def place_limit_order(self, account: FutureAccount, instrument: FutureInstrument,
                                price: float, quantity: float) -> str:
        if isinstance(instrument, FutureInstrument):
            order = FutureLimitOrder(account=account, instrument=instrument, price=price, quantity=quantity,
                                     order_id=gen_unique_id())
        else:
            raise NotImplementedError()
        self._trade_counter.submit_order(order)
        return order.order_id

    async def place_market_order(self, account: FutureAccount, instrument: FutureInstrument,
                                 quantity: float) -> str:
        if isinstance(instrument, FutureInstrument):
            order = FutureMarketOrder(account=account, instrument=instrument, quantity=quantity,
                                      order_id=gen_unique_id())
        else:
            raise NotImplementedError()
        self._trade_counter.submit_order(order)
        return order.order_id

    # TODO
    async def amend_order(self, account: FutureAccount, order_id: str, quantity: Optional[float],
                          price: Optional[float]) -> bool:
        raise NotImplementedError()

    async def cancel_order(self, account: FutureAccount, order_id: str) -> bool:
        self._trade_counter.cancel_order(order_id)
        return True

    async def open_orders(self, account: FutureAccount) -> List[dict]:
        outcome = []
        open_orders: ValuesView[ORDER_T] = self._trade_counter.open_orders()
        order: ORDER_T
        for order in open_orders:
            outcome.append(base_order_to_dict(order))
        return outcome

    async def available_instruments(self) -> ValuesView["Instrument"]:
        active_instruments = self._data.active_instruments()
        return active_instruments.values()

    async def get_kline(self, instrument: FutureInstrument,
                        count: int = 100, including_now: bool = False) -> pandas.DataFrame:
        return self._data.get_kline(instrument, count)

    def match_open_orders(self) -> None:
        self._trade_counter.match()

    def get_open_orders(self, account: FutureAccount) -> List[ORDER_T]:
        return list(self._trade_counter.open_orders())


class BitmexExchange(BaseExchange):
    INSTRUMENT_KEY_MAP = {
        'symbol': 'symbol',
        'listing': 'listing_date',
        'expiry': 'expiry_date',
        'underlying': 'underlying',
        "quoteCurrency": 'quote_currency',
        'lotSize': 'lot_size',
        'tickSize': 'tick_size',
        'makerFee': 'maker_fee',
        'takerFee': 'taker_fee',

        'initMargin': 'init_margin_rate',
        'maintMargin': 'maint_margin_rate',

        'settlementFee': 'settlement_fee',
        'settlCurrency': 'settle_currency',

        'settle': 'settle_date',
        'front': 'front_date',
        'referenceSymbol': 'reference_symbol',
        'deleverage': 'deleverage',

        'rootSymbol': 'root_symbol'
    }

    def __init__(self, context: "Context", name: str, exchange_setting: dict,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        :param exchange_setting:
        example:
        {
            'engine': 'monkq.exchange.bitmex',
            "IS_TEST": True,
            "API_KEY": '',
            "API_SECRET": ''
        }
        """
        super(BitmexExchange, self).__init__(context=context, name=name,
                                             exchange_setting=exchange_setting)
        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()
        if self.exchange_setting['IS_TEST']:
            ws_url = BITMEX_TESTNET_WEBSOCKET_URL
        else:
            ws_url = BITMEX_WEBSOCKET_URL

        self._trace_config = TraceConfig()
        self._ssl = ssl.create_default_context()
        if context.settings.SSL_PATH:  # type:ignore
            self._ssl.load_verify_locations(context.settings.SSL_PATH)  # type:ignore

        self.api_key = exchange_setting.get("API_KEY", '')
        self.api_secret = exchange_setting.get("API_SECRET", '')

        self._available_instrument_cache: Dict[str, Instrument] = {}

        self._connector = TCPConnector(keepalive_timeout=90)  # type:ignore
        self.session = ClientSession(trace_configs=[self._trace_config],
                                     loop=self._loop,
                                     connector=self._connector)

        self.ws = BitmexWebsocket(strategy=context.strategy, loop=self._loop,
                                  session=self.session, ws_url=ws_url,
                                  api_key=self.api_key, api_secret=self.api_secret,
                                  ssl=self._ssl, http_proxy=None)
        proxy = self.context.settings.HTTP_PROXY or None  # type:ignore

        self.http_interface = BitMexHTTPInterface(exchange_setting, self._connector,
                                                  self.session, self._ssl, proxy, loop)

    async def setup(self) -> None:
        await self.ws.setup()

    async def close(self) -> None:
        await self.session.close()

    async def get_last_price(self, instrument: FutureInstrument,
                             timeout: int = sentinel, max_retry: int = 0) -> float:
        content = await self.http_interface.get_instrument_info(instrument.symbol, timeout, max_retry)
        try:
            one = content[0]
            last_price = one['lastPrice']
            return last_price
        except IndexError:
            return 0

    def exchange_info(self) -> ExchangeInfo:
        return bitmex_info

    async def place_limit_order(self, account: RealFutureAccount, instrument: FutureInstrument,
                                price: float, quantity: float, timeout: int = sentinel,
                                max_retry: int = 0) -> str:
        target = instrument.symbol
        return await self.http_interface.place_limit_order(account.api_key, target, price, quantity, timeout,
                                                           max_retry)

    async def place_market_order(self, account: RealFutureAccount, instrument: FutureInstrument,
                                 quantity: float, timeout: int = sentinel,
                                 max_retry: int = 0) -> str:
        target = instrument.symbol

        return await self.http_interface.place_market_order(account.api_key, target, quantity, timeout, max_retry)

    async def amend_order(self, account: RealFutureAccount, order_id: str, quantity: Optional[float] = None,
                          price: Optional[float] = None, timeout: int = sentinel,
                          max_retry: int = 0) -> bool:

        resp = await self.http_interface.amend_order(account.api_key, order_id, quantity, price, timeout, max_retry)
        if 300 > resp.status >= 200:
            return True
        else:
            return False

    async def cancel_order(self, account: RealFutureAccount, order_id: str, timeout: int = sentinel,
                           max_retry: int = 0) -> bool:

        resp = await self.http_interface.cancel_order(account.api_key, order_id, timeout, max_retry)
        if 300 > resp.status >= 200:
            return True
        else:
            return False

    async def open_orders(self, account: RealFutureAccount) -> List[dict]:
        return await self.http_interface.open_orders_http(account.api_key)

    async def available_instruments(self, timeout: int = sentinel) -> ValuesView[Instrument]:
        if self._available_instrument_cache:
            return self._available_instrument_cache.values()
        contents = await self.http_interface.active_instruments(timeout)
        for one in contents:
            instrument = FutureInstrument.create(self.INSTRUMENT_KEY_MAP, one, self)
            self._available_instrument_cache[instrument.symbol] = instrument
        return self._available_instrument_cache.values()

    async def get_kline(self, instrument: FutureInstrument, count: int = 100, including_now: bool = False,
                        timeout: int = sentinel, max_retry: int = 5) -> pandas.DataFrame:

        klines_list = await self.http_interface.get_kline(instrument.symbol, "1m", count, including_now, timeout,
                                                          max_retry)
        return kline_from_list_of_dict(klines_list)

    async def get_recent_trades(self, instrument: FutureInstrument,
                                count: int = 100, timeout: int = sentinel,
                                max_retry: int = 5) -> List[dict]:
        return await self.http_interface.get_recent_trades(instrument.symbol, count, timeout, max_retry)
