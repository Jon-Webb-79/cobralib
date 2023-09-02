.. Core Utilities documentation master file, created by
   sphinx-quickstart
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Cobralib documentation!
==================================

The cobralib package contains classes and functions that simplify
the process of reading ASCII formatted text files in standardized
ways.  In addition, this library contains classes that provide a
standardized interface to MySQL, PostGreSQL, SQLite, and
Microsoft SQL-Server relational databases.  In some cases,
the software in this package is merely a wrapper around existing
libraries that changes the interface or extends the current
capability of the package.

**NOTE:** This version of the cobralib package is focused on
software to support the process of reading in data, and in some
cases writing data to a log file.  However, future versions
may include data structures that are not provided with the
standard Python library or the Numpy library.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   io <io>
   db <db>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Installation
============
This package is loaded on the PyPi repository and can be installed via the following method

#. Create a python virtual environment ``python -m venv /path/to/new/virtual/environment``
#. Activate the virtual environment with the following command;

.. table:: Activation Commands for Virtual Environments

   +----------------------+------------------+-------------------------------------------+
   | Platform             | Shell            | Command to activate virtual environment   |
   +======================+==================+===========================================+
   | POSIX                | bash/zsh         | ``$ source <venv>/bin/activate``          |
   +                      +------------------+-------------------------------------------+
   |                      | fish             | ``$ source <venv>/bin/activate.fish``     |
   +                      +------------------+-------------------------------------------+
   |                      | csh/tcsh         | ``$ source <venv>/bin/activate.csh``      |
   +                      +------------------+-------------------------------------------+
   |                      | Powershell       | ``$ <venv>/bin/Activate.ps1``             |
   +----------------------+------------------+-------------------------------------------+
   | Windows              | cmd.exe          | ``C:\> <venv>\\Scripts\\activate.bat``    |
   +                      +------------------+-------------------------------------------+
   |                      | PowerShell       | ``PS C:\\> <venv>\\Scripts\\Activate.ps1``|
   +----------------------+------------------+-------------------------------------------+

#. If you are using a Python instance installed via a package manager such as brew, yum, pacman,
   or directly installed from the wheel, install with the command ``pip install cobralib``
#. If you wish to use extra dependencies for SQL-Server or MySQL databases insall with one of the following commands.

   - ``pip install 'cobralib[mysql]'``
   - ``pip install 'cobralib[postgresql]'``
   - ``pip install 'cobralib[mysql, postresql]'``

To install todo_six application as a developer, follow these steps.

.. rst-class:: numbered-list

#. Install poetry globally on your computer. Follow the instructions from the
   `Poetry <https://python-poetry.org/docs/>`_ web site
#. Set the poetry virtual environment with the following command ``poetry config virtualenvs.in-project true``
#. Ensure you have .git installed on your computer.
#. At your desired location create a directory titled ``cobralib``
#. Open a terminal (Bash, zsh or DOS) and cd to the ``cobralib`` directory
#. Type ``git clone https://github.com/Jon-Webb-79/cobralib.git``
#. Install packages with ``poetry install``


Usage
=====
The user instructions for this application is shown in :doc:`io` and :doc:`db`.


Contributing
============
Pull requests are welcome.  For major changes, please open an issue first to discuss what
you would like to change.  Please make sure to include and update tests as well
as relevant cod-strings and sphinx updates.

License
=======
This project uses a basic MIT license
