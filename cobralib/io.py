# Import necessary packages here
import json
import os
import xml.etree.ElementTree as ET
from typing import Any, Union

import xmltodict

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
# eof
