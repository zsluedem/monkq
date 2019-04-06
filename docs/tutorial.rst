==============
Tutorial
==============

Let's learn monkq by example.

Through this tutorial, we'll walk you through the creation of a basic strategy.

We'll assume you have already installed monkq.

Create a project
=================

If this is your first time using monkq, you'll have to take care of some
initial setup. Namely, you'll need to auto-generate some codes that establishes
a monkq project -- a collection of settings for an instance of monkq.

From the command line, ``cd`` into a directory where you'd like to store your
code, then run the following command:

.. code-block:: console

    $ monkq startstrategy --name mystrategy

This will create a ``mystrategy`` directory in your current directory.

.. note::

    You'll need to avoid naming projects after built-in Python or Django
    components. In particular, this means you should avoid using names like
    ``os`` (which will conflict with a built-in Python package).

Let's look at what ``startstrategy`` created::

    mystrategy/
        __init__.py
        manage.py
        mystrategy_settings.py
        strategy.py

These files are:

* :file:`__init__.py`: An empty file that tells Python that this directory
  should be considered a Python package.If you're a Python beginner, read
  :ref:`more about packages <tut-packages>` in the official Python docs.

* :file:`manage.py`: A command-line utility that lets you interact with this
  monkq strategy in various ways.

* :file:`mystrategy_settings.py`: Settings/configuration for this monkq project.
  :doc:`/refs/settings` will tell you details about the settings.

* :file:`strategy.py`: This is the main file you would edit to make a strategy.
  Your strategy would stay in it.

Write the First Strategy
==========================

Now, we are trying to write our first strategy. See the codes in the
:file:`strategy.py`.

.. code-block:: python

    from monkq.base_strategy import BaseStrategy


    class MyStrategy(BaseStrategy):
        async def setup(self):  # type:ignore
            pass

        async def handle_bar(self):  # type:ignore
            pass


Now we are going to reimplment the :meth:`~BaseStrategy.setup` method
and the :meth:`~BaseStrategy.handle_bar` method.

1. :meth:`~BaseStrategy.setup` method would be trigger in the very first
   place of your strategy and triggered for only one time.
   You can setup some value or attr here.
2. :meth:`~BaseStrategy.handle_bar` method is the period calling method.
   The frequency to trigger the `handle_bar` method depends on
   the :attr:`~Setting.FREQUENCY` (right now monkq only support
   1 minute frequency).

Implement Setup Method
------------------------

Now we want to set :attr:`~MyStrategy.exchange` and
:attr:`~MyStrategy.account` in the :meth:`~BaseStrategy.setup` method.
But we have to know that which exchange and account would be init by monkq.

To know that, we have to look at :file:`mystrategy_settings.py`.

.. code-block:: python

    import os
    from monkq.const import RUN_TYPE
    from monkq.utils.timefunc import utc_datetime

    # HTTP Proxy
    HTTP_PROXY = ""

    # used only for testing
    SSL_PATH = ''

    FREQUENCY = '1m'  # tick, 1m ,5m ,1h

    LOG_LEVEL = 'INFO'  # DEBUG, INFO, NOTICE, WARNING, ERROR

    START_TIME = utc_datetime(2018, 1, 1)
    END_TIME = utc_datetime(2018, 6, 1)

    RUN_TYPE = RUN_TYPE.BACKTEST  # type: ignore

    STRATEGY = "strategy.MyStrategy"

    DATA_DIR = os.path.expanduser("~/.monk/data")

    EXCHANGES = {  # type: ignore
        'bitmex': {
            'ENGINE': 'monkq.exchange.bitmex.default_sim_exchange',
            "IS_TEST": True,
        }
    }

    ACCOUNTS = [
        {
            'NAME': 'bitmex_account',
            'EXCHANGE': 'bitmex',
            "START_WALLET_BALANCE": 100000,
            'ACCOUNT_MODEL': 'monkq.assets.account.FutureAccount'
        }
    ]

    TRADE_COUNTER = "monkq.tradecounter.TradeCounter"

    STATISTIC = "monkq.stat.Statistic"

    REPORT_FILE = 'result.pkl'

According to the codes above, we know that monkq would init an exchange named
**bitmex** and init an account named **bitmex_account**. The **bitmex_account**
is correspond to the **bitmex** exchange.

We can setup the :attr:`~MyStrategy.exchange` and :attr:`~MyStrategy.account`
like below.

.. code-block:: python

    from monkq.base_strategy import BaseStrategy


    class MyStrategy(BaseStrategy):
        async def setup(self):  # type:ignore
            self.exchange = self.context.exchanges['bitmex']
            self.account = self.context.accounts['bitmex_account']
            self.is_order = False

        async def handle_bar(self):  # type:ignore
            pass


The :attr:`~BaseStrategy.context` holds all the settings of the strategy, all
the account instances and all the exchange instances of the strategy. It is
the core part of the strategy.

:attr:`~Context.exchanges` is a dict hold the exchange instance and
:attr:`~Context.accounts` is a dict holds the account instance.

See the settings

.. code-block:: python

    EXCHANGES = {  # type: ignore
        'bitmex': {
            'ENGINE': 'monkq.exchange.bitmex.default_sim_exchange',
            "IS_TEST": True,
        }
    }

The key of the **EXCHANGE** setting is the key of :attr:`~Context.exchanges`
so

.. code-block:: python

    self.exchange = self.context.exchanges['bitmex']

can retrieve the exchange of bitmex

Same like exchange see the **ACCOUNT** setting.

.. code-block:: python

    ACCOUNTS = [
        {
            'NAME': 'bitmex_account',
            'EXCHANGE': 'bitmex',
            "START_WALLET_BALANCE": 100000,
            'ACCOUNT_MODEL': 'monkq.assets.account.FutureAccount'
        }
    ]

The name of the account is ``bitmex_account`` and it is correspond the
exchange ``bitmex`` above. So we can retrieve the account

.. code-block:: python

    self.account = self.context.accounts['bitmex_account']

Implement Handle Bar Method
-----------------------------

Now we are going to write a strategy that buy one contract of BitMex exchange
and hold it till the end of the backtest end time.

Here is the codes for that.

.. code-block:: python

    async def handle_bar(self):  # type:ignore
        if not self.is_order:
            xbt = self.bitmex.get_instrument("XBTUSD")
            self.exchange.place_market_order(self.account, xbt, 1000)
            self.is_order = True

:meth:`~BaseExchange.available_instruments` would return valueview of the
available instruments. We are going to choose one instrument **XBTUSD** to
order.

We submit a market order of **XBTUSD** and the order would be traded
immediately regardless of the volume and trading condition at that time. That
is the current trading match situation right now.

In the example above , we use :meth:`~BaseExchange.available_instruments` and
:meth:`~BaseExchange.place_market_order` these two methods of
:class:`~BaseExchange`.

Now we have a strategy that could simulating trading of the exchange. Let's see
the result of :file:`strategy.py`.

.. code-block:: python

    from monkq.base_strategy import BaseStrategy


    class MyStrategy(BaseStrategy):
        async def setup(self):  # type:ignore
            self.exchange = self.context.exchanges['bitmex']
            self.account = self.context.accounts['bitmex_account']
            self.is_order = False

        async def handle_bar(self):  # type:ignore
            if not self.is_order:
                xbt = self.exchange.get_instrument("XBTUSD")
                self.exchange.place_market_order(self.account, xbt, 1000)
                self.is_order = True

Now we can run this strategy to do a backtest.Run the command below in the
``mystrategy`` directory you created above ::

    $ python manage.py runstrategy

Then you would see some logs of the strategy. After all that, an
:file:`result.pkl` would be generated. It is a :py:mod:`~pickle` file.

If you unpickle the file , you would get a dict like below

.. code-block:: python

    {
        "daily_capital": [
            {
                'timestamp': datetime.datetime,
                'bitmex_account':100000
            }, ...]
        "orders": [order1, order2]
        "trades": [trade1, trade2]
    }


1. daily_capital -> the daily account balance change during the backtest
2. orders -> all the orders you submit
3. trades -> all the trades generated in the strategy during the backtest

That's the result you want to analyse.