#!/usr/bin/env python

"""Model for event."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from models.day import DayEnum


class Event:
    """Represents a single event."""

    def __init__(self, name, content, event_type, ping_time):
        """Constructor.
        Args:
            name:
            content:
            event_type:
            ping_time:
        """
        self.name = name
        self.content = content
        self.event_type = event_type
        self.ping_time = ping_time

    @staticmethod
    def event_keyboard_type():
        """Generates the keyboard for the event types.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [[InlineKeyboardButton("{}".format(EventType.REGULARLY.name),
                                          callback_data="{}".format(EventType.REGULARLY.value))],
                    [InlineKeyboardButton("{}".format(EventType.SINGLE.name),
                                          callback_data="{}".format(EventType.SINGLE.value))]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_day():
        """Generates the keyboard for days.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        for day in DayEnum:
            keyboard.append([InlineKeyboardButton("{}".format(day.name), callback_data="d{}".format(day.value))])

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
                             InlineKeyboardButton("{}".format(i+1), callback_data="h{}".format(i+1)),
                             InlineKeyboardButton("{}".format(i+2), callback_data="h{}".format(i+2)),
                             InlineKeyboardButton("{}".format(i+3), callback_data="h{}".format(i+3))])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def event_keyboard_minutes():
        """Generates the keyboard for minutes.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        # Remove 00 and 05 from loop so that the leading 0 can be shown.
        keyboard = [[InlineKeyboardButton("00", callback_data="m0"), InlineKeyboardButton("05", callback_data="m5")]]
        for i in range(15, 60, 10):
            keyboard.append([InlineKeyboardButton("{}".format(i), callback_data="m{}".format(i)),
                             InlineKeyboardButton("{}".format(i+5), callback_data="m{}".format(i+5))])

        return InlineKeyboardMarkup(keyboard)


class EventType(Enum):
    """Enum for event types."""
    REGULARLY = 0
    SINGLE = 1
