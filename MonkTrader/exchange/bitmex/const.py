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

from enum import Enum


class CommissionType(Enum):
    MAKER = 1
    TAKER = 2


class PositionDirection(Enum):
    LONG = 1
    SHORT = 2


class Side(Enum):
    BUY = 1
    SELL = 2


class OrderType(Enum):
    LIMIT = 1
    MARKET = 2
    # MarketWithLeftOverAsLimit = 3
    # STOP = 4
    # StopLimit = 5
    # MarketIfTouched = 6
    # LimitIfTouched = 7


Bitmex_api_url = "https://www.bitmex.com/api/v1/"
Bitmex_websocket_url = "wss://www.bitmex.com/realtime"
Bitmex_testnet_api_url = "https://testnet.bitmex.com/api/v1/"
Bitmex_testnet_websocket_url = "wss://testnet.bitmex.com/realtime"