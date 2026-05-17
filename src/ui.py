"""
ui.py
Tkinter UI application for the Clinical Data Warehouse.
Provides role-based access to patient data and analytics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

from user import validate_login, load_credentials
from data_loader import load_all
from analytics import (
    count_visits_on_date,
    count_visits_per_patient_on_date,
    count_visits_by_department_on_date,
    top_providers_by_workload,
    department_revenue,
    key_statistics,
)
from file_writer import save_patients
from logger import log_event
from patient import Patient


# ─── Colour palette ──────────────────────────────────────────────────────────
BG        = "#F0F4F8"
SIDEBAR   = "#1E3A5F"
ACCENT    = "#2E86AB"
BTN_FG    = "#FFFFFF"
BTN_HOVER = "#1B6CA8"
DANGER    = "#C0392B"
SUCCESS   = "#27AE60"
TEXT      = "#2C3E50"
LIGHT     = "#FFFFFF"
ENTRY_BG  = "#FFFFFF"
HEADER_BG = "#1E3A5F"
ROW_ALT   = "#EBF5FB"


def _make_button(parent, text, command, color=ACCENT, width=22):
    """Helper to create a consistently styled button."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=BTN_FG,
        font=("Helvetica", 11, "bold"),
        relief="flat", cursor="hand2",
        padx=10, pady=6, width=width,
        activebackground=BTN_HOVER, activeforeground=BTN_FG,
    )
    return btn


def _label(parent, text, font=("Helvetica", 11), **kwargs):
    return tk.Label(parent, text=text, font=font, bg=BG, fg=TEXT, **kwargs)


class ClinicalApp:
    """
    Main Tkinter application class for the Clinical Data Warehouse UI.

    Attributes:
        root       – Tk root window
        credentials– dict of {username: {password, role}}
        patients   – dict of {patient_id: Patient}
        providers  – dict of {provider_id: Provider}
        departments– dict of {dept_id: Department}
        encounters – dict of {enc_id: Encounter}
        procedures – dict of {proc_id: Procedure}
        notes      – list of Note objects
        current_user – User object after successful login
    """

    DATA_DIR = "./Data/"
    CRED_PATH = "./Data/credentials.csv"

    def __init__(self, root):
        self.root = root
        self.root.title("Clinical Data Warehouse")
        self.root.geometry("950x680")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.credentials = load_credentials(self.CRED_PATH)
        self.patients = {}
        self.providers = {}
        self.departments = {}
        self.encounters = {}
        self.procedures = {}
        self.notes = []
        self.current_user = None
        self._action_log = []          # track actions for this session

        self._show_login()

    # ─────────────────────────────────────────────────────────────────────────
    # SCREEN MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def _clear(self):
        """Destroy all widgets in the root window."""
        for w in self.root.winfo_children():
            w.destroy()

    # ─────────────────────────────────────────────────────────────────────────
    # LOGIN SCREEN
    # ─────────────────────────────────────────────────────────────────────────

    def _show_login(self):
        self._clear()

        # Header banner
        banner = tk.Frame(self.root, bg=HEADER_BG, height=80)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text="🏥  Clinical Data Warehouse",
            font=("Helvetica", 22, "bold"),
            bg=HEADER_BG, fg=LIGHT,
        ).pack(pady=20)

        # Card frame
        card = tk.Frame(self.root, bg=LIGHT, bd=0, relief="flat")
        card.place(relx=0.5, rely=0.52, anchor="center", width=420, height=360)

        tk.Label(card, text="Sign In", font=("Helvetica", 18, "bold"),
                 bg=LIGHT, fg=TEXT).pack(pady=(30, 5))
        tk.Label(card, text="Enter your credentials to continue",
                 font=("Helvetica", 10), bg=LIGHT, fg="#7F8C8D").pack(pady=(0, 20))

        # Username
        tk.Label(card, text="Username", font=("Helvetica", 11, "bold"),
                 bg=LIGHT, fg=TEXT, anchor="w").pack(fill="x", padx=40)
        self._username_var = tk.StringVar()
        username_entry = tk.Entry(card, textvariable=self._username_var,
                                  font=("Helvetica", 12), relief="solid", bd=1)
        username_entry.pack(fill="x", padx=40, ipady=6, pady=(2, 12))
        username_entry.focus()

        # Password
        tk.Label(card, text="Password", font=("Helvetica", 11, "bold"),
                 bg=LIGHT, fg=TEXT, anchor="w").pack(fill="x", padx=40)
        self._password_var = tk.StringVar()
        tk.Entry(card, textvariable=self._password_var, show="•",
                 font=("Helvetica", 12), relief="solid", bd=1).pack(
            fill="x", padx=40, ipady=6, pady=(2, 20))

        # Error label
        self._login_error = tk.StringVar()
        tk.Label(card, textvariable=self._login_error, font=("Helvetica", 10),
                 bg=LIGHT, fg=DANGER).pack()

        # Login button
        _make_button(card, "  Log In  ", self._attempt_login, width=16).pack(pady=8)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._attempt_login())

    def _attempt_login(self):
        username = self._username_var.get().strip()
        password = self._password_var.get().strip()
        user = validate_login(username, password, self.credentials)

        if user:
            self.current_user = user
            self._action_log = []
            log_event(username, user.role, "login", "success")
            self._load_data()
            self._show_dashboard()
        else:
            self._login_error.set("⚠  Invalid username or password.")
            log_event(username, "unknown", "login", "failed")

    # ─────────────────────────────────────────────────────────────────────────
    # DATA LOADING
    # ─────────────────────────────────────────────────────────────────────────

    def _load_data(self):
        """Load all CSV data into memory."""
        (self.patients, self.providers, self.departments,
         self.encounters, self.procedures, self.notes) = load_all(self.DATA_DIR)

    # ─────────────────────────────────────────────────────────────────────────
    # DASHBOARD / MAIN MENU
    # ─────────────────────────────────────────────────────────────────────────

    def _show_dashboard(self):
        self._clear()
        self.root.unbind("<Return>")

        user = self.current_user

        # Sidebar
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🏥", font=("Helvetica", 28),
                 bg=SIDEBAR, fg=LIGHT).pack(pady=(30, 5))
        tk.Label(sidebar, text="Clinical DW", font=("Helvetica", 14, "bold"),
                 bg=SIDEBAR, fg=LIGHT).pack()
        tk.Frame(sidebar, bg="#2E4B70", height=1).pack(fill="x", padx=20, pady=15)

        tk.Label(sidebar, text=f"👤  {user.username}",
                 font=("Helvetica", 11, "bold"), bg=SIDEBAR, fg=LIGHT).pack(anchor="w", padx=20)
        tk.Label(sidebar, text=f"Role: {user.role.capitalize()}",
                 font=("Helvetica", 9), bg=SIDEBAR, fg="#A9C4D9").pack(anchor="w", padx=20, pady=(2, 20))

        # Action buttons in sidebar
        for action in user.get_allowed_actions():
            cmd = self._get_action_command(action)
            color = DANGER if action == "Exit" else ACCENT
            btn = tk.Button(
                sidebar, text=action, command=cmd,
                bg=color, fg=BTN_FG,
                font=("Helvetica", 10, "bold"),
                relief="flat", cursor="hand2",
                padx=8, pady=8, anchor="w",
                activebackground=BTN_HOVER, activeforeground=BTN_FG,
            )
            btn.pack(fill="x", padx=15, pady=4)

        # Main content area
        self._content = tk.Frame(self.root, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        # Welcome panel
        self._show_welcome()

    def _show_welcome(self):
        """Show a welcome/home panel in the content area."""
        for w in self._content.winfo_children():
            w.destroy()

        tk.Label(
            self._content,
            text=f"Welcome, {self.current_user.username.capitalize()}!",
            font=("Helvetica", 20, "bold"), bg=BG, fg=TEXT,
        ).pack(pady=(50, 10))
        tk.Label(
            self._content,
            text="Select an action from the sidebar to get started.",
            font=("Helvetica", 12), bg=BG, fg="#7F8C8D",
        ).pack()

        # Quick stats
        stats_frame = tk.Frame(self._content, bg=BG)
        stats_frame.pack(pady=40)
        cards = [
            ("👥 Patients", len(self.patients)),
            ("🏨 Encounters", len(self.encounters)),
            ("💊 Procedures", len(self.procedures)),
        ]
        for label, val in cards:
            c = tk.Frame(stats_frame, bg=LIGHT, relief="flat", bd=0)
            c.pack(side="left", padx=15, ipadx=20, ipady=15)
            tk.Label(c, text=str(val), font=("Helvetica", 28, "bold"),
                     bg=LIGHT, fg=ACCENT).pack()
            tk.Label(c, text=label, font=("Helvetica", 10),
                     bg=LIGHT, fg=TEXT).pack()

    def _get_action_command(self, action):
        """Map action label to the correct handler method."""
        mapping = {
            "Retrieve Patient":        self._action_retrieve_patient,
            "Add Patient":             self._action_add_patient,
            "Remove Patient":          self._action_remove_patient,
            "Count Visits":            self._action_count_visits,
            "View Note":               self._action_view_note,
            "Generate Key Statistics": self._action_key_statistics,
            "Monitor Revenue":         self._action_monitor_revenue,
            "Monitor Workload":        self._action_monitor_workload,
            "Exit":                    self._exit_app,
        }
        return mapping.get(action, self._show_welcome)

    def _clear_content(self):
        """Clear the right-hand content panel."""
        for w in self._content.winfo_children():
            w.destroy()

    def _content_header(self, title):
        """Render a header bar in the content area."""
        hdr = tk.Frame(self._content, bg=HEADER_BG, height=50)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=("Helvetica", 14, "bold"),
                 bg=HEADER_BG, fg=LIGHT).pack(side="left", padx=20, pady=10)

    # ─────────────────────────────────────────────────────────────────────────
    # RETRIEVE PATIENT
    # ─────────────────────────────────────────────────────────────────────────

    def _action_retrieve_patient(self):
        self._clear_content()
        self._content_header("🔍  Retrieve Patient")
        self._log_action("Retrieve Patient")

        form = tk.Frame(self._content, bg=BG)
        form.pack(pady=30, padx=40, anchor="w")

        _label(form, "Patient ID:").grid(row=0, column=0, sticky="w", pady=8)
        pid_var = tk.StringVar()
        tk.Entry(form, textvariable=pid_var, font=("Helvetica", 12),
                 relief="solid", bd=1, width=20).grid(row=0, column=1, padx=10)

        result_frame = tk.Frame(self._content, bg=BG)
        result_frame.pack(fill="both", expand=True, padx=40)

        def search():
            for w in result_frame.winfo_children():
                w.destroy()
            pid = pid_var.get().strip()
            if pid not in self.patients:
                tk.Label(result_frame, text=f"⚠  Patient '{pid}' not found.",
                         font=("Helvetica", 11), bg=BG, fg=DANGER).pack(pady=10)
                return
            p = self.patients[pid]
            enc = p.most_recent_encounter()

            info = [
                ("Patient ID",   p.patient_id),
                ("Age",          p.age),
                ("Gender",       p.gender),
                ("BMI",          p.bmi),
                ("A1C",          p.a1c if p.a1c else "N/A"),
                ("BP Systolic",  p.bp_sys),
                ("BP Diastolic", p.bp_dia),
                ("Smoker",       "Yes" if p.smoking else "No"),
                ("Total Visits", p.count_encounters()),
            ]
            if enc:
                info += [
                    ("Last Visit Date", enc.encounter_date),
                    ("Last Visit Type", enc.encounter_type),
                    ("Provider",        enc.provider_id),
                    ("Department",      enc.department_id),
                ]

            card = tk.Frame(result_frame, bg=LIGHT, relief="flat")
            card.pack(fill="x", pady=10)
            for i, (field, val) in enumerate(info):
                row_bg = ROW_ALT if i % 2 == 0 else LIGHT
                row = tk.Frame(card, bg=row_bg)
                row.pack(fill="x")
                tk.Label(row, text=field, font=("Helvetica", 10, "bold"),
                         bg=row_bg, fg=TEXT, width=20, anchor="w").pack(side="left", padx=10, pady=5)
                tk.Label(row, text=str(val), font=("Helvetica", 10),
                         bg=row_bg, fg=TEXT, anchor="w").pack(side="left")

        _make_button(form, "Search", search, width=10).grid(row=0, column=2, padx=8)

    # ─────────────────────────────────────────────────────────────────────────
    # ADD PATIENT
    # ─────────────────────────────────────────────────────────────────────────

    def _action_add_patient(self):
        self._clear_content()
        self._content_header("➕  Add Patient")
        self._log_action("Add Patient")

        canvas = tk.Canvas(self._content, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self._content, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        form = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        fields = {}

        def row(label, widget_fn, r):
            _label(form, label).grid(row=r, column=0, sticky="w", pady=6, padx=20)
            w = widget_fn(form)
            w.grid(row=r, column=1, padx=10, pady=6, sticky="w")
            return w

        def entry(parent):
            v = tk.StringVar()
            e = tk.Entry(parent, textvariable=v, font=("Helvetica", 11),
                         relief="solid", bd=1, width=22)
            fields[e] = v
            return e

        pid_var = tk.StringVar()
        _label(form, "Patient ID *").grid(row=0, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=pid_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=0, column=1, padx=10, pady=6)

        age_var = tk.StringVar()
        _label(form, "Age *").grid(row=1, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=age_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=1, column=1, padx=10, pady=6)

        gender_var = tk.StringVar(value="Male")
        _label(form, "Gender *").grid(row=2, column=0, sticky="w", pady=6, padx=20)
        ttk.Combobox(form, textvariable=gender_var,
                     values=["Male", "Female", "Non-binary"],
                     state="readonly", width=20).grid(row=2, column=1, padx=10, pady=6)

        bmi_var = tk.StringVar()
        _label(form, "BMI *").grid(row=3, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=bmi_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=3, column=1, padx=10, pady=6)

        a1c_var = tk.StringVar()
        _label(form, "A1C (leave blank if N/A)").grid(row=4, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=a1c_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=4, column=1, padx=10, pady=6)

        bps_var = tk.StringVar()
        _label(form, "BP Systolic *").grid(row=5, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=bps_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=5, column=1, padx=10, pady=6)

        bpd_var = tk.StringVar()
        _label(form, "BP Diastolic *").grid(row=6, column=0, sticky="w", pady=6, padx=20)
        tk.Entry(form, textvariable=bpd_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=22).grid(row=6, column=1, padx=10, pady=6)

        smoking_var = tk.StringVar(value="No")
        _label(form, "Smoker *").grid(row=7, column=0, sticky="w", pady=6, padx=20)
        ttk.Combobox(form, textvariable=smoking_var,
                     values=["Yes", "No"], state="readonly",
                     width=20).grid(row=7, column=1, padx=10, pady=6)

        status_var = tk.StringVar()
        tk.Label(form, textvariable=status_var, font=("Helvetica", 10),
                 bg=BG, fg=SUCCESS).grid(row=9, column=0, columnspan=3, pady=4)

        def submit():
            pid = pid_var.get().strip()
            if not pid:
                status_var.set("⚠  Patient ID is required.")
                return
            try:
                age  = int(age_var.get())
                bmi  = float(bmi_var.get())
                bps  = int(bps_var.get())
                bpd  = int(bpd_var.get())
                a1c  = float(a1c_var.get()) if a1c_var.get().strip() else None
            except ValueError:
                status_var.set("⚠  Please enter valid numeric values.")
                return

            smoking = smoking_var.get() == "Yes"

            if pid in self.patients:
                # Patient exists — ask for a new encounter date
                self._add_encounter_for_existing(pid)
                return

            new_patient = Patient(pid, age, gender_var.get(), bmi, a1c, bps, bpd, smoking)
            self.patients[pid] = new_patient
            save_patients(self.patients, self.DATA_DIR)
            status_var.set(f"✅  Patient {pid} added successfully.")

        _make_button(form, "Submit", submit, width=14).grid(
            row=8, column=1, pady=15, sticky="w", padx=10)

    def _add_encounter_for_existing(self, pid):
        """Prompt for a visit date when patient already exists."""
        win = tk.Toplevel(self.root)
        win.title("Add Visit")
        win.geometry("340x200")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text=f"Patient {pid} already exists.",
                 font=("Helvetica", 11, "bold"), bg=BG, fg=TEXT).pack(pady=15)
        tk.Label(win, text="Enter visit date (YYYY-MM-DD):",
                 font=("Helvetica", 10), bg=BG, fg=TEXT).pack()

        date_var = tk.StringVar()
        tk.Entry(win, textvariable=date_var, font=("Helvetica", 11),
                 relief="solid", bd=1, width=18).pack(pady=8)

        msg = tk.StringVar()
        tk.Label(win, textvariable=msg, bg=BG, fg=SUCCESS, font=("Helvetica", 10)).pack()

        def add_visit():
            from encounter import Encounter
            date = date_var.get().strip()
            if not date:
                msg.set("Please enter a date.")
                return
            enc_id = "E" + "".join(random.choices(string.digits, k=6))
            enc = Encounter(enc_id, pid, "PR1", "D1", date, "Outpatient")
            self.patients[pid].add_encounter(enc)
            self.encounters[enc_id] = enc
            msg.set(f"✅  Visit {enc_id} added.")

        _make_button(win, "Add Visit", add_visit, width=14).pack(pady=6)

    # ─────────────────────────────────────────────────────────────────────────
    # REMOVE PATIENT
    # ─────────────────────────────────────────────────────────────────────────

    def _action_remove_patient(self):
        self._clear_content()
        self._content_header("🗑  Remove Patient")
        self._log_action("Remove Patient")

        form = tk.Frame(self._content, bg=BG)
        form.pack(pady=30, padx=40, anchor="w")

        _label(form, "Patient ID:").grid(row=0, column=0, sticky="w", pady=8)
        pid_var = tk.StringVar()
        tk.Entry(form, textvariable=pid_var, font=("Helvetica", 12),
                 relief="solid", bd=1, width=20).grid(row=0, column=1, padx=10)

        status_var = tk.StringVar()
        tk.Label(self._content, textvariable=status_var, font=("Helvetica", 11),
                 bg=BG, fg=DANGER).pack(pady=5)

        def remove():
            pid = pid_var.get().strip()
            if pid not in self.patients:
                status_var.set(f"⚠  Patient '{pid}' not found.")
                return
            confirm = messagebox.askyesno(
                "Confirm Removal",
                f"Remove ALL records for patient {pid}? This cannot be undone.",
            )
            if confirm:
                del self.patients[pid]
                # Also remove encounters
                to_del = [eid for eid, e in self.encounters.items() if e.patient_id == pid]
                for eid in to_del:
                    del self.encounters[eid]
                save_patients(self.patients, self.DATA_DIR)
                status_var.configure(fg=SUCCESS)
                status_var.set(f"✅  Patient {pid} and {len(to_del)} encounter(s) removed.")

        _make_button(form, "Remove", remove, color=DANGER, width=10).grid(
            row=0, column=2, padx=8)

    # ─────────────────────────────────────────────────────────────────────────
    # COUNT VISITS
    # ─────────────────────────────────────────────────────────────────────────

    def _action_count_visits(self):
        self._clear_content()
        self._content_header("📅  Count Visits")
        self._log_action("Count Visits")

        form = tk.Frame(self._content, bg=BG)
        form.pack(pady=20, padx=40, anchor="w")

        _label(form, "Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=8)
        date_var = tk.StringVar()
        tk.Entry(form, textvariable=date_var, font=("Helvetica", 12),
                 relief="solid", bd=1, width=18).grid(row=0, column=1, padx=10)

        mode_var = tk.StringVar(value="Total")
        _label(form, "View by:").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Combobox(form, textvariable=mode_var,
                     values=["Total", "Per Patient", "By Department"],
                     state="readonly", width=18).grid(row=1, column=1, padx=10)

        result_frame = tk.Frame(self._content, bg=BG)
        result_frame.pack(fill="both", expand=True, padx=40, pady=10)

        def search():
            for w in result_frame.winfo_children():
                w.destroy()
            date = date_var.get().strip()
            mode = mode_var.get()

            if mode == "Total":
                total = count_visits_on_date(self.encounters, date)
                tk.Label(result_frame,
                         text=f"Total visits on {date}:  {total}",
                         font=("Helvetica", 14, "bold"), bg=BG, fg=ACCENT).pack(pady=20)

            elif mode == "Per Patient":
                data = count_visits_per_patient_on_date(self.patients, date)
                if not data:
                    tk.Label(result_frame, text="No visits found for that date.",
                             bg=BG, fg=TEXT, font=("Helvetica", 11)).pack()
                    return
                self._render_table(result_frame, ["Patient ID", "Visits"], list(data.items()))

            elif mode == "By Department":
                data = count_visits_by_department_on_date(self.departments, date)
                if not data:
                    tk.Label(result_frame, text="No visits found for that date.",
                             bg=BG, fg=TEXT, font=("Helvetica", 11)).pack()
                    return
                self._render_table(result_frame, ["Department", "Visits"], list(data.items()))

        _make_button(form, "Search", search, width=10).grid(row=0, column=2, padx=8)

    # ─────────────────────────────────────────────────────────────────────────
    # VIEW NOTE
    # ─────────────────────────────────────────────────────────────────────────

    def _action_view_note(self):
        self._clear_content()
        self._content_header("📝  View Clinical Note")
        self._log_action("View Note")

        form = tk.Frame(self._content, bg=BG)
        form.pack(pady=20, padx=40, anchor="w")

        _label(form, "Patient ID:").grid(row=0, column=0, sticky="w", pady=8)
        pid_var = tk.StringVar()
        tk.Entry(form, textvariable=pid_var, font=("Helvetica", 12),
                 relief="solid", bd=1, width=18).grid(row=0, column=1, padx=10)

        _label(form, "Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=8)
        date_var = tk.StringVar()
        tk.Entry(form, textvariable=date_var, font=("Helvetica", 12),
                 relief="solid", bd=1, width=18).grid(row=1, column=1, padx=10)

        result_frame = tk.Frame(self._content, bg=BG)
        result_frame.pack(fill="both", expand=True, padx=40, pady=10)

        def search():
            for w in result_frame.winfo_children():
                w.destroy()
            pid  = pid_var.get().strip()
            date = date_var.get().strip()

            matching = [
                n for n in self.notes
                if n.patient_id == pid and n.note_date == date
            ]

            if not matching:
                tk.Label(result_frame,
                         text=f"No notes found for patient '{pid}' on {date}.",
                         font=("Helvetica", 11), bg=BG, fg=DANGER).pack(pady=10)
                return

            for i, note in enumerate(matching):
                card = tk.Frame(result_frame, bg=LIGHT, relief="flat")
                card.pack(fill="x", pady=6)
                header = tk.Frame(card, bg=ACCENT)
                header.pack(fill="x")
                tk.Label(header,
                         text=f"  Note {note.note_id}  |  {note.note_type}  |  {note.note_date}",
                         font=("Helvetica", 10, "bold"), bg=ACCENT, fg=LIGHT).pack(
                    side="left", pady=5, padx=8)
                tk.Label(card, text=note.note_text, font=("Helvetica", 10),
                         bg=LIGHT, fg=TEXT, wraplength=600, justify="left",
                         anchor="w").pack(fill="x", padx=12, pady=8)

        _make_button(form, "Search", search, width=10).grid(row=0, column=2, padx=8, rowspan=2)

    # ─────────────────────────────────────────────────────────────────────────
    # KEY STATISTICS  (management)
    # ─────────────────────────────────────────────────────────────────────────

    def _action_key_statistics(self):
        self._clear_content()
        self._content_header("📊  Key Statistics")
        self._log_action("Generate Key Statistics")

        stats = key_statistics(self.patients, self.encounters, self.procedures)

        canvas = tk.Canvas(self._content, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self._content, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        sections = [
            ("Population Overview", [
                ("Total Patients",    stats["total_patients"]),
                ("Total Encounters",  stats["total_encounters"]),
                ("Total Procedures",  stats["total_procedures"]),
            ]),
            ("Patient Demographics", [
                ("Average Age",  stats["avg_age"]),
                ("Age Range",    f"{stats['min_age']} – {stats['max_age']}"),
                ("Average BMI",  stats["avg_bmi"]),
                ("Average A1C",  stats["avg_a1c"]),
                ("Smokers",      stats["smoker_count"]),
                ("Non-Smokers",  stats["non_smoker_count"]),
            ]),
            ("Encounter Types", [
                (k, v) for k, v in stats["encounter_type_counts"].items()
            ]),
            ("Financial Summary", [
                ("Total Revenue",         f"${stats['total_revenue']:,.2f}"),
                ("Avg Procedure Cost",    f"${stats['avg_procedure_cost']:,.2f}"),
            ]),
        ]

        for section_title, rows in sections:
            tk.Label(inner, text=section_title, font=("Helvetica", 13, "bold"),
                     bg=BG, fg=ACCENT).pack(anchor="w", padx=30, pady=(18, 4))
            card = tk.Frame(inner, bg=LIGHT)
            card.pack(fill="x", padx=30, pady=2)
            for i, (field, val) in enumerate(rows):
                row_bg = ROW_ALT if i % 2 == 0 else LIGHT
                row = tk.Frame(card, bg=row_bg)
                row.pack(fill="x")
                tk.Label(row, text=field, font=("Helvetica", 10, "bold"),
                         bg=row_bg, fg=TEXT, width=25, anchor="w").pack(side="left", padx=12, pady=5)
                tk.Label(row, text=str(val), font=("Helvetica", 10),
                         bg=row_bg, fg=TEXT, anchor="w").pack(side="left")

        # Gender breakdown
        tk.Label(inner, text="Gender Breakdown", font=("Helvetica", 13, "bold"),
                 bg=BG, fg=ACCENT).pack(anchor="w", padx=30, pady=(18, 4))
        card = tk.Frame(inner, bg=LIGHT)
        card.pack(fill="x", padx=30, pady=2)
        for i, (g, cnt) in enumerate(stats["gender_counts"].items()):
            row_bg = ROW_ALT if i % 2 == 0 else LIGHT
            row = tk.Frame(card, bg=row_bg)
            row.pack(fill="x")
            tk.Label(row, text=g, font=("Helvetica", 10, "bold"),
                     bg=row_bg, fg=TEXT, width=25, anchor="w").pack(side="left", padx=12, pady=5)
            tk.Label(row, text=str(cnt), font=("Helvetica", 10),
                     bg=row_bg, fg=TEXT).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # MONITOR REVENUE  (management)
    # ─────────────────────────────────────────────────────────────────────────

    def _action_monitor_revenue(self):
        self._clear_content()
        self._content_header("💰  Department Revenue")
        self._log_action("Monitor Revenue")

        revenues = department_revenue(list(self.departments.values()))
        rows = sorted(revenues.items(), key=lambda x: x[1], reverse=True)

        frame = tk.Frame(self._content, bg=BG)
        frame.pack(pady=20, padx=40, fill="both", expand=True)

        total = sum(revenues.values())
        tk.Label(frame, text=f"Total Hospital Revenue:  ${total:,.2f}",
                 font=("Helvetica", 14, "bold"), bg=BG, fg=ACCENT).pack(pady=(0, 15))

        self._render_table(frame, ["Department", "Revenue ($)"],
                           [(k, f"{v:,.2f}") for k, v in rows])

    # ─────────────────────────────────────────────────────────────────────────
    # MONITOR WORKLOAD  (admin)
    # ─────────────────────────────────────────────────────────────────────────

    def _action_monitor_workload(self):
        self._clear_content()
        self._content_header("🩺  Provider Workload")
        self._log_action("Monitor Workload")

        ranked = top_providers_by_workload(list(self.providers.values()))

        frame = tk.Frame(self._content, bg=BG)
        frame.pack(pady=20, padx=40, fill="both", expand=True)

        self._render_table(
            frame,
            ["Rank", "Provider ID", "Name", "Encounters"],
            [(i + 1, pid, name, cnt) for i, (pid, name, cnt) in enumerate(ranked)],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SHARED UI HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _render_table(self, parent, headers, rows):
        """Render a styled table inside parent frame."""
        table = tk.Frame(parent, bg=LIGHT)
        table.pack(fill="both", expand=True)

        # Header row
        for col, h in enumerate(headers):
            tk.Label(table, text=h, font=("Helvetica", 10, "bold"),
                     bg=HEADER_BG, fg=LIGHT, padx=12, pady=7,
                     relief="flat", anchor="w").grid(
                row=0, column=col, sticky="ew", padx=1, pady=1)
            table.columnconfigure(col, weight=1)

        # Data rows
        for r, row in enumerate(rows):
            bg = ROW_ALT if r % 2 == 0 else LIGHT
            for col, val in enumerate(row):
                tk.Label(table, text=str(val), font=("Helvetica", 10),
                         bg=bg, fg=TEXT, padx=12, pady=5, anchor="w").grid(
                    row=r + 1, column=col, sticky="ew", padx=1)

    # ─────────────────────────────────────────────────────────────────────────
    # LOGGING & EXIT
    # ─────────────────────────────────────────────────────────────────────────

    def _log_action(self, action):
        """Log this action for the current user session."""
        if self.current_user:
            self._action_log.append(action)
            log_event(self.current_user.username, self.current_user.role, action)

    def _exit_app(self):
        """Flush session log and close the application."""
        self.root.quit()
        self.root.destroy()
