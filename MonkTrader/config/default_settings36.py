# Mongodb uri which is used to load data or download data in.
DATABASE_URI = "mongodb://127.0.0.1"

# HTTP Proxy
HTTP_PROXY = ""

# used only for testing
SSL_PATH = ''

FREQUENCY = 'tick'  # tick, 1m ,5m ,1h

LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

START_TIME = '2018-01-01T00:00:00Z'
END_TIME = '2018-06-01T00:00:00Z'

RUN_TYPE = 'backtest'  # backtest , realtime

TICK_TYPE = 'tick'  # tick , bar

STRATEGY = "strategy.MyStrategy"

EXCHANGE: dict = {
    'bitmex': {
        "IS_TEST": True,
        "API_KEY": '',
        "API_SECRET": ''
    }
}

BUILTIN_PLUGINS: dict = {

}

INSTALLED_PLUGINS: dict = {

}
