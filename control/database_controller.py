#!/usr/bin/env python

"""Controller for database access."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import json
import logging
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class DatabaseController:

    def __init__(self):
        self.data = {}
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "quotes.json")) as quotes_file:
            self.data = json.load(quotes_file)

        logger.info("Data %s loaded", self.data)

    def save_data(self, data):
        """
        Args:
            data (dict):
        Returns:

        """

    def load_data(self, user):
        """
        Args:
            user (string): 
        Returns:

        """