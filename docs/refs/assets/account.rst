.. _asset_account:

============
Account
============

BaseAccount
============

.. class:: BaseAccount

    `BaseAccount` is the base class for all the accounts in MonkTrader.The
    ``accounts`` below all have the base attrs of it.

    .. attribute:: exchange

        The :class:`~Exchange` the account belongs to.

    .. attribute:: positions

        A dict-like obj :class:`~PositionManager`. You can access a specific
        position by it like:

        .. code-block::python

            position = account.positions[instrument]

    .. attribute:: wallet_balance

        THe total balance of the account have

FutureAccount
===============

.. class:: FutureAccount

    `FutureAccount` can hold future position. It calculates all the data
    which future position have.

    .. attribute:: position_margin

        The total position margin of all the positions in the account.

    .. attribute:: order_margin

        The total order margin of all the open orders in the account.

    .. attribute:: unrealised_pnl

        The unrealised profit/loss of the current positions in the account.

    .. attribute:: margin_balance

        Equal to:

        :attr:`~BaseAccount.wallet_balance` +
        :attr:`~FutureAccount.unrealised_pnl`

    .. attribute:: available_balance

        The available balance you can use for order or position change.
        It is calculated by formula below:

        :attr:`~FutureAccount.margin_balance` -
        :attr:`~FutureAccount.position_balance` -
        :attr:`~FutureAccount.order_margin`



