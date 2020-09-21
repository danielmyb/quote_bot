#!/usr/bin/env python

"""Controller for event checking."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging
import time
from datetime import datetime

from telegram import ParseMode

from control.bot_control import BotControl
from control.database_controller import DatabaseController

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class EventChecker:
    """Checker for events."""

    def __init__(self, updater):
        """Constructor."""
        self.interval = None
        self.user = None

        self.updater = updater
        self.interval = DatabaseController.configuration['configuration_values']['event_checker']['interval']

    def check_events(self):
        """Checks the events of all user regularly and pings them."""
        userdata = DatabaseController.load_all_events_from_all_users()
        today = "{}".format(datetime.today().weekday())
        for user_id in userdata:
            events_of_today = userdata[user_id][today]
            self._check_event_ping(user_id, events_of_today)
        time.sleep(self.interval)
        self.check_events()

    def _check_event_ping(self, user_id, events):
        """Check which events are not already passed and pings the user.
        Args:
            user_id (int): ID of the user.
            events (dict): Contains all events of the user for a single day.
        """
        current_time = datetime.now()
        bot = BotControl.get_bot()

        ping_list = []
        for event in events:
            event_hour, event_minute = event["ping_time"].split(":")
            if int(event_hour) > current_time.hour or \
                    (int(event_hour) == current_time.hour and int(event_minute) > current_time.minute):
                logger.info("CT: %s | ET: %s", current_time, event["ping_time"])
                ping_list.append(event)

        if ping_list:
            message = self.build_ping_message(ping_list)
            bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

    def build_ping_message(self, events):
        """Generates the ping message for the user.
        Args:
            events (list of 'dict'): Contains all events of a user for a given day that are not passed yet.
        Returns:
            str: Formatted message.
        """
        message = "*EVENT REMINDER*\n\n"

        for event in events:
            message += "*Event:* {}\n".format(event["title"])
            message += "*Inhalt:* {}\n".format(event["content"])
            message += "*Start:* {}\n".format(event["ping_time"])
            message += "\n"

        return message
