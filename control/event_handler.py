#!/usr/bin/env python

"""Controller for handling events."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from models.event import Event
from models.user import User


class EventHandler:
    """Handler for events."""

    def __init__(self):
        """Constructor."""
        self.user = None

    @staticmethod
    def add_new_event(update, context):
        """
        Args:
            update:
            context:

        Returns:

        """
        user = User(update.message.from_user)
        update.message.reply_text('Okay - dann legen wir mal was neues für dich an, {}!'
                                  .format(user.telegram_user.first_name))
        update.message.reply_text('Was darfs denn sein?', reply_markup=Event.event_keyboard_type())

    @staticmethod
    def add_new_event_query_handler(update, context):
        """
        Args:
            update:
            context:

        Returns:

        """
        query = update.callback_query
        query.answer()

        query.edit_message_text(text='Ja nice! {}'.format(query.data))
