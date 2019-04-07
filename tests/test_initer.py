from typing import Generator
from unittest.mock import MagicMock

import pytest
from monkq.exchange.base import BaseSimExchange
from monkq.initer import Initer
from monkq.utils.timefunc import utc_datetime
from tests.tools import random_kline_data_with_start_end


@pytest.fixture()
def context() -> Generator[MagicMock, None, None]:
    context = MagicMock()
    context.exchanges.__getitem__.return_value = MagicMock(BaseSimExchange)
    context.exchanges.__getitem__().all_data.return_value = random_kline_data_with_start_end(
        utc_datetime(2018, 1, 1),
        utc_datetime(2018, 2, 1)
    )
    context.now = utc_datetime(2018, 1, 10, 0, 1)
    yield context


def test_initer(context: MagicMock) -> None:
    initer = Initer(context)
    instrument = MagicMock()
    initer.init_kline_freq('30min', instrument)
    initer.init_indicator('30min', instrument, 'MA', "MA_store", ['close'])
    initer.init_indicator('1min', instrument, "MA", "ma1m", ['close'])

    history_kline_30min = initer.history_kline('30min', instrument, 100)
    assert len(history_kline_30min) == 100
    assert history_kline_30min.index[-1] == utc_datetime(2018, 1, 10)

    history_ma_30min = initer.history_indicator("MA_store", 100)
    assert len(history_ma_30min) == 100
    assert history_ma_30min.index[-1] == utc_datetime(2018, 1, 10)


def test_initer_not_exist(context: MagicMock) -> None:
    initer = Initer(context)
    instrument = MagicMock()

    initer.init_kline_freq('60min', instrument)
    initer.init_indicator('60min', instrument, 'MA', "MA_store", ['close'])

    with pytest.raises(KeyError):
        initer.history_kline('30min', instrument, 100)
    with pytest.raises(KeyError):
        initer.history_indicator('MA', 100)
