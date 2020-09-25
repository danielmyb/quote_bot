#!/usr/bin/env python

"""Controller to adjust configurations of the bot."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from control.bot_control import BotControl
from control.database_controller import DatabaseController
from utils.localization_manager import receive_translation, receive_languages

CONFIG_LANGUAGE = "config_start_language"
CONFIG_DAILY_PING = "config_start_daily_ping"


class Configurator:
    """Manages the alteration of the configuration."""

    @staticmethod
    def start_configuration_dialog(update, context):
        """Starts the configuration dialog."""
        user_id = update.message.from_user.id
        user_language = DatabaseController.load_selected_language(user_id)
        Configurator.config_options_keyboard(user_language)

        update.message.reply_text(receive_translation("config_dialog_started", user_language),
                                  reply_markup=Configurator.config_options_keyboard(user_language))

    @staticmethod
    def handle_configuration_dialog(update, context):
        """Handles the configuration dialog."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']
        user_language = DatabaseController.load_selected_language(user_id)

        bot = BotControl.get_bot()

        if query.data == CONFIG_LANGUAGE:
            query.edit_message_text(text=receive_translation("config_language_which", user_language),
                                    reply_markup=Configurator.config_language_keyboard())
        elif query.data == CONFIG_DAILY_PING:
            query.edit_message_text(text=receive_translation("config_daily_ping_decide", user_language),
                                    reply_markup=Configurator.config_daily_ping_keyboard(user_language))

    @staticmethod
    def handle_configuration_change(update, context):
        """Handles changes inside the configuration."""
        query = update.callback_query
        query.answer()

        if "language" in query.data:
            Configurator.handle_configuration_language_change(update, context)
        elif "daily_ping" in query.data:
            Configurator.handle_configuration_daily_ping_change(update, context)

    @staticmethod
    def handle_configuration_language_change(update, context):
        """Handles the change of language."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']

        selected_language = query.data.split("_")[-1:][0]
        DatabaseController.save_user_language(user_id, selected_language)

        query.edit_message_text(receive_translation("config_language_changed", selected_language))

    @staticmethod
    def handle_configuration_daily_ping_change(update, context):
        """Handles the change of daily ping."""
        query = update.callback_query
        query.answer()

        user_id = query.from_user['id']
        user_language = DatabaseController.load_selected_language(user_id)

        selected_daily_ping = query.data.split("_")[-1:][0]

        if selected_daily_ping == "yes":
            config_value = True
            answer = receive_translation("config_daily_ping_enable", user_language)
        else:
            config_value = False
            answer = receive_translation("config_daily_ping_disable", user_language)
        DatabaseController.save_daily_ping(user_id, config_value)
        query.edit_message_text(answer)

    @staticmethod
    def config_options_keyboard(user_language):
        """Generates the keyboard for all available configuration options.
        Args:
            user_language (str): Language that is used to communicate with the user.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [
            [
                InlineKeyboardButton(receive_translation(CONFIG_LANGUAGE, user_language),
                                     callback_data=CONFIG_LANGUAGE),
                InlineKeyboardButton(receive_translation(CONFIG_DAILY_PING, user_language),
                                     callback_data=CONFIG_DAILY_PING)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def config_language_keyboard():
        """Generates the language configuration keyboard.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = []
        languages = receive_languages()

        for language in languages:
            keyboard.append([
                InlineKeyboardButton(language, callback_data="config_select_language_{}".format(languages[language]))
            ])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def config_daily_ping_keyboard(user_language):
        """Generates the daily ping configuration keyboard.
        Args:
            user_language (str): Language that is used to communicate with the user.
        Returns:
            InlineKeyboardMarkup: Generated keyboard.
        """
        keyboard = [
            [
                InlineKeyboardButton(receive_translation("yes", user_language),
                                     callback_data="config_select_daily_ping_yes"),
                InlineKeyboardButton(receive_translation("no", user_language),
                                     callback_data="config_select_daily_ping_no")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
