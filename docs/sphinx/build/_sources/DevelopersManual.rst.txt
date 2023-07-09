*****************
Developers Manual
*****************
The various classes, methods and functions contained within this document enable
easy implementation of utilities that are relevant to the average Python user.

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

YAML Files
==========

.. autofunction:: cobralib.io.read_yaml_file
