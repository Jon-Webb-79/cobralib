**************************
Database Management System
**************************
The io module was written to contain functions and classes that can simplify and
standardize the way a user interacts with Relational Database Management Systems(RDBMS).
This module contains classes that a user can use and expand upong to interact
with Microsoft SQL-Server, MySQL, PostGreSQL, and SQLite.  In addition,
that class contains a comman interface for all four RDBM systems.  **NOTE:** Future
versions of this library may also contain interfaces for OracleDB.

Database Commonality
====================
This library impelments several classes that enable a user to use and interact with
different database.  Each class is written with the :ref:`Protocol Overview` class
definition so they will have a common interface.  Each class is further described
in the :ref:`SQL Overview` section; however, it should be noticed, that with exception
of the class instantiation, each method maintains the same interface.

.. _Protocol Overview:

Protocol Class
==============
The Protocol class ``RelationalDB`` provides an implicit interface for the development of all database classes.
This class provides a contract to all future developers that guides the implementation of each class.

.. autoclass:: cobralib.db.RelationalDB
   :members:

.. _SQL Overview:

SQL Classes
===========
This section outlines the classes that enable a user to interface with MySQL, PostGreSQL, SQLite,
and Microsoft SQLServer.  With exception of the class instantiation, the interfaces for the methods
of each class are identical, which enables a user to easily switch between the use of the different
databases.

.. autoclass:: cobralib.db.MySQLDB
   :members:

.. autoclass:: cobralib.db.PostGreSQLDB
   :members:

.. autoclass:: cobralib.db.SQLiteDB
   :members:

.. autoclass:: cobralib.db.SQLServerDB
   :members:
