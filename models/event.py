#!/usr/bin/env python

"""Model for event."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum


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


class EventType(Enum):
    """Enum for event types."""
    REGULARLY = 0
    SINGLE = 1
