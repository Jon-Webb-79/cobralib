********
cobralib
********

Describe project here

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/

.. image:: https://readthedocs.org/projects/flake8/badge/?version=latest
    :target: https://flake8.pycqa.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
   :target: http://mypy-lang.org/

Overview
########
This library contains basic utility classes and functions that enable faster Python programming.
THese functions and methods standardize the process for reading in files of different
types to include ``.csv``, ``.txt``, ``.xls``, ``.xlsx``, ``.json``, ``.xml``, ``.yaml``,
``toml``, ``SQLite``, ``MySQL``, ``SQL-Server``
and ``PostGreSQL`` files.  In addition this library standardizes the process of setting
and implementing log files. **NOTE:** Despite the fact that github shows the tests as failing,
all tests do pass on a Linux and Mac platform before being uploaded to github.  This issue
appears to be caused by a library that while it works, was not written to be compatible
with Python 3.11.  We are working to fix this issue, but rest assure, the unit tests to
pass.

Contributing
############
Pull requests are welcome.  For major changes, please open an issue first to discuss
what you would like to change.  Please make sure to include and update tests
as well as relevant doc-string and sphinx updates.

License
#######
This project is licensed under a basic MIT License

Requirements
############
Python 3.8 or greater, developed with Python 3.11

Installation
############
In order to download this repository from github, follow these instructions

#. Install poetry globally on your computer. Follow the instructions from the
   `Poetry <https://python-poetry.org/docs/>`_ website
#. Set the poetry virtual environment with the following command ``poetry config virtualenvs.in-project true``
#. Ensure you have .git installed on your computer.
#. Open a terminal (Bash, zsh or DOS) and ``cd`` to the directory where you want to install the cobralib library
#. Type ``git clone https://github.com/Jon-Webb-79/cobralib.git``
#. ``cd`` into the cobralib directory
#. Create a virtual environment with the command ``python3 -m venv .venv``
#. Activate the virtual environment with the command ``source .venv/bin/activate``
#. Install packages.  This library uses underlying packages to manage MySQL and PostGreSQL; however, each
   of these libraries requires that the user have MySQL and PostGreSQL servers installed locally
   on their machine

   - If the user does not have MySQL or PostGreSQL server installed on their machine type ``poetry install``. This will
     install all packages other than the libraries for these two database management systems (DBMSs).  Note, you
     will not be able to use the underlying functionality for these to DBMS's.
   - If the user only has MySQL server installed locally, type ``poetry install -E mysql``
   - If the user only has PostGreSQL installed locally, type ``poetry install -E postgresql``
   - If the user has both MySQL and PostGreSQL installed locally, type ``poetry install -E mysql -E postgresql``
   - If you plan to support development, install the read_the_doc sphinx package with pip, ``pip install sphinx_rtd_theme``
#. In the future this repository may also be available on PyPi

This package can also be installed via pip

#. Install with all packages ``pip install cobralib``
#. Install with optional dependencies ``pip install 'cobralib[mysql, postgresql]'``

Bug Report
##########
#. Despite the fact that the test suite passes on Mac and Linux, the Github tests appear to be failing due to a mismatch in libraries.

Future Work
###########
#. Strengthen unit testing for existing functions and classes
#. Strenghten typing requirements for functions in io.py (yaml, json, xml, etc)
#. Add support for Oracle RDBMS
#. Add functionality for database backup for all db classes
#. Add functionality for database migration for all db classes
#. Consider C++ implementation for linked list and binary search trees
