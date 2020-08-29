#!/usr/bin/env python

"""Controller for handling events."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
from control.bot_control import BotControl
from models.event import Event, EventType
from models.user import User
from state_machines.user_event_creation_machine import UserEventCreationMachine


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

        user_id = query.from_user['id']

        if UserEventCreationMachine.receive_state_of_user(user_id) == 0:
            if query.data == "{}".format(EventType.SINGLE.value):
                message = "Okay, ein neues einmaliges Event!"
            elif query.data == "{}".format(EventType.REGULARLY.value):
                message = "Okay, ein neues regelmäßiges Event!"
            else:
                message = "Irgendwas ist schief gegangen..."
            query.edit_message_text(text=message)
            UserEventCreationMachine.set_state_of_user(user_id, 1)
        else:
            query.edit_message_text(text='NYI')

        bot = BotControl.get_bot()
        bot.send_message(user_id, text='Hier passier bald mehr!')
