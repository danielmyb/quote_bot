#!/usr/bin/env python

"""Controller for database access."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import json
import logging
import os

from utils.path_utils import USERDATA_PATH, PROJECT_ROOT

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class DatabaseController:

    configuration = {}

    def __init__(self):
        DatabaseController.load_configuration()

    @staticmethod
    def load_configuration():
        """Loads the configuration from file or provides it if it was already loaded.
        Returns:
            dict: Loaded configuration.
        """
        if DatabaseController.configuration:
            return DatabaseController.configuration
        with open(os.path.join(PROJECT_ROOT, "configuration.json")) as configuration_file:
            return json.load(configuration_file)

    def check_or_create_database(self, user_id):
        """
        Args:
            user_id (int): Id of user.
        Returns:
            bool: True if new DB was created, False if not.
        """

        user_id_string = "{}".format(user_id)
        userdata_path = os.path.join(USERDATA_PATH, "{}.json".format(user_id_string))

        if os.path.isfile(userdata_path):
            return False
        with open(userdata_path, "w") as userdata_file:
            userdata_file.write("{}")
        return True

    def save_event_data(self, user_id, data):
        """
        Args:
            user_id (int): Id of user.
            data (dict):
        Returns:

        """

    def load_event_data(self, user_id):
        """
        Args:
            user_id (int): Id of user.
        Returns:

        """
