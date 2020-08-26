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
        """Constructor."""
        DatabaseController.configuration = DatabaseController.load_configuration()

    @staticmethod
    def load_configuration():
        """Loads the configuration from file or provides it if it was already loaded.
        Returns:
            dict: Loaded configuration.
        """
        if DatabaseController.configuration:
            logger.info(DatabaseController.configuration)
            return DatabaseController.configuration
        with open(os.path.join(PROJECT_ROOT, "configuration.json")) as configuration_file:
            json_content = json.load(configuration_file)
            logger.info(json_content)
            return json_content

    @staticmethod
    def load_user_entry(user_id):
        """
        Args:
            user_id (int): ID of user.

        Returns:
            dict: Data of the user as dict.
        """
        user_id_string = "{}".format(user_id)
        userdata_path = os.path.join(USERDATA_PATH, "{}.json".format(user_id_string))

        if not os.path.isfile(userdata_path):
            with open(userdata_path, "w") as userdata_file:
                user_dict = {"user_id": user_id}
                json.dump(user_dict, userdata_file)

        with open(userdata_path, "r") as userdata_file:
            userdata = json.load(userdata_file)

        return userdata

    def save_event_data(self, user_id, data):
        """
        Args:
            user_id (int): ID of user.
            data (dict):
        Returns:

        """

    def load_event_data(self, user_id):
        """
        Args:
            user_id (int): ID of user.
        Returns:

        """
