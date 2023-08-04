# Import necessary packages here
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from cobralib.db import MySQLDB

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
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

    # Test close_conn method
    db.close_conn()
    mock_conn.close.assert_called_once()


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_connect_fail():
    with pytest.raises(ConnectionError):
        MySQLDB("username", "password", port=3306, hostname="localhost")


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
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        assert db.conn == mock_conn
        assert db.cur == mock_cursor

        # Simulate changing the database
        db.change_db("new_db")
        mock_cursor.execute.assert_called_once_with("USE new_db")


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_get_mysql_dbs():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_dbs = [["db1"], ["db2"], ["db3"]]  # use list of lists
    mock_cursor.fetchall.return_value = mock_dbs

    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", port=3306, hostname="localhost")

        dbs = db.get_dbs()

        mock_cursor.execute.assert_called_once_with("SHOW DATABASES;")
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
        db = MySQLDB("username", "password", port=3306, hostname="localhost")

        # Change to the specified DB
        db.change_db("DB_Name")

        # Invoke the method
        tables = db.get_db_tables()
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
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("DB_Name")

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
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("Inventory")

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
        db.query_db(query)

        db.csv_to_table(
            "../data/test/read_csv.csv",
            "Inventory",
            ["Product", "Inventory"],
            ["Prd", "Inv"],
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.query_db(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_query_mysql_db():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("names")

        # Mock the fetchall method to return known columns and their metadata
        mock_return = [("Jon", "Fred"), ("Webb", "Smith")]
        db.cur.fetchall.return_value = mock_return

        db.cur.description = [("FirstName",), ("LastName",)]
        expected_df = pd.DataFrame(mock_return, columns=["FirstName", "LastName"])

        query = "SELECT * FROM names;"
        result = db.query_db(query)

        # Check the result
        pd.testing.assert_frame_equal(result, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_excel_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("Inventory")

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
        db.query_db(query)

        db.excel_to_table(
            "../data/test/read_xls.xlsx",
            "Inventory",
            ["Product", "Inventory"],
            ["Prd", "Inv"],
            "test",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.query_db(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_txt_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("Inventory")

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
        db.query_db(query)

        db.csv_to_table(
            "../data/test/read_txt.txt",
            "Inventory",
            ["Product", "Inventory"],
            ["Prd", "Inv"],
            delemeter=r"\s+",
        )
        query = "SELECT Prd, Inv FROM Inventory;"
        inventory = db.query_db(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


@pytest.mark.mysql
def test_mysql_pdf_to_table():
    mock_conn = MagicMock()

    # Mocking the connect and cursor methods
    with patch("cobralib.db.connect", return_value=mock_conn):
        db = MySQLDB("username", "password", port=3306, hostname="localhost")
        db.change_db("CollegeAdmissions")

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
            PRIMARY KEY (product_id);
        """
        db.query_db(query)

        db.pdf_to_table(
            "../data/test/pdf_tables.pdf",
            "Admissions",
            {"Term": str, "Graduate": int},
            table_idx=2,
        )
        query = "SELECT Prd, Inv FROM Admissions;"
        inventory = db.query_db(query)

        pd.testing.assert_frame_equal(inventory, expected_df, check_dtype=False)


# ------------------------------------------------------------------------------------------


# def test_implementation():
#     obj = MySQLDB("root", "GrandCanyon12#$", database = "ZillowHousing")
#     qry = """CREATE TABLE IF NOT EXISTS College (
#         college_id INTEGER AUTO_INCREMENT,
#         Term VARCHAR(20),
#         Graduate INT,
#         PRIMARY KEY (college_id)
#     )
#     """
#     file = "../data/test/pdf_tables.pdf"
#     pdf_headers = {"Term": str, "Graduate": int}
#     obj.query_db(qry)
#     tables = obj.get_db_tables()
#     print(tables)
#     obj.pdf_to_table(file, "College", pdf_headers, table_idx=2)
#     dat = obj.query_db("SELECT * FROM College;")
#     print(dat)
#     obj.close_conn()
# ==========================================================================================
# ==========================================================================================
# eof
