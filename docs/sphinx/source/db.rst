**************************
Database Management System
**************************
The io module was written to contain functions and classes that can simplify and
standardize the way a user interacts with Relational Database Management Systems(RDBMS).
This module contains classes that a user can use and expand upong to interact
with Microsoft SQL-Server, MySQL, PostGreSQL, and SQLite.  In addition,
that class contains a comman interface for all four RDBM systems.  **NOTE:** Future
versions of this library may also contain interfaces for OracleDB.

.. _rel_db:
relational_database
===================
The ``relational_database`` function provides a common interface to the Microsfot SQL-Server,
MySQL, PostGreSQL, and SQLite Relational Database Management Systems.  This function
returns an object of ``MySQLDB``, ``PostGreSQLDB`` or ``SQLiteDB`` which is described
in the :ref:`SQL Classes<SQL Overview>` Section of this documnet.  The form of these classes
must conform to the interfaces of the Protocol class titled :ref:`RelationalDatabase<Protocol Overview>`.

.. autofunction:: cobralib.db.relational_database

The ``RelationalDB`` object returned by this ``relational_database`` function is described in
the :ref:`RelationalDatabase<Protocol Overview>` Section. The following are examples for how
these methods can be used.

close_connection
****************
The close connection methods closes the database and the the server connection.  This method
is further demonstrated in each example.

.. code-block:: python

   # Code example for connection to a NySQL server instance
   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="MYSQL", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='database_name')

   # close connection
   db.close_connection()

.. code-block:: python

   # Code example for connection to a SQLite instance
   from cobralib.db import relational_database

   # open connection (SQLite only needs the database_file name to be passed in the constructor
   db = relational_database(db_type="SQLITE", database='database_name')

   # close connection
   db.close_connection()

change_database
***************
This method allows a user to change from one database to another

.. code-block:: python

   # Code example with PostGreSQL
   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="POSTGRES", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='first_db')
   print(db.database)

   db.change_database('second_db')
   print(db.database)

   # close connection
   db.close_connection()

This produces the following output, and changes the cursor to interact with the new database

.. code-block:: bash

   first_db
   second_db

get_databases
*************
This method allows a user to return a pandas dataframe containing a list of all databases
in the server.

.. code-block:: python

   # Code example with PostGreSQL
   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="POSTGRES", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='first_db')
   df = db.get_databases()
   print(df)
   db.close_connection()

This method will return a value similar to the one shown below where db_one, db_two, and db_three
represent databases within the server

.. code-block:: bash

       Databases
   0   db_one
   1   db_two
   2   db_two

SQLite does not contain true databases, and instead employes database files, typically ending
with a .db.  Implementing this function with SQLite will give the following results.

.. code-block:: python

   from cobralib.db import relational_database

   # open connection (SQLite only needs the database_file name to be passed in the constructor
   db = relational_database(db_type="SQLITE", database='database_name')
   df = db.get_databases()
   print(df)
   # close connection
   db.close_connection()

.. code-block:: bash

   SQLite does not support databases, returning an empty dataframe

       Databases

get_database_tables
*******************
This method allows a user to return a pandas dataframe containing all of the tables
in the current, or a user selected database.

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="MYSQL", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='first_db')
   df = db.get_database_tables()

   # - While in first_db, we can access second_db tables, assuming your password
   #   and username have access to the second database
   new_df = db.get_database_tables('second_db')
   print(df)
   print()
   print(new_df)

   # While in db_one
   db.close_connection()

.. code-block:: bash

       Tables
   0   first_db_table_one
   1   first_db_table_two
   2   first_db_table_two

       Tables
   0   second_db_table_one
   1   second_db_table_two
   2   second_db_table_three

get_table_columns
*****************
This method will return a list of table column names and their attributes.  The user
can select from a table within their current database or a database that they
are not currently in, assuming they have password permission to use the other database,
with the expception of SQLite which does not require a password.

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="MYSQL", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='first_db')
   df = db.get_table_columns('Names')
   print(df)
   db.close_connection()

.. code-block:: bash

         Field      Type        Null   Key     Default  Extra
   0     name_id    Integer     True   Primary  False   auto_increment
   1     FirstName  Varchar(20) False  NA       False   None
   2     MiddleName Varchar(20) True   NA       False   None
   3     LastName   Varchar(20) False  NA       False   None

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="MYSQL", username='usernaame', password='password',
                            hostname='localhost', port=3306, database='first_db')

   # Get table attributes from a table in another database
   df = db.get_table_columns('Names', 'second_db')
   print(df)
   db.close_connection()

.. code-block:: bash

         Field      Type        Null   Key     Default  Extra
   0     name_id    Integer     True   Primary  False   auto_increment
   1     FirstName  Varchar(20) False  NA       False   None
   2     MiddleName Varchar(20) True   NA       False   None
   3     LastName   Varchar(20) False  NA       False   None

execute_query
*************
This method allows a user to execute a databse query that can interact with the database and return
no information, or it can also return information in a pandas dataframe.  Furthermore for SQL injection
attack protectionl this method allows a user to parameterize their query and pass parameters as
a seperate attribute in the method. **NOTE:**, Usually when using ``sqlite3`` to manage a SQLite
interface, parameters are passed as a ``?``; however, in an effort to standardize the interface
params are passed as ``%s`` to mirror the behavior of ``mysql-connector-python`` and ``postgresql``.

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="SQLITE", database='first_db.db')
   query = """CREATE TABLE IF NOT EXISTS Names (
       name_id INTEGER PRIMARY KEY AUTOINCREMENT,
       FirstName VARCHAR(20) NOT NULL,
       MiddleName VARCHAR(20),
       LastName VARCHAR(20) NOT NULL
    );
   """
   db.execute_query(query)
   db.execute_query("INSERT INTO TABLE Names (FirstName, LastName) VALUES('Jon', 'Webb';")
   db.execute_query("INSERT INTO TABLE Names (FirstName, LastName) VALUES('Jillian', 'Webb';")
   db.execute_query("INSERT INTO TABLE Names (FirstName, MiddleName, LastName) VALUES('Chris', 'Tate', 'Smith';")
   df = db.execute_query("SELECT * FROM Names;")
   new_df.execute_query("SELECT * FROM Names WHERE LastName = %s;", ('Webb', ))
   print(df)
   print()
   print(new_df)
   db.close_connection()

.. code-block:: bash

         name_id  FirstName  MiddleName  LastNam
   0     1        Jon                    Webb
   1     2        Jillian                Webb
   2     3        Chris      Tate        Smith

         name_id  FirstName  MiddleName  LastNam
   0     1        Jon                    Webb
   1     2         Jillian                Webb

csv_to_table
************
This method allows a user to read in specific columns from a csv table, and map them
to the column names of a SQL table.  For example assume we have a csv file with the following
format. **NOTE:** The following method also has a skip attribute that can be used to skip
rows in a csv or other ASCII based text file before reading in a header.

.. code-block:: bash

   Product,Inventory
   Apple,5
   Banana,12
   Cucumber,20
   Peach,3

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="SQLITE", database='first_db.db')
   query = """CREATE TABLE IF NOT EXISTS Inventory (
       inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
       Prd VARCHAR(20) NOT NULL,
       Inv INTEGER
    );
   """
   db.execute_query(query)
   csv_file = "inventory.csv"
   table_name = 'inventory'
   dat_type = {"Product": str, "Inventory": int}
   # Table cols are optional if csv file and table have same header names
   table_cols = ["Prd", "Inv"]
   db.csv_to_table(csv_file, table_name, dat_type, table_cols)
   df = db.execute_query("SELECT * FROM Inventory;")
   print(df)
   db.close_connection()

.. code-block:: bash

         inv_id   Prd      Inv
   0     1        Apple    5
   1     2        Banana   12
   2     3        Cucumber 20
   3     4        Peach    3

This method can also be used to read data in from space delimited files

.. code-block:: bash

   Product   Inventory
   Apple     5
   Banana    12
   Cucumber  20
   Peach     3

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="SQLITE", database='first_db.db')
   query = """CREATE TABLE IF NOT EXISTS Inventory (
       inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
       Prd VARCHAR(20) NOT NULL,
       Inv INTEGER
    );
   """
   db.execute_query(query)
   csv_file = "inventory.txt"
   table_name = 'inventory'
   dat_type = {"Product": str, "Inventory": int}
   # Table cols are optional if csv file and table have same header names
   table_cols = ["Prd", "Inv"]
   db.csv_to_table(csv_file, table_name, dat_type, table_cols, delimiter=r"\s+")
   df = db.execute_query("SELECT * FROM Inventory;")
   print(df)
   db.close_connection()

.. code-block:: bash

         inv_id   Prd      Inv
   0     1        Apple    5
   1     2        Banana   12
   2     3        Cucumber 20
   3     4        Peach    3

excel_to_table
**************
This method can be used to read in specific columns from an excel file
and feed them into an existing sql table.  Assume we have the following
excel table stored in the sheet name titled test.

.. code-block:: bash

   Product   Inventory
   Apple     5
   Banana    12
   Cucumber  20
   Peach     3

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="SQLITE", database='first_db.db')
   query = """CREATE TABLE IF NOT EXISTS Inventory (
       inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
       Prd VARCHAR(20) NOT NULL,
       Inv INTEGER
    );
   """
   db.execute_query(query)
   excel_file = "inventory.xlsx"
   table_name = 'inventory'
   dat_type = {"Product": str, "Inventory": int}
   # Table cols are optional if csv file and table have same header names
   table_cols = ["Prd", "Inv"]
   db.excel_to_table(excel_file, table_name, dat_type, table_cols, sheet_name="test")
   df = db.execute_query("SELECT * FROM Inventory;")
   print(df)
   db.close_connection()

.. code-block:: bash

         inv_id   Prd      Inv
   0     1        Apple    5
   1     2        Banana   12
   2     3        Cucumber 20
   3     4        Peach    3

pdf_to_table
************
While excel files and csv files are some of the most common data storage methods, data can also
be found within vectorized pdf files.  This method allows a user to extract data from
vectorized pdf files, and can read data in from tables that span multiple pages.  Imagine
a pdf table has the following structure.  The pdf table exists as the 3rd table on page 2
of the document.


.. code-block:: bash

   Product   Inventory
   Apple     5
   Banana    12
   Cucumber  20
   Peach     3

.. code-block:: python

   from cobralib.db import relational_database

   # open connection, user must pass a database name
   db = relational_database(db_type="SQLITE", database='first_db.db')
   query = """CREATE TABLE IF NOT EXISTS Inventory (
       inv_id INTEGER PRIMARY KEY AUTOINCREMENT,
       Prd VARCHAR(20) NOT NULL,
       Inv INTEGER
    );
   """
   db.execute_query(query)
   excel_file = "inventory.xlsx"
   table_name = 'inventory'
   dat_type = {"Product": str, "Inventory": int}
   # Table cols are optional if csv file and table have same header names
   table_cols = ["Prd", "Inv"]
   db.excel_to_table(excel_file, table_name, dat_type, table_cols, table_idx=2,
                     page_num=2)
   df = db.execute_query("SELECT * FROM Inventory;")
   print(df)
   db.close_connection()

.. code-block:: bash

         inv_id   Prd      Inv
   0     1        Apple    5
   1     2        Banana   12
   2     3        Cucumber 20
   3     4        Peach    3

.. _Protocol Overview:

Protocol Class
==============
The :ref:`relational_database<rel_db>` function implements a Factory Pattern to create an object of type ``RelationalDB``.
Any class that is implemented in the factory pattern must constrain to the interface described in the ``RelationalDB`` Protocol
class below.

.. autoclass:: cobralib.db.RelationalDB
   :members:

.. _SQL Overview:

SQL Classes
===========
The classes described in this section are used in the Factory Patter which build the :ref:`relational_database<rel_db>` function.
However, a user can also import and access these classes if they wish to inherit them and build upon their capability.

.. autoclass:: cobralib.db.MySQLDB
   :members:

.. autoclass:: cobralib.db.PostGreSQLDB
   :members:

.. autoclass:: cobralib.db.SQLiteDB
   :members:
