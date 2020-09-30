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
from utils.localization_manager import DEFAULT_LANGUAGE
from utils.path_utils import PROJECT_ROOT

TEST_CONFIG = os.path.join(PROJECT_ROOT, "tests", "test_files", "configuration.json")
TEST_USER_DATA = os.path.join(PROJECT_ROOT, "tests", "test_files", ".data", "user_data")


class TestDatabase(unittest.TestCase):
    """Tests functionality of the database controller."""

    dbc = None

    def setUp(self):
        """Set up test."""
        self.dbc = DatabaseController(config_file=TEST_CONFIG, userdata_path=TEST_USER_DATA)

    @classmethod
    def tearDownClass(cls):
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
