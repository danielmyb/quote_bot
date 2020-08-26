#!/usr/bin/env python

import os

"""Utils regarding paths."""

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, ".data")
USERDATA_PATH = os.path.join(DATA_PATH, "user_data")
