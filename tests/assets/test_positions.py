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
from typing import TypeVar
from unittest.mock import MagicMock

import pytest
from MonkTrader.assets.account import BaseAccount, FutureAccount
from MonkTrader.assets.instrument import FutureInstrument, Instrument
from MonkTrader.assets.order import BaseOrder
from MonkTrader.assets.positions import (
    BasePosition, CrossPosition, FutureBasePosition,
    FutureCrossIsolatePosition, IsolatedPosition, PositionManager,
)
from MonkTrader.assets.trade import Trade
from MonkTrader.assets.variable import DIRECTION, POSITION_EFFECT
from MonkTrader.exception import MarginException, MarginNotEnoughException

from ..utils import random_string

T_EXCHANGE = TypeVar('T_EXCHANGE', bound="AbcExchange")


def test_position_manager(instrument: Instrument, base_account: BaseAccount) -> None:
    position_manager: PositionManager = PositionManager(BasePosition, base_account)
    position = position_manager[instrument]
    assert isinstance(position, BasePosition)
    assert position is position_manager[instrument]


def test_empty_position_deal(instrument: Instrument, base_account: BaseAccount) -> None:
    position = BasePosition(instrument=instrument, account=base_account)
    order = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=80)
    # open a position
    trade1 = Trade(order=order, exec_price=10, exec_quantity=30, trade_id=random_string(6))
    assert position.position_effect(trade1) == POSITION_EFFECT.OPEN
    position.deal(trade1)
    assert position.quantity == 30
    assert position.open_price == 10

    # get more on a position
    trade2 = Trade(order=order, exec_price=13, exec_quantity=50, trade_id=random_string(6))
    position.deal(trade2)
    assert position.position_effect(trade2) == POSITION_EFFECT.GET_MORE

    assert position.quantity == 80
    assert position.open_price == 11.875

    # sell part of the position
    order2 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-180)
    trade3 = Trade(order=order2, exec_price=15, exec_quantity=-40, trade_id=random_string(6))
    assert position.position_effect(trade3) == POSITION_EFFECT.CLOSE_PART
    position.deal(trade3)
    assert position.quantity == 40
    assert position.open_price == 11.875

    # close a position and open a opposite position
    trade4 = Trade(order=order2, exec_price=15, exec_quantity=-60, trade_id=random_string(6))
    assert position.position_effect(trade4) == POSITION_EFFECT.CLOSE_AND_OPEN
    position.deal(trade4)
    assert position.quantity == -20
    assert position.open_price == 15

    # get more on a position
    trade5 = Trade(order=order2, exec_price=12, exec_quantity=-80, trade_id=random_string(6))
    assert position.position_effect(trade5) == POSITION_EFFECT.GET_MORE
    position.deal(trade5)
    assert position.quantity == -100
    assert position.open_price == 12.6

    # close a position
    order3 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=100)
    trade6 = Trade(order=order3, exec_price=12, exec_quantity=100, trade_id=random_string(6))
    assert position.position_effect(trade6) == POSITION_EFFECT.CLOSE
    position.deal(trade6)
    assert position.quantity == 0
    assert position.open_price == 0

    # open a position
    order4 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-80)
    trade7 = Trade(order=order4, exec_price=13, exec_quantity=-30, trade_id=random_string(6))
    assert position.position_effect(trade7) == POSITION_EFFECT.OPEN
    position.deal(trade7)
    assert position.quantity == -30
    assert position.open_price == 13

    # get more on position
    trade8 = Trade(order=order4, exec_price=15, exec_quantity=-50, trade_id=random_string(6))
    assert position.position_effect(trade8) == POSITION_EFFECT.GET_MORE
    position.deal(trade8)

    assert position.quantity == -80
    assert position.open_price == 14.25

    # sell part of the position
    order5 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=180)
    trade9 = Trade(order=order5, exec_price=10, exec_quantity=40, trade_id=random_string(6))
    assert position.position_effect(trade9) == POSITION_EFFECT.CLOSE_PART
    position.deal(trade9)
    assert position.quantity == -40
    assert position.open_price == 14.25

    # close a position and open a opposite position
    trade10 = Trade(order=order5, exec_price=11, exec_quantity=60, trade_id=random_string(6))
    assert position.position_effect(trade10) == POSITION_EFFECT.CLOSE_AND_OPEN
    position.deal(trade10)
    assert position.quantity == 20
    assert position.open_price == 11

    # get more on a position
    trade11 = Trade(order=order5, exec_price=13, exec_quantity=80, trade_id=random_string(6))
    assert position.position_effect(trade11) == POSITION_EFFECT.GET_MORE
    position.deal(trade11)
    assert position.quantity == 100
    assert position.open_price == 12.6

    # close a position
    order6 = BaseOrder(account=base_account, order_id=random_string(6), instrument=instrument, quantity=-100)
    trade12 = Trade(order=order6, exec_price=15, exec_quantity=-100, trade_id=random_string(6))
    assert position.position_effect(trade12) == POSITION_EFFECT.CLOSE
    position.deal(trade12)
    assert position.quantity == 0
    assert position.open_price == 0


def test_future_base_position(exchange: MagicMock, future_instrument: FutureInstrument,
                              future_account: FutureAccount) -> None:
    exchange.get_last_price.return_value = 10
    assert exchange == future_instrument.exchange
    assert future_instrument.last_price == 10
    position = FutureBasePosition(instrument=future_instrument, account=future_account)

    position.quantity = 100
    position.open_price = 9.5
    assert position.direction == DIRECTION.LONG
    assert position.market_value == 1000
    assert position.open_value == 950
    assert position.unrealised_pnl == 47.5
    assert position.min_open_maint_margin == 23.75
    assert position.open_init_margin == 47.5
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = 100
    position.open_price = 11
    assert position.direction == DIRECTION.LONG
    assert position.market_value == 1000
    assert position.open_value == 1100
    assert position.unrealised_pnl == -102.5
    assert position.min_open_maint_margin == 27.5
    assert position.open_init_margin == 55
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = -100
    position.open_price = 9
    assert position.direction == DIRECTION.SHORT
    assert position.market_value == 1000
    assert position.open_value == 900
    assert position.unrealised_pnl == -102.5
    assert position.min_open_maint_margin == 22.5
    assert position.open_init_margin == 45
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25

    position.quantity = -100
    position.open_price = 11
    assert position.direction == DIRECTION.SHORT
    assert position.market_value == 1000
    assert position.open_value == 1100
    assert position.unrealised_pnl == 97.5
    assert position.min_open_maint_margin == 27.5
    assert position.open_init_margin == 55
    assert position.last_init_margin == 50
    assert position.min_last_maint_margin == 25


def test_cross_position(exchange: MagicMock, future_instrument: FutureInstrument,
                        future_account: FutureAccount) -> None:
    exchange.get_last_price.return_value = 18
    assert future_instrument.last_price == 18

    mock_account = MagicMock(future_account)
    mock_account.available_balance = 10000

    position = CrossPosition(instrument=future_instrument, account=mock_account)
    # long
    position.open_price = 20
    position.quantity = 2000
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)
    assert position.maint_margin == 12000
    assert position.position_margin == pytest.approx(1890)
    with pytest.raises(MarginException):
        position.maint_margin = 10
    with pytest.raises(MarginException):
        position.leverage

    # short
    mock_account.available_balance = 12000
    position.open_price = 22
    position.quantity = -1800
    assert position.liq_price == pytest.approx(28.9699, 0.0001)
    assert position.bankruptcy_price == pytest.approx(29.6924, 0.0001)
    assert position.maint_margin == 13980
    assert position.position_margin == pytest.approx(1701)
    with pytest.raises(MarginException):
        position.maint_margin = 10
    with pytest.raises(MarginException):
        position.leverage


def test_isolated_position(exchange: MagicMock, future_instrument: FutureInstrument,
                           future_account: FutureAccount) -> None:
    exchange.get_last_price.return_value = 10
    assert future_instrument.last_price == 10

    mock_account = MagicMock(future_account)
    mock_account.available_balance = 1000
    assert mock_account.available_balance == 1000

    position = IsolatedPosition(instrument=future_instrument, account=mock_account)

    # long
    position.open_price = 11
    position.quantity = 1000
    position.maint_margin = 800
    assert position.leverage == 12.5
    assert position.liq_price == pytest.approx(10.4884, 0.0001)
    assert position.position_margin == 800
    assert position.bankruptcy_price == pytest.approx(10.2255, 0.0001)

    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.maint_margin = 1100

    with pytest.raises(MarginNotEnoughException):
        # less than the init margin
        position.maint_margin = 400

    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.set_leverage(2)

    mock_account.available_balance = 10000
    position.open_price = 11
    position.quantity = 1000
    position.set_leverage(5)
    assert position.maint_margin == 2000
    assert position.leverage == 5
    assert position.liq_price == pytest.approx(9.2544, 0.0001)
    assert position.position_margin == 2000
    assert position.bankruptcy_price == pytest.approx(9.0225, 0.0001)

    # short
    mock_account.available_balance = 10000
    exchange.get_last_price.return_value = 11

    assert future_instrument.last_price == 11
    position.maint_margin = 1000
    position.open_price = 9
    position.quantity = -600
    assert position.liq_price == pytest.approx(10.3811, 0.0001)
    assert position.position_margin == 1000
    assert position.bankruptcy_price == pytest.approx(10.6401, 0.0001)
    assert position.leverage == 6.6
    # position.maint_margin =
    with pytest.raises(MarginNotEnoughException):
        # more than the available margin
        position.maint_margin = 11000

    with pytest.raises(MarginNotEnoughException):
        # less than the init margin
        position.maint_margin = 100

    with pytest.raises(MarginNotEnoughException):
        mock_account.available_balance = 3000
        position.set_leverage(2)

    mock_account.available_balance = 10000
    exchange.get_last_price.return_value = 11
    assert future_instrument.last_price == 11
    position.open_price = 10.5
    position.quantity = -800

    position.set_leverage(4)
    assert position.maint_margin == 2200
    assert position.leverage == 4
    assert position.position_margin == 2200
    assert position.liq_price == pytest.approx(12.8953, 0.0001)
    assert position.bankruptcy_price == pytest.approx(13.2169, 0.0001)


def test_cross_isolated_position(exchange: MagicMock, future_instrument: FutureInstrument,
                                 future_account: FutureAccount) -> None:
    exchange.get_last_price.return_value = 18
    assert future_instrument.last_price == 18

    mock_account = MagicMock(future_account)
    mock_account.available_balance = 10000
    assert mock_account.available_balance == 10000

    position = FutureCrossIsolatePosition(instrument=future_instrument, account=mock_account)
    position.open_price = 20
    position.quantity = 2000
    assert not position.isolated
    assert not position.is_isolated
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)
    assert position.maint_margin == 12000
    assert position.position_margin == pytest.approx(1890)
    with pytest.raises(MarginException):
        position.leverage
    with pytest.raises(MarginException):
        position.maint_margin = 100

    with pytest.raises(MarginNotEnoughException):
        position.set_leverage(3)
    assert not position.isolated
    with pytest.raises(MarginNotEnoughException):
        position.set_maint_margin(300)
    assert not position.isolated

    position.set_leverage(4)
    assert position.isolated
    assert position.is_isolated
    assert position.maint_margin == 9000
    assert position.liq_price == pytest.approx(15.9383, 0.0001)
    assert position.bankruptcy_price == pytest.approx(15.5388, 0.0001)
    assert position.position_margin == 9000
    assert position.leverage == 4

    position.set_cross()
    assert not position.isolated
    assert not position.is_isolated

    position.maint_margin = 9000
    assert position.isolated
    assert position.is_isolated
    assert position.liq_price == pytest.approx(15.9383, 0.0001)
    assert position.bankruptcy_price == pytest.approx(15.5388, 0.0001)

    position.set_cross()
    assert not position.isolated
    assert not position.is_isolated
    assert position.liq_price == pytest.approx(14.3958, 0.0001)
    assert position.bankruptcy_price == pytest.approx(14.0351, 0.0001)

    position.set_maint_margin(9000)
    assert position.isolated
    assert position.is_isolated
