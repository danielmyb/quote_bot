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


class Event:
    """Represents a single event."""

    def __init__(self, name, content, event_type, event_time, ping_times=None):
        """Constructor.
        Args:
            name (str): Name of the event.
            content (str): Content of the event.
            event_type (EventType): Type of the event, like singular.
            event_time (str): Time when the event is happening.
            ping_times (list of 'str'): Timeslots when the user should be pinged for that event.
        """
        self.name = name
        self.content = content
        self.event_type = event_type
        self.event_time = event_time
        if ping_times:
            self.ping_times = ping_times
        else:
            self.ping_times = []

    @staticmethod
    def event_keyboard_type(user_language):
        """Generates the keyboard for the event types.
        Args:
            user_language (str): Language that should be used.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [[InlineKeyboardButton("{}".format(EventType.REGULARLY.receive_type_translation(user_language)),
                                          callback_data="{}".format(EventType.REGULARLY.value))],
                    [InlineKeyboardButton("{}".format(EventType.SINGLE.receive_type_translation(user_language)),
                                          callback_data="{}".format(EventType.SINGLE.value))]]
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
    def event_keyboard_hours():
        """Generates the keyboard for hours.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        for i in range(0, 24, 4):
            keyboard.append([InlineKeyboardButton("{}".format(i), callback_data="h{}".format(i)),
                             InlineKeyboardButton("{}".format(i + 1), callback_data="h{}".format(i + 1)),
                             InlineKeyboardButton("{}".format(i + 2), callback_data="h{}".format(i + 2)),
                             InlineKeyboardButton("{}".format(i + 3), callback_data="h{}".format(i + 3))])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_minutes():
        """Generates the keyboard for minutes.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        # Remove 00 and 05 from loop so that the leading 0 can be shown.
        keyboard = [[InlineKeyboardButton("00", callback_data="m00"), InlineKeyboardButton("05", callback_data="m05")]]
        for i in range(15, 60, 10):
            keyboard.append([InlineKeyboardButton("{}".format(i), callback_data="m{}".format(i)),
                             InlineKeyboardButton("{}".format(i + 5), callback_data="m{}".format(i + 5))])

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
            [InlineKeyboardButton(receive_translation("done", user_language),
                                  callback_data="{}_done".format(callback_prefix))]
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
        for ping_time in self.ping_times:
            message += "*{}:* {}\n".format(receive_translation("event_pingtime", user_language), ping_time)
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
