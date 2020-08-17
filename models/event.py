#!/usr/bin/env python

"""Model for event."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------


class Event:

    def __init__(self):
        """Constructor."""
        self.name = None
        self.content = None
        self.type = None
        self.pingtime = None
