===========
Analyser
===========

Analyser
==========

.. class:: Analyser

    .. py:attribute:: trades

        A pandas dataframe concludes all the trade data you make in the strategy.

    .. py:method:: fetch_kline(self, exchange, freq, symbol, start=None, end=None)

        :param exchange str: the exchange name in your settings
        :param freq str: the frequency of the kline you want to get. Please follow `pandas offset rules <http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_.
        :param symbol str: symbol name
        :param start: Aware py:class:`~datetime.datetime` object. If you use None here, it would get from the date when the symbol listed.
        :param end: Aware py:class:`~datetime.datetime`.If you use None here, it would get from the date when the symbol delisted.

        Fetch the kline of one symbol from the exchange.

    .. py:method:: plot_kline(self, exchange, freq, symbol, start=None, end=None, alpha=1, axes=None)

        :param exchange str: the exchange name in your settings
        :param freq str: the frequency of the kline you want to get. Please follow `pandas offset rules <http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_.
        :param symbol str: symbol name
        :param start: Aware py:class:`~datetime.datetime` object. If you use None here, it would get from the date when the symbol listed.
        :param end: Aware py:class:`~datetime.datetime`.If you use None here, it would get from the date when the symbol delisted.
        :param alpha float: the alpha value of the kline in the image
        :param axes: :class:`~matplotlib.axes.Axes` obj. The axes you want to plot. If you use None here, it would generate a new :class:`~matplotlib.figure.Figure` and plot there.

        :return: Tuple of (:class:`~matplotlib.figure.Figure`, :class:`~matplotlib.axes.Axes`) the figure and axe where it plotted.

        Plot the kline data in an image.

    .. py:method:: plot_indicator(self, exchange, freq, symbol, func, columns, start=None, end=None, alpha=1, axes=None, *args, **kwargs):

        :param exchange str: the exchange name in your settings
        :param freq str: the frequency of the kline you want to get. Please follow `pandas offset rules <http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_.
        :param symbol str: symbol name
        :param func str: the indicator function you want to apply to kline data. See all the :ref:`available_func`.
        :param columns list: the column names of the indicator need, like ["high", "low", "close"]
        :param start: Aware py:class:`~datetime.datetime` object. If you use None here, it would get from the date when the symbol listed.
        :param end: Aware py:class:`~datetime.datetime`.If you use None here, it would get from the date when the symbol delisted.
        :param alpha float: the alpha value of the kline in the image
        :param axes: :class:`~matplotlib.axes.Axes` obj. The axes you want to plot. If you use None here, it would generate a new :class:`~matplotlib.figure.Figure` and plot there.

        :return: Tuple of (:class:`~matplotlib.figure.Figure`, :class:`~matplotlib.axes.Axes`) the figure and axe where it plotted.

        Plot the indicator in a image.

    .. py:method:: plot_volume(self, exchange, freq, symbol, start=None, end=None, color='b', alpha=1, axes=None)

        :param exchange str: the exchange name in your settings
        :param freq str: the frequency of the kline you want to get. Please follow `pandas offset rules <http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_.
        :param symbol str: symbol name
        :param start: Aware py:class:`~datetime.datetime` object. If you use None here, it would get from the date when the symbol listed.
        :param end: Aware py:class:`~datetime.datetime`.If you use None here, it would get from the date when the symbol delisted.
        :param color str: The color of the volume bar you want to use.
        :param alpha float: the alpha value of the kline in the image
        :param axes: :class:`~matplotlib.axes.Axes` obj. The axes you want to plot. If you use None here, it would generate a new :class:`~matplotlib.figure.Figure` and plot there.

        :return: Tuple of (:class:`~matplotlib.figure.Figure`, :class:`~matplotlib.axes.Axes`) the figure and axe where it plotted.

        Plot the volume image.

    .. py:method:: plot_account(self, axes=None)

        :param axes: :class:`~matplotlib.axes.Axes` obj. The axes you want to plot. If you use None here, it would generate a new :class:`~matplotlib.figure.Figure` and plot there.
        :return: Tuple of (:class:`~matplotlib.figure.Figure`, :class:`~matplotlib.axes.Axes`) the figure and axe where it plotted.

        Plot the account profit informations.

    .. py:method:: mark_trades(self, axes=None, start=None, end=None)

        :param axes: :class:`~matplotlib.axes.Axes` obj. The axes you want to plot. If you use None here, it would generate a new :class:`~matplotlib.figure.Figure` and plot there.
        :param start: Aware py:class:`~datetime.datetime` object. If you use None here, it would get from the date when the symbol listed.
        :param end: Aware py:class:`~datetime.datetime`.If you use None here, it would get from the date when the symbol delisted.
        :return: Tuple of (:class:`~matplotlib.figure.Figure`, :class:`~matplotlib.axes.Axes`) the figure and axe where it plotted.

        Use a marker to mark the trade happen