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


from monkq.assets.order import BaseOrder, LimitOrder, MarketOrder


def base_order_to_dict(order: BaseOrder) -> dict:
    return {
        'order_id': order.order_id,
        'quantity': order.quantity,
        'traded_quantity': order.traded_quantity,
        'trades': order.trades,
        'symbol': order.instrument.symbol
    }


def limit_order_to_dict(order: LimitOrder) -> dict:
    base = base_order_to_dict(order)
    base.update({'price': order.price, 'order_type': 'limit'})
    return base


def market_order_to_dict(order: MarketOrder) -> dict:
    base = base_order_to_dict(order)
    base.update({'order_type': 'market'})
    return base
