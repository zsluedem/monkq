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
from typing import Optional
import json


class Order():
    def __init__(self, symbol: str, quantity: int, price: Optional[float] = None, side: Optional[str] = None,
                 order_type: Optional[str] = None, displayQty: Optional[int] = None, stopPx: Optional[float] = None,
                 clOrdID: Optional[str] = None, pegOffsetValue: Optional[float] = None,
                 pegPriceType: Optional[str] = None, timeInForce: Optional[str] = None, execInst: Optional[str] = None,
                 text: Optional[str] = None):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.displayQty = displayQty
        self.stopPx = stopPx
        self.clOrdID = clOrdID
        self.pegOffsetValue = pegOffsetValue
        self.pegPriceType = pegPriceType
        self.timeInForce = timeInForce
        self.execInst = execInst
        self.text = text

    @classmethod
    def create_order(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def to_postdict(self):
        return {
            'symbol': self.symbol,
            'side': self.side,
            'orderQty': self.quantity,
            'order_type': self.order_type,
            'price': self.price,
            'displayQty': self.displayQty,
            'stopPx': self.stopPx,
            'clOrdID': self.clOrdID,
            'pegOffsetValue': self.pegOffsetValue,
            'pegPriceType': self.pegPriceType,
            'timeInForce': self.timeInForce,
            'execInst': self.execInst,
            'text': self.text
        }

    def to_json(self):
        return json.dumps({
            'symbol': self.symbol,
            'side': self.side,
            'orderQty': self.quantity,
            'order_type': self.order_type,
            'price': self.price,
            'displayQty': self.displayQty,
            'stopPx': self.stopPx,
            'clOrdID': self.clOrdID,
            'pegOffsetValue': self.pegOffsetValue,
            'pegPriceType': self.pegPriceType,
            'timeInForce': self.timeInForce,
            'execInst': self.execInst,
            'text': self.text
        })
