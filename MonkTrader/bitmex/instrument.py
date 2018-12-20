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
from dataclasses import dataclass
from dateutil.parser import parse
from MonkTrader.config import CONF

import datetime


@dataclass
class Instrument():
    symbol: str
    rootSymbol: str
    state: str
    typ: str # unknown
    listing: datetime.datetime
    front: datetime.datetime
    expiry: datetime.datetime
    settle: datetime.datetime
    positionCurrency: str
    underlying: str
    quoteCurrency: str
    underlyingSymbol: str
    multiplier: int
    settlCurrency: str
    initMargin: float
    maintMargin: float
    makerFee: float
    takerFee: float
    settlementFee: float
    insuranceFee: float

    mongo_projection = {
        "symbol",
        "rootSymbol",
        "state",
        "typ",
        "listing",
        "front",
        "expiry",
        "settle",
        "positionCurrency",
        "underlying",
        "quoteCurrency",
        "underlyingSymbol",
        "multiplier",
        "settlCurrency",
        "initMargin",
        "maintMargin",
        "makerFee",
        "takerFee",
        "settlementFee",
        "insuranceFee"
    }


p = {i:1 for i in Instrument.mongo_projection}
p.update({"_id":0})
xbt_symbol = CONF.db['bitmex']['symbols'].find_one({"symbol":"XBTUSD"},p)
XBT_SYMBOL = Instrument(**xbt_symbol)