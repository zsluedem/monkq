from typing import Generator
from unittest.mock import MagicMock

import pytest
from MonkTrader.stat import Statistic
from MonkTrader.utils.timefunc import utc_datetime


@pytest.fixture()
def statistic_context() -> Generator[MagicMock, None, None]:
    account1 = MagicMock()
    account2 = MagicMock()
    account1.total_capital = 2000
    account2.total_capital = 5000
    accounts = {"account1": account1, "account2": account2}
    context = MagicMock()
    context.now = utc_datetime(2018, 1, 1)
    context.accounts = accounts

    yield context


def test_statistic(statistic_context: MagicMock) -> None:
    stat = Statistic(statistic_context)

    stat.collect_daily()

    assert stat.daily_capital == [{"timestamp": utc_datetime(2018, 1, 1), "account1": 2000, "account2": 5000}]

    order = MagicMock()
    stat.collect_order(order)

    assert order in stat.order_collections

    trade = MagicMock()
    stat.collect_trade(trade)

    assert trade in stat.trade_collections
