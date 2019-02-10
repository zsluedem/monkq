=========
Strategy
=========

You have to edit your own strategy based on the :class:`~BaseStrategy`.
You have to implement :meth:`~BaseStrategy.setup`,
:meth:`~BaseStrategy.on_trade`, :meth:`~BaseStrategy.tick`,
:meth:`~BaseStrategy.handle_bar` these 4 methods.

.. class::BaseStrategy

    You would implement your core strategy based on the `BaseStrategy`.
    There are some specifications for the methods you have to implement below.

    .. method::setup(self)

        The framework would trigger the `setup` method in the very first
        place. You can setup all the stuffs need for the strategy. This
        method would only trigger **one time**.

    .. method::on_trade(trade)

        When you successfully submit an order and the order is successfully
        traded in the exchange. The strategy would trigger this method.
