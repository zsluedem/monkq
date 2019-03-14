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
import datetime
from typing import Generator, TypeVar

import pytest
from dateutil.tz import tzutc
from monkq.assets.account import BaseAccount, FutureAccount
from monkq.assets.instrument import FutureInstrument, Instrument
from monkq.assets.positions import BasePosition, FuturePosition
from monkq.exchange.base import (  # noqa: F401
    BaseExchange, BaseSimExchange,
)

T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")
T_EXCHANGE = TypeVar('T_EXCHANGE', bound="BaseSimExchange")


@pytest.fixture()
def base_account(exchange: T_EXCHANGE) -> Generator[BaseAccount, None, None]:
    yield BaseAccount(exchange=exchange, position_cls=BasePosition)


@pytest.fixture()
def future_account(exchange: T_EXCHANGE) -> Generator[FutureAccount, None, None]:
    yield FutureAccount(exchange=exchange, position_cls=FuturePosition)


@pytest.fixture()
def instrument(exchange: T_EXCHANGE) -> Generator[Instrument, None, None]:
    yield Instrument(
        symbol="TRXH19",
        listing_date=datetime.datetime(2018, 12, 12, 6, tzinfo=tzutc()),
        expiry_date=datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc()),
        underlying="TRX",
        quote_currency="XBT",
        lot_size=1,
        tick_size=1e-8,
        maker_fee=-0.0005,
        taker_fee=0.0025,
        exchange=exchange
    )


@pytest.fixture()
def future_instrument(exchange: T_EXCHANGE) -> Generator[FutureInstrument, None, None]:
    yield FutureInstrument(
        symbol="TRXH19",
        root_symbol="TRX",

        listing_date=datetime.datetime(2018, 12, 12, 6, tzinfo=tzutc()),
        expiry_date=datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc()),
        underlying="TRX",
        quote_currency="XBT",
        lot_size=1,
        tick_size=1e-8,
        maker_fee=-0.0005,
        taker_fee=0.0025,
        exchange=exchange,

        init_margin_rate=0.05,
        maint_margin_rate=0.025,
        settlement_fee=0,
        settle_currency="XBt",
        front_date=datetime.datetime(2019, 2, 22, 12, tzinfo=tzutc()),
        settle_date=datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc()),
        reference_symbol=".TRXXBT30M",
        deleverage=True,
    )


@pytest.fixture()
def future_instrument2(exchange: T_EXCHANGE) -> Generator[FutureInstrument, None, None]:
    yield FutureInstrument(
        symbol="XBTUSD",
        root_symbol="XBT",

        listing_date=datetime.datetime(2016, 5, 4, 12, tzinfo=tzutc()),
        expiry_date=None,
        underlying="XBT",
        quote_currency="USD",
        lot_size=1,
        tick_size=0.5,
        maker_fee=-0.00025,
        taker_fee=0.00075,
        exchange=exchange,

        init_margin_rate=0.01,
        maint_margin_rate=0.005,
        settlement_fee=0,
        settle_currency="XBt",
        front_date=datetime.datetime(2016, 5, 4, 12, tzinfo=tzutc()),
        settle_date=None,
        reference_symbol=".BXBT",
        deleverage=True,
    )
