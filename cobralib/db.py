# Import necessary packages here
import re
import sqlite3

import pandas as pd

try:
    from mysql.connector import (
        DatabaseError,
        Error,
        InterfaceError,
        ProgrammingError,
        connect,
    )
except ImportError:
    msg = "Warning: mysql-connector-python package is not installed. "
    msg += "Some features may not work."
    # Handle the case when mysql-connector is not available
    print(msg)

from cobralib.io import (
    read_excel_columns_by_headers,
    read_pdf_columns_by_headers,
    read_text_columns_by_headers,
)

# ==========================================================================================
# ==========================================================================================

# File:    db.py
# Date:    July 17, 2023
# Author:  Jonathan A. Webb
# Purpose: This file contains functions and classes that are used to connect to and
#          manipulate databases
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class MySQLDB:
    """
    A class for connecting to MySQL databases using mysql-connector-python.
    The user can access the conn and cur variables, where conn is the
    connection variable and cur is the connection.cursor() method to
    expand the capability of this class beyond its methods.

    :param username: The username for the database connection.
    :param password: The password for the database connection.
    :param port: The port number for the database connection. Defaulted to 3306
    :param hostname: The hostname for the database connection
                     (default is 'localhost').
    :param database: The database you wish to connect to, defaulted to None
    :raises ConnectionError: If a connection can not be established
    :ivar conn: The connection attribute of the mysql-connector-python module.
    :ivar cur: The cursor method for the mysql-connector-python module.
    :ivar database: The name of the database currently being used.
    """

    def __init__(
        self,
        username: str,
        password: str,
        port: int = 3306,
        hostname: str = "localhost",
        database: str = None,
    ):
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self.database = database
        self.conn = None
        self.cur = None

        self._create_connection(password)
        if self.database is not None:
            self.change_database(database)

    # ------------------------------------------------------------------------------------------

    def change_database(self, db_name: str) -> None:
        """
        Change to the specified database within the server.

        :param db_name: The name of the database to change to.
        :raises ConnectionError: if query fails.
        """
        try:
            self.conn.database = db_name
            self.cur.execute(f"USE {db_name}")
            self.database = db_name
        except ProgrammingError as e:
            # Handle errors related to non-existing databases or insufficient permissions.
            raise ConnectionError(
                f"Failed to change database due to ProgrammingError: {e}"
            )
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(f"Failed to change database due to InterfaceError: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to change database: {e}")

    # ------------------------------------------------------------------------------------------

    def close_connection(self) -> None:
        """
        Close the connection to the server.

        :raises ConnectionError: If the connection does not exist.
        """
        try:
            if self.conn and self.conn.is_connected():
                self.conn.close()
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to close the connection: {e}")

    # ------------------------------------------------------------------------------------------

    def get_databases(self) -> pd.DataFrame:
        """
        Retrieve the names of all databases available to the user.

        :return: A pandas dataframe of database names with a header of Databases
        :raises ConnectionError: If program fails to retrive database

        If you assume the server has three databases available to the username, and
        those databases were ``Inventory``, ``Address``, ``project_data``, you
        could use this class with the following commands.

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           dbs = db.get_dbs()
           db.close_conn()
           print(dbs)
           >> index  Databases
              0      Address
              1      Inventory
              2      project_data

        """
        try:
            self.cur.execute("SHOW DATABASES;")
            databases = self.cur.fetchall()
            return pd.DataFrame(databases, columns=["Databases"])
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(f"Failed to fetch databases due to InterfaceError: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch databases: {e}")

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, db: str = None) -> pd.DataFrame:
        """
        Retrieve the names of all tables within the current database.

        :param db: Database name, defaulted to currently selected database or None
        :return: A pandas dataframe of table names with a header of Tables
        :raises ValueError: If no database is currently selected.
        :raises ConnectionError: If program is not able to get tables

        Assuming the user has a database titled ``Inventory`` which had the
        tables ``Names``, ``Product``, ``Sales``.

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           dbs = db.get_db_tables("Inventory")
           db.close_conn()
           print(dbs)
           >> index  Tables
              0      Names
              1      Product
              2      Sales

        """
        if db is None:
            db = self.database

        if not db:
            raise ValueError("No database is currently selected.")
        msg = f"Failed to fetch tables from {db}"
        try:
            self.cur.execute(f"SHOW TABLES FROM {db}")
            tables = self.cur.fetchall()
            return pd.DataFrame(tables, columns=["Tables"])
        except InterfaceError as e:
            # Handle errors related to the interface.
            msg += f" due to InterfaceError {e}"
            raise ConnectionError(msg)
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch tables from {db}: {e}")

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, db: str = None) -> pd.DataFrame:
        """
         Retrieve the names and data types of the columns within the specified table.

         :param table_name: The name of the table.
         :param db: The database name, defaulted to currently selected database
                    or None
         :return: A pandas dataframe with headers ot Field, Type, Null, Key, Default,
                  and Extra
         :raises ValueError: If the database is not selected at the class level
         :raises ConnectionError: If the columns cannot be retrieved.

         This example shows a scenario where the database analyst has navigated
         into a database

         .. highlight:: python
         .. code-block:: python

            from cobralib.io import MySQLDB

            db = MySQLDB('username', 'password', port=3306, hostname='localhost')
            db.change_db('Address')
            query = '''CREATE TABLE IF NOT EXIST Names (
                name_id INTEGER AUTO_INCREMENT,
                FirstName VARCHAR(20) NOT NULL,
                MiddleName VARCHAR(20),
                LastName VARCHAR(20) NOT NULL,
                PRIMARY KEY (name_id)
            );
            '''
            db.query_db(query)
            cols = db.get_columns('Names')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   auto_increment
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        However, this code can also be executed when not in the database

         .. code-block:: python

            from cobralib.io import MySQLDB

            db = MySQLDB('username', 'password', port=3306, hostname='localhost')
            cols = db.get_columns('Names', 'Address')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   auto_increment
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        """

        if db is None:
            db = self.database

        msg = f"Failed to fetch columns from {table_name}"
        if not db:
            raise ValueError("No database is currently selected.")

        try:
            self.conn.execute(f"SHOW COLUMNS FROM {db}.{table_name}")
            columns_info = self.cur.fetchall()
            df = pd.DataFrame(
                columns_info, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
            )
            return df
        except InterfaceError as e:
            # Handle errors related to the interface.
            msg += f" fue to InterfaceError: {e}"
            raise ConnectionError(msg)
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch columns from {table_name}: {e}")

    # ------------------------------------------------------------------------------------------

    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute a query with placeholders and return the result as a Pandas DataFrame.
        The user of this class should ensure that when applicable they parameteratize
        the inputs to this method to minimize the potential for an injection
        attack

        :param query: The query with placeholders.
        :param params: The values to be substituted into the placeholders
                       (default is an empty tuple).
        :return: A Pandas DataFrame with the query result.
        :raises ValueError: If the database name is not provided.
        :raises ConnectionError: If the query execution fails.

        Example usage when parameters are provided:

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           query = "SELECT * FROM names WHERE name_id = %s"
           params = (2,)
           result = db.query_db(query, params)
           print(result)
           >> index  name_id  FirstName  LastName
              0      2        Fred       Smith

        Example usage when no parameters are provided:

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           query = "SELECT * FROM names"
           result = db.query_db(query)
           print(result)
           >> index  name_id  FirstName  LastName
            0        1        Jon        Webb
            1        2        Fred       Smith
            2        3        Jillian    Webb

        """

        msg = "The number of placeholders in the query does not "
        msg += "match the number of parameters."
        if not self.database:
            raise ValueError("No database is currently selected.")
        num_placeholders = query.count("%s")
        if num_placeholders != len(params):
            raise ValueError(msg)

        try:
            if len(params) == 0:
                self.cur.execute(query)
            else:
                self.cur.execute(query, params)
            rows = self.cur.fetchall()
            if rows:
                column_names = [desc[0] for desc in self.cur.description]
                df = pd.DataFrame(rows, columns=column_names)
                return df
            else:
                return pd.DataFrame()
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(f"Failed to execute query: {e}")
        except Error as e:
            raise ConnectionError(f"Failed to execute query: {e}")

    # ------------------------------------------------------------------------------------------

    def csv_to_table(
        self,
        csv_file: str,
        table_name: str,
        csv_headers: dict[str, type],
        table_headers: list = None,
        delimiter: str = ",",
        skip: int = 0,
    ) -> None:
        """
        Read data from a CSV or TXT file and insert it into the specified table.

        :param csv_file: The path to the CSV file or TXT file.
        :param table_name: The name of the table.
        :param csv_headers: The names of the columns in the TXT file and datatypes
                            as a dictionary.
        :param table_headers: The names of the columns in the table (default is None,
                              assumes CSV column names and table column names
                              are the same).
        :param delimiter: The seperating delimeter in the text file.  Defaulted to
                          ',' for a CSV file, but can work with other delimeters
        :param skip: The number of rows to be skipped if metadata exists before
                     the header definition.  Defaulted to 0
        :raises ValueError: If the CSV file or table name is not provided, or if
                            the number of CSV columns and table columns mismatch.
        :raises Error: If the data insertion fails or the data types are
                       incompatible.

        Assune we have a csv table with the following Columns, ``FirstName``,
        ``MiddleName``, ``LastName``.  Within the ``Names`` database we have
        a table with no entries that has columns for ``First`` and ``Last``.

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           db.change_db('Names')
           db.csv_to_table('csv_file.csv', 'FirstLastName',
                           ['FirstName': str, 'LastName': str],
                           ['First', 'Last'])
           query = "SELDCT * FROM Names;"
           result = db.query_db(query)
           print(result)
           >> index  name_id First   Last
              0      1       Jon     Webb
              1      2       Fred    Smith
              2      3       Jillian Webb

        If instead of a csv file, you have a text file that uses spaces as
        a delimeter, and the first two rows are consumed by file metadata
        before reaching the header, the following code will work

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           db.change_db('Names')
           db.csv_to_table('txt_file.txt', 'FirstLastName',
                           ['FirstName': str, 'LastName': str],
                           ['First', 'Last'], delemeter=r"\\s+", skip=2)
           query = "SELDCT * FROM Names;"
           result = db.query_db(query)
           print(result)
           >> index  name_id First   Last
              0      1       Jon     Webb
              1      2       Fred    Smith
              2      3       Jillian Webb
        """
        if len(csv_headers) == 0:
            raise ValueError("CSV column names are required.")

        try:
            csv_data = read_text_columns_by_headers(
                csv_file, csv_headers, skip=skip, delimiter=delimiter
            )

            if table_headers is None:
                table_headers = list(csv_headers.keys())

            sanitized_columns = [
                self._sanitize_column_name(name) for name in table_headers
            ]

            csv_header_keys = list(csv_headers.keys())

            for _, row in csv_data.iterrows():
                insert_data = {}
                for i, column in enumerate(table_headers):
                    value = row[csv_header_keys[i]]
                    insert_data[column] = value

                placeholders = ", ".join(["%s"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self.cur.execute(query, values)
            self.conn.commit()  # Commit changes
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise Error(f"Failed to insert data into the table: {e}")

    # ------------------------------------------------------------------------------------------

    def excel_to_table(
        self,
        excel_file: str,
        table_name: str,
        excel_headers: dict[str, type],
        table_headers: list = None,
        sheet_name: str = "Sheet1",
        skip: int = 0,
    ) -> None:
        """
        Read data from an Excel file and insert it into the specified table.

        :param excel_file: The path to the Excel file.
        :param table_name: The name of the table.
        :param excel_headers: The names of the columns in the Excel file and their
                              data types as a dictionary
        :param table_headers: The names of the columns in the table (default is None,
                              assumes Excel column names and table column names are
                              the same).
        :param sheet_name: The name of the sheet in the Excel file
                           (default is 'Sheet1').
        :param skip: The number of rows to be skipped if metadata exists before
                     the header definition.  Defaulted to 0
        :raises ValueError: If the Excel file, table name, or sheet name is not
                            provided, or if the number of Excel columns and table
                            columns mismatch.
        :raises Error: If the data insertion fails or the data types are
                       incompatible.

        Assune we have an excel table with the following Columns, ``FirstName``,
        ``MiddleName``, ``LastName``.  Within the ``Names`` database we have
        a table with no entries that has columns for ``First`` and ``Last``.

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           db.change_db('Names')
           db.csv_to_table('excel_file.xlsx', 'FirstLastName',
                           {'FirstName': str, 'LastName': str},
                           ['First', 'Last'])
           query = "SELDCT * FROM Names;"
           result = db.query_db(query)
           print(result)
           >> index  name_id First   Last
              0      1       Jon     Webb
              1      2       Fred    Smith
              2      3       Jillian Webb
        """
        if len(excel_headers) == 0:
            raise ValueError("Excel column names are required.")

        try:
            excel_data = read_excel_columns_by_headers(
                excel_file, sheet_name, excel_headers, skip
            )
            if table_headers is None:
                table_headers = list(excel_headers.keys())

            sanitized_columns = [
                self._sanitize_column_name(name) for name in table_headers
            ]

            excel_header_keys = list(excel_headers.keys())

            for _, row in excel_data.iterrows():
                insert_data = {}
                for i, column in enumerate(table_headers):
                    value = row[excel_header_keys[i]]
                    insert_data[column] = value

                placeholders = ", ".join(["%s"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self.cur.execute(query, values)

            self.conn.commit()
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise Error(f"Failed to insert data into the table: {e}")

    # ------------------------------------------------------------------------------------------

    def pdf_to_table(
        self,
        pdf_file: str,
        table_name: str,
        pdf_headers: dict[str, type],
        table_columns: list = None,
        table_idx: int = 0,
        page_num: int = 0,
        skip: int = 0,
    ) -> None:
        """
        Read a table from a PDF file and insert it into the specified MySQL table.

        :param pdf_file: The path to the PDF file.
        :param table_name: The name of the MySQL table.
        :param pdf_headers: A dictionary of column names in the PDF and their data
                            types.
        :param table_columns: The names of the columns in the MySQL table
                              (default is None, assumes PDF column names and MySQL
                              column names are the same).
        :param table_idx: Index of the table in the PDF (default: 0).
        :param page_num: Page number from which to extract the table (default: 0).
        :param skip: The number of rows to skip in the PDF table.
        :raises ValueError: If the PDF file, table name, or sheet name is not
                            provided, or if the number of PDF headers and table
                            columns mismatch.
        :raises Error: If the data insertion fails or the data types are
                       incompatible.
        """

        if len(pdf_headers) == 0:
            raise ValueError("PDF headers are required.")

        try:
            # Read the table from the PDF file
            pdf_data = read_pdf_columns_by_headers(
                pdf_file, pdf_headers, table_idx, page_num, skip
            )

            if table_columns is None:
                table_columns = list(pdf_headers.keys())

            sanitized_columns = [
                self._sanitize_column_name(name) for name in table_columns
            ]
            pdf_header_keys = list(pdf_headers.keys())

            for _, row in pdf_data.iterrows():
                insert_data = {}
                for i, column in enumerate(table_columns):
                    value = row[pdf_header_keys[i]]
                    insert_data[column] = value

                placeholders = ", ".join(["%s"] * len(insert_data))
                columns = ", ".join(sanitized_columns)
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self.cur.execute(query, values)

            self.conn.commit()
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise Error(f"Failed to insert data into the table: {e}")

    # ==========================================================================================
    # PRIVATE-LIKE METHOD

    def _create_connection(self, passwd):
        """
        Create a connection to the MySQL database.

        :return: The MySQL connection object.
        """
        try:
            self.conn = connect(
                host=self.hostname, user=self.username, password=passwd, port=self.port
            )
            self.cur = self.conn.cursor()
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(
                f"Failed to create a connection due to InterfaceError: {e}"
            )
        except ProgrammingError as e:
            # Handle programming errors.
            raise ConnectionError(
                f"Failed to create a connection due to ProgrammingError: {e}"
            )
        except DatabaseError as e:
            # Handle other database-related errors.
            raise ConnectionError(
                f"Failed to create a connection due to DatabaseError: {e}"
            )
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to create a connection: {e}")

    # ------------------------------------------------------------------------------------------

    def _sanitize_column_name(self, name: str) -> str:
        """
        Sanitize column names to include only alphanumeric characters and underscores.
        """
        return re.sub(r"\W|^(?=\d)", "_", name)


# ==========================================================================================
# ==========================================================================================


class SQLiteDB:
    """
    A class for connection to a SQLite database file using the sqlite3 python package.
    The usser can access the conn and cur variables, where conn is the connection
    variable and cur is the connection.cursor() method to expand the capability
    of this class beyond its methods.  **NOTE:** If the user passes an incorrect
    database name to the constructor, the class will assume that the user wants
    to create a database of that name, and will create a new database file.

    :param database: The name of the database file to include its path length.
    :raises ConnectionError: If a connection can not be established.
    :ivar conn: The connection attribute of the mysql-connector-python module.
    :ivar cur: The cursor method for the mysql-connector-python module.
    :ivar database: The name of the database currently being used.
    """

    def __init__(self, database: str = None):
        self.database = database
        self.conn = None
        self.curr = None

        self._create_connection()

    # ------------------------------------------------------------------------------------------

    def close_connection(self) -> None:
        """
        Close the connection to tjhe SQLite database
        """
        self.conn.close()

    # ------------------------------------------------------------------------------------------

    def change_database(self, db_name: str) -> None:
        """
        Method to change the connection from one database file to another

        :paramn db_name: The new database file to be used to include the path length
        """
        self.database = db_name
        self.close_connection()
        self._create_connection()

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, db_name: str = None) -> pd.DataFrame:
        if db_name is None:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
            except sqlite3.Error as e:
                raise Error(f"Failed to retrieve tables: {e}")

            return df
        else:
            db = self.database
            self.close_connection()
            self.database = db_name
            self._create_connection()
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
            except sqlite3.Error as e:
                raise Error(f"Failed to retrieve tables: {e}")
            self.close_connection()
            self.database = db
            self._create_connection()
            return df

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_connection(self) -> None:
        """
        Create a connection to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.database)
            self.cur = self.conn.cursor()
        except sqlite3.DatabaseError as e:
            raise ConnectionError(
                f"Failed to create a connection due to DatabaseError: {e}"
            )


# ==========================================================================================
# ==========================================================================================
# eof
