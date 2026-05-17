# Clinical Data Warehouse - HI 741 Final Project

**Student:** Nikhila Pati  
**Course:** HI 741 Spring 2026  
**Instructor:** Lu He  

---
 https://github.com/nikhilapati/hospital_managment.git
---

## What this program does

This is a desktop application for a hospital clinical data warehouse. It has a login screen and depending on who logs in, they see different buttons and can do different things. For example a clinician can look up patients and add or remove them, but a management user can only see statistics and revenue reports.

I built this using Python and Tkinter for the GUI. All the data is stored in CSV files inside the Data folder.

---

## How to run it

Make sure you have Python 3.9 or higher installed.

If you are on Mac and get a tkinter error, run this first:
```
brew install python-tk@3.13
```

If you are on Linux:
```
sudo apt install python3-tk
```

Windows should work without any extra steps.

Then just run:
```
python3 main.py
```

---

## Login credentials

These are the test users already in credentials.csv:

| Username | Password | Role |
|----------|----------|------|
| alice | pass123 | clinician |
| brandon | pass124 | clinician |
| nina | pass201 | nurse |
| omar | pass202 | nurse |
| dave | pass000 | admin |
| erin | admin456 | admin |
| carol | pass789 | management |
| mia | mgmt456 | management |

I usually test with alice/pass123 for full access or carol/pass789 for the statistics side.

---

## File structure

```
project/
├── main.py              <- run this
├── README.md
├── requirements.txt
├── UML_Diagram.pdf
├── Data/
│   ├── credentials.csv
│   ├── patients.csv
│   ├── encounters.csv
│   ├── providers.csv
│   ├── departments.csv
│   ├── procedures.csv
│   ├── notes.csv
│   └── data_generator.py
├── output/
│   └── usage_statistics.csv  <- created automatically when you run
└── src/
    ├── ui.py
    ├── user.py
    ├── patient.py
    ├── encounter.py
    ├── provider.py
    ├── department.py
    ├── procedure.py
    ├── note.py
    ├── analytics.py
    ├── data_loader.py
    ├── file_writer.py
    └── logger.py
```

---

## What each role can do

- **clinician / nurse** - retrieve patient, add patient, remove patient, count visits, view notes
- **admin** - count visits, monitor provider workload
- **management** - generate key statistics, monitor department revenue

---

## Output files

The program creates/updates two files automatically:

1. **Data/patients.csv** - gets updated whenever a patient is added or removed
2. **output/usage_statistics.csv** - every login and action is recorded here, including failed login attempts

---

## Classes used

I created 8 classes for this project:

- ClinicalApp - the main tkinter window and all UI logic
- User - stores the logged in user and their role
- Patient - patient information and their visit history
- Encounter - a single visit/encounter
- Provider - doctor or provider info
- Department - hospital department
- Procedure - a procedure done during a visit
- Note - clinical note for a patient visit

---

## Regenerating data

If you want to reset the data back to the original:
```
cd Data
python3 data_generator.py
```

---

## Notes

- I did not use any third party libraries, everything is from Python standard library
- The src/ folder has all the modules and main.py imports from there
- If usage_statistics.csv does not exist yet it will be created on first login

