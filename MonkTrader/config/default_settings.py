import os

from MonkTrader.const import RUN_TYPE
from MonkTrader.utils.timefunc import utc_datetime

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = '1m'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = utc_datetime(2018, 1, 1)
END_TIME = utc_datetime(2018, 6, 1)

RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

STRATEGY = "MonkTrader.base_strategy.BaseStrategy"

DATA_DIR = os.path.expanduser("~/.monk/data")

EXCHANGES = {  # type: ignore
    'bitmex': {
        'ENGINE': 'MonkTrader.exchange.bitmex.default_sim_exchange',
        "IS_TEST": True,
    }
}

ACCOUNTS = [
    {
        'NAME': 'bitmex_account',
        'EXCHANGE': 'bitmex',
        "START_WALLET_BALANCE": 100000,
        'ACCOUNT_MODEL': 'MonkTrader.assets.account.FutureAccount'
    }
]

TRADE_COUNTER = "MonkTrader.tradecounter.TradeCounter"

STATISTIC = "MonkTrader.stat.Statistic"
