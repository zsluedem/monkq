=========
Settings
=========

Core Settings
=============

.. class:: Setting

    .. attribute:: FREQUENCY

        MonkTrader only provide two options for `frequency`--`tick` and `1m`.
        `tick` means the strategy would run in the tick level. Every tick
        would trigger your strategy method.

    .. attribute:: LOG_LEVEL

        The log level to run the strategy.You can choose from `DEBUG`, `INFO`,
        `NOTICE`, `WARNING`, `ERROR`.

    .. attribute:: START_TIME

        It is used for the backtest only. If you use a realtime mode strategy
        running, you can ignore this parameter.It is the start time of the
        backtest running. It must be smaller than `END_TIME`. It can either be
        a string like date time like `2018-01-01T00:00:00Z` or
        :py:class:`~datetime.datetime`. MonkTrader would parse string
        with utc :py:class:`~datetime.datetime`.

    .. attribute:: END_TIME

        It is used for the backtest only. If you use a realtime mode strategy
        running, you can ignore this parameter. It is the end time of the
        backtest. It must be bigger than `START_TIME`. It can either be
        a string like date time like `2018-01-01T00:00:00Z` or
        :py:class:`~datetime.datetime`. MonkTrader would parse string
        with utc :py:class:`~datetime.datetime`.

    .. attribute:: STRATEGY

        pass

    .. attribute:: DATA_DIR

        The data directory where you put your download. MonkTrader would use
        the data directory when you run a backtest.

    .. attribute:: EXCHANGES

        The exchange setting. It is a :py:class:`~dict` like object. The key
        of the dict is the name of the exchange and the value is the setting
        of the exchange.

    .. attribute:: HTTP_PROXY

        If you want to send http request through a http proxy, you can set
        your http proxy with it. If you don't want that, you can just leave it
        with an empty string or `None`.

    .. attribute:: SSL_PATH

        If you want to use a specific ssl for you request, you can set your
        ssl path here. More info you can see :py:module:`~ssl`
