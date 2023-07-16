# Import necessary packages here
import json
import logging
import logging.handlers
import os
import re
import xml.etree.ElementTree as ET
from collections import deque
from typing import Any, Union

import pandas as pd
import xmltodict
import yaml
from mysql.connector import (
    DatabaseError,
    Error,
    InterfaceError,
    ProgrammingError,
    connect,
)

# ==========================================================================================
# ==========================================================================================

# File:    io.py
# Date:    July 09, 2023
# Author:  Jonathan A. Webb
# Purpose: This file contains classes and functions that can be used to read and write
#          to files
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class ReadKeyWords:
    """
    This class can be used by a read to read a text based config file.  The methods
    will look for a specific key word that must begin on the first character of each
    line, and will read in the variable or variables just to the right of the
    keyword as a user specified data type.  The user can also print the object
    which will display the user specified number of lines on the screen.

    This class is cabale of reading files that contain text, json and xml
    data in one file.  In addition, this class can read files that are entirely
    compriesd of text, json, or xml data.

    :param file_name: The file name to be read including the path length
    :param print_lines: The number of lines to be printed to the screen if the
                        user prints an instance of the class. Defaulted to 50
    :raises FileNotFoundError: If the file does not exist

    Example file titled test_key_words.txt

    .. literalinclude:: ../../../data/test/text_key_words.txt
       :language: text

    .. code-block:: python

        # Instantiate the class
        reader = ReadKeyWords("test_key_words.txt", print_lines=2)

        # Print the instance, displaying 2 lines
        print(reader)

        >> Float Value: 4.387 # Comment line not to be read
        >> Double Value: 1.11111187 # Comment line not to be read

    The user can also adjust the print_lines attribute after instantiation
    if they wish to change the number of printed lines

    """

    def __init__(self, file_name: str, print_lines: int = 50):
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"FATAL ERROR: {file_name} does not exist")
        self._file_name = file_name
        self.__lines = self._read_lines()
        self.print_lines = print_lines

    # ------------------------------------------------------------------------------------------

    def read_variable(self, keyword: str, data_type: type) -> Any:
        """
        Search each line for the specified keyword and read the variable to the
        right of the keyword as the specified data type

        :param keyword: The keyword to search for in each line.
        :param data_type: The data type to be used in order to casy the variable
        :return: The float variable to the right of the keyword.
        :raises ValueError: If the keyword is not found or if the variable cannot
                            be parsed as a float.

        .. code-block:: python

           import numpy as np
           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_variable("Double Value:", np.float32)
           print(value)
           print(type(value))

           >> 1.11111187
           >> <class 'numpy.float32'>

        However, be carefult with strings.  This method will only read the first
        character array following the key word. In order to read in the entire
        line as a string, use the read_string_variable method.

        .. code-block:: python

           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_variable("String:", str)
           print(value)
           print(type(value))

           >> "Hello"
           >> str
        """
        for line in self.__lines:
            if line.startswith(keyword):
                value_str = line[len(keyword) :].strip()
                try:
                    return data_type(value_str)
                except ValueError:
                    raise ValueError(f"Invalid float value found for {keyword}")
        raise ValueError(f"Keyword '{keyword}' not found in the file")

    # ------------------------------------------------------------------------------------------

    def read_string_variable(self, keyword: str) -> str:
        """
        Search each line for the specified keyword and read the string variable
        to the right of the keyword.

        :param keyword: The keyword to search for in each line.
        :return: The string variable to the right of the keyword.
        :raises ValueError: If the keyword is not found.

        .. code-block:: python

           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_variable("String:", str)
           print(value)
           print(type(value))

           >> Hello # Comment to be read
           >> str
        """
        for line in self.__lines:
            if line.startswith(keyword):
                return line[len(keyword) :].strip()
        raise ValueError(f"Keyword '{keyword}' not found in the file")

    # ------------------------------------------------------------------------------------------

    def read_list(self, keyword: str, data_type: type) -> list[Any]:
        """
        Search each line for the specified keyword and read the values after the keyword
        as a list of the user-defined data type.

        :param keyword: The keyword to search for in each line.
        :param data_type: The data type to which the values should be transformed.
        :return: The list of values after the keyword, transformed into the specified
                 data type.
        :raises ValueError: If the keyword is not found.

        .. code-block:: python

           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_list("Float List:", float)
           print(value)

           >> [ 1.1, 2.2, 3.3, 4.4 ]
        """
        for line in self.__lines:
            if line.startswith(keyword):
                tokens = line.split()[2:]  # Skip the keyword and colon
                try:
                    values = [data_type(token) for token in tokens]
                    return values
                except ValueError:
                    raise ValueError(
                        f"Invalid {data_type.__name__} value found for {keyword}"
                    )
        raise ValueError(f"Keyword '{keyword}' not found in the file")

    # ------------------------------------------------------------------------------------------

    def read_json(self, keyword: str) -> dict:
        """
        Search each line for the specified keyword and read the JSON data
        to the right of the keyword until the termination of brackets.

        :param keyword: The keyword to search for in each line.
        :return: The JSON data as a dictionary.
        :raises ValueError: If the keyword is not found or if the JSON data is not valid.

        .. code-block:: python

           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_json("JSON Data:")
           print(value)

           >> {"book": "History of the World", "year": 1976}
        """
        found_keyword = False
        json_data = ""
        for line in self.__lines:
            if line.startswith(keyword):
                found_keyword = True
                json_data += line.split(keyword)[-1].strip()
                if json_data.startswith("{") and json_data.endswith("}"):
                    try:
                        return json.loads(json_data)
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON data for keyword '{keyword}'")

        if not found_keyword:
            raise ValueError(f"Keyword '{keyword}' not found in the file")
        else:
            raise ValueError(f"Invalid JSON data for keyword '{keyword}'")

    # ------------------------------------------------------------------------------------------

    def read_full_json(self, keyword: str = None) -> Union[dict, list]:
        """
        Read the entire contents of the file as JSON data.
        If a keyword is provided, search for that keyword and return the nested
        dictionaries beneath it.

        :param keyword: The keyword to search for in the file. If None,
                        returns the entire JSON data.
        :return: The JSON data as a dictionary or list.
        :raises ValueError: If the keyword is specified but not found
                            in the file.

        Unlike the read_json method, this method assumes the entire file is
        formatted as a .json file.  This method will allow a user to read
        in the entire contents of the json file as a dictionary, or it
        will read in the dictionaries nested under a specific key word.
        If you assume the input file titled example.json has the following
        format

        .. code-block:: json

           {
            "key1": "value1",
            "key2": {
                "subkey1": "subvalue1",
                "subkey2": {
                    "subsubkey1": "subsubvalue1",
                    "subsubkey2": "subsubvalue2"
                 }
              }
           }

        The code to extract data would look like:

        .. code-block:: python

           reader = ReadKeyWords("example.json")
           value = reader.read_full_json()
           print(value)

           >> {
               "key1": "value1",
               "key2": {
                   "subkey1": "subvalue1",
                   "subkey2": {
                       "subsubkey1": "subsubvalue1",
                       "subsubkey2": "subsubvalue2"
                   }
               }
           }

           new_value = reader.read_full_json("subkey2")
           print(new_value)
           >> {"subsubkey1": "subsubvalue1", "subsubkey2": "subsubvalue2"}
        """
        json_data = json.loads("\n".join(self.__lines))

        if keyword is None:
            return json_data

        def find_nested_dictionaries(data, keyword):
            if isinstance(data, dict):
                if keyword in data:
                    return data[keyword]
                for value in data.values():
                    result = find_nested_dictionaries(value, keyword)
                    if result is not None:
                        return result
            elif isinstance(data, list):
                for item in data:
                    result = find_nested_dictionaries(item, keyword)
                    if result is not None:
                        return result
            return None

        result = find_nested_dictionaries(json_data, keyword)
        if result is not None:
            return result
        else:
            raise ValueError(f"Keyword '{keyword}' not found in the JSON data")

    # ------------------------------------------------------------------------------------------

    def read_xml(self, keyword: str) -> dict:
        """
        Search each line for the specified keyword and read the XML data
        to the right of the keyword until the termination of tags.

        :param keyword: The keyword to search for in each line.
        :return: The XML data as a dictionary.
        :raises ValueError: If the keyword is not found or if the XML data is not valid.
        """
        found_keyword = False
        xml_data = ""
        for line in self.__lines:
            if line.startswith(keyword):
                found_keyword = True
                xml_data += line.split(keyword)[-1].strip()
                if xml_data.startswith("<") and xml_data.endswith(">"):
                    try:
                        return xmltodict.parse(xml_data)
                    except xmltodict.ParsingInterrupted:
                        raise ValueError(f"Invalid XML data for keyword '{keyword}'")

        if not found_keyword:
            raise ValueError(f"Keyword '{keyword}' not found in the file")
        else:
            raise ValueError(f"Invalid XML data for keyword '{keyword}'")

    # ------------------------------------------------------------------------------------------

    def read_full_xml(self, keyword: str = None):
        """
        Read the XML data. If a keyword is provided, search for the specified
        keyword in the XML data and return the nested elements beneath it.
        If no keyword is provided, return the full XML data.

        :param keyword: The keyword to search for in the XML data.
        :return: The XML data as a dictionary object or the nested elements
                 as an ElementTree object if a keyword is provided.
        :raises ValueError: If the keyword is specified but not found in the XML data.

        If you assume the input file titled example.xml has the following format:

        .. code-block:: xml

           <root>
               <key1>value1</key1>
               <key2>
                   <subkey1>subvalue1</subkey1>
                   <subkey2>
                       <subsubkey1>subsubvalue1</subsubvalue1>
                       <subsubkey2>subsubvalue2</subsubvalue2>
                   </subkey2>
               </key2>
           </root>

        The code to extract data would look like:

        .. code-block:: python

           reader = ReadKeyWords("example.xml")
           value = reader.read_full_xml()
           print(value)

           >> {
               "root": {
                   "key1": "value1",
                   "key2": {
                       "subkey1": "subvalue1",
                       "subkey2": {
                           "subsubkey1": "subsubvalue1",
                           "subsubkey2": "subsubvalue2"
                       }
                   }
               }
           }

           new_value = reader.read_full_xml("subkey2")
           print(new_value)
           >> {
               "subkey1": "subvalue1",
               "subkey2": {
                   "subsubkey1": "subsubvalue1",
                   "subsubkey2": "subsubvalue2"
               }
           }
        """
        tree = ET.parse(self._file_name)
        root = tree.getroot()
        if keyword is None:
            xml_string = ET.tostring(root, encoding="utf-8").decode()
            return xmltodict.parse(xml_string)
        else:
            elements = root.findall(f".//{keyword}")
            if elements:
                xml_string = ET.tostring(elements[0], encoding="utf-8").decode()
                return xmltodict.parse(xml_string)
            else:
                raise ValueError(f"Keyword '{keyword}' not found in the XML data")

    # ==========================================================================================
    # PRIVATE-LIKE methods

    def _read_lines(self):
        """
        This private method will read in all lines from the text file
        """
        with open(self._file_name) as file:
            lines = [line.strip() for line in file]
        return lines

    # ------------------------------------------------------------------------------------------

    def __str__(self):
        """
        This private method determines how many of the lines are to be printed to
        screen and pre-formats the data for printing.
        """
        num_lines = min(self.print_lines, len(self.__lines))
        return "\n".join(self.__lines[:num_lines])


# ==========================================================================================
# ==========================================================================================
# READ COLUMNAR DATA


def read_csv_columns_by_headers(
    file_name: str, headers: dict[str, type], skip: int = 0
) -> pd.DataFrame:
    """

    :param file_name: The file name to include path-link
    :param headers: A dictionary of column names and their data types.
                    types are limited to ``numpy.int64``, ``numpy.float64``,
                    and ``str``
    :param skip: The number of lines to be skipped before reading data
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    This function assumes the file has a comma (i.e. ,) delimiter, if
    it does not, then it is not a true .csv file and should be transformed
    to a text function and read by the read_text_columns_by_headers function.
    Assume we have a .csv file titled ``test.csv`` with the following format.

    .. list-table:: test.csv
      :widths: 6 10 6 6
      :header-rows: 1

      * - ID,
        - Inventory,
        - Weight_per,
        - Number
      * - 1,
        - Shoes,
        - 1.5,
        - 5
      * - 2,
        - t-shirt,
        - 1.8,
        - 3,
      * - 3,
        - coffee,
        - 2.1,
        - 15
      * - 4,
        - books,
        - 3.2,
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_csv_columns_by_headers

       > file_name = 'test.csv'
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float. 'Number': int}
       > df = read_csv_columns_by_headers(file_name, headers)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test1.csv
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - ID,
        - Inventory,
        - Weight_per,
        - Number
      * - 1,
        - Shoes,
        - 1.5,
        - 5
      * - 2,
        - t-shirt,
        - 1.8,
        - 3,
      * - 3,
        - coffee,
        - 2.1,
        - 15
      * - 4,
        - books,
        - 3.2,
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_csv_columns_by_headers

       > file_name = 'test1.csv'
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int}
       > df = read_csv_columns_by_headers(file_name, headers, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    head = list(headers.keys())
    df = pd.read_csv(file_name, usecols=head, dtype=headers, skiprows=skip)
    return df


# ----------------------------------------------------------------------------


def read_csv_columns_by_index(
    file_name: str,
    headers: dict[int, type],
    col_names: list[str],
    skip: int = 0,
) -> pd.DataFrame:
    """
    :param file_name: The file name to include path-link
    :param headers: A dictionary of column index and their data types.
                    types are limited to ``numpy.int64``, ``numpy.float64``,
                    and ``str``
    :param col_names: A list containing the names to be given to
                      each column
    :param skip: The number of lines to be skipped before reading data
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    This function assumes the file has a comma (i.e. ,) delimiter, if
    it does not, then it is not a true .csv file and should be transformed
    to a text function and read by the xx function.  Assume we have a .csv
    file titled ``test.csv`` with the following format.

    .. list-table:: test.csv
      :widths: 6 10 6 6
      :header-rows: 0

      * - 1,
        - Shoes,
        - 1.5,
        - 5
      * - 2,
        - t-shirt,
        - 1.8,
        - 3,
      * - 3,
        - coffee,
        - 2.1,
        - 15
      * - 4,
        - books,
        - 3.2,
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_csv_columns_by_index

       > file_name = 'test.csv'
       > headers = {0: int, 1: str, 2: float, 3: int}
       > names = ['ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_csv_columns_by_index(file_name, headers, names)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test1.csv
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - 1,
        - Shoes,
        - 1.5,
        - 5
      * - 2,
        - t-shirt,
        - 1.8,
        - 3,
      * - 3,
        - coffee,
        - 2.1,
        - 15
      * - 4,
        - books,
        - 3.2,
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_csv_columns_by_index

       > file_name = 'test1.csv'
        > headers = {0: int, 1: str, 2: float, 3: int}
       > names = ['ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_csv_columns_by_index(file_name, headers,
                                        names, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    col_index = list(headers.keys())
    df = pd.read_csv(
        file_name, usecols=col_index, names=col_names, dtype=headers, skiprows=skip
    )
    return df


# ------------------------------------------------------------------------------------------


def read_text_columns_by_headers(
    file_name: str,
    headers: dict[str, type],
    skip: int = 0,
    delimiter=r"\s+",
) -> pd.DataFrame:
    """

    :param file_name: The file name to include path-link
    :param headers: A dictionary of column names and their data types.
                    types are limited to ``numpy.int64``, ``numpy.float64``,
                    and ``str``
    :param skip: The number of lines to be skipped before reading data
    :param delimiter: The type of delimiter separating data in the text file.
                Defaulted to space delimited, where a space is one or
                more white spaces.  This function can use any delimiter,
                to include a comma separation; however, a comma delimiter
                should be a .csv file extension.
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    This function assumes the file has a space delimiter, if
    Assume we have a .csv file titled ``test.txt`` with the following
    format.

    .. list-table:: test.txt
      :widths: 6 10 6 6
      :header-rows: 1

      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_text_columns_by_headers

       > file_name = 'test.txt'
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int}
       > df = read_text_columns_by_headers(file_name, headers)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test.txt
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_text_columns_by_headers

       > file_name = 'test.txt'
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int}
       > df = read_text_columns_by_headers(file_name, headers, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    head = list(headers.keys())
    df = pd.read_csv(file_name, usecols=head, dtype=headers, skiprows=skip, sep=delimiter)
    return df


# --------------------------------------------------------------------------------


def read_text_columns_by_index(
    file_name: str,
    headers: dict[int, type],
    col_names: list[str],
    skip: int = 0,
    delimiter=r"\s+",
) -> pd.DataFrame:
    """

    :param file_name: The file name to include path-link
    :param headers: A dictionary of column index` and their data types.
                    types are limited to ``numpy.int64``, ``numpy.float64``,
                    and ``str``
    :param col_names: A list containing the names to be given to
                      each column
    :param skip: The number of lines to be skipped before reading data
    :param delimiter: The type of delimiter separating data in the text file.
                Defaulted to space delimited, where a space is one or
                more white spaces.  This function can use any delimiter,
                to include a comma separation; however, a comma delimiter
                should be a .csv file extension.
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    Assume we have a .txt file titled ``test.txt`` with the following format.

    .. list-table:: test.txt
      :widths: 6 10 6 6
      :header-rows: 0

      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_text_columns_by_index

       > file_name = 'test.txt'
       > headers = {0: int, 1: str, 2: float, 3: int}
       > names = [ headers = {'ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_text_columns_by_index(file_name, headers, names)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test.txt
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_text_columns_by_index

       > file_name = 'test.txt'
       > headers = {0: int, 1: str, 2: float, 3: int}
       > names = ['ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_text_columns_by_index(file_name, headers,
                                         names, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    head = list(headers.keys())
    df = pd.read_csv(
        file_name,
        usecols=head,
        names=col_names,
        dtype=headers,
        skiprows=skip,
        sep=delimiter,
    )
    return df


# ------------------------------------------------------------------------------------------


def read_excel_columns_by_headers(
    file_name: str, tab: str, headers: dict[str, type], skip: int = 0
) -> pd.DataFrame:
    """

    :param file_name: The file name to include path-link.  Must be an
                      .xls file format.  This code will **not** read .xlsx
    :param tab: The tab or sheet name that data will be read from
    :param headers: A dictionary of column names and their data types.
                    types are limited to ``numpy.int64``, ``numpy.float64``,
                    and ``str``
    :param skip: The number of lines to be skipped before reading data
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    Assume we have a .xls file titled ``test.xls`` with the following format
    in a tab titled ``primary``.

    .. list-table:: test.xls
      :widths: 6 10 6 6
      :header-rows: 1

      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       > file_name = 'test.xls'
       > tab = "primary"
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int}
       > df = read_excel_columns_by_headers(file_name, tab, headers)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test.xls
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_excel_columns_by_headers

       > file_name = 'test.xls'
       > tab = "primary"
       > headers = ['ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int]
       > df = read_excel_columns_by_headers(file_name, tab,
                                            headers, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    head = list(headers.keys())
    df = pd.read_excel(
        file_name,
        sheet_name=tab,
        usecols=head,
        dtype=headers,
        skiprows=skip,
        engine="openpyxl",
    )
    return df


# ----------------------------------------------------------------------------


def read_excel_columns_by_index(
    file_name: str,
    tab: str,
    col_index: dict[int, str],
    col_names: list[str],
    skip: int = 0,
) -> pd.DataFrame:
    """

    :param file_name: The file name to include path-link.  Must be an
                      .xls file format.  This code will **not** read .xlsx
    :param tab: The tab or sheet name that data will be read from
    :param col_index: A dictionary of column index` and their data types.
                     types are limited to ``numpy.int64``, ``numpy.float64``,
                     and ``str``
    :param col_names: A list containing the names to be given to
                      each column
    :param skip: The number of lines to be skipped before reading data
    :return df: A pandas dataframe containing all relevant information
    :raises FileNotFoundError: If the file is found to not exist

    Assume we have a .txt file titled ``test.xls`` with the following format.

    .. list-table:: test.xls
      :widths: 6 10 6 6
      :header-rows: 0

      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_excel_columns_by_index

       > file_name = 'test.xls'
       > tab = 'primary'
       > headers = {0: int, 1: str, 2: float, 3: int}
       > names = ['ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_excel_columns_by_index(file_name, tab, headers, names)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40

    This function can also use the `skip` attributed read data when the
    headers are not on the first line.  For instance, assume the following csv file;

    .. list-table:: test.xls
      :widths: 16 8 5 5
      :header-rows: 0

      * - This line is used to provide metadata for the csv file
        -
        -
        -
      * - This line is as well
        -
        -
        -
      * - ID
        - Inventory
        - Weight_per
        - Number
      * - 1
        - Shoes
        - 1.5
        - 5
      * - 2
        - t-shirt
        - 1.8
        - 3
      * - 3
        - coffee
        - 2.1
        - 15
      * - 4
        - books
        - 3.2
        - 48

    This file can be read via the following command

    .. code-block:: python

       from cobralib.io import read_excel_columns_by_index

       > file_name = 'test.xls'
       > tab = "primary"
       > headers = {0: int, 1: str, 2: float, 3: int}
       > names = ['ID', 'Inventory', 'Weight_per', 'Number']
       > df = read_excel_columns_by_index(file_name, tab, headers,
                                          names, skip=2)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")
    head = list(col_index.keys())
    df = pd.read_excel(
        file_name,
        sheet_name=tab,
        usecols=head,
        names=col_names,
        dtype=col_index,
        skiprows=skip,
        header=None,
        engine="openpyxl",
    )
    return df


# ==========================================================================================
# ==========================================================================================
# READ AND WRITE TO YAML


def read_yaml_file(file_path: str, safe: bool = False, **kwargs) -> list[Any]:
    """
    This function can be used to read in the contents of a single yaml file, or
    a yaml file with multiple documents.  In order to accomodate thea reading
    of several documents, the contents are returned as a list, with each
    index representing a different document.  **NOTE** Under the hood, this
    funtion is using the pyyaml library and has all of its attributes.

    :param file_name: The file name to be read including the path length
    :param print_lines: The number of lines to be printed to the screen if the
                        user prints an instance of the class. Defaulted to 50
    :raises FileNotFoundError: If the file does not exist

    Example file titled test_file.yaml

    .. literalinclude:: ../../../data/test/test_file.yaml
       :language: text

    .. code-block:: python

       from cobralib.io import read_yaml_file

       data = read_yaml_file('test_file.yaml', safe=True)
       print(data)
       >> [{'name': 'John Doe', 'age': 25, 'occupation': 'Developer', 'hobbies':
          ['Reading', 'Coding', 'Playing guitar']}, {'name': 'Alice Smith',
           'age': 30, 'occupation': 'Designer', 'hobbies':
           ['Painting', 'Traveling', 'Hiking']}]

    """

    try:
        with open(file_path) as file:
            if safe:
                documents = list(yaml.safe_load_all(file, **kwargs))
            else:
                documents = list(yaml.load_all(file, Loader=yaml.Loader, **kwargs))
        return [doc for sublist in documents for doc in sublist]
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")


# ------------------------------------------------------------------------------------------


def write_yaml_file(file_path: str, data: dict, append: bool = False) -> None:
    """
    Write or append data to a YAML file.

    :param file_path: The path of the YAML file
    :param data: The data to be written or appended as a dictionary
    :param append: True to append data to the file, False to overwrite
                   the file or create a new one (default: False)
    :raises FileNotFoundError: If the file does not exist in append mode

    .. code-block:: python

       from corbalib.io import write_yaml_file

       dict_file = {'sports' : ['soccer', 'football', 'basketball',
                    'cricket', 'hockey', 'table tennis']},
                    {'countries' : ['Pakistan', 'USA', 'India',
                    'China', 'Germany', 'France', 'Spain']}
       # Create new yaml file
       write_yaml_file('new_file.yaml', data, dict_file, append=False)

    This will create a file titled new_file.yaml with the following contents

    .. literalinclude:: ../../../data/test/output.yaml
       :language: text

    """
    mode = "a" if append else "w"

    if append and not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    try:
        with open(file_path, mode) as file:
            if append:
                file.write("---\n")  # Add YAML document separator
            yaml.safe_dump(data, file)
    except OSError as e:
        print(f"Error writing to file: {e}")


# ==========================================================================================
# ==========================================================================================


class Logger:
    """
    Custom logging class that writes messages to both console and log file.

    :param filename: The name of the file to write logs to.
    :param console_level: The minimum logging level for the console. Should be one
                          of: 'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
                          'CRITICAL'.
    :param file_level: The minimum logging level for the log file. Should be one of:
                       'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
    :param max_lines: The maximum number of lines in the log file. When exceeded,
                      the oldest entries are deleted.
    :raises ValueError: If `console_level` or `file_level` are not valid logging
                        levels.
    :raises IOError: If an I/O error occurs when opening the file.

    **Example usage:**

    .. code-block:: python

        # create logger with filename='my_log.log', console_level='INFO',
        # file_level='DEBUG', and max_lines=100

        logger = Logger('my_log.log', 'INFO', 'DEBUG', 100)

        # log a DEBUG message
        logger.log('DEBUG', 'This is a debug message')

        # log an INFO message
        logger.log('INFO', 'This is an info message')
    """

    def __init__(self, filename, console_level, file_level, max_lines):
        self.filename = filename
        self.max_lines = max_lines

        # Creating logger
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(logging.DEBUG)

        # Creating console handler and setting its level
        ch = logging.StreamHandler()
        ch.setLevel(self._str_to_log_level(console_level))

        # Creating file handler and setting its level
        fh = logging.handlers.RotatingFileHandler(filename, backupCount=1)
        fh.setLevel(self._str_to_log_level(file_level))

        # Creating formatter
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(fmt)

        # Setting formatter for ch and fh
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Adding ch and fh to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    # ------------------------------------------------------------------------------------------

    def _str_to_log_level(self, level):
        """
        Convert string representation of logging level to corresponding
        logging module constants.

        :param level: The string representation of the logging level.
        :return: Corresponding logging level.
        """
        levels = {
            "NOTSET": logging.NOTSET,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(level, logging.NOTSET)

    # ------------------------------------------------------------------------------------------

    def log(self, level, msg):
        """
        Write a log entry.

        :param level: The level of the log entry. Should be one of: 'NOTSET',
                      'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
        :param msg: The message to be logged.
        :raises ValueError: If `level` is not a valid logging level.
        """
        self.logger.log(self._str_to_log_level(level), msg)
        self._trim_log_file()

    def _trim_log_file(self):
        """
        Trims the log file to the last `max_lines` entries.

        :raises IOError: If an I/O error occurs when trying to trim the file.
        """
        try:
            with open(self.filename, "r+") as f:
                lines = deque(f, self.max_lines)
                f.seek(0)
                f.writelines(lines)
                f.truncate()
        except OSError:
            self.logger.exception("Error while trimming log file")


# ==========================================================================================
# ==========================================================================================
# Database class


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
    :raises ConnectionError: If a connection can not be established
    :ivar conn: The connection attribute of the mysql-connector-python module.
    :ivar cur: The cursor method for the mysql-connector-python module.
    :ivar database: The name of the database currently being used.
    """

    def __init__(self, username, password, port=3306, hostname="localhost"):
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self.database = None
        self.conn = None
        self.cur = None

        self._create_connection(password)

    # ------------------------------------------------------------------------------------------

    def change_db(self, db_name) -> None:
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

    def close_conn(self) -> None:
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

    def get_dbs(self) -> pd.DataFrame:
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

    def get_db_tables(self, db: str = None) -> pd.DataFrame:
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
            self.conn.execute(f"SHOW TABLES FROM {db}")
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

    def query_db(self, query: str, params: tuple = ()) -> pd.DataFrame:
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
        txt_file: str,
        table_name: str,
        txt_columns: list,
        table_columns: list = None,
        delemeter: str = ",",
        skip: int = 0,
    ) -> None:
        """
        Read data from a CSV or TXT file and insert it into the specified table.

        :param txt_file: The path to the CSV file or TXT file.
        :param table_name: The name of the table.
        :param txt_columns: The names of the columns in the TXT file.
        :param table_columns: The names of the columns in the table (default is None,
                              assumes CSV column names and table column names
                              are the same).
        :param delemeter: The seperating delimeter in the text file.  Defaulted to
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
           db.csv_to_table('csv_file.csv', 'FirstLastName', ['FirstName', 'LastName'],
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
           db.csv_to_table('txt_file.txt', 'FirstLastName', ['FirstName', 'LastName'],
                           ['First', 'Last'], delemeter=r"\\s+", skip=2)
           query = "SELDCT * FROM Names;"
           result = db.query_db(query)
           print(result)
           >> index  name_id First   Last
              0      1       Jon     Webb
              1      2       Fred    Smith
              2      3       Jillian Webb
        """
        if len(txt_columns) == 0:
            raise ValueError("CSV column names are required.")

        try:
            csv_data = pd.read_csv(txt_file, sep=delemeter, skiprows=skip)

            if table_columns is None:
                table_columns = txt_columns

            sanitized_columns = [
                self._sanitize_column_name(name) for name in table_columns
            ]

            for _, row in csv_data.iterrows():
                insert_data = {}
                for i, column in enumerate(table_columns):
                    value = row[txt_columns[i]]
                    insert_data[column] = value

                placeholders = ", ".join(["%s"] * len(insert_data))
                if table_columns is not None:
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
        excel_columns: list,
        table_columns: list = None,
        sheet_name: str = "Sheet1",
        skip: int = 0,
    ) -> None:
        """
        Read data from an Excel file and insert it into the specified table.

        :param excel_file: The path to the Excel file.
        :param table_name: The name of the table.
        :param excel_columns: The names of the columns in the Excel file.
        :param table_columns: The names of the columns in the table (default is None,
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
           db.csv_to_table('excel_file.xlsx', 'FirstLastName', ['FirstName', 'LastName'],
                           ['First', 'Last'])
           query = "SELDCT * FROM Names;"
           result = db.query_db(query)
           print(result)
           >> index  name_id First   Last
              0      1       Jon     Webb
              1      2       Fred    Smith
              2      3       Jillian Webb
        """
        if len(excel_columns) == 0:
            raise ValueError("Excel column names are required.")

        try:
            excel_data = pd.read_excel(
                excel_file, sheet_name=sheet_name, usecols=excel_columns, skiprows=skip
            )
            if table_columns is None:
                table_columns = excel_columns

            sanitized_columns = [
                self._sanitize_column_name(name) for name in table_columns
            ]
            for _, row in excel_data.iterrows():
                insert_data = {}
                for i, column in enumerate(table_columns):
                    value = row[excel_columns[i]]
                    insert_data[column] = value

                placeholders = ", ".join(["%s"] * len(insert_data))
                if table_columns is not None:
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
# eof
