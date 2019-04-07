====================
Installation guide
====================

Python Version
===============
Monkq only supports **Python3.6 and above**. Monkq **doesn't** support Python2,
Python3.3, Python3.4, Python3.5 because Monkq use some new grammar which is
introduced in Python3.6. Make sure you use the right Python version

You can get the latest version of Python at https://www.python.org/downloads/
or with your operating system’s package manager.

Prerequisites
==============

In order to use monkq, there two additional requirements which pip can not
take care for you and you have to install in you computer.

1. TA-lib_
2. HDF5_

Install HDF5
-------------
Monkq use HDF5_ as the storage system. It is a
very good system which support dataset storage.

PyTables_ is built on top of the HDF5_ library,
using the Python language and the NumPy package. PyTables_ is package for
managing hierarchical datasets and designed to efficiently and
easily cope with extremely large amounts of data.

**Linux**

1. Ubuntu

.. code-block:: console

    sudo apt install libhdf5-dev

2. Centos Like

.. code-block:: console

    sudo yum -y install hdf5-devel

**Mac OS X**

.. code-block:: console

    brew install hdf5

**Windows**

If you are using **Windows** system, you can install binary package from pypi
and don't have to install any other additional packages.

Install TA-lib
----------------
TA-Lib is widely used by trading software developers requiring to
perform technical analysis of financial market data.

**Mac OS X**

.. code-block:: console

    brew install ta-lib

**Windows**

Download `ta-lib-0.4.0-msvc.zip <http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip>`_
and unzip to C:\ta-lib.

This is a 32-bit binary release. If you want to use 64-bit Python,
you will need to build a 64-bit version of the library.
Some unofficial (and unsupported) instructions
for building on 64-bit Windows 10, here for reference:

1. Download and Unzip ta-lib-0.4.0-msvc.zip
2. Move the Unzipped Folder ta-lib to C:\
3. Download and Install Visual Studio Community 2015
4. Remember to Select [Visual C++] Feature
5. Build TA-Lib Library
6. From Windows Start Menu, Start [VS2015 x64 Native Tools Command Prompt]
7. Move to C:\ta-lib\c\make\cdr\win32\msvc
8. Build the Library nmake

You might also try these unofficial windows binaries for both 32-bit and 64-bit:

https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

**Linux**

Download `ta-lib-0.4.0-src.tar.gz <http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz>`_ and:

.. code-block:: console

    $ tar -xzf ta-lib-0.4.0-src.tar.gz
    $ cd ta-lib/
    $ ./configure --prefix=/usr
    $ make
    $ sudo make install


Install monkq
===============
Recommend you to install `monkq` with pypi. Just simply run:

.. code-block:: console

    pip install monkq


.. _HDF5: https://www.hdfgroup.org/
.. _PyTables: https://www.pytables.org/
.. _TA-lib: https://github.com/mrjbq7/ta-lib
