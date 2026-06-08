# Lifetrack

Un vault Obsidian pour suivre tes finances, médias (films, animés, séries, jeux, lectures) et commandes.

## Installation

### Option 1 - Git (recommandé, mises à jour faciles)

```bash
git clone https://github.com/OWNER/lifetrack.git
```

### Option 2 - ZIP

Clique sur **Code → Download ZIP**, décompresse, puis ouvre le dossier dans Obsidian.

---

Ouvre Obsidian → **Ouvrir un autre vault** → sélectionne le dossier `lifetrack`.
Active les plugins communautaires quand Obsidian le propose.

## Mise à jour

Double-clique sur `update.bat` (Windows) ou lance `./update.sh` (Linux/Mac).

Le script télécharge les dernières versions des fichiers système (scripts, templates, notes système, code Finances.md) **sans toucher à ton contenu personnel** (transactions, notes, configuration).

## Structure

```
lifetrack/
├── 0 - Inbox/              ← Tes notes temporaires
├── 2 - Domaines/
│   └── Finances/           ← Suivi budgétaire
│       └── Transactions/   ← Tes données (ignorées par git)
├── _Système/
│   ├── Scripts/            ← Scripts d'import bancaire
│   ├── Templates/          ← Templates de notes
│   └── MOC/                ← Maps of Content
├── update.sh / update.bat  ← Script de mise à jour
└── Dashboard.md            ← Page d'accueil
```

## Import bancaire

Voir `_Système/TUTO - Import de relevés bancaires.md` pour la documentation complète.
