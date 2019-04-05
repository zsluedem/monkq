.. _asset_position:

BasePosition
=============

.. class:: BasePosition

    `BasePosition` is the base position class of all the position class. All
    the position class should inherit the attr of `BasePosition`.

    .. py:attribute:: instrument

        It returns the reference to the :class:`~Instrument` of the position.

    .. py:attribute:: account

        Reference to the :class:`~BaseAccount` which the position belongs to.

    .. py:attribute:: quantity

        The current holding quantity of the position.

    .. py:attribute:: open_price

        The average price to open the position


FutureBasePosition
===================

.. class:: FutureBasePosition

    Future position class.

    .. py:attribute:: direction

        The :class:`~DIRECTION` of the position.

    .. py:attribute:: market_value

        The market value of the position at the last price of the instrument.

    .. py:attribute:: open_value

        The total value to open the position.

    .. py:attribute:: unrealised_pnl

        The unrealised profit and loss of the position.

    .. py:attribute:: min_open_maint_margin

        The minimum margin for this position.
        If the margin for this position is lower than the maint_margin,
        the position would be liquidated.

    .. py:attribute:: open_init_margin

        The initial margin of the position at the open price.

    .. py:attribute:: min_last_maint_margin

        The maintainance margin of the position at the last price.

    .. py:attribute:: last_init_margin

        The initial margin of the position at the last price.

    .. py:attribute:: liq_price

        When the price hit the liq price, the position would be liquidated by
        exchange.

    .. py:attribute:: bankruptcy_price

        When the price hit the bankruptcy price , the

    .. py:attribute:: maint_margin

        The maintainance margin of the position.

    .. py:attribute:: leverage

        The current leverage of the position.

    .. py:attribute:: position_margin

        The margin of the position is taking.


.. note::

    If you are not familiar with the `initial margin`
    and `maintainance margin`. Please check
    https://www.investopedia.com/ask/answers/033015/what-difference-between-initial-margin-and-maintenance-margin.asp


FutureCrossIsolatePosition
============================

.. class:: FutureCrossIsolatePosition

    FutureCrossIsolatePosition is a special future position. You can set the
    position to be a cross position or a isolated position. It is two different
    kinds of ways to calculate maintainance margin. Please check
    https://www.bitmex.com/app/isolatedMargin to know more.

    FutureCrossIsolatePosition is inherited from :class:`~FutureBasePosition`.
    It has all the attrs which :class:`~FutureBasePosition` has.

    .. py:method:: set_leverage(leverage)

        :param float leverage: the leverage of the position you want to set

        Set the leverage of the position. After this operation, the position
        would be a isolated position.

    .. py:method:: set_maint_margin(value)

        :param float value: the margin value of the position you want to set

        Set the maintainance margin of the position. After this operation,
        the position would be a isolated position. It is like
        :func:`~FutureCrossIsolatePosition.set_leverage` but set the margin.

    .. py:method:: set_cross

        Set the position to become a cross position.

    .. py:attribute:: is_isolated

        return a bool value. True means the position is now a isolated position
        otherwise cross position.


PositionManager
==================

.. class:: PositionManager(position_cls, account)

    :param position_cls: position default class, :class:`BasePosition`
        and its subclasses.
    :param account: The :class:`BaseAccount` or its subclasses. The account
        which the position manager belongs to.

    `PositionManager` is a py:class:`collections.defaultdict` which key is
    :class:`~Instrument` and value is :class:`~BasePosition` and its
    subclasses.