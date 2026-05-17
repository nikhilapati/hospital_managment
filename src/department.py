"""
department.py
Defines the Department class representing a hospital department.
"""


class Department:
    """Represents a hospital department that contains providers and encounters."""

    def __init__(self, dept_id, name, location):
        self.department_id = dept_id
        self.name = name
        self.location = location
        self.visit_list = []

    def add_encounter(self, enc):
        """Attach an Encounter to this department."""
        self.visit_list.append(enc)

    def count_encounters(self):
        """Return the number of encounters in this department."""
        return len(self.visit_list)

    def total_revenue(self):
        """Sum all procedure costs across all encounters in this department."""
        revenue = 0.0
        for visit in self.visit_list:
            for proc in visit.procedures:
                revenue += proc.cost
        return revenue

    def __repr__(self):
        return f"Department({self.department_id}, {self.name}, {self.location})"
