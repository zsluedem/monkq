==============
Tutorial
==============

Let's learn monkq by example.

Through this tutorial, we'll walk you through the creation of a basic strategy.

We'll assume you have already installed monkq.

Create a project
====================

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

First Strategy
-----------------

