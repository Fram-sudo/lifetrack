#!/usr/bin/env python3
"""
Import de relevés bancaires (SG / Revolut / génériques) → JSON annuels Obsidian.
Interface graphique - Windows & Linux.

Emplacement attendu : <vault>/_Système/Scripts/import_releves.py
Le script trouve le vault automatiquement depuis son emplacement.
"""

import sys
import json
import re
import platform as _platform
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime

# ── Chemins ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent

SCRIPT_CONFIG_FILE = SCRIPT_DIR / 'script_config.json'

def load_script_config() -> dict:
    if SCRIPT_CONFIG_FILE.exists():
        try:
            return json.loads(SCRIPT_CONFIG_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}

def save_script_config(cfg: dict):
    SCRIPT_CONFIG_FILE.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')

def get_vault_root() -> Path:
    """Chemin du vault : detecte automatiquement depuis l'emplacement du script.
    Pour forcer un autre chemin (vault deplace, plusieurs vaults sur la meme
    machine...), ajoute "vault_path" dans _Système/Scripts/script_config.json.

    Exemple (Linux/Mac) :
        { "vault_path": "/home/guillaume/Documents/Obsidian/Lifetrack" }

    Exemple (Windows, utilise des / et pas des \\) :
        { "vault_path": "C:/Users/TonNom/Documents/Obsidian/Lifetrack" }
    """
    cfg = load_script_config()
    if 'vault_path' in cfg:
        p = Path(cfg['vault_path'])
        if p.exists():
            return p
    return SCRIPT_DIR.parent.parent

VAULT_ROOT  = get_vault_root()

def find_tx_dir(vault_root: Path) -> Path:
    """Detecte automatiquement le dossier Transactions selon la structure du vault.
    Compatible avec Second Cerveau (Personnel/Finances/) et Lifetrack (Finances/)."""
    candidates = [
        vault_root / "2 - Domaines" / "Personnel" / "Finances" / "Transactions",
        vault_root / "2 - Domaines" / "Finances" / "Transactions",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # Fallback par defaut

TX_DIR = find_tx_dir(VAULT_ROOT)

# ── Import du parser SG/Revolut ───────────────────────────────────────────────
sys.path.insert(0, str(SCRIPT_DIR))
PARSER_OK = False; PARSER_ERROR = ""
try:
    from parse_finances import parse_sg_pdf, parse_revolut_pdf
    PARSER_OK = True
except Exception as _e:
    PARSER_ERROR = str(_e)

# ── ttkbootstrap (auto-install si absent) ─────────────────────────────────────
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    USE_BS = True
except ImportError:
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                               'ttkbootstrap', '--break-system-packages'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import *
        USE_BS = True
    except Exception:
        from tkinter import ttk
        USE_BS = False


# ═════════════════════════════════════════════════════════════════════════════
# Logique métier - inchangée
# ═════════════════════════════════════════════════════════════════════════════

def detect_pdf_type(filepath: str) -> str:
    disabled = get_disabled_builtins()
    name = Path(filepath).name.lower()
    if 'SG' not in disabled:
        if re.search(r'relevecpte|relevecompte', name) or re.match(r'releve', name):
            return 'sg'
    if 'Revolut' not in disabled:
        if 'account-statement' in name or 'revolut' in name:
            return 'revolut'
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = " ".join((p.extract_text() or "") for p in pdf.pages[:2])
        if 'SG' not in disabled and re.search(r'soci[eé]t[eé]\s*g[eé]n[eé]rale', text, re.I): return 'sg'
        if 'Revolut' not in disabled and 'Revolut' in text: return 'revolut'
        # Vérifier les banques configurées manuellement (ignorer les clés internes _*)
        for bank_name, cfg in load_bank_configs().items():
            if bank_name.startswith('_') or not isinstance(cfg, dict):
                continue
            fp = cfg.get('fingerprint', '')
            if fp and fp.lower() in text.lower():
                return f'custom:{bank_name}'
    except Exception:
        pass
    return 'inconnu'


def load_existing(tx_dir: Path):
    bank_by_year = {}; manual_all = []
    for jf in sorted(tx_dir.glob("💰 *.json")):
        year = jf.stem.replace("💰 ", "").strip()
        try:
            data = json.loads(jf.read_text(encoding='utf-8'))
        except Exception:
            continue
        bank_by_year[year] = [t for t in data if not t.get('_manual')]
        manual_all.extend(t for t in data if t.get('_manual'))
    return bank_by_year, manual_all


def _tx_key(t: dict) -> tuple:
    # Pour les transactions Revolut parsées avec balance_after, on utilise
    # (date, compte, balance_after) comme clé - unique même si le libellé
    # diffère entre deux exports PDF du même compte.
    if 'balance_after' in t:
        return ('bal', t.get('compte', ''), t.get('date', ''),
                str(round(float(t['balance_after']), 2)),
                str(round(float(t.get('montant', 0)), 2)))
    return (t.get('date', ''), t.get('compte', ''),
            str(round(float(t.get('montant', 0)), 2)), t.get('label', ''))


def _soft_key(t: dict) -> tuple:
    """Clé souple (date, compte, montant) - fallback pour comptes sans balance_after.
    Utilisée en dédup secondaire pour absorber les légères variations de libellé
    entre deux exports du même compte (peu importe la banque)."""
    return (t.get('date', ''), t.get('compte', ''),
            str(round(float(t.get('montant', 0)), 2)))


def dedup_new_vs_existing(new_txs: list, bank_by_year: dict):
    from collections import Counter
    all_existing = [t for txs in bank_by_year.values() for t in txs]

    # Clé exacte (inclut balance_after pour Revolut)
    exact_counts = Counter(_tx_key(t) for t in all_existing)
    # Clé souple uniquement pour les transactions sans balance_after
    # (celles avec balance_after ont déjà une clé suffisamment précise)
    soft_counts  = Counter(_soft_key(t) for t in all_existing if 'balance_after' not in t)

    really_new = []; already = []
    for t in new_txs:
        ek = _tx_key(t)
        if exact_counts.get(ek, 0) > 0:
            exact_counts[ek] -= 1
            already.append(t)
        elif 'balance_after' not in t and soft_counts.get(_soft_key(t), 0) > 0:
            # Même date/compte/montant mais libellé légèrement différent - doublon
            soft_counts[_soft_key(t)] -= 1
            already.append(t)
        else:
            really_new.append(t)
    return really_new, already


def find_manual_duplicates(new_txs: list, manual_all: list):
    used = set(); duplicates = []
    for new_tx in new_txs:
        try: nd = datetime.strptime(new_tx['date'], '%Y-%m-%d')
        except Exception: continue
        for i, m_tx in enumerate(manual_all):
            if i in used: continue
            if m_tx.get('compte') != new_tx.get('compte'): continue
            if abs(float(m_tx.get('montant',0)) - float(new_tx.get('montant',0))) > 0.01: continue
            try: md = datetime.strptime(m_tx['date'], '%Y-%m-%d')
            except Exception: continue
            if abs((nd - md).days) <= 3:
                duplicates.append({'new': new_tx, 'manual': m_tx}); used.add(i); break
    return duplicates, [t for i, t in enumerate(manual_all) if i not in used]


def find_recat_candidates(already_here: list, bank_by_year: dict) -> list:
    """
    Parmi les transactions déjà présentes en JSON (already_here),
    détecte celles dont la catégorie aurait changé selon les règles actuelles.
    Chaque élément retourné : {'new_tx': ..., 'stored_tx': ..., 'year': ...}
    'new_tx'     = transaction parsée depuis le PDF (catégorie = règles actuelles)
    'stored_tx'  = transaction stockée en JSON (catégorie = ancienne)
    """
    # Index des transactions auto-importées par clé
    stored_index: dict = {}
    for year, txs in bank_by_year.items():
        for t in txs:
            if not t.get('_manual'):
                k = _tx_key(t)
                stored_index.setdefault(k, []).append((year, t))

    candidates = []
    used: dict = {}
    for new_tx in already_here:
        k = _tx_key(new_tx)
        available = stored_index.get(k, [])
        idx = used.get(k, 0)
        if idx < len(available):
            year, stored_tx = available[idx]
            used[k] = idx + 1
            if new_tx.get('categorie', '') != stored_tx.get('categorie', ''):
                candidates.append({
                    'new_tx':    new_tx,
                    'stored_tx': stored_tx,
                    'year':      year,
                })
    return candidates


def save_import(tx_dir: Path, bank_by_year: dict, new_txs: list, manual_to_keep: list) -> int:
    updated = {y: list(txs) for y, txs in bank_by_year.items()}
    for t in new_txs:
        year = t['date'][:4]
        updated.setdefault(year, []).append({k: v for k, v in t.items() if k != '_manual'})
    manual_by_year: dict = {}
    for t in manual_to_keep:
        year = (t.get('date') or str(datetime.now().year))[:4]
        manual_by_year.setdefault(year, []).append({**t, '_manual': True})
    all_years = sorted(set(list(updated.keys()) + list(manual_by_year.keys())))
    for year in all_years:
        combined = sorted(updated.get(year,[]) + manual_by_year.get(year,[]),
                          key=lambda t: t.get('date',''))
        (tx_dir / f"💰 {year}.json").write_text(
            json.dumps(combined, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(all_years)


# ═════════════════════════════════════════════════════════════════════════════
# Banques génériques - config persistante
# ═════════════════════════════════════════════════════════════════════════════

BANK_CONFIGS_FILE = SCRIPT_DIR / 'bank_configs.json'


def load_bank_configs() -> dict:
    if BANK_CONFIGS_FILE.exists():
        try:
            return json.loads(BANK_CONFIGS_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def save_bank_configs(configs: dict):
    BANK_CONFIGS_FILE.write_text(
        json.dumps(configs, ensure_ascii=False, indent=2), encoding='utf-8')


# ── Règles par défaut extraites de categorize() ───────────────────────────────
# Ordre = priorité (première correspondance gagne).
# Note : les cas crédit/débit ambigus sont résolus en faveur de l'interprétation
# la plus fréquente. Les règles spéciales (montants fixes du prêt, IBAN Revolut)
# restent gérées par la logique hardcodée en fallback.
DEFAULT_BUILTIN_RULES: dict[str, list] = {
    'SG': [
        {'keywords': 'REMBT',
         'categorie': '🔙 Avoir / Remboursement achat', 'direction': 'crédit'},
        {'keywords': 'AVANTAGECOMMERCIAL, REGULARISATIONDECOMMISSION, REMISECHEQUE',
         'categorie': '🔙 Avoir / Remboursement achat', 'direction': 'crédit'},
        {'keywords': 'REMBOURSEMENTVIREMENT',
         'categorie': '🔄 Transfert interne in', 'direction': 'crédit'},
        {'keywords': 'POCKET, SAVING',
         'categorie': '💸 Retrait économies', 'direction': 'crédit'},
        {'keywords': 'POCKET, SAVING',
         'categorie': '💰 Économies', 'direction': 'débit'},
        {'keywords': 'CAF, CAISSEALLOCATION, DROITSFAMILLE, BOURSE, CROUS, DRFIP, ACADEMIE, ENSEIGNEMENTSUP',
         'categorie': '🎓 Bourse & Aides sociales', 'direction': 'crédit'},
        {'keywords': 'SALAIRE, PAYE, TRAITEMENT',
         'categorie': '💼 Salaire', 'direction': 'crédit'},
        {'keywords': 'VRSTGAB, VERSTESPGAB, OPENBANKING, DEPOSIT',
         'categorie': '💵 Dépôt espèces', 'direction': 'crédit'},
        {'keywords': 'VINTED, BACKMARKET, MGP, MANGOPAY, XPOLLENS',
         'categorie': '💰 Revenus divers', 'direction': 'crédit'},
        {'keywords': 'ALPIQ, EDF, ENGIE',
         'categorie': '🏠 Loyer & Charges', 'direction': 'débit'},
        {'keywords': 'PRELEVEMENT',
         'categorie': '🏠 Loyer & Charges', 'direction': 'débit'},
        {'keywords': 'MUTUELLE, PHARMAC',
         'categorie': '🏥 Santé', 'direction': 'débit'},
        {'keywords': 'NETFLIX, SPOTIFY, CRUNCHYROLL, LASTPASS, CYBERGHOST, CLAUDE, ANTHROPIC, APPLE, UBERONE, AMAZONPRIME',
         'categorie': '📺 Abonnements', 'direction': 'débit'},
        {'keywords': 'SNCF, RATP, BLABLACAR, FLIXBUS, TRANSAVIA, EASYJET, RYANAIR, AIRFRANCE',
         'categorie': '🚗 Transport', 'direction': 'débit'},
        {'keywords': 'LECLERC, CARREFOUR, LIDL, ALDI, INTERMARCHE, MONOPRIX, SUPERU, AUCHAN, UBEREATS, DELIVEROO, MCDONALD, KFC, BURGERKING',
         'categorie': '🛒 Alimentation', 'direction': 'débit'},
        {'keywords': 'RETRAITDAB, RETRAITGAB',
         'categorie': '🏧 Retrait espèces', 'direction': 'débit'},
        {'keywords': 'GOOGLEPLAY, XSOLLA, INSTANTGAMING, STEAMPURCHASE, STEAM, DOKKANBATTLE, SUPERCELL, PAYSAFECARD, NINTENDO, SONYINTERACT, CGR, PATHE, UGC',
         'categorie': '🎮 Loisirs & Jeux', 'direction': 'débit'},
        {'keywords': 'AMAZON, VINTED, MGP, BACKMARKET, LDLC, RHINOSHIELD, PAYPAL',
         'categorie': '🛍️ Shopping', 'direction': 'débit'},
        {'keywords': 'TREATWELL',
         'categorie': '💇 Coiffure & Beauté', 'direction': 'débit'},
        {'keywords': 'COTISATIONMENS, COTISANNU, FRAISVIRINSTANT, FRAISPAIEMENT',
         'categorie': '💳 Frais bancaires', 'direction': 'débit'},
        {'keywords': 'ORANGEMONEY, TRANSFERWISE, VIRINSTANTANEE, VIREUROPEEN, PAYLIB',
         'categorie': '💸 Envoi d\'argent', 'direction': 'débit'},
    ],
    'Revolut': [
        {'keywords': 'REVOLUTPREMIUM, REVOLUTPLUS, REVOLUTMETAL, REVOLUTULTRA, REVOLUTSTANDARD',
         'categorie': '📺 Abonnements', 'direction': 'débit'},
        {'keywords': 'POCKET, SAVING',
         'categorie': '💸 Retrait économies', 'direction': 'crédit'},
        {'keywords': 'POCKET, SAVING',
         'categorie': '💰 Économies', 'direction': 'débit'},
        {'keywords': 'CAF, CAISSEALLOCATION, BOURSE, CROUS, DRFIP',
         'categorie': '🎓 Bourse & Aides sociales', 'direction': 'crédit'},
        {'keywords': 'SALAIRE, PAYE',
         'categorie': '💼 Salaire', 'direction': 'crédit'},
        {'keywords': 'CASHBACK, REFUND',
         'categorie': '🔙 Avoir / Remboursement achat', 'direction': 'crédit'},
        {'keywords': 'VINTED, BACKMARKET',
         'categorie': '💰 Revenus divers', 'direction': 'crédit'},
        {'keywords': 'ALPIQ, EDF, ENGIE',
         'categorie': '🏠 Loyer & Charges', 'direction': 'débit'},
        {'keywords': 'MUTUELLE, PHARMAC',
         'categorie': '🏥 Santé', 'direction': 'débit'},
        {'keywords': 'NETFLIX, SPOTIFY, CRUNCHYROLL, LASTPASS, CYBERGHOST, CLAUDE, ANTHROPIC, UBERONE, AMAZONPRIME',
         'categorie': '📺 Abonnements', 'direction': 'débit'},
        {'keywords': 'SNCF, RATP, UBER, BLABLACAR, FLIXBUS, TRANSAVIA, EASYJET, RYANAIR',
         'categorie': '🚗 Transport', 'direction': 'débit'},
        {'keywords': 'LECLERC, CARREFOUR, LIDL, ALDI, INTERMARCHE, MONOPRIX, AUCHAN, UBEREATS, DELIVEROO, MCDONALD, KFC, BURGERKING',
         'categorie': '🛒 Alimentation', 'direction': 'débit'},
        {'keywords': 'ATM, WITHDRAWAL',
         'categorie': '🏧 Retrait espèces', 'direction': 'débit'},
        {'keywords': 'STEAM, NINTENDO, PLAYSTATION, GAMING',
         'categorie': '🎮 Loisirs & Jeux', 'direction': 'débit'},
        {'keywords': 'AMAZON, VINTED, BACKMARKET, LDLC, PAYPAL',
         'categorie': '🛍️ Shopping', 'direction': 'débit'},
        {'keywords': 'FEE',
         'categorie': '💳 Frais bancaires', 'direction': 'débit'},
        {'keywords': 'TRANSFERWISE, ORANGEMONEY',
         'categorie': '💸 Envoi d\'argent', 'direction': 'débit'},
    ],
}


# Toutes les catégories connues du système - toujours disponibles dans les menus
KNOWN_CATEGORIES: list = sorted({
    '❓ Autre',
    '🎓 Bourse & Aides sociales',
    '💰 Économies',
    '💰 Revenus divers',
    '💵 Dépôt espèces',
    '💼 Salaire',
    '🔙 Avoir / Remboursement achat',
    '💸 Envoi d\'argent',
    '💸 Retrait économies',
    '🔄 Transfert interne in',
    '🔄 Transfert interne out',
    '🏠 Loyer & Charges',
    '🏧 Retrait espèces',
    '🏥 Santé',
    '📺 Abonnements',
    '🎮 Loisirs & Jeux',
    '🛒 Alimentation',
    '🛍️ Shopping',
    '💇 Coiffure & Beauté',
    '💳 Frais bancaires',
    '🚗 Transport',
})

def load_categories_from_json(tx_dir: Path) -> list:
    """Retourne toutes les catégories connues + celles présentes dans les JSON de transactions."""
    cats: set = set(KNOWN_CATEGORIES)
    if tx_dir.exists():
        for jf in tx_dir.glob('💰 *.json'):
            try:
                data = json.loads(jf.read_text(encoding='utf-8'))
                cats.update(t['categorie'] for t in data if t.get('categorie'))
            except Exception:
                pass
    return sorted(cats)


CATEGORY_TYPES = {
    '🎓 Bourse & Aides sociales':     'revenu',
    '💰 Revenus divers':               'revenu',
    '💵 Dépôt espèces':                'revenu',
    '💵 Revenus divers':               'revenu',
    '💵 Remboursement in':             'revenu',
    '💼 Salaire':                      'revenu',
    '🔙 Avoir / Remboursement achat':  'avoir',
    '💰 Économies':                    'épargne',
    '💸 Retrait économies':            'épargne-retrait',
    '🔄 Transfert interne in':         'revenu',
    '🔄 Transfert interne out':        'dépense',
}

def get_category_type(cat: str) -> str:
    return CATEGORY_TYPES.get(cat, 'dépense')


def apply_categorization_rules_to_tx(label: str, rules: list, is_credit: bool = None) -> tuple:
    """Applique les règles utilisateur à un label.
    is_credit=True/False filtre les règles par direction. None = pas de filtre.
    Retourne (categorie, type)."""
    ctx = re.sub(r'\s+', '', label.upper())
    for rule in rules:
        direction = rule.get('direction', 'tous')
        if direction == 'crédit' and is_credit is False:
            continue
        if direction == 'débit' and is_credit is True:
            continue
        kws = [k.strip().upper().replace(' ', '')
               for k in rule.get('keywords', '').split(',') if k.strip()]
        if kws and any(kw in ctx for kw in kws):
            cat = rule.get('categorie', '❓ Autre')
            return cat, get_category_type(cat)
    return '❓ Autre', 'dépense'


def get_builtin_rules(name: str) -> list:
    return load_bank_configs().get('_builtin_rules', {}).get(name, [])


def set_builtin_rules(name: str, rules: list):
    configs = load_bank_configs()
    configs.setdefault('_builtin_rules', {})[name] = rules
    save_bank_configs(configs)


def get_disabled_builtins() -> list:
    return load_bank_configs().get('_disabled_builtins', [])


def set_builtin_disabled(name: str, disabled: bool):
    configs = load_bank_configs()
    lst = configs.get('_disabled_builtins', [])
    if disabled and name not in lst:
        lst.append(name)
    elif not disabled and name in lst:
        lst.remove(name)
    configs['_disabled_builtins'] = lst
    save_bank_configs(configs)


def parse_amount_generic(s: str):
    """Parse un montant FR/EN, positif/négatif. Retourne float ou None."""
    if not s:
        return None
    s = s.strip().replace('\xa0', '').replace(' ', '').replace(' ', '')
    negative = False
    if s.startswith('(') and s.endswith(')'):
        negative = True; s = s[1:-1]
    if s.startswith('-'):
        negative = True; s = s[1:]
    elif s.startswith('+'):
        s = s[1:]
    # Format FR "1 234,56" ou "1234,56"
    if ',' in s and '.' not in s:
        s = s.replace(',', '.')
    elif ',' in s and '.' in s:
        if s.index('.') < s.index(','):   # EN: "1,234.56"
            s = s.replace(',', '')
        else:                              # FR: "1.234,56"
            s = s.replace('.', '').replace(',', '.')
    s = re.sub(r'[€$£\s]', '', s)
    try:
        v = float(s)
        return -v if negative else v
    except ValueError:
        return None


def extract_pdf_preview(filepath: str) -> list:
    """Extrait les tables des 3 premières pages pour prévisualisation."""
    try:
        import pdfplumber
        tables = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                for tbl in (page.extract_tables() or []):
                    if tbl and len(tbl) >= 2:
                        clean = [[str(c or '').strip() for c in row] for row in tbl]
                        tables.append(clean)
        return tables
    except Exception:
        return []


def parse_generic_pdf(filepath: str, config: dict) -> list:
    """Parse un PDF bancaire générique selon une config de mapping de colonnes."""
    import pdfplumber
    col_date    = config['col_date']
    col_label   = config['col_label']
    col_montant = config.get('col_montant')
    col_debit   = config.get('col_debit')
    col_credit  = config.get('col_credit')
    date_fmt    = config.get('date_format', '%d/%m/%Y')
    compte      = config.get('compte', config.get('name', 'Banque'))
    header_rows = config.get('header_rows', 1)

    transactions = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            for tbl in (page.extract_tables() or []):
                for row_idx, row in enumerate(tbl):
                    if row_idx < header_rows or not row:
                        continue
                    try:
                        date_str = str(row[col_date] or '').strip()
                        if not date_str:
                            continue
                        date = datetime.strptime(date_str, date_fmt)
                        label = ' '.join(str(row[col_label] or '').split())
                        if not label:
                            continue
                        if col_montant is not None:
                            montant = parse_amount_generic(str(row[col_montant] or ''))
                        else:
                            d = parse_amount_generic(str(row[col_debit]  or '')) if col_debit  is not None else None
                            c = parse_amount_generic(str(row[col_credit] or '')) if col_credit is not None else None
                            if d:   montant = -abs(d)
                            elif c: montant = abs(c)
                            else:   continue
                        if montant is None:
                            continue
                        rules = config.get('rules', [])
                        is_credit = montant > 0
                        cat, typ = apply_categorization_rules_to_tx(label, rules, is_credit=is_credit) if rules else ('❓ Autre', 'dépense')
                        transactions.append({
                            'date':      date.strftime('%Y-%m-%d'),
                            'label':     label,
                            'montant':   round(montant, 2),
                            'categorie': cat,
                            'type':      typ,
                            'compte':    compte,
                        })
                    except (ValueError, IndexError, TypeError):
                        continue
    return sorted(transactions, key=lambda t: t['date'])


# ═════════════════════════════════════════════════════════════════════════════
# Interface graphique - redesign ttkbootstrap
# ═════════════════════════════════════════════════════════════════════════════

# Palette de couleurs
CLR = {
    'header_bg':  '#1e293b',
    'header_fg':  '#f1f5f9',
    'header_sub': '#94a3b8',
    'card_bg':    '#ffffff',
    'page_bg':    '#f1f5f9',
    'border':     '#e2e8f0',
    'primary':    '#2563eb',
    'success':    '#16a34a',
    'warning':    '#d97706',
    'danger':     '#dc2626',
    'muted':      '#64748b',
    'text':       '#0f172a',
    # badges type PDF
    'sg_fg':      '#0891b2', 'sg_bg':      '#cffafe',
    'rev_fg':     '#7c3aed', 'rev_bg':     '#ede9fe',
    'unk_fg':     '#374151', 'unk_bg':     '#f3f4f6',
}

def _fmt_montant(m: float) -> str:
    return f"{m:+.2f} €"

def _pill(parent, text, fg, bg, font_size=8):
    """Petit badge coloré arrondi (simulé avec un Label padded)."""
    lbl = tk.Label(parent, text=text, fg=fg, bg=bg,
                   font=('Segoe UI', font_size, 'bold'),
                   padx=7, pady=2)
    return lbl


# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires UI - DPI, police, centrage fenêtres, scroll, combobox
# ══════════════════════════════════════════════════════════════════════════════

def setup_dpi_awareness():
    """Windows : active la conscience DPI avant création de la fenêtre principale."""
    if _platform.system() == 'Windows':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)   # Per-Monitor DPI Aware
        except Exception:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()    # fallback Windows 7
            except Exception:
                pass


def apply_dpi_scaling(root: tk.Tk):
    """Règle le facteur d'échelle tkinter selon le DPI réel de l'écran."""
    try:
        dpi = root.winfo_fpixels('1i')   # pixels per inch
        scale = dpi / 72.0               # tkinter scaling unit = points per pixel
        if scale > 0.5:
            root.tk.call('tk', 'scaling', scale)
    except Exception:
        pass


def detect_font_family() -> str:
    """Détecte la meilleure police UI disponible sur le système."""
    try:
        import tkinter.font as tkfont
        available = set(tkfont.families())
        for f in ['Segoe UI', 'Ubuntu', 'Cantarell', 'DejaVu Sans',
                  'Helvetica Neue', 'Helvetica', 'Arial']:
            if f in available:
                return f
    except Exception:
        pass
    return 'TkDefaultFont'


# Police UI - mise à jour dans ImportApp.__init__() après création de la fenêtre
_UI_FONT: list = ['Segoe UI']

def F(size: int = 9, weight: str = 'normal') -> tuple:
    """Retourne un tuple font avec la famille détectée au runtime."""
    return (_UI_FONT[0], size, weight)


def center_window(win: tk.Toplevel, width: int, height: int):
    """Centre une fenêtre Toplevel sur l'écran."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = max(0, (sw - width) // 2)
    y = max(0, (sh - height) // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')


def fit_and_center(win: tk.Toplevel, min_w: int = 400, min_h: int = 300,
                   max_w_pct: float = 0.88, max_h_pct: float = 0.82):
    """Auto-dimensionne et centre une fenêtre selon son contenu et l'écran."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    rw = win.winfo_reqwidth()
    rh = win.winfo_reqheight()
    w  = max(min_w, min(rw + 40, int(sw * max_w_pct)))
    h  = max(min_h, min(rh + 40, int(sh * max_h_pct)))
    x  = max(0, (sw - w) // 2)
    y  = max(0, (sh - h) // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')


def _activate_canvas_scroll(canvas: tk.Canvas):
    """Active le scroll souris sur le canvas (bind_all, scope réduit via Enter/Leave)."""
    if _platform.system() == 'Windows':
        canvas.bind_all('<MouseWheel>',
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))
    else:
        canvas.bind_all('<Button-4>', lambda e: canvas.yview_scroll(-1, 'units'))
        canvas.bind_all('<Button-5>', lambda e: canvas.yview_scroll(1,  'units'))


def _deactivate_canvas_scroll(canvas: tk.Canvas):
    """Retire les bindings scroll du canvas."""
    if _platform.system() == 'Windows':
        canvas.unbind_all('<MouseWheel>')
    else:
        canvas.unbind_all('<Button-4>')
        canvas.unbind_all('<Button-5>')


def bind_canvas_scroll(canvas: tk.Canvas, *extra_enter_widgets):
    """
    Active le scroll uniquement quand la souris est dans la zone du canvas.
    Passer les widgets supplémentaires (ex: la frame interne) pour étendre la zone.
    """
    enter = lambda e: _activate_canvas_scroll(canvas)
    leave = lambda e: _deactivate_canvas_scroll(canvas)
    canvas.bind('<Enter>', enter)
    canvas.bind('<Leave>', leave)
    for w in extra_enter_widgets:
        try:
            w.bind('<Enter>', enter)
            w.bind('<Leave>', leave)
        except Exception:
            pass


def mk_combobox(parent, **kwargs) -> 'ttk.Combobox':
    """
    Crée un Combobox sans réaction au scroll souris.
    Prévient les changements accidentels lors du scroll de la liste parente.
    Nécessite un clic pour ouvrir / changer la valeur.
    """
    cb = ttk.Combobox(parent, **kwargs)
    cb.bind('<MouseWheel>', lambda e: 'break')
    cb.bind('<Button-4>',   lambda e: 'break')
    cb.bind('<Button-5>',   lambda e: 'break')
    return cb


_DIR_LABELS = ['Tous', 'Crédit ↑', 'Débit ↓']
_DIR_TO_LABEL = {'tous': 'Tous', 'crédit': 'Crédit ↑', 'débit': 'Débit ↓'}
_LABEL_TO_DIR = {'Tous': 'tous', 'Crédit ↑': 'crédit', 'Débit ↓': 'débit'}


class CategorizationRulesDialog(tk.Toplevel):
    """
    Fenêtre modale pour configurer les règles de catégorisation d'une banque.
    Chaque règle : mots-clés (séparés par virgule) → catégorie + direction crédit/débit.
    Les catégories sont chargées depuis les fichiers JSON de transactions.
    """

    # Largeurs de colonnes en pixels - uniformes entre en-têtes et lignes
    _W_HANDLE = 55    # numéro + boutons ▲▼
    _W_KW     = 560   # mots-clés (libellés longs)
    _W_CAT    = 340   # catégories (emojis + texte)
    _W_DIR    = 115   # direction
    _W_DEL    = 28
    _GAP      = 10    # espacement inter-colonnes
    _ROW_PAD  = 12    # padx du cadre intérieur de chaque ligne

    def __init__(self, parent, bank_name: str, rules: list, categories: list,
                 suggested_labels: list = None):
        super().__init__(parent)
        self.bank_name        = bank_name
        self.rules            = [dict(r) for r in rules]   # copie
        self.categories       = categories
        self.suggested_labels = suggested_labels or []
        self.result           = None   # liste de règles si validé, None si annulé
        self.rows: list       = []     # list of dicts {kw, cat, dir, frame}
        self._canvas          = None   # référence canvas pour scroll

        self.title(f"Règles de catégorisation - {bank_name}")
        self.resizable(True, True)
        self.minsize(900, 520)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()
        self._build()
        self.transient(parent)
        # Taille = 82% de l'écran (garantit que les colonnes sont lisibles)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = max(900, int(sw * 0.82))
        h  = max(520, int(sh * 0.80))
        center_window(self, w, h)
        self.wait_window()

    def _col_frame(self, parent, width: int, bg: str, height: int = 28) -> tk.Frame:
        """Cadre de largeur et hauteur fixes pour aligner les colonnes."""
        f = tk.Frame(parent, width=width, height=height, bg=bg)
        f.pack_propagate(False)
        return f

    def _build_header_row(self, outer_bg: str = '#f8fafc'):
        """Construit la ligne d'en-têtes dans le même conteneur que les règles."""
        hdr = tk.Frame(self._header_host, bg=outer_bg, pady=5)
        hdr.pack(fill='x')
        inner = tk.Frame(hdr, bg=outer_bg)
        inner.pack(fill='x', padx=self._ROW_PAD)

        # En-tête colonne numéro / ordre
        sp = self._col_frame(inner, self._W_HANDLE, outer_bg, height=22)
        sp.pack(side='left', padx=(0, self._GAP))
        tk.Label(sp, text='N°', bg=outer_bg, fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold'), anchor='center').pack(fill='both')

        # Mots-clés
        f = self._col_frame(inner, self._W_KW, outer_bg, height=22)
        f.pack(side='left', padx=(0, self._GAP))
        tk.Label(f, text='Mots-clés (séparés par virgule)',
                 bg=outer_bg, fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold'), anchor='w').pack(fill='both')

        # Catégorie
        f = self._col_frame(inner, self._W_CAT, outer_bg, height=22)
        f.pack(side='left', padx=(0, self._GAP))
        tk.Label(f, text='Catégorie',
                 bg=outer_bg, fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold'), anchor='w').pack(fill='both')

        # Direction
        f = self._col_frame(inner, self._W_DIR, outer_bg, height=22)
        f.pack(side='left')
        tk.Label(f, text='Direction',
                 bg=outer_bg, fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold'), anchor='w').pack(fill='both')

        tk.Frame(self._header_host, bg=CLR['border'], height=1).pack(fill='x')

    def _build(self):
        # ── Header bleu ───────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=10)
        hdr.pack(fill='x')
        tk.Label(hdr, text=f"📋  Règles de catégorisation - {self.bank_name}",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 11, 'bold')).pack()
        tk.Label(hdr,
                 text="Les règles sont vérifiées dans l'ordre. La première correspondance gagne.\n"
                      "Pour SG et Revolut, les règles s'appliquent AVANT la logique automatique.",
                 bg=CLR['header_bg'], fg=CLR['header_sub'],
                 font=('Segoe UI', 8), justify='center').pack(pady=(2, 0))

        # ── Zone centrale avec bordure ─────────────────────────────────────────
        outer = tk.Frame(self, bg=CLR['border'], pady=1, padx=1)
        outer.pack(fill='both', expand=True, padx=16, pady=4)
        inner_bg = tk.Frame(outer, bg=CLR['card_bg'])
        inner_bg.pack(fill='both', expand=True)

        # En-têtes colonnes (non-scrollable, même conteneur que les lignes)
        self._header_host = inner_bg
        self._build_header_row()

        # Canvas scrollable
        canvas = tk.Canvas(inner_bg, bg=CLR['card_bg'], highlightthickness=0)
        sb = ttk.Scrollbar(inner_bg, orient='vertical', command=canvas.yview)
        self._rules_frame = tk.Frame(canvas, bg=CLR['card_bg'])
        self._rules_frame.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        win_id = canvas.create_window((0, 0), window=self._rules_frame, anchor='nw')
        canvas.bind('<Configure>',
            lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        self._canvas = canvas

        # Dialog modale (grab_set) → scroll actif en permanence le temps de son ouverture.
        # Les mk_combobox bloquent le scroll sur eux-mêmes avec return 'break'.
        _activate_canvas_scroll(canvas)
        self.bind('<Destroy>', lambda e: _deactivate_canvas_scroll(canvas))

        # ── Bannière libellés suggérés ─────────────────────────────────────────
        if self.suggested_labels:
            n_sug = len(self.suggested_labels)
            sug_frm = tk.Frame(self, bg='#eff6ff', pady=6, padx=14)
            sug_frm.pack(fill='x', padx=16, pady=(0, 2))
            tk.Label(sug_frm,
                     text=f'💡  {n_sug} libellé{"s" if n_sug!=1 else ""} détecté{"s" if n_sug!=1 else ""} dans le PDF.',
                     bg='#eff6ff', fg='#1e40af',
                     font=('Segoe UI', 9, 'bold')).pack(side='left')
            btn_txt = ('Pré-remplir les règles' if not self.rules
                       else 'Ajouter les libellés non couverts')
            tk.Button(sug_frm, text=f'  ＋  {btn_txt}',
                      bg=CLR['primary'], fg='#ffffff',
                      font=('Segoe UI', 8, 'bold'), relief='flat', bd=0,
                      cursor='hand2', padx=10, pady=3,
                      command=self._import_suggestions).pack(side='left', padx=(12, 0))
            tk.Label(sug_frm,
                     text='Les mots-clés sont pré-remplis - raccourcissez-les si besoin.',
                     bg='#eff6ff', fg='#3b82f6',
                     font=('Segoe UI', 7, 'italic')).pack(side='left', padx=8)

        # ── Bouton ajouter ─────────────────────────────────────────────────────
        add_frm = tk.Frame(self, bg=CLR['page_bg'], pady=6)
        add_frm.pack(fill='x', padx=16)
        tk.Button(add_frm, text='＋  Ajouter une règle',
                  bg=CLR['border'], fg=CLR['text'],
                  font=('Segoe UI', 9), relief='solid', bd=1,
                  cursor='hand2', padx=10, pady=4,
                  command=self._add_row).pack(side='left')
        tk.Label(add_frm,
                 text='Les mots-clés sont insensibles à la casse et aux espaces.',
                 bg=CLR['page_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 7, 'italic')).pack(side='left', padx=10)

        # ── Zone avertissement conflits (position fixée ici, contenu mis à jour dynamiquement)
        self._warn_frm = tk.Frame(self, bg='#fffbeb')
        self._warn_frm.pack(fill='x', padx=16, pady=0)
        self._warn_lbl = tk.Label(self._warn_frm,
                                  bg='#fffbeb', fg='#92400e',
                                  font=('Segoe UI', 8), justify='left',
                                  anchor='w', wraplength=900)
        # (label packé/dépacké dynamiquement dans _refresh_conflicts)

        # ── Barre boutons ──────────────────────────────────────────────────────
        tk.Frame(self, bg=CLR['border'], height=1).pack(fill='x')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x')
        tk.Button(bar, text='Annuler',
                  bg=CLR['border'], fg=CLR['text'],
                  font=('Segoe UI', 9, 'bold'), relief='solid', bd=1,
                  cursor='hand2', padx=12, pady=6,
                  command=self.destroy).pack(side='right', padx=(8, 0))
        tk.Button(bar, text='💾  Enregistrer',
                  bg=CLR['success'], fg='#ffffff',
                  font=('Segoe UI', 9, 'bold'), relief='flat', bd=0,
                  cursor='hand2', padx=12, pady=6,
                  command=self._save).pack(side='right')

        # ── Peupler avec les règles existantes ────────────────────────────────
        for rule in self.rules:
            self._add_row(rule.get('keywords', ''), rule.get('categorie', '❓ Autre'),
                          rule.get('direction', 'tous'))
        # Si aucune règle et des libellés suggérés : pré-remplir automatiquement
        if not self.rules:
            if self.suggested_labels:
                for label in self.suggested_labels:
                    self._add_row(keywords=label)
            else:
                self._add_row()
        self._update_row_numbers()
        self._refresh_conflicts()

    def _update_row_numbers(self):
        """Met à jour les numéros pour toutes les lignes."""
        for i, rd in enumerate(self.rows):
            if rd.get('num_lbl'):
                rd['num_lbl'].config(text=str(i + 1))

    # ── Drag & drop ─────────────────────────────────────────────────────────

    def _drag_start(self, event, row_data):
        self._drag_row = row_data
        if row_data.get('drag_lbl'):
            row_data['drag_lbl'].config(fg=CLR['primary'])

    def _drag_motion(self, event):
        rd = getattr(self, '_drag_row', None)
        if rd is None:
            return
        root_y = event.widget.winfo_rooty() + event.y
        src_idx = self.rows.index(rd)
        for i, other in enumerate(self.rows):
            f = other['frame']
            top = f.winfo_rooty()
            bot = top + f.winfo_height()
            if i != src_idx and top <= root_y < bot:
                direction = 1 if i > src_idx else -1
                self._move_row(rd, direction)
                break

    def _drag_end(self, event):
        rd = getattr(self, '_drag_row', None)
        if rd and rd.get('drag_lbl'):
            rd['drag_lbl'].config(fg=CLR['muted'])
        self._drag_row = None

    def _move_row(self, row_data: dict, direction: int):
        """Déplace une règle vers le haut (direction=-1) ou le bas (+1)."""
        idx = self.rows.index(row_data)
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.rows):
            return
        # Swap dans la liste
        self.rows[idx], self.rows[new_idx] = self.rows[new_idx], self.rows[idx]
        # Repack le frame déplacé dans le bon ordre tkinter
        displaced_frame = self.rows[idx]['frame']   # l'autre frame (après swap)
        if direction == -1:   # monter : se placer avant l'autre
            row_data['frame'].pack(before=displaced_frame)
        else:                 # descendre : se placer après l'autre
            row_data['frame'].pack(after=displaced_frame)
        self._update_row_numbers()
        self._refresh_conflicts()

    def _refresh_conflicts(self, *_):
        """Détecte les mots-clés généraux qui masquent des mots-clés plus spécifiques
        situés plus bas dans la liste, et met à jour la bannière d'avertissement."""
        def norm(s):
            return s.strip().upper().replace(' ', '')

        # Construire la liste (index, [(kw_normalisé, kw_original), ...])
        rows_kws = []
        for rd in self.rows:
            kws = [(norm(k), k.strip()) for k in rd['kw'].get().split(',') if k.strip()]
            rows_kws.append(kws)

        conflicts = []
        for i, kws_i in enumerate(rows_kws):
            for kw_norm_i, kw_raw_i in kws_i:
                if not kw_norm_i:
                    continue
                for j in range(i + 1, len(rows_kws)):
                    for kw_norm_j, kw_raw_j in rows_kws[j]:
                        if not kw_norm_j:
                            continue
                        # kw_i (règle haute) est sous-chaîne de kw_j (règle basse)
                        # → règle i masque règle j pour les libellés contenant kw_j
                        if kw_norm_i in kw_norm_j and kw_norm_i != kw_norm_j:
                            conflicts.append(
                                f"⚠️  « {kw_raw_i} » (règle {i+1}) masque « {kw_raw_j} »"
                                f" (règle {j+1}) - placez la règle {j+1} au-dessus."
                            )

        if conflicts:
            self._warn_lbl.config(text='\n'.join(conflicts))
            self._warn_lbl.pack(fill='x', padx=14, pady=6)
        else:
            self._warn_lbl.pack_forget()

    def _import_suggestions(self):
        """Ajoute les libellés suggérés non encore couverts par une règle existante."""
        # Construire l'ensemble des mots-clés déjà définis (en majuscules, sans espaces)
        covered = set()
        for rd in self.rows:
            for kw in rd['kw'].get().split(','):
                covered.add(kw.strip().upper().replace(' ', ''))

        added = 0
        for label in self.suggested_labels:
            label_ctx = label.upper().replace(' ', '')
            # Ne pas ajouter si déjà couvert par un mot-clé existant
            if any(kw and kw in label_ctx for kw in covered):
                continue
            self._add_row(keywords=label)
            covered.add(label_ctx)
            added += 1

        if added == 0:
            tk.messagebox.showinfo('Libellés',
                'Tous les libellés sont déjà couverts par les règles existantes.')

    def _add_row(self, keywords: str = '', categorie: str = '❓ Autre', direction: str = 'tous'):
        kw_var  = tk.StringVar(value=keywords)
        # S'assurer que la catégorie est dans la liste (même si elle n'existe plus dans les JSON)
        cats = list(self.categories)
        if categorie and categorie not in cats:
            cats.insert(0, categorie)
        cat_var = tk.StringVar(value=categorie if categorie in cats else (cats[0] if cats else '❓ Autre'))
        dir_var = tk.StringVar(value=_DIR_TO_LABEL.get(direction, 'Tous'))

        row_data: dict = {'kw': kw_var, 'cat': cat_var, 'dir': dir_var, 'frame': None,
                          'num_lbl': None, 'drag_lbl': None}
        kw_var.trace_add('write', self._refresh_conflicts)

        container = tk.Frame(self._rules_frame, bg=CLR['card_bg'])
        container.pack(fill='x')
        row_data['frame'] = container

        # Ligne intérieure avec le même padx que l'en-tête → colonnes parfaitement alignées
        inner = tk.Frame(container, bg=CLR['card_bg'], pady=4)
        inner.pack(fill='x', padx=self._ROW_PAD)

        # ── Numéro + poignée de glissement ─────────────────────────────────
        hf = self._col_frame(inner, self._W_HANDLE, CLR['card_bg'])
        hf.pack(side='left', padx=(0, self._GAP))
        num_lbl = tk.Label(hf, text='', bg=CLR['card_bg'], fg=CLR['muted'],
                           font=('Segoe UI', 8, 'bold'), width=2, anchor='e')
        num_lbl.pack(side='left')
        drag_lbl = tk.Label(hf, text='⠿', bg=CLR['card_bg'], fg=CLR['muted'],
                            font=('Segoe UI', 11), cursor='fleur', padx=3)
        drag_lbl.pack(side='left', fill='both', expand=True)
        drag_lbl.bind('<ButtonPress-1>',   lambda e, rd=row_data: self._drag_start(e, rd))
        drag_lbl.bind('<B1-Motion>',       self._drag_motion)
        drag_lbl.bind('<ButtonRelease-1>', self._drag_end)
        row_data['num_lbl']  = num_lbl
        row_data['drag_lbl'] = drag_lbl

        # ── Mots-clés ───────────────────────────────────────────────────────
        kf = self._col_frame(inner, self._W_KW, CLR['card_bg'])
        kf.pack(side='left', padx=(0, self._GAP))
        tk.Entry(kf, textvariable=kw_var,
                 font=('Segoe UI', 9)).pack(fill='both', expand=True, ipady=2)

        # ── Catégorie ───────────────────────────────────────────────────────
        cf = self._col_frame(inner, self._W_CAT, CLR['card_bg'])
        cf.pack(side='left', padx=(0, self._GAP))
        mk_combobox(cf, textvariable=cat_var, values=cats,
                    state='readonly',
                    font=('Segoe UI', 9)).pack(fill='both', expand=True)

        # ── Direction ───────────────────────────────────────────────────────
        df = self._col_frame(inner, self._W_DIR, CLR['card_bg'])
        df.pack(side='left', padx=(0, self._GAP))
        mk_combobox(df, textvariable=dir_var, values=_DIR_LABELS,
                    state='readonly',
                    font=('Segoe UI', 9)).pack(fill='both', expand=True)

        # ── Supprimer ───────────────────────────────────────────────────────
        def del_row(rd=row_data):
            rd['frame'].destroy()
            if rd in self.rows:
                self.rows.remove(rd)
            self._update_row_numbers()
            self._refresh_conflicts()

        tk.Button(inner, text='✕',
                  bg=CLR['card_bg'], fg=CLR['danger'],
                  font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                  cursor='hand2', padx=4, pady=1,
                  command=del_row).pack(side='left', anchor='center')

        tk.Frame(container, bg=CLR['border'], height=1).pack(fill='x')
        self.rows.append(row_data)
        self._update_row_numbers()

    def _save(self):
        rules = []
        for rd in self.rows:
            kw  = rd['kw'].get().strip()
            cat = rd['cat'].get().strip()
            direction = _LABEL_TO_DIR.get(rd['dir'].get(), 'tous')
            if kw and cat:
                rules.append({'keywords': kw, 'categorie': cat, 'direction': direction})
        self.result = rules
        self.destroy()


class BankSetupDialog(tk.Toplevel):
    """
    Fenêtre modale pour configurer une nouvelle banque.
    Affiche la table extraite du PDF, permet de mapper les colonnes,
    et sauvegarde la config dans bank_configs.json.
    """

    DATE_FORMATS = [
        ('%d/%m/%Y',  '31/12/2024'),
        ('%d/%m/%y',  '31/12/24'),
        ('%Y-%m-%d',  '2024-12-31'),
        ('%d-%m-%Y',  '31-12-2024'),
        ('%d.%m.%Y',  '31.12.2024'),
        ('%m/%d/%Y',  '12/31/2024'),
    ]
    COL_ROLES = ['Ignorer', 'Date', 'Libellé', 'Montant (+/-)', 'Débit (négatif)', 'Crédit (positif)']

    def __init__(self, parent, filepath: str):
        super().__init__(parent)
        self.filepath  = filepath
        self.result    = None        # dict config si validé, None si annulé
        self.col_roles: list = []    # tk.StringVar par colonne

        self.title(f"Nouvelle banque - {Path(filepath).name}")
        self.resizable(True, True)
        self.minsize(720, 520)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()

        self.tables = extract_pdf_preview(filepath)
        self.current_table_idx = 0
        self._auto_name = self._detect_bank_name()

        self._build()
        self.transient(parent)
        fit_and_center(self, min_w=760, min_h=560)
        self.wait_window()

    # ── Détection auto du nom ─────────────────────────────────────────────────

    def _detect_bank_name(self) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(self.filepath) as pdf:
                text = (pdf.pages[0].extract_text() or '')[:500]
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            return lines[0][:50] if lines else ''
        except Exception:
            return ''

    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=10)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🏦  Configurer une nouvelle banque",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 12, 'bold')).pack()
        tk.Label(hdr, text=Path(self.filepath).name,
                 bg=CLR['header_bg'], fg=CLR['header_sub'],
                 font=('Segoe UI', 8)).pack(pady=(2, 0))

        main = tk.Frame(self, bg=CLR['page_bg'])
        main.pack(fill='both', expand=True, padx=16, pady=10)

        if not self.tables:
            tk.Label(main,
                text="⚠️  Aucune table détectée dans ce PDF.\n\n"
                     "Seuls les PDFs contenant des tableaux natifs peuvent être\n"
                     "importés automatiquement. Les PDFs scannés (image) ne sont\n"
                     "pas supportés.",
                bg=CLR['page_bg'], fg=CLR['danger'],
                font=('Segoe UI', 10), justify='center', pady=40).pack(expand=True)
            self._mk_btn(self, "Fermer", CLR['border'], CLR['text'],
                         self.destroy, border=True).pack(side='bottom', pady=10)
            return

        # Sélecteur de table si > 1
        if len(self.tables) > 1:
            tr = tk.Frame(main, bg=CLR['page_bg'])
            tr.pack(fill='x', pady=(0, 6))
            tk.Label(tr, text='Table à utiliser :',
                     bg=CLR['page_bg'], fg=CLR['text'],
                     font=('Segoe UI', 9)).pack(side='left')
            self._tbl_var = tk.IntVar(value=0)
            for i, tbl in enumerate(self.tables):
                ttk.Radiobutton(tr, text=f"Table {i+1} ({len(tbl)} lignes)",
                               variable=self._tbl_var, value=i,
                               command=self._on_table_change).pack(side='left', padx=6)

        # Vue table avec dropdowns
        self._tbl_outer = tk.Frame(main, bg=CLR['border'], pady=1, padx=1)
        self._tbl_outer.pack(fill='both', expand=True, pady=(0, 8))
        self._build_table_view()

        # Formulaire
        cfg = tk.Frame(main, bg=CLR['page_bg'])
        cfg.pack(fill='x', pady=(0, 4))

        def field_row(parent, labels_vars):
            """Ligne de paires label+widget."""
            row = tk.Frame(parent, bg=CLR['page_bg'])
            row.pack(fill='x', pady=2)
            for lbl, widget_fn in labels_vars:
                tk.Label(row, text=lbl, bg=CLR['page_bg'], fg=CLR['text'],
                         font=('Segoe UI', 9), anchor='w', width=22).pack(side='left')
                widget_fn(row)
            return row

        # Ligne 1 : nom banque + nom compte
        self._name_var   = tk.StringVar(value=self._auto_name[:40])
        self._compte_var = tk.StringVar(value=self._auto_name[:30])
        r1 = tk.Frame(cfg, bg=CLR['page_bg']); r1.pack(fill='x', pady=2)
        tk.Label(r1, text='Nom de la banque :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=22, anchor='w').pack(side='left')
        tk.Entry(r1, textvariable=self._name_var, width=22,
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 16))
        tk.Label(r1, text='Nom du compte :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=16, anchor='w').pack(side='left')
        tk.Entry(r1, textvariable=self._compte_var, width=22,
                 font=('Segoe UI', 9)).pack(side='left')

        # Ligne 2 : format date + lignes en-tête
        date_labels = [f"{fmt}  (ex: {ex})" for fmt, ex in self.DATE_FORMATS]
        self._date_fmt_var   = tk.StringVar(value=date_labels[0])
        self._header_rows_var = tk.IntVar(value=1)
        r2 = tk.Frame(cfg, bg=CLR['page_bg']); r2.pack(fill='x', pady=2)
        tk.Label(r2, text='Format de date :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=22, anchor='w').pack(side='left')
        mk_combobox(r2, textvariable=self._date_fmt_var, values=date_labels,
                    width=26, state='readonly', font=('Segoe UI', 9)).pack(side='left', padx=(0, 16))
        tk.Label(r2, text="Lignes d'en-tête :", bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=16, anchor='w').pack(side='left')
        tk.Spinbox(r2, from_=0, to=5, textvariable=self._header_rows_var,
                   width=4, font=('Segoe UI', 9)).pack(side='left')
        tk.Label(r2, text='à ignorer', bg=CLR['page_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8)).pack(side='left', padx=4)

        # Ligne 3 : fingerprint
        self._fp_var = tk.StringVar(value=self._auto_name[:60])
        r3 = tk.Frame(cfg, bg=CLR['page_bg']); r3.pack(fill='x', pady=2)
        tk.Label(r3, text='Texte de reconnaissance :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=22, anchor='w').pack(side='left')
        tk.Entry(r3, textvariable=self._fp_var, width=38,
                 font=('Segoe UI', 9)).pack(side='left')
        tk.Label(r3, text='(texte présent dans tous les PDFs de cette banque)',
                 bg=CLR['page_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 7, 'italic')).pack(side='left', padx=6)

        # Ligne 4 : règles de catégorisation
        self._rules: list = []
        self._parsed_txs: list = []   # rempli après un test réussi
        r4 = tk.Frame(cfg, bg=CLR['page_bg']); r4.pack(fill='x', pady=2)
        tk.Label(r4, text='Catégorisation :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), width=22, anchor='w').pack(side='left')
        self._rules_lbl = tk.Label(r4, text='Aucune règle - tout en ❓ Autre',
                                   bg=CLR['page_bg'], fg=CLR['muted'],
                                   font=('Segoe UI', 9))
        self._rules_lbl.pack(side='left')
        self._btn_rules = tk.Button(r4, text='✏ Configurer les règles',
                  bg=CLR['border'], fg=CLR['text'],
                  font=('Segoe UI', 8), relief='solid', bd=1,
                  cursor='hand2', padx=8, pady=2,
                  command=self._edit_rules)
        self._btn_rules.pack(side='left', padx=(8, 0))

        # Zone prévisualisation résultats
        self._preview_frame = tk.Frame(main, bg=CLR['page_bg'])
        self._preview_frame.pack(fill='x')

        # Barre boutons
        sep = tk.Frame(self, bg=CLR['border'], height=1)
        sep.pack(fill='x', side='bottom')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x', side='bottom')
        self._mk_btn(bar, "🔍  Tester la config", CLR['primary'], '#ffffff',
                     self._test_config).pack(side='left')
        self._mk_btn(bar, "Annuler", CLR['border'], CLR['text'],
                     self.destroy, border=True).pack(side='right', padx=(8, 0))
        self._mk_btn(bar, "💾  Enregistrer", CLR['success'], '#ffffff',
                     self._save).pack(side='right')

    def _build_table_view(self):
        """Reconstruit la vue table + dropdowns de mapping."""
        for w in self._tbl_outer.winfo_children():
            w.destroy()

        table = self.tables[self.current_table_idx] if self.tables else []
        if not table:
            return

        ncols = max(len(row) for row in table)
        self.col_roles = [tk.StringVar(value='Ignorer') for _ in range(ncols)]
        self._auto_detect_roles(table, ncols)

        container = tk.Frame(self._tbl_outer, bg=CLR['card_bg'])
        container.pack(fill='both', expand=True)

        canvas = tk.Canvas(container, bg=CLR['card_bg'], highlightthickness=0, height=200)
        sb_v = ttk.Scrollbar(container, orient='vertical',   command=canvas.yview)
        sb_h = ttk.Scrollbar(container, orient='horizontal', command=canvas.xview)
        inner = tk.Frame(canvas, bg=CLR['card_bg'])
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side='right', fill='y')
        sb_h.pack(side='bottom', fill='x')
        canvas.pack(side='left', fill='both', expand=True)

        # Ligne dropdowns
        drop_row = tk.Frame(inner, bg='#f1f5f9', pady=4)
        drop_row.pack(fill='x')
        tk.Label(drop_row, text='#', bg='#f1f5f9', fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold'), width=3).pack(side='left', padx=4)
        for i in range(ncols):
            mk_combobox(drop_row, textvariable=self.col_roles[i],
                        values=self.COL_ROLES, width=13, state='readonly',
                        font=('Segoe UI', 8)).pack(side='left', padx=3)
        tk.Frame(inner, bg=CLR['border'], height=1).pack(fill='x')

        # Données (max 12 lignes)
        CW = 15
        for ri, row in enumerate(table[:12]):
            bg = '#f8fafc' if ri % 2 == 0 else CLR['card_bg']
            dr = tk.Frame(inner, bg=bg, pady=2)
            dr.pack(fill='x')
            tk.Label(dr, text=str(ri), bg=bg, fg=CLR['muted'],
                     font=('Segoe UI', 7), width=3).pack(side='left', padx=4)
            for ci in range(ncols):
                cell = str(row[ci] if ci < len(row) else '').strip()[:CW]
                tk.Label(dr, text=cell, bg=bg, fg=CLR['text'],
                         font=('Courier New', 8), width=CW, anchor='w').pack(side='left', padx=2)

    def _auto_detect_roles(self, table, ncols):
        """Devine les rôles à partir des en-têtes de la première ligne."""
        if not table:
            return
        header = [str(c or '').lower() for c in table[0]]
        date_kw    = ['date', 'jour', 'day']
        label_kw   = ['libellé', 'libelle', 'description', 'label', 'opération', 'operation', 'intitulé', 'motif']
        debit_kw   = ['débit', 'debit', 'sortie', 'retrait', 'dépense', 'depense']
        credit_kw  = ['crédit', 'credit', 'entrée', 'versement', 'dépôt', 'depot']
        amount_kw  = ['montant', 'amount', 'valeur']
        for i, h in enumerate(header[:ncols]):
            if any(k in h for k in date_kw):   self.col_roles[i].set('Date')
            elif any(k in h for k in label_kw): self.col_roles[i].set('Libellé')
            elif any(k in h for k in debit_kw): self.col_roles[i].set('Débit (négatif)')
            elif any(k in h for k in credit_kw):self.col_roles[i].set('Crédit (positif)')
            elif any(k in h for k in amount_kw):self.col_roles[i].set('Montant (+/-)')

    def _edit_rules(self):
        name = self._name_var.get().strip() or 'Nouvelle banque'
        cats = load_categories_from_json(TX_DIR)
        # Libellés uniques depuis les transactions testées (ordre de première apparition)
        seen: set = set()
        unique_labels: list = []
        for t in self._parsed_txs:
            lbl = t.get('label', '').strip()
            if lbl and lbl not in seen:
                seen.add(lbl)
                unique_labels.append(lbl)
        dlg = CategorizationRulesDialog(self, name, self._rules, cats,
                                         suggested_labels=unique_labels or None)
        if dlg.result is not None:
            self._rules = dlg.result
            n = len(self._rules)
            self._rules_lbl.config(
                text=f"{n} règle{'s' if n!=1 else ''} configurée{'s' if n!=1 else ''}" if n
                     else 'Aucune règle - tout en ❓ Autre',
                fg=CLR['text'] if n else CLR['muted'])

    def _on_table_change(self):
        self.current_table_idx = self._tbl_var.get()
        self._build_table_view()

    # ── Récupération config ───────────────────────────────────────────────────

    def _get_config(self):
        roles = [v.get() for v in self.col_roles]
        if 'Date' not in roles:
            messagebox.showwarning("Config incomplète",
                "Assignez le rôle 'Date' à une colonne."); return None
        if 'Libellé' not in roles:
            messagebox.showwarning("Config incomplète",
                "Assignez le rôle 'Libellé' à une colonne."); return None
        if not ('Montant (+/-)' in roles or 'Débit (négatif)' in roles or 'Crédit (positif)' in roles):
            messagebox.showwarning("Config incomplète",
                "Assignez au moins une colonne de montant."); return None
        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning("Nom manquant",
                "Saisissez un nom pour cette banque."); return None

        date_fmt = self._date_fmt_var.get().split('  ')[0].strip()
        cfg = {
            'name':        name,
            'compte':      self._compte_var.get().strip() or name,
            'fingerprint': self._fp_var.get().strip(),
            'date_format': date_fmt,
            'header_rows': self._header_rows_var.get(),
            'table_idx':   self.current_table_idx,
            'col_date':    roles.index('Date'),
            'col_label':   roles.index('Libellé'),
        }
        if 'Montant (+/-)' in roles:
            cfg['col_montant'] = roles.index('Montant (+/-)')
        if 'Débit (négatif)' in roles:
            cfg['col_debit'] = roles.index('Débit (négatif)')
        if 'Crédit (positif)' in roles:
            cfg['col_credit'] = roles.index('Crédit (positif)')
        cfg['rules'] = getattr(self, '_rules', [])
        return cfg

    # ── Tester ────────────────────────────────────────────────────────────────

    def _test_config(self):
        cfg = self._get_config()
        if not cfg:
            return
        for w in self._preview_frame.winfo_children():
            w.destroy()
        try:
            txs = parse_generic_pdf(self.filepath, cfg)
        except Exception as e:
            tk.Label(self._preview_frame, text=f'❌  Erreur : {e}',
                     bg=CLR['page_bg'], fg=CLR['danger'],
                     font=('Segoe UI', 9)).pack(anchor='w', pady=4)
            return
        if not txs:
            tk.Label(self._preview_frame,
                text='⚠️  Aucune transaction extraite - vérifiez le format de date et le mapping.',
                bg=CLR['page_bg'], fg=CLR['warning'],
                font=('Segoe UI', 9)).pack(anchor='w', pady=4)
            return
        # Stocker les transactions pour la suggestion de règles
        self._parsed_txs = txs
        n_labels = len({t['label'] for t in txs})
        self._btn_rules.config(
            text=f'✏ Configurer les règles  ({n_labels} libellés disponibles)',
            bg=CLR['primary'], fg='#ffffff')
        tk.Label(self._preview_frame,
            text=f'✅  {len(txs)} transaction(s) extraite(s). Aperçu (5 premières) :',
            bg=CLR['page_bg'], fg=CLR['success'],
            font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(4, 2))
        for tx in txs[:5]:
            s = f"  {tx['date']}   {tx['label'][:38]:<38}   {tx['montant']:+.2f} €"
            tk.Label(self._preview_frame, text=s,
                     bg=CLR['page_bg'], fg=CLR['text'],
                     font=('Courier New', 8), anchor='w').pack(anchor='w')

    # ── Enregistrer ───────────────────────────────────────────────────────────

    def _save(self):
        cfg = self._get_config()
        if not cfg:
            return
        try:
            txs = parse_generic_pdf(self.filepath, cfg)
        except Exception as e:
            messagebox.showerror('Erreur de parsing', str(e)); return
        if not txs:
            if not messagebox.askyesno('Aucune transaction',
                    "Aucune transaction extraite avec cette config.\n"
                    "Enregistrer quand même ?"):
                return
        configs = load_bank_configs()
        configs[cfg['name']] = cfg
        save_bank_configs(configs)
        self.result = cfg
        self.destroy()

    def _mk_btn(self, parent, text, bg, fg, cmd, border=False, padx=14, pady=6):
        return tk.Button(parent, text=text, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         font=('Segoe UI', 9, 'bold'),
                         relief='flat' if not border else 'solid',
                         bd=1 if border else 0, cursor='hand2',
                         padx=padx, pady=pady, command=cmd)


class ConfirmImportDialog(tk.Toplevel):
    """Dialogue de confirmation d'import stylisé."""

    def __init__(self, parent, nn: int, n_replaced: int, nm: int):
        super().__init__(parent)
        self.result = False
        self.title("Confirmer l'import")
        self.resizable(False, False)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()
        self.transient(parent)
        self._build(nn, n_replaced, nm)
        fit_and_center(self, min_w=380, min_h=260)
        self.wait_window()

    def _build(self, nn, n_replaced, nm):
        # Header
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text="📋  Résumé de l'import",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 11, 'bold')).pack()

        # Corps
        body = tk.Frame(self, bg=CLR['page_bg'], padx=24, pady=16)
        body.pack(fill='both', expand=True)

        rows = [
            ("📥", f"{nn} nouvelle{'s' if nn!=1 else ''} transaction{'s' if nn!=1 else ''} à ajouter",
             CLR['success'] if nn > 0 else CLR['muted']),
            ("🔄", f"{n_replaced} saisie{'s' if n_replaced!=1 else ''} manuelle{'s' if n_replaced!=1 else ''} à remplacer",
             CLR['warning'] if n_replaced > 0 else CLR['muted']),
            ("📌", f"{nm} saisie{'s' if nm!=1 else ''} manuelle{'s' if nm!=1 else ''} conservée{'s' if nm!=1 else ''}",
             CLR['primary'] if nm > 0 else CLR['muted']),
        ]
        for icon, text, color in rows:
            row = tk.Frame(body, bg=CLR['card_bg'], pady=8, padx=12)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=icon, bg=CLR['card_bg'],
                     font=('Segoe UI', 13)).pack(side='left', padx=(0, 10))
            tk.Label(row, text=text, bg=CLR['card_bg'], fg=color,
                     font=('Segoe UI', 9, 'bold'), anchor='w').pack(side='left')

        # Barre boutons
        tk.Frame(self, bg=CLR['border'], height=1).pack(fill='x')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x')
        tk.Button(bar, text="✓  Confirmer",
                  bg=CLR['success'], fg='#ffffff',
                  activebackground=CLR['success'], activeforeground='#ffffff',
                  font=('Segoe UI', 9, 'bold'), relief='flat', bd=0,
                  cursor='hand2', padx=16, pady=7,
                  command=self._ok).pack(side='right')
        tk.Button(bar, text="Annuler",
                  bg=CLR['border'], fg=CLR['text'],
                  activebackground=CLR['border'], activeforeground=CLR['text'],
                  font=('Segoe UI', 9, 'bold'), relief='solid', bd=1,
                  cursor='hand2', padx=14, pady=7,
                  command=self.destroy).pack(side='right', padx=(0, 8))

    def _ok(self):
        self.result = True
        self.destroy()


class SuccessImportDialog(tk.Toplevel):
    """Dialogue de succès d'import stylisé."""

    def __init__(self, parent, nn: int, n_replaced: int, n_files: int):
        super().__init__(parent)
        self.title("Import terminé")
        self.resizable(False, False)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()
        self.transient(parent)
        self._build(nn, n_replaced, n_files)
        fit_and_center(self, min_w=340, min_h=240)
        self.wait_window()

    def _build(self, nn, n_replaced, n_files):
        # Header vert
        hdr = tk.Frame(self, bg='#166534', pady=12)
        hdr.pack(fill='x')
        tk.Label(hdr, text="✅  Import réussi !",
                 bg='#166534', fg='#ffffff',
                 font=('Segoe UI', 11, 'bold')).pack()

        body = tk.Frame(self, bg=CLR['page_bg'], padx=24, pady=16)
        body.pack(fill='both', expand=True)

        rows = [
            ("📥", f"{nn} transaction{'s' if nn!=1 else ''} ajoutée{'s' if nn!=1 else ''}"),
            ("🔄", f"{n_replaced} doublon{'s' if n_replaced!=1 else ''} remplacé{'s' if n_replaced!=1 else ''}"),
            ("💾", f"{n_files} fichier{'s' if n_files!=1 else ''} JSON mis à jour"),
        ]
        for icon, text in rows:
            row = tk.Frame(body, bg=CLR['card_bg'], pady=8, padx=12)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=icon, bg=CLR['card_bg'],
                     font=('Segoe UI', 13)).pack(side='left', padx=(0, 10))
            tk.Label(row, text=text, bg=CLR['card_bg'], fg=CLR['text'],
                     font=('Segoe UI', 9), anchor='w').pack(side='left')

        tk.Label(body, text="Rafraîchissez la page Finances dans Obsidian.",
                 bg=CLR['page_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8, 'italic')).pack(pady=(10, 0))

        tk.Frame(self, bg=CLR['border'], height=1).pack(fill='x')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x')
        tk.Button(bar, text="Fermer",
                  bg=CLR['primary'], fg='#ffffff',
                  activebackground=CLR['primary'], activeforeground='#ffffff',
                  font=('Segoe UI', 9, 'bold'), relief='flat', bd=0,
                  cursor='hand2', padx=16, pady=7,
                  command=self.destroy).pack(side='right')


class BankManagerDialog(tk.Toplevel):
    """
    Fenêtre de gestion des configurations de banques.
    Affiche les parsers intégrés (SG, Revolut) et les configs custom (bank_configs.json).
    Permet de modifier ou supprimer les configs custom, et d'éditer les règles de catégorisation.
    """

    def __init__(self, parent, tx_dir: Path = None):
        super().__init__(parent)
        self.tx_dir = tx_dir or TX_DIR
        self.title("Gestion des banques")
        self.resizable(True, True)
        self.minsize(580, 380)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()
        self._build()
        self.transient(parent)
        fit_and_center(self, min_w=620, min_h=420)

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=10)
        hdr.pack(fill='x')
        tk.Label(hdr, text="🏦  Gestion des banques",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 12, 'bold')).pack()
        tk.Label(hdr, text="Visualisez et gérez les configurations de parsers.",
                 bg=CLR['header_bg'], fg=CLR['header_sub'],
                 font=('Segoe UI', 8)).pack(pady=(2, 0))

        self._main = tk.Frame(self, bg=CLR['page_bg'])
        self._main.pack(fill='both', expand=True, padx=16, pady=12)
        self._render()

        sep = tk.Frame(self, bg=CLR['border'], height=1)
        sep.pack(fill='x', side='bottom')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x', side='bottom')
        self._mk_btn(bar, "Fermer", CLR['border'], CLR['text'],
                     self.destroy, border=True).pack(side='right')

    def _render(self):
        for w in self._main.winfo_children():
            w.destroy()

        # ── Parsers intégrés ─────────────────────────────────────────
        self._section(self._main, "INTÉGRÉS - lecture seule")
        for name, banque, desc in [
            ("SG",      "Société Générale", "Parser natif - relevés ReleveCompte_*.pdf"),
            ("Revolut", "Revolut",          "Parser natif - account-statement-*.pdf"),
        ]:
            self._row_builtin(name, banque, desc)

        # ── Configs custom ───────────────────────────────────────────
        configs = load_bank_configs()
        self._section(self._main, "CONFIGURÉES - bank_configs.json")

        if not configs:
            tk.Label(self._main,
                text="Aucune configuration sauvegardée.\n"
                     "Importez un PDF d'une nouvelle banque pour en créer une.",
                bg=CLR['page_bg'], fg=CLR['muted'],
                font=('Segoe UI', 9, 'italic'), justify='left').pack(
                    anchor='w', padx=4, pady=6)
        else:
            for name, cfg in configs.items():
                if name.startswith('_'):   # ignorer les clés internes (_builtin_rules, etc.)
                    continue
                self._row_custom(name, cfg)

    def _section(self, parent, title: str):
        tk.Label(parent, text=title, bg=CLR['page_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', pady=(8, 3))
        tk.Frame(parent, bg=CLR['border'], height=1).pack(fill='x', pady=(0, 4))

    def _row_builtin(self, name, banque, desc):
        disabled = get_disabled_builtins()
        is_off   = name in disabled
        row_bg   = '#f8fafc' if not is_off else '#f1f5f9'
        row = tk.Frame(self._main, bg=row_bg, relief='flat', pady=8, padx=12)
        row.pack(fill='x', pady=2)
        bar_clr = CLR['border'] if is_off else CLR['primary']
        tk.Frame(row, bg=bar_clr, width=3).pack(side='left', fill='y', padx=(0, 10))
        info = tk.Frame(row, bg=row_bg)
        info.pack(side='left', fill='x', expand=True)
        name_clr = CLR['muted'] if is_off else CLR['text']
        n_rules = len(get_builtin_rules(name))
        rules_hint = f"  -  {n_rules} règle{'s' if n_rules!=1 else ''} perso" if n_rules else ''
        tk.Label(info, text=name + (' (désactivé)' if is_off else '') + rules_hint,
                 bg=row_bg, fg=name_clr,
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        tk.Label(info, text=f"🏛 {banque}  -  {desc}",
                 bg=row_bg, fg=CLR['muted'],
                 font=('Segoe UI', 8)).pack(anchor='w')
        btn_row = tk.Frame(row, bg=row_bg)
        btn_row.pack(side='right')
        # Bouton règles de catégorisation
        self._mk_btn(btn_row, "📋 Règles", CLR['primary'], '#ffffff',
                     lambda n=name: self._edit_builtin_rules(n),
                     padx=8, pady=3).pack(side='left', padx=(0, 4))
        if is_off:
            self._mk_btn(btn_row, "✓ Réactiver", CLR['success'], '#ffffff',
                         lambda n=name: self._toggle_builtin(n, False),
                         padx=8, pady=3).pack(side='left', padx=(0, 4))
        else:
            self._mk_btn(btn_row, "🚫 Désactiver", CLR['danger'], '#ffffff',
                         lambda n=name: self._toggle_builtin(n, True),
                         padx=8, pady=3).pack(side='left', padx=(0, 4))
        lbl_txt = "désactivé" if is_off else "intégré"
        lbl_bg  = '#fca5a5' if is_off else CLR['card_bg']
        lbl_fg  = '#7f1d1d' if is_off else CLR['primary']
        tk.Label(row, text=lbl_txt, bg=lbl_bg, fg=lbl_fg,
                 font=('Segoe UI', 7, 'bold'), padx=6, pady=2).pack(side='right', padx=(0, 6))

    def _edit_builtin_rules(self, name: str):
        current_rules = get_builtin_rules(name)
        # Première ouverture → pré-peupler avec les règles par défaut extraites du code
        if not current_rules:
            current_rules = DEFAULT_BUILTIN_RULES.get(name, [])
        cats = load_categories_from_json(self.tx_dir)
        dlg = CategorizationRulesDialog(self, name, current_rules, cats)
        if dlg.result is not None:
            set_builtin_rules(name, dlg.result)
            self._render()

    def _row_custom(self, name, cfg):
        row = tk.Frame(self._main, bg=CLR['card_bg'], pady=8, padx=12)
        row.pack(fill='x', pady=2)
        tk.Frame(row, bg='#8b5cf6', width=3).pack(side='left', fill='y', padx=(0, 10))
        info = tk.Frame(row, bg=CLR['card_bg'])
        info.pack(side='left', fill='x', expand=True)
        tk.Label(info, text=name, bg=CLR['card_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        compte = cfg.get('compte', '')
        fp     = cfg.get('fingerprint', '')
        fmt    = cfg.get('date_format', '')
        details = f"Compte : {compte}   |   Format date : {fmt}"
        if fp:
            details += f"   |   Reconnaissance : « {fp[:40]}{'…' if len(fp)>40 else ''} »"
        tk.Label(info, text=details, bg=CLR['card_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8)).pack(anchor='w')

        # Boutons
        btn_row = tk.Frame(row, bg=CLR['card_bg'])
        btn_row.pack(side='right')
        self._mk_btn(btn_row, "✏ Modifier", CLR['primary'], '#ffffff',
                     lambda n=name, c=cfg: self._edit(n, c),
                     padx=8, pady=3).pack(side='left', padx=(0, 4))
        self._mk_btn(btn_row, "🗑 Supprimer", CLR['danger'], '#ffffff',
                     lambda n=name: self._delete(n),
                     padx=8, pady=3).pack(side='left')

    def _toggle_builtin(self, name: str, disable: bool):
        if disable:
            if not messagebox.askyesno("Désactiver le parser",
                    f"Désactiver le parser intégré « {name} » ?\n\n"
                    "Les PDFs de cette banque seront traités comme inconnus\n"
                    "lors du prochain import (vous pourrez les reconfigurer manuellement).\n\n"
                    "Vous pourrez le réactiver à tout moment depuis cette fenêtre."):
                return
        set_builtin_disabled(name, disable)
        self._render()

    def _delete(self, name: str):
        if not messagebox.askyesno("Supprimer la config",
                f"Supprimer la configuration « {name} » ?\n\n"
                "Les transactions déjà importées ne seront pas affectées,\n"
                "mais les prochains PDFs de cette banque seront traités comme inconnus."):
            return
        configs = load_bank_configs()
        configs.pop(name, None)
        save_bank_configs(configs)
        self._render()

    def _edit(self, name: str, cfg: dict):
        """Ouvre un formulaire d'édition simple (sans PDF requis)."""
        dlg = BankEditDialog(self, name, cfg)
        if dlg.result:
            configs = load_bank_configs()
            # Si le nom a changé, supprimer l'ancienne entrée
            if dlg.result['name'] != name:
                configs.pop(name, None)
            configs[dlg.result['name']] = dlg.result
            save_bank_configs(configs)
            self._render()

    def _mk_btn(self, parent, text, bg, fg, cmd, border=False, padx=10, pady=5):
        return tk.Button(parent, text=text, bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         font=('Segoe UI', 8, 'bold'),
                         relief='flat' if not border else 'solid',
                         bd=1 if border else 0, cursor='hand2',
                         padx=padx, pady=pady, command=cmd)


class BankEditDialog(tk.Toplevel):
    """Formulaire d'édition d'une config de banque (sans prévisualisation PDF)."""

    DATE_FORMATS = [
        ('%d/%m/%Y', '31/12/2024'), ('%d/%m/%y', '31/12/24'),
        ('%Y-%m-%d', '2024-12-31'), ('%d-%m-%Y', '31-12-2024'),
        ('%d.%m.%Y', '31.12.2024'), ('%m/%d/%Y', '12/31/2024'),
    ]

    def __init__(self, parent, name: str, cfg: dict):
        super().__init__(parent)
        self.result = None
        self.cfg    = cfg
        self.title(f"Modifier - {name}")
        self.resizable(False, False)
        self.configure(bg=CLR['page_bg'])
        self.grab_set()
        self._build(name, cfg)
        self.transient(parent)
        fit_and_center(self, min_w=460, min_h=320)
        self.wait_window()

    def _build(self, name, cfg):
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=8)
        hdr.pack(fill='x')
        tk.Label(hdr, text=f"✏  Modifier « {name} »",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 11, 'bold')).pack()

        frm = tk.Frame(self, bg=CLR['page_bg'])
        frm.pack(fill='both', expand=True, padx=20, pady=14)

        def field(lbl, var, row):
            tk.Label(frm, text=lbl, bg=CLR['page_bg'], fg=CLR['text'],
                     font=('Segoe UI', 9), anchor='w', width=24).grid(
                         row=row, column=0, sticky='w', pady=4)
            e = tk.Entry(frm, textvariable=var, width=34, font=('Segoe UI', 9))
            e.grid(row=row, column=1, sticky='ew', pady=4, padx=(6, 0))

        self._name_var    = tk.StringVar(value=name)
        self._compte_var  = tk.StringVar(value=cfg.get('compte', ''))
        self._fp_var      = tk.StringVar(value=cfg.get('fingerprint', ''))

        field("Nom de la banque :",       self._name_var,   0)
        field("Nom du compte :",          self._compte_var, 1)
        field("Texte de reconnaissance :", self._fp_var,    2)

        # Format date
        tk.Label(frm, text="Format de date :", bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), anchor='w', width=24).grid(
                     row=3, column=0, sticky='w', pady=4)
        date_labels = [f"{fmt}  (ex: {ex})" for fmt, ex in self.DATE_FORMATS]
        current_fmt = cfg.get('date_format', '%d/%m/%Y')
        # Trouver le label correspondant au format actuel
        default_lbl = next((l for l in date_labels if l.startswith(current_fmt)), date_labels[0])
        self._date_var = tk.StringVar(value=default_lbl)
        mk_combobox(frm, textvariable=self._date_var, values=date_labels,
                    width=32, state='readonly',
                    font=('Segoe UI', 9)).grid(row=3, column=1, sticky='ew',
                                               pady=4, padx=(6, 0))

        # Header rows
        tk.Label(frm, text="Lignes d'en-tête :", bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), anchor='w', width=24).grid(
                     row=4, column=0, sticky='w', pady=4)
        self._hr_var = tk.IntVar(value=cfg.get('header_rows', 1))
        tk.Spinbox(frm, from_=0, to=5, textvariable=self._hr_var,
                   width=6, font=('Segoe UI', 9)).grid(row=4, column=1,
                                                        sticky='w', pady=4, padx=(6, 0))

        # Catégorisation - règles
        tk.Label(frm, text='Catégorisation :', bg=CLR['page_bg'], fg=CLR['text'],
                 font=('Segoe UI', 9), anchor='w', width=24).grid(
                     row=5, column=0, sticky='w', pady=4)
        self._rules: list = list(cfg.get('rules', []))
        rules_cell = tk.Frame(frm, bg=CLR['page_bg'])
        rules_cell.grid(row=5, column=1, sticky='ew', pady=4, padx=(6, 0))
        n = len(self._rules)
        self._rules_lbl = tk.Label(rules_cell,
            text=f"{n} règle{'s' if n!=1 else ''} configurée{'s' if n!=1 else ''}" if n
                 else 'Aucune règle - tout en ❓ Autre',
            bg=CLR['page_bg'], fg=CLR['text'] if n else CLR['muted'],
            font=('Segoe UI', 9))
        self._rules_lbl.pack(side='left')
        tk.Button(rules_cell, text='✏ Configurer',
                  bg=CLR['border'], fg=CLR['text'],
                  font=('Segoe UI', 8), relief='solid', bd=1,
                  cursor='hand2', padx=8, pady=2,
                  command=self._edit_rules).pack(side='left', padx=(8, 0))

        frm.columnconfigure(1, weight=1)

        sep = tk.Frame(self, bg=CLR['border'], height=1)
        sep.pack(fill='x', side='bottom')
        bar = tk.Frame(self, bg=CLR['card_bg'], pady=10, padx=16)
        bar.pack(fill='x', side='bottom')
        tk.Button(bar, text="Annuler", bg=CLR['border'], fg=CLR['text'],
                  font=('Segoe UI', 9, 'bold'), relief='solid', bd=1,
                  cursor='hand2', padx=12, pady=5,
                  command=self.destroy).pack(side='right', padx=(8, 0))
        tk.Button(bar, text="💾  Enregistrer", bg=CLR['success'], fg='#ffffff',
                  font=('Segoe UI', 9, 'bold'), relief='flat', bd=0,
                  cursor='hand2', padx=12, pady=5,
                  command=self._save).pack(side='right')

    def _edit_rules(self):
        name = self._name_var.get().strip() or self.cfg.get('name', 'Banque')
        cats = load_categories_from_json(TX_DIR)
        dlg  = CategorizationRulesDialog(self, name, self._rules, cats)
        if dlg.result is not None:
            self._rules = dlg.result
            n = len(self._rules)
            self._rules_lbl.config(
                text=f"{n} règle{'s' if n!=1 else ''} configurée{'s' if n!=1 else ''}" if n
                     else 'Aucune règle - tout en ❓ Autre',
                fg=CLR['text'] if n else CLR['muted'])

    def _save(self):
        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning("Nom manquant", "Le nom est requis."); return
        date_fmt = self._date_var.get().split('  ')[0].strip()
        self.result = {
            **self.cfg,                          # préserve col_date, col_label, etc.
            'name':        name,
            'compte':      self._compte_var.get().strip(),
            'fingerprint': self._fp_var.get().strip(),
            'date_format': date_fmt,
            'header_rows': self._hr_var.get(),
            'rules':       self._rules,
        }
        self.destroy()


class ImportApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Import de relevés bancaires")
        self.resizable(True, True)
        self.minsize(800, 540)
        self.configure(bg=CLR['page_bg'])

        # ── DPI scaling et police optimale ────────────────────────────────────
        apply_dpi_scaling(self)
        _UI_FONT[0] = detect_font_family()

        if USE_BS:
            self._bs = ttk.Style(theme='litera')

        self.vault_root = get_vault_root()
        self.tx_dir = find_tx_dir(self.vault_root)

        self.pdf_list:     list[tuple[str, str]] = []
        self.analysis:     dict | None = None
        self.replace_vars: list[tk.BooleanVar] = []
        self.recat_vars:   list[tk.BooleanVar] = []

        self._build()
        # Centrer la fenêtre principale
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 860, 600
        self.geometry(f'{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}')

        if not PARSER_OK:
            self.after(300, lambda: messagebox.showerror(
                "Dépendance manquante",
                f"Impossible d'importer parse_finances.py :\n{PARSER_ERROR}\n\n"
                "Vérifiez que parse_finances.py est dans le même dossier."))


    # ── Construction ──────────────────────────────────────────────────────────

    def _build(self):
        self._build_header()
        # Conteneur principal scrollable
        self._main = tk.Frame(self, bg=CLR['page_bg'])
        self._main.pack(fill='both', expand=True, padx=20, pady=16)
        self._build_step1()
        self._build_analyze_btn()
        # Zone résultats (construite dynamiquement)
        self._frm_results = tk.Frame(self._main, bg=CLR['page_bg'])
        # Bottom bar
        self._build_bottom()

    def _build_header(self):
        hdr = tk.Frame(self, bg=CLR['header_bg'], pady=14)
        hdr.pack(fill='x')
        tk.Label(hdr, text="💰  Import de relevés bancaires",
                 bg=CLR['header_bg'], fg=CLR['header_fg'],
                 font=('Segoe UI', 14, 'bold')).pack()
        vault_row = tk.Frame(hdr, bg=CLR['header_bg'])
        vault_row.pack(pady=(2, 0))
        vault_short = str(self.vault_root).replace(str(Path.home()), '~')
        self._lbl_vault = tk.Label(vault_row, text=f"Vault : {vault_short}",
                 bg=CLR['header_bg'], fg=CLR['header_sub'],
                 font=('Segoe UI', 8))
        self._lbl_vault.pack(side='left')
        tk.Button(vault_row, text="📁", bg=CLR['header_bg'], fg=CLR['header_sub'],
                  activebackground=CLR['header_bg'], activeforeground=CLR['header_fg'],
                  font=('Segoe UI', 8), relief='flat', bd=0, cursor='hand2',
                  padx=4, pady=0, command=self._change_vault).pack(side='left', padx=(4, 0))

    def _card(self, parent, title: str) -> tk.Frame:
        """Crée une carte blanche avec titre."""
        outer = tk.Frame(parent, bg=CLR['border'], pady=1, padx=1)
        outer.pack(fill='x', pady=(0, 12))
        inner = tk.Frame(outer, bg=CLR['card_bg'])
        inner.pack(fill='both', expand=True)
        if title:
            tk.Label(inner, text=title, bg=CLR['card_bg'], fg=CLR['muted'],
                     font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=14, pady=(10,4))
            tk.Frame(inner, bg=CLR['border'], height=1).pack(fill='x', padx=0)
        body = tk.Frame(inner, bg=CLR['card_bg'], padx=14, pady=10)
        body.pack(fill='both', expand=True)
        return body

    def _build_step1(self):
        body = self._card(self._main, "ÉTAPE 1 - Sélectionner les relevés PDF")

        # Barre de boutons
        btn_row = tk.Frame(body, bg=CLR['card_bg'])
        btn_row.pack(fill='x', pady=(0, 8))
        self._btn_add = self._mk_btn(btn_row, "＋  Ajouter des PDFs",
                                     CLR['primary'], '#ffffff', self._add_pdfs)
        self._btn_add.pack(side='left')
        tk.Label(btn_row, text='Ctrl+clic pour sélectionner plusieurs fichiers',
                 bg=CLR['card_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 7, 'italic')).pack(side='left', padx=(8,0))
        self._btn_rem = self._mk_btn(btn_row, "✕  Retirer",
                                     CLR['border'], CLR['muted'], self._remove_pdf,
                                     border=True)
        self._btn_rem.pack(side='left', padx=(8,0))
        self._lbl_count = tk.Label(btn_row, text='Aucun PDF sélectionné.',
                                   bg=CLR['card_bg'], fg=CLR['muted'],
                                   font=('Segoe UI', 8))
        self._lbl_count.pack(side='right')

        # Liste PDFs - canvas scrollable vertical uniquement
        list_frame = tk.Frame(body, bg=CLR['border'], pady=1, padx=1)
        list_frame.pack(fill='x')
        self._pdf_canvas = tk.Canvas(list_frame, bg=CLR['card_bg'],
                                     highlightthickness=0, height=130)
        self._pdf_sb = ttk.Scrollbar(list_frame, orient='vertical',
                                     command=self._pdf_canvas.yview)
        self._pdf_inner = tk.Frame(self._pdf_canvas, bg=CLR['card_bg'])
        self._pdf_inner.bind('<Configure>',
            lambda e: self._pdf_canvas.configure(
                scrollregion=self._pdf_canvas.bbox('all')))
        self._pdf_win_id = self._pdf_canvas.create_window(
            (0, 0), window=self._pdf_inner, anchor='nw')
        # Étirer l'inner frame à la largeur du canvas (évite le scroll horizontal)
        self._pdf_canvas.bind('<Configure>',
            lambda e: self._pdf_canvas.itemconfig(self._pdf_win_id, width=e.width))
        self._pdf_canvas.configure(yscrollcommand=self._pdf_sb.set)
        self._pdf_canvas.pack(side='left', fill='both', expand=True)
        self._pdf_sb.pack(side='right', fill='y')
        # Scroll souris actif uniquement dans la zone PDF
        bind_canvas_scroll(self._pdf_canvas, self._pdf_inner)

        # Placeholder texte
        self._pdf_placeholder = tk.Label(
            self._pdf_inner,
            text='Cliquez sur "＋ Ajouter des PDFs" pour sélectionner vos relevés.',
            bg=CLR['card_bg'], fg=CLR['muted'], font=('Segoe UI', 9),
            pady=40, wraplength=500)
        self._pdf_placeholder.pack(expand=True)

    def _build_analyze_btn(self):
        frm = tk.Frame(self._main, bg=CLR['page_bg'])
        frm.pack(fill='x', pady=(0, 12))
        self._btn_analyze = self._mk_btn(
            frm, "🔍   Analyser les PDFs",
            CLR['primary'], '#ffffff', self._analyze,
            font_size=10, padx=28, pady=10)
        self._btn_analyze.pack(side='left')
        self._btn_analyze.config(state='disabled',
                                  bg='#cbd5e1', fg='#94a3b8')
        self._lbl_status = tk.Label(frm, text='', bg=CLR['page_bg'],
                                    fg=CLR['muted'], font=('Segoe UI', 9))
        self._lbl_status.pack(side='left', padx=14)

    def _build_bottom(self):
        bar = tk.Frame(self, bg=CLR['border'], pady=1)
        bar.pack(fill='x', side='bottom')
        inner = tk.Frame(bar, bg=CLR['card_bg'], pady=10, padx=20)
        inner.pack(fill='x')
        self._btn_confirm = self._mk_btn(
            inner, "✓   Importer",
            CLR['success'], '#ffffff', self._confirm,
            font_size=10, padx=22, pady=8)
        self._btn_confirm.pack(side='right')
        self._btn_confirm.config(state='disabled', bg='#cbd5e1', fg='#94a3b8')
        self._mk_btn(inner, "Fermer", CLR['border'], CLR['text'],
                     self.destroy, border=True, padx=18, pady=8
                     ).pack(side='right', padx=(0,8))
        self._mk_btn(inner, "⚙️  Gérer les banques", CLR['border'], CLR['text'],
                     lambda: BankManagerDialog(self, tx_dir=self.tx_dir),
                     border=True, padx=14, pady=8
                     ).pack(side='left')

    # ── Changer le vault ──────────────────────────────────────────────────────

    def _change_vault(self):
        new_path = filedialog.askdirectory(
            title="Sélectionner le dossier racine du vault",
            initialdir=str(self.vault_root))
        if not new_path:
            return
        new_path = Path(new_path)
        # Vérification minimale : le dossier Transactions doit exister
        new_tx = find_tx_dir(new_path)
        if not new_tx.exists():
            if not messagebox.askyesno("Dossier inattendu",
                    f"Le dossier suivant n'existe pas dans le vault sélectionné :\n"
                    f"  {new_tx}\n\n"
                    "Voulez-vous quand même utiliser ce vault ?"):
                return
        # Sauvegarder et mettre à jour
        cfg = load_script_config()
        cfg['vault_path'] = str(new_path)
        save_script_config(cfg)
        self.vault_root = new_path
        self.tx_dir     = new_tx
        vault_short = str(new_path).replace(str(Path.home()), '~')
        self._lbl_vault.config(text=f"Vault : {vault_short}")
        # Vider la liste de PDFs (ils venaient peut-être de l'ancien vault)
        self.pdf_list.clear()
        self.analysis = None
        self._refresh_pdf_list()
        self._lbl_status.config(text='')

    # ── Helpers widgets ───────────────────────────────────────────────────────

    def _mk_btn(self, parent, text, bg, fg, cmd,
                font_size=9, padx=14, pady=6, border=False):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg,
                        activebackground=bg, activeforeground=fg,
                        font=('Segoe UI', font_size, 'bold'),
                        relief='flat' if not border else 'solid',
                        bd=1 if border else 0,
                        cursor='hand2',
                        padx=padx, pady=pady,
                        command=cmd)
        if border:
            btn.config(highlightthickness=1,
                       highlightbackground=CLR['border'])
        return btn

    def _btn_enable(self, btn, bg, fg):
        btn.config(state='normal', bg=bg, fg=fg,
                   activebackground=bg, activeforeground=fg)

    def _btn_disable(self, btn):
        btn.config(state='disabled', bg='#cbd5e1', fg='#94a3b8')

    # ── Dialogue de fichiers natif ────────────────────────────────────────────

    @staticmethod
    def _open_native_dialog() -> list[str]:
        """
        Ouvre le dialogue de fichiers natif du système :
        - kdialog  (KDE/Plasma)   → dialogue KDE natif
        - zenity   (GNOME/GTK)    → dialogue GTK
        - tkinter  (fallback)     → dialogue générique
        """
        import subprocess, platform
        start_dir = str(Path.home() / "Downloads")

        if platform.system() == 'Linux':
            # Essai kdialog (KDE Plasma)
            # FileNotFoundError = non installé → essayer le suivant
            # Sinon (cancel ou sélection) → s'arrêter ici
            try:
                r = subprocess.run(
                    ['kdialog', '--multiple',
                     '--getopenfilename', start_dir,
                     '*.pdf|Fichiers PDF (*.pdf)',
                     '--title', 'Sélectionner les relevés PDF (Ctrl+clic pour plusieurs)'],
                    capture_output=True, text=True)
                if r.returncode == 0 and r.stdout.strip():
                    raw = r.stdout.strip()
                    # KDE Plasma retourne les chemins séparés par \n ou par espace,
                    # SANS guillemets même si les chemins contiennent des espaces.
                    # On ne peut pas utiliser shlex.split car ça découpe les espaces
                    # dans les noms de dossiers (ex: "Relevé Société Générale").
                    # Astuce : tous les chemins Linux sont absolus (commencent par /),
                    # donc on splitte sur " /" pour retrouver les chemins.
                    if '\n' in raw:
                        files = [f.strip() for f in raw.split('\n') if f.strip()]
                    else:
                        # Splitter sur " /" : chaque chemin absolu commence par "/"
                        parts = raw.split(' /')
                        files = [parts[0]] + ['/' + p for p in parts[1:]]
                        files = [f.strip() for f in files if f.strip()]
                    return [f for f in files if f]
                return []   # kdialog trouvé mais annulé → stop
            except FileNotFoundError:
                pass        # kdialog absent → essayer zenity

            # Essai zenity (GNOME, XFCE, etc.)
            try:
                r = subprocess.run(
                    ['zenity', '--file-selection', '--multiple',
                     '--file-filter=Fichiers PDF (*.pdf) | *.pdf',
                     '--filename', start_dir + '/',
                     '--title', 'Sélectionner les relevés PDF'],
                    capture_output=True, text=True)
                if r.returncode == 0 and r.stdout.strip():
                    return [f for f in r.stdout.strip().split('|')
                            if f and Path(f).exists()]
                return []   # zenity trouvé mais annulé → stop
            except FileNotFoundError:
                pass        # zenity absent → fallback tkinter

        # Fallback : dialogue tkinter
        files = filedialog.askopenfilenames(
            title='Sélectionner les relevés PDF',
            initialdir=start_dir,
            filetypes=[('Fichiers PDF', '*.pdf'), ('Tous les fichiers', '*.*')])
        return list(files)

    # ── Gestion PDFs ──────────────────────────────────────────────────────────

    def _add_pdfs(self):
        files = self._open_native_dialog()
        existing = {fp for fp, _ in self.pdf_list}
        for fp in files:
            if fp not in existing:
                self.pdf_list.append((fp, detect_pdf_type(fp)))
        self._refresh_pdf_list()

    def _remove_pdf(self):
        if self._selected_pdf_idx is not None:
            self.pdf_list.pop(self._selected_pdf_idx)
            self._selected_pdf_idx = None
            self._refresh_pdf_list()

    def _refresh_pdf_list(self):
        for w in self._pdf_inner.winfo_children():
            w.destroy()
        self._selected_pdf_idx = None

        if not self.pdf_list:
            tk.Label(self._pdf_inner,
                     text='Cliquez sur "＋ Ajouter des PDFs" pour sélectionner vos relevés.',
                     bg=CLR['card_bg'], fg=CLR['muted'],
                     font=('Segoe UI', 9), pady=40).pack(expand=True)
        else:
            for i, (fp, ptype) in enumerate(self.pdf_list):
                self._pdf_row(i, fp, ptype)

        n = len(self.pdf_list)
        self._lbl_count.config(
            text=f"{n} PDF{'s' if n!=1 else ''} sélectionné{'s' if n!=1 else ''}."
            if n else "Aucun PDF sélectionné.")

        if n:
            self._btn_enable(self._btn_analyze, CLR['primary'], '#ffffff')
        else:
            self._btn_disable(self._btn_analyze)

        # Reset résultats
        self.analysis = None
        self._btn_disable(self._btn_confirm)
        self._frm_results.pack_forget()
        for w in self._frm_results.winfo_children():
            w.destroy()
        self._lbl_status.config(text='')

    def _pdf_row(self, idx: int, fp: str, ptype: str):
        if ptype.startswith('custom:'):
            label = ptype[7:][:8]
            cfg   = (label, '#5b21b6', '#ede9fe')   # violet pour banques custom
        else:
            cfg = {
                'sg':      ('SG',      CLR['sg_fg'],  CLR['sg_bg']),
                'revolut': ('Revolut', CLR['rev_fg'], CLR['rev_bg']),
                'inconnu': ('?',       CLR['unk_fg'], CLR['unk_bg']),
            }.get(ptype, ('?', CLR['unk_fg'], CLR['unk_bg']))

        row = tk.Frame(self._pdf_inner, bg=CLR['card_bg'],
                       pady=6, padx=10, cursor='hand2')
        row.pack(fill='x')

        badge = tk.Label(row, text=cfg[0], fg=cfg[1], bg=cfg[2],
                         font=('Segoe UI', 8, 'bold'), padx=8, pady=2)
        badge.pack(side='left')

        name = tk.Label(row, text=f"  {Path(fp).name}",
                        bg=CLR['card_bg'], fg=CLR['text'],
                        font=('Segoe UI', 9), anchor='w')
        name.pack(side='left', fill='x', expand=True)

        sep = tk.Frame(self._pdf_inner, bg=CLR['border'], height=1)
        sep.pack(fill='x')

        def select(e, i=idx, r=row):
            self._selected_pdf_idx = i
            for c in self._pdf_inner.winfo_children():
                if isinstance(c, tk.Frame) and c != sep:
                    c.config(bg=CLR['card_bg'])
                    for w in c.winfo_children():
                        if isinstance(w, tk.Label) and w.cget('bg') != w.cget('bg'):
                            pass
            r.config(bg='#eff6ff')
            for w in r.winfo_children():
                if w.cget('bg') == CLR['card_bg']:
                    w.config(bg='#eff6ff')

        for w in [row, name]:
            w.bind('<Button-1>', select)

    # ── Analyse ───────────────────────────────────────────────────────────────

    def _analyze(self):

        self._lbl_status.config(text='⏳  Analyse en cours…', fg=CLR['warning'])
        self._btn_disable(self._btn_analyze)
        self.update()

        if not PARSER_OK:
            messagebox.showerror('Erreur', 'parse_finances.py introuvable.'); return

        try:
            raw_new, errors = [], []
            for fp, ptype in self.pdf_list:
                try:
                    if ptype == 'sg':
                        raw_new.extend(parse_sg_pdf(fp, user_rules=get_builtin_rules('SG')))
                    elif ptype == 'revolut':
                        raw_new.extend(parse_revolut_pdf(fp, user_rules=get_builtin_rules('Revolut')))
                    elif ptype.startswith('custom:'):
                        bank_name = ptype[7:]
                        configs   = load_bank_configs()
                        if bank_name in configs:
                            raw_new.extend(parse_generic_pdf(fp, configs[bank_name]))
                        else:
                            errors.append(f"Config introuvable pour '{bank_name}' : {Path(fp).name}")
                    else:
                        # Banque inconnue → ouvrir la fenêtre de configuration
                        dlg = BankSetupDialog(self, fp)
                        if dlg.result:
                            raw_new.extend(parse_generic_pdf(fp, dlg.result))
                            # Mettre à jour le badge dans la liste
                            for i, (pfp, _) in enumerate(self.pdf_list):
                                if pfp == fp:
                                    self.pdf_list[i] = (fp, f"custom:{dlg.result['name']}")
                            self._refresh_pdf_list()
                        else:
                            errors.append(f"Configuration annulée : {Path(fp).name}")
                except Exception as e:
                    errors.append(f"{Path(fp).name} : {e}")

            bank_by_year, manual_all = load_existing(self.tx_dir)
            really_new, already_here = dedup_new_vs_existing(raw_new, bank_by_year)
            duplicates, clean_manual = find_manual_duplicates(really_new, manual_all)
            recat_candidates         = find_recat_candidates(already_here, bank_by_year)

            self.analysis = dict(bank_by_year=bank_by_year, really_new=really_new,
                                 already_here=already_here, duplicates=duplicates,
                                 clean_manual=clean_manual, errors=errors,
                                 recat_candidates=recat_candidates)
            self._show_results()
        except Exception as e:
            self._lbl_status.config(text=f'❌  Erreur : {e}', fg=CLR['danger'])
        finally:
            self._btn_enable(self._btn_analyze, CLR['primary'], '#ffffff')

    # ── Résultats ─────────────────────────────────────────────────────────────

    def _show_results(self):
        a  = self.analysis
        nn = len(a['really_new'])
        ns = len(a['already_here'])
        nd = len(a['duplicates'])
        nm = len(a['clean_manual'])
        nc = len(a['recat_candidates'])

        # Status line
        if nn == 0 and nd == 0 and nc == 0:
            self._lbl_status.config(
                text='Tout est déjà à jour - aucune nouvelle transaction.',
                fg=CLR['success'])
        else:
            self._lbl_status.config(
                text="Analyse terminée - vérifiez les résultats ci-dessous.",
                fg=CLR['success'])

        # Zone résultats
        for w in self._frm_results.winfo_children():
            w.destroy()
        self._frm_results.pack(fill='both', expand=True)

        # ── Bandeau de stats ──
        stats_card = self._card(self._frm_results, "ÉTAPE 2 - Résultats")
        stats_row = tk.Frame(stats_card, bg=CLR['card_bg'])
        stats_row.pack(fill='x', pady=(0,10))

        self._stat_pill(stats_row, f"✅  {nn} nouvelle{'s' if nn!=1 else ''}",
                        CLR['success'], '#dcfce7').pack(side='left', padx=(0,8))
        self._stat_pill(stats_row, f"⏭  {ns} déjà présente{'s' if ns!=1 else ''}",
                        CLR['muted'], '#f1f5f9').pack(side='left', padx=(0,8))
        self._stat_pill(stats_row, f"⚠️  {nd} doublon{'s' if nd!=1 else ''}",
                        CLR['warning'], '#fef9c3').pack(side='left', padx=(0,8))
        if nc > 0:
            self._stat_pill(stats_row, f"🔄  {nc} recatégorisation{'s' if nc!=1 else ''}",
                            '#7c3aed', '#f5f3ff').pack(side='left')

        # ── Notebook ──
        nb_frame = tk.Frame(stats_card, bg=CLR['card_bg'])
        nb_frame.pack(fill='both', expand=True)

        nb = ttk.Notebook(nb_frame)
        nb.pack(fill='both', expand=True)

        t1 = tk.Frame(nb, bg=CLR['card_bg'])
        nb.add(t1, text=f"  ✅ Nouvelles ({nn})  ")
        self._tab_tx(t1, a['really_new'])

        t2 = tk.Frame(nb, bg=CLR['card_bg'])
        nb.add(t2, text=f"  ⚠️ Doublons ({nd})  ")
        self._tab_dup(t2, a['duplicates'])

        t3 = tk.Frame(nb, bg=CLR['card_bg'])
        nb.add(t3, text=f"  📋 Manuelles ({nm})  ")
        self._tab_tx(t3, a['clean_manual'])

        t4 = tk.Frame(nb, bg=CLR['card_bg'])
        nb.add(t4, text=f"  🔄 Catégories ({nc})  ")
        self._tab_recat(t4, a['recat_candidates'])
        if nc > 0:
            nb.select(t4)   # ouvrir ce tab en premier si des recatégorisations existent

        if a['errors']:
            tk.Label(stats_card, text='⚠️  ' + '  |  '.join(a['errors']),
                     bg=CLR['card_bg'], fg=CLR['danger'],
                     font=('Segoe UI', 8)).pack(anchor='w', pady=(6,0))

        if nn > 0 or nd > 0 or nc > 0:
            self._btn_enable(self._btn_confirm, CLR['success'], '#ffffff')

        self.geometry('880x720')

    def _stat_pill(self, parent, text, fg, bg):
        return tk.Label(parent, text=text, fg=fg, bg=bg,
                        font=('Segoe UI', 9, 'bold'),
                        padx=12, pady=5)

    # ── Tab transactions ──────────────────────────────────────────────────────

    def _tab_tx(self, parent, txs: list):
        if not txs:
            tk.Label(parent, text='Aucune transaction.',
                     fg=CLR['muted'], bg=CLR['card_bg'],
                     font=('Segoe UI', 9)).pack(pady=24)
            return

        cols   = ('date', 'label', 'montant', 'categorie', 'compte')
        hdrs   = ('Date ⇅', 'Description ⇅', 'Montant ⇅', 'Catégorie ⇅', 'Compte ⇅')
        widths = (88, 220, 82, 180, 110)

        wrap = tk.Frame(parent, bg=CLR['card_bg'])
        wrap.pack(fill='both', expand=True, padx=2, pady=4)

        tree = ttk.Treeview(wrap, columns=cols, show='headings', height=10)

        # Colonnes triables
        sort_state: dict = {c: False for c in cols}   # False = ascendant

        def sort_col(col: str):
            desc = sort_state[col]
            items = list(tree.get_children(''))
            # Tri numérique pour montant, alphabétique sinon
            try:
                if col == 'montant':
                    items.sort(
                        key=lambda iid: float(tree.set(iid, col)
                                              .replace('\xa0', '').replace('+', '').replace(' €', '')),
                        reverse=desc)
                else:
                    items.sort(key=lambda iid: tree.set(iid, col).lower(), reverse=desc)
            except Exception:
                items.sort(key=lambda iid: tree.set(iid, col).lower(), reverse=desc)
            for idx, iid in enumerate(items):
                tree.move(iid, '', idx)
                # Rafraîchir la couleur alternée (garde cr/db, change odd/even)
                old_tags = tree.item(iid, 'tags')
                cr_db = 'cr' if any(t.startswith('cr') for t in old_tags) else 'db'
                tree.item(iid, tags=(f'{cr_db}_{"odd" if idx%2==0 else "even"}',))
            sort_state[col] = not desc

        for col, hdr, w in zip(cols, hdrs, widths):
            tree.heading(col, text=hdr, command=lambda c=col: sort_col(c))
            tree.column(col, width=w, minwidth=50,
                        anchor='e' if col == 'montant' else 'w')

        # Couleurs alternées + crédit/débit
        tree.tag_configure('cr_odd',  foreground=CLR['success'], background='#f0fdf4')
        tree.tag_configure('cr_even', foreground=CLR['success'], background='#ffffff')
        tree.tag_configure('db_odd',  foreground=CLR['danger'],  background='#fff5f5')
        tree.tag_configure('db_even', foreground=CLR['danger'],  background='#ffffff')

        for idx, t in enumerate(txs):
            m   = float(t.get('montant', 0))
            tag = f'{"cr" if m >= 0 else "db"}_{"odd" if idx % 2 == 0 else "even"}'
            tree.insert('', 'end',
                values=(t.get('date',''), t.get('label',''),
                        _fmt_montant(m), t.get('categorie',''), t.get('compte','')),
                tags=(tag,))

        sb = ttk.Scrollbar(wrap, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        tk.Label(parent, text=f"  {len(txs)} transaction{'s' if len(txs)!=1 else ''}  -  clic sur en-tête pour trier",
                 bg=CLR['card_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8)).pack(anchor='w', pady=(2, 4))

    # ── Tab doublons ──────────────────────────────────────────────────────────

    def _tab_dup(self, parent, duplicates: list):
        self.replace_vars = []
        self.recat_vars   = []

        if not duplicates:
            tk.Label(parent, text='Aucun doublon détecté ✓',
                     fg=CLR['success'], bg=CLR['card_bg'],
                     font=('Segoe UI', 9, 'bold')).pack(pady=24)
            return

        tk.Label(parent,
            text=("Cochez ✓ pour remplacer la saisie manuelle par la donnée du relevé (recommandé).\n"
                  "Décochez pour conserver votre version manuelle."),
            fg=CLR['muted'], bg=CLR['card_bg'], font=('Segoe UI', 8),
            justify='left').pack(anchor='w', padx=10, pady=(8,6))

        # Zone scrollable
        outer = tk.Frame(parent, bg=CLR['card_bg'])
        outer.pack(fill='both', expand=True, padx=4)
        canvas = tk.Canvas(outer, bg=CLR['card_bg'], highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg=CLR['card_bg'])
        inner.bind('<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0,0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        bind_canvas_scroll(canvas, inner)

        # En-tête colonnes
        hdr_row = tk.Frame(inner, bg='#f8fafc')
        hdr_row.pack(fill='x', padx=2)
        for txt, w in [('', 32), ('✓', 30), ('Version relevé', 360), ('Version manuelle', 360)]:
            tk.Label(hdr_row, text=txt, bg='#f8fafc', fg=CLR['muted'],
                     font=('Segoe UI', 8, 'bold'), width=0,
                     anchor='w').pack(side='left', padx=5, pady=4)

        for dup in duplicates:
            var = tk.BooleanVar(value=True)
            self.replace_vars.append(var)
            row = tk.Frame(inner, bg=CLR['card_bg'])
            row.pack(fill='x', padx=2, pady=1)

            tk.Checkbutton(row, variable=var,
                           bg=CLR['card_bg'], activebackground=CLR['card_bg'],
                           cursor='hand2').pack(side='left', padx=8)

            for tx, fg in [(dup['new'], '#0369a1'), (dup['manual'], '#b45309')]:
                m = float(tx.get('montant', 0))
                s = f"{tx.get('date','')}   {tx.get('label','')[:28]:<28}   {_fmt_montant(m)}"
                tk.Label(row, text=s, fg=fg, bg=CLR['card_bg'],
                         font=('Courier New', 8),
                         anchor='w', width=48).pack(side='left', padx=6)

            tk.Frame(inner, bg=CLR['border'], height=1).pack(fill='x', padx=2)

    # ── Tab recatégorisation ──────────────────────────────────────────────────

    def _tab_recat(self, parent, candidates: list):
        self.recat_vars: list[tk.BooleanVar] = []

        if not candidates:
            tk.Label(parent,
                     text="Aucune recatégorisation détectée.\n"
                          "Les catégories de toutes les transactions déjà importées\n"
                          "correspondent aux règles actuelles.",
                     bg=CLR['card_bg'], fg=CLR['muted'],
                     font=('Segoe UI', 9), justify='center').pack(expand=True, pady=30)
            return

        # En-tête explicatif
        tk.Label(parent,
                 text="Ces transactions sont déjà dans le vault mais leur catégorie a changé "
                      "selon vos règles actuelles.\nCochez celles à mettre à jour.",
                 bg=CLR['card_bg'], fg=CLR['muted'],
                 font=('Segoe UI', 8), justify='left').pack(anchor='w', padx=12, pady=(8, 4))

        # Boutons tout cocher / décocher
        ctrl = tk.Frame(parent, bg=CLR['card_bg'])
        ctrl.pack(anchor='w', padx=12, pady=(0, 6))
        def _all(v):
            for bv in self.recat_vars: bv.set(v)
        tk.Button(ctrl, text="Tout cocher",   font=('Segoe UI', 8), relief='solid', bd=1,
                  bg=CLR['border'], fg=CLR['text'], cursor='hand2', padx=8, pady=2,
                  command=lambda: _all(True)).pack(side='left', padx=(0, 6))
        tk.Button(ctrl, text="Tout décocher", font=('Segoe UI', 8), relief='solid', bd=1,
                  bg=CLR['border'], fg=CLR['text'], cursor='hand2', padx=8, pady=2,
                  command=lambda: _all(False)).pack(side='left')

        # Zone scrollable
        canvas = tk.Canvas(parent, bg=CLR['card_bg'], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg=CLR['card_bg'])
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        win_id = canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        _activate_canvas_scroll(canvas)
        parent.bind('<Destroy>', lambda e: _deactivate_canvas_scroll(canvas))

        for cand in candidates:
            new_tx    = cand['new_tx']
            stored_tx = cand['stored_tx']
            old_cat   = stored_tx.get('categorie', '?')
            new_cat   = new_tx.get('categorie', '?')
            m         = float(new_tx.get('montant', 0))

            var = tk.BooleanVar(value=True)
            self.recat_vars.append(var)

            row = tk.Frame(inner, bg=CLR['card_bg'], pady=4)
            row.pack(fill='x', padx=8)

            tk.Checkbutton(row, variable=var,
                           bg=CLR['card_bg'], activebackground=CLR['card_bg'],
                           cursor='hand2').pack(side='left')

            info = tk.Frame(row, bg=CLR['card_bg'])
            info.pack(side='left', fill='x', expand=True)

            # Ligne 1 : date + libellé + montant
            top = tk.Frame(info, bg=CLR['card_bg'])
            top.pack(fill='x')
            tk.Label(top, text=new_tx.get('date', ''), fg=CLR['muted'],
                     bg=CLR['card_bg'], font=('Segoe UI', 8), width=11, anchor='w').pack(side='left')
            tk.Label(top, text=new_tx.get('label', '')[:45], fg=CLR['text'],
                     bg=CLR['card_bg'], font=('Segoe UI', 9, 'bold'), anchor='w').pack(side='left', padx=(4, 8))
            color = CLR['success'] if m >= 0 else CLR['danger']
            tk.Label(top, text=_fmt_montant(m), fg=color,
                     bg=CLR['card_bg'], font=('Segoe UI', 9, 'bold')).pack(side='right')

            # Ligne 2 : ancienne catégorie → nouvelle catégorie
            bot = tk.Frame(info, bg=CLR['card_bg'])
            bot.pack(fill='x')
            tk.Label(bot, text=old_cat, fg='#d20f39',
                     bg=CLR['card_bg'], font=('Segoe UI', 8)).pack(side='left', padx=(0, 4))
            tk.Label(bot, text='→', fg=CLR['muted'],
                     bg=CLR['card_bg'], font=('Segoe UI', 8)).pack(side='left', padx=(0, 4))
            tk.Label(bot, text=new_cat, fg='#40a02b',
                     bg=CLR['card_bg'], font=('Segoe UI', 8, 'bold')).pack(side='left')

            tk.Frame(inner, bg=CLR['border'], height=1).pack(fill='x', padx=8)

    # ── Confirmation ──────────────────────────────────────────────────────────

    def _confirm(self):
        a = self.analysis
        if not a: return

        # Appliquer les recatégorisations cochées directement dans bank_by_year
        for i, cand in enumerate(a.get('recat_candidates', [])):
            if i < len(getattr(self, 'recat_vars', [])) and self.recat_vars[i].get():
                stored_tx = cand['stored_tx']
                new_tx    = cand['new_tx']
                stored_tx['categorie'] = new_tx.get('categorie', stored_tx['categorie'])
                stored_tx['type']      = new_tx.get('type',      stored_tx.get('type', 'dépense'))

        manual_to_keep = list(a['clean_manual'])
        n_replaced = 0
        for i, dup in enumerate(a['duplicates']):
            if i < len(self.replace_vars) and self.replace_vars[i].get():
                n_replaced += 1
            else:
                manual_to_keep.append(dup['manual'])

        nn = len(a['really_new'])
        nm = len(manual_to_keep)
        dlg = ConfirmImportDialog(self, nn, n_replaced, nm)
        if not dlg.result: return

        try:
            n_files = save_import(self.tx_dir, a['bank_by_year'], a['really_new'], manual_to_keep)
            SuccessImportDialog(self, nn, n_replaced, n_files)
            self._btn_disable(self._btn_confirm)
            self._lbl_status.config(text='✓  Import terminé avec succès.', fg=CLR['success'])
        except Exception as e:
            messagebox.showerror("Erreur lors de l'écriture", str(e))


# ═════════════════════════════════════════════════════════════════════════════
# Point d'entrée
# ═════════════════════════════════════════════════════════════════════════════

def main():
    # ── DPI Windows : doit être appelé AVANT toute création de fenêtre ────────
    setup_dpi_awareness()

    vault = get_vault_root()
    tx    = find_tx_dir(vault)
    if not tx.exists():
        root = tk.Tk(); root.withdraw()
        if messagebox.askyesno('Dossier introuvable',
                f"Le dossier Transactions est introuvable :\n{tx}\n\n"
                "Voulez-vous sélectionner manuellement le vault ?"):
            root.destroy()
            # Lancer l'app quand même - l'utilisateur pourra changer le vault via 📁
            ImportApp().mainloop()
        else:
            root.destroy()
        return
    ImportApp().mainloop()

if __name__ == '__main__':
    main()
