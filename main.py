"""
main.py
Entry point for the Clinical Data Warehouse application.

Usage:
    python main.py

The program will open a Tkinter GUI window. All data files are expected
to be located in the ./Data/ directory relative to this file.
"""

import sys
import os
import tkinter as tk

# Ensure the src/ directory is on the path so all modules import correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ui import ClinicalApp


def main():
    root = tk.Tk()
    app = ClinicalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
