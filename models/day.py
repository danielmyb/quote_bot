#!/usr/bin/env python

"""Model for days."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging
from enum import Enum

from utils.localization_manager import receive_translation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Day:

    def __init__(self):
        """Constructor."""
        self.user = None
        self.day = None
        self.events = []

    def add_event(self, event):
        """
        Args:
            event (Event):

        Returns:

        """
        logger.info("Add event called with %s for %s %s", event, self.user, self.day)
        return True


class DayEnum(Enum):
    """Enum for days of the week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def receive_day_translation(self, user_language):
        """Receive the translation of the selected day.
        Args:
            user_language (str): Language that should be used.
        Returns:
            str: Translation for the day.
        """
        return receive_translation("day_{}".format(self.name.lower()), user_language)
