"""
logger.py
Handles logging of user activity and login attempts to a usage statistics CSV file.
"""

import csv
import os
from datetime import datetime

LOG_FILE = "./output/usage_statistics.csv"
FIELDNAMES = ["timestamp", "username", "role", "action", "status"]


def _ensure_log_file():
    """Create the log file with headers if it does not exist."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_event(username, role, action, status="success"):
    """
    Append a usage event to the log file.

    Parameters:
        username (str): the user's login name
        role (str): the user's role (or 'unknown' for failed logins)
        action (str): description of the action performed
        status (str): 'success' or 'failed'
    """
    _ensure_log_file()
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "role": role,
        "action": action,
        "status": status,
    }
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)
