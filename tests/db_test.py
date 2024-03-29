# Import necessary packages here
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from cobralib.db import MySQLDB, PostGreSQLDB, SQLiteDB, SQLServerDB

# ==========================================================================================
# ==========================================================================================
# File:    db_test.py
# Date:    July 17, 2023
# Author:  Jonathan A. Webb
# Purpose: This file contains functions that test the various functions and classes
#          in the db.py file
# Instruction: This code can be run in hte following ways
#              - pytest # runs all functions beginnning with the word test in the
#                         directory
#              - pytest file_name.py # Runs all functions in file_name beginning
#                                      with the word test
#              - pytest file_name.py::test_func_name # Runs only the function
#                                                      titled test_func_name in
#                                                      the file_name.py file
#              - pytest -s # Runs tests and displays when a specific file
#                            has completed testing, and what functions failed.
#                            Also displays print statments
#              - pytest -v # Displays test results on a function by function
#              - pytest -p no:warnings # Runs tests and does not display warning
#                          messages
#              - pytest -s -v -p no:warnings # Displays relevant information and
#                                supports debugging
#              - pytest -s -p no:warnings # Run for record
# ==========================================================================================
# ==========================================================================================


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("mysql.connector.connect")


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_connection():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock mysql.connector.connect to return the mock connection
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

    # Test close_conn method
    db.close_connection()
    mock_conn.close.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_connect_fail():
    with pytest.raises(ConnectionError):
        MySQLDB("username", "password", "database", port=3306, hostname="localhost")


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_change_mysql_db():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock mysql.connector.connect to return the mock connection
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

        # Simulate changing the database
        db.change_database("new_db")
    #  mock_cursor.execute.assert_called_once_with("USE new_db")


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_get_mysql_dbs():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_dbs = [["db1"], ["db2"], ["db3"]]  # use list of lists
    mock_cursor.fetchall.return_value = mock_dbs

    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")

        dbs = db.get_databases()

        # mock_cursor.execute.assert_called_once_with("SHOW DATABASES;")
        assert list(dbs["Databases"]) == ["db1", "db2", "db3"]
        assert dbs.equals(pd.DataFrame(mock_dbs, columns=["Databases"]))


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_get_mysql_db_tables():
    # Create the mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Assign the mock cursor to the mock connection
    mock_conn.cursor.return_value = mock_cursor
    mock_tables = [["Table1"], ["Table2"]]
    # Mock the fetchall method to return known tables
    mock_cursor.fetchall.return_value = mock_tables

    # Mocking the connect method
    with patch("cobralib.db.connect", return_value=mock_conn):
        # Create an instance of the class
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")

        # Change to the specified DB
        db.change_database("DB_Name")

        # Invoke the method
        tables = db.get_database_tables()
        # Check the result
        assert list(tables["Tables"]) == ["Table1", "Table2"]

    # Verify the cursor method was called
    mock_conn.cursor.assert_called_once()

    # Verify fetchall method was called
    mock_cursor.fetchall.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_get_mysql_table_columns():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("DB_Name")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [
            ("Column1", "Integer", "YES", "MUL", None, ""),
            ("Column2", "Varchar(50)", "NO", "", None, ""),
            ("Column3", "Datetime", "YES", "", None, ""),
        ]
        db.cur.fetchall.return_value = mock_return

        # Invoke the method
        columns = db.get_table_columns("Table1")

        # Create expected DataFrame for comparison
        expected_df = pd.DataFrame(
            mock_return, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
        )

        # Check the result
        pd.testing.assert_frame_equal(columns, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_csv_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_csv.csv",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_query_mysql_db():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("names")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Jon", "Fred"), ("Webb", "Smith")]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("FirstName",), ("LastName",)]
        expected_df = pd.DataFrame(mock_return, columns=["FirstName", "LastName"])

        query = "SELECT * FROM names;"
        result = db.execute_query(query)

        # Check the result
        pd.testing.assert_frame_equal(result, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_excel_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.excel_to_table(
            "../data/test/read_xls.xlsx",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            "test",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_txt_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_txt.txt",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            delimiter=r"\s+",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_pdf_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", "database", port=3306, hostname="localhost")
        db.change_database("CollegeAdmissions")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Fall 2019", 3441), ("Winter 2020", 3499), ("Spring 2020", 3520)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Term",), ("Graduate",)]
        expected_df = pd.DataFrame(mock_return, columns=["Term", "Graduate"])

        # Create table
        query = """CREATE TABLE Admissions (
            term_id INTEGER AUTO_INCREMENT
            Term VARCHAR(20) NOT NULL,
            Graduate INT NOT NULL,
            PRIMARY KEY (term_id)
        );
        """
        db.execute_query(query)

        db.pdf_to_table(
            "../data/test/pdf_tables.pdf",
            "Admissions",
            {"Term": str, "Graduate": int},
            table_idx=2,
        )
        query = "SELECT Term, Graduate FROM Admissions;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ==========================================================================================
# ==========================================================================================
# Test SQLiteDB


@pytest.mark.sqlite
def test_sqlite_connection():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    assert db.database == db_file
    # Test close_conn method
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_change_sqlite_db():
    db_file = "../data/test/db_two.db"
    db = SQLiteDB(db_file)
    db.change_database("../data/test/db_one.db")
    assert db.database == "../data/test/db_one.db"
    df = db.get_database_tables()
    mock_return = [("Produce"), ("sqlite_sequence"), ("Inventory")]

    expected_df = pd.DataFrame(mock_return, columns=["Tables"])
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_get_sqlite_tables():
    db_file = "../data/test/db_two.db"
    db = SQLiteDB(db_file)
    df = db.get_database_tables("../data/test/db_one.db")
    mock_return = [("Produce"), ("sqlite_sequence"), ("Inventory")]

    expected_df = pd.DataFrame(mock_return, columns=["Tables"])
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    assert db.database == db_file
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_get_sqlite_table_columns():
    db_file = "../data/test/db_two.db"
    db = SQLiteDB(db_file)
    # df = db.get_table_columns("Students")
    df = db.get_table_columns("Students", "../data/test/db_two.db")
    mock_return = [
        ("student_id", "INTEGER", "NO", "PRI", None, ""),
        ("FirstName", "VARCHAR(20)", "NO", "", None, ""),
        ("LastName", "VARCHAR(20)", "NO", "", None, ""),
    ]
    expected_df = pd.DataFrame(
        mock_return, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
    )
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_query_sqlite():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    query = "SELECT * FROM Inventory WHERE Item = %s;"
    df = db.execute_query(query, ("Apple",))
    mock_return = [
        (1, "Apple", 5),
    ]
    expected_df = pd.DataFrame(mock_return, columns=["inv_id", "item", "number"])
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_sqlite_csv_to_table():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    create = """CREATE TABLE IF NOT EXISTS Test (
        prd_id INTEGER NOT NULL,
        Prd VARCHAR(20) NOT NULL,
        Inv INTEGER,
        PRIMARY KEY (prd_id)
    );"""
    db.execute_query(create)
    db.csv_to_table(
        "../data/test/read_csv.csv",
        "Test",
        {"Product": str, "Inventory": int},
        ["Prd", "Inv"],
    )
    df = db.execute_query("SELECT * FROM Test;")
    df = df.drop(["prd_id"], axis=1)
    mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
    expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])
    db.execute_query("DROP TABLE Test;")
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_sqlite_text_to_table():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    create = """CREATE TABLE IF NOT EXISTS Test (
        prd_id INTEGER NOT NULL,
        Prd VARCHAR(20) NOT NULL,
        Inv INTEGER,
        PRIMARY KEY (prd_id)
    );"""
    db.execute_query(create)
    db.csv_to_table(
        "../data/test/read_txt.txt",
        "Test",
        {"Product": str, "Inventory": int},
        ["Prd", "Inv"],
        delimiter=r"\s+",
    )
    df = db.execute_query("SELECT * FROM Test;")
    df = df.drop(["prd_id"], axis=1)
    mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
    expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])
    db.execute_query("DROP TABLE Test;")
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_sqlite_excel_to_table():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    create = """CREATE TABLE IF NOT EXISTS Test (
        prd_id INTEGER NOT NULL,
        Prd VARCHAR(20) NOT NULL,
        Inv INTEGER,
        PRIMARY KEY (prd_id)
    );"""
    db.execute_query(create)
    db.excel_to_table(
        "../data/test/read_xls.xlsx",
        "Test",
        {"Product": str, "Inventory": int},
        ["Prd", "Inv"],
        sheet_name="test",
    )
    df = db.execute_query("SELECT * FROM Test;")
    df = df.drop(["prd_id"], axis=1)
    mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
    expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])
    db.execute_query("DROP TABLE Test;")
    pd.testing.assert_frame_equal(df, expected_df, check_dtype=False)
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.sqlite
def test_sqlite_pdf_to_table():
    db_file = "../data/test/db_one.db"
    db = SQLiteDB(db_file)
    # Create table
    query = """CREATE TABLE IF NOT EXISTS Admissions (
        term_id INTEGER NOT NULL,
        Term VARCHAR(20) NOT NULL,
        Graduate INTEGER NOT NULL,
        PRIMARY KEY (term_id)
    );
    """
    db.execute_query(query)
    # Mock the fetchall method to return known columns and their metadata
    mock_return = [("Fall 2019", 3441), ("Winter 2020", 3499), ("Spring 2020", 3520)]

    expected_df = pd.DataFrame(mock_return, columns=["Term", "Graduate"])

    db.pdf_to_table(
        "../data/test/pdf_tables.pdf",
        "Admissions",
        {"Term": str, "Graduate": int},
        table_idx=2,
    )
    query = "SELECT Term, Graduate FROM Admissions;"
    inventory = db.execute_query(query)
    db.execute_query("DROP TABLE Admissions;")
    pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ==========================================================================================
# ==========================================================================================
# TEST POSTGRESQL CLASS


@pytest.fixture(autouse=True)
def no_requests_post(monkeypatch):
    monkeypatch.delattr("pg.connect")


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_connection():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock mysql.connector.connect to return the mock connection
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

    # Test close_conn method
    db.close_connection()
    mock_conn.close.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_connect_fail():
    with pytest.raises(ConnectionError):
        PostGreSQLDB("username", "password", "database", port=5432, hostname="localhost")


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_change_postgres_db():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock mysql.connector.connect to return the mock connection
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

        # Simulate changing the database
        db.change_database("new_db")
    #  mock_cursor.execute.assert_called_once_with("USE new_db")


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_get_postgres_dbs():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_dbs = [["db1"], ["db2"], ["db3"]]  # use list of lists
    mock_cursor.fetchall.return_value = mock_dbs

    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )

        dbs = db.get_databases()

        # mock_cursor.execute.assert_called_once_with("SHOW DATABASES;")
        assert list(dbs["Databases"]) == ["db1", "db2", "db3"]
        assert dbs.equals(pd.DataFrame(mock_dbs, columns=["Databases"]))


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_get_postgres_db_tables():
    # Create the mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Assign the mock cursor to the mock connection
    mock_conn.cursor.return_value = mock_cursor
    mock_tables = [["Table1"], ["Table2"]]
    # Mock the fetchall method to return known tables
    mock_cursor.fetchall.return_value = mock_tables

    # Mocking the connect method
    with patch("pgdb.connect", return_value=mock_conn):
        # Create an instance of the class
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )

        # Change to the specified DB
        db.change_database("DB_Name")

        # Invoke the method
        tables = db.get_database_tables()
        # Check the result
        assert list(tables["Tables"]) == ["Table1", "Table2"]

    # Verify fetchall method was called
    mock_cursor.fetchall.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_get_postgres_table_columns():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("DB_Name")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [
            ("Column1", "Integer", "YES", "MUL", "Primary", ""),
            ("Column2", "Varchar(50)", "NO", "", "Primary", ""),
            ("Column3", "Datetime", "YES", "", "Primary", ""),
        ]
        db.cur.fetchall.return_value = mock_return

        # Invoke the method
        columns = db.get_table_columns("Table1")

        # Create expected DataFrame for comparison
        expected_df = pd.DataFrame(
            mock_return, columns=["Field", "Type", "Null", "Default", "Key", "Extra"]
        )

        # Check the result
        pd.testing.assert_frame_equal(columns, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_csv_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_csv.csv",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_query_postgres_db():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("names")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Jon", "Fred"), ("Webb", "Smith")]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("FirstName",), ("LastName",)]
        expected_df = pd.DataFrame(mock_return, columns=["FirstName", "LastName"])

        query = "SELECT * FROM names;"
        result = db.execute_query(query)

        # Check the result
        pd.testing.assert_frame_equal(result, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_excel_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.excel_to_table(
            "../data/test/read_xls.xlsx",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            "test",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_txt_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_txt.txt",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            delimiter=r"\s+",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.postgres
def test_postgres_pdf_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pgdb.connect", return_value=mock_conn):
        db = PostGreSQLDB(
            "username", "password", "database", port=5432, hostname="localhost"
        )
        db.change_database("CollegeAdmissions")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Fall 2019", 3441), ("Winter 2020", 3499), ("Spring 2020", 3520)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Term",), ("Graduate",)]
        expected_df = pd.DataFrame(mock_return, columns=["Term", "Graduate"])

        # Create table
        query = """CREATE TABLE Admissions (
            term_id INTEGER AUTO_INCREMENT
            Term VARCHAR(20) NOT NULL,
            Graduate INT NOT NULL,
            PRIMARY KEY (term_id)
        );
        """
        db.execute_query(query)

        db.pdf_to_table(
            "../data/test/pdf_tables.pdf",
            "Admissions",
            {"Term": str, "Graduate": int},
            table_idx=2,
        )
        query = "SELECT Term, Graduate FROM Admissions;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ==========================================================================================
# ==========================================================================================
# TEST SQL-SERVER CLASS


@pytest.mark.mssql
def test_mssql_connection():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock pyodbc.connect
    with patch("pyodbc.connect", return_value=mock_conn):
        # Instantiate your SQLServerDB class
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )

        # Assertions to ensure mocked connection and cursor are used
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

    # Test if close method of mock connection is called
    db.close_connection()
    mock_conn.close.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_mssql_connect_fail():
    # Make mock_conn.cursor() return mock_cursor
    with pytest.raises(ConnectionError):
        SQLServerDB("username", "password", "database", port=1433, hostname="localhost")


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_change_mssql_db():
    # Create mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Make mock_conn.cursor() return mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock mysql.connector.connect to return the mock connection
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

        # Simulate changing the database
        db.change_database("new_db")
    mock_cursor.execute.assert_called_once_with("USE new_db")
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_get_mssql_dbs():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_dbs = [["db1"], ["db2"], ["db3"]]  # use list of lists
    mock_cursor.fetchall.return_value = mock_dbs

    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )

        dbs = db.get_databases()

        # mock_cursor.execute.assert_called_once_with("SHOW DATABASES;")
        assert list(dbs["Databases"]) == ["db1", "db2", "db3"]
        assert dbs.equals(pd.DataFrame(mock_dbs, columns=["Databases"]))
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_get_mssql_db_tables():
    # Create the mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Assign the mock cursor to the mock connection
    mock_conn.cursor.return_value = mock_cursor
    mock_tables = [["Table1"], ["Table2"]]
    # Mock the fetchall method to return known tables
    mock_cursor.fetchall.return_value = mock_tables

    # Mocking the connect method
    with patch("pyodbc.connect", return_value=mock_conn):
        # Create an instance of the class
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )

        # Change to the specified DB
        db.change_database("DB_Name")

        # Invoke the method
        tables = db.get_database_tables()
        # Check the result
        assert list(tables["Tables"]) == ["Table1", "Table2"]

    # Verify fetchall method was called
    mock_cursor.fetchall.assert_called_once()
    db.close_connection()


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_get_mssql_table_columns():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("DB_Name")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [
            ("Column1", "Integer", "YES", "MUL", "Primary", ""),
            ("Column2", "Varchar(50)", "NO", "", "Primary", ""),
            ("Column3", "Datetime", "YES", "", "Primary", ""),
        ]
        db.cur.fetchall.return_value = mock_return

        # Invoke the method
        columns = db.get_table_columns("Table1")
        # Create expected DataFrame for comparison
        expected_df = pd.DataFrame(
            mock_return, columns=["Field", "Type", "Null", "Key", "Default", "Extra"]
        )

        # Check the result
        pd.testing.assert_frame_equal(columns, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_mssql_csv_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER IDENTITY(1,1)
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_csv.csv",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_query_mssql_db():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("names")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Jon", "Fred"), ("Webb", "Smith")]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("FirstName",), ("LastName",)]
        expected_df = pd.DataFrame(mock_return, columns=["FirstName", "LastName"])

        query = "SELECT * FROM names;"
        result = db.execute_query(query)

        # Check the result
        pd.testing.assert_frame_equal(result, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_mssql_excel_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.excel_to_table(
            "../data/test/read_xls.xlsx",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            "test",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_mssql_txt_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("Inventory")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Apples", 5), ("Banana", 12), ("Cucumber", 20), ("Peach", 3)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Prd",), ("Inv",)]
        expected_df = pd.DataFrame(mock_return, columns=["Prd", "Inv"])

        # Create table
        query = """CREATE TABLE Inventory (
            product_id INTEGER AUTO_INCREMENT
            Prd VARCHAR(20) NOT NULL,
            Inv INT NOT NULL,
            PRIMARY KEY (product_id);
        """
        db.execute_query(query)

        db.csv_to_table(
            "../data/test/read_txt.txt",
            "Inventory",
            {"Product": str, "Inventory": int},
            ["Prd", "Inv"],
            delimiter=r"\s+",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mssql
def test_mssql_pdf_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("pyodbc.connect", return_value=mock_conn):
        db = SQLServerDB(
            "username", "password", "database", port=1433, hostname="localhost"
        )
        db.change_database("CollegeAdmissions")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Fall 2019", 3441), ("Winter 2020", 3499), ("Spring 2020", 3520)]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("Term",), ("Graduate",)]
        expected_df = pd.DataFrame(mock_return, columns=["Term", "Graduate"])

        # Create table
        query = """CREATE TABLE Admissions (
            term_id INTEGER AUTO_INCREMENT
            Term VARCHAR(20) NOT NULL,
            Graduate INT NOT NULL,
            PRIMARY KEY (term_id)
        );
        """
        db.execute_query(query)

        db.pdf_to_table(
            "../data/test/pdf_tables.pdf",
            "Admissions",
            {"Term": str, "Graduate": int},
            table_idx=2,
        )
        query = "SELECT Term, Graduate FROM Admissions;"
        inventory = db.execute_query(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ==========================================================================================
# ==========================================================================================
# eof
