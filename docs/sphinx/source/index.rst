.. Core Utilities documentation master file, created by
   sphinx-quickstart
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Cobalib documentation!
=================================

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
The user instructions for this application is shown in :doc:`io` and :doc `db`.


Contributing
============
Pull requests are welcome.  For major changes, please open an issue first to discuss what
you would like to change.  Please make sure to include and update tests as well
as relevant cod-strings and sphinx updates.

License
=======
This project uses a basic MIT license
