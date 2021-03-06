#!/usr/bin/env python

"""Main for bot."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from control.bot_control import BotControl
from control.configurator import Configurator
from control.database_controller import DatabaseController
from control.event_checker import EventChecker
from control.event_handler import EventHandler
from models.user import User
from state_machines.user_event_alteration_machine import UserEventAlterationMachine
from state_machines.user_event_creation_machine import UserEventCreationMachine
from utils.localization_manager import receive_translation

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

db_controller = DatabaseController()


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    user = User.resolve_user(update)
    update.message.reply_text(
        receive_translation("greeting", user.language).format(USERNAME=user.telegram_user.first_name))


def help_command(update, context):
    """Send a message when the command /help is issued."""
    user = User.resolve_user(update)
    update.message.reply_markdown_v2(receive_translation("help", user.language))


def parse_input(update, context):
    """Echo the user message."""
    user = User.resolve_user(update)
    if UserEventCreationMachine.receive_state_of_user(user.user_id) == 1:
        if user.user_id in EventHandler.events_in_creation.keys() and not EventHandler.events_in_creation[user.user_id]:
            EventHandler.add_new_event_title(update, context)
        elif EventHandler.events_in_creation[user.user_id]["title"]:
            EventHandler.add_new_event_content(update, context)
    elif UserEventAlterationMachine.receive_state_of_user(user.user_id) > 10:
        EventHandler.event_alteration_handle_reply(update, context)
    else:
        update.message.reply_text(receive_translation("confused_echo", user.language))


def main():
    """Start the bot."""
    # Get the dispatcher to register handlers
    updater = BotControl.setup_bot()

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("config", Configurator.start_configuration_dialog))
    dp.add_handler(CommandHandler("new_event", EventHandler.add_new_event))
    dp.add_handler(CommandHandler("list_events", EventHandler.list_all_events_of_user))
    dp.add_handler(CallbackQueryHandler(Configurator.handle_configuration_dialog, pattern="config_start_[_a-zA-Z]*"))
    dp.add_handler(CallbackQueryHandler(Configurator.handle_configuration_change, pattern="config_select_[_a-zA-Z]*"))
    dp.add_handler(CallbackQueryHandler(EventHandler.event_alteration_start, pattern="event_alteration_[a-zA-Z]*"))
    dp.add_handler(CallbackQueryHandler(EventHandler.event_alteration_perform,
                                        pattern="event_(delete|change|silence)_[0-9a-zA-Z]+"))
    dp.add_handler(CallbackQueryHandler(EventHandler.add_new_event_query_handler))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, parse_input))

    # Start the Bot
    updater.start_polling()

    event_checker = EventChecker()
    event_checker.check_events()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
