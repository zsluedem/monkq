from monkq.initer import Initer
from unittest.mock import MagicMock
import pytest
from tests.tools import random_kline_data_with_start_end
from monkq.utils.timefunc import utc_datetime


@pytest.fixture()
def context():
    context = MagicMock()
    context.exchanges.__getitem__().all_data.return_value = random_kline_data_with_start_end(
        utc_datetime(2018,1,1),
        utc_datetime(2018,2,1)
    )
    context.now = utc_datetime(2018, 1, 10, 0, 1)
    yield context

def test_initer(context: MagicMock):
    initer = Initer(context)
    instrument = MagicMock()
    initer.init_kline_freq('30min', instrument)
    initer.init_indicator('30min', instrument, 'MA', ['close'])

    history_kline_30min = initer.history_kline('30min', instrument, 100)
    assert len(history_kline_30min) == 100
    assert history_kline_30min.index[-1] == utc_datetime(2018, 1, 10)

    history_ma_30min = initer.history_indicator('30min', instrument, 100)
    assert len(history_ma_30min) == 100
    assert history_ma_30min.index[-1] == utc_datetime(2018, 1, 10)

