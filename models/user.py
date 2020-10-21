#!/usr/bin/env python

"""Model for user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from control.database_controller import DatabaseController
from models.day import DayEnum
from models.event import EventType, Event


class User:

    def __init__(self, user_id, telegram_user=None):
        """Constructor.
        Args:
            user_id (int): ID of the user.
            telegram_user (telegram.User, optional): Telegram user object.
        """
        self.telegram_user = telegram_user
        self.user_id = user_id
        self.user_config = DatabaseController.load_user_config(self.user_id)
        self.language = self.user_config["language"]

    @staticmethod
    def resolve_user(update, user_id=None):
        """Resolves the user from the given update object.
        Args:
            update (telegram.Update): Update object.
            user_id (int): Needed in case of group queries. From user is then the ID of the bot and thus
                a ID has to be given.

        Returns:
            user: User object.
        """
        if update.message.chat['type'] == "group":
            user = User(update.message.chat.id, update.message.from_user)
        elif user_id:
            user = User(update.message.chat.id, user_id)
        else:
            user = User(update.message.from_user.id, update.message.from_user)
        return user

    def is_group(self):
        """Determines whether the user object is representing a single user or a group."""
        return self.user_id < 0

    def retrieve_all_events(self):
        """Retrieve all events of the user.
        Returns:
            dict: Contains all events of the user.
        """
        event_list = []

        for event in DatabaseController.load_user_events(self.user_id):
            name = event["name"]
            day = DayEnum(event["day"])
            content = event["content"]
            event_type = EventType(event["event_type"])
            ping_time = event["event_time"]
            event_list.append(Event(name, day, content, event_type, ping_time))

        return event_list
