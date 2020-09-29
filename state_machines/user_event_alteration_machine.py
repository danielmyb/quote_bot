#!/usr/bin/env python

"""State machine for event creation of a user."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from enum import Enum


class UserEventAlterationMachine:

    state_dict = {}

    @staticmethod
    def receive_state_of_user(user_id):
        """Receives the state the user is currently in. If there was no state saved the state is set to 0.
        Args:
            user_id (int): ID of the user
        Returns:
            int: State the user is currently in.
        """
        if not UserEventAlterationMachine.state_dict or not UserEventAlterationMachine.state_dict[user_id]:
            UserEventAlterationMachine.state_dict[user_id] = 0
        return UserEventAlterationMachine.state_dict[user_id]

    @staticmethod
    def set_state_of_user(user_id, state):
        """Sets the state of the given user.
        Args:
            user_id (int): ID of the user.
            state (int): State the user should be in.
        """
        # TODO: Add check for valid state
        UserEventAlterationMachine.state_dict[user_id] = state


class ValidStates(Enum):
    """Contains all valid states for the UserEventCreationMachine."""
    DONE = -1
    INITIAL = 0
    ALTER_NAME = 1
    ALTER_CONTENT = 2
    ALTER_TYPE = 3
    ALTER_START_TIME = 4
    AlTER_PING_TIMES = 5

    ALTER_NAME_REPLY = 11
    ALTER_CONTENT_REPLY = 12
    ALTER_TYPE_REPLY = 13

    ALTER_START_TIME_HOURS = 41
    ALTER_START_TIME_MINUTES = 42

    ALTER_PING_TIMES_SELECT = 51

    PARSE_CHOICE = 99

    DELETE_CONFIRMATION = 101
