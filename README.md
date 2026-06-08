# 📊 Lifetrack

Un vault Obsidian pour suivre tes **finances**, **médias** (films, animés, séries, jeux, lectures) et **commandes**.

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
| ⚙️ **Ta config bancaire** | `bank_configs.json` (tes banques configurées) est préservé |
| 📂 **Ta config script** | `script_config.json` (chemin de ton vault) est préservé |
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
│   └── Finances/
│       ├── 💰 Finances.md            ← Dashboard budgétaire
│       └── Transactions/             ← Tes données JSON (ignorées par git)
├── _Système/
│   ├── Scripts/
│   │   ├── import_releves.py         ← Script d'import bancaire
│   │   ├── lancer_import.sh          ← Lanceur Linux/Mac
│   │   ├── lancer_import.bat         ← Lanceur Windows
│   │   ├── bank_configs.json         ← Ta config bancaire (non versionnée)
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

Le script `import_releves.py` permet d'importer des relevés PDF de n'importe quelle banque.

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
