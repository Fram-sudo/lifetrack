#!/usr/bin/env python3
"""
Lifetrack - Script de mise a jour
Met a jour les fichiers systeme du vault sans toucher au contenu personnel.
"""

import sys, os, urllib.request, urllib.parse, stat
from pathlib import Path

# ── CONFIGURATION ────────────────────────────────────────────────
# A mettre a jour avec l'URL de ton depot GitHub apres publication
REPO_RAW = "https://raw.githubusercontent.com/Fram-sudo/lifetrack/main"

# ── FICHIERS SYSTEME ─────────────────────────────────────────────
# Ces fichiers sont telecharges et ecrases a chaque mise a jour.
# Le contenu personnel (Transactions/, bank_configs.json, etc.) n'est jamais touche.
SYSTEM_FILES = [
    # Scripts
    "_Système/Scripts/update.py",
    "_Système/Scripts/import_releves.py",
    "_Système/Scripts/parse_finances.py",
    "_Système/Scripts/create_fiches_medias.py",
    "_Système/Scripts/lancer_import.sh",
    "_Système/Scripts/lancer_import.bat",
    "_Système/Scripts/Import Relevés.bat",
    "_Système/Scripts/Import Relevés.desktop",
    "_Système/Scripts/QuickAdd/openDashboard.js",
    "_Système/Scripts/Hevy/import_hevy.py",
    "_Système/Scripts/Hevy/lancer_hevy.sh",
    "_Système/Scripts/Hevy/Import Hevy.desktop",
    "_Système/Scripts/Hevy/Import Hevy.bat",
    # Lanceurs racine
    "update.sh",
    "update.bat",
    # Guides
    "_Système/TUTO - Import de relevés bancaires.md",
    "_Système/Guide Lifetrack.md",
    "Guide Lifetrack - Démarrage & Utilisation.md",
    "README.md",
    # Dashboard
    "Dashboard.md",
    # MOC
    "_Système/MOC/🔍 Explorateur.md",
    "_Système/MOC/MOC - Commandes.md",
    "_Système/MOC/MOC - Films, Animés & Séries.md",
    "_Système/MOC/MOC - Jeux Vidéo.md",
    "_Système/MOC/MOC - Lectures.md",
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
    "_Système/Templates/Mettre à jour la note.md",
    "_Système/Templates/Mettre à jour la priorité.md",
    "_Système/Templates/Mettre à jour le statut.md",
    "_Système/Templates/Mettre à jour les affiches.md",
    "_Système/Templates/Ajouter une session.md",
    # Domaine Sport
    "2 - Domaines/Sport/🏋️ Sport.md",
    # Plugin obsidian-git
    ".obsidian/plugins/obsidian-git/main.js",
    ".obsidian/plugins/obsidian-git/manifest.json",
    ".obsidian/plugins/obsidian-git/styles.css",
]

# Fichier special : frontmatter utilisateur preserve, code JS mis a jour
FINANCES_MD = "2 - Domaines/Finances/💰 Finances.md"

# Fichier special : liste de plugins fusionnee (jamais ecrasee, pour ne pas
# desactiver un plugin que l'utilisateur aurait installe de son cote).
COMMUNITY_PLUGINS = ".obsidian/community-plugins.json"

# ── FICHIERS OBSOLETES ────────────────────────────────────────────
# Anciens fichiers systeme remplaces par une version fusionnee/renommee.
# Supprimes uniquement si le fichier de remplacement a ete telecharge avec succes,
# pour eviter de perdre du contenu si le reseau coupe en cours de route.
LEGACY_REMOVE = {
    "_Système/MOC/MOC - Films, Animés & Séries.md": [
        "_Système/MOC/MOC - Films & Animés.md",
        "_Système/MOC/MOC - Séries.md",
    ],
}

# Fichiers NE JAMAIS ajouter a SYSTEM_FILES (donnees personnelles / config locale) :
#   _Système/Config.md, _Système/Scripts/bank_configs.json, _Système/Scripts/script_config.json,
#   2 - Domaines/Sport/Data/*, 2 - Domaines/Finances/Transactions/*
# 🏋️ Sport.md n'a pas de frontmatter utilisateur (pas de config perso comme Finances.md,
# juste type/tags/cssclasses) -> il est ecrase entierement comme un fichier systeme normal.


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


def update_community_plugins(vault, new_content):
    """Fusionne la liste de plugins (union) au lieu d'ecraser : preserve les
    plugins que l'utilisateur aurait installes de son cote."""
    import json
    dest = vault / COMMUNITY_PLUGINS
    try:
        new_list = json.loads(new_content)
    except Exception:
        return "contenu distant invalide, ignore"
    current_list = []
    if dest.exists():
        try:
            current_list = json.loads(dest.read_text(encoding="utf-8"))
        except Exception:
            current_list = []
    merged = current_list + [p for p in new_list if p not in current_list]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    added = [p for p in new_list if p not in current_list]
    return f"fusionne ({len(added)} nouveau(x) : {', '.join(added)})" if added else "deja a jour"


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

    # Rendre les scripts shell/executables
    for sh in ["lancer_import.sh", "update.sh"]:
        make_executable(vault / "_Système/Scripts" / sh)
    make_executable(vault / "update.sh")
    make_executable(vault / "_Système/Scripts/Hevy/lancer_hevy.sh")
    make_executable(vault / "_Système/Scripts/Hevy/Import Hevy.desktop")
    make_executable(vault / "_Système/Scripts/Import Relevés.desktop")

    # Finances.md (traitement special)
    content = fetch(FINANCES_MD)
    if content:
        result = update_finances(vault, content)
        print(f"  v  {FINANCES_MD} ({result})")
        ok.append(FINANCES_MD)
    else:
        print(f"  x  {FINANCES_MD}")
        ko.append(FINANCES_MD)

    # community-plugins.json (traitement special : fusion, jamais ecrase)
    content = fetch(COMMUNITY_PLUGINS)
    if content:
        result = update_community_plugins(vault, content)
        print(f"  v  {COMMUNITY_PLUGINS} ({result})")
        ok.append(COMMUNITY_PLUGINS)
    else:
        print(f"  x  {COMMUNITY_PLUGINS}")
        ko.append(COMMUNITY_PLUGINS)

    # Nettoyage des anciens fichiers remplaces (uniquement si le remplacement a reussi)
    removed = []
    for new_path, old_paths in LEGACY_REMOVE.items():
        if new_path not in ok:
            continue
        for old_path in old_paths:
            old_file = vault / old_path
            if old_file.exists():
                try:
                    old_file.unlink()
                    print(f"  -  {old_path} (obsolete, supprime)")
                    removed.append(old_path)
                except Exception:
                    pass

    print(f"\n {len(ok)} fichier(s) mis a jour", end="")
    if removed:
        print(f", {len(removed)} fichier(s) obsolete(s) supprime(s)", end="")
    if ko:
        print(f", {len(ko)} echec(s) : {', '.join(ko)}")
    else:
        print(" - tout est a jour !")

    input("\nAppuie sur Entree pour fermer...")


if __name__ == "__main__":
    main()
