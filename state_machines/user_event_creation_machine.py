#!/usr/bin/env python

"""State machine for event creation of a user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum


class UserEventCreationMachine:

    state_dict = {}

    @staticmethod
    def receive_state_of_user(user_id):
        """Receives the state the user is currently in. If there was no state saved the state is set to 0.
        Args:
            user_id (int): ID of the user
        Returns:
            int: State the user is currently in.
        """
        if not UserEventCreationMachine.state_dict or user_id not in UserEventCreationMachine.state_dict.keys():
            UserEventCreationMachine.state_dict[user_id] = 0
        return UserEventCreationMachine.state_dict[user_id]

    @staticmethod
    def set_state_of_user(user_id, state):
        """Sets the state of the given user.
        Args:
            user_id (int): ID of the user.
            state (int): State the user should be in.
        """
        # TODO: Add check for valid state
        UserEventCreationMachine.state_dict[user_id] = state


class ValidStates(Enum):
    """Contains all valid states for the UserEventCreationMachine."""
    DONE = -1
    INITIAL = 0
    STARTED = 1
    DAY = 2
    HOURS = 3
    MINUTES = 4

    PING_TIMES_START = 10
    PING_TIMES_SELECT = 11
