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
from models.event import Event, EventType
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
        user_ids = DatabaseController.load_all_user_ids()
        today = datetime.today().weekday()
        self._ping_users(user_ids, today)

        time.sleep(self.interval)

        # Check if a new day has begun
        current_day = datetime.today().weekday()
        if today != current_day:
            # Use fresh userdata
            user_ids = DatabaseController.load_all_user_ids()
            self._ping_users(user_ids, current_day)

        # Refresh pings of all events of yesterday
        user_ids = DatabaseController.load_all_user_ids()
        self._refresh_start_pings(user_ids, (datetime.today() - timedelta(days=1)).weekday())

        self.check_events()

    def _ping_users(self, user_ids, day):
        """Pings all users inside userdata with the events of the given day
        Args:
            user_ids (list of 'str'): Contains all users.
            day (int): Represents the day which should be pinged for.
        """
        tomorrow = day + 1 if day < 6 else 0
        for user_id in user_ids:
            user_events = DatabaseController.load_user_events(user_id)
            events_of_today = [event for event in user_events if event.day.value == day]
            events_of_tomorrow = [event for event in user_events if event.day.value == tomorrow]
            self._check_event_ping(user_id, events_of_today)
            self._check_event_ping(user_id, events_of_tomorrow, today=False)

    def _check_event_ping(self, user_id, events, today=True):
        """Check which events are not already passed and pings the user.
        Args:
            user_id (int): ID of the user.
            events (list of 'Event'): Contains all events of the user for a single day.
            today (bool, optional): Indicates whether the events of today or tomorrow are checked.
                Checking today by default.
        """
        bot = BotControl.get_bot()

        ping_list = []
        logger.info("Checking %s | %s", user_id, events)
        for event in events:
            ping_needed, event_delete = self.check_ping_needed(user_id, event, today)
            if ping_needed:
                event.deleted = event_delete
                ping_list.append(event)

        # Only ping if there are events to notify about
        if ping_list:
            for event in ping_list:
                message = self.build_ping_message(user_id, event)
                if event.deleted:
                    bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)
                else:
                    language = DatabaseController.load_selected_language(user_id)
                    weekday = datetime.now().weekday() if today else (datetime.now() + timedelta(days=1)).weekday()
                    postfix = "_{}".format(event.uuid)
                    bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2,
                                     reply_markup=Event.event_keyboard_alteration(language, "event", postfix))

    @staticmethod
    def check_ping_needed(user_id, event, today=True):
        """Checks if an event needs to be pinged.
        Args:
            user_id (int): ID of the user.
            event (Event): Contains the event that should be checked.
            today (bool, optional): Indicates whether today or tomorrow is checked.
        Returns:
            bool: True if a ping has to be sent. False if not.
        """
        current_time = datetime.now()
        ping_times = event.ping_times

        event_month = current_time.month
        event_day = current_time.day
        if not today:
            event_date = current_time + timedelta(days=1)
            event_day = event_date.day
            event_month = event_date.month

        event_time = datetime(year=current_time.year, month=event_month, day=event_day,
                              hour=event.event_time_hours, minute=event.event_time_minutes)

        needs_ping = False

        for ping_time in ping_times:
            # If multiple ping times are already reached ping one time and disable all "used" times.
            if ping_times[ping_time]:
                delta = timedelta(hours=int(ping_time.split(':')[0]), minutes=int(ping_time.split(':')[1]))
                if event_time - delta < current_time:
                    event.ping_times[ping_time] = False
                    needs_ping = True

                    # Save ping times for regularly events
                    if event.event_type == EventType.REGULARLY:
                        event.ping_times_to_refresh[ping_time] = True

        event_deleted = False

        # Cleanup event if it is passed
        if event_time < current_time and not event.start_ping_done:
            needs_ping = True
            if event.event_type == EventType.SINGLE:
                DatabaseController.delete_event_of_user(user_id, event.uuid)
                event_deleted = True
            else:
                event.start_ping_done = True

        if needs_ping:
            # Save the changes on the event
            DatabaseController.save_event_data_user(user_id, event)

        return needs_ping, event_deleted

    @staticmethod
    def build_ping_message(user_id, event):
        """Generates the ping message for the user.
        Args:
            user_id (int): ID of the user - needed for localization.
            event (Event): Contains all events of a user for a given day that are not passed yet.
        Returns:
            str: Formatted message.
        """
        user_language = DatabaseController.load_selected_language(user_id)
        message = "*{}*\n\n".format(receive_translation("event_reminder", user_language))

        message += "*{}:* {}\n".format(receive_translation("event", user_language), event.name)
        message += "*{}:* {}\n".format(receive_translation("event_content", user_language), event.content)
        message += "*{}:* {}\n".format(receive_translation("event_start", user_language), event.event_time)
        message += "\n"

        return message

    @staticmethod
    def _refresh_start_pings(user_ids, day):
        """Refreshes the "start ping done" booleans inside the user data for regularly events on the given day.
        Args:
            user_ids (dict): Contains all users and their events.
            day (int): Day which should be refreshed.
        """
        for user_id in user_ids:
            events = [event for event in DatabaseController.load_user_events(user_id) if event.day == day]
            for event in events:
                event.start_ping_done = False

                # Restore ping times for regularly events
                for event_ping in event.ping_times_to_refresh:
                    event.ping_times[event_ping] = True
                event.ping_times_to_refresh = {}

                DatabaseController.save_event_data_user(user_id, event)
