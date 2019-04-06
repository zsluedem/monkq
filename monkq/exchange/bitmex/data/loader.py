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

import json
import os
from typing import TYPE_CHECKING, Dict, Type

import pandas
from logbook import Logger
from monkq.assets.instrument import (
    CallOptionInstrument, FutureInstrument, Instrument, PerpetualInstrument,
    PutOptionInstrument,
)
from monkq.data import DataLoader
from monkq.exception import LoadDataError
from monkq.exchange.bitmex.const import INSTRUMENT_FILENAME, KLINE_FILE_NAME
from monkq.lazyhdf import LazyHDFTableStore
from monkq.utils.dataframe import kline_dataframe_window, make_datetime_exactly
from monkq.utils.i18n import _

from ..log import logger_group

if TYPE_CHECKING:
    from monkq.context import Context
    from monkq.exchange.bitmex.exchange import BitmexSimulateExchange  # pragma: no cover

logger = Logger('exchange.bitmex.dataloader')
logger_group.add_logger(logger)

instrument_map = {
    'symbol': 'symbol',
    "rootSymbol": 'root_symbol',
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
    'deleverage': 'deleverage'
}


class BitmexDataloader(DataLoader):
    instrument_cls: Dict[str, Type[Instrument]] = {
        'OPECCS': PutOptionInstrument,  # put options
        'OCECCS': CallOptionInstrument,  # call options
        'FFCCSX': FutureInstrument,  # normal futures contracts
        'FFWCSX': PerpetualInstrument,  # perpetual  futures contracts
        'FXXXS': FutureInstrument,
        'FFICSX': FutureInstrument,
        'FMXXS': FutureInstrument
    }

    # abandon typ in Bitmex
    # https://www.onixs.biz/fix-dictionary/4.4/app_6_d.html
    # below are all index like instrument
    _abandon_instrument_type = ('MRIXXX', 'MRRXXX', 'MRCXXX')

    def __init__(self, exchange: 'BitmexSimulateExchange', context: "Context", data_dir: str) -> None:
        self.data_dir = data_dir
        self.instruments: Dict[str, Instrument] = dict()
        self.exchange = exchange
        self.context = context
        self.trade_data: Dict = dict()
        self._kline_store = LazyHDFTableStore(os.path.join(data_dir, KLINE_FILE_NAME))

        self.load_instruments()

    def load_instruments(self) -> None:
        logger.debug("Now loading the instruments data.")
        instruments_file = os.path.join(self.data_dir, INSTRUMENT_FILENAME)
        with open(instruments_file) as f:
            instruments_raw = json.load(f)
        for instrument_raw in instruments_raw:
            if instrument_raw['typ'] in self._abandon_instrument_type:
                continue
            instrument_cls = self.instrument_cls.get(instrument_raw['typ'])
            if instrument_cls is None:
                raise LoadDataError(_("Unsupport instrument type {}").format(instrument_raw['typ']))
            instrument = instrument_cls.create(instrument_map, instrument_raw, self.exchange)
            self.instruments[instrument.symbol] = instrument
        logger.debug("Now loading the instruments data.")

    def active_instruments(self) -> Dict[str, Instrument]:
        active = {}
        for instrument in self.instruments.values():
            if instrument.expiry_date is None:
                active[instrument.symbol] = instrument
                continue
            if instrument.listing_date is None:
                continue
            if instrument.listing_date < self.context.now and instrument.expiry_date > self.context.now:
                active[instrument.symbol] = instrument
        return active

    def get_last_price(self, instrument: Instrument) -> float:
        kline = self._kline_store.get(instrument.symbol)
        time_target = make_datetime_exactly(self.context.now, "T", forward=False)
        try:
            bar = kline.loc[time_target - kline.index.freq.delta]
            return bar['close']
        except KeyError:
            logger.warning(_("Instrument {} on {} has no bar data., Use 0 as last price"
                             .format(instrument.symbol, self.context.now)))
            return 0.0

    def get_kline(self, instrument: "Instrument",
                  count: int) -> pandas.DataFrame:
        kline_frame = self._kline_store.get(instrument.symbol)
        target_klines = kline_dataframe_window(kline_frame, self.context.now, count)
        return target_klines

    def all_data(self, instrument: "Instrument") -> pandas.DataFrame:
        return self._kline_store.get(instrument.symbol)