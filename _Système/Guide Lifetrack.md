---
type: guide
created: 2026-06-05
tags: [guide, lifetrack]
obsidianUIMode: preview
---

# 📖 Guide Lifetrack

Bienvenue dans **Lifetrack** - un vault Obsidian pour suivre tes médias (films, animés, séries, mangas, livres, jeux vidéo), tes commandes en ligne et tes finances personnelles, le tout avec des statistiques détaillées.

Ce guide t'explique tout, de l'installation à l'utilisation quotidienne.

---

## 📋 Table des matières

1. [Installation et premier lancement](#1--installation-et-premier-lancement)
2. [Se repérer dans le vault](#2--se-repérer-dans-le-vault)
3. [Ajouter et gérer des médias](#3--ajouter-et-gérer-des-médias)
4. [Films](#4--films)
5. [Animés et Séries TV](#5--animés-et-séries-tv)
6. [Mangas, Manwhas et Manhuas](#6--mangas-manwhas-et-manhuas)
7. [Romans et Livres](#7--romans-et-livres)
8. [Jeux Vidéo](#8--jeux-vidéo)
9. [Commandes](#9--commandes)
10. [Finances](#10--finances)
11. [Statistiques](#11--statistiques)
12. [Explorateur](#12--explorateur)
13. [Raccourcis clavier](#13--raccourcis-clavier)
14. [Problèmes courants](#14--problèmes-courants)

---

## 1 - Installation et premier lancement

### Étape 1 : Ouvrir le vault

1. Lance **Obsidian**
2. Clique sur **Ouvrir un dossier comme vault**
3. Sélectionne le dossier `Lifetrack`
4. Obsidian s'ouvre sur le **Dashboard** automatiquement

### Étape 2 : Activer les plugins

Au premier lancement, Obsidian affiche un avertissement sur les plugins communautaires.

1. Va dans **Paramètres** (icône ⚙️ en bas à gauche, ou `Ctrl+,`)
2. Clique sur **Plugins communautaires**
3. Clique sur **Activer le mode non restreint** et confirme
4. Dans la liste des plugins installés, active chacun en cliquant sur le toggle

> Tous les plugins sont déjà présents dans le dossier - **pas besoin de les télécharger**.

### Plugins installés

| Plugin | Rôle |
|--------|------|
| **Dataview** | Affiche toutes les données dynamiques (MOCs, stats, Dashboard) |
| **Templater** | Applique automatiquement les bons templates à la création d'une note |
| **QuickAdd** | Menu rapide pour créer un média ou une commande (`Ctrl+Q`) |
| **Homepage** | Ouvre le Dashboard au démarrage |
| **Obsidian Banners** | Bannière visuelle en haut des fiches animés/séries et du Dashboard |
| **Icon Folder** | Icônes visuelles sur les dossiers dans la barre latérale |
| **Style Settings** | Paramètres de personnalisation du thème |
| **Table Editor** | Édition facilitée des tableaux Markdown |
| **Tag Wrangler** | Gestion des tags (renommer, fusionner…) |

### Étape 3 : Vérifier les paramètres Dataview

1. **Paramètres** → **Plugins communautaires** → **Dataview** → icône ⚙️
2. Vérifie que **"Enable DataviewJS"** et **"Enable Inline DataviewJS"** sont activés
3. L'intervalle de rafraîchissement peut rester à 2500 ms

---

## 2 - Se repérer dans le vault

### Le Dashboard

Le Dashboard est la **page d'accueil** du vault. Il s'ouvre automatiquement au démarrage (`Ctrl+D` pour y revenir à tout moment).

Il contient :
- Une **barre de stats** : nombre de médias en cours, total de notes
- Un **hub** de 8 cartes cliquables vers chaque section
- Une **heatmap** d'activité annuelle (une case par jour, colorée selon le nombre de notes créées)

### Structure des dossiers

```
Lifetrack/
├── 0 - Inbox/              ← Notes créées sans catégorie définie
├── 2 - Domaines/
│   ├── Médias/
│   │   ├── Films/
│   │   ├── Animés/
│   │   ├── Séries/
│   │   ├── Manga & Manwha/
│   │   ├── Romans & Livres/
│   │   └── Jeux Vidéo/
│   ├── Commandes/
│   └── Finances/
│       └── Transactions/
└── _Système/               ← Ne pas toucher (templates, scripts, configs)
```

Chaque dossier média contient des **sous-dossiers par statut** (ex : `Animés/En cours`, `Animés/Terminé`…). La note se déplace automatiquement dans le bon sous-dossier quand tu changes le statut.

### Les MOCs (Maps of Content)

Les MOCs sont les pages de visualisation de chaque section. Ils affichent toutes tes entrées sous forme de **cartes avec cover**, avec des filtres et une barre de recherche.

Accès depuis le Dashboard ou la barre latérale (`_Système/MOC/`).

---

## 3 - Ajouter et gérer des médias

### Créer une fiche

**Méthode recommandée - QuickAdd :**

1. Appuie sur `Ctrl+Q`
2. Sélectionne **🎬 Nouveau média**
3. Choisis le type (Animé, Film, Série, Manga, Roman, Jeu Vidéo)
4. Entre le **titre** → appuie sur Entrée
5. La fiche s'ouvre automatiquement en mode lecture

**Méthode alternative :** crée un nouveau fichier directement dans le bon sous-dossier (ex : `2 - Domaines/Médias/Animés/À voir/`). Le template s'applique automatiquement grâce à Templater.

### Interface d'une fiche

Toutes les fiches s'ouvrent en **mode lecture**. En haut de chaque fiche, une barre d'actions propose des boutons :

- **✏ Modifier** - ouvre un formulaire pour modifier les champs (titre, statut, note, genre, cover…)
- **➕ Session** - ajouter une session de visionnage/lecture/jeu (selon le type)
- **🌅 Bannière** *(animés/séries)* - définir une image bannière en haut de la fiche
- **🎬 Saisons** *(animés/séries)* - gérer le nombre de saisons

### Modifier une fiche

Clique sur **✏ Modifier**. Un panneau s'ouvre avec tous les champs éditables :

- Les champs modifiés sont sauvegardés en cliquant sur **✓ Sauvegarder**
- Changer le **statut** déplace automatiquement la note dans le bon sous-dossier

### Ajouter une cover

Dans **✏ Modifier**, champ **Cover** :
- Colle une **URL d'image** (ex. depuis MyAnimeList, IGDB, Goodreads…)
- Ou entre le nom d'un fichier image stocké dans `_Système/Attachments/`

La cover apparaît dans les MOCs sous forme de vignette.

### Supprimer une fiche

Clic droit sur la note dans la barre latérale → **Mettre à la corbeille**.

---

## 4 - Films

### Créer une fiche film

`Ctrl+Q` → Nouveau média → **🎬 Film** → entrer le titre

Lors de la création, Obsidian te demande le **statut initial** :
- **À voir** - dans ta liste de films à regarder
- **En cours** - tu le regardes actuellement
- **Vu** - déjà regardé
- **Abandonné** - arrêté en cours de route

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Titre du film |
| **Cover** | URL ou fichier image |
| **Genre** | Genre(s) du film |
| **Réalisateur** | Réalisateur |
| **Statut** | À voir / En cours / Vu / Abandonné |
| **Date de visionnage** | Date à laquelle tu l'as regardé |
| **Note** | Note de 0 à 10 |

### Sections de la fiche

- **Synopsis** - résumé du film
- **Mon avis** - tes impressions personnelles
- **Ce que je retiens** - les moments marquants, citations…
- **Films similaires** - liens vers d'autres fiches

---

## 5 - Animés et Séries TV

Les animés et les séries TV fonctionnent de la même manière - ils partagent le même système de saisons et de sessions.

### Créer une fiche

`Ctrl+Q` → Nouveau média → **🎌 Animé** ou **📺 Série TV** → entrer le titre

Obsidian demande d'abord le **statut** puis le **nombre de saisons**.

### Statuts disponibles

| Statut | Signification |
|--------|--------------|
| **À voir** | Dans ta liste d'attente |
| **En cours** | Tu le regardes actuellement |
| **Terminé** | Terminé |
| **Abandonné** | Arrêté définitivement |
| **En pause** | Mis en pause temporairement |

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Titre de l'animé/série |
| **Cover** | URL ou fichier image (format portrait 2:3) |
| **Bannière** | URL ou fichier image (format paysage, affiché en haut) |
| **Studio / Chaîne** | Studio de production ou chaîne TV |
| **Genre** | Genre(s) |
| **Saisons** | Nombre de saisons |
| **Statut** | À voir / En cours / Terminé / Abandonné / En pause |
| **Note** | Note de 0 à 10 |

### Ajouter une session

Clique sur **➕ Session**. Un formulaire apparaît :

- **Date** - date de la session (par défaut aujourd'hui)
- **Saison** - numéro de la saison regardée
- **Épisode début** - premier épisode de la session
- **Épisode fin** - dernier épisode de la session (peut être identique au début si 1 seul épisode)

Les sessions sont enregistrées dans le frontmatter et apparaissent dans un tableau sur la fiche. Chaque session peut être éditée ou supprimée.

### Gérer les saisons

Clique sur **🎬 Saisons** pour :
- Voir le résumé de chaque saison
- Ajouter/supprimer des saisons
- Modifier le nombre d'épisodes par saison

### Bannière

Clique sur **🌅 Bannière** pour entrer l'URL d'une image au format paysage. Elle s'affiche en haut de la fiche comme une bannière décorative.

---

## 6 - Mangas, Manwhas et Manhuas

### Créer une fiche

`Ctrl+Q` → Nouveau média → **📖 Manga / Manwha** → entrer le titre

Obsidian te demande de choisir le **type** (Manga, Manwha ou Manhua) puis le **statut**.

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Titre de l'œuvre |
| **Cover** | URL ou fichier image |
| **Auteur** | Auteur / dessinateur |
| **Genre** | Genre(s) |
| **Statut** | À lire / En cours / Terminé / Abandonné |
| **Chapitres lus** | Nombre de chapitres lus au total |
| **Chapitres total** | Nombre de chapitres total de l'œuvre (optionnel, affiche une barre de progression) |
| **Note** | Note de 0 à 10 |

### Ajouter une session de lecture

Clique sur **➕ Session** :

- **Date** - date de la session
- **Chapitre début** - premier chapitre lu
- **Chapitre fin** - dernier chapitre lu

Le champ **Chapitres lus** se met à jour automatiquement.

---

## 7 - Romans et Livres

### Créer une fiche

`Ctrl+Q` → Nouveau média → **📚 Roman & Livre** → entrer le titre

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Titre du livre |
| **Cover** | URL ou fichier image |
| **Auteur** | Auteur |
| **Genre** | Genre(s) |
| **Statut** | À lire / En cours / Terminé / Abandonné |
| **Tomes** | Nombre de tomes (pour les séries) |
| **Pages** | Nombre de pages total |
| **Pages lues** | Nombre de pages lues |
| **Date début** | Date de début de lecture |
| **Date fin** | Date de fin de lecture |
| **Note** | Note de 0 à 10 |

### Sections de la fiche

- **Synopsis** - résumé du livre
- **Mon avis** - impressions personnelles
- **Citations** - passages marquants
- **Livres similaires** - liens vers d'autres fiches

---

## 8 - Jeux Vidéo

### Créer une fiche

`Ctrl+Q` → Nouveau média → **🎮 Jeu Vidéo** → entrer le titre

### Statuts disponibles

| Statut | Signification |
|--------|--------------|
| **Backlog** | Dans ta liste de jeux à faire |
| **En cours** | Tu y joues actuellement |
| **Terminé** | Terminé |
| **Abandonné** | Arrêté définitivement |

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Titre du jeu |
| **Cover** | URL ou fichier image |
| **Studio** | Développeur / éditeur |
| **Genre** | Genre(s) |
| **Plateforme** | Sur quelle(s) plateforme(s) tu y joues |
| **Opus** | Numéro dans une série (ex : 3 pour le 3ème opus) |
| **Statut** | Backlog / En cours / Terminé / Abandonné |
| **Heures jouées** | Total d'heures jouées (calculé automatiquement depuis les sessions) |
| **Note** | Note de 0 à 10 |

### Ajouter une session de jeu

Clique sur **➕ Session** :

- **Date** - date de la session
- **Durée** - durée au format `HH:MM` (ex : `1:30` pour 1h30, `0:45` pour 45 minutes)

Les heures s'accumulent automatiquement. Le total s'affiche sur la fiche et dans les statistiques.

---

## 9 - Commandes

### Créer une commande

`Ctrl+Q` → **🛒 Nouvelle commande** → entrer un nom descriptif (ex : `Amazon - Casque Sony`)

### Champs disponibles

| Champ | Description |
|-------|-------------|
| **Titre** | Description de la commande |
| **Site** | Site marchand (Amazon, Fnac, etc.) |
| **Montant** | Montant total en euros |
| **Numéro de commande** | Référence de suivi |
| **Statut** | Commandé / Expédié / Livré / Annulé |
| **Date de commande** | Date à laquelle tu as commandé |
| **Date de livraison estimée** | Date estimée de réception |

### Suivi des statuts

| Statut | Couleur | Signification |
|--------|---------|--------------|
| 🛒 Commandé | Orange | Commande passée, pas encore expédiée |
| 📦 Expédié | Bleu | En cours de livraison |
| ✅ Livré | Vert | Reçu |
| ❌ Annulé | Gris | Annulé ou retourné |

### MOC Commandes

Le MOC Commandes permet de voir toutes tes commandes avec des filtres par :
- **Statut** (Tout, Commandé, Expédié, Livré, Annulé)
- **Année**
- **Mois**
- **Site marchand**
- **Recherche** par nom

La barre de stats affiche le total de commandes, le montant total dépensé, et la répartition par statut.

---

## 10 - Finances

### Premier démarrage

La section Finances démarre **entièrement vide**. La première chose à faire est de configurer tes comptes.

1. Ouvre **💰 Finances** depuis le Dashboard
2. Clique sur **⚙️ Paramètres** (en haut à droite)
3. Dans l'onglet **Comptes**, clique sur **➕ Ajouter un compte**

### Configurer un compte

Pour chaque compte, renseigne :
- **Nom** - ex : "Compte courant", "Épargne"
- **Banque** - ex : "BNP", "Revolut"
- **Type** - courant, épargne, etc.
- **Solde initial** - le solde de départ (peut être mis à 0 et ajusté manuellement)

### Ajouter une transaction manuellement

En bas de la page Finances, quatre boutons permettent d'accéder directement au bon formulaire selon le type d'opération :

| Bouton | Usage |
|--------|-------|
| **➕ Dépense** | Une dépense classique (courses, loyer, abonnement…) |
| **💵 Revenu** | Un revenu (salaire, remboursement reçu, bourse…) |
| **💰 Mettre de côté** | Virer de l'argent vers ton épargne |
| **💸 Piocher** | Retirer de l'argent depuis ton épargne |

Le formulaire demande : **Date**, **Libellé**, **Montant** (toujours positif, le signe est appliqué automatiquement), **Catégorie** et **Compte**.

### Virements internes entre comptes

Si tu as plusieurs comptes (ex : compte courant + Revolut), tu peux enregistrer un virement entre eux sans fausser tes stats.

Utilise les catégories **🔄 Transfert interne out** (compte qui envoie) et **🔄 Transfert interne in** (compte qui reçoit). Ces transactions sont automatiquement exclues des revenus et dépenses affichés dans les statistiques - elles n'apparaissent que dans la section **Économies & mouvements**.

> **Exemple :** tu envoies 200 € de ton compte courant vers Revolut.
> - Transaction 1 : -200 € · Catégorie "🔄 Transfert interne out" · Compte courant
> - Transaction 2 : +200 € · Catégorie "🔄 Transfert interne in" · Revolut

### Mettre de l'argent de côté / Piocher dans ses économies

L'épargne est traitée séparément des revenus et dépenses. Le solde épargne est affiché dans la section **Économies** de la page Finances.

- **💰 Mettre de côté** → catégorie "💰 Économies" → déduit du solde courant, ajoute au solde épargne
- **💸 Piocher** → catégorie "💸 Retrait économies" → ajoute au solde courant, réduit le solde épargne

> **Exemple :** tu mets 300 € de côté en début de mois, puis tu en retires 50 € pour une dépense imprévue.
> - Transaction 1 : Mettre de côté · 300 € · "💰 Économies"
> - Transaction 2 : Piocher · 50 € · "💸 Retrait économies"
> → Solde épargne net : +250 €

### Avoirs et remboursements d'achat

Quand tu reçois un avoir ou un remboursement suite à un retour produit, utilise la catégorie **🔙 Avoir / Remboursement achat**. Ce montant vient en déduction des dépenses (pas en revenu) - tes stats reflètent ainsi ce que tu as réellement dépensé.

> **Exemple :** tu retournes un article commandé à 45 €. Tu saisis un avoir de 45 € avec la catégorie "🔙 Avoir / Remboursement achat". Tes dépenses du mois sont réduites de 45 €.

### Catégories prédéfinies

Les catégories sont déjà configurées au démarrage :

**Revenus :** Revenus, Salaire, Remboursement in, Transfert interne in, Bourse & Aides sociales

**Dépenses :** Alimentation, Jeux & Loisirs, Abonnements, Transport, Logement, Santé, Formation, Divers, Commandes, Envoi d'argent, Remboursement out, Retrait espèces, Transfert interne out, Frais bancaires, Coiffure & Beauté, Sport & Activités, Dons & Cadeaux

**Épargne :** Économies, Retrait économies

**Avoir :** Avoir / Remboursement achat

Tu peux ajouter/modifier les catégories via **⚙️ Paramètres** → onglet **Catégories**.

### Importer des relevés bancaires (PDF)

Le moyen le plus rapide d'alimenter tes finances est d'importer tes relevés PDF.

**Prérequis :** Python 3 installé + `pip install ttkbootstrap pdfplumber`

**Lancer le script :**
- **Linux** : double-clique sur `Import Relevés.desktop` depuis ton gestionnaire de fichiers, ou `lancer_import.sh`, ou `python3 import_releves.py` dans un terminal
- **Windows** : double-clique sur `Import Relevés.bat` (ou `lancer_import.bat`)

> Les scripts installent automatiquement `pdfplumber` et `ttkbootstrap` si manquants.

**Banques supportées nativement :**
- Société Générale
- Revolut

**Autres banques :**
Clique sur **⚙️ Gérer les banques** dans la fenêtre du script. Tu peux configurer n'importe quelle banque en définissant le format de tes relevés CSV/PDF.

**Changer le chemin du vault :**
Si tu utilises Syncthing ou si le vault est à un emplacement différent, clique sur l'icône **📁** dans l'en-tête du script pour sélectionner le bon dossier.

### Stockage des transactions - fichiers JSON par année

Les transactions sont stockées dans `2 - Domaines/Finances/Transactions/` sous forme de fichiers JSON, un par année :

```
Transactions/
├── 💰 2024.json
├── 💰 2025.json
└── 💰 2026.json
```

Chaque fichier contient toutes les transactions de l'année - qu'elles viennent d'un import de relevé ou d'une saisie manuelle. Le script distingue les deux avec un champ interne `_manual` : les transactions manuelles sont conservées même quand tu réimportes un relevé.

**Déduplication automatique :** le script détecte les doublons à la date, au montant et au libellé près - tu peux réimporter le même relevé plusieurs fois sans risque de créer des doublons.

> Ne modifie pas ces fichiers JSON manuellement - passe toujours par l'interface de Lifetrack ou par le script d'import.

### Navigation et filtres

La page Finances propose plusieurs filtres :

- **Filtre période** : Ce mois / Ce trimestre / Cette année / Tout / Année spécifique
- **Filtre compte** : voir les transactions d'un seul compte
- **Recherche** : chercher par libellé

### Sections de la page Finances

- **Solde actuel** - calculé dynamiquement depuis toutes les transactions (hors épargne)
- **Budgets mensuels** - comparatif budget prévu vs dépenses réelles par catégorie
- **Revenus & dépenses par mois** - graphique en barres
- **Répartition des dépenses** - donut chart par catégorie
- **Économies** - suivi du solde épargne séparé
- **Liste des transactions** - toutes les transactions avec tri et suppression

### Gérer les budgets

Dans **⚙️ Paramètres** → onglet **Budgets** :
- Associe un montant mensuel à chaque catégorie de dépense
- La page Finances affichera la progression budget/réel pour chaque catégorie

### Mode blur

Un bouton 👁 permet de masquer les montants pour plus de confidentialité (utile en public).

---

## 11 - Statistiques

La page **📊 Statistiques** (accessible depuis le Dashboard) centralise toute l'activité de tes médias.

### Vue globale

Affiche les données de **toutes tes sessions** sur la période choisie.

**Sélecteur de période :**
- Aujourd'hui
- Cette semaine
- Ce mois
- Cette année
- Tout
- 📅 Plage… - sélectionner une plage de dates personnalisée

**Cartes de stats :**
- 🎌 Épisodes d'animés regardés
- 📺 Épisodes de séries regardés
- 🎮 Heures jouées
- 📖 Chapitres lus
- 🎬 Films vus

**Graphique d'activité** - barres représentant le nombre de sessions par jour/semaine/mois selon la période.

**Heatmap** - calendrier annuel montrant tes sessions jour par jour. Survole une case pour voir le détail.

**Activité récente** - grille des médias consultés récemment avec leur cover et la date de la dernière session.

### Vue individuelle

Clique sur **🔍 Vue individuelle** pour chercher un titre spécifique et voir :

- **Métrique clé** - total d'épisodes/heures/chapitres sur la période
- **Heatmap individuelle** - activité spécifique à ce titre
- **Graphique de sessions** - avec choix de granularité (par session, par semaine, par mois)
- **Liste de toutes les sessions** - avec date et détail

Pour ouvrir le détail d'un titre, clique sur sa carte depuis l'activité récente (vue globale) ou depuis la grille (vue individuelle).

---

## 12 - Explorateur

La page **🔍 Explorateur** permet de **rechercher dans tout le vault** avec des filtres avancés.

### Modes de recherche

- **Mode titre** (par défaut) - recherche instantanée par nom de note
- **Mode contenu** - recherche dans le texte de toutes les notes (plus lent)

Bascule entre les deux modes avec les boutons en haut de la barre de recherche.

### Filtres disponibles

Clique sur **⚙ Filtres** pour accéder aux filtres avancés :

- **Domaine** - Tout / Médias / Commandes / Finances / Système
- **Statut** - filtrer par statut (en cours, terminé, à voir…)
- **Période** - notes créées ou modifiées sur une période
- **Note minimale** - afficher seulement les notes avec une note ≥ seuil
- **Tri** - par date de modification, nom A→Z, nom Z→A

### Résultats

Les résultats s'affichent en liste avec le nom, le type, le dossier et la date de modification. Clique sur une entrée pour ouvrir la note.

---

## 13 - Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+D` | Ouvrir le Dashboard |
| `Ctrl+Q` | QuickAdd (nouveau média ou commande) |
| `Ctrl+T` | Insérer un template manuellement |
| `Ctrl+O` | Ouverture rapide (chercher et ouvrir une note) |
| `Ctrl+Shift+F` | Recherche globale dans tout le vault |
| `Ctrl+G` | Afficher le graph view |
| `Ctrl+,` | Ouvrir les paramètres |
| `Ctrl+\` | Afficher/masquer la barre latérale gauche |
| `Ctrl+Alt+←` | Page précédente (historique) |
| `Ctrl+Alt+→` | Page suivante (historique) |
| `Ctrl+B` | Mettre en gras |
| `Ctrl+I` | Mettre en italique |
| `Ctrl+Entrée` | Cocher/décocher une case |

---

## 14 - Problèmes courants

**Les MOCs et le Dashboard n'affichent rien / affichent des erreurs**
→ Va dans **Paramètres → Dataview** et vérifie que **Enable DataviewJS** et **Enable Inline DataviewJS** sont activés. Recharge le vault (`Ctrl+R`).

**Les templates ne s'appliquent pas automatiquement**
→ Va dans **Paramètres → Templater** et vérifie que **"Trigger on file creation"** est activé et que le dossier de templates est bien `_Système/Templates`.

**QuickAdd ne fonctionne pas**
→ Vérifie que le plugin QuickAdd est bien activé. Appuie sur `Ctrl+Q` - si rien ne se passe, tente `Ctrl+P` et cherche "QuickAdd".

**Le Dashboard ne s'ouvre pas au démarrage**
→ Va dans **Paramètres → Homepage** et configure la page sur "Dashboard" et la vue sur "Reading view".

**Le script d'import ne se lance pas**
→ Vérifie que Python 3 est installé (`python3 --version` dans un terminal). Installe ensuite les dépendances : `pip install ttkbootstrap`.

**Les covers ne s'affichent pas dans les MOCs**
→ Vérifie que l'URL de la cover est bien une URL directe vers une image (terminant par `.jpg`, `.png`, `.webp`…). Les URLs de pages web (ex : page MyAnimeList) ne fonctionnent pas - il faut l'URL de l'image elle-même (clic droit sur l'image → "Copier l'adresse de l'image").

**Les heures jouées d'un jeu ne s'additionnent pas**
→ Le format attendu est `H:MM` (ex : `1:30` pour 1h30, `0:45` pour 45 min). Évite d'écrire "1h30" ou "90 min".

**Une note s'est retrouvée dans "0 - Inbox"**
→ C'est normal si elle a été créée sans passer par QuickAdd ou un dossier avec template. Déplace-la manuellement dans le bon dossier - le template s'appliquera à la prochaine ouverture.

**Le vault est lent**
→ Le mode "Tout" des Finances peut être plus gourmand avec beaucoup de transactions. C'est normal. Si l'ensemble du vault est lent, augmente l'intervalle de rafraîchissement Dataview : **Paramètres → Dataview → Refresh interval** → mettre 5000 (5 secondes).

---

## 💡 Conseils et astuces

- **Covers depuis MyAnimeList** : va sur la fiche d'un anime, clic droit sur l'image de couverture → "Copier l'adresse de l'image" → colle-la dans le champ Cover
- **Covers depuis IGDB** (jeux) ou **Goodreads** (livres) : même procédé
- **Bouton ↑** : un bouton flottant en bas à droite de chaque page permet de revenir en haut rapidement
- **Recherche rapide** : `Ctrl+O` ouvre l'ouverture rapide - tape quelques lettres du titre pour trouver instantanément une note
- **Statistiques rétroactives** : si tu ajoutes des sessions avec des dates passées, les statistiques et la heatmap se mettent à jour automatiquement
- **Plusieurs plateformes** : pour les jeux multi-plateformes, le champ "Plateforme" accepte plusieurs valeurs
- **Éviter les doublons** : avant de créer une fiche, utilise `Ctrl+O` pour vérifier qu'elle n'existe pas déjà

---

*Lifetrack - créé le 2026-06-05 · guide mis à jour le 2026-06-06*
