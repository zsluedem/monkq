BaseExchange
---------------

.. class:: BaseExchange(context, name, exchange_settinng)

    :param context: :class:`~Context` of the strategy
    :param str name: the name of the exchange
    :param dict exchange_setting: the setting of the exchange

    `BaseExchange` is the base exchange class of every exchange. Every exchange
    should be inherited from `BaseExchange` and implemented the function of
    the base exchange.

    .. comethod:: setup

        Setup step for exchange.

    .. comethod:: get_last_price(self, instrument)

        :param instrument: :class:`~Instrument`.


        Get the last price of an instrument.

    .. method:: exchange_info

        :return ExchangeInfo: an instance of :class:`~ExchangeInfo`

    .. comethod:: place_limit_order(self, account, instrument, price, quantity)

        :param account: an instance of :class:`~BaseAccount`
        :param instrument: an instance of :class:`~Instrument`
        :param float price: the price of the limit order
        :param float quantity: the quantity of the order

        :return order_id: the order id of the order

        Submit a limit order of an instrument.

    .. comethod:: place_market_order(self, account, instrument, quantity)

        :param account: an instance of :class:`~BaseAccount`
        :param instrument: an instance of :class:`~Instrument`
        :param float quantity: the quantity of the market order

        :return order_id: the order id of the order

        Submit a market order of an instrument.

    .. comethod:: amend_order(self, account, order_id, quantity, price)

        :param account: an instance of :class:`~BaseAccount`
        :param str order_id: the order id
        :param float quantity: the quantity to be amended
        :param float price: the price to be amended

        :return: result -> bool

    .. comethod:: cancel_order(self, account, order_id)

        :param account: an instance of :class:`~BaseAccount`
        :param str order_id: the order is

        :return: result -> bool

    .. comethod:: open_orders(self, account)

        :param account: an instance of :class:`~BaseAccount`

        :return orders: list of :class:`~BaseOrder`

    .. comethod:: available_instruments(self)

        :return: Valueview of :class:`~Instrument`

    .. comethod:: get_kline(self, instrument, count, including_now)

        :param instrument: an instance of :class:`~Instrument`
        :param int count: the count number of kline
        :param bool including_now: is including now or not

        :return: Dataframe kline

        Get the kline of an instrument

    .. comethod:: get_recent_trades(self, instrument)

        :param instrument: an instance of :class:`~Instrument`

        :return: list of dict


.. class:: BaseSimExchange

    `BaseSimExchange` is for backtesting. It provide some non-async method
    which is easier for the backtest engine to implement.

    .. method:: last_price(self, instrument)

        :param instrument: an instance of :class:`~Instrument`

        Get the last price of an instrument.

    .. method:: get_open_orders(self, account)

        :param account: an instance of :class:`~BaseAccount`

        Get the open orders of an account.

.. warning::

    Make sure you don't use the method above in the :class:`~BaseSimExchange`
    in the real trading situation. These methods only work for backtesting.

