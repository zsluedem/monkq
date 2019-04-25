=========
Initer
=========

There are two main purposes for :class:`~Initer`:

1. Generate different frequency kline data
2. Pre generate indicator bar data which would improve backtest performance

Right now , monkq only store the 1 minute kline data locally. If you want to
get different frequency kline data. You have to use :class:`~Initer` to
generate the data.

What's more, you might need some indicator data like `MA`, `EMA`. If you
calculate in every :meth:`~BaseStrategy.handle_bar`, that would make the
backtest run very slow. Use :class:`~Initer` to pre generate the data would
improve the backtest performance a lot.(Make sure to use the
:meth:`~Initer.history_indicator` to get the indicator data to avoid future
data)

Here is an example how to use :class:`~Initer`.

.. code-block:: python

    class MyStrategy(BaseStrategy):
        async def setup(self):  # type:ignore
            self.exchange = self.context.exchanges['bitmex']
            self.initer = Initer(self.context)
            self.instrument = self.exchange.get_instrument("XBTUSD")
            self.initer.init_kline_freq("60min", instrument)
            self.initer.init_indicator("1min", instrument, "MA", "MA_XBT_1", ['close'])


        async def handle_bar(self):  # type:ignore
            kline_60m = self.initer.history_kline("60min", self.instrument, 100)
            ma_1m = self.initer.history_indicator("MA_XBT_1", 20)


We should use :meth:`~Initer.init_kline_freq` and :meth:`~Initer.init_indicator`
in the :meth:`~BaseStrategy.setup` step. It is to generate the data you might use
in the backtest.

The **only safe way** to retrieve the generate data is to use
:meth:`~Initer.history_kline` and :meth:`~Initer.history_indicator`. Don't use
other ways to get the pregenerated data which would cause other accurate
problems during the backtest.

.. warning::
    If you don't generate the 15 minutes kline data in the setup step, and you
    want to get the data in :meth:`~BaseStrategy.handle_bar`, it would raise
    py:exception`~KeyError`.

.. class:: Initer

    .. py:method:: init_kline_freq(self, freq, instrument)

        :param str freq: The frequency of the kline data you want to pregenerate
        :param instrument: instance of :class:`~Instrument`, the instrument
                           you want to pregenerate

        :return: None

    .. py:method:: init_indicator(self, freq, instrument, func, store_key, columns, *args, **kwargs)

        :param str freq: The frequency of indicator data you want to pregenerate
        :param instrument: An instance of :class:`~Instrument`, the instrument
        :param str func:  indicator function you want to use, see :ref:`available_func`.
        :param str store_key: The store key you want to put in cache. The
                              pre-generated data would store in a dict. The key
                              of the data would be `store_key`.
        :param list columns: The list of column which the `func` would use. Choose
                             from ['close', 'high', 'low', 'open', 'volume', 'turnover'].
        :param args: additional args would apply to `func`
        :param kwargs: additional kwargs would apply to `func`


    .. py:method:: history_kline(self, freq, instrument, count)

        :param str freq: The frequency you want to get from kline.
        :param instrument: An instance of :class:`~Instrument`, the instrument
        :param int count: The amount of the bars you want.

        :return: pandas.Dataframe with timeindex

    .. py:method:: history_indicator(self, store_key, count)

        :param str store_key: The `store_key` you use to init the indicator data.
        :param int count: The amount of the bars you want.

        :return: pandas.Dataframe with timeindex

.. _available_func:

Available Indicator Function
-----------------------------

The indicator system use talib_ to
calculate to indicator. The :class:`~Initer` supports all the function which
talib_ support. Check https://github.com/mrjbq7/ta-lib#supported-indicators-and-functions
to see all the indicator and functions.


.. _talib: https://github.com/mrjbq7/ta-lib