"""
file_writer.py
Functions to persist patient data changes back to the patients.csv file.
"""

import csv
import os

PATIENT_FIELDNAMES = [
    "patient_id", "age", "gender", "bmi", "a1c", "bp_sys", "bp_dia", "smoking"
]


def save_patients(patients, data_dir="./Data/"):
    """
    Overwrite the patients.csv file with the current in-memory patients dict.

    Parameters:
        patients (dict): {patient_id: Patient}
        data_dir (str): directory where patients.csv lives
    """
    path = os.path.join(data_dir, "patients.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PATIENT_FIELDNAMES)
        writer.writeheader()
        for p in patients.values():
            writer.writerow(p.to_dict())
