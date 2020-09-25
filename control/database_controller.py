#!/usr/bin/env python

"""Controller for database access."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import glob
import json
import logging
import os

from models.day import DayEnum
from utils.localization_manager import DEFAULT_LANGUAGE
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
                user_dict = {"user_id": user_id, "language": DEFAULT_LANGUAGE, "events": {}}
                for day in DayEnum:
                    user_dict["events"][day.value] = []
                json.dump(user_dict, userdata_file)

        with open(userdata_path, "r") as userdata_file:
            userdata = json.load(userdata_file)

        return userdata

    @staticmethod
    def load_selected_language(user_id):
        """Loads the code of language the user has selected.
        Args:
            user_id (int): ID of the User
        Returns:
            str: Code of the language.
        """
        user_id_string = "{}".format(user_id)
        userdata_path = os.path.join(USERDATA_PATH, "{}.json".format(user_id_string))

        with open(userdata_path, "r") as userdata_file:
            userdata = json.load(userdata_file)

        return userdata["language"]

    @staticmethod
    def save_day_event_data(user_id, day, event):
        """Saves the event data of a given day of a given user into the database
        Args:
            user_id (int): ID of user.
            day (int): Day of the event.
            event (Event): Event that should be saved.
        """
        logger.info("%s %s %s", user_id, day, event)
        userdata = DatabaseController.load_user_entry(user_id)

        userdata["events"][day] += [{"title": event.name, "content": event.content,
                                     "event_type": event.event_type.value, "event_time": event.event_time}]
        user_id_string = "{}".format(user_id)
        userdata_path = os.path.join(USERDATA_PATH, "{}.json".format(user_id_string))

        with open(userdata_path, "w") as userdata_file:
            json.dump(userdata, userdata_file)

    @staticmethod
    def read_event_data_of_user(user_id):
        """Reads the event data of a given user.
        Args:
            user_id (int): ID of user.
        Returns:

        """
        user_data = DatabaseController._read_user_data(user_id)
        return user_data["events"]

    @staticmethod
    def _read_user_data(user_id):
        """Reads the data of the given user.
        Args:
            user_id (int): ID of the user whose data should be read.
        Returns:
            dict: Contains all data of the user.
        """
        userdata_file = os.path.join(USERDATA_PATH, "{}.json".format(user_id))
        with open(userdata_file, "r") as userdata_content:
            content = json.load(userdata_content)
        return content

    @staticmethod
    def _save_user_data(user_id, content):
        """Saves the data of the given user.
        Args:
            user_id (int): ID of the user whose data should be saved.
            content (dict): Contains the user data.
        """
        userdata_file = os.path.join(USERDATA_PATH, "{}.json".format(user_id))
        with open(userdata_file, "w") as userdata_content:
            json.dump(content, userdata_content)

    @staticmethod
    def load_all_events_from_all_users():
        """Loads all saved events from all users.
        Returns:
            dict: Contains all events of all users.
        """
        userdata_files = glob.glob("{}/*.json".format(USERDATA_PATH))
        userdata = {}
        for userdata_file in userdata_files:
            with open(userdata_file, "r") as userdata_content:
                content = json.load(userdata_content)
                userdata["{}".format(content["user_id"])] = content["events"]

        return userdata

    @staticmethod
    def save_all_events_for_user(user_id, event_data):
        """Saves all events for a given user.
        Args:
            user_id (int): ID of the user.
            event_data (dict): Contains the event data of a user.
        """
        content = DatabaseController._read_user_data(user_id)
        content["events"] = event_data
        DatabaseController._save_user_data(user_id, content)

    @staticmethod
    def save_user_language(user_id, language):
        """Saves the selected language for the given user.
        Args:
            user_id (int): ID of the user whose language should be changed.
            language (str): Code of the desired language.
        """
        content = DatabaseController._read_user_data(user_id)
        content["language"] = language
        DatabaseController._save_user_data(user_id, content)

    @staticmethod
    def save_daily_ping(user_id, daily_ping):
        """Saves the selected daily ping config for the given user.
        Args:
            user_id (int): ID of the user.
            daily_ping (bool): Indicates whether a daily ping should be done or not.
        """
        content = DatabaseController._read_user_data(user_id)
        content["daily_ping"] = daily_ping
        DatabaseController._save_user_data(user_id, content)
