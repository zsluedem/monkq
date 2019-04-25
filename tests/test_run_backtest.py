import os
import pickle
import tempfile
from typing import Generator

import pytest
from monkq.__main__ import cmd_main
from monkq.config import SETTING_MODULE
from monkq.utils.timefunc import utc_datetime

from .utils import add_path, change_current_working_dir, random_string

test_strategy = """
from monkq.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    def __init__(self, context):
        super(TestStrategy, self).__init__(context)
        self.is_order = False

        self.symbol = "XBTZ15"

    async def handle_bar(self) -> None:
        if not self.is_order:
            bitmex_exchange = self.context.exchanges['bitmex']
            bitmex_account = self.context.accounts['bitmex_account']
            instruments = await bitmex_exchange.available_instruments()
            target = None
            for instrument in instruments:
                if instrument.symbol == self.symbol:
                    target = instrument
            if target is None:
                return
            await bitmex_exchange.place_market_order(bitmex_account, instrument, 100)
            self.is_order = True
"""

test_settings = """
import os

from monkq.const import RUN_TYPE
from monkq.utils.timefunc import utc_datetime

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = '1m'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = utc_datetime(2015, 6, 1)
END_TIME = utc_datetime(2015, 12, 1)

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "strategy.TestStrategy"

DATA_DIR = r"@data_dir@"

EXCHANGES = {
    'bitmex': {
        'ENGINE': 'monkq.exchange.bitmex.default_sim_exchange',
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": '',
    }
}

ACCOUNTS = [
    {
        'NAME': 'bitmex_account',
        'EXCHANGE': 'bitmex',
        "START_WALLET_BALANCE": 100000,
        'ACCOUNT_MODEL': 'monkq.assets.account.FutureAccount'
    }
]

TRADE_COUNTER = "monkq.tradecounter.TradeCounter"

STATISTIC = "monkq.stat.Statistic"

COLLECT_FREQ = "24H"

REPORT_FILE = r"@tmp@/result.pkl"
"""


@pytest.fixture()
def start_strategy_condition(tem_data_dir: str) -> Generator[str, None, None]:
    strateg_name = "strategy1m_{}".format(random_string(6))
    with tempfile.TemporaryDirectory() as tem_dir:
        cmd_main.main(['startstrategy', '-n', strateg_name, '-d', tem_dir], standalone_mode=False)

        with open(os.path.join(tem_dir, "{}/{}_settings.py".format(strateg_name, strateg_name)), 'w') as f:
            f.write(test_settings.replace("@data_dir@", tem_data_dir).replace('@tmp@', tem_dir))

        with open(os.path.join(tem_dir, "{}/strategy.py".format(strateg_name)), 'w') as f:
            f.write(test_strategy)

        with change_current_working_dir(os.path.join(tem_dir, strateg_name)) as strategy_dir:
            with add_path(strategy_dir):
                yield tem_dir

    os.environ.pop(SETTING_MODULE)


def test_run_1m_backtest(start_strategy_condition: str) -> None:
    from manage import cmd_main as strategy_cmd

    strategy_cmd.main(['runstrategy'], standalone_mode=False)

    with open(os.path.join(start_strategy_condition, 'result.pkl'), 'rb') as f:
        obj = pickle.load(f)

    daily_capital = obj['daily_capital']

    assert pytest.approx(daily_capital[-1]['bitmex_account'], 113324.03)
    assert daily_capital[-1]['timestamp'] == utc_datetime(2015, 12, 1)

    assert pytest.approx(daily_capital[1]['bitmex_account'], 98721.99024999999)
    assert daily_capital[1]['timestamp'] == utc_datetime(2015, 6, 2)

    assert len(obj['orders']) == 1
    order = obj['orders'][0]
    assert order.instrument.symbol == "XBTZ15"
    assert len(obj['trades']) == 1
    trade = obj['trades'][0]
    assert trade.order.instrument.symbol == "XBTZ15"
