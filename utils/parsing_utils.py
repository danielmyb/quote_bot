#!/usr/bin/env python

"""Utils regarding parsing input of the user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------

RESERVED_CHARACTERS = {"!": "", "_": " ", "*": ""}


def replace_reserved_characters(input_string):
    """Replaced reserved characters inside the given string with preset replacements.
    Args:
        input_string (str): String that should be checked for reserved characters.
    Returns:
        str: String with replaced characters.
    """
    for char in RESERVED_CHARACTERS:
        input_string = input_string.replace(char, RESERVED_CHARACTERS[char])
    return input_string
