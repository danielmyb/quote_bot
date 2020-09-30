#!/usr/bin/env python

"""Controller for event checking."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging
import time
from datetime import datetime, timedelta

from telegram import ParseMode

from control.bot_control import BotControl
from control.database_controller import DatabaseController
from models.event import EventType
from utils.localization_manager import receive_translation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class EventChecker:
    """Checker for events."""

    def __init__(self):
        """Constructor."""

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
        # Trigger a cleanup
        self.removed_passed_single_events(userdata)
        self.check_events()

    def _ping_users(self, userdata, day):
        """Pings all users inside userdata with the events of the given day
        Args:
            userdata (dict): Contains the data of all users.
            day (int): Represents the day which should be pinged for.
        """
        tomorrow = day + 1 if day < 6 else 0
        day = "{}".format(day)
        tomorrow = "{}".format(tomorrow)
        for user_id in userdata:
            events_of_today = userdata[user_id][day]
            events_of_tomorrow = userdata[user_id][tomorrow]
            self._check_event_ping(user_id, events_of_today)
            self._check_event_ping(user_id, events_of_tomorrow, today=False)

    def _check_event_ping(self, user_id, events, today=True):
        """Check which events are not already passed and pings the user.
        Args:
            user_id (int): ID of the user.
            events (dict): Contains all events of the user for a single day.
            today (bool, optional): Indicates whether the events of today or tomorrow are checked.
                Checking today by default.
        """
        bot = BotControl.get_bot()

        ping_list = []
        for event in events:
            if (not self.check_event_passed(event) or not today) and self.check_ping_needed(user_id, event, today):
                ping_list.append(event)

        # Only ping if there are events to notify about
        if ping_list:
            message = self.build_ping_message(user_id, ping_list)
            bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

    @staticmethod
    def check_ping_needed(user_id, event, today=True):
        """Checks if an event needs to be pinged.
        Args:
            user_id (int): ID of the user.
            event (dict): Contains the event that should be checked.
            today (bool, optional): Indicates whether today or tomorrow is checked.
        Returns:
            bool: True if a ping has to be sent. False if not.
        """
        current_time = datetime.now()
        ping_times = event["ping_times"]

        event_day = current_time.day
        event_month = current_time.month
        if not today:
            event_date = current_time + timedelta(days=1)
            event_day = event_date.day
            event_month = event_date.month

        event_time = datetime(year=current_time.year, month=event_month, day=event_day,
                              hour=int(event["event_time"].split(":")[0]),
                              minute=int(event["event_time"].split(":")[1]))

        needs_ping = False

        for ping_time in ping_times:
            # If multiple ping times are already reached ping one time and disable all "used" times.
            if ping_times[ping_time]:
                delta = timedelta(hours=int(ping_time.split(':')[0]), minutes=int(ping_time.split(':')[1]))
                if event_time - delta < current_time:
                    event["ping_times"][ping_time] = False
                    needs_ping = True

        if needs_ping:
            # Save the changes on the event
            logger.info(event_time)
            DatabaseController.save_changes_on_event(user_id, event_time.weekday(), event)

        return needs_ping

    @staticmethod
    def check_event_passed(event):
        """Checks if the given event is already passed.
        Args:
            event (dict): Contains an event.
        Returns:
            bool: Determines whether the event has passed or not.
        """
        event_hour, event_minute = event["event_time"].split(":")
        current_time = datetime.now()
        if int(event_hour) > current_time.hour or (int(event_hour) == current_time.hour and
                                                   int(event_minute) > current_time.minute):
            return False
        return True

    @staticmethod
    def build_ping_message(user_id, events):
        """Generates the ping message for the user.
        Args:
            user_id (int): ID of the user - needed for localization.
            events (list of 'dict'): Contains all events of a user for a given day that are not passed yet.
        Returns:
            str: Formatted message.
        """
        user_language = DatabaseController.load_selected_language(user_id)
        message = "*{}*\n\n".format(receive_translation("event_reminder", user_language))

        for event in events:
            message += "*{}:* {}\n".format(receive_translation("event", user_language), event["title"])
            message += "*{}:* {}\n".format(receive_translation("event_content", user_language), event["content"])
            message += "*{}:* {}\n".format(receive_translation("event_start", user_language), event["event_time"])
            message += "\n"

        return message

    def removed_passed_single_events(self, userdata):
        """Removes passed non-regularly events from the event lists of all users.
        Args:
            userdata (dict): Contains all event data of all users.
        """
        today = "{}".format(datetime.today().weekday())

        for user_id in userdata:
            # Track that at least on change was done so that no useless database operation is called
            at_least_one_change = False
            days = userdata[user_id]
            for day in days:
                if day > today:
                    break
                for event in days[day]:
                    # Do not remove regularly events
                    if event["event_type"] == EventType.REGULARLY:
                        continue
                    if day < today:
                        passed = True
                    else:
                        passed = self.check_event_passed(event)
                    if passed:
                        userdata[user_id][day].remove(event)
                        at_least_one_change = True
            if at_least_one_change:
                DatabaseController.save_all_events_for_user(user_id, userdata[user_id])
