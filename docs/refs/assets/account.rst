.. _asset_account:

============
Account
============

BaseAccount
============

.. class:: BaseAccount

    `BaseAccount` is the base class for all the accounts in monkq.The
    ``accounts`` below all have the base attrs of it.

    .. py:attribute:: exchange

        The :class:`~BaseExchange` the account belongs to.

    .. py:attribute:: positions

        A dict-like obj :class:`~PositionManager`. You can access a specific
        position by it like:

        .. code-block::python

            position = account.positions[instrument]

    .. py:attribute:: wallet_balance

        The total balance of the account have

    .. py:attribute:: total_capital

        The total capital asset of the account including the profit and loss.

FutureAccount
===============

.. class:: FutureAccount

    `FutureAccount` is inherited from :class:`~BaseAccount`.
    `FutureAccount` can hold :class:`~FutureBasePosition`.See the attr below
    which would use mostly.

    .. py:attribute:: position_margin

        The total position margin of all the positions in the account.

    .. py:attribute:: order_margin

        The total order margin of all the open orders in the account.

    .. py:attribute:: unrealised_pnl

        The unrealised profit/loss of the current positions in the account.

    .. py:attribute:: margin_balance

        Equal to:

        :attr:`~BaseAccount.wallet_balance` +
        :attr:`~FutureAccount.unrealised_pnl`

    .. py:attribute:: available_balance

        The available balance you can use for order or position change.
        It is calculated by formula below:

        :attr:`~FutureAccount.margin_balance` -
        :attr:`~FutureAccount.position_margin` -
        :attr:`~FutureAccount.order_margin`



