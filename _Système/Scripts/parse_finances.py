#!/usr/bin/env python3
"""Parser SG + Revolut → JSON unifié (règles génériques, sans données personnelles).

Ce module est importé par import_releves.py. Il expose parse_sg_pdf() et
parse_revolut_pdf() qui transforment un relevé PDF Société Générale ou Revolut
en une liste de transactions structurées.

Les règles de catégorisation ci-dessous sont volontairement génériques
(enseignes nationales/internationales connues). Pour affiner la catégorisation
avec tes propres commerces locaux, utilise le gestionnaire de règles intégré à
import_releves.py (bouton "Gérer les règles" - SG / Revolut) : tes réglages
sont sauvegardés dans bank_configs.json, qui reste local et n'est jamais
écrasé par les mises à jour du vault.
"""
import re
from datetime import datetime
import pdfplumber

# ── Catégorisation par règles utilisateur ─────────────────────────────────────

_CAT_TYPES = {
    '🎓 Bourse & Aides sociales': 'revenu',
    '💰 Revenus divers':          'revenu',
    '💵 Dépôt espèces':           'revenu',
    '💵 Revenus divers':           'revenu',
    '💵 Remboursement in':         'revenu',
    '💼 Salaire':                  'revenu',
    '🔙 Avoir / Remboursement achat': 'avoir',
    '💰 Économies':                'épargne',
    '💸 Retrait économies':        'épargne-retrait',
    '🔄 Transfert interne in':     'revenu',
    '🔄 Transfert interne out':    'dépense',
}

def _cat_type(cat: str) -> str:
    return _CAT_TYPES.get(cat, 'dépense')

def apply_user_rules(label: str, raw_ctx: str, user_rules: list, is_credit: bool = None):
    """Vérifie les règles utilisateur avant la logique hardcodée.
    - is_credit=True  → transaction crédit (argent reçu)
    - is_credit=False → transaction débit  (argent dépensé)
    - is_credit=None  → direction inconnue, toutes les règles s'appliquent
    Retourne (categorie, type) ou None si aucune règle ne correspond."""
    ctx = re.sub(r'\s+', '', (raw_ctx + ' ' + label).upper())
    for rule in user_rules:
        # Filtre direction
        direction = rule.get('direction', 'tous')
        if direction == 'crédit' and is_credit is False:
            continue
        if direction == 'débit' and is_credit is True:
            continue
        # Correspondance mots-clés
        kws = [k.strip().upper().replace(' ', '')
               for k in rule.get('keywords', '').split(',') if k.strip()]
        if kws and any(kw in ctx for kw in kws):
            cat = rule.get('categorie', '❓ Autre')
            return cat, _cat_type(cat)
    return None

# ─── MERCHANT NORMALIZATION (enseignes nationales/internationales) ────────────
MERCHANT_MAP = [
    (r'(?i)E\.?LECLERC', 'E.Leclerc'),
    (r'(?i)CARREFOUR\s*MARKET', 'Carrefour Market'),
    (r'(?i)CARREFOUR(?!\s*MARKET)', 'Carrefour'),
    (r'(?i)\bLIDL\b', 'Lidl'), (r'(?i)\bALDI\b', 'Aldi'),
    (r'(?i)INTERMARCHE', 'Intermarché'),
    (r'(?i)MONOPRIX', 'Monoprix'), (r'(?i)FRANPRIX', 'Franprix'),
    (r'(?i)SUPER\s*U\b', 'Super U'), (r'(?i)AUCHAN', 'Auchan'),
    (r'(?i)UBER\s*\*?\s*EATS?', 'Uber Eats'), (r'(?i)DELIVEROO', 'Deliveroo'),
    (r'(?i)MCDONALD', "McDonald's"), (r'(?i)\bKFC\b', 'KFC'),
    (r'(?i)BURGER\s*KING', 'Burger King'),
    (r'(?i)\bSNCF\b', 'SNCF'), (r'(?i)\bRATP\b', 'RATP'),
    (r'(?i)BLABLACAR', 'BlaBlaCar'), (r'(?i)FLIXBUS', 'FlixBus'),
    (r'(?i)TRANSAVIA', 'Transavia'), (r'(?i)EASYJET', 'EasyJet'),
    (r'(?i)RYANAIR', 'Ryanair'), (r'(?i)AIR\s*FRANCE', 'Air France'),
    (r'(?i)UBER\s*\*?\s*TRIP|^Uber$', 'Uber'),
    (r'(?i)GOOGLE\s*PLAY|GOOGLEPLAY', 'Google Play'),
    (r'(?i)XSOLLA', 'Xsolla BNE'),
    (r'(?i)INSTANT\s*GAMING', 'Instant Gaming'),
    (r'(?i)STEAMPURCHASE|\bSTEAM\b', 'Steam'),
    (r'(?i)DOKKANBATTLE', 'Dokkan Battle'),
    (r'(?i)SUPERCELL', 'Supercell'),
    (r'(?i)PAYSAFECARD', 'Paysafecard'),
    (r'(?i)CGR', 'CGR Cinémas'), (r'(?i)PATH[EÉ]', 'Cinéma Pathé'),
    (r'(?i)NINTENDO', 'Nintendo'),
    (r'(?i)SONY\s*INTERACT|PLAYSTATION', 'PlayStation Store'),
    (r'(?i)LASTPASS', 'LastPass'),
    (r'(?i)CLAUDE\s*AI|ANTHROPIC', 'Claude AI'),
    (r'(?i)AMAZON\s*PRIME', 'Amazon Prime'),
    (r'(?i)\bNETFLIX\b', 'Netflix'), (r'(?i)\bSPOTIFY\b', 'Spotify'),
    (r'(?i)FREE\s*MOBILE', 'Free Mobile'), (r'(?i)\bSOSH\b', 'Sosh'),
    (r'(?i)REVOLUT\s*PREMIUM|PREMIUM\s*PLAN', 'Revolut Premium Plan'),
    (r'(?i)CRUNCHYROLL', 'Crunchyroll'),
    (r'(?i)UBER\s*\*?\s*ONE', 'Uber One'),
    (r'(?i)CYBERGHOST', 'CyberGhost VPN'),
    (r'(?i)AMAZON(?!\s*PRIME)', 'Amazon'),
    (r'(?i)\bVINTED\b|MGP\*VINTED|MGP\*', 'Vinted'),
    (r'(?i)BACK[- ]?MARKET', 'Back Market'),
    (r'(?i)\bLDLC\b', 'LDLC'),
    (r'(?i)RHINOSHIELD', 'RhinoShield'),
    (r'(?i)TREATWELL', 'Treatwell'),
    (r'(?i)PHARMAC', 'Pharmacie'),
    (r'(?i)MUTUELLE', 'Mutuelle'),
    (r'(?i)\bALPIQ\b', 'Alpiq'),
    (r'(?i)PAYPAL', 'PayPal'),
    (r'(?i)MANGOPAY', 'Mangopay'),
    (r'(?i)XPOLLENS', 'Xpollens'),
    (r'(?i)ORANGEMONEY|ORANGE\s*MONEY', 'Orange Money'),
    (r'(?i)TRANSFERWISE|TRANSF\w*WISE', 'TransferWise'),
    (r'(?i)DRFIP', 'DRFIP'),
    (r'(?i)CROUS', 'CROUS'),
    (r'(?i)LAPOSTE', 'La Poste'),
]

def normalize_label(raw):
    raw = raw.strip()
    for pattern, name in MERCHANT_MAP:
        if re.search(pattern, raw):
            return name
    return raw


# ─── CATEGORIZATION ────────────────────────────────────────────────────────────
def categorize(label, raw_ctx, is_credit, amount=0.0, user_rules=None):
    if user_rules:
        res = apply_user_rules(label, raw_ctx, user_rules, is_credit=is_credit)
        if res:
            return res
    ctx = re.sub(r'\s+', '', raw_ctx.upper())

    # ── REMBT = avoir ──
    if 'REMBT' in ctx:
        return ('🔙 Avoir / Remboursement achat', 'avoir')

    # ── Abonnements Revolut (AVANT check générique 'REVOLUT') ──
    if any(x in ctx for x in ['REVOLUTPREMIUM','REVOLUTPLUS','REVOLUTMETAL','REVOLUTULTRA','REVOLUTSTANDARD']):
        return ('📺 Abonnements', 'dépense')

    # ── Transferts internes entre comptes du même utilisateur (ex: SG ↔ Revolut) ──
    # Détection générique via motif "Revolut ####" (référence de virement),
    # sans dépendre d'un numéro de compte/IBAN personnel codé en dur.
    revolut_topup = bool(re.search(r'\brevolut\s+\d{3,4}\b', raw_ctx, re.I)) or \
                    bool(re.search(r'Revolut\s*\*{0,2}\d{3,4}\*?', raw_ctx))
    if revolut_topup:
        return ('🔄 Transfert interne in', 'revenu') if is_credit else ('🔄 Transfert interne out', 'dépense')

    # ── Remboursement virement ──
    if 'REMBOURSEMENTVIREMENT' in ctx:
        return ('🔄 Transfert interne in', 'revenu')

    # ── Virements émis SG→SG (virements européens LOGITEL) ──
    if re.search(r'(?:000001)?VIREUROPE', ctx) and 'REVOLUT' not in ctx:
        return ('💸 Retrait économies', 'épargne-retrait') if is_credit else ('💸 Envoi d\'argent', 'dépense')

    # ── Épargne Revolut Pockets ──
    if re.search(r'pocket|saving', raw_ctx, re.I):
        return ('💸 Retrait économies', 'épargne-retrait') if is_credit else ('💰 Économies', 'épargne')

    # ── Revenus ──
    if is_credit:
        if any(x in ctx for x in ['CAF','CAISSEALLOCATION','DROITSFAMILLE']):
            return ('🎓 Bourse & Aides sociales', 'revenu')
        if any(x in ctx for x in ['BOURSE','CROUS','DRFIP','ACADEMIE','ENSEIGNEMENTSUP']):
            return ('🎓 Bourse & Aides sociales', 'revenu')
        if any(x in ctx for x in ['SALAIRE','PAYE','TRAITEMENT']):
            return ('💼 Salaire', 'revenu')
        if any(x in ctx for x in ['VRSTGAB','VERSTESPGAB','OPENBANKING','DEPOSIT']):
            return ('💵 Dépôt espèces', 'revenu')
        if any(x in ctx for x in ['BACKMARKET','VINTED','MGP','MANGOPAY','XPOLLENS']):
            return ('💰 Revenus divers', 'revenu')
        if any(x in ctx for x in ['AVANTAGECOMMERCIAL','REGULARISATIONDECOMMISSION','REMISECHEQUE']):
            return ('🔙 Avoir / Remboursement achat', 'avoir')
        return ('💰 Revenus divers', 'revenu')

    # ── Dépenses ──
    if any(x in ctx for x in ['ALPIQ','EDF','ENGIE']):
        return ('🏠 Loyer & Charges', 'dépense')
    if any(x in ctx for x in ['MUTUELLE','PHARMAC']):
        return ('🏥 Santé', 'dépense')
    if any(x in ctx for x in ['NETFLIX','SPOTIFY','CRUNCHYROLL','LASTPASS','CYBERGHOST',
                                'CLAUDE','ANTHROPIC','APPLE','UBERONE','AMAZONPRIME']):
        return ('📺 Abonnements', 'dépense')
    if any(x in ctx for x in ['SNCF','RATP','BLABLACAR','FLIXBUS','TRANSAVIA',
                                'EASYJET','RYANAIR','AIRFRANCE','UBER']):
        return ('🚗 Transport', 'dépense')
    if any(x in ctx for x in ['LECLERC','CARREFOUR','LIDL','ALDI','INTERMARCHE','MONOPRIX',
                                'SUPERU','AUCHAN','UBEREATS','DELIVEROO',
                                'MCDONALD','KFC','BURGERKING']):
        return ('🛒 Alimentation', 'dépense')
    if any(x in ctx for x in ['RETRAITDAB','RETRAITGAB','ATM','WITHDRAWAL']):
        return ('🏧 Retrait espèces', 'dépense')
    if any(x in ctx for x in ['GOOGLEPLAY','XSOLLA','INSTANTGAMING','STEAMPURCHASE','STEAM',
                                'DOKKANBATTLE','SUPERCELL','PAYSAFECARD','NINTENDO',
                                'SONYINTERACT','CGR','PATHE','UGC','PLAYSTATION','GAMING']):
        return ('🎮 Loisirs & Jeux', 'dépense')
    if any(x in ctx for x in ['AMAZON','VINTED','MGP','BACKMARKET','LDLC','RHINOSHIELD','PAYPAL']):
        return ('🛍️ Shopping', 'dépense')
    if 'TREATWELL' in ctx:
        return ('💇 Coiffure & Beauté', 'dépense')
    if any(x in ctx for x in ['COTISATIONMENS','COTISANNU','FRAISVIRINSTANT','FRAISPAIEMENT',
                                'COMMISSIOND','FEE']):
        return ('💳 Frais bancaires', 'dépense')
    if any(x in ctx for x in ['ORANGEMONEY','TRANSFERWISE']):
        return ('💸 Envoi d\'argent', 'dépense')
    if any(x in ctx for x in ['VIRINSTANTANEE','VIREUROPEEN','PAYLIB']):
        return ('💸 Envoi d\'argent', 'dépense')
    if 'PRELEVEMENT' in ctx:
        return ('🏠 Loyer & Charges', 'dépense')
    return ('❓ Autre', 'dépense')


# ─── SG HELPERS ───────────────────────────────────────────────────────────────
def parse_fr(s):
    s = re.sub(r'\.(?=\d{3})', '', s.strip())
    return float(s.replace(',', '.'))

SG_TX = re.compile(
    r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\S.*?)\s+([\d\.]+,\d{2})\*?\s*$'
)

SG_CREDIT_KW = [
    'VIRRECU', 'VIR RECU', 'VIREMENTRECU', 'AVANTAGECOMMERCIAL', 'AVANTAGE COMMERCIAL',
    'REMBOURSEMENTVIREMENT', 'VIREMENT RECU', 'CREDIT',
    'VIRINSTRE', 'VRSTGAB', 'VERSTESPGAB',
    'REMISECHEQUE', 'REMBT', 'REGULARISATIONDECOMMISSION',
]

def build_sg_label(desc, cont_lines):
    cont = ' '.join(cont_lines)
    d = desc.strip()

    if re.match(r'VIRRECU|VIRINSTRE', d, re.I):
        de = re.search(r'DE:\s*(.+)', cont, re.I)
        motif = re.search(r'MOTIF:\s*(.+)', cont, re.I)
        if de:
            src = de.group(1).strip()
            if motif and motif.group(1).strip() not in ['.', '..', '...', '']:
                return normalize_label(src + ' - ' + motif.group(1).strip()[:40])
            return normalize_label(src)
        return normalize_label(d)

    if re.match(r'CARTEX', d, re.I):
        merchant = re.sub(r'^CARTEX\d{4}(?:REMBT)?(?:\d{2}/\d{2})?(?:RETRAITDABSG\S+)?', '', d, flags=re.I).strip()
        if re.search(r'RETRAITDAB', d, re.I):
            return 'Retrait espèces (DAB)'
        return normalize_label(merchant)

    if re.match(r'VRST|VERSTE', d, re.I):
        return 'Versement espèces (GAB)'

    if re.match(r'PRELEVEMENTEURO', d, re.I):
        de = re.search(r'DE:\s*(.+)', cont, re.I)
        return normalize_label(de.group(1).strip()) if de else normalize_label(d)

    if re.match(r'(?:000001)?VIREURO|(?:000001)?VIRINSTANT', d, re.I):
        pour = re.search(r'POUR:\s*(.+)', cont, re.I)
        motif = re.search(r'MOTIF:\s*(.+)', cont, re.I)
        if pour:
            label = pour.group(1).strip()
            if motif and motif.group(1).strip() not in ['.', '..', '...', '']:
                return normalize_label(label + ' - ' + motif.group(1).strip()[:40])
            return normalize_label(label)
        return normalize_label(d)

    if re.match(r'FRAISPAIEMENT|FRAISVIRINST', d, re.I):
        return 'Frais bancaires'
    if re.match(r'REGULARISATION', d, re.I):
        return 'Régularisation de commission'
    if re.match(r'AVANTAGE', d, re.I):
        return 'Avantage commercial'

    return normalize_label(d)


def parse_sg_pdf(filepath, user_rules=None):
    transactions = []
    with pdfplumber.open(filepath) as pdf:
        lines = []
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                lines.extend(t.split('\n'))

    SKIP = {'SOLDE', 'TOTAUX', 'NOUVEAU', 'Page', 'SociétéGénérale', 'suite>>>',
            'Depuis', 'Pour toute', 'agence', 'Médiateur', 'BGSY', 'EMEDA',
            'RELEVÉ', 'COMPTE', 'VOS CONTACTS', 'envoin', 'Votre',
            'Changements', 'Livret', 'Capital', 'Développement', 'Epargne'}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = SG_TX.match(line)
        if not m:
            i += 1
            continue

        date_op, _, desc, amt_str = m.group(1), m.group(2), m.group(3), m.group(4)
        try:
            amount = parse_fr(amt_str)
        except:
            i += 1
            continue

        cont_lines = []
        j = i + 1
        while j < len(lines):
            nxt = lines[j].strip()
            if re.match(r'^\d{2}/\d{2}/\d{4}', nxt):
                break
            if any(s in nxt for s in SKIP):
                break
            if nxt:
                cont_lines.append(nxt)
            j += 1
        i = j

        desc_up = desc.upper().replace(' ', '')
        is_credit = any(kw in desc_up for kw in SG_CREDIT_KW)
        is_rembt = 'REMBT' in desc_up

        day, month, year = date_op.split('/')
        date_iso = f"{year}-{month}-{day}"
        label = build_sg_label(desc, cont_lines)
        effective_credit = is_credit or is_rembt
        cat, typ = categorize(label, desc + ' ' + ' '.join(cont_lines), effective_credit, amount, user_rules=user_rules)
        if is_rembt:
            cat, typ = ('🔙 Avoir / Remboursement achat', 'avoir')
        montant = round(amount if effective_credit else -amount, 2)

        transactions.append({
            'date': date_iso, 'label': label, 'montant': montant,
            'categorie': cat, 'type': typ, 'compte': 'courant',
        })

    return transactions


# ─── REVOLUT PARSER ───────────────────────────────────────────────────────────
# Format: "MMM D, YYYY Description €amount -?€balance"
REV_TX = re.compile(
    r'^(\w{3})\s+(\d{1,2}),\s+(\d{4})\s+(.+?)\s+€([\d,]+\.\d{2})\s+(-?)€([\d,]+\.\d{2})\s*$'
)

def revolut_is_credit(desc, cont, prev_bal, new_bal):
    """Determine if transaction is credit using balance delta first, then heuristics."""
    if prev_bal is not None:
        delta = new_bal - prev_bal
        if abs(delta) > 0.001:
            return delta > 0
    # Heuristic fallback
    ctx = (desc + ' ' + cont).lower()
    credit_kw = ['received', 'cashback', 'refund', 'top-up', 'topup', 'top up',
                  'open banking deposit', 'payment from', 'from ', 'salary',
                  'caf', 'bourse', 'deposit', 'back?market', 'backmarket']
    debit_kw = ['sent', 'payment to', 'to ', 'card payment', 'atm',
                 'fee', 'subscription', 'exchange', 'withdrawal']
    for kw in credit_kw:
        if kw in ctx:
            return True
    for kw in debit_kw:
        if kw in ctx:
            return False
    return None  # unknown

def parse_revolut_pdf(filepath, user_rules=None):
    transactions = []
    with pdfplumber.open(filepath) as pdf:
        lines = []
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                lines.extend(t.split('\n'))

    # Extraire le solde d'ouverture depuis le résumé (ex: "Account (Current Account) €43.59 ...")
    # Sans ça, prev_balance=0 inverse le signe de la première transaction sur les relevés courts
    full_text = '\n'.join(lines)
    opening_balance = 0.0
    ob_m = re.search(r'Account\s+\(Current\s+Account\)\s+€([\d,]+\.\d{2})', full_text)
    if ob_m:
        opening_balance = float(ob_m.group(1).replace(',', ''))

    # Find "Account transactions" section start
    acct_start = 0
    for idx, ln in enumerate(lines):
        if 'Account transactions from' in ln:
            acct_start = idx + 2  # skip header row
            break

    # Stop at Pockets section
    pockets_stop = len(lines)
    for idx, ln in enumerate(lines[acct_start:], acct_start):
        if 'Personal and Group Pockets' in ln:
            pockets_stop = idx
            break

    prev_balance = opening_balance
    CONT_KW = ('To:', 'From:', 'Reference:', 'Card:', 'Exchange rate:', 'Fee:')

    i = acct_start
    while i < pockets_stop:
        ln = lines[i].strip()
        m = REV_TX.match(ln)
        if not m:
            i += 1
            continue

        month_str, day, year = m.group(1), m.group(2), m.group(3)
        desc_raw = m.group(4).strip()
        tx_amount = float(m.group(5).replace(',', ''))
        _bal_sign = -1 if m.group(6) == '-' else 1
        new_balance = _bal_sign * float(m.group(7).replace(',', ''))

        # Collect continuation lines
        cont_parts = []
        j = i + 1
        while j < pockets_stop and j < i + 6:
            nxt = lines[j].strip()
            if REV_TX.match(nxt):
                break
            if any(nxt.startswith(k) for k in CONT_KW):
                cont_parts.append(nxt)
                j += 1
            else:
                break
        i = j

        cont = ' '.join(cont_parts)

        try:
            dt = datetime.strptime(f"{month_str} {day} {year}", "%b %d %Y")
            date_iso = dt.strftime('%Y-%m-%d')
        except:
            prev_balance = new_balance
            continue

        is_cr = revolut_is_credit(desc_raw, cont, prev_balance, new_balance)
        if is_cr is None:
            is_cr = new_balance > prev_balance
        prev_balance = new_balance

        label = normalize_label(desc_raw)
        cat, typ = categorize(label, desc_raw + ' ' + cont, is_cr, tx_amount, user_rules=user_rules)
        montant = round(tx_amount if is_cr else -tx_amount, 2)

        transactions.append({
            'date': date_iso, 'label': label, 'montant': montant,
            'categorie': cat, 'type': typ, 'compte': 'compte-secondaire',
            'balance_after': round(new_balance, 2),
        })

    return transactions
