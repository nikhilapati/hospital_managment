"""
encounter.py
Defines the Encounter class representing a single patient visit.
"""


class Encounter:
    """Represents a clinical encounter (visit) between a patient and provider."""

    def __init__(self, enc_id, patient_id, provider_id, dept_id, date, enc_type):
        self.encounter_id = enc_id
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.department_id = dept_id
        self.encounter_date = date
        self.encounter_type = enc_type
        self.procedures = []

    def add_procedure(self, proc):
        """Attach a Procedure object to this encounter."""
        self.procedures.append(proc)

    def count_procedures(self):
        """Return the number of procedures in this encounter."""
        return len(self.procedures)

    def __repr__(self):
        return f"Encounter({self.encounter_id}, {self.patient_id}, {self.encounter_date})"
