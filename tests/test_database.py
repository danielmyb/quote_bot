#!/usr/bin/env python

"""Contains tests of the database."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import glob
import os
import unittest

from control.database_controller import DatabaseController
from models.event import EventType, Event
from utils.localization_manager import DEFAULT_LANGUAGE
from utils.path_utils import PROJECT_ROOT

TEST_CONFIG = os.path.join(PROJECT_ROOT, "tests", "test_files", "configuration.json")
TEST_USER_DATA = os.path.join(PROJECT_ROOT, "tests", "test_files", ".data", "user_data")


class TestDatabase(unittest.TestCase):
    """Tests functionality of the database controller."""

    dbc = None

    @classmethod
    def setUpClass(cls):
        """Set up test."""
        cls.dbc = DatabaseController(config_file=TEST_CONFIG, userdata_path=TEST_USER_DATA)

    def tearDown(self):
        """Tear down test."""
        user_data_files = glob.glob("{}/*.json".format(TEST_USER_DATA))
        for user_data_file in user_data_files:
            os.remove(user_data_file)

    def test_load_config(self):
        """Check that configuration values are loaded correctly."""
        self.assertEqual(self.dbc.configuration['configuration_values']['event_checker']['interval'], 300)
        self.assertEqual(self.dbc.configuration['version'], "0.test")

    def test_load_user_entry(self):
        """Check that a previously non-existing user files is created and correct."""
        user_id = 12345

        # First check creation - then loading existing one
        for _ in range(0, 2):
            test_entry = self.dbc.load_user_entry(user_id)
            self.assertTrue(test_entry)
            self.assertEqual(test_entry['user_id'], user_id)
            self.assertEqual(test_entry['language'], DEFAULT_LANGUAGE)
            self.assertTrue(test_entry['events'])
            for day in range(0, 7):
                self.assertEqual(test_entry['events']['{}'.format(day)], [])

    def test_load_selected_language(self):
        """Check that selected language of an user is returned correctly."""
        user_id = 12345
        self.dbc.load_user_entry(user_id)
        self.assertEqual(self.dbc.load_selected_language(user_id), DEFAULT_LANGUAGE)

    def test_save_day_event_data_entry(self):
        """Check that saving of an event to an day is working and that days that are outside of the
        day enum are rejected.
        """
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_day_event_data(user_id, 0, test_event)

        # Days that are not existing are raising a key error:
        with self.assertRaises(KeyError):
            self.dbc.save_day_event_data(user_id, 42, test_event)

    def test_read_event_of_user(self):
        """Check that reading an event of an user is successful if the event is existing and None is returned
        when it is not existing.
        """
        test_event = self.create_test_event()
        user_id = 12345

        for day in range(0, 7):
            self.dbc.save_day_event_data(user_id, day, test_event)

        for day in range(0, 7):
            self.assertIsNone(self.dbc.read_event_of_user(user_id, day, 'NotThere'))

        for day in range(0, 7):
            self.assertTrue(self.dbc.read_event_of_user(user_id, day, test_event.name))

    def test_delete_event_of_user(self):
        """Check that events of an user are deleted correctly and that the deletion of a not existing event
        is not raising any issues.
        """
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_day_event_data(user_id, 0, test_event)

        for day in range(0, 7):
            self.dbc.delete_event_of_user(user_id, day, 'NotThere')

        self.dbc.delete_event_of_user(user_id, 0, test_event.name)

        self.assertIsNone(self.dbc.read_event_of_user(user_id, 0, test_event.name))

    def test_read_event_data_of_user(self):
        """Check that saved events are returned when calling read event data of user and that days without
        events contain empty lists."""
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_day_event_data(user_id, 0, test_event)
        self.dbc.save_day_event_data(user_id, 3, test_event)
        self.dbc.save_day_event_data(user_id, 6, test_event)

        events = self.dbc.read_event_data_of_user(user_id)

        self.assertEqual(test_event.name, events['0'][0]['title'])
        self.assertEqual(events['1'], [])
        self.assertEqual(events['2'], [])
        self.assertEqual(test_event.name, events['3'][0]['title'])
        self.assertEqual(events['4'], [])
        self.assertEqual(events['5'], [])
        self.assertEqual(test_event.name, events['6'][0]['title'])

    def test_load_all_events_from_all_users(self):
        """Check that the loading of all events from all users is working successfully."""
        test_event = self.create_test_event()
        user_id = 12345
        user_id_string = "{}".format(user_id)

        # Ensure that no user files are existing
        user_data_files = glob.glob("{}/*.json".format(TEST_USER_DATA))
        for user_data_file in user_data_files:
            os.remove(user_data_file)

        self.assertEqual(self.dbc.load_all_events_from_all_users(), {})

        # Ensure a user entry is generated
        self.dbc.load_user_entry(user_id)

        event_data = self.dbc.load_all_events_from_all_users()
        self.assertIn(user_id_string, event_data.keys())
        self.assertEqual(len(event_data.keys()), 1)

        self.dbc.save_day_event_data(user_id, 0, test_event)

        event_data = self.dbc.load_all_events_from_all_users()
        self.assertEqual(len(event_data[user_id_string]['0']), 1)
        self.assertEqual(event_data[user_id_string]['0'][0]['title'], test_event.name)

        user_id_2 = 54321
        user_id_2_string = "{}".format(user_id_2)

        # Ensure a user entry is generated
        self.dbc.load_user_entry(user_id_2)

        event_data = self.dbc.load_all_events_from_all_users()
        self.assertIn(user_id_2_string, event_data.keys())
        self.assertEqual(len(event_data.keys()), 2)

    @staticmethod
    def create_test_event(name='TestEvent', content='TestContent', event_type=EventType.SINGLE, event_time="12:00",
                          ping_times=None, in_daily_ping=True, start_ping_done=False):
        """Creates an test event where every parameter of the event is adjustable."""
        test_event = Event(name, content, event_type, event_time, ping_times, in_daily_ping, start_ping_done)
        return test_event
