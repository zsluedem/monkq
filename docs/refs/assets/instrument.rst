.. _asset_instrument:

================
Instruments
================

Instrument describe a trading item in the exchange.

Instrument
============

.. class:: Instrument

    .. py:attribute:: exchange

        The :class:`~BaseExchange` the instrument belongs to

    .. py:attribute:: symbol

        The symbol of the instrument. Usually describe as "BTCUSDT".

    .. py:attribute:: listing_date

        The date the instrument listed in the :class:`~BaseExchange`.

    .. py:attribute:: expiry_date

        Some instruments would be delisted in the exchange. The date when the
        instrument was delisted is the expiry_date. But as for some future
        instrument, the expiry date means the date when the constract ends.

    .. py:attribute:: underlying

        The underlying crypto token of the instrument.

    .. py:attribute:: quote_currency

        The quote currency of the underlying token.

    .. py:attribute:: lot_size

        The minimum lot size of the underlying token.

    .. py:attribute:: tick_size

        The minimum tick size of quote currency.

    .. py:attribute:: maker_fee

        Maker fees are paid when you add liquidity to our order book by
        placing a limit order below the ticker price for buy,
        and above the ticker price for sell.

    .. py:attribute:: taker_fee

        Taker fees are paid when you remove liquidity from our order book
        by placing any order that is executed against an order
        on the order book.

.. note::

    If you want to know more about the :attr:`~Instrument.maker_fee` and
    :attr:`~Instrument.taker_fee` you can check
    https://support.bitfinex.com/hc/en-us/articles/213919589-What-fees-do-you-charge-


FutureInstrument
==================

.. class:: FutureInstrument

    Future contract instruments describe the future contract in exchange.

    .. py:attribute:: root_symbol

        The root symbol of the instrument.

    .. py:attribute:: init_margin_rate

        The init margin rate to open the position

    .. py:attribute:: maint_margin_rate

        The minimum maintainance margin rate to keep the position not to liquidate.

    .. py:attribute:: settlement_fee

        The settlement fee of the contract when the contract is to be settled.

    .. py:attribute:: settlement_currency

        The currency when the settlement happens.

    .. py:attribute:: settle_date

        The date when the settlement happens.

    .. py:attribute:: front_date

        Not clear now.

    .. py:attribute:: reference_symbol

        The reference symbol of the instrument, mostly is index future.

    .. py:attribute:: deleverage

        It is a bool value depends on whether the instrument is allowed to be
        deleveraged.

.. note::

    If you are not familiar with the :attr:`~FutureInstrument.init_margin_rate`
    and :attr:`~FutureInstrument.maint_margin_rate`. Please check
    https://www.investopedia.com/ask/answers/033015/what-difference-between-initial-margin-and-maintenance-margin.asp


.. class:: CallOptionInstrument

    CallOptionInstrument describes the call option of an instrument. It is
    inherited from :class:`~FutureInstrument`.

.. warning::

    CallOptionInstrument hasn't been tested in any conditions. Please be
    careful to use it.

.. class:: PutOptionInstrument

    PutOptionInstrument describes the put option of an instrument. It is
    inherited from :class:`~FutureInstrument`.

.. warning::

    PutOptionInstrument hasn't been tested in any conditions. Please be
    careful to use it.

.. class:: PerpetualInstrument

    PerpetualInstrument describes perpetual contract of an instrument. It is
    inherited from :class:`~FutureInstrument` which has all the attr of
    :class:`~FutureInstrument`.

    .. py:attribute:: funding_rate

        Perpetual contract would cost a fund every period time. For more
        information, please check
        https://www.bitmex.com/app/perpetualContractsGuide.
