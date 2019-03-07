from unittest.mock import MagicMock

from MonkTrader.stat import Statistic
from MonkTrader.utils.timefunc import utc_datetime


def test_statistic() -> None:
    account = MagicMock()
    context = MagicMock()
    context.now = utc_datetime(2018, 1, 1)
    account.wallet_balance = 1000000
    stat = Statistic(account, context)

    stat.collect_daily()

    assert stat.collected_data == [(utc_datetime(2018, 1, 1), 1000000)]
