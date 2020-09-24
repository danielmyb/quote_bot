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
from models.event import EventType

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
        today = datetime.today().weekday()
        self._ping_users(userdata, today)

        time.sleep(self.interval)

        # Check if a new day has begun
        current_day = datetime.today().weekday()
        if today != current_day:
            # Use fresh userdata
            userdata = DatabaseController.load_all_events_from_all_users()
            self._ping_users(userdata, current_day)
            # Trigger weekly reset when a new week is reached
            self.removed_passed_single_events(userdata, current_day < today)
        else:
            # Trigger a regular cleanup
            self.removed_passed_single_events(userdata)
        self.check_events()

    def _ping_users(self, userdata, day):
        """Pings all users inside userdata with the events of the given day
        Args:
            userdata (dict): Contains the data of all users.
            day (int): Represents the day which should be pinged for.
        """
        day = "{}".format(day)
        for user_id in userdata:
            events_of_today = userdata[user_id][day]
            self._check_event_ping(user_id, events_of_today)

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
            if not self.check_event_passed(event):
                ping_list.append(event)

        # Only ping if there are events to notify about
        if ping_list:
            message = self.build_ping_message(ping_list)
            bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

    @staticmethod
    def check_event_passed(event):
        event_hour, event_minute = event["event_time"].split(":")
        current_time = datetime.now()
        if int(event_hour) > current_time.hour or (int(event_hour) == current_time.hour and
                                                   int(event_minute) > current_time.minute):
            return False
        return True

    @staticmethod
    def build_ping_message(events):
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
            message += "*Start:* {}\n".format(event["event_time"])
            message += "\n"

        return message

    def removed_passed_single_events(self, userdata, weekly_cleanup=False):
        """Removes passed non-regularly events from the event lists of all users.
        Args:
            userdata (dict): Contains all event data of all users.
            weekly_cleanup (bool, optional): Indicates whether all non-regularly events should be cleared or not.
        """
        today = "{}".format(datetime.today().weekday())

        for user_id in userdata:
            # Track that at least on change was done so that no useless database operation is called
            at_least_one_change = False
            days = userdata[user_id]
            for day in days:
                if not weekly_cleanup and day > today:
                    break
                for event in days[day]:
                    # Do not remove regularly events
                    if event["event_type"] == EventType.REGULARLY:
                        continue
                    if weekly_cleanup or day < today:
                        passed = True
                    else:
                        passed = self.check_event_passed(event)
                    if passed:
                        userdata[user_id][day].remove(event)
                        at_least_one_change = True
            if at_least_one_change:
                DatabaseController.save_all_events_for_user(user_id, userdata[user_id])
