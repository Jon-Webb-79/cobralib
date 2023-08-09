**
io
**
The io module contains several functions and classes that can be user to read
various ASCII based files.

ReadKeyWords
============
The ``ReadKeyWords`` class is mean to allow a user to read any ASCII based text
file, look for keywords and read in the value to the right of th ekey word.  In
essense this enables a user to use a ``.txt`` file as a basic configuration file.

.. autoclass:: cobralib.io.ReadKeyWords
   :members:

Read Columnar Data
==================
The following functions can be used to read columnar data from ``.txt``, ``.csv``,
``.xls``, and ``.xlsx`` files.

.. autofunction:: cobralib.io.read_csv_columns_by_headers

.. autofunction:: cobralib.io.read_csv_columns_by_index

.. autofunction:: cobralib.io.read_text_columns_by_headers

.. autofunction:: cobralib.io.read_text_columns_by_index

.. autofunction:: cobralib.io.read_pdf_columns_by_headers

.. autofunction:: cobralib.io.read_pdf_columns_by_index

.. autofunction:: cobralib.io.read_excel_columns_by_headers

.. autofunction:: cobralib.io.read_excel_columns_by_index

YAML Files
==========
The following functions are wrappers arund pyyaml and can be used
to read from and write to yaml files

.. autofunction:: cobralib.io.read_yaml_file

.. autofunction:: cobralib.io.write_yaml_file

Logger
======
This class is a wrapper around the logging module that adds the ability
to truncate a log file to a user specified number of log values.

.. autoclass:: cobralib.io.Logger
   :members:
