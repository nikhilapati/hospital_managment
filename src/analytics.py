"""
analytics.py
Functions for generating statistics, revenue reports, and provider workload.
"""

from collections import Counter


def count_encounters_per_patient(patients):
    """Return dict of {patient_id: encounter_count}."""
    return {p.patient_id: p.count_encounters() for p in patients}


def encounters_by_department(departments):
    """Return dict of {department_name: encounter_count}."""
    return {d.name: d.count_encounters() for d in departments}


def count_visits_on_date(encounters, date_str):
    """Return total number of encounters on a specific date (YYYY-MM-DD)."""
    return sum(1 for e in encounters.values() if e.encounter_date == date_str)


def count_visits_per_patient_on_date(patients, date_str):
    """Return dict of {patient_id: visit_count} for a given date."""
    result = {}
    for p in patients.values():
        count = sum(1 for e in p.visit_list if e.encounter_date == date_str)
        if count > 0:
            result[p.patient_id] = count
    return result


def count_visits_by_department_on_date(departments, date_str):
    """Return dict of {department_name: visit_count} for a given date."""
    result = {}
    for d in departments.values():
        count = sum(1 for e in d.visit_list if e.encounter_date == date_str)
        if count > 0:
            result[d.name] = count
    return result


def identify_eligible_patients(patients, criteria):
    """Return list of patient_ids meeting the given criteria dict."""
    return [p.patient_id for p in patients if p.meets_criteria(criteria)]


def top_providers_by_workload(providers):
    """Return list of (provider_id, name, encounter_count) sorted descending."""
    ranked = sorted(providers, key=lambda p: p.count_encounters(), reverse=True)
    return [(p.provider_id, p.name, p.count_encounters()) for p in ranked]


def department_revenue(departments):
    """Return dict of {department_name: total_revenue}."""
    return {d.name: round(d.total_revenue(), 2) for d in departments}


def key_statistics(patients, encounters, procedures):
    """
    Compute a set of meaningful statistics for the management dashboard.

    Returns:
        dict with various stats about patients, encounters, procedures.
    """
    patient_list = list(patients.values())
    enc_list = list(encounters.values())
    proc_list = list(procedures.values())

    ages = [p.age for p in patient_list]
    bmis = [p.bmi for p in patient_list if p.bmi is not None]
    a1cs = [p.a1c for p in patient_list if p.a1c is not None]
    smokers = sum(1 for p in patient_list if p.smoking)
    gender_counts = Counter(p.gender for p in patient_list)

    enc_types = Counter(e.encounter_type for e in enc_list)
    total_cost = sum(p.cost for p in proc_list)
    avg_cost = total_cost / len(proc_list) if proc_list else 0

    return {
        "total_patients": len(patient_list),
        "total_encounters": len(enc_list),
        "total_procedures": len(proc_list),
        "avg_age": round(sum(ages) / len(ages), 1) if ages else 0,
        "min_age": min(ages) if ages else 0,
        "max_age": max(ages) if ages else 0,
        "avg_bmi": round(sum(bmis) / len(bmis), 1) if bmis else 0,
        "avg_a1c": round(sum(a1cs) / len(a1cs), 2) if a1cs else 0,
        "smoker_count": smokers,
        "non_smoker_count": len(patient_list) - smokers,
        "gender_counts": dict(gender_counts),
        "encounter_type_counts": dict(enc_types),
        "total_revenue": round(total_cost, 2),
        "avg_procedure_cost": round(avg_cost, 2),
    }
