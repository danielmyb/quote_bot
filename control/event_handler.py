#!/usr/bin/env python

"""Controller for handling events."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging

from telegram import ParseMode

from control.bot_control import BotControl
from control.database_controller import DatabaseController
from models.day import DayEnum
from models.event import Event, EventType
from models.user import User
from state_machines.user_event_creation_machine import UserEventCreationMachine
from utils.localization_manager import receive_translation


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
        update.message.reply_text(receive_translation("event_creation_start", user.language)
                                  .format(USERNAME=user.telegram_user.first_name))

    @staticmethod
    def add_new_event_title(update, context):
        """Handles the title of the new event."""
        user_id = update.message.from_user.id
        user_language = DatabaseController.load_selected_language(user_id)
        if UserEventCreationMachine.receive_state_of_user(user_id) != 1:
            return
        EventHandler.events_in_creation[user_id]["title"] = update.message.text
        update.message.reply_text(receive_translation("event_creation_content", user_language))

    @staticmethod
    def add_new_event_content(update, context):
        """Handles the addition of content of a new event."""
        user_id = update.message.from_user.id
        user_language = DatabaseController.load_selected_language(user_id)
        if UserEventCreationMachine.receive_state_of_user(user_id) != 1:
            return
        EventHandler.events_in_creation[user_id]["content"] = update.message.text
        update.message.reply_text(receive_translation("event_creation_type", user_language),
                                  reply_markup=Event.event_keyboard_type(user_language))

    @staticmethod
    def add_new_event_query_handler(update, context):
        """Creates a new event with help of the event creation state machine and keyboards."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']
        user_language = DatabaseController.load_selected_language(user_id)

        bot = BotControl.get_bot()

        # State: Requesting event type
        if UserEventCreationMachine.receive_state_of_user(user_id) == 1:
            EventHandler.events_in_creation[user_id]["type"] = query.data
            if query.data == "{}".format(EventType.SINGLE.value):
                message = receive_translation("event_creation_type_single", user_language)
            elif query.data == "{}".format(EventType.REGULARLY.value):
                message = receive_translation("event_creation_type_regularly", user_language)
            else:
                message = receive_translation("undefined_error_response", user_language)
            query.edit_message_text(text=message)
            UserEventCreationMachine.set_state_of_user(user_id, 2)

        # State: Requesting day of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 2:
            logging.info(query.data)
            if query.data[0] == 'd':
                EventHandler.events_in_creation[user_id]["day"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 3)
                query.edit_message_text(text=receive_translation("event_creation_hours", user_language))
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_day", user_language),
                                 reply_markup=Event.event_keyboard_day(user_language))

        # State: Requesting start hours of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 3:
            logging.info(query.data)
            if query.data[0] == 'h':
                EventHandler.events_in_creation[user_id]["hours"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 4)
                query.edit_message_text(text=receive_translation("event_creation_minutes", user_language))
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_hours", user_language),
                                 reply_markup=Event.event_keyboard_hours())

        # State: Requesting start minutes of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 4:
            logging.info(query.data)
            if query.data[0] == 'm':
                EventHandler.events_in_creation[user_id]["minutes"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, -1)
                query.edit_message_text(text=receive_translation("event_creation_finished", user_language))
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_minutes", user_language),
                                 reply_markup=Event.event_keyboard_minutes())

        # State: All data collected - creating event
        if UserEventCreationMachine.receive_state_of_user(user_id) == -1:
            event_in_creation = EventHandler.events_in_creation[user_id]
            event = Event(event_in_creation["title"], event_in_creation["content"],
                          EventType(int(event_in_creation["type"])),
                          "{}:{}".format(event_in_creation["hours"], event_in_creation["minutes"]))
            DatabaseController.save_day_event_data(user_id, event_in_creation["day"], event)
            UserEventCreationMachine.set_state_of_user(user_id, 0)
            EventHandler.events_in_creation.pop(user_id)

            message = receive_translation("event_creation_summary_header", user_language)
            message += event.pretty_print_formatting(user_id)
            bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

    @staticmethod
    def list_all_events_of_user(update, context):
        """Lists all events of the user."""
        user = User(update.message.from_user)

        message = "*{}:*\n\n".format(receive_translation("event_list_header", user.language))
        event_data = DatabaseController.read_event_data_of_user(user.telegram_user.id)

        for day in event_data:
            message += "*{}:*\n".format(DayEnum(int(day)).receive_day_translation(user.language))

            if not event_data[day]:
                message += "{}\n\n".format(receive_translation("no_events", user.language))
            for event in event_data[day]:
                event_object = Event(event["title"], event["content"], EventType(event["event_type"]),
                                     event["event_time"])
                message += event_object.pretty_print_formatting(user.telegram_user.id)
                message += "\n"

        update.message.reply_markdown_v2(message)
