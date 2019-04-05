=========
Strategy
=========

You have to edit your own strategy based on the :class:`~BaseStrategy`.
You have to implement :meth:`~BaseStrategy.setup`,
:meth:`~BaseStrategy.handle_bar` these 2 methods.

.. class::BaseStrategy

    You would implement your core strategy based on the `BaseStrategy`.
    There are some specifications for the methods you have to implement below.

    .. comethod::setup(self)

        The framework would trigger the `setup` method in the very first
        place. You can setup all the stuffs need for the strategy. This
        method would only trigger **one time**.

    .. comethod::handle_bar(self)

        The strategy would trigger the handler_bar method according to the
        :attr:`~Setting.FREQUENCY` of your setting. It is a time based
        strategy trigger method.

