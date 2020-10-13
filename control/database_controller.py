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
import uuid

from models.day import DayEnum
from models.event import Event, EventType
from utils.localization_manager import DEFAULT_LANGUAGE
from utils.path_utils import USERDATA_PATH, CONFIG_PATH

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class DatabaseController:
    configuration = {}
    config_file = CONFIG_PATH
    userdata_path = USERDATA_PATH

    def __init__(self, config_file=CONFIG_PATH, userdata_path=USERDATA_PATH):
        """Constructor."""
        DatabaseController.config_file = config_file
        DatabaseController.userdata_path = userdata_path
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
        with open(DatabaseController.config_file) as configuration_file:
            json_content = json.load(configuration_file)
            logger.info(json_content)
            return json_content

    @staticmethod
    def load_user_config(user_id):
        """Loads the user config entry of the given user.
        Args:
            user_id (int): ID of user.
        Returns:
            dict: Config of the user as dict.
        """
        user_id_string = str(user_id)
        user_config_path = os.path.join(DatabaseController.userdata_path, "{}_config.json".format(user_id_string))

        if not os.path.isfile(user_config_path):
            with open(user_config_path, "w") as user_config_file:
                user_config_dict = {"user_id": user_id, "language": DEFAULT_LANGUAGE, "daily_ping": True}
                json.dump(user_config_dict, user_config_file)

        with open(user_config_path, "r") as user_config_file:
            user_config = json.load(user_config_file)

        return user_config

    @staticmethod
    def load_user_events(user_id):
        """Loads the user events entry of the given user.
        Args:
            user_id (int): ID of user.
        Returns:
            list of 'Event': Events of the user as list.
        """
        user_events_dict = DatabaseController._load_user_event_entry(user_id)

        user_events = []
        for event_id in user_events_dict:
            event = user_events_dict[event_id]
            event_object = Event(event['title'], DayEnum(event['day']), event['content'],
                                 EventType(event['event_type']), event['event_time'], event['ping_times'],
                                 start_ping_done=event['start_ping_done'])
            if "ping_times_to_refresh" in event.keys():
                event_object.ping_times_to_refresh = event['ping_times_to_refresh']
            event_object.uuid = event_id
            user_events.append(event_object)

        return user_events

    @staticmethod
    def _load_user_event_entry(user_id):
        """Loads the user events entry of the given user and returns it as dict.
        Args:
            user_id (int): ID of user.
        Returns:
            dict: Events of the user as dict.
        """
        user_id_string = str(user_id)
        user_events_path = os.path.join(DatabaseController.userdata_path, "{}_events.json".format(user_id_string))

        if not os.path.isfile(user_events_path):
            with open(user_events_path, "w") as user_events_file:
                user_events_dict = {}
                json.dump(user_events_dict, user_events_file)

        with open(user_events_path, "r") as user_events_file:
            user_events_dict = json.load(user_events_file)

        return user_events_dict

    @staticmethod
    def load_selected_language(user_id):
        """Loads the code of language the user has selected.
        Args:
            user_id (int): ID of the User
        Returns:
            str: Code of the language.
        """
        user_id_string = "{}".format(user_id)
        userdata_path = os.path.join(DatabaseController.userdata_path, "{}_config.json".format(user_id_string))

        with open(userdata_path, "r") as userdata_file:
            userdata = json.load(userdata_file)

        return userdata["language"]

    @staticmethod
    def save_event_data_user(user_id, event):
        """Saves the event data of a given day of a given user into the database
        Args:
            user_id (int): ID of user.
            event (Event): Event that should be saved.
        """
        user_event_data = DatabaseController._load_user_event_entry(user_id)
        if not event.uuid:
            user_event_data_id = uuid.uuid4().hex
            while user_event_data_id in user_event_data:
                user_event_data_id = uuid.uuid4().hex
            event.uuid = user_event_data_id

        user_event_data[event.uuid] = {"title": event.name, "day": event.day.value, "content": event.content,
                                       "event_type": event.event_type.value, "event_time": event.event_time,
                                       "ping_times": event.ping_times, "in_daily_ping": event.in_daily_ping,
                                       "start_ping_done": event.start_ping_done,
                                       "ping_times_to_refresh": event.ping_times_to_refresh}

        DatabaseController._save_event_data_user(user_id, user_event_data)

    @staticmethod
    def _save_event_data_user(user_id, user_event_data):
        """Saves the event data of user.
        Args:
            user_id (int): ID of user.
            user_event_data (dict): Event data of the user.
        """
        user_id_string = str(user_id)
        user_event_data_path = os.path.join(DatabaseController.userdata_path, "{}_events.json".format(user_id_string))

        with open(user_event_data_path, "w") as user_event_data_file:
            json.dump(user_event_data, user_event_data_file)

    @staticmethod
    def read_event_of_user(user_id, event_id):
        """Read the event data of a user for the given day with the given name.
        Args:
            user_id (int): ID of user.
            event_id (str): ID of the event.
        Returns:
            dict: Contains all data of the event.
        """
        user_events = DatabaseController._load_user_event_entry(user_id)
        if event_id in user_events.keys():
            return user_events[event_id]
        return None

    @staticmethod
    def delete_event_of_user(user_id, event_id):
        """Removes the event with the given name from the given user on the given day.
        Args:
            user_id (int): ID of user.
            event_id (str): ID of the event.
        """
        event_data = DatabaseController._load_user_event_entry(user_id)
        if event_id in event_data:
            event_data.pop(event_id)
            DatabaseController._save_event_data_user(user_id, event_data)

    @staticmethod
    def _read_user_data(user_id):
        """Reads the data of the given user.
        Args:
            user_id (int): ID of the user whose data should be read.
        Returns:
            dict: Contains all data of the user.
        """
        userdata_file = os.path.join(DatabaseController.userdata_path, "{}_config.json".format(user_id))
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
        userdata_file = os.path.join(DatabaseController.userdata_path, "{}_config.json".format(user_id))
        with open(userdata_file, "w") as userdata_content:
            json.dump(content, userdata_content)

    @staticmethod
    def load_all_user_ids():
        """Loads all users that are stored inside the database.
        Returns:
            list of 'str': Contains all user ids.
        """
        user_data_config_files = glob.glob("{}/*_config.json".format(DatabaseController.userdata_path))

        users = [os.path.basename(user_data_config_file).split('_')[0] for user_data_config_file in
                 user_data_config_files]

        return users

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
