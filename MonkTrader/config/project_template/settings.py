import os

from MonkTrader.const import RUN_TYPE
from MonkTrader.utils.timefunc import utc_datetime

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = 'tick'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = utc_datetime(2018, 1, 1)
END_TIME = utc_datetime(2018, 6, 1)

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "strategy.MyStrategy"

DATA_DIR = os.path.expanduser("~/.monk/data")

EXCHANGES = {  # type: ignore
    'bitmex': {
        'engine': 'MonkTrader.exchange.bitmex',
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": '',
        "START_WALLET_BALANCE": 100000
    }
}
