# Import necessary packages here
import os
from typing import Any

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
