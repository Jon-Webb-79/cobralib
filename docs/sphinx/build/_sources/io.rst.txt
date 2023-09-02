*******************
Input / Output (io)
*******************
The io module contains several functions and classes that can be used to read
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
``.xls``, and ``.xlsx``, and ``.pdf`` files.

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
This class can be used to read a YAML file or a file with a YAML like structure.

.. autoclass:: cobralib.io.ReadYAML
   :members:

.. The following functions are wrappers are in essence created as a wrapper
.. around the PyYaml package and can be used to read from and write to yaml
.. files.  The total functionality enabled by these function can
.. be explored in the `PyYaml <https://pyyaml.org/wiki/PyYAMLDocumentation>`_ documentation.

Logger
======
This class is a wrapper around the logging module that adds the ability
to truncate a log file to a user specified number of log values.

.. autoclass:: cobralib.io.Logger
   :members:

.. autofunction:: cobralib.io.write_yaml_file
