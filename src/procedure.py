"""
procedure.py
Defines the Procedure class representing a clinical procedure performed during an encounter.
"""


class Procedure:
    """Represents a single clinical procedure with associated cost."""

    def __init__(self, proc_id, enc_id, patient_id, code, name, cost):
        self.procedure_id = proc_id
        self.encounter_id = enc_id
        self.patient_id = patient_id
        self.procedure_code = code
        self.procedure_name = name
        self.cost = cost

    def __repr__(self):
        return f"Procedure({self.procedure_id}, {self.procedure_name}, ${self.cost:.2f})"
