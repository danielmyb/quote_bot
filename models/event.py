#!/usr/bin/env python

"""Model for event."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from control.database_controller import DatabaseController
from models.day import DayEnum
from utils.localization_manager import receive_translation

UNCHECKED_CHECKBOX = u'\U00002610'
CHECKED_CHECKBOX = u'\U00002611'


class Event:
    """Represents a single event."""

    def __init__(self, name, content, event_type, event_time, ping_times=None, in_daily_ping=True):
        """Constructor.
        Args:
            name (str): Name of the event.
            content (str): Content of the event.
            event_type (EventType): Type of the event, like singular.
            event_time (str): Time when the event is happening.
            ping_times (list of 'str', optional): Timeslots when the user should be pinged for that event.
            in_daily_ping (bool, optional): Determines whether this event is shown in the daily ping or not.
        """
        self.name = name
        self.content = content
        self.event_type = event_type
        self.event_time = event_time
        if ping_times:
            self.ping_times = ping_times
        else:
            self.ping_times = {}
        self.in_daily_ping = in_daily_ping

    @staticmethod
    def event_keyboard_type(user_language, callback_prefix=""):
        """Generates the keyboard for the event types.
        Args:
            user_language (str): Language that should be used.
            callback_prefix (str, optional): Prefix that should be used for the callback data parameter.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [[InlineKeyboardButton("{}".format(EventType.REGULARLY.receive_type_translation(user_language)),
                                          callback_data="{}{}".format(callback_prefix, EventType.REGULARLY.value))],
                    [InlineKeyboardButton("{}".format(EventType.SINGLE.receive_type_translation(user_language)),
                                          callback_data="{}{}".format(callback_prefix, EventType.SINGLE.value))]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_day(user_language):
        """Generates the keyboard for days.
        Args:
            user_language (str): Language that should be used.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        for day in DayEnum:
            keyboard.append([InlineKeyboardButton("{}".format(day.receive_day_translation(user_language)),
                                                  callback_data="d{}".format(day.value))])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_hours(callback_prefix=""):
        """Generates the keyboard for hours.
        Args:
            callback_prefix (str): Prefix that is used to generate the callback data string.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        for i in range(0, 24, 4):
            keyboard.append([InlineKeyboardButton("{}".format(i), callback_data="{}h{}".format(callback_prefix, i)),
                             InlineKeyboardButton("{}".format(i + 1),
                                                  callback_data="{}h{}".format(callback_prefix, i + 1)),
                             InlineKeyboardButton("{}".format(i + 2),
                                                  callback_data="{}h{}".format(callback_prefix, i + 2)),
                             InlineKeyboardButton("{}".format(i + 3),
                                                  callback_data="{}h{}".format(callback_prefix, i + 3))])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_minutes(callback_prefix=""):
        """Generates the keyboard for minutes.
        Args:
            callback_prefix (str): Prefix that is used to generate the callback data string.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        # Remove 00 and 05 from loop so that the leading 0 can be shown.
        keyboard = [[InlineKeyboardButton("00", callback_data="{}m00".format(callback_prefix)),
                     InlineKeyboardButton("05", callback_data="{}m05".format(callback_prefix))]]
        for i in range(10, 60, 10):
            keyboard.append([InlineKeyboardButton("{}".format(i), callback_data="{}m{}".format(callback_prefix, i)),
                             InlineKeyboardButton("{}".format(i + 5),
                                                  callback_data="{}m{}".format(callback_prefix, i + 5))])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_alteration(user_language):
        """Generates the keyboard for event alteration.
        Args:
            user_language (str): Language that should be used.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [
            [
                InlineKeyboardButton(receive_translation("event_alteration_change", user_language),
                                     callback_data="event_alteration_change"),
                InlineKeyboardButton(receive_translation("event_alteration_delete", user_language),
                                     callback_data="event_alteration_delete")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_alteration_action(events, user_language, mode):
        """Generates the event alteration keyboard for the given mode.
        Args:
            events (dict): Contains all events of a user.
            user_language (str): Language that should be used.
            mode (str): Contains the alteration mode (delete or change)
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        for day in events:
            keyboard_day = []
            for event in events[day]:
                title = event["title"]
                event_description = "{} ({}: {})".format(
                    title, DayEnum(int(day)).receive_day_translation(user_language), event["event_time"])
                keyboard_day.append(
                    InlineKeyboardButton(event_description, callback_data="event_{}_{}_{}".format(mode, day, title))
                )
            if keyboard_day:
                keyboard.append(keyboard_day)

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_alteration_change_start(user_language, callback_prefix):
        """Generates the event alternation change keyboard.
        Args:
            user_language (str): Language that should be used.
            callback_prefix (str): Prefix that is used to generate the callback data string.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [
            [InlineKeyboardButton(receive_translation("event_name", user_language),
                                  callback_data="{}_name".format(callback_prefix))],
            [InlineKeyboardButton(receive_translation("event_content", user_language),
                                  callback_data="{}_content".format(callback_prefix))],
            [InlineKeyboardButton(receive_translation("event_type", user_language),
                                  callback_data="{}_type".format(callback_prefix))],
            [InlineKeyboardButton(receive_translation("event_start", user_language),
                                  callback_data="{}_start".format(callback_prefix))],
            [InlineKeyboardButton(receive_translation("event_pingtime", user_language),
                                  callback_data="{}_pingtimes".format(callback_prefix))],
            [InlineKeyboardButton(receive_translation("done", user_language),
                                  callback_data="{}_done".format(callback_prefix))]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_ping_times(user_language, callback_prefix, states=None):
        """Generates the event ping times keyboard.
        Args:
            user_language (str): Language that should be used.
            callback_prefix (str): Prefix that is used to generate the callback data string.
            states (dict, optional): States of the ping times.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        if not states:
            states = {"00:30": False, "01:00": False, "02:00": False, "04:00": False, "06:00": False, "12:00": False,
                      "24:00": False}
        keyboard = []
        for state in states:
            checkbox = UNCHECKED_CHECKBOX
            if states[state]:
                checkbox = CHECKED_CHECKBOX
            keyboard.append([InlineKeyboardButton(text="{} {}".format(checkbox, state),
                                                  callback_data="{}_ping_times_{}".format(callback_prefix, state))])

        keyboard.append([InlineKeyboardButton(text=receive_translation("done", user_language),
                                              callback_data="{}_ping_times_done".format(callback_prefix))])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_confirmation(user_language, callback_prefix):
        """Generates the event alteration delete confirmation keyboard.
        Args:
            user_language (str): Language that should be used.
            callback_prefix (str): Prefix that is used to generate the callback data string.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [
            [
                InlineKeyboardButton(receive_translation("yes", user_language),
                                     callback_data="{}_yes".format(callback_prefix)),
                InlineKeyboardButton(receive_translation("no", user_language),
                                     callback_data="{}_no".format(callback_prefix))
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def pretty_print_formatting(self, user_id):
        """Collects all data about an event and returns a pretty printed version.
        Args:
            user_id (int): ID of the user - needed for localization.
        Returns:
            str: Pretty formatted event information.
        """
        user_language = DatabaseController.load_selected_language(user_id)
        message = "*{}:* {}\n".format(receive_translation("event_name", user_language), self.name)
        message += "*{}:* {}\n".format(receive_translation("event_content", user_language), self.content)
        message += "*{}:* {}\n".format(receive_translation("event_type", user_language),
                                       self.event_type.receive_type_translation(user_language))
        message += "*{}:* {}\n".format(receive_translation("event_start", user_language), self.event_time)

        ping_times_enabled = ""
        for ping_time in self.ping_times:
            if self.ping_times[ping_time]:
                ping_times_enabled += "{}\n".format(ping_time)
        if ping_times_enabled:
            message += "*{}:*\n{}".format(receive_translation("event_pingtime", user_language), ping_times_enabled)
        return message


class EventType(Enum):
    """Enum for event types."""
    REGULARLY = 0
    SINGLE = 1

    def receive_type_translation(self, user_language):
        """Receive the translation of the selected EventType.
        Args:
            user_language (str): Language that should be used.
        Returns:
            str: Translation for the event type.
        """
        return receive_translation("event_type_{}".format(self.name.lower()), user_language)
