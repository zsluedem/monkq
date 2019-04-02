import os
import pickle
import tempfile
from typing import Generator
from unittest.mock import MagicMock

import pytest
from monkq.stat import Statistic
from monkq.utils.timefunc import utc_datetime


class PickleMock():
    pass


@pytest.fixture()
def statistic_context() -> Generator[PickleMock, None, None]:
    account1 = PickleMock()
    account2 = PickleMock()
    account1.total_capital = 2000  # type:ignore
    account2.total_capital = 5000  # type:ignore
    accounts = {"account1": account1, "account2": account2}
    context = MagicMock()
    context.now = utc_datetime(2018, 1, 1)
    context.accounts = accounts
    with tempfile.TemporaryDirectory() as tmp:
        context.settings.REPORT_FILE = os.path.join(tmp, 'result.pkl')

        yield context


def test_statistic(statistic_context: MagicMock) -> None:
    stat = Statistic(statistic_context)

    stat.collect_daily()

    assert stat.daily_capital == [{"timestamp": utc_datetime(2018, 1, 1), "account1": 2000, "account2": 5000}]

    order = PickleMock()
    stat.collect_order(order)  # type:ignore

    assert order in stat.order_collections

    trade = PickleMock()
    stat.collect_trade(trade)  # type:ignore

    assert trade in stat.trade_collections

    stat.report()

    with open(stat.report_file, 'rb') as f:
        obj = pickle.load(f)
    assert obj['daily_capital'] == [{"timestamp": utc_datetime(2018, 1, 1), "account1": 2000, "account2": 5000}]
