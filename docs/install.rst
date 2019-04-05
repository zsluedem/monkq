====================
Installation guide
====================

Python Version
---------------
Monkq only supports **Python3.6 and above**. Monkq **doesn't** support Python2,
Python3.3, Python3.4, Python3.5 because Monkq use some new grammar which is
introduced in Python3.6. Make sure you use the right Python version

You can get the latest version of Python at https://www.python.org/downloads/
or with your operating system’s package manager.

Prerequisites
---------------
Monkq use HDF5_ as the storage system. It is a
very good system which support dataset storage.

PyTables_ is built on top of the HDF5_ library,
using the Python language and the NumPy package. PyTables_ is package for
managing hierarchical datasets and designed to efficiently and
easily cope with extremely large amounts of data.

**Unix**

If you are using **Unix** system, you have to install the hdf lib to support
PyTables.

1. Ubuntu

.. code-block:: console

    sudo apt install libhdf5-dev

2. Centos Like

.. code-block:: console

    sudo yum -y install hdf5-devel

3. MacOs

.. code-block:: console

    brew install hdf5

**Windows**

If you are using **Windows** system, you can install binary package from pypi
and don't have to install any other additional packages.


Install monkq
-----------------
Recommend you to install `monkq` with pypi. Just simply run:

.. code-block:: console

    pip install monkq


.. _HDF5: https://www.hdfgroup.org/
.. _PyTables: https://www.pytables.org/
