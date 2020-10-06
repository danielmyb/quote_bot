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
from state_machines.user_event_alteration_machine import UserEventAlterationMachine
from state_machines.user_event_creation_machine import UserEventCreationMachine
from utils.localization_manager import receive_translation
from utils.parsing_utils import replace_reserved_characters


class EventHandler:
    """Handler for events."""

    events_in_creation = {}
    events_in_alteration = {}

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
        title = replace_reserved_characters(update.message.text)
        EventHandler.events_in_creation[user_id]["title"] = title
        update.message.reply_text(receive_translation("event_creation_content", user_language))

    @staticmethod
    def add_new_event_content(update, context):
        """Handles the addition of content of a new event."""
        user_id = update.message.from_user.id
        user_language = DatabaseController.load_selected_language(user_id)
        if UserEventCreationMachine.receive_state_of_user(user_id) != 1:
            return
        content = replace_reserved_characters(update.message.text)
        EventHandler.events_in_creation[user_id]["content"] = content
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
                bot.delete_message(user_id, query.message.message_id)
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_day", user_language),
                                 reply_markup=Event.event_keyboard_day(user_language))

        # State: Requesting start hours of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 3:
            logging.info(query.data)
            if query.data[0] == 'h':
                EventHandler.events_in_creation[user_id]["hours"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 4)
                bot.delete_message(user_id, query.message.message_id)
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_hours", user_language),
                                 reply_markup=Event.event_keyboard_hours())

        # State: Requesting start minutes of the event
        if UserEventCreationMachine.receive_state_of_user(user_id) == 4:
            logging.info(query.data)
            if query.data[0] == 'm':
                EventHandler.events_in_creation[user_id]["minutes"] = query.data[1:]
                UserEventCreationMachine.set_state_of_user(user_id, 10)
                query.edit_message_text(text=receive_translation("event_creation_finished", user_language))
            else:
                bot.send_message(user_id, text=receive_translation("event_creation_minutes", user_language),
                                 reply_markup=Event.event_keyboard_minutes())

        # State: Start requesting ping times for the event - reset status.
        if UserEventCreationMachine.receive_state_of_user(user_id) == 10:
            ping_states = {"00:30": False, "01:00": False, "02:00": False, "04:00": False, "06:00": False,
                           "12:00": False, "24:00": False}
            EventHandler.events_in_creation[user_id]["ping_times"] = ping_states
            query.edit_message_text(text=receive_translation("event_creation_ping_times_header", user_language),
                                    reply_markup=Event.event_keyboard_ping_times(user_language, "event_creation",
                                                                                 ping_states))
            UserEventCreationMachine.set_state_of_user(user_id, 11)

        elif UserEventCreationMachine.receive_state_of_user(user_id) == 11:
            if "ping_times" in query.data:
                suffix = query.data.split('_')[-1]
                if suffix == "done":
                    UserEventCreationMachine.set_state_of_user(user_id, -1)
                    bot.delete_message(user_id, query.message.message_id)
                else:
                    EventHandler.events_in_creation[user_id]["ping_times"][suffix] = \
                        not EventHandler.events_in_creation[user_id]["ping_times"][suffix]
                    query.edit_message_text(
                        text=receive_translation("event_creation_ping_times_header", user_language),
                        reply_markup=Event.event_keyboard_ping_times(
                            user_language, "event_creation", EventHandler.events_in_creation[user_id]["ping_times"]))

        # State: All data collected - creating event
        if UserEventCreationMachine.receive_state_of_user(user_id) == -1:
            event_in_creation = EventHandler.events_in_creation[user_id]
            event = Event(event_in_creation["title"], event_in_creation["content"],
                          EventType(int(event_in_creation["type"])),
                          "{}:{}".format(event_in_creation["hours"], event_in_creation["minutes"]),
                          event_in_creation["ping_times"])
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
        has_content = False

        for day in event_data:
            if not event_data[day]:
                continue

            has_content = True
            message += "*{}:*\n".format(DayEnum(int(day)).receive_day_translation(user.language))

            for event in event_data[day]:
                event_object = Event(event["title"], event["content"], EventType(event["event_type"]),
                                     event["event_time"], event["ping_times"])
                message += event_object.pretty_print_formatting(user.telegram_user.id)
                message += "\n"

        if not has_content:
            message += "{}".format(receive_translation("no_events", user.language))
        bot = BotControl.get_bot()
        bot.send_message(user.telegram_user.id, text=message, parse_mode=ParseMode.MARKDOWN_V2,
                         reply_markup=Event.event_keyboard_alteration(user.language))

    @staticmethod
    def event_alteration_start(update, context):
        """Starts the event alteration process."""
        query = update.callback_query
        query.answer()

        altering_type = query.data.split("_")[-1:][0]

        user_id = query.from_user['id']
        events = DatabaseController.read_event_data_of_user(user_id)
        user_language = DatabaseController.load_selected_language(user_id)

        message = None
        if altering_type == 'change':
            message = receive_translation("event_alteration_change_header", user_language)
        elif altering_type == 'delete':
            message = receive_translation("event_alteration_delete_header", user_language)

        if UserEventAlterationMachine.receive_state_of_user(
                user_id) == 0 or UserEventAlterationMachine.receive_state_of_user(user_id) == -1:
            bot = BotControl.get_bot()
            bot.send_message(user_id, text=message, parse_mode=ParseMode.MARKDOWN_V2,
                             reply_markup=Event.event_keyboard_alteration_action(events, user_language,
                                                                                 mode=altering_type))

    @staticmethod
    def event_alteration_perform(update, context):
        """Performs the event alteration."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']
        user_language = DatabaseController.load_selected_language(user_id)
        logging.info("data: %s | state: %s", query.data, UserEventAlterationMachine.receive_state_of_user(user_id))

        event_day = query.data.split('_')[2]
        event_name = "".join(query.data.split('_')[3])
        event_suffix = "{}_{}".format(event_day, event_name)

        # Handle change of events
        if query.data.startswith("event_change"):

            # State: Choice - Check which button the user clicked after change was started.
            if UserEventAlterationMachine.receive_state_of_user(user_id) == 99:
                choice = query.data.split('_')[-1]
                if choice == "name":
                    UserEventAlterationMachine.set_state_of_user(user_id, 1)
                elif choice == "content":
                    UserEventAlterationMachine.set_state_of_user(user_id, 2)
                elif choice == "type":
                    UserEventAlterationMachine.set_state_of_user(user_id, 3)
                elif choice == "start":
                    UserEventAlterationMachine.set_state_of_user(user_id, 4)
                elif choice == "pingtimes":
                    UserEventAlterationMachine.set_state_of_user(user_id, 5)
                elif choice == "done":
                    UserEventAlterationMachine.set_state_of_user(user_id, -1)

            # State: Initial - return options to the user.
            if UserEventAlterationMachine.receive_state_of_user(user_id) == 0:
                EventHandler.events_in_alteration[user_id] = {}
                EventHandler.events_in_alteration[user_id]["old"] = \
                    DatabaseController.read_event_of_user(user_id, event_day, event_name)
                EventHandler.events_in_alteration[user_id]["new"] = \
                    EventHandler.events_in_alteration[user_id]["old"].copy()
                EventHandler.events_in_alteration[user_id]["old"]["day"] = event_day

                query.edit_message_text(text=receive_translation("event_alteration_change_decision", user_language),
                                        reply_markup=Event.event_keyboard_alteration_change_start(user_language,
                                                                                                  query.data))
                UserEventAlterationMachine.set_state_of_user(user_id, 99)

            # State: Name - Change name of event.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 1:
                query.edit_message_text(text=receive_translation("event_alteration_change_name", user_language))
                UserEventAlterationMachine.set_state_of_user(user_id, 11)

            # State: Content - Change content of event.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 2:
                query.edit_message_text(text=receive_translation("event_alteration_change_content", user_language))
                UserEventAlterationMachine.set_state_of_user(user_id, 12)

            # State: Type - Change type of event.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 3:
                query.edit_message_text(text=receive_translation("event_alteration_change_type", user_language),
                                        reply_markup=Event.event_keyboard_type(user_language, callback_prefix=
                                        "event_change_{}_type_".format(event_suffix)))
                UserEventAlterationMachine.set_state_of_user(user_id, 13)

            # State: Start time - Change start time of event.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 4:
                query.edit_message_text(text=receive_translation("event_alteration_change_hours", user_language),
                                        reply_markup=Event.event_keyboard_hours(
                                            callback_prefix="event_change_{}_hours_".format(event_suffix)))
                UserEventAlterationMachine.set_state_of_user(user_id, 41)

            # State: Ping times - Change ping times of event.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 5:
                query.edit_message_text(text=receive_translation("event_creation_ping_times_header", user_language),
                                        reply_markup=Event.event_keyboard_ping_times(
                                            user_language, callback_prefix="event_change_{}".format(event_suffix),
                                        states=EventHandler.events_in_alteration[user_id]["old"]["ping_times"]))
                UserEventAlterationMachine.set_state_of_user(user_id, 51)

            # State: Alter event type
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 13:
                EventHandler.events_in_alteration[user_id]['new']['event_type'] = int(query.data.split('_')[-1][0])
                UserEventAlterationMachine.set_state_of_user(user_id, 99)
                query.edit_message_text(text=receive_translation("event_alteration_change_decision", user_language),
                                        reply_markup=Event.event_keyboard_alteration_change_start(
                                            user_language, "event_change_{}".format(event_suffix)))

            # State: Alter event hours
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 41:
                EventHandler.events_in_alteration[user_id]['new']['event_time'] = \
                    "{}:{}".format(query.data.split('_')[-1][1:],
                                   EventHandler.events_in_alteration[user_id]['new']['event_time'].split(':')[1])
                UserEventAlterationMachine.set_state_of_user(user_id, 42)
                query.edit_message_text(text=receive_translation("event_alteration_change_minutes", user_language),
                                        reply_markup=Event.event_keyboard_minutes(
                                            callback_prefix="event_change_{}_minutes_".format(event_suffix)))

            # State: Alter event minutes
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 42:
                EventHandler.events_in_alteration[user_id]['new']['event_time'] = \
                    "{}:{}".format(EventHandler.events_in_alteration[user_id]['new']['event_time'].split(':')[0],
                                   query.data.split('_')[-1][1:])
                UserEventAlterationMachine.set_state_of_user(user_id, 99)
                query.edit_message_text(text=receive_translation("event_alteration_change_decision", user_language),
                                        reply_markup=Event.event_keyboard_alteration_change_start(
                                            user_language, "event_change_{}".format(event_suffix)))

            # State: Alter ping times - trigger chance on ping time
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 51:
                toggle_data = query.data.split('_')[-1]
                if toggle_data == 'done':
                    UserEventAlterationMachine.set_state_of_user(user_id, 99)
                    query.edit_message_text(text=receive_translation("event_alteration_change_decision", user_language),
                                            reply_markup=Event.event_keyboard_alteration_change_start(
                                                user_language, "event_change_{}".format(event_suffix)))
                else:
                    EventHandler.events_in_alteration[user_id]["new"]["ping_times"][toggle_data] = \
                        not EventHandler.events_in_alteration[user_id]["new"]["ping_times"][toggle_data]
                    query.edit_message_text(text=receive_translation("event_creation_ping_times_header", user_language),
                                            reply_markup=Event.event_keyboard_ping_times(
                                                user_language, callback_prefix="event_change_{}".format(event_suffix),
                                            states=EventHandler.events_in_alteration[user_id]["new"]["ping_times"]))

            # State: Done - Save changes and delete temporary object.
            elif UserEventAlterationMachine.receive_state_of_user(user_id) == -1:
                day = EventHandler.events_in_alteration[user_id]["old"]["day"]
                user_events = DatabaseController.read_event_data_of_user(user_id)
                events_for_day = []
                for event in user_events[day]:
                    if event["title"] == EventHandler.events_in_alteration[user_id]["old"]["title"]:
                        events_for_day.append(EventHandler.events_in_alteration[user_id]["new"])
                    else:
                        events_for_day.append(event)
                user_events[day] = events_for_day
                DatabaseController.save_all_events_for_user(user_id, user_events)
                query.edit_message_text(text=receive_translation("event_alteration_change_done", user_language))
                EventHandler.events_in_alteration.pop(user_id)
                UserEventAlterationMachine.set_state_of_user(user_id, 0)

        elif query.data.startswith("event_delete"):

            # State: Initial - request confirmation from user
            if UserEventAlterationMachine.receive_state_of_user(user_id) == 0:

                message = receive_translation("event_alteration_delete_request_confirmation", user_language)
                message += "\n"

                event_data = DatabaseController.read_event_of_user(user_id, event_day, event_name)
                event = Event(event_name, event_data['content'], EventType(event_data['event_type']),
                              event_data['event_time'])

                message += event.pretty_print_formatting(user_id)

                query.edit_message_text(text=message, reply_markup=Event.event_keyboard_confirmation(
                    user_language, "event_delete_{}".format(event_suffix)), parse_mode=ParseMode.MARKDOWN_V2)

                UserEventAlterationMachine.set_state_of_user(user_id, 101)

            elif UserEventAlterationMachine.receive_state_of_user(user_id) == 101:

                if query.data.split('_')[-1] == 'yes':
                    DatabaseController.delete_event_of_user(user_id, event_day, event_name)
                    query.edit_message_text(text=receive_translation("event_alteration_delete_confirmed",
                                                                     user_language))
                elif query.data.split('_')[-1] == 'no':
                    query.edit_message_text(text=receive_translation("event_alteration_delete_aborted", user_language))

                UserEventAlterationMachine.set_state_of_user(user_id, 0)

    @staticmethod
    def event_alteration_handle_reply(update, context):
        """Handles the replies of the event alteration."""
        user_id = update.message.from_user.id
        user_language = DatabaseController.load_selected_language(user_id)

        state = UserEventAlterationMachine.receive_state_of_user(user_id)

        bot = BotControl.get_bot()
        event_suffix = "{}_{}".format(EventHandler.events_in_alteration[user_id]['old']['day'],
                                      EventHandler.events_in_alteration[user_id]['old']['title'])

        # State: Alter name
        if state == 11:
            title = replace_reserved_characters(update.message.text)
            EventHandler.events_in_alteration[user_id]['new']['title'] = title
            UserEventAlterationMachine.set_state_of_user(user_id, 99)
            bot.send_message(user_id, text=receive_translation("event_alteration_change_decision", user_language),
                             reply_markup=Event.event_keyboard_alteration_change_start(user_language,
                                                                                       "event_change_{}".format(
                                                                                           event_suffix)))

        # State: Alter content
        elif state == 12:
            content = replace_reserved_characters(update.message.text)
            EventHandler.events_in_alteration[user_id]['new']['content'] = content
            UserEventAlterationMachine.set_state_of_user(user_id, 99)
            bot.send_message(user_id, text=receive_translation("event_alteration_change_decision", user_language),
                             reply_markup=Event.event_keyboard_alteration_change_start(user_language,
                                                                                       "event_change_{}".format(
                                                                                           event_suffix)))
