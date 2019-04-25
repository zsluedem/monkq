.. _monkq_const:

========
Const
========

There are many `const` in monkq. Most of them are :py:class:`~enum` types
and used for indicating some basic unchanged constant.

Direction
==========

.. class:: DIRECTION

    `DIRECTION` is usually used for describing a future position direction.
    It is either `LONG` which means you have a positive quantity of
    the position or `SHORT` which meanns you have a negative quantity of the
    position.

    `DIRECTION` is inherited from :py:class:`~enum`.

    .. attribute:: LONG

        The long direction of the position.

    .. attribute:: SHORT

        The short direction of the position.


Position Effect
================

.. class:: POSITION_EFFECT

    Normally when you get a new trade for a position, there would be a status
    change for the position.`POSITION_EFFECT` is used for describing the kinds
    of the status change for the position.

    `POSITION_EFFECT` is inherited from :py:class:`~enum`.

    .. attribute:: OPEN

        When your position quantity is 0 and you have a new trade for the
        position, then the position effect is to `OPEN` the position.

    .. attribute:: CLOSE

        When your position quantity is not 0 and you have a new trade
        to reduce your position to 0, then the position effect is
        to `CLOSE` the position.

    .. attribute:: GET_MORE

        When your position quantity is not 0 and you have a new trade to
        get more quantity on the same direction of your position, then the
        position effect is to `GET_MORE` on the position.

    .. attribute:: CLOSE_PART

        When your position quantity is not 0 and you have a new trade to
        reduce quantity of your position, then the
        position effect is to `CLOSE_PART` on the position.

    .. attribute:: CLOSE_AND_OPEN

        When your position quantity is not 0 and you have a new trade to reduce
        close all your quantity on the direction and open a opposite direction
        of the position, then the position effect is `CLOSE_AND_OPEN`.

Side
========

.. class:: SIDE

    `SIDE` is used to describe the side of the order and the trade.

    `SIDE` is inherited from :py:class:`~enum`.


    .. attribute:: BUY

        The buy side.

    .. attribute:: SELL

        The sell side.


Order Status
=============

.. class:: ORDER_STATUS

    `ORDER_STATUS` is used to describe the status of the order.

    `ORDER_STATUS` is inherited from :py:class:`~enum`.

    .. attribute:: NOT_TRADED

        It means the order is not traded at all. The
        :attr:`~BaseOrder.traded_quantity` is 0.

    .. attribute:: FULL_TRADED

        The order is fully traded.The
        :attr:`~BaseOrder.traded_quantity` is equal to
        :attr:`~BaseOrder.quantity`.

    .. attribute:: PARTLY_TRADED

        THe order is partly traded.
