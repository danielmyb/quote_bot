#!/usr/bin/env python

"""State machine for event creation of a user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------


class UserEventCreationMachine:

    state_dict = {}

    @staticmethod
    def receive_state_of_user(user):
        """
        Args:
            user:

        Returns:

        """
        if not UserEventCreationMachine.state_dict or not UserEventCreationMachine.state_dict[user]:
            UserEventCreationMachine.state_dict[user] = 0
        return UserEventCreationMachine.state_dict[user]

    @staticmethod
    def set_state_of_user(user, state):
        """
        Args:
            user:
            state:

        Returns:

        """
        # TODO: Add check for valid state
        UserEventCreationMachine.state_dict[user] = state
