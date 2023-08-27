# Import necessary packages here
import re
import sqlite3
from typing import Any, Protocol

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

try:
    import pgdb
except ImportError:
    msg = "Warning: postgresql package is not installed. "
    msg += "Some features may not work."
    # Handle the case when mysql-connector is not available
    print(msg)

try:
    import pyodbc
except ImportError:
    msg = "Warning: pyodbc package is not installed. "
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


class RelationalDB(Protocol):
    """
    A protocol class to handle structural sub-typing of classes used to read and
    interact with relational databases

    :ivar database: The name of the database currently being used
    :ivar conn: The connection attribute of the database management system
    :ivar cur: The cursor attribute of the database management system.
    :ivar db_engine: A string representing the type of database engine
    :raises ConnectionError: If a connection can not be established

    More to be added later
    """

    _database: str
    _db_engine: str
    _conn: Any
    _cur: Any

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        ...

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        ...

    # ------------------------------------------------------------------------------------------

    # proprty
    def db_engine(self) -> str:
        """
        Protection for the _db_engine attribute
        """
        ...

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        ...

    # ------------------------------------------------------------------------------------------

    def close_connection(self) -> None:
        """
        Close the connection to the database managment system

        :raises ConnectionError: If the connection does not exist.
        """
        ...

    # ------------------------------------------------------------------------------------------

    def change_database(self, database: str) -> None:
        """
        Method to change the connection from one database to another.

        :param database: The new database or database file to be used.  If a database
                        file, this must include the path length.
        :raises ConnectionError: if query fails.
        """
        ...

    # ------------------------------------------------------------------------------------------

    def get_databases(self) -> pd.DataFrame:
        """
        Retrieve the names of all databases available to the user.

        :return: A pandas dataframe of database names with a header of Databases
        """
        ...

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        """
        Method to retrieve a dataframe containing a list of all tables wtihin
        the SQL database or database file.

        :param database: The name of the database or database file that the tables
                         will be retrieved from.
        :return df: A dataframe containing all information relating to the tables
                    within the database or database file.
        :raises ConnectionError: If program is not able to get tables
        """
        ...

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        """
        Retrieve the names and data types of the columns within the specified table.

        :param table_name: The name of the table.
        :param database: The database name, defaulted to currently selected database
                         or None
        :return: A Pandas Dataframe with the table information
        :raises ValueError: If the database is not selected at the class level
         :raises ConnectionError: If the columns cannot be retrieved.
        """
        ...

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
        """
        ...

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
        """
        ...

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
                              data types as a dictionary.
        :param table_headers: The names of the columns in the table (default is None,
                              assumes Excel column names and table column names are
                              the same).
        :param sheet_name: The name of the sheet in the Excel file (default is 'Sheet1').
        :param skip: The number of rows to be skipped if metadata exists before
                     the header definition. Defaulted to 0.
        :raises ValueError: If the Excel file, table name, or sheet name is not
                            provided, or if the number of Excel columns and table
                            columns mismatch.
        :raises Error: If the data insertion fails or the data types are
                       incompatible.
        """
        ...

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
        Read a table from a PDF file and insert it into the specified SQLite table.

        :param pdf_file: The path to the PDF file.
        :param table_name: The name of the SQLite table.
        :param pdf_headers: A dictionary of column names in the PDF and their data
                            types.
        :param table_columns: The names of the columns in the SQLite table
                              (default is None, assumes PDF column names and SQLite
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
        ...


# ==========================================================================================
# ==========================================================================================


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
    :ivar db_engine: A string describing the database engine
    :ivar database: The name of the database currently being used.
    """

    _db_engine: str = "MYSQL"

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        port: int = 3306,
        hostname: str = "localhost",
    ):
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self._database = database

        self._create_connection(password)
        self.change_database(database)

    # ------------------------------------------------------------------------------------------

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        return self._conn

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        return self._cur

    # ------------------------------------------------------------------------------------------

    @property
    def db_engine(self) -> str:
        """
        Protection for the _db_engine attribute
        """
        return self._db_engine

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        return self._database

    # ------------------------------------------------------------------------------------------

    def change_database(self, database: str) -> None:
        """
        Change to the specified database within the server.

        :param database: The name of the database to change to.
        :raises ConnectionError: if query fails.
        """
        try:
            self._cur.execute(f"USE {database}")
            self._database = database
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
            if self._conn and self._conn.is_connected():
                self._conn.close()
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
           dbs = db.get_databases()
           db.close_conn()
           print(dbs)
           >> index  Databases
              0      Address
              1      Inventory
              2      project_data

        """
        try:
            self._cur.execute("SHOW DATABASES;")
            databases = self._cur.fetchall()
            return pd.DataFrame(databases, columns=["Databases"])
        except InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(f"Failed to fetch databases due to InterfaceError: {e}")
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch databases: {e}")

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        """
        Retrieve the names of all tables within the current database.

        :param database: Database name, defaulted to currently selected database or None
        :return: A pandas dataframe of table names with a header of Tables
        :raises ValueError: If no database is currently selected.
        :raises ConnectionError: If program is not able to get tables

        Assuming the user has a database titled ``Inventory`` which had the
        tables ``Names``, ``Product``, ``Sales``.

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           dbs = db.get_database_tables("Inventory")
           db.close_conn()
           print(dbs)
           >> index  Tables
              0      Names
              1      Product
              2      Sales

        """
        if database is None:
            database = self.database

        if not database:
            raise ValueError("No database is currently selected.")
        msg = f"Failed to fetch tables from {database}"
        try:
            self._cur.execute(f"SHOW TABLES FROM {database}")
            tables = self._cur.fetchall()
            return pd.DataFrame(tables, columns=["Tables"])
        except InterfaceError as e:
            # Handle errors related to the interface.
            msg += f" due to InterfaceError {e}"
            raise ConnectionError(msg)
        except Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch tables from {database}: {e}")

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        """
         Retrieve the names and data types of the columns within the specified table.

         :param table_name: The name of the table.
         :param database: The database name, defaulted to currently selected database
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
            db.change_database('Address')
            query = '''CREATE TABLE IF NOT EXIST Names (
                name_id INTEGER AUTO_INCREMENT,
                FirstName VARCHAR(20) NOT NULL,
                MiddleName VARCHAR(20),
                LastName VARCHAR(20) NOT NULL,
                PRIMARY KEY (name_id)
            );
            '''
            db.execute_query(query)
            cols = db.get_table_columns('Names')
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
            cols = db.get_table_columns('Names', 'Address')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   auto_increment
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        """

        if database is None:
            database = self.database

        msg = f"Failed to fetch columns from {table_name}"
        if not database:
            raise ValueError("No database is currently selected.")

        try:
            self._cur.execute(f"SHOW COLUMNS FROM {database}.{table_name}")
            columns_info = self._cur.fetchall()
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
           result = db.execute_query(query, params)
           print(result)
           >> index  name_id  FirstName  LastName
              0      2        Fred       Smith

        Example usage when no parameters are provided:

        .. code-block:: python

           from cobralib.io import MySQLDB

           db = MySQLDB('username', 'password', port=3306, hostname='localhost')
           query = "SELECT * FROM names"
           result = db.execute_query(query)
           print(result)
           >> index  name_id  FirstName  LastName
            0        1        Jon        Webb
            1        2        Fred       Smith
            2        3        Jillian    Webb

        """

        msg = "The number of placeholders in the query does not match "
        msg += "the number of parameters."
        if not self.database:
            raise ValueError("No database is currently selected.")

        num_placeholders = query.count("%s")
        if num_placeholders != len(params):
            raise ValueError(msg)

        try:
            if len(params) == 0:
                self._cur.execute(query)
            else:
                self._cur.execute(query, params)
            if (
                query.strip()
                .upper()
                .startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            ):
                self._conn.commit()

            # Check if there's a result set available
            if self._cur.description:
                rows = self._cur.fetchall()
                column_names = [desc[0] for desc in self._cur.description]
                df = pd.DataFrame(rows, columns=column_names)
                return df
            else:
                return pd.DataFrame()  # No rows to return

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
                self._cur.execute(query, values)
            self._conn.commit()  # Commit changes
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
                self._cur.execute(query, values)

            self._conn.commit()
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
                self._cur.execute(query, values)

            self._conn.commit()
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
            self._conn = connect(
                host=self.hostname, user=self.username, password=passwd, port=self.port
            )
            self._cur = self._conn.cursor()
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
    :ivar conn: The connection attribute of the sqlite3 module.
    :ivar cur: The cursor method for the sqlite3 module.
    :ivar database: The name of the database currently being used.
    :ivar db_engine: A string describing the database engine
    """

    _db_engine: str = "SQLITEDB"

    def __init__(self, database: str):
        self._database = database
        self._create_connection()

    # ------------------------------------------------------------------------------------------

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        return self._conn

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        return self._cur

    # ------------------------------------------------------------------------------------------

    @property
    def db_engine(self) -> str:
        """
        Protection for the _db_engine attribute
        """
        return self._db_engine

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        return self._database

    # ------------------------------------------------------------------------------------------

    def close_connection(self) -> None:
        """
        Close the connection to tjhe SQLite database
        """
        self._conn.close()

    # ------------------------------------------------------------------------------------------

    def change_database(self, database: str) -> None:
        """
        Method to change the connection from one database file to another

        :paramn database: The new database file to be used to include the path length
        """
        self._database = database
        self.close_connection()
        self._create_connection()

    # ------------------------------------------------------------------------------------------
    def get_databases(self) -> pd.DataFrame:
        """
        Method included for compatibility with RelationalDB Protocol class. This method
        returns an empty dataframe since SQLite does not support true databases.

        :return : An empty pandas dataframe
        """
        print("SQLite does not support databases, returning an empty dataframe")
        return pd.DataFrame()

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        """
        Method the retrieve a dataframe containing a list of all tables within
        a SQLite database file.  If the user does not pass a database name, the
        method will return the list of tables in the current database.  However,
        the user can also pass this method the name of another database file,
        and this will return a list of tables in that database file/

        :param database: The name of the database or database file that the tables
                         will be retrieved from.
        :return df: A dataframe containing all information relating to the tables
                    within the database or database file.

        Assuming the user has a database titled ``Inventory`` which had the
        tables ``Names``, ``Product``, ``Sales``.

        .. code-block:: python

           from cobralib.io import SQLiteDB

           db = SQLiteDB('test.db')
           dbs = db.get_database_tables("Inventory")
           db.close_connection()
           print(dbs)
           >> index  Tables
              0      Names
              1      Product
              2      Sales
        """
        rename = {"name": "Tables"}
        if database is None:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
                df.rename(columns=rename, inplace=True)
            except sqlite3.Error as e:
                raise Error(f"Failed to retrieve tables: {e}")

            return df
        else:
            original_db = self.database
            self.close_connection()
            self._database = database
            self._create_connection()
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
                df.rename(columns=rename, inplace=True)
            except sqlite3.Error as e:
                raise Error(f"Failed to retrieve tables: {e}")
            self.close_connection()
            self._database = original_db
            self._create_connection()
            return df

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        """
         Retrieve the names and data types of the columns within the specified table.

         :param table_name: The name of the table.
         :param database: The database name, defaulted to currently selected database
                          or None
         :return: A pandas dataframe with headers ot Field, Type, Null, Key, Default,
                  and Extra
         :raises ValueError: If the database is not selected at the class level
         :raises ConnectionError: If the columns cannot be retrieved.

         This example shows a scenario where the database analyst has navigated
         into a database

         .. highlight:: python
         .. code-block:: python

            from cobralib.io import SQLiteDB

            db = SQLiteDB('test_db.db')
            query = '''CREATE TABLE IF NOT EXIST Names (
                name_id INTEGER AUTO_INCREMENT,
                FirstName VARCHAR(20) NOT NULL,
                MiddleName VARCHAR(20),
                LastName VARCHAR(20) NOT NULL,
                PRIMARY KEY (name_id)
            );
            '''
            db.execute_query(query)
            cols = db.get_table_columns('Names')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   autoincrement
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        However, this code can also be executed when not in the database

         .. code-block:: python

            from cobralib.io import MySQLDB

            db = MySQLDB('username', 'password', port=3306, hostname='localhost')
            cols = db.get_table_columns('Names', 'Address')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   autoincrement
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        """
        original_db = self.database
        if database is None:
            try:
                # Execute the PRAGMA command to get the table information
                self._cur.execute(f"PRAGMA table_info({table_name})")

                # Fetch all rows from the cursor
                rows = self._cur.fetchall()

                if len(rows) == 0:
                    raise Error(f"The table '{table_name}' does not exist.")

                # The names of the columns in the result set
                columns = ["id", "name", "type", "notnull", "default_value", "pk"]

                # Convert the result set to a DataFrame
                df = pd.DataFrame(rows, columns=columns)

                # Modify the DataFrame to match the output from the MySQLDB method
                df["Field"] = df["name"]
                df["Type"] = df["type"]
                df["Null"] = df["notnull"].map({0: "YES", 1: "NO"})
                df["Key"] = df["pk"].map({0: "", 1: "PRI"})
                df["Default"] = df["default_value"]
                df["Extra"] = ""

                # Only include the relevant columns in the DataFrame
                df = df[["Field", "Type", "Null", "Key", "Default", "Extra"]]

                return df

            except sqlite3.Error as e:
                # Handle any SQLite errors that occur
                raise Error(f"An error occurred: {e}")
        else:
            self.close_connection()
            self._database = database
            self._create_connection()
            try:
                # Execute the PRAGMA command to get the table information
                self._cur.execute(f"PRAGMA table_info({table_name})")

                # Fetch all rows from the cursor
                rows = self._cur.fetchall()

                if len(rows) == 0:
                    raise Error(f"The table '{table_name}' does not exist.")

                # The names of the columns in the result set
                columns = ["id", "name", "type", "notnull", "default_value", "pk"]

                # Convert the result set to a DataFrame
                df = pd.DataFrame(rows, columns=columns)

                # Modify the DataFrame to match the output from the MySQLDB method
                df["Field"] = df["name"]
                df["Type"] = df["type"]
                df["Null"] = df["notnull"].map({0: "YES", 1: "NO"})
                df["Key"] = df["pk"].map({0: "", 1: "PRI"})
                df["Default"] = df["default_value"]
                df["Extra"] = ""

                # Only include the relevant columns in the DataFrame
                df = df[["Field", "Type", "Null", "Key", "Default", "Extra"]]
                self._database = original_db
                self.close_connection()
                self._create_connection()

                return df

            except sqlite3.Error as e:
                self._database = original_db
                self.close_connection()
                self._create_connection()
                # Handle any SQLite errors that occur
                raise Error(f"An error occurred: {e}")

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
        :raises Error: If the query execution fails.

        Example usage when parameters are provided:

        .. code-block:: python

          from mylib.io import SQLiteDB

          db = SQLiteDB('example.db')
          query = "SELECT * FROM names WHERE name_id = ?"
          params = (2,)
          result = db.execute_query(query, params)
          print(result)
          >> index  name_id  FirstName  LastName
             0      2        Fred       Smith

        Example usage when no parameters are provided:

        .. code-block:: python

          from mylib.io import SQLiteDB

          db = SQLiteDB('example.db')
          query = "SELECT * FROM names"
          result = db.execute_query(query)
          print(result)
          >> index  name_id  FirstName  LastName
           0        1        Jon        Webb
           1        2        Fred       Smith
           2        3        Jillian    Webb

        """
        msg = "The number of placeholders in the query does not "
        msg += "match the number of parameters."
        query = query.replace("%s", "?")
        num_placeholders = query.count("?")
        if num_placeholders != len(params):
            raise ValueError(msg)
        try:
            if params:
                self._cur.execute(query, params)
            else:
                self._cur.execute(query)
            if (
                query.strip()
                .upper()
                .startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            ):
                self._conn.commit()

            if self._cur.description:
                columns = [desc[0] for desc in self._cur.description]
                return pd.DataFrame(self._cur.fetchall(), columns=columns)
            else:
                self._conn.commit()
                return pd.DataFrame()

        except sqlite3.InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to execute query: {e}")
        except sqlite3.Error as e:
            raise Error(f"Failed to execute query: {e}")

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

                placeholders = ", ".join(["?"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)
            self._conn.commit()  # Commit changes
        except sqlite3.InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except sqlite3.Error as e:
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
                              data types as a dictionary.
        :param table_headers: The names of the columns in the table (default is None,
                              assumes Excel column names and table column names are
                              the same).
        :param sheet_name: The name of the sheet in the Excel file (default is 'Sheet1').
        :param skip: The number of rows to be skipped if metadata exists before
                     the header definition. Defaulted to 0.
        :raises ValueError: If the Excel file, table name, or sheet name is not
                            provided, or if the number of Excel columns and table
                            columns mismatch.
        :raises Error: If the data insertion fails or the data types are
                       incompatible.
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

                placeholders = ", ".join(["?"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)

            self._conn.commit()
        except sqlite3.InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except sqlite3.Error as e:
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
        Read a table from a PDF file and insert it into the specified SQLite table.

        :param pdf_file: The path to the PDF file.
        :param table_name: The name of the SQLite table.
        :param pdf_headers: A dictionary of column names in the PDF and their data
                            types.
        :param table_columns: The names of the columns in the SQLite table
                              (default is None, assumes PDF column names and SQLite
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

                placeholders = ", ".join(["?"] * len(insert_data))
                columns = ", ".join(sanitized_columns)
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)

            self._conn.commit()
        except sqlite3.InterfaceError as e:
            # Handle errors related to the interface.
            raise Error(f"Failed to insert data into the table: {e}")
        except sqlite3.Error as e:
            # Generic error handler for any other exceptions.
            raise Error(f"Failed to insert data into the table: {e}")

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_connection(self) -> None:
        """
        Create a connection to the SQLite database.
        """
        try:
            self._conn = sqlite3.connect(self.database)
            self._cur = self._conn.cursor()
        except sqlite3.DatabaseError as e:
            raise ConnectionError(
                f"Failed to create a connection due to DatabaseError: {e}"
            )

    # ------------------------------------------------------------------------------------------

    def _sanitize_column_name(self, name: str) -> str:
        """
        Sanitize column names to include only alphanumeric characters and underscores.
        """
        return re.sub(r"\W|^(?=\d)", "_", name)


# ==========================================================================================
# ==========================================================================================


class PostGreSQLDB:
    """
    Initialize the database connection to a PostgreSQL server.

    :param username: The PostgreSQL username.
    :param password: The PostgreSQL password.
    :param database: The name of the database to connect to.
    :param port: The port number for the PostgreSQL server (default is 5432).
    :param hostname: The server's hostname (default is 'localhost').
    :raises ConnectionError: If a connection can not be established.
    :ivar conn: The connection attribute of the sqlite3 module.
    :ivar cur: The cursor method for the sqlite3 module.
    :ivar database: The name of the database currently being used.
    :ivar db_engine: A string describing the database engine
    """

    _db_engine: str = "POSTGRES"

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        port: int = 5432,
        hostname: str = "localhost",
    ):
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self._database = database

        self._create_connection(password, database)

    # ------------------------------------------------------------------------------------------

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        return self._conn

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        return self._cur

    # ------------------------------------------------------------------------------------------

    @property
    def db_engine(self) -> str:
        """
        Protection for the _db_engine attribute
        """
        return self._db_engine

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        return self._database

    # ------------------------------------------------------------------------------------------

    def close_connection(self):
        """
        Close the connection to the PostgreSQL server and database.

        :raises ConnectionError: If there's an issue closing the connection or cursor.
        """
        try:
            if self._cur:
                self._cur.close()
            if self._conn:
                self._conn.close()
        except pgdb.Error as e:
            raise ConnectionError(f"Failed to close the connection: {e}")
        except Exception as e:
            # Generic handler for any other exceptions
            raise ConnectionError(f"Failed to close the connection: {e}")

    # ------------------------------------------------------------------------------------------

    def change_database(self, database: str) -> None:
        """
        Change to a different PostgreSQL database.

        :param database: The name of the database to switch to.
        :raises ConnectionError: If there's an issue establishing a connection
                                 to the new database.
        """
        try:
            # Close the current connection if it exists
            if self._conn:
                self._conn.close()

            # Establish a new connection to the desired database
            self._conn = pgdb.connect(
                database=database,
                user=self.username,
                password=self.password,
                host=self.hostname,
                port=self.port,
            )
            self._database = database
            self._cur = self._conn.cursor()
        except pgdb.DatabaseError as e:
            raise ConnectionError(f"Failed to change to database '{database}': {e}")
        except Exception as e:
            # Generic handler for any other exceptions
            raise ConnectionError(f"Failed to change to database '{database}': {e}")

    # ------------------------------------------------------------------------------------------

    def get_databases(self) -> pd.DataFrame:
        """
        Fetch a list of databases from the PostgreSQL server.

        :return: A pandas DataFrame containing the list of databases with the
                 column header "Databases".
        """
        query = "SELECT datname FROM pg_database;"

        try:
            self._cur.execute(query)
            data = self._cur.fetchall()
            df = pd.DataFrame(data, columns=["Databases"])
            return df
        except pgdb.DatabaseError as e:
            raise Exception(f"Failed to fetch databases: {e}")

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        """
        Fetch a list of tables from the specified or current PostgreSQL database.

        :param database: The name of the database to fetch tables from. If not
                         provided, uses the current database.
        :return: A pandas DataFrame containing the list of tables with the column
                 header "Tables".
        """

        original_db = self._database

        # If db_name is provided, switch to that database
        if database:
            self.change_database(database)

        query = "SELECT tablename FROM pg_tables WHERE schemaname='public';"

        try:
            self._cur.execute(query)
            data = self._cur.fetchall()
            df = pd.DataFrame(data, columns=["Tables"])

            # If db_name was provided, switch back to the original database
            if database:
                self.change_database(original_db)

            return df
        except pgdb.DatabaseError as e:
            if database:
                try:
                    self.change_database(original_db)
                except (pgdb.DatabaseError, pgdb.OperationalError):
                    pass
            raise Exception(f"Failed to fetch tables: {e}")

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        """
        Fetch column details for the given table in the specified or current
        PostgreSQL database.

        :param table_name: The name of the table to fetch column details for.
        :param database: The name of the database the table resides in. If not provided,
                         uses the current database.
        :return: A pandas DataFrame containing column details.
        """

        original_db = self.database

        # If db is provided, switch to that database
        if database:
            self.change_database(database)

        try:
            # Fetch column details
            column_query = f"""
            SELECT column_name as "Field",
                   data_type as "Type",
                   is_nullable = 'YES' as "Null",
                   column_default as "Default",
                   '' as "Key",
                   '' as "Extra"
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """

            self._cur.execute(column_query)
            columns = self._cur.fetchall()
            df = pd.DataFrame(
                columns, columns=["Field", "Type", "Null", "Default", "Key", "Extra"]
            )

            # Fetch primary key
            pk_query = f"""
            SELECT a.attname as "Field", 'Primary' as "Key"
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = '{table_name}'::regclass AND i.indisprimary;
            """

            self._cur.execute(pk_query)
            pks = self._cur.fetchall()
            for pk in pks:
                df.loc[df["Field"] == pk[0], "Key"] = "Primary"

            # - Updating Foreign Key would be a more involved process due to the
            #   way PostgreSQL manages it,
            # skipping that for the moment.

            # If db was provided, switch back to the original database
            if database:
                self.change_database(original_db)

            return df
        except pgdb.DatabaseError as e:
            # - If db was provided and there's an error, try to switch back to
            #   the original database
            if database:
                try:
                    self.change_database(original_db)
                except (pgdb.DatabaseError, pgdb.OperationalError):
                    pass
            raise Exception(f"Failed to fetch table columns: {e}")

    # ------------------------------------------------------------------------------------------

    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Executes the provided SQL query and returns the results as a pandas DataFrame.

        :param query: The SQL query to execute.
        :param params: A tuple of parameters to bind to the query.
        :return: A pandas DataFrame containing the query results.
        """

        try:
            if params:
                self._cur.execute(query, params)
            else:
                self._cur.execute(query)
            if (
                query.strip()
                .upper()
                .startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            ):
                self._conn.commit()

            if self._cur.description:
                columns = [desc[0] for desc in self._cur.description]
                return pd.DataFrame(self._cur.fetchall(), columns=columns)
            else:
                self._conn.commit()
                return pd.DataFrame()
        except (pgdb.DatabaseError, pgdb.OperationalError) as e:
            raise Exception(f"Failed to execute query: {e}")

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

           from cobralib.io import PostGreSQLDB

           db = PostGreSQL('username', 'password', 'Names', port=3306,
                           hostname='localhost')
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

           from cobralib.io import PostGreSQLDB

           db = PostGreSQLDB('username', 'password', 'Names',
                              port=3306, hostname='localhost')
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

        ... [rest of the docstring remains unchanged] ...
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
                self._cur.execute(query, values)
            self._conn.commit()  # Commit changes
        except pgdb.InterfaceError as e:
            # Handle errors related to the interface.
            raise Exception(f"Failed to insert data into the table: {e}")
        except pgdb.DatabaseError as e:
            # Generic error handler for any other exceptions.
            raise Exception(f"Failed to insert data into the table: {e}")

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

           from cobralib.io import PostGreSQLDB

           db = PostGreSQL('username', 'password', 'Names',
                           port=3306, hostname='localhost')
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
        if not excel_headers:
            raise ValueError("Excel column names are required.")

        try:
            # Using pandas to read the Excel file
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
                insert_data = {
                    table_headers[i]: row[excel_header_keys[i]]
                    for i in range(len(table_headers))
                }

                placeholders = ", ".join(["%s"] * len(insert_data))
                columns = ", ".join(sanitized_columns)
                values = tuple(insert_data.values())

                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)

            self._conn.commit()
        except (pgdb.DatabaseError, pgdb.OperationalError) as e:
            raise Exception(f"Failed to insert data into the table: {e}")

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
                self._cur.execute(query, values)

            self._conn.commit()
        except (pgdb.DatabaseError, pgdb.OperationalError) as e:
            # Handle errors related to
            raise Exception(f"Failed to insert data into the table: {e}")

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_connection(self, password: str, database: str) -> None:
        """
        Create a connection to the PostgreSQL database.

        :param password: The PostgreSQL password.
        :param database: The name of the database to connect to.
        :return: The PostgreSQL connection object.
        """
        try:
            self._conn = pgdb.connect(
                database=database,
                host=self.hostname,
                user=self.username,
                password=password,
                port=self.port,
            )
            self._cur = self._conn.cursor()
        except pgdb.OperationalError as e:
            raise ConnectionError(
                f"Failed to create a connection due to OperationalError: {e}"
            )
        except pgdb.ProgrammingError as e:
            raise ConnectionError(
                f"Failed to create a connection due to ProgrammingError: {e}"
            )
        except pgdb.InternalError as e:
            raise ConnectionError(
                f"Failed to create a connection due to InternalError: {e}"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to create a connection: {e}")

    # ------------------------------------------------------------------------------------------

    def _sanitize_column_name(self, name: str) -> str:
        """
        Sanitize column names to include only alphanumeric characters and underscores.
        """
        return re.sub(r"\W|^(?=\d)", "_", name)


# ==========================================================================================
# ==========================================================================================


class SQLServerDB:
    """
    Initialize the SQLServerDB object with connection parameters.

    :param username: The username to connect to the database.
    :param password: The password to connect to the database.
    :param port: The port number to use for the connection. Default is 1433.
    :param hostname: The database server name or IP address. Default is
                    'localhost'.
    :param database: The initial database to connect to (can be changed later).
    :param cert: yes to trust certificat and no to not trust certificate
                 without authentication. Defaulted to yes
    :param driver: The ODBC driver to use for connection. Defaulted to
                   "{ODBC Driver 18 for SQL Server}"
    :raises ConnectionError: If a connection can not be established.
    :ivar conn: The connection attribute of the sqlite3 module.
    :ivar cur: The cursor method for the sqlite3 module.
    :ivar database: The name of the database currently being used.
    :ivar db_engine: A string describing the database engine
    """

    _db_engine: str = "MSSQL"

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        port: int = 1433,
        hostname: str = "localhost",
        cert: str = "yes",
        driver: str = "{ODBC Driver 18 for SQL Server}",
    ):
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self._database = database
        self.driver = driver

        self._create_connection(cert)

    # ------------------------------------------------------------------------------------------

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        return self._conn

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        return self._cur

    # ------------------------------------------------------------------------------------------

    @property
    def db_engine(self) -> str:
        """
        Protection for the _db_engine attribute
        """
        return self._db_engine

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        return self._database

    # ------------------------------------------------------------------------------------------

    def change_database(self, database: str):
        """
        Change the active database for the current connection.

        :param database: The name of the database to switch to.
        :raises ConnectionError: if query fails.
        """
        if not database:
            raise ValueError("Database name is required.")

        # Prevent SQL injection by verifying database name
        if not re.match("^[A-Za-z0-9_]+$", database):
            raise ValueError("Invalid database name provided.")

        try:
            self._cur.execute(f"USE {database}")
            self._conn.commit()
        except pyodbc.ProgrammingError as e:
            # Handle programming errors like syntax errors.
            raise ConnectionError(
                f"Failed to switch database due to ProgrammingError: {e}"
            )
        except pyodbc.DatabaseError as e:
            # Handle other database-related errors like non-existing database.
            raise ConnectionError(f"Failed to switch database due to DatabaseError: {e}")
        except pyodbc.Error as e:
            raise ConnectionError(f"Failed to switch database: {e}")

    # ------------------------------------------------------------------------------------------

    def close_connection(self):
        """
        Close the database connection.
        """
        try:
            if self._cur:
                self._cur.close()
            if self._conn:
                self._conn.close()
        except Error as e:
            raise ConnectionError(f"Failed to close the connection: {e}")

    # ------------------------------------------------------------------------------------------

    def get_databases(self) -> pd.DataFrame:
        """
        Retrieve a list of databases from the SQL Server.

        :return: DataFrame containing the database names.
        :raises ConnectionError: If program fails to retrive database

        If you assume the server has three databases available to the username, and
        those databases were ``Inventory``, ``Address``, ``project_data``, you
        could use this class with the following commands.

        .. code-block:: python

           from cobralib.io import SQLServerDB

           db = SQServerDB('username', 'password', port=3306, hostname='localhost')
           dbs = db.get_databases()
           db.close_conn()
           print(dbs)
           >> index  Databases
              0      Address
              1      Inventory
              2      project_data

        """

        try:
            self._cur.execute("SELECT name FROM sys.databases")
            databases = [row[0] for row in self._cur.fetchall()]
            return pd.DataFrame(databases, columns=["Databases"])
        except pyodbc.ProgrammingError as e:
            # Handle programming errors like syntax errors.
            raise ConnectionError(
                f"Failed to fetch databases due to ProgrammingError: {e}"
            )
        except pyodbc.DatabaseError as e:
            # Handle other database-related errors.
            raise ConnectionError(f"Failed to fetch databases due to DatabaseError: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch databases: {e}")

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        """
        Retrieve a list of tables from the given or current SQL Server database.

        :param database: Optional name of the database to fetch tables from.
        :return: DataFrame containing the table names.

        :raises ValueError: If no database is currently selected.
        :raises ConnectionError: If program is not able to get tables

        Assuming the user has a database titled ``Inventory`` which had the
        tables ``Names``, ``Product``, ``Sales``.

        .. code-block:: python

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
           dbs = db.get_database_tables("Inventory")
           db.close_conn()
           print(dbs)
           >> index  Tables
              0      Names
              1      Product
              2      Sales

        """

        # If no specific database is given, use the current one.
        if database is None:
            database = self._database

        # Remember the original database to switch back later if needed.
        original_database = self._database

        try:
            # If the user provides a different database, switch to it.
            if database != original_database:
                self.change_database(database)

            # Fetch the list of tables.
            self._cur.execute("SELECT table_name FROM information_schema.tables")
            tables = [row[0] for row in self._cur.fetchall()]

            # If we did switch databases, switch back to the original one.
            if database != original_database:
                self.change_database(original_database)

            return pd.DataFrame(tables, columns=["Tables"])

        except pyodbc.ProgrammingError as e:
            # Handle programming errors.
            raise ConnectionError(f"Failed to fetch tables due to ProgrammingError: {e}")
        except pyodbc.DatabaseError as e:
            # Handle other database-related errors.
            raise ConnectionError(f"Failed to fetch tables due to DatabaseError: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch tables: {e}")

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        """
        Retrieve column details of the specified table from the given or current SQL
        Server database.

        :param table_name: Name of the table to fetch column details from.
        :param database: Optional name of the database the table is in.
        :return: DataFrame containing the column details.

        :raises ValueError: If the database is not selected at the class level
         :raises ConnectionError: If the columns cannot be retrieved.

         This example shows a scenario where the database analyst has navigated
         into a database

         .. highlight:: python
         .. code-block:: python

            from cobralib.io import SQLServerDB

            db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
            db.change_database('Address')
            query = '''CREATE TABLE IF NOT EXIST Names (
                name_id INTEGER AUTO_INCREMENT,
                FirstName VARCHAR(20) NOT NULL,
                MiddleName VARCHAR(20),
                LastName VARCHAR(20) NOT NULL,
                PRIMARY KEY (name_id)
            );
            '''
            db.execute_query(query)
            cols = db.get_table_columns('Names')
            db.close_conn()
            print(cols)
            >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   auto_increment
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None

        However, this code can also be executed when not in the database

        .. code-block:: python

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
           cols = db.get_table_columns('Names', 'Address')
           db.close_conn()
           print(cols)
           >> index Field      Type        Null   Key     Default  Extra
               0     name_id    Integer     True   Primary  False   auto_increment
               1     FirstName  Varchar(20) False  NA       False   None
               2     MiddleName Varchar(20) True   NA       False   None
               3     LastName   Varchar(20) False  NA       False   None


        """

        # If no specific database is given, use the current one.
        if database is None:
            database = self._database

        # Remember the original database to switch back later if needed.
        original_database = self._database

        try:
            # If the user provides a different database, switch to it.
            if database != original_database:
                self.change_database(database)

            # Fetch the column details.
            query = f"""
            SELECT
                c.COLUMN_NAME AS [Field],
                c.DATA_TYPE + ISNULL('(' + CAST(c.CHARACTER_MAXIMUM_LENGTH AS VARCHAR)
                + ')', '') AS [Type],
                CASE WHEN c.IS_NULLABLE = 'YES' THEN 'YES' ELSE 'NO' END AS [Null],
                CASE WHEN pk.TABLE_NAME IS NOT NULL THEN 'PRI' ELSE '' END AS [Key],
                c.COLUMN_DEFAULT AS [Default],
                '' AS Extra
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON c.TABLE_NAME = kcu.TABLE_NAME AND c.COLUMN_NAME = kcu.COLUMN_NAME
            LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
            ON pk.TABLE_NAME = kcu.TABLE_NAME AND pk.CONSTRAINT_TYPE = 'PRIMARY KEY'
            WHERE c.TABLE_NAME = '{table_name}'
            """

            self._cur.execute(query)
            columns = self._cur.fetchall()

            # Convert the results to a list of lists
            data = [list(row) for row in columns]

            # Convert the results to a DataFrame
            df = pd.DataFrame(
                data, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
            )
            # Convert the results to a DataFrame

            # If we did switch databases, switch back to the original one.
            if database != original_database:
                self.change_database(original_database)

            return df

        except pyodbc.ProgrammingError as e:
            # Handle programming errors.
            raise ConnectionError(f"Failed to fetch columns due to ProgrammingError: {e}")
        except pyodbc.DatabaseError as e:
            # Handle other database-related errors.
            raise ConnectionError(f"Failed to fetch columns due to DatabaseError: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ConnectionError(f"Failed to fetch columns: {e}")

    # ------------------------------------------------------------------------------------------

    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute a given query on the SQL Server database.

        :param query: The SQL query string to execute.
        :param params: Optional tuple containing parameters for the query.
        :return: DataFrame containing the query results if any, otherwise an empty
                 DataFrame.

        :raises ValueError: If the database name is not provided.
        :raises ConnectionError: If the query execution fails.

        Example usage when parameters are provided:

        .. code-block:: python

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
           query = "SELECT * FROM names WHERE name_id = %s"
           params = (2,)
           result = db.execute_query(query, params)
           print(result)
           >> index  name_id  FirstName  LastName
              0      2        Fred       Smith

        Example usage when no parameters are provided:

        .. code-block:: python

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
           query = "SELECT * FROM names"
           result = db.execute_query(query)
           print(result)
           >> index  name_id  FirstName  LastName
            0        1        Jon        Webb
            1        2        Fred       Smith
            2        3        Jillian    Webb


        """
        msg = "The number of placeholders in the query does not "
        msg += "match the number of parameters."
        query = query.replace("%s", "?")
        num_placeholders = query.count("?")
        if num_placeholders != len(params):
            raise ValueError(msg)
        try:
            # If parameters are provided, execute the query with those parameters.
            if len(params) > 0:
                self._cur.execute(query, params)
            else:
                self._cur.execute(query)

            if (
                query.strip()
                .upper()
                .startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            ):
                self._conn.commit()

            # Try fetching results; if there's an exception, assume no results
            try:
                rows = self._cur.fetchall()
                columns = [column[0] for column in self._cur.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            except pyodbc.Error:
                # If the query did not return any rows, return an empty DataFrame.
                return pd.DataFrame()

        except pyodbc.ProgrammingError as e:
            raise ValueError(f"Failed to execute query due to ProgrammingError: {e}")

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

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
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

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
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

                placeholders = ", ".join(["?"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)
            self._conn.commit()  # Commit changes
        except pyodbc.InterfaceError as e:
            # Handle errors related to the interface.
            raise ValueError(f"Failed to insert data into the table: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ValueError(f"Failed to insert data into the table: {e}")

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

           from cobralib.io import SQLServerDB

           db = SQLServerDB('username', 'password', port=3306, hostname='localhost')
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

                placeholders = ", ".join(["?"] * len(insert_data))
                if table_headers is not None:
                    columns = ", ".join(sanitized_columns)
                else:
                    columns = ", ".join(insert_data.keys())
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)

            self._conn.commit()
        except pyodbc.InterfaceError as e:
            # Handle errors related to the interface.
            raise ValueError(f"Failed to insert data into the table: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ValueError(f"Failed to insert data into the table: {e}")

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

                placeholders = ", ".join(["?"] * len(insert_data))
                columns = ", ".join(sanitized_columns)
                values = tuple(insert_data.values())
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                self._cur.execute(query, values)

        except pyodbc.InterfaceError as e:
            # Handle errors related to the interface.
            raise ValueError(f"Failed to insert data into the table: {e}")
        except pyodbc.Error as e:
            # Generic error handler for any other exceptions.
            raise ValueError(f"Failed to insert data into the table: {e}")

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_connection(self, cert):
        """
        Create a connection to the SQL Server database.

        :param cert: yes to trust certificat and no to not trust certificate without
                     authentication
        """
        try:
            connect = f"DRIVER={self.driver};SERVER={self.hostname},{self.port}"
            connect += f";DATABASE={self._database};UID={self.username};"
            connect += f"PWD={self.password};TrustServerCertificate={cert}"
            self._conn = pyodbc.connect(connect)
            self._cur = self._conn.cursor()
        except pyodbc.InterfaceError as e:
            # Handle errors related to the interface.
            raise ConnectionError(
                f"Failed to create a connection due to InterfaceError: {e}"
            )
        except pyodbc.ProgrammingError as e:
            # Handle programming errors.
            raise ConnectionError(
                f"Failed to create a connection due to ProgrammingError: {e}"
            )
        except pyodbc.DatabaseError as e:
            # Handle other database-related errors.
            raise ConnectionError(
                f"Failed to create a connection due to DatabaseError: {e}"
            )
        except pyodbc.Error as e:
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
# Factory pattern for Relational Database Management Systems


def relational_database(
    db_type: str,
    database: str,
    username: str = "",
    password: str = "",
    port: int = -1,
    hostname: str = "localhost",
    cert: str = "yes",
    driver: str = "{ODBC Driver 18 for SQL Server}",
) -> RelationalDB:
    """
    Method will return a relational database object of type RelationalDB

    :param db_type: A string representing the database management system, can be
                    MySQL, MSSQL, PostGres or SQLite. This parameter is case
                    insensitive. Case Insensitive
    :param database: The database you wish to connect to, defaulted to appropriate
                     port number for each database manager
    :param username: The username for the database connection.
    :param password: The password for the database connection.
    :param port: The port number for the database connection. Defaulted to 3306
    :param hostname: The hostname for the database connection
                     (default is 'localhost').
    :param cert: yes to trust certificat and no to not trust certificate
                 without authentication. Defaulted to yes
    :param driver: The ODBC driver to use for connection. Defaulted to
                   "{ODBC Driver 18 for SQL Server}"
    """
    db_types = ["MYSQL", "SQLITE", "POSTGRES", "MSSQL"]
    if db_type.upper() not in db_types:
        raise ValueError(f"db_type must be one of {db_types}")
    if db_type.upper() == "MYSQL":
        if port == -1:
            port = 3306
        return MySQLDB(
            username=username,
            password=password,
            database=database,
            port=port,
            hostname=hostname,
        )
    elif db_type.upper() == "POSTGRES":
        if port == -1:
            port = 5432
        return PostGreSQLDB(
            username=username,
            password=password,
            database=database,
            port=port,
            hostname=hostname,
        )
    elif db_type.upper() == "MSSQL":
        if port == -1:
            port = 1433
        return SQLServerDB(
            username=username,
            password=password,
            database=database,
            port=port,
            hostname=hostname,
            cert=cert,
            driver=driver,
        )
    else:
        return SQLiteDB(database)


# ==========================================================================================
# ==========================================================================================
# eof
