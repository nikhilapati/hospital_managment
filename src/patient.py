"""
patient.py
Defines the Patient class with attributes and methods for managing patient data.
"""


class Patient:
    """Represents a single patient and their associated encounters."""

    def __init__(self, pid, age, gender, bmi, a1c, bp_sys, bp_dia, smoking):
        self.patient_id = pid
        self.age = age
        self.gender = gender
        self.bmi = bmi
        self.a1c = a1c
        self.bp_sys = bp_sys
        self.bp_dia = bp_dia
        self.smoking = smoking
        self.visit_list = []

    def add_encounter(self, enc):
        """Attach an Encounter object to this patient."""
        self.visit_list.append(enc)

    def remove_encounters(self):
        """Clear all encounters for this patient."""
        self.visit_list = []

    def count_encounters(self):
        """Return total number of encounters."""
        return len(self.visit_list)

    def most_recent_encounter(self):
        """Return the most recent Encounter object, or None."""
        if not self.visit_list:
            return None
        return max(self.visit_list, key=lambda e: e.encounter_date)

    def meets_criteria(self, criteria):
        """Check if patient meets a dict of field: condition criteria."""
        for field, condition in criteria.items():
            val = getattr(self, field, None)
            if val is None:
                return False
            if isinstance(condition, tuple):
                lo, hi = condition
                if lo is not None and val < lo:
                    return False
                if hi is not None and val > hi:
                    return False
            elif val != condition:
                return False
        return True

    def to_dict(self):
        """Return patient attributes as a flat dict for CSV writing."""
        return {
            "patient_id": self.patient_id,
            "age": self.age,
            "gender": self.gender,
            "bmi": self.bmi,
            "a1c": self.a1c if self.a1c is not None else "",
            "bp_sys": self.bp_sys,
            "bp_dia": self.bp_dia,
            "smoking": self.smoking,
        }

    def __repr__(self):
        return f"Patient({self.patient_id}, age={self.age}, gender={self.gender})"
