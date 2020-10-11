#!/usr/bin/env python

"""Contains tests of the database."""

# ----------------------------------------------
# Copyright: Daniel Bebber, 2020
# Author: Daniel Bebber <daniel.bebber@gmx.de>
# ----------------------------------------------
import glob
import os
import unittest
import uuid

from control.database_controller import DatabaseController
from models.day import DayEnum
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

    def test_load_user_config(self):
        """Check that a previously non-existing user config file is created and correct."""
        user_id = 12345

        # First check creation - then loading existing one
        for _ in range(0, 2):
            test_entry = self.dbc.load_user_config(user_id)
            self.assertTrue(test_entry)
            self.assertEqual(test_entry['user_id'], user_id)
            self.assertEqual(test_entry['language'], DEFAULT_LANGUAGE)

    def test_load_user_events(self):
        """Check that a previously non-existing user events file is created and correct."""
        user_id = 12345

        # First check creation - then loading existing one
        test_entry = self.dbc.load_user_events(user_id)
        self.assertFalse(test_entry)
        test_event = self.create_test_event(event_uuid=uuid.uuid4().hex)
        self.dbc.save_event_data_user(user_id, test_event)
        events = self.dbc.load_user_events(user_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(test_event.uuid, events[0].uuid)
        self.assertEqual(test_event.name, events[0].name)
        self.assertEqual(test_event.day, events[0].day)
        self.assertEqual(test_event.content, events[0].content)
        self.assertEqual(test_event.event_type, events[0].event_type)
        self.assertEqual(test_event.event_time, events[0].event_time)
        self.assertEqual(test_event.ping_times, events[0].ping_times)

    def test_load_selected_language(self):
        """Check that selected language of an user is returned correctly."""
        user_id = 12345
        self.dbc.load_user_config(user_id)
        self.assertEqual(self.dbc.load_selected_language(user_id), DEFAULT_LANGUAGE)

    def test_save_day_event_data_entry(self):
        """Check that saving of an event to an day is working and that days that are outside of the
        day enum are rejected.
        """
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_event_data_user(user_id, test_event)

    def test_read_event_of_user(self):
        """Check that reading an event of an user is successful if the event is existing and None is returned
        when it is not existing.
        """
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_event_data_user(user_id, test_event)

        self.assertIsNone(self.dbc.read_event_of_user(user_id, 'NotThere'))

        self.assertTrue(self.dbc.read_event_of_user(user_id, test_event.uuid))

    def test_delete_event_of_user(self):
        """Check that events of an user are deleted correctly and that the deletion of a not existing event
        is not raising any issues.
        """
        test_event = self.create_test_event()
        user_id = 12345

        self.dbc.save_event_data_user(user_id, test_event)

        self.dbc.delete_event_of_user(user_id, 'NotThere')

        self.dbc.delete_event_of_user(user_id, test_event.uuid)

        self.assertIsNone(self.dbc.read_event_of_user(user_id, test_event.uuid))

    def test_read_event_data_of_user(self):
        """Check that saved events are returned when calling read event data of user and that days without
        events contain empty lists."""
        test_event_1 = self.create_test_event(event_uuid=uuid.uuid4().hex)
        test_event_2 = self.create_test_event(event_uuid=uuid.uuid4().hex)
        test_event_3 = self.create_test_event(event_uuid=uuid.uuid4().hex)
        user_id = 12345

        self.dbc.save_event_data_user(user_id, test_event_1)
        self.dbc.save_event_data_user(user_id, test_event_2)
        self.dbc.save_event_data_user(user_id, test_event_3)

        events = self.dbc.load_user_events(user_id)

        self.assertEqual(test_event_1.uuid, events[0].uuid)
        self.assertEqual(test_event_2.uuid, events[1].uuid)
        self.assertEqual(test_event_3.uuid, events[2].uuid)

    def test_load_all_user_ids(self):
        """Check that the loading of all events from all users is working successfully."""
        user_id = 12345
        user_id_string = str(user_id)

        # Ensure that no user files are existing
        user_data_files = glob.glob("{}/*.json".format(TEST_USER_DATA))
        for user_data_file in user_data_files:
            os.remove(user_data_file)

        self.assertEqual(self.dbc.load_all_user_ids(), [])

        # Ensure a user entry is generated
        self.dbc.load_user_config(user_id)

        user_id_2 = 54321
        user_id_2_string = "{}".format(user_id_2)

        # Ensure a user entry is generated
        self.dbc.load_user_config(user_id_2)

        user_ids = self.dbc.load_all_user_ids()
        self.assertIn(user_id_string, user_ids)
        self.assertIn(user_id_2_string, user_ids)
        self.assertEqual(len(user_ids), 2)

    @staticmethod
    def create_test_event(name='TestEvent', day=DayEnum(0), content='TestContent', event_type=EventType.SINGLE,
                          event_time="12:00", ping_times=None, in_daily_ping=True, start_ping_done=False,
                          event_uuid=None):
        """Creates an test event where every parameter of the event is adjustable."""
        test_event = Event(name, day, content, event_type, event_time, ping_times, in_daily_ping, start_ping_done)
        if event_uuid:
            test_event.uuid = event_uuid
        return test_event
