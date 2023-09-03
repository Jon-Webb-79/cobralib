# Import necessary packages here
import json
import os

import pandas as pd
import pytest
from openpyxl import Workbook
from pandas.testing import assert_frame_equal

from cobralib.io import (
    Logger,
    ReadJSON,
    ReadYAML,
    read_csv_columns_by_headers,
    read_csv_columns_by_index,
    read_excel_columns_by_headers,
    read_excel_columns_by_index,
    read_pdf_columns_by_headers,
    read_pdf_columns_by_index,
    read_text_columns_by_headers,
    read_text_columns_by_index,
)

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


# ------------------------------------------------------------------------------------------


@pytest.fixture
def sample_file3(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_content = (
        "key1 value1\n"
        "key2 value2\n"
        "key3 value3\n"
        "String Value: Hello World\n"
        "JSON Data: {"
        '"key1": "value1",'
        '"key2": {'
        '"subkey1": "subvalue1",'
        '"subkey2": {'
        '"subsubkey1": "subsubvalue1",'
        '"subsubkey2": "subsubvalue2"'
        "}"
        "}"
        "}\n"
        "Nested JSON Data: {"
        '"key1": "value1",'
        '"key2": {'
        '"subkey1": "subvalue1",'
        '"subkey2": {'
        '"subsubkey1": "subsubvalue1",'
        '"subsubkey2": "subsubvalue2"'
        "}"
        "}"
        "}\n"
    )
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def sample_file4(tmp_path):
    file_path = tmp_path / "sample.json"
    json_data = {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"},
        },
    }
    file_path.write_text(json.dumps(json_data))
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def xml_file3(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_content = (
        "key1 value1\n"
        "key2 value2\n"
        "key3 value3\n"
        "String Value: Hello World\n"
        "XML Data: <root>"
        "<element1>"
        "<subelement>Value1</subelement>"
        "</element1>"
        "<element2>"
        "<subelement>Value2</subelement>"
        "</element2>"
        "<element3>"
        "<subelement>Value3</subelement>"
        "</element3>"
        "</root>\n"
        "Nested JSON Data: {"
        '"key1": "value1",'
        '"key2": {'
        '"subkey1": "subvalue1",'
        '"subkey2": {'
        '"subsubkey1": "subsubvalue1",'
        '"subsubkey2": "subsubvalue2"'
        "}"
        "}"
        "}\n"
    )
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def sample_file5(tmp_path):
    file_path = tmp_path / "sample.xml"
    file_content = """
        <root>
            <element1>
                <subelement>Value1</subelement>
            </element1>
            <element2>
                <subelement>Value2</subelement>
            </element2>
            <element3>
                <subelement>Value3</subelement>
            </element3>
        </root>
    """
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def csv_file(tmp_path):
    file_path = tmp_path / "test.csv"
    file_content = """ID,Inventory,Weight_per,Number
                      1,Shoes,1.5,5
                      2,t-shirt,1.8,3
                      3,coffee,2.1,15
                      4,books,3.2,48"""
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_content = """ID Inventory Weight_per Number
                     1 Shoes 1.5 5
                     2 t-shirt 1.8 3
                     3 coffee 2.1 15
                     4 books 3.2 48"""
    file_path.write_text(file_content)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def excel_file(tmp_path):
    file_path = tmp_path / "test.xlsx"
    headers = ["ID", "Inventory", "Weight_per", "Number"]
    data = [
        [1, "Shoes", 1.5, 5],
        [2, "T-shirt", 1.8, 3],
        [3, "coffee", 2.1, 15],
        [4, "books", 3.2, 48],
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "primary"
    sheet.append(headers)
    for row in data:
        sheet.append(row)
    workbook.save(file_path)
    return str(file_path)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def data():
    return {"name": "Alice", "age": 30}


# ------------------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before your test, for example:
    yield
    # Code that will run after your test, for example:
    if os.path.exists("test.log"):
        os.remove("test.log")


# ==========================================================================================
# ==========================================================================================
# Tests ReadYAML class


@pytest.mark.readyaml
def test_read_yaml_instantiation():
    """
    Test to ensure correct instantiation of class
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    assert reader._file_name == "../data/test/read_yaml.yaml"


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_doc_one_keyword():
    """
    Test to ensure values can be read from one document.  This also tests the ability
    to read a float variable
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("key:", float, 0)
    assert value == 4.387
    assert type(value) == float


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_doc_two_keyword():
    """
    Test to ensure values can be read from one document. This also tests the ability
    to read an integer
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("age:", int, 1)
    assert value == 30
    assert type(value) == int


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_bool_true():
    """
    Test to ensure method can read in all equivalent true values
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value1 = reader.read_key_value("bool test1:", bool, 1)
    value2 = reader.read_key_value("bool test4:", bool, 1)
    value3 = reader.read_key_value("bool test5:", bool, 1)
    assert value1 is True
    assert value2 is True
    assert value3 is True
    assert type(value1) is bool
    assert type(value2) is bool
    assert type(value3) is bool


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_bool_false():
    """
    Test to ensure method can read in all equivalent false values
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value1 = reader.read_key_value("bool test2:", bool, 1)
    value2 = reader.read_key_value("bool test3:", bool, 1)
    value3 = reader.read_key_value("bool test6:", bool, 1)
    assert value1 is False
    assert value2 is False
    assert value3 is False
    assert type(value1) is bool
    assert type(value2) is bool
    assert type(value3) is bool


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_inline_string():
    """
    This also tests the ability to read an inline string
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("String Value:", str, 1)
    assert value == "Hello Again World!"
    assert type(value) == str


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_next_indent_string():
    """
    This also tests the ability to read a next line string
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("Sentence:", str, 1)
    assert value == "Hello world"
    assert type(value) == str


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_next_multiline_string():
    """
    This also tests the ability to read a next line string
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("Multi Sentence:", str, 1)
    string = """This is a multiline sentence,
there is no reason to worry!"""
    assert value == string
    assert type(value) == str


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_next_connected_string():
    """
    This also tests the ability to read a next line string
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_key_value("Second Mult Sentence:", str, 1)
    string = "This is a multiline sentence, there is no reason to worry!"
    assert value == string
    assert type(value) == str


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_list():
    """
    This also tests the ability to read a list into memory
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_yaml_list("First List:", float, 1)
    expected = [1.1, 2.2, 3.3, 4.4]
    assert expected == value
    for i, j in zip(value, expected):
        type(i) == type(j)


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_list_string():
    """
    This also tests the ability to read a list of strings into memory
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_yaml_list("Numbers:", str, 1)
    expected = ["Hello World\nThis is Jon\n", "This", "Is", "Correct"]
    assert value == expected
    expected = [1.1, 2.2, 3.3, 4.4]


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_inline_list():
    """
    This also tests the ability to read a list of strings into memory
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_yaml_list("Inline List:", float, 0)
    expected = [1.1, 2.2, 3.3, 4.4]
    assert expected == value
    for i, j in zip(value, expected):
        type(i) == type(j)


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_dict():
    """
    This also tests the ability to read a dictionary
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_yaml_dict("Ages:", str, int, 1)
    expected = {"Jon": 44, "Jill": 32, "Bob": 12}
    assert value == expected


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_dict_strings():
    """
    This also tests the ability to read a dictionary
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    value = reader.read_yaml_dict("String Test:", int, str, 1)
    expected = {
        0: "String One",
        1: "Another String",
        2: "This is multiline\n one",
        3: "This is multiline\ntwo",
    }
    assert value == expected


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_full_yaml():
    """
    This also tests the ability to read a dictionary
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    data = reader.read_full_yaml()
    expected = {"Jon": 44, "Jill": 32, "Bob": 12}
    assert data[1]["Ages"] == expected


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_yaml_dict_list():
    """
    This also tests the ability to read a dictionary of lists
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    values = reader.read_yaml_dict_of_list("Dict List:", str, int, 0)
    expected = {"One": [1, 2, 3], "Two": [3, 4, 5], "Three": [6, 7, 8]}
    assert expected == values


# ------------------------------------------------------------------------------------------


@pytest.mark.readyaml
def test_read_dict_list_string():
    """
    This also tests the ability to read a dictionary of lists
    """
    reader = ReadYAML("../data/test/read_yaml.yaml")
    values = reader.read_yaml_dict_of_list("Str Dict List:", str, str, 0)
    expected = {"One": ["One", "Two", "Three"], "Two": ["Multi Line\nlist", "Hello"]}
    assert expected == values


# ==========================================================================================
# ==========================================================================================
# Test ReadJSON class


@pytest.mark.readjson
def test_read_json_variable_nested_values(sample_file3):
    """
    Test to ensure that the class will properly read in json data inserted after
    a key word
    """
    reader = ReadJSON(sample_file3)
    json_data = reader.read_json("JSON Data:")
    expected_data = {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"},
        },
    }
    assert json_data == expected_data


# ------------------------------------------------------------------------------------------


@pytest.mark.readjson
def test_read_full_json(sample_file4):
    """
    Ensure that the class will read in a .json file
    """
    reader = ReadJSON(sample_file4)
    full_json = reader.read_full_json()
    assert full_json == {
        "key1": "value1",
        "key2": {
            "subkey1": "subvalue1",
            "subkey2": {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"},
        },
    }


# ==========================================================================================
# ==========================================================================================
# Test ReadKeyWords class


# @pytest.mark.readkeywords
# def test_read_keywords_instantiation(sample_file1):
#     """
#     Test to ensure correct instantiation of class
#     """
#     reader = ReadKeyWords(sample_file1)
#     assert reader._file_name == sample_file1
#     assert reader.print_lines == 50


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_keywords_printing(sample_file1, capsys):
#     """
#     Test to ensure proper print out when object is printed
#     """
#     reader = ReadKeyWords(sample_file1, print_lines=2)
#     print(reader)
#     captured = capsys.readouterr()
#     expected_output = "key1 value1\nkey2 value2\n"
#     assert captured.out == expected_output


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_variable_existing_keyword(sample_file2):
#     """
#     Test to ensure the class can properly read in a float variable
#     """
#     reader = ReadKeyWords(sample_file2)
#     value = reader.read_variable("Float Value:", float)
#     assert value == 4.387

# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_yaml_keywords():
#     reader = ReadYAML("../data/test/read_yaml.yaml")
#     value = reader.read_yaml_list("Numbers:", str, 2)
#     print()
#     print(value)
# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_variable_nonexistent_keyword(sample_file2):
#     """
#     Test to ensure class fails properly when a value is not found
#     """
#     reader = ReadKeyWords(sample_file2)
#     with pytest.raises(ValueError):
#         reader.read_variable("Nonexistent Keyword", float)


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_variable_double(sample_file2):
#     """
#     Test to ensure class can handle numpy data types
#     """
#     reader = ReadKeyWords(sample_file2)
#     value = reader.read_variable("Double Value:", np.float32)
#     assert value == np.float32(1.11111187)


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_string_variable_existing_keyword(sample_file1):
#     """
#     Test to ensure that the read_string_variable method properly reads in a string
#     """
#     reader = ReadKeyWords(sample_file1)
#     value = reader.read_string_variable("String Value:")
#     assert value == "Hello World"


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_string_variable_yaml():
#     reader = ReadKeyWords("../data/test/read_yaml.yaml")
#     value = reader.read_string_variable("Multi Sentence:", 2)
#     print(value)
# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_list_existing_keyword(sample_file2):
#     """
#     Test to ensure that the class will properly read in a list
#     """
#     reader = ReadKeyWords(sample_file2)
#     values = reader.read_list("Int List:", int)
#     expected_values = [1, 2, 3, 4, 5]
#     assert values == expected_values


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_json_variable_nested_values(sample_file3):
#     """
#     Test to ensure that the class will properly read in json data inserted after
#     a key word
#     """
#     reader = ReadKeyWords(sample_file3)
#     json_data = reader.read_json("JSON Data:")
#     expected_data = {
#         "key1": "value1",
#         "key2": {
#             "subkey1": "subvalue1",
#             "subkey2": {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"},
#         },
#     }
#     assert json_data == expected_data


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_full_json(sample_file4):
#     """
#     Ensure that the class will read in a .json file
#     """
#     reader = ReadKeyWords(sample_file4)
#     full_json = reader.read_full_json()
#     assert full_json == {
#         "key1": "value1",
#         "key2": {
#             "subkey1": "subvalue1",
#             "subkey2": {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"},
#         },
#     }


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_xml_variable_nested_values(xml_file3):
#     """
#     Test to ensure that the class will properly read in XML data inserted after
#     a keyword
#     """
#     reader = ReadKeyWords(xml_file3)
#     xml_data = reader.read_xml("XML Data:")
#     expected_data = {
#         "root": {
#             "element1": {"subelement": "Value1"},
#             "element2": {"subelement": "Value2"},
#             "element3": {"subelement": "Value3"},
#         }
#     }
#     assert xml_data == expected_data


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_xml_full_data(sample_file5):
#     """
#     Test to ensure the class can properly read in an entire XML file
#     """
#     reader = ReadKeyWords(sample_file5)
#     xml_data = reader.read_full_xml()
#     assert isinstance(xml_data, dict)
#     assert "root" in xml_data
#     root = xml_data["root"]
#     assert isinstance(root, dict)


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_xml_by_keyword_existing(sample_file5):
#     """
#     Test to ensure that the class can read XML data under a specific keyword
#     """
#     reader = ReadKeyWords(sample_file5)
#     xml_data = reader.read_full_xml("element2")
#     assert isinstance(xml_data, dict)
#     assert "element2" in xml_data
#     element2 = xml_data["element2"]
#     assert isinstance(element2, dict)


# ------------------------------------------------------------------------------------------


# @pytest.mark.readkeywords
# def test_read_xml_by_keyword_nonexistent(sample_file5):
#     """
#     Test to ensure class fails properly when XML data is not properly formatted
#     """
#     reader = ReadKeyWords(sample_file5)
#     with pytest.raises(ValueError) as error:
#         reader.read_full_xml("nonexistent")
#     assert str(error.value) == "Keyword 'nonexistent' not found in the XML data"


# ==========================================================================================
# ==========================================================================================
# TEST READ COLUMNAR DATA


@pytest.mark.read_columnar
def test_read_csv_columns_by_headers(csv_file):
    """
    Test the read_csv_columns_by_headers function to ensure it properly reads in data
    """
    headers = {"ID": int, "Inventory": str, "Weight_per": float, "Number": int}
    df = read_csv_columns_by_headers(csv_file, headers)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "t-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_csv_columns_by_index(csv_file):
    """
    Test the read_csv_columns_by_index function to ensure it properly reads in data
    """
    col_index = {0: int, 1: str, 2: float, 3: int}
    col_names = ["ID", "Inventory", "Weight_per", "Number"]
    df = read_csv_columns_by_index(csv_file, col_index, col_names, skip=1)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "t-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_text_columns_by_headers(text_file):
    headers = {"ID": int, "Inventory": str, "Weight_per": float, "Number": int}
    df = read_text_columns_by_headers(text_file, headers)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "t-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_text_columns_by_index(text_file):
    col_index = {0: int, 1: str, 2: float, 3: int}
    col_names = ["ID", "Inventory", "Weight_per", "Number"]
    df = read_text_columns_by_index(text_file, col_index, col_names, skip=1)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "t-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_excel_columns_by_headers(excel_file):
    #  excel_file = "../data/test/test.xlsx"
    tab = "primary"
    headers = {"ID": int, "Inventory": str, "Weight_per": float, "Number": int}
    df = read_excel_columns_by_headers(excel_file, tab, headers)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "T-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_excel_columns_by_index(excel_file):
    tab = "primary"
    col_index = {0: int, 1: str, 2: float, 3: int}
    col_names = ["ID", "Inventory", "Weight_per", "Number"]
    df = read_excel_columns_by_index(excel_file, tab, col_index, col_names, skip=1)
    expected_data = {
        "ID": [1, 2, 3, 4],
        "Inventory": ["Shoes", "T-shirt", "coffee", "books"],
        "Weight_per": [1.5, 1.8, 2.1, 3.2],
        "Number": [5, 3, 15, 48],
    }
    expected_df = pd.DataFrame(expected_data)
    assert df.equals(expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_pdf_columns_by_header():
    file = "../data/test/pdf_tables.pdf"
    number = 2
    dat_type = {"Term": str, "Undergraduate": int}
    df = read_pdf_columns_by_headers(file, dat_type, number)

    col_names = ["Term", "Undergraduate"]
    vals = [["Fall 2019", 19886], ["Winter 2020", 19660], ["Spring 2020", 19593]]
    expected_df = pd.DataFrame(vals, columns=col_names)
    assert_frame_equal(df, expected_df)


# ------------------------------------------------------------------------------------------


@pytest.mark.read_columnar
def test_read_pdf_columns_by_index():
    file = "../data/test/pdf_tables.pdf"
    number = 2
    dat_type = {0: str, 1: int}
    cols = ["Term", "Undergraduate"]
    df = read_pdf_columns_by_index(file, dat_type, cols, number)

    col_names = ["Term", "Undergraduate"]
    vals = [["Fall 2019", 19886], ["Winter 2020", 19660], ["Spring 2020", 19593]]
    expected_df = pd.DataFrame(vals, columns=col_names)
    assert_frame_equal(df, expected_df)


# ==========================================================================================
# ==========================================================================================
# TEST READ AND WRITE TO YAML FILES


# @pytest.mark.read_yaml
# def test_yaml_file_reader():
#     # Test safe_load=True
#     reader = read_yaml_file("../data/test/test_file.yaml", safe=True)
#     # Access variables from the first document
#     document1 = reader[0]
#     assert document1["name"] == "John Doe"
#     assert document1["age"] == 25
#     assert document1["occupation"] == "Developer"
#     assert document1["hobbies"] == ["Reading", "Coding", "Playing guitar"]

#     # Access variables from the second document
#     document2 = reader[1]
#     assert document2["name"] == "Alice Smith"
#     assert document2["age"] == 30
#     assert document2["occupation"] == "Designer"
#     assert document2["hobbies"] == ["Painting", "Traveling", "Hiking"]


# ------------------------------------------------------------------------------------------


# @pytest.mark.read_yaml
# def test_append_yaml_file(data):
#     with TemporaryDirectory() as temp_dir:
#         file_path = os.path.join(temp_dir, "output.yaml")

#         write_yaml_file(file_path, data)

#         more_data = {"name": "Bob", "age": 35}
#         write_yaml_file(file_path, more_data, append=True)

#         with open(file_path) as file:
#             file_data = list(yaml.safe_load_all(file))

#         expected_data = []
#         expected_data.append(data)
#         expected_data.append(more_data)
#         assert file_data == expected_data


# ------------------------------------------------------------------------------------------


# @pytest.mark.read_yaml
# def test_write_yaml_file_nonexistent(data):
#     file_path = "/path/to/nonexistent/output.yaml"
#     pytest.raises(FileNotFoundError, write_yaml_file, file_path, data, append=True)


# ==========================================================================================
# ==========================================================================================


@pytest.mark.logger
def test_logger_creation():
    """Test Logger initialization"""
    logger = Logger("test.log", "DEBUG", "DEBUG", 10)
    assert logger.filename == "test.log"
    assert logger.max_lines == 10


# ------------------------------------------------------------------------------------------


@pytest.mark.logger
def test_logger_logging():
    """Test logging function"""
    logger = Logger("test.log", "DEBUG", "DEBUG", 10)
    logger.log("DEBUG", "Test message")
    with open("test.log") as f:
        log_content = f.read()
        assert "Test message" in log_content


# ------------------------------------------------------------------------------------------


@pytest.mark.logger
def test_logger_log_trimming():
    """Test that logs are correctly trimmed"""
    logger = Logger("test.log", "DEBUG", "DEBUG", 10)
    for i in range(20):  # Log more lines than max_lines
        logger.log("DEBUG", f"Test message {i}")
    with open("test.log") as f:
        log_lines = f.readlines()
        assert len(log_lines) == 10  # Only last 10 messages should be there
        assert "Test message 19" in log_lines[-1]  # Last message should be last in file
        assert "Test message 10" in log_lines[0]  # Messages before 10 should be trimmed


# ==========================================================================================
# ==========================================================================================
# eof
