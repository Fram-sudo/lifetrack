# 📊 Lifetrack

Un vault Obsidian pour suivre tes **finances**, **médias** (films, animés, séries, jeux, lectures), **commandes** et ta **pratique sportive** (import Hevy).

> Développé et maintenu par [Fram-sudo](https://github.com/Fram-sudo)

---

## 📥 Installation

### Option A - Git (recommandé)

Nécessite [Git](https://git-scm.com/downloads) installé sur ta machine.

```bash
git clone https://github.com/Fram-sudo/lifetrack.git
```

Avantage : les mises à jour sont plus rapides (voir section [Mise à jour](#-mise-à-jour)).

### Option B - Téléchargement ZIP

1. Clique sur le bouton vert **Code** en haut de cette page
2. Clique sur **Download ZIP**
3. Décompresse l'archive où tu veux

### Ouvrir dans Obsidian

1. Lance Obsidian
2. Clique sur **Ouvrir un autre vault** → **Ouvrir un dossier comme vault**
3. Sélectionne le dossier `lifetrack`
4. Active les plugins communautaires quand Obsidian le propose (nécessaire pour le dashboard Finances)

---

## 🔄 Mise à jour

Quand une nouvelle version du vault est disponible, tu peux récupérer les changements en un double-clic.

### Lancer la mise à jour

- **Windows** : double-clique sur `update.bat` à la racine du vault
- **Linux / Mac** : ouvre un terminal dans le dossier du vault et lance `./update.sh`

Le script télécharge automatiquement les dernières versions des fichiers système depuis GitHub et les remplace sur ta machine.

### Ce qui est mis à jour

Les fichiers "système" que je maintiens : scripts d'import, guides, templates, MOC, dashboard, code du module Finances.

### Ce qui est conservé quoi qu'il arrive

| Élément | Détail |
|---------|--------|
| 💰 **Tes transactions** | Le dossier `Transactions/` n'est jamais touché |
| 🏋️ **Tes séances de sport** | Le dossier `2 - Domaines/Sport/Data/` (imports Hevy) n'est jamais touché |
| ⚙️ **Ta config bancaire** | `bank_configs.json` (tes banques configurées, tes règles de catégorisation) est préservé |
| 📂 **Ta config script** | `script_config.json` (chemin de ton vault) est préservé |
| 🔑 **Ta clé API TMDB** | `_Système/Config.md` n'est jamais écrasé |
| 📝 **Tes notes personnelles** | Tout ce que tu as écrit toi-même dans le vault |
| 🗂️ **Tes paramètres Finances** | Frontmatter de `Finances.md` : tes comptes, catégories, soldes initiaux, devise — jamais écrasés |

> **En clair :** la mise à jour remplace le "moteur" (scripts, code, guides), mais jamais tes données.

### Après la mise à jour

Rafraîchis les notes concernées dans Obsidian avec **Ctrl+R** (ou **Cmd+R** sur Mac).

---

## 🗂️ Structure du vault

```
lifetrack/
├── 0 - Inbox/                        ← Tes notes temporaires
├── 2 - Domaines/
│   ├── Finances/
│   │   ├── 💰 Finances.md            ← Dashboard budgétaire
│   │   └── Transactions/             ← Tes données JSON (ignorées par git)
│   ├── Sport/
│   │   ├── 🏋️ Sport.md               ← Dashboard sport (import Hevy)
│   │   └── Data/                     ← Tes séances JSON (ignorées par git)
│   ├── Commandes/                    ← Suivi de commandes
│   ├── Médias/                       ← Films, animés, séries, jeux, lectures
│   └── Tâches.md                     ← Liste de tâches (utilisée par le Dashboard)
├── _Système/
│   ├── Config.md                     ← Ta clé API TMDB (non versionnée)
│   ├── Scripts/
│   │   ├── import_releves.py         ← Script d'import bancaire (SG/Revolut natifs + banques génériques)
│   │   ├── parse_finances.py         ← Parsers PDF Société Générale / Revolut
│   │   ├── create_fiches_medias.py   ← Import en masse de fiches médias (AniList/TMDB)
│   │   ├── lancer_import.sh          ← Lanceur Linux/Mac
│   │   ├── lancer_import.bat         ← Lanceur Windows
│   │   ├── bank_configs.json         ← Ta config bancaire (non versionnée)
│   │   ├── Hevy/                     ← Import des séances Hevy (CSV)
│   │   ├── QuickAdd/                 ← Scripts QuickAdd (ouverture Dashboard, etc.)
│   │   └── update.py                 ← Script de mise à jour
│   ├── Templates/                    ← Templates de notes
│   ├── MOC/                          ← Maps of Content
│   ├── Guide Lifetrack.md            ← Documentation complète
│   └── TUTO - Import de relevés bancaires.md
├── Dashboard.md                      ← Page d'accueil
├── update.bat                        ← Mise à jour Windows
└── update.sh                         ← Mise à jour Linux/Mac
```

---

## 💰 Module Finances

### Fonctionnement

Le dashboard Finances (`2 - Domaines/Finances/💰 Finances.md`) lit tes fichiers JSON de transactions et affiche :
- Solde par compte
- Répartition des dépenses (graphique en donut)
- Historique des transactions filtrables

### Importer des relevés bancaires

Le script `import_releves.py` reconnaît nativement les relevés **Société Générale** et **Revolut** (catégorisation automatique incluse), et permet aussi de configurer n'importe quelle autre banque via mapping de colonnes (bouton "⚙️ Gérer les banques").

**Lancement :**
- Windows : double-clique sur `_Système/Scripts/Import Relevés.bat`
- Linux/Mac : double-clique sur `_Système/Scripts/lancer_import.sh` ou lance-le depuis un terminal

**Première utilisation :**
1. Lance le script — il installe automatiquement les dépendances (`pdfplumber`, `ttkbootstrap`)
2. Clique sur **⚙️ Gérer les banques** pour configurer ta banque (format PDF, colonnes, etc.)
3. Importe tes relevés PDF

La documentation complète est dans `_Système/TUTO - Import de relevés bancaires.md`.

### Prérequis

- Python 3.8 ou supérieur ([télécharger](https://www.python.org/downloads/))
- Sur Linux : `sudo apt install python3-tk` si tkinter est absent

---

## 🎬 Module Médias

Suivi de films, animés, séries, jeux vidéo, mangas et lectures via des templates de notes dédiés.

Les MOC (Maps of Content) dans `_Système/MOC/` centralisent et affichent des statistiques pour chaque catégorie.

### Auto-remplissage TMDB / AniList

Les templates `TPL - Film.md`, `TPL - Série.md` et `TPL - Animé.md` peuvent remplir automatiquement titre, synopsis, affiche, genres, etc. à partir de TMDB (films/séries) et AniList (animés).

1. Crée une clé API gratuite sur [themoviedb.org](https://www.themoviedb.org/settings/api) (section "API")
2. Renseigne-la dans `_Système/Config.md` (`tmdb_api_key: "ta-clé-ici"`) — ce fichier n'est jamais écrasé par les mises à jour
3. Crée une nouvelle fiche média (via QuickAdd) et renseigne l'ID TMDB ou AniList : les champs se remplissent seuls

Pour importer plusieurs fiches d'un coup, utilise `_Système/Scripts/create_fiches_medias.py` (renseigne tes identifiants dans le script puis lance-le).

---

## 🏋️ Module Sport

Le dashboard `2 - Domaines/Sport/🏋️ Sport.md` affiche tes séances de musculation importées depuis [Hevy](https://www.hevyapp.com/) : rythme d'entraînement, progression par exercice (records), historique des séances.

**Import d'un export Hevy :**
1. Dans l'app Hevy : Profil → ⚙️ Paramètres → Exporter les données (tu reçois un CSV par e-mail)
2. Lance `_Système/Scripts/Hevy/lancer_hevy.sh` (Linux/Mac) ou le script Python directement (Windows)
3. Sélectionne le CSV exporté — les séances sont fusionnées dans `2 - Domaines/Sport/Data/hevy_<année>.json` (jamais écrasé par les mises à jour)

---

## ❓ Problèmes fréquents

**Le dashboard Finances ne s'affiche pas**
→ Active les plugins communautaires dans Obsidian (Paramètres → Plugins communautaires → Activer).

**"Python introuvable" au lancement du script**
→ Installe Python depuis [python.org](https://www.python.org/downloads/). Sur Windows, coche bien "Add Python to PATH" lors de l'installation.

**"tkinter manquant" sur Linux**
→ Lance : `sudo apt install python3-tk`

**La mise à jour échoue**
→ Vérifie ta connexion internet. Le script télécharge les fichiers depuis GitHub — si GitHub est inaccessible, réessaie plus tard.

---

## 📄 Licence

Libre d'utilisation personnelle.
