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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from MonkTrader.assets import AbcExchange
from MonkTrader.assets.instrument import Instrument, FutureInstrument



class MockExchange(AbcExchange):
    def withdraw(self):
        pass

    def deposit(self):
        pass

    def exchange_info(self):
        pass

    def order_book(self):
        pass

    def get_account(self):
        pass

    def place_limit_order(self):
        pass

    def place_market_order(self):
        pass

    def place_stop_limit_order(self):
        pass

    def place_stop_market_order(self):
        pass

    def open_orders(self):
        pass

    def cancel_order(self):
        pass

    def available_instruments(self):
        pass

    def setup(self):
        pass

exchange = MockExchange()

instrument = Instrument(**{
    "symbol": "TRXH19",
    "listing_date": "2018-12-12T06:00:00.000Z",
    "expiry_date": "2019-03-29T12:00:00.000Z",
    "underlying": "TRX",
    "quote_currency": "XBT",
    "lot_size": 1,
    "tick_size": 1e-8,
    "maker_fee": -0.0005,
    "taker_fee": 0.0025,
    "exchange": exchange
})

future_instrument = FutureInstrument(**{
    "symbol": "TRXH19",
    "root_symbol": "TRX",

    "listing_date": "2018-12-12T06:00:00.000Z",
    "expiry_date": "2019-03-29T12:00:00.000Z",
    "underlying": "TRX",
    "quote_currency": "XBT",
    "lot_size": 1,
    "tick_size": 1e-8,
    "maker_fee": -0.0005,
    "taker_fee": 0.0025,
    "exchange": exchange,

    "init_margin": 0.05,
    "maint_margin": 0.025,
    "settlement_fee": 0,
    "settle_currency": "XBt",
    "front_date": "2019-02-22T12:00:00.000Z",
    "settle_date": "2019-03-29T12:00:00.000Z",
    "reference_symbol": ".TRXXBT30M",
    "deleverage": True,
})
