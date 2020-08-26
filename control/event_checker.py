#!/usr/bin/env python

"""Controller for event checking."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import time

from control.database_controller import DatabaseController


class EventChecker:

    def __init__(self, updater):
        """Constructor."""
        self.interval = None
        self.user = None

        self.updater = updater
        self.interval = DatabaseController.configuration['configuration_values']['event_checker']['interval']

        self.check_events()

    def check_events(self):
        """
        Returns:

        """
