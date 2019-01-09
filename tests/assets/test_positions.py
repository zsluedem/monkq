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
from MonkTrader.assets.positions import PositionManager, BasePosition, FuturePosition
from MonkTrader.assets.order import BaseOrder
from MonkTrader.assets.trade import Trade
from ..utils import random_string
from .mock_resource import instrument, future_instrument, account


def test_position_manager():
    position_manager = PositionManager(BasePosition, account)
    assert isinstance(position_manager[instrument], BasePosition)


def test_empty_position_deal():
    position = BasePosition(instrument=instrument, account=account)
    order = BaseOrder(order_id=random_string(6), instrument=instrument,quantity=80)
    # open a position
    trade1 = Trade(order=order, exec_price=10, exec_quantity=30, trade_id=random_string(6))
    position.deal(trade1)
    assert position.quantity == 30
    assert position.open_price == trade1.avg_price

    # get more on a position
    trade2 = Trade(order=order, exec_price=13, exec_quantity=50, trade_id=random_string(6))
    position.deal(trade2)
    new_open_price = (trade1.avg_price * trade1.exec_quantity + trade2.avg_price* trade2.exec_quantity) /(trade1.exec_quantity+ trade2.exec_quantity)
    assert position.quantity == 80
    assert position.open_price == new_open_price

    # sell part of the position
    order2 = BaseOrder(order_id=random_string(6), instrument=instrument,quantity=-180)
    trade3 = Trade(order=order2, exec_price=15, exec_quantity=-40, trade_id=random_string(6))
    position.deal(trade3)
    assert position.quantity == 40
    assert position.open_price == new_open_price

    # close a position and open a opposite position
    trade4 = Trade(order=order2, exec_price=15, exec_quantity=-60, trade_id=random_string(6))
    position.deal(trade4)
    assert position.quantity == -20
    assert position.open_price == trade4.avg_price

    # get more on a position
    trade5 = Trade(order=order2, exec_price=12, exec_quantity=-80, trade_id=random_string(6))
    position.deal(trade5)
    assert position.quantity == -100
    assert position.open_price == (-20* trade4.avg_price + trade5.exec_quantity* trade5.avg_price)/(-20+ trade5.exec_quantity)

    # close a position
    order3 = BaseOrder(order_id=random_string(6), instrument=instrument,quantity=100)
    trade6 = Trade(order=order3, exec_price=12, exec_quantity=100, trade_id=random_string(6))
    position.deal(trade6)
    assert position.quantity == 0
    assert position.open_price == 0

    # open a position
    order4 =BaseOrder(order_id=random_string(6), instrument=instrument,quantity=-80)
    trade7 = Trade(order=order4, exec_price=13, exec_quantity=-30, trade_id=random_string(6))
    position.deal(trade7)
    assert position.quantity == -30
    assert position.open_price == trade7.avg_price

    # get more on position
    trade8 = Trade(order=order4, exec_price=15, exec_quantity=-50, trade_id=random_string(6))
    position.deal(trade8)
    new_open_price2 = (trade7.avg_price * trade7.exec_quantity + trade8.avg_price* trade8.exec_quantity) /(trade7.exec_quantity+ trade8.exec_quantity)
    assert position.quantity == -80
    assert position.open_price == new_open_price2

    # sell part of the position
    order5 = BaseOrder(order_id=random_string(6), instrument=instrument,quantity=180)
    trade9 = Trade(order=order5, exec_price=10, exec_quantity=40, trade_id=random_string(6))
    position.deal(trade9)
    assert position.quantity ==  -40
    assert position.open_price == new_open_price2

    # close a position and open a opposite position
    trade10 = Trade(order=order5, exec_price=11, exec_quantity=60, trade_id=random_string(6))
    position.deal(trade10)
    assert position.quantity == 20
    assert position.open_price == trade10.avg_price

    # get more on a position
    trade11 = Trade(order=order5, exec_price=13, exec_quantity=80, trade_id=random_string(6))
    position.deal(trade11)
    assert position.quantity == 100
    assert position.open_price == (20 * trade10.avg_price + trade11.avg_price * trade11.exec_quantity) / (trade11.exec_quantity + 20)

    # close a position
    order6 = BaseOrder(order_id=random_string(6), instrument=instrument,quantity=-100)
    trade12 = Trade(order=order6, exec_price=15, exec_quantity=-100, trade_id=random_string(6))
    position.deal(trade12)
    assert position.quantity == 0
    assert position.open_price == 0


def test_future_position():
    position = FuturePosition(instrument=future_instrument, account=account)

