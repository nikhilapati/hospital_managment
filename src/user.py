"""
user.py
Defines the User class and credential-checking logic.
"""

import csv


VALID_ROLES = {"clinician", "nurse", "admin", "management"}


class User:
    """Represents an authenticated system user with a specific role."""

    def __init__(self, username, role):
        self.username = username
        self.role = role

    def can_access_phi(self):
        """Return True if this role is allowed to view patient PHI."""
        return self.role in ("clinician", "nurse")

    def get_allowed_actions(self):
        """Return the list of action button labels this role may see."""
        if self.role in ("clinician", "nurse"):
            return [
                "Retrieve Patient",
                "Add Patient",
                "Remove Patient",
                "Count Visits",
                "View Note",
                "Exit",
            ]
        elif self.role == "admin":
            return [
                "Count Visits",
                "Monitor Workload",
                "Exit",
            ]
        elif self.role == "management":
            return [
                "Generate Key Statistics",
                "Monitor Revenue",
                "Exit",
            ]
        return ["Exit"]

    def __repr__(self):
        return f"User({self.username}, role={self.role})"


def load_credentials(credentials_path):
    """
    Load credentials from CSV file.

    Returns:
        dict: {username: {"password": str, "role": str}}
    """
    credentials = {}
    try:
        with open(credentials_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                credentials[row["username"].strip()] = {
                    "password": row["password"].strip(),
                    "role": row["role"].strip(),
                }
    except FileNotFoundError:
        print(f"Credentials file not found: {credentials_path}")
    return credentials


def validate_login(username, password, credentials):
    """
    Check username/password against the credentials dict.

    Returns:
        User object if valid, None if invalid.
    """
    username = username.strip()
    password = password.strip()
    if username in credentials:
        stored = credentials[username]
        if stored["password"] == password:
            return User(username, stored["role"])
    return None
