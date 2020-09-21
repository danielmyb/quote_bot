#!/usr/bin/env python

"""Controller for handling events."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging

from control.bot_control import BotControl
from control.database_controller import DatabaseController
from models.event import Event, EventType
from models.user import User
from state_machines.user_event_creation_machine import UserEventCreationMachine


class EventHandler:
    """Handler for events."""

    events_in_creation = {}

    def __init__(self):
        """Constructor."""
        self.user = None

    @staticmethod
    def add_new_event(update, context):
        """Reply to the /new_event command. Created the event in creation entry for the requesting user and starts the
        event creation cycle.
        """
        user = User(update.message.from_user)
        UserEventCreationMachine.set_state_of_user(user.telegram_user.id, 1)
        EventHandler.events_in_creation[user.telegram_user.id] = {}
        update.message.reply_text('Okay - dann legen wir mal was neues für dich an, {}! Wie soll das Event den heißen?'
                                  .format(user.telegram_user.first_name))

    @staticmethod
    def add_new_event_title(update, context):
        """Handles the title of the new event."""
        if UserEventCreationMachine.receive_state_of_user(update.message.from_user.id) != 1:
            return
        EventHandler.events_in_creation[update.message.from_user.id]["title"] = update.message.text
        update.message.reply_text('Nun kannst du noch beschreiben was der Inhalt des Events ist')

    @staticmethod
    def add_new_event_content(update, context):
        """"""
        if UserEventCreationMachine.receive_state_of_user(update.message.from_user.id) != 1:
            return
        EventHandler.events_in_creation[update.message.from_user.id]["content"] = update.message.text
        update.message.reply_text('Was darfs denn sein?', reply_markup=Event.event_keyboard_type())

    @staticmethod
    def add_new_event_query_handler(update, context):
        """Creates a new event with help of the event creation state machine and keyboards."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']

        bot = BotControl.get_bot()

        # State: Requesting event type
        if UserEventCreationMachine.receive_state_of_user(user_id) == 1:
            EventHandler.events_in_creation[user_id]["type"] = query.data
            if query.data == "{}".format(EventType.SINGLE.value):
                message = "Okay, ein neues einmaliges Event!"
            elif query.data == "{}".format(EventType.REGULARLY.value):
                message = "Okay, ein neues regelmäßiges Event!"
            else:
                message = "Irgendwas ist schief gegangen..."
            query.edit_message_text(text=message)
            UserEventCreationMachine.set_state_of_user(user_id, 2)

        # State: Requesting day of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 2:
            logging.info(query.data)
            if query.data[0] == 'd':
                EventHandler.events_in_creation[user_id]["day"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 3)
                query.edit_message_text(text='Gut, jetzt die Stunden')
            else:
                bot.send_message(user_id, text='An welchem Tag findet der Spaß denn statt?',
                                 reply_markup=Event.event_keyboard_day())

        # State: Requesting start hours of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 3:
            logging.info(query.data)
            if query.data[0] == 'h':
                EventHandler.events_in_creation[user_id]["hours"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 4)
                query.edit_message_text(text='Weiter zu den Minuten.')
            else:
                bot.send_message(user_id, text='Okay - nun zur Uhrzeit. Erstmal die Stunden!',
                                 reply_markup=Event.event_keyboard_hours())

        # State: Requesting start minutes of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 4:
            logging.info(query.data)
            if query.data[0] == 'm':
                EventHandler.events_in_creation[user_id]["minutes"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, -1)
                query.edit_message_text(text='Vielen dank - dann bastel ich das mal zusammen.')
            else:
                bot.send_message(user_id, text='Und nun die Minuten!', reply_markup=Event.event_keyboard_minutes())

        # State: All data collected - creating event
        if UserEventCreationMachine.receive_state_of_user(user_id) == -1:
            event_in_creation = EventHandler.events_in_creation[user_id]
            event = Event(event_in_creation["title"], event_in_creation["content"], event_in_creation["type"],
                          "{}:{}".format(event_in_creation["hours"], event_in_creation["minutes"]))
            DatabaseController.save_day_event_data(user_id, event_in_creation["day"], event)
            UserEventCreationMachine.set_state_of_user(user_id, 0)
            EventHandler.events_in_creation.pop(user_id)
