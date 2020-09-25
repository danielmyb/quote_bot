#!/usr/bin/env python

"""Model for days."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import json
import os

from utils.path_utils import DATA_PATH

LOCALIZATION_PATH = os.path.join(DATA_PATH, "localization.json")
DEFAULT_LANGUAGE = "DE"


def receive_translation(keyword, language=DEFAULT_LANGUAGE):
    """Retrieve the translation of a given keyword for the chosen language.
    Args:
        keyword (str): Keyword that the correct translation is searched for.
        language (str): Language in whose the keyword should be returned.
    Returns:
        str: Localized keyword.
    """
    with open(LOCALIZATION_PATH, "r", encoding='UTF-8') as localization_file:
        localization_data = json.load(localization_file)
        if not localization_data[keyword]:
            raise RuntimeError("Trying to access unknown keyword.")
        # If there is no localization for the keyword return the default one.
        if not localization_data[keyword][language]:
            return localization_data[keyword][DEFAULT_LANGUAGE]
        return localization_data[keyword][language]


def receive_languages():
    """Retrieve all available languages.
    Returns:
        dict: Contains all languages with their keywords.
    """
    with open(LOCALIZATION_PATH, "r", encoding='UTF-8') as localization_file:
        localization_data = json.load(localization_file)
    return localization_data["languages"]
