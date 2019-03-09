import os
import tempfile

from MonkTrader.__main__ import cmd_main

from .utils import add_path, change_current_working_dir

test_strategy = """
from MonkTrader.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    def __init__(self, context):
        super(TestStrategy, self).__init__(context)
        self.is_order = False

        self.symbol = "XBTZ15"

    async def handle_bar(self) -> None:
        if not self.is_order:
            bitmex_exchange = self.context.exchanges['bitmex']
            instruments = await bitmex_exchange.available_instruments()
            target = None
            for instrument in instruments:
                if instrument.symbol == self.symbol:
                    target = instrument
            if target is None:
                return
            await bitmex_exchange.place_market_order(instrument, 100)
            self.is_order = True
"""

test_settings = """
import os
from MonkTrader.const import RUN_TYPE
from MonkTrader.utils.timefunc import utc_datetime

FREQUENCY = '1m'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = utc_datetime(2015, 6, 1)
END_TIME = utc_datetime(2015, 12, 1)

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "strategy.TestStrategy"

DATA_DIR = r"@data_dir@"

EXCHANGES = {
    'bitmex': {
        'engine': 'MonkTrader.exchange.bitmex',
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": '',
        "START_WALLET_BALANCE": 100000
    }
}
"""


def test_run_1m_backtest(tem_data_dir: str) -> None:
    strateg_name = "strategy1"
    with tempfile.TemporaryDirectory() as tem_dir:
        cmd_main.main(['startstrategy', '-n', strateg_name, '-d', tem_dir], standalone_mode=False)

        with open(os.path.join(tem_dir, "{}/settings.py".format(strateg_name)), 'w') as f:
            f.write(test_settings.replace("@data_dir@", tem_data_dir))

        with open(os.path.join(tem_dir, "{}/strategy.py".format(strateg_name)), 'w') as f:
            f.write(test_strategy)

        with change_current_working_dir(os.path.join(tem_dir, strateg_name)) as strategy_dir:
            with add_path(strategy_dir):
                from manage import cmd_main as strategy_cmd

                strategy_cmd.main(['runstrategy'], standalone_mode=False)
