"""
note.py
Defines the Note class representing a clinical note for a patient encounter.
"""


class Note:
    """Represents a clinical note written during a patient encounter."""

    def __init__(self, note_id, patient_id, encounter_id, note_date, note_type, note_text):
        self.note_id = note_id
        self.patient_id = patient_id
        self.encounter_id = encounter_id
        self.note_date = note_date
        self.note_type = note_type
        self.note_text = note_text

    def __repr__(self):
        return f"Note({self.note_id}, {self.patient_id}, {self.note_date}, {self.note_type})"
