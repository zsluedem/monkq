================
Instruments
================

Instrument describe a trading item in the exchange.

Instrument
============

.. class:: Instrument

    .. attribute:: exchange

        The :class:`~Exchange` the instrument belongs to

    .. attribute:: symbol

        The symbol of the instrument.Usually describe as "BTCUSTD".

    .. attribute:: listing_date

        The date the instrument listed in the :class:`~exchange`.

    .. attribute:: expiry_date

        Some instruments would be delisted in the exchange. The date when the
        instrument was delisted is the expiry_date. But as for some future
        instrument, the expiry date means the date when the constract ends.

    .. TODO

    .. attribute:: underlying

        pass

    .. attribute:: quote_currency

        pass

    .. attribute:: lot_size

        pass

    .. attribute:: tick_size

        pass

    .. attribute:: maker_fee

        pass

    .. attribute:: taker_fee

        pass


FutureInstrument
==================

.. class:: FutureInstrument

    .. attribute:: root_symbol

        pass

    .. attribute:: init_margin_rate

        pass

    .. attribute:: maint_margin_rate

        pass

    .. attribute:: settlement_fee

        pass

    .. attribute:: settlement_currency

        pass

    .. attribute:: settle_date

        pass

    .. attribute:: front_date

        pass

    .. attribute:: reference_symbol

        pass

    .. attribute:: deleverage

        pass