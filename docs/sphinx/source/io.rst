*******************
Input / Output (io)
*******************
The io module contains several functions and classes that can be used to read
various ASCII based files.

.. _read_key_words:

ReadKeyWords
============
The ``ReadKeyWords`` class is a multi-purpose class that enables a user to read in
several different configuration file formats, and in addition, it allows a user
to create a configuration file with a mixture of YAML, JSON, and XML data.
While this class can read in data of any ASCII based text format, when mixing
configuration formats it is recommended that the .jwc format be used.  In
addition this class inherits the :ref:`ReadYAML <read_yaml>`, :ref:`ReadJSON <read_json>`,
and :ref:`ReadXML <read_xml>` classes.  Further information on the ReadKeyWords
class can be found in the documentation for the inherited classes.

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

.. _read_yaml:

Read YAML
=========
This class inherited by the :ref:`ReadKeyWords <read_key_words>` class;
however, it can be independently used

.. autoclass:: cobralib.io.ReadYAML
   :members:

.. _read_json:

Read JSON
=========
This class inherited by the :ref:`ReadKeyWords <read_key_words>` class;
however, it can be independently used

.. autoclass:: cobralib.io.ReadJSON
   :members:

.. _read_xml:

Read XML
========
This class inherited by the :ref:`ReadKeyWords <read_key_words>` class;
however, it can be independently used

.. autoclass:: cobralib.io.ReadXML
   :members:

Logger
======
This class is a wrapper around the logging module that adds the ability
to truncate a log file to a user specified number of log values.

.. autoclass:: cobralib.io.Logger
   :members:

.. autofunction:: cobralib.io.write_yaml_file
