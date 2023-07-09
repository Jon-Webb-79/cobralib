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


.. image:: https://github.com/Jon-Webb-79/py_util_lib/workflows/Tests/badge.svg?cache=none
    :target: https://github.com/Jon-Webb-79/py_util_lib/actions

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
List code package requirements here

Installation
############
In order to download this repository from github, follow these instructions

#. Install poetry globally on your computer. Follow the instructions from the
   `Poetry <https://python-poetry.org/docs/>`_ website
#. Set the poetry virtual environment with the following command ``poetry config virtualenvs.in-project true``
#. Ensure you have .git installed on your computer.
#. At your desired location create a directory titled ``cobralib``
#. Open a terminal (Bash, zsh or DOS) and cd to the ``cobralib`` directory
#. Type ``git clone https://github.com/Jon-Webb-79/cobralib.git``
#. Install packages with ``poetry install``
#. In the future this repository may also be available on PyPi
