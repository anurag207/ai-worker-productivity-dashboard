"""
Application configuration settings.
"""
import os
from pathlib import Path

# Database settings
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/productivity.db")

# API settings
API_PREFIX = "/api/v1"

# Event processing settings
# Assume each event represents activity for this duration (in minutes)
# This is used when calculating time-based metrics from discrete events
EVENT_DURATION_MINUTES = 5

# Duplicate detection window (in seconds)
# Events with same worker_id, workstation_id, event_type within this window are considered duplicates
DUPLICATE_DETECTION_WINDOW_SECONDS = 10

# Shift duration for per-shift calculations (in hours)
SHIFT_DURATION_HOURS = 8




