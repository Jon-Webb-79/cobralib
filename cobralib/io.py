# Import necessary packages here
import json
import logging
import logging.handlers
import os
import xml.etree.ElementTree as ET
from collections import deque
from typing import Any, Union

import pandas as pd
import pdfplumber
import xmltodict
import yaml

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


class ReadYAML:
    """

    :param file_name: The name and path length for the file with the yaml-like
                      format
    :raises FileNotFoundError: If the file does not exist.

    This class can be used to read a file woith a YAML-like format.  This class is
    tailoered to read basic YAML files, but with looser requirements on how
    key words are formatted, and stricter requirements on data typing. The methods
    within this class can be used to read scalar variables from key-variable pairs,
    lists, and flat dictionaries.  This class also enforces type casting for all
    variables read into memory. This class is more meory efficient than using
    PyYAML, since it only reads the requested lines to memory.

    All code examples described in the documentation for this class reference
    the read_yaml.yaml file shown below.

    .. literalinclude:: ../../../data/test/read_yaml.yaml
       :language: text
    """

    def __init__(self, file_name: str):
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"FATAL ERROR: {file_name} does not exist")
        self._file_name = file_name
        self.__lines = self._read_lines()

    # ------------------------------------------------------------------------------------------

    def read_key_value(
        self, keyword: str, data_type: type, document_index: int = 0
    ) -> Any:
        """
        :param keyword: The keyword associated with the value to be read in. Unlike a
                        pure YAML file this value does not have to end with a :
                        symbol
        :param data_type: The data type of the value to be read in
        :param document_index: The number of the yaml document in the yaml file.
        :return value: The value associated with a keyword
        :raise ValueError: If the value can not be cast to the user defined type

        This method can be used to read a key-value pair from a yaml or yaml-like
        file.  This method will rcognize the >, ^, and | symbols that symbolize
        strings that either start on the next line, or multiline strings.

        Example 1
        ---------
        An example of a python code to read an float value from the
        1st yaml document.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           value = reader.read_key_value('key:', float, 0)
           print(value)
           >> 4.387

        Example 2
        ---------
        An example to read a multiline string value from the second yaml document
        in the file

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           value = reader.read_key_value('Multi Sentence:', str, 1)
           new_value = reader.read_key_value('Second Mult Sentence:', str, 1)
           print(value)
           print(new_value)

        .. code-block:: bash

            >> This is a multiline sentence,
               there is no reason to worry!
            >> This is a multiline sentence, there is no reason to worry!

        Example 3
        ---------
        An example that shows the different way boolean values can be read into
        memory.  A value of True, on, or yes will equate to True and values of
        False, off, no will equate to False.  The values in the yaml-like
        file are case insensitive.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           true_value = reader.read_key_value('bool test1:', bool, 1)
           yes_value = reader.read_key_value('bool test4:', bool, 1)
           on_value = reader.read_key_value('bool test5:', bool, 1)
           false_value = reader.read_key_value('bool test2:', bool, 1)
           no_value = reader.read_key_value('bool test3:', bool, 1)
           off_value = reader.read_key_value('bool test6:', bool, 1)

        .. code-block:: bash

           >> True
           >> True
           >> True
           >> False
           >> False
           >> False
        """
        yaml_docs = self._read_yaml_documents()
        self._check_document_length(document_index, yaml_docs)

        lines = yaml_docs[document_index].split("\n")
        for i, line in enumerate(lines):
            stripped_line = line.lstrip()
            if stripped_line.startswith(keyword):
                keyword_indent = len(line) - len(stripped_line)
                value_str = stripped_line[len(keyword) :].strip()
                return self._parse_value(
                    value_str, lines[i + 1 :], keyword_indent, data_type
                )

        raise ValueError(f"Keyword '{keyword}' not found in the specified document")

    # ------------------------------------------------------------------------------------------

    def read_yaml_list(
        self, keyword: str, data_type: type, document_index: int = 0
    ) -> list[Any]:
        """
        :param keyword: The keyword associated with the value to be read in. Unlike
                        a pure YAML file, this value does not have to end with a :
                        symbol.
        :param data_type: The data type of the value to be read in
        :param document_index: The number of the yaml document in the yaml file.
        :return value: The list associated with a keyword
        :raise ValueError: If the value can not be cast to the user defined type

        This method can be used to read a key-value pair from a yaml or yaml-like
        file where the value is a list of values.  This method will rcognize the
        >, ^, and | symbols that symbolize strings that either start on the next
        line, or multiline strings.

        Example 1
        ---------
        An example of a python code to read a list of integer values from the
        1st yaml document.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           list_values = reader.read_yaml_list('First List:', int, 0)
           print(list_values)

        .. code-block:: bash

            >> [1.1, 2.2, 3.3, 4.4]

        Example 2
        ---------
        This method will also read string values from the list that may use the
        ^, > or | symbols that signify the string as starting on the next line,
        a multi-line string that should be read into one line, or a multiline
        string that should be read as a multiline string.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           list_values = reader.read_yaml_list('Numbers:', int, 0)
           print(list_values)

        .. code-block:: text

            >> ['Hello World
                 This is Jon',
                'This',
                'Is',
                'Correct']
        """
        yaml_docs = self._read_yaml_documents()
        self._check_document_length(document_index, yaml_docs)

        lines = yaml_docs[document_index].split("\n")
        values = []
        is_reading_list = False
        keyword_indent = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.lstrip()
            current_indent = len(line) - len(stripped_line)

            if stripped_line.startswith(keyword):
                keyword_indent = current_indent
                is_reading_list = True

                # Check for an inline list
                rest_of_line = stripped_line[len(keyword) :].strip()
                if rest_of_line.startswith("[") and rest_of_line.endswith("]"):
                    inline_list = rest_of_line[1:-1].split(",")
                    for x in inline_list:
                        try:
                            values.append(data_type(x.strip()))
                        except ValueError:
                            raise ValueError("Invalid value")
                    return values

                i += 1  # Move to the next line
                continue

            if is_reading_list:
                if current_indent <= keyword_indent:
                    break

                # Add list items
                if stripped_line.startswith("-"):
                    value_str = stripped_line[1:].strip()  # Remove "-" and leading spaces

                    # Check for special string types
                    if value_str in ["^", ">", "|"]:
                        complex_str = value_str
                        value_str = ""
                        i += 1
                        while i < len(lines):
                            next_line = lines[i]
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= current_indent:
                                i -= (
                                    1  # Step back to let the outer loop process this line
                                )
                                break

                            if complex_str == "^":
                                value_str = next_line.strip()
                                break
                            elif complex_str == "|":
                                value_str += next_line.strip() + "\n"
                            elif complex_str == ">":
                                next_line_content = next_line[current_indent:].lstrip()
                                value_str += next_line_content + " "
                            i += 1

                        if complex_str == ">":
                            value_str = value_str.rstrip()

                    try:
                        values.append(data_type(value_str))
                    except ValueError:
                        raise ValueError("Invalid value")

            i += 1
        msg = f"Keyword '{keyword}' not found or it is "
        msg += "not a list in the specified document."
        if not is_reading_list:
            raise ValueError(msg)

        return values

    # ------------------------------------------------------------------------------------------

    def read_yaml_dict(
        self,
        keyword: str,
        key_data_type: type,
        value_data_type: type,
        document_index: int = 0,
    ) -> dict:
        """
        :param keyword: The keyword associated with the value to be read in. Unlike
                        a pure YAML file, this value does not have to end with a :
                        symbol.
        :param key_data_type: The data type of the key value.
        :param value_data_type: The data type of the value to be read in
        :param document_index: The number of the yaml document in the yaml file.
        :return value: The dictionary associated with a keyword
        :raise ValueError: If the value can not be cast to the user defined type

        This method can be used to read a key-value pair from a yaml or yaml-like
        file where the value is a dictionary of values.  This method will recognize
        the >, ^, and | symbols that symbolize strings that either start on the next
        line, or multiline strings. **NOTE:** This method assumes a flat
        (i.e. not nested) dictionary structure.

        Example 1
        ---------
        An example of a python code to read a list of integer values from the
        1st yaml document.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           value = reader.read_yaml_dict('Ages:', 'str', 'int', 1)
           print(value)

        .. code-block:: text

            >> {'Jon': 44. 'Jill': 32, 'Bob': 12}
        """
        yaml_docs = self._read_yaml_documents()
        self._check_document_length(document_index, yaml_docs)

        lines = yaml_docs[document_index].split("\n")
        found_dict = {}
        is_reading_dict = False
        keyword_indent = None
        val_str = ""

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.lstrip()
            current_indent = len(line) - len(stripped_line)

            if stripped_line.startswith(keyword):
                is_reading_dict = True
                keyword_indent = current_indent
                i += 1  # Move to the next line
                continue

            if is_reading_dict:
                if current_indent <= keyword_indent:
                    break

                # Ensure this line is part of the dict
                if ":" in stripped_line:
                    key_str, value_str = map(str.strip, stripped_line.split(":", 1))
                    key = self._parse_value(key_str, [], current_indent, key_data_type)

                    if value_str in ["^", ">", "|"]:
                        value_str = ""
                        i += 1
                        while i < len(lines):
                            next_line = lines[i]
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= current_indent:
                                i -= 1
                                break
                            value_str += next_line + "\n"  # Add the line to value_str
                            i += 1
                        # Remove trailing newline and pass all lines for parsing
                        val_str = value_str
                        value_str = value_str.rstrip("\n")
                        value = self._parse_value(
                            value_str,
                            value_str.split("\n"),
                            current_indent,
                            value_data_type,
                        )
                        value = self._remove_uniform_indent(value)
                    else:
                        value = self._parse_value(
                            value_str, [], current_indent, value_data_type
                        )
                    if val_str in [">", "|"]:
                        print("YES")
                        value = self._remove_uniform_indent(value)

                    found_dict[key] = value

            i += 1
        msg = f"Keyword '{keyword}' not found or it is not a "
        msg += " dictionary in the specified document."
        if not is_reading_dict:
            raise ValueError(msg)

        return found_dict

    # ------------------------------------------------------------------------------------------

    def read_full_yaml(self, safe_read: bool = True) -> Any:
        """
        Reads the full YAML file and returns it as a PyYAML object.

        :params safe_read: Whether to read the file in a safe more or not.
                           Defaulted to True
        :return Any: The full content of the YAML file as a PyYAML object. This method
                     assumes the possibility of multiple documents in one file. The
                     result is returned as a list

        Unlike other methods in this class, this method will read an entire yaml file
        into memory and return a PyYaml object.  This is not as memory efficient as the
        other methods, but this will make the accessing of data quicker for larger
        files.  In addition, the user must adhere to the strict rules of YAML
        when using this method.  The rules for a PyYaml class can be
        found at `PyYaml <https://pyyaml.org/wiki/PyYAMLDocumentation>`_.

        Example 1
        ---------
        An example of a python code to read a list of integer values from the
        1st yaml document.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           data = reader.read_full_yaml()  # Read in as safe mode
           print(data[1]['Ages'])

        .. code-block:: text

            >> {'Jon': 44. 'Jill': 32, 'Bob': 12}
        """
        with open(self._file_name) as file:
            if safe_read:
                return list(yaml.safe_load_all(file))
            else:
                return list(yaml.load_all(file))

    # ------------------------------------------------------------------------------------------

    def read_yaml_dict_of_list(
        self,
        keyword: str,
        key_data_type: type,
        list_data_type: type,
        document_index: int = 0,
    ) -> dict:
        """
        :param keyword: The keyword associated with the value to be read in. Unlike
                        a pure YAML file, this value does not have to end with a :
                        symbol.
        :param key_data_type: The data type of the key value.
        :param list_data_type: The data type of the value to be read in
        :param document_index: The number of the yaml document in the yaml file.
        :return value: The dictionary associated with a keyword
        :raise ValueError: If the value can not be cast to the user defined type

        This method can be used to read a key-value pair from a yaml or yaml-like
        file where the value is a dictionary of lists.  This method will recognize
        the >, ^, and | symbols that symbolize strings that either start on the next
        line, or multiline strings. **NOTE:** This method assumes a flat
        (i.e. not nested) dictionary structure.

        Example 1
        ---------
        An example of a python code to read a dictionary of integer list values
        from the 1st yaml document.

        .. code-block:: python

           from cobralib.io import ReadYAML

           reader = ReadYAML('read_yaml.yaml')
           value = reader.read_yaml_dict('Dict List:', 'str', 'int', 0)
           print(value)

        .. code-block:: text

            >> {'One': [1, 2, 3], 'Two': [3, 4, 5], 'Three': [6, 7, 8]}
        """
        yaml_docs = self._read_yaml_documents()
        self._check_document_length(document_index, yaml_docs)

        lines = iter(yaml_docs[document_index].split("\n"))  # Convert to an iterator
        is_reading_dict = False
        keyword_indent = None
        current_dict = {}
        current_list = None

        for line in lines:
            stripped_line = line.lstrip()
            current_indent = len(line) - len(stripped_line)

            if stripped_line.startswith(keyword):
                is_reading_dict = True
                keyword_indent = current_indent
                continue

            if is_reading_dict:
                if current_indent <= keyword_indent:
                    break

                if ":" in stripped_line:
                    key, value = map(str.strip, stripped_line.split(":", 1))
                    key = key_data_type(key)

                    if value.startswith("[") and value.endswith("]"):
                        current_list = [
                            list_data_type(v.strip()) for v in value[1:-1].split(",")
                        ]
                        current_dict[key] = current_list
                        current_list = None
                    else:
                        current_list = []
                        current_dict[key] = current_list
                elif stripped_line.startswith("-"):
                    value_str = stripped_line[1:].strip()
                    complex_str = None
                    if value_str in ["^", ">", "|"]:
                        complex_str = value_str
                        value_str = self._parse_block_scalar(
                            lines, current_indent, complex_str
                        )
                    current_list.append(list_data_type(value_str))
        msg = f"Keyword '{keyword}' not found or it is not "
        msg += "dictionary of lists in the specified document."
        if not is_reading_dict:
            raise ValueError(msg)

        return current_dict

    # ==========================================================================================
    # PRIVATE-LIKE methods

    def _read_lines(self):
        """
        This private method will read in all lines from the text file
        """
        with open(self._file_name) as file:
            lines = [line.rstrip() for line in file]
        return lines

    # ------------------------------------------------------------------------------------------

    def _read_yaml_documents(self):
        yaml_docs = list(
            filter(lambda x: x.strip(), "\n".join(self.__lines).split("---"))
        )
        return yaml_docs

    # ------------------------------------------------------------------------------------------

    def _check_document_length(self, document_index, yaml_docs) -> None:
        if document_index >= len(yaml_docs) or document_index < 0:
            raise ValueError(
                f"""Document index {document_index} out of range.
                              File contains {len(yaml_docs)} documents."""
            )

    # ------------------------------------------------------------------------------------------

    def _calculate_indent(self, line: str):
        return len(line) - len(line.lstrip())

    # ------------------------------------------------------------------------------------------

    def _parse_block_scalar(self, lines: iter, current_indent: int, complex_str: str):
        value_str = ""
        lines_iter = iter(lines)
        while True:
            line = next(lines_iter, "").rstrip()
            next_indent = self._calculate_indent(line)
            if next_indent <= current_indent:
                break

            line_content = line[next_indent:].lstrip()
            if complex_str == "^":
                value_str = line_content.strip()
                break
            elif complex_str == "|":
                value_str += line_content + "\n"
            elif complex_str == ">":
                value_str += line_content + " "
        return value_str.rstrip() if complex_str in ["|", ">"] else value_str

    # ------------------------------------------------------------------------------------------

    def _remove_uniform_indent(self, multi_line_str: str) -> str:
        lines = multi_line_str.split("\n")

        # Calculate the minimum number of leading white spaces
        min_indent = float("inf")  # Set to infinity initially
        for line in lines:
            stripped_line = line.lstrip()
            if stripped_line:  # Ignore empty lines
                indent = len(line) - len(stripped_line)
                min_indent = min(min_indent, indent)

        # Remove the minimum indent from each line
        lines = [line[min_indent:] for line in lines]

        return "\n".join(lines)

    # ------------------------------------------------------------------------------------------

    def _parse_value(
        self, value_str: str, subsequent_lines: list, keyword_indent: int, data_type: type
    ) -> Any:
        if data_type == bool:
            value_str = value_str.lower()
            if value_str.upper() in ["TRUE", "YES", "ON"]:
                return True
            elif value_str.upper() in ["FALSE", "NO", "OFF"]:
                return False
            else:
                raise ValueError("Invalid boolean value")

        if data_type == str and value_str in ["^", ">", "|"]:
            value_str = self._parse_block_scalar(
                subsequent_lines, keyword_indent, value_str
            )

        try:
            return data_type(value_str)
        except ValueError:
            raise ValueError("Invalid value")


# ==========================================================================================
# ==========================================================================================


class ReadJSON:
    """

    :param file_name: The name and path length for the file with the yaml-like
                      format
    :raises FileNotFoundError: If the file does not exist.

    This class can be used to read a file woith a JSON-like format.  This class is
    tailoered to read basic JSON files, but with looser requirements on how
    key words are formatted, and stricter requirements on data typing. The methods
    within this class can be used to read scalar variables from key-variable pairs,
    lists, and flat dictionaries.

    All code examples described in the documentation for this class reference
    the read_yaml.yaml file shown below.

    """

    def __init__(self, file_name: str):
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"FATAL ERROR: {file_name} does not exist")
        self._file_name = file_name
        self.__lines = self._read_lines()

    # ------------------------------------------------------------------------------------------

    def read_json(self, keyword: str) -> dict:
        """
        Search each line for the specified keyword and read the JSON data
        to the right of the keyword until the termination of brackets.

        :param keyword: The keyword to search for in each line.
        :return: The JSON data as a dictionary.
        :raises ValueError: If the keyword is not found or if the JSON data is not valid.

        Example 1
        ---------
        This example shows a file that mixes YAML and JSON data types.  In order
        to delinate the file type that contains mixed data, it is recommended that
        the .jwc file format be used; however, it is not required.

        .. code-block:: text

            Yaml Dict:
                - 1
                - 2
                - 3
            Yaml Key: Test String
            Yaml Dict:
                One: 1.1
                Two: 2.2
                Three: 3.3
            Json Book Data: {"book": "History of the World", "year": 1976}

        .. code-block:: python

           # Instantiate the class
           reader = ReadKeyWords("test_key_words.jwc")
           value = reader.read_json("JSON Book Data:")
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

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _read_lines(self):
        """
        This private method will read in all lines from the text file
        """
        with open(self._file_name) as file:
            lines = [line.rstrip() for line in file]
        return lines


# ==========================================================================================
# ==========================================================================================


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

    def read_variable(
        self, keyword: str, data_type: type, document_index: int = 0
    ) -> Any:
        """
        Search each line for the specified keyword and read the variable to the
        right of the keyword as the specified data type

        :param keyword: The keyword to search for in each line.
        :param data_type: The data type to be used in order to casy the variable
        :param document_index: The document number if the file is a yaml file with
                               multiple documents in the file
        :return: The float variable to the right of the keyword.
        :raises ValueError: If the keyword is not found or if the variable cannot
                            be parsed as a float.

        .. code-block:: python

           import numpy as np
           from cobralib.io import ReadKeyWords

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

           from cobralib.io import ReadKeyWords
           # Instantiate the class
           reader = ReadKeyWords("test_key_words.txt")
           value = reader.read_variable("String:", str)
           print(value)
           print(type(value))

           >> "Hello"
           >> str

        This method also works with yaml files.  Assume a .yaml or .yml file with the
        following content.

        .. literalinclude:: ../../../data/test/read_yaml.yaml
          :language: text

        .. code-block:: python

           from cobralib.io import ReadKeyWords

           # Instantiate the class
           reader = ReadKeyWords("read_yaml.yaml")
           value = reader.read_variable("age:", int, 1)
           print(value)
           print(type(value))

           >> 30
           >> int
        """
        # Split the file contents into separate YAML documents based on '---'
        yaml_docs = "\n".join(self.__lines).split("---")

        if document_index >= len(yaml_docs) or document_index < 0:
            raise ValueError(
                f"""Document index {document_index} out of range.
                              File contains {len(yaml_docs)} documents."""
            )

        # Iterate over lines in the specified YAML document
        for line in yaml_docs[document_index].split("\n"):
            if line.startswith(keyword):
                value_str = line[len(keyword) :].strip()
                try:
                    return data_type(value_str)
                except ValueError:
                    raise ValueError(f"Invalid value found for {keyword}")

        raise ValueError(f"Keyword '{keyword}' not found in the specified document")

    # ------------------------------------------------------------------------------------------

    def read_string_variable(self, keyword: str, document_index: int = 0) -> str:
        """
        Search each line for the specified keyword and read the string variable
        to the right of the keyword.

        :param keyword: The keyword to search for in each line.
        :param document_index: The document number if the file is a yaml file with
                               multiple documents in the file
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

        # Split the file contents into separate YAML documents based on '---'
        yaml_docs = "\n".join(self.__lines).split("---")

        if document_index >= len(yaml_docs) or document_index < 0:
            raise ValueError(
                f"""Document index {document_index} out of range.
                              File contains {len(yaml_docs)} documents."""
            )

        lines = yaml_docs[document_index].split("\n")

        for i, line in enumerate(lines):
            if line.startswith(keyword):
                value = line[len(keyword) :].strip()

                if value == "^" and i + 1 < len(lines):
                    return lines[i + 1].strip()

                if value == "|":
                    multiline_values = []
                    # Determine the indentation of the current keyword line
                    indentation = len(line) - len(line.lstrip())
                    print(indentation)
                    # Start reading lines from the next line after '|'
                    for subsequent_line in lines[i + 1 :]:
                        # If we encounter a line with equal or lesser indentation,
                        # we've found the end of the multiline string.
                        if (
                            len(subsequent_line) - len(subsequent_line.lstrip())
                            <= indentation
                        ):
                            break
                        multiline_values.append(subsequent_line)
                    return "\n".join(multiline_values)

                return value

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


# ------------------------------------------------------------------------------------------


def read_pdf_columns_by_headers(
    file_name: str,
    headers: dict[str, type],
    table_idx: int = 0,
    page_num: int = 0,
    skip: int = 0,
) -> pd.DataFrame:
    """
    Read a table from a PDF document and save user-specified columns into a pandas
    DataFrame. This function will read a pdf table that spans multiple
    pages. **NOTE:** The pdf document must be a vectorized pdf document and not
    a scan of another document for this function to work.

    :param file_name: The file name to include the path-link to the PDF file.
    :param headers: A dictionary of column names and their data types.
                    Data types are limited to ``int``, ``float``, and ``str``.
    :param table_idx: Index of the table to extract from the page (default: 0).
    :param page_num: Page number from which to extract the table (default: 0).
    :param skip: The number of lines to be skipped before reading data
    :return df: A pandas DataFrame containing the specified columns from the table.
    :raises FileNotFoundError: If the PDF file is found to not exist.

    Example usage:

    .. code-block:: python

       from cobralib.io import read_pdf_columns_by_headers

       > file_name = 'test.pdf'
       > headers = {'ID': int, 'Inventory': str, 'Weight_per': float, 'Number': int}
       > df = read_pdf_columns_by_headers(file_name, headers, table_idx=0, page_num=1)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")

    # Extract tables from the specified page of the PDF using pdfplumber
    with pdfplumber.open(file_name) as pdf:
        page = pdf.pages[page_num]
        table = page.extract_tables()

    if table_idx >= len(table):
        raise ValueError(f"Table index {table_idx} out of range.")

    # Convert the table to a pandas DataFrame
    df = pd.DataFrame(table[table_idx][1:], columns=table[table_idx][0])

    # Skip specified number of rows before reading the header
    df = df.iloc[skip:]

    # Filter out columns based on user-specified headers
    selected_columns = [column for column in headers.keys() if column in df.columns]
    df = df[selected_columns]

    # Rename the columns to match the user-specified headers
    df.columns = list(headers.keys())

    # Convert the columns to the specified data types
    for column, dtype in headers.items():
        df[column] = df[column].astype(dtype)

    return df


# ------------------------------------------------------------------------------------------


def read_pdf_columns_by_index(
    file_name: str,
    headers: dict[int, type],
    col_names: list[str],
    table_idx: int = 0,
    skip_rows: int = 0,
    page_num: int = 0,
) -> pd.DataFrame:
    """
    Read a table from a PDF document and save user-specified columns into a pandas
    DataFrame based on their column index. This function will read a pdf table that
    spans multiple pages. **NOTE:** The pdf document must be a vectorized pdf
    document and not a scan of another document for this function to work.

    :param file_name: The file name to include the path-link to the PDF file.
    :param headers: A dictionary of column index and their data types.
                    Data types are limited to ``int``, ``float``, and ``str``.
    :param col_names: A list containing the names to be given to each column.
    :param table_idx: Index of the table to extract from the page (default: 0).
    :param skip_rows: Number of rows to skip before reading the header row (default: 0).
    :param page_num: Page number from which to extract the table (default: 0).
    :return df: A pandas DataFrame containing the specified columns from the table.
    :raises FileNotFoundError: If the PDF file is found to not exist.

    Example usage:

    .. code-block:: python

       from cobralib.io import read_pdf_columns_by_index

       > file_name = 'test.pdf'
       > headers = {0: int, 1: str, 2: float, 3: int}
       > col_names = ['ID', 'Inventory', 'Weight_per', 'Number']  # Column names
       > df = read_pdf_columns_by_index(file_name, headers, col_names,
                                        table_idx=0, skip_rows=2, page_num=1)
       > print(df)
           ID Inventory Weight_per Number
        0  1  shoes     1.5        5
        1  2  t-shirt   1.8        3
        2  3  coffee    2.1        15
        3  4  books     3.2        40
    """
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File '{file_name}' not found")

    # Extract tables from the specified page of the PDF using pdfplumber
    with pdfplumber.open(file_name) as pdf:
        page = pdf.pages[page_num]
        table = page.extract_tables()

    if table_idx >= len(table):
        raise ValueError(f"Table index {table_idx} out of range.")

    # Convert the table to a pandas DataFrame
    df = pd.DataFrame(table[table_idx][1:], columns=table[table_idx][0])

    # Skip specified number of rows before reading the header
    df = df.iloc[skip_rows:]

    # Filter out columns based on user-specified column indices
    selected_columns = [
        col_idx for col_idx in headers.keys() if col_idx < len(df.columns)
    ]
    df = df.iloc[:, selected_columns]

    # Rename the columns with user-specified column names
    df.columns = col_names[: len(selected_columns)]

    dat_type = list(headers.values())
    name_dict = dict(zip(col_names, dat_type))
    # Convert the columns to the specified data types
    for column, dtype in name_dict.items():
        df[column] = df[column].astype(dtype)

    return df


# ==========================================================================================
# ==========================================================================================
# READ AND WRITE TO YAML


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
# eof
