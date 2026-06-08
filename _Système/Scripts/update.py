#!/usr/bin/env python3
"""
Lifetrack - Script de mise a jour
Met a jour les fichiers systeme du vault sans toucher au contenu personnel.
"""

import sys, os, urllib.request, urllib.parse, stat
from pathlib import Path

# ── CONFIGURATION ────────────────────────────────────────────────
# A mettre a jour avec l'URL de ton depot GitHub apres publication
REPO_RAW = "https://raw.githubusercontent.com/OWNER/lifetrack/main"

# ── FICHIERS SYSTEME ─────────────────────────────────────────────
# Ces fichiers sont telecharges et ecrases a chaque mise a jour.
# Le contenu personnel (Transactions/, bank_configs.json, etc.) n'est jamais touche.
SYSTEM_FILES = [
    # Scripts
    "_Système/Scripts/update.py",
    "_Système/Scripts/import_releves.py",
    "_Système/Scripts/parse_finances.py",
    "_Système/Scripts/lancer_import.sh",
    "_Système/Scripts/lancer_import.bat",
    "_Système/Scripts/Import Relevés.bat",
    "_Système/Scripts/Import Relevés.desktop",
    # Lanceurs racine
    "update.sh",
    "update.bat",
    # Guides
    "_Système/TUTO - Import de relevés bancaires.md",
    "_Système/Guide Lifetrack.md",
    "Guide Lifetrack - Démarrage & Utilisation.md",
    # Dashboard
    "Dashboard.md",
    # MOC
    "_Système/MOC/🔍 Explorateur.md",
    "_Système/MOC/MOC - Commandes.md",
    "_Système/MOC/MOC - Films & Animés.md",
    "_Système/MOC/MOC - Jeux Vidéo.md",
    "_Système/MOC/MOC - Lectures.md",
    "_Système/MOC/MOC - Séries.md",
    "_Système/MOC/📊 Statistiques.md",
    # Templates
    "_Système/Templates/TPL - Animé.md",
    "_Système/Templates/TPL - Film.md",
    "_Système/Templates/TPL - Jeu Vidéo.md",
    "_Système/Templates/TPL - Manga & Manwha.md",
    "_Système/Templates/TPL - Roman & Livre.md",
    "_Système/Templates/TPL - Série.md",
    "_Système/Templates/TPL - Startup.md",
    "_Système/Templates/TPL - Suivi Commande.md",
]

# Fichier special : frontmatter utilisateur preserve, code JS mis a jour
FINANCES_MD = "2 - Domaines/Finances/💰 Finances.md"


def vault_root():
    """Racine du vault = 3 niveaux au-dessus de ce script (_Système/Scripts/update.py)."""
    return Path(__file__).resolve().parent.parent.parent


def fetch(rel_path):
    url = REPO_RAW + "/" + urllib.parse.quote(rel_path)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Lifetrack-Updater/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return None


def frontmatter_split(text):
    """Separe le frontmatter YAML du corps du fichier.
    Retourne (frontmatter_avec_delimiteurs, corps) ou (None, text) si pas de frontmatter."""
    lines = text.splitlines(keepends=True)
    count = 0
    for i, l in enumerate(lines):
        if l.strip() == "---":
            count += 1
            if count == 2:
                return "".join(lines[:i + 1]), "".join(lines[i + 1:])
    return None, text


def update_finances(vault, new_content):
    """Met a jour Finances.md : nouveau code JS + frontmatter utilisateur preserve."""
    dest = vault / FINANCES_MD
    if dest.exists():
        current = dest.read_text(encoding="utf-8")
        user_fm, _ = frontmatter_split(current)
        _, new_body = frontmatter_split(new_content)
        if user_fm and new_body is not None:
            merged = user_fm + new_body
            dest.write_text(merged, encoding="utf-8")
            return "code JS mis a jour, frontmatter preserve"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(new_content, encoding="utf-8")
    return "cree"


def make_executable(path):
    """Rend un fichier executable (Linux/Mac)."""
    if sys.platform != "win32":
        try:
            p = Path(path)
            p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            pass


def main():
    vault = vault_root()
    print("\n Lifetrack Updater")
    print(f" Vault  : {vault}")
    print(f" Source : {REPO_RAW}\n")

    if "OWNER" in REPO_RAW:
        print(" ATTENTION : REPO_RAW contient encore 'OWNER' - mets a jour l'URL dans update.py\n")

    ok, ko = [], []

    # Fichiers systeme
    for path in SYSTEM_FILES:
        content = fetch(path)
        if content is None:
            print(f"  x  {path}")
            ko.append(path)
        else:
            dest = vault / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            print(f"  v  {path}")
            ok.append(path)

    # Rendre les scripts shell executables
    for sh in ["lancer_import.sh", "update.sh"]:
        make_executable(vault / "_Système/Scripts" / sh)
    make_executable(vault / "update.sh")

    # Finances.md (traitement special)
    content = fetch(FINANCES_MD)
    if content:
        result = update_finances(vault, content)
        print(f"  v  {FINANCES_MD} ({result})")
        ok.append(FINANCES_MD)
    else:
        print(f"  x  {FINANCES_MD}")
        ko.append(FINANCES_MD)

    print(f"\n {len(ok)} fichier(s) mis a jour", end="")
    if ko:
        print(f", {len(ko)} echec(s) : {', '.join(ko)}")
    else:
        print(" - tout est a jour !")

    input("\nAppuie sur Entree pour fermer...")


if __name__ == "__main__":
    main()
