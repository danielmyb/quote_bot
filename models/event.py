#!/usr/bin/env python

"""Model for event."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
        keyboard = [[InlineKeyboardButton("{}".format(EventType.REGULARLY.name),
                                          callback_data="{}".format(EventType.REGULARLY))],
                    [InlineKeyboardButton("{}".format(EventType.SINGLE.name),
                                          callback_data="{}".format(EventType.SINGLE))]]
        return InlineKeyboardMarkup(keyboard)


class EventType(Enum):
    """Enum for event types."""
    REGULARLY = 0
    SINGLE = 1
