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

from MonkTrader.exchange.bitmex.instrument import Instrument
import datetime
import pytz

xbt = {'symbol': 'XBTUSD', 'rootSymbol': 'XBT', 'state': 'Open', 'typ': 'FFWCSX', 'listing': datetime.datetime(2016,5,13,12, tzinfo=pytz.UTC),
       'front': datetime.datetime(2016,5,13,12, tzinfo=pytz.UTC), 'expiry': None, 'settle': None, 'positionCurrency': 'USD',
       'underlying': 'XBT', 'quoteCurrency': 'USD', 'underlyingSymbol': 'XBT=', 'multiplier': -100000000,
       'settlCurrency': 'XBt', 'initMargin': 0.01, 'maintMargin': 0.005, 'makerFee': -0.00025, 'takerFee': 0.00075,
       'settlementFee': 0, 'insuranceFee': 0}


def test_perpetual_future_instrument():
    xbt_instrument = Instrument(**xbt)
    assert xbt_instrument.symbol == "XBTUSD"
    assert xbt_instrument.rootSymbol == 'XBT'
    assert xbt_instrument.state == "Open"
    assert xbt_instrument.typ == "FFWCSX"
    assert xbt_instrument.listing == datetime.datetime(2016,5,13,12,tzinfo=pytz.UTC)
    assert xbt_instrument.front == datetime.datetime(2016,5,13,12, tzinfo=pytz.UTC)
    assert xbt_instrument.expiry is None
    assert xbt_instrument.settle is None
    assert xbt_instrument.positionCurrency == "USD"
    assert xbt_instrument.underlying == "XBT"
    assert xbt_instrument.quoteCurrency == "USD"
    assert xbt_instrument.underlyingSymbol == "XBT="
    assert xbt_instrument.multiplier == -100000000
    assert xbt_instrument.settlCurrency == "XBt"
    assert xbt_instrument.initMargin == 0.01
    assert xbt_instrument.maintMargin == 0.005
    assert xbt_instrument.makerFee == -0.00025
    assert xbt_instrument.takerFee == 0.00075
    assert xbt_instrument.settlementFee == 0
    assert xbt_instrument.insuranceFee == 0

def test_future_instrument():
    pass

def test_normal_instrument():
    pass