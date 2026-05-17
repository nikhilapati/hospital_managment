"""
provider.py
Defines the Provider class representing a clinical provider (doctor/nurse).
"""


class Provider:
    """Represents a healthcare provider with a specialty and department."""

    def __init__(self, pid, name, specialty, dept_id):
        self.provider_id = pid
        self.name = name
        self.specialty = specialty
        self.department_id = dept_id
        self.visit_list = []

    def add_encounter(self, enc):
        """Attach an Encounter to this provider."""
        self.visit_list.append(enc)

    def count_encounters(self):
        """Return the number of encounters handled."""
        return len(self.visit_list)

    def __repr__(self):
        return f"Provider({self.provider_id}, {self.name}, {self.specialty})"
