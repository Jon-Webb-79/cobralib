# Import necessary packages here
import numpy as np
import pytest

from cobralib.io import ReadKeyWords

# ==========================================================================================
# ==========================================================================================
# File:    test.py
# Date:    July 09, 2023
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
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
# Place fixtures here


@pytest.fixture
def sample_file1(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_content = "key1 value1\nkey2 value2\nkey3 value3\nString Value: Hello World"
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def sample_file2(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_content = "Float Value: 4.387\nDouble Value: 1.11111187\nInt List: 1 2 3 4 5"
    file_path.write_text(file_content)
    return str(file_path)


# Insert Code here


def test_give_name_here():
    # Add test here
    pass


# ==========================================================================================
# ==========================================================================================
# Test ReadKeyWords class


def test_read_keywords_instantiation(sample_file1):
    """
    Test to ensure correct instantiation of class
    """
    reader = ReadKeyWords(sample_file1)
    assert reader._file_name == sample_file1
    assert reader.print_lines == 50


# ------------------------------------------------------------------------------------------


def test_read_keywords_printing(sample_file1, capsys):
    """
    Test to ensure proper print out when object is printed
    """
    reader = ReadKeyWords(sample_file1, print_lines=2)
    print(reader)
    captured = capsys.readouterr()
    expected_output = "key1 value1\nkey2 value2\n"
    assert captured.out == expected_output


# ------------------------------------------------------------------------------------------


def test_read_variable_existing_keyword(sample_file2):
    """
    Test to ensure the class can properly read in a float variable
    """
    reader = ReadKeyWords(sample_file2)
    value = reader.read_variable("Float Value:", float)
    assert value == 4.387


# ------------------------------------------------------------------------------------------


def test_read_variable_nonexistent_keyword(sample_file2):
    """
    Test to ensure class fails properly when a value is not found
    """
    reader = ReadKeyWords(sample_file2)
    with pytest.raises(ValueError) as error:
        reader.read_variable("Nonexistent Keyword", float)
    assert str(error.value) == "Keyword 'Nonexistent Keyword' not found in the file"


# ------------------------------------------------------------------------------------------


def test_read_variable_double(sample_file2):
    """
    Test to ensure class can handle numpy data types
    """
    reader = ReadKeyWords(sample_file2)
    value = reader.read_variable("Double Value:", np.float32)
    assert value == np.float32(1.11111187)


# ------------------------------------------------------------------------------------------


def test_read_string_variable_existing_keyword(sample_file1):
    """
    Test to ensure that the read_string_variable method properly reads in a string
    """
    reader = ReadKeyWords(sample_file1)
    value = reader.read_string_variable("String Value:")
    assert value == "Hello World"


# ------------------------------------------------------------------------------------------


def test_read_list_existing_keyword(sample_file2):
    """
    Test to ensure that the class will properly read in a list
    """
    reader = ReadKeyWords(sample_file2)
    values = reader.read_list("Int List:", int)
    expected_values = [1, 2, 3, 4, 5]
    assert values == expected_values


# ==========================================================================================
# ==========================================================================================
# eof
