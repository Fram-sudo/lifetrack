#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_hevy.py - Import des exports Hevy (CSV) vers Lifetrack
"""

import csv
import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "..", "script_config.json")

def load_vault_path():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f).get("vault_path", "")
    except Exception:
        return ""

VAULT_PATH = load_vault_path()
SPORT_DATA_DIR = os.path.join(VAULT_PATH, "2 - Domaines/Sport/Data")

# ── PARSING CSV ──────────────────────────────────────────────────────────────────
def parse_hevy_csv(filepath):
    """
    Parse un export CSV Hevy et retourne une liste de séances.
    Hevy exporte le poids dans la colonne 'weight_lbs' mais les valeurs
    correspondent à l'unité choisie dans l'app (kg si l'app est configurée en kg).
    """
    workouts = {}  # (title, start_time) → workout dict

    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title      = (row.get('title') or '').strip()
            start_time = (row.get('start_time') or '').strip()
            end_time   = (row.get('end_time') or '').strip()
            ex_title   = (row.get('exercise_title') or '').strip()
            set_index  = int(row.get('set_index') or 0)
            set_type   = (row.get('set_type') or 'normal').strip()
            # Colonne poids : weight_kg si dispo, sinon weight_lbs (valeur en unité app)
            w_raw  = row.get('weight_kg') or row.get('weight_lbs') or '0'
            weight = float(w_raw or 0)
            reps   = int(row.get('reps') or 0)
            rpe_r  = (row.get('rpe') or '').strip()
            rpe    = float(rpe_r) if rpe_r else None
            dur_s  = int(row.get('duration_seconds') or 0)

            key = (title, start_time)
            if key not in workouts:
                try:
                    dt_s = datetime.strptime(start_time[:19], '%Y-%m-%d %H:%M:%S')
                    dt_e = datetime.strptime(end_time[:19],   '%Y-%m-%d %H:%M:%S')
                    date_str   = dt_s.strftime('%Y-%m-%d')
                    duration_m = int((dt_e - dt_s).total_seconds() / 60)
                except Exception:
                    date_str   = start_time[:10] if start_time else '2000-01-01'
                    duration_m = 0

                safe = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                workouts[key] = {
                    'id':               f"{date_str}_{safe}",
                    'title':            title,
                    'date':             date_str,
                    'start_time':       start_time,
                    'end_time':         end_time,
                    'duration_minutes': duration_m,
                    'exercises':        {}
                }

            if ex_title:
                w = workouts[key]
                w['exercises'].setdefault(ex_title, []).append({
                    'index':            set_index,
                    'type':             set_type,
                    'weight_kg':        weight,
                    'reps':             reps,
                    'rpe':              rpe,
                    'duration_seconds': dur_s if dur_s > 0 else None
                })

    result = []
    for w in workouts.values():
        w['exercises'] = [
            {'name': name, 'sets': sorted(sets, key=lambda s: s['index'])}
            for name, sets in w['exercises'].items()
        ]
        result.append(w)

    return sorted(result, key=lambda w: w['date'])


def load_existing_year(year):
    path = os.path.join(SPORT_DATA_DIR, f"hevy_{year}.json")
    if os.path.exists(path):
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def merge_and_save(new_workouts):
    """Fusionne les nouvelles séances avec les JSON existants (par année)."""
    by_year = {}
    for w in new_workouts:
        year = w['date'][:4]
        by_year.setdefault(year, []).append(w)

    total_added = 0
    year_counts = {}
    os.makedirs(SPORT_DATA_DIR, exist_ok=True)

    for year, ws in sorted(by_year.items()):
        existing     = load_existing_year(year)
        existing_ids = {w['id'] for w in existing}
        added        = [w for w in ws if w['id'] not in existing_ids]
        merged       = sorted(existing + added, key=lambda w: w['date'])

        path = os.path.join(SPORT_DATA_DIR, f"hevy_{year}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        total_added    += len(added)
        year_counts[year] = len(added)

    return total_added, year_counts


# ── GUI ──────────────────────────────────────────────────────────────────────────
class ImportHevyApp:
    BG     = "#1e1e2e"
    CARD   = "#313244"
    ACCENT = "#1e66f5"
    FG     = "#cdd6f4"
    FG2    = "#a6adc8"
    SUCCESS = "#40a02b"
    ERROR   = "#d20f39"

    def __init__(self, root):
        self.root = root
        root.title("Import Hevy → Lifetrack")
        root.resizable(False, False)
        root.configure(bg=self.BG)

        self._build_ui()
        self.csv_path = None

        root.update_idletasks()
        w, h = 520, 360
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=self.BG, padx=24, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏋️  Import Hevy", font=("Inter", 16, "bold"),
                 bg=self.BG, fg=self.FG).pack(anchor="w")
        tk.Label(hdr, text="Importe ton export CSV Hevy dans Lifetrack",
                 font=("Inter", 10), bg=self.BG, fg=self.FG2).pack(anchor="w")

        tk.Frame(self.root, height=1, bg="#45475a").pack(fill="x")

        # Corps
        body = tk.Frame(self.root, bg=self.BG, padx=24, pady=18)
        body.pack(fill="both", expand=True)

        # Infos export
        info = tk.Frame(body, bg=self.CARD, padx=12, pady=10)
        info.pack(fill="x", pady=(0, 16))
        tk.Label(info, text="💡 Comment exporter depuis Hevy",
                 font=("Inter", 10, "bold"), bg=self.CARD, fg=self.FG).pack(anchor="w")
        tk.Label(info,
                 text="Profil → ⚙️ Paramètres → Exporter les données\n"
                      "Tu recevras un e-mail avec le fichier CSV en pièce jointe.",
                 font=("Inter", 9), bg=self.CARD, fg=self.FG2,
                 justify="left").pack(anchor="w", pady=(4, 0))

        # Sélecteur de fichier
        pick_row = tk.Frame(body, bg=self.BG)
        pick_row.pack(fill="x", pady=(0, 10))

        tk.Button(pick_row, text="📂  Choisir le fichier CSV",
                  command=self._pick_file,
                  font=("Inter", 10), bg=self.ACCENT, fg="white",
                  relief="flat", padx=12, pady=6,
                  cursor="hand2", activebackground="#1a5adb",
                  activeforeground="white").pack(side="left")

        self.file_var = tk.StringVar(value="Aucun fichier sélectionné")
        tk.Label(pick_row, textvariable=self.file_var,
                 font=("Inter", 9), bg=self.BG, fg=self.FG2,
                 wraplength=280).pack(side="left", padx=12)

        # Statut
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(body, textvariable=self.status_var,
                                   font=("Inter", 9), bg=self.BG, fg=self.FG2,
                                   justify="left", wraplength=460)
        self.status_lbl.pack(anchor="w", pady=(4, 0))

        # Bouton Importer
        btn_row = tk.Frame(body, bg=self.BG)
        btn_row.pack(fill="x", pady=(14, 0))

        self.import_btn = tk.Button(
            btn_row, text="⬆️  Importer",
            command=self._do_import,
            font=("Inter", 11, "bold"),
            bg=self.ACCENT, fg="white",
            relief="flat", padx=16, pady=8,
            cursor="hand2", state="disabled",
            activebackground="#1a5adb", activeforeground="white"
        )
        self.import_btn.pack(side="right")

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Choisir l'export CSV Hevy",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.csv_path = path
            self.file_var.set(os.path.basename(path))
            self.import_btn.config(state="normal")
            self.status_var.set("")

    def _do_import(self):
        if not self.csv_path:
            return
        try:
            self.status_var.set("⏳ Analyse du fichier en cours…")
            self.status_lbl.config(fg=self.FG2)
            self.root.update()

            workouts = parse_hevy_csv(self.csv_path)

            if not workouts:
                self.status_var.set("⚠️ Aucune séance trouvée dans ce fichier.")
                return

            added, by_year = merge_and_save(workouts)

            if added == 0:
                self.status_var.set("✅ Aucune nouvelle séance - tout est déjà importé.")
                self.status_lbl.config(fg=self.SUCCESS)
            else:
                lines = [f"✅ {added} séance(s) importée(s) avec succès :"]
                for y, n in sorted(by_year.items()):
                    if n > 0:
                        lines.append(f"   • {y} → {n} séance(s) ajoutée(s) dans hevy_{y}.json")
                self.status_var.set("\n".join(lines))
                self.status_lbl.config(fg=self.SUCCESS)

        except Exception as e:
            self.status_var.set(f"❌ Erreur : {e}")
            self.status_lbl.config(fg=self.ERROR)


def main():
    root = tk.Tk()
    ImportHevyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
