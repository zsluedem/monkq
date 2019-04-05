=========
Settings
=========

Core Settings
=============

.. class:: Setting

    .. py:attribute:: FREQUENCY

        monkq only provide two options for `frequency`--`tick` and `1m`.
        `tick` means the strategy would run in the tick level. Every tick
        would trigger your strategy method.

    .. py:attribute:: LOG_LEVEL

        The log level to run the strategy.You can choose from `DEBUG`, `INFO`,
        `NOTICE`, `WARNING`, `ERROR`.

    .. py:attribute:: START_TIME

        It is used for the backtest only. If you use a realtime mode strategy
        running, you can ignore this parameter.It is the start time of the
        backtest running. It must be smaller than `END_TIME`. It must be a
        time-zone aware :py:class:`~datetime.datetime` object. Recommend you
        to use :func:`~utc_datetime`.

    .. py:attribute:: END_TIME

        It is used for the backtest only. If you use a realtime mode strategy
        running, you can ignore this parameter. It is the end time of the
        backtest. It must be bigger than `START_TIME`. It must be a
        time-zone aware :py:class:`~datetime.datetime` object. Recommend you
        to use :func:`~utc_datetime`.

    .. py:attribute:: STRATEGY

        It can be dotted path which can be imported as the subclass of
        :class:`~BaseStrategy` or directly the subclass of
        :class:`~BaseStrategy`.

    .. py:attribute:: DATA_DIR

        The data directory where you put your download. monkq would use
        the data directory when you run a backtest.

    .. py:attribute:: EXCHANGES

        The exchange setting. It is a :py:class:`~dict` like object. The key
        of the dict is the name of the exchange and the value is the setting
        of the exchange. Below is the example::
            
            'bitmex': {
                'ENGINE': 'monkq.exchange.bitmex.default_sim_exchange',
                "IS_TEST": True,
            }

        Key `bitmex` is the name of the exchange.
        
        `ENGINE` is a dotted path which can be imported or directly a subclass
        of :class:`~BaseExchange`.

    .. py:attribute:: ACCOUNTS

        The account setting. It is a :py:class:`~list` like object. The value
        of the list is the dict of an account setting like::

                {
                    'NAME': 'bitmex_account',
                    'EXCHANGE': 'bitmex',
                    "START_WALLET_BALANCE": 100000,
                    'ACCOUNT_MODEL': 'monkq.assets.account.FutureAccount'
                }


        `NAME` is the name of the account. You can get the account through
        :attr:`~Context.accounts`.

        `EXCHANGE` is the exchange of the account belongs to. It correspond to
        the name in the `EXCHANGE` settings.

        `START_WALLET_BALANCE` is the start wallet for the account. It is only 
        for backtest.

        `ACCOUNT_MODEL`: a dotted path which can be imported or directly 
        subclass of :class:`~BaseAccount`.

    .. py:attribute:: TRADE_COUNTER

        A dotted path of trade counter class or directly the trade 
        counter class.

    .. py:attribute:: STATISTIC

        A dotted path of the statistic class or directly the statistic class.

    .. py:attribute:: REPORT_FILE

        The result of a backtest file path.

    .. py:attribute:: HTTP_PROXY

        If you want to send http request through a http proxy, you can set
        your http proxy with it. If you don't want that, you can just leave it
        with an empty string or `None`.

    .. py:attribute:: SSL_PATH

        If you want to use a specific ssl for you request, you can set your
        ssl path here. More info you can see :py:mod:`~ssl`
