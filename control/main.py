#!/usr/bin/env python

"""Main for bot."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from control.bot_control import BotControl
from control.database_controller import DatabaseController
from control.event_checker import EventChecker
from control.event_handler import EventHandler
from models.user import User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

db_controller = DatabaseController()


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    user = User(update.message.from_user)
    update.message.reply_text('Hallo {}!'.format(user.telegram_user.first_name))
    update.message.reply_text('Folgendes hab ich von dir: {}'.format(user.user_data))


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown_v2('*YOU NEED SOME HELP?* \n'
                                     'Gibs dann irgendwann undso')


def echo(update, context):
    """Echo the user message."""
    user_id = User(update.message.from_user).telegram_user.id
    if user_id in EventHandler.events_in_creation.keys():
        EventHandler.add_new_event_title(update, context)
    else:
        update.message.reply_text("Ähm hi ...?")


def main():
    """Start the bot."""
    # Get the dispatcher to register handlers
    updater = BotControl.setup_bot()

    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("new_event", EventHandler.add_new_event))
    dp.add_handler(CallbackQueryHandler(EventHandler.add_new_event_query_handler))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    event_checker = EventChecker(updater)
    event_checker.check_events()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
