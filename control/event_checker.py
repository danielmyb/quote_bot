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
from models.event import Event
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
            self._refresh_start_pings(userdata, today)
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
            ping_needed, event_delete = self.check_ping_needed(user_id, event, today)
            if ping_needed:
                event['deleted'] = event_delete
                ping_list.append(event)

        # Only ping if there are events to notify about
        if ping_list:
            for event in ping_list:
                message = self.build_ping_message(user_id, event)
                if event['deleted']:
                    bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    language = DatabaseController.load_selected_language(user_id)
                    weekday = datetime.now().weekday() if today else (datetime.now() + timedelta(days=1)).weekday()
                    postfix = "_{}_{}".format(weekday, event['title'])
                    bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=Event.event_keyboard_alteration(language, "event", postfix))

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

        event_deleted = False

        # Cleanup event if it is passed
        if event_time < current_time and not event.get("start_ping_done", False):
            needs_ping = True
            if event["event_type"] == 1:
                DatabaseController.delete_event_of_user(user_id, event_time.weekday(), event["title"])
                event_deleted = True
            else:
                event["start_ping_done"] = True

        if needs_ping:
            # Save the changes on the event
            DatabaseController.save_changes_on_event(user_id, event_time.weekday(), event)

        return needs_ping, event_deleted

    @staticmethod
    def check_event_passed(event, today=True):
        """Checks if the given event is already passed.
        Args:
            event (dict): Contains an event.
            today (bool, optional): Indicates whether today or tomorrow is checked.
        Returns:
            bool: Determines whether the event has passed or not.
        """
        if not today:
            return False
        event_hour, event_minute = event["event_time"].split(":")
        current_time = datetime.now()
        if int(event_hour) > current_time.hour or (int(event_hour) == current_time.hour and
                                                   int(event_minute) > current_time.minute):
            return False
        return True

    @staticmethod
    def build_ping_message(user_id, event):
        """Generates the ping message for the user.
        Args:
            user_id (int): ID of the user - needed for localization.
            event (dict): Contains all events of a user for a given day that are not passed yet.
        Returns:
            str: Formatted message.
        """
        user_language = DatabaseController.load_selected_language(user_id)
        message = "*{}*\n\n".format(receive_translation("event_reminder", user_language))

        message += "*{}:* {}\n".format(receive_translation("event", user_language), event["title"])
        message += "*{}:* {}\n".format(receive_translation("event_content", user_language), event["content"])
        message += "*{}:* {}\n".format(receive_translation("event_start", user_language), event["event_time"])
        message += "\n"

        return message

    @staticmethod
    def _refresh_start_pings(userdata, day):
        """Refreshes the "start ping done" booleans inside the user data for regularly events on the given day.
        Args:
            userdata (dict): Contains all users and their events.
            day (int): Day which should be refreshed.
        """
        day = "{}".format(day)
        for user in userdata:
            logger.info(userdata)
            for event_data in userdata[user][day]:
                event_data["start_ping_done"] = False

            DatabaseController.save_all_events_for_user(user, userdata[user])
