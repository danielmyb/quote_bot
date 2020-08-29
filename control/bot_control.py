#!/usr/bin/env python

"""Controller for bot related actions."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import os

import telegram
from telegram.ext import Updater

from utils.path_utils import DATA_PATH


class BotControl:
    """Holds shortcuts and controlling options for the bot."""
    token = None

    @classmethod
    def setup_bot(cls):
        """
        Returns:

        """
        token_file_path = os.path.join(DATA_PATH, ".token")
        if not token_file_path:
            raise RuntimeError("Token file {} was not found!".format(token_file_path))

        with open(token_file_path) as token_file:
            cls.token = token_file.read()

        if not cls.token:
            raise RuntimeError("Token in {} was empty".format(token_file_path))

        # Create the Updater and pass it your bots token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(cls.token, use_context=True)
        return updater

    @classmethod
    def get_bot(cls):
        """
        Returns:

        """
        return telegram.Bot(token=cls.token)
