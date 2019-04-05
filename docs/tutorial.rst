==============
Tutorial
==============

Let's learn monkq by example.

Through this tutorial, we'll walk you through the creation of a basic strategy.

We'll assume you have already installed monkq.

Create a project
-----------------

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

Write First Strategy
-----------------------

Now, we are trying to write our first strategy. See the codes in the
:file:`strategy.py`.

.. code-block:: python

    from monkq.base_strategy import BaseStrategy


    class MyStrategy(BaseStrategy):
        async def setup(self):  # type:ignore
            pass

        async def handle_bar(self):  # type:ignore
            pass


Now we are going to reimplment the `handler_bar` method and the `setup` method.

1. `setup` method would be trigger in the very first place of your strategy and
    triggered for only one time. You can setup some value or attr here.
2. `handle_bar` method is the period calling method. The frequency to trigger
    the `handle_bar` method depends on the :attr:`~Setting.FREQUENCY`
    (right now monkq only support 1 minute frequency).

