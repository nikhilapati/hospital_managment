"""
data_loader.py
Functions to load all CSV data files and build the in-memory object graph.
"""

import csv
import os

from patient import Patient
from provider import Provider
from department import Department
from encounter import Encounter
from procedure import Procedure
from note import Note


def parse_csv(path):
    """Read a CSV file and return list of row dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_patients(rows):
    """Build Patient objects from CSV rows."""
    patients = {}
    for r in rows:
        smoking_raw = r.get("smoking", r.get("Smoking", "false")).strip().lower()
        a1c_raw = r.get("a1c", "").strip()
        obj = Patient(
            r["patient_id"].strip(),
            int(r["age"]),
            r["gender"].strip(),
            float(r["bmi"]),
            float(a1c_raw) if a1c_raw else None,
            int(r["bp_sys"]),
            int(r["bp_dia"]),
            smoking_raw in ("true", "1", "yes"),
        )
        patients[obj.patient_id] = obj
    return patients


def build_providers(rows):
    """Build Provider objects from CSV rows."""
    providers = {}
    for r in rows:
        obj = Provider(
            r["provider_id"].strip(),
            r["name"].strip(),
            r["specialty"].strip(),
            r["department_id"].strip(),
        )
        providers[obj.provider_id] = obj
    return providers


def build_departments(rows):
    """Build Department objects from CSV rows."""
    departments = {}
    for r in rows:
        obj = Department(
            r["department_id"].strip(),
            r["name"].strip(),
            r["location"].strip(),
        )
        departments[obj.department_id] = obj
    return departments


def build_encounters(rows, patients, providers, departments):
    """Build Encounter objects and link them to patients, providers, departments."""
    encounters = {}
    for r in rows:
        obj = Encounter(
            r["encounter_id"].strip(),
            r["patient_id"].strip(),
            r["provider_id"].strip(),
            r["department_id"].strip(),
            r["encounter_date"].strip(),
            r["encounter_type"].strip(),
        )
        encounters[obj.encounter_id] = obj

        if obj.patient_id in patients:
            patients[obj.patient_id].add_encounter(obj)
        if obj.provider_id in providers:
            providers[obj.provider_id].add_encounter(obj)
        if obj.department_id in departments:
            departments[obj.department_id].add_encounter(obj)

    return encounters


def build_procedures(rows, encounters):
    """Build Procedure objects and link them to encounters."""
    procedures = {}
    for r in rows:
        obj = Procedure(
            r["procedure_id"].strip(),
            r["encounter_id"].strip(),
            r["patient_id"].strip(),
            r["procedure_code"].strip(),
            r["procedure_name"].strip(),
            float(r["cost"]),
        )
        procedures[obj.procedure_id] = obj
        if obj.encounter_id in encounters:
            encounters[obj.encounter_id].add_procedure(obj)
    return procedures


def build_notes(rows):
    """Build Note objects from CSV rows."""
    notes = []
    for r in rows:
        obj = Note(
            r["note_id"].strip(),
            r["patient_id"].strip(),
            r["encounter_id"].strip(),
            r["note_date"].strip(),
            r["note_type"].strip(),
            r["note_text"].strip(),
        )
        notes.append(obj)
    return notes


def load_all(data_dir="./Data/"):
    """Load all data files and return the full object graph."""
    patients    = build_patients(parse_csv(os.path.join(data_dir, "patients.csv")))
    providers   = build_providers(parse_csv(os.path.join(data_dir, "providers.csv")))
    departments = build_departments(parse_csv(os.path.join(data_dir, "departments.csv")))
    encounters  = build_encounters(
        parse_csv(os.path.join(data_dir, "encounters.csv")),
        patients, providers, departments,
    )
    procedures  = build_procedures(
        parse_csv(os.path.join(data_dir, "procedures.csv")),
        encounters,
    )
    notes = build_notes(parse_csv(os.path.join(data_dir, "notes.csv")))
    return patients, providers, departments, encounters, procedures, notes
