#!/usr/bin/env python

"""Model for user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from control.database_controller import DatabaseController
from models.event import EventType, Event


class User:

    def __init__(self, user):
        """Constructor.
        Args:
            user (telegram.User):
        """
        self.telegram_user = user
        self.user_data = DatabaseController.load_user_entry(self.telegram_user.id)
        self.language = self.user_data["language"]

    def retrieve_all_events(self):
        """
        Returns:

        """
        event_list = []

        if not self.user_data["events"]:
            return None

        for event in self.user_data["events"]:
            name = event["name"]
            content = event["content"]
            event_type = EventType(event["event_type"])
            ping_time = event["event_time"]
            event_list.append(Event(name, content, event_type, ping_time))

        return event_list
