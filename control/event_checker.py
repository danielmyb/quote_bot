#!/usr/bin/env python

"""Controller for event checking."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from control.database_controller import DatabaseController


class EventChecker:

    def __init__(self):
        """Constructor."""
        self.interval = None
        self.user = None

        self.interval = DatabaseController.configuration["event_checker"]["interval"]

    def check_events(self):
        """
        Returns:

        """