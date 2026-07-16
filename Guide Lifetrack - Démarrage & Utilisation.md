# 🗂️ Lifetrack - Guide de démarrage et d'utilisation

> Ce guide est destiné aux nouveaux utilisateurs du vault **Lifetrack**. Il couvre l'installation complète d'Obsidian, la configuration de tous les plugins, puis une prise en main détaillée de chaque section avec des exemples concrets.

---

## Table des matières

1. [Prérequis](#1--prérequis)
2. [Installer Obsidian et ouvrir le vault](#2--installer-obsidian-et-ouvrir-le-vault)
3. [Activer et configurer les plugins](#3--activer-et-configurer-les-plugins)
4. [Se repérer dans le vault](#4--se-repérer-dans-le-vault)
5. [Films](#5--films)
6. [Animés](#6--animés)
7. [Séries TV](#7--séries-tv)
8. [Mangas, Manwhas et Manhuas](#8--mangas-manwhas-et-manhuas)
9. [Romans et Livres](#9--romans-et-livres)
10. [Jeux Vidéo](#10--jeux-vidéo)
11. [Commandes](#11--commandes)
12. [Sport](#12--sport)
13. [Finances](#13--finances)
14. [Statistiques](#14--statistiques)
15. [Explorateur](#15--explorateur)
16. [Raccourcis clavier](#16--raccourcis-clavier)
17. [Problèmes courants](#17--problèmes-courants)

---

## 1 - Prérequis

### Obsidian (obligatoire)

Obsidian est l'application qui fait tourner le vault. Elle est **gratuite** pour usage personnel.

- Site officiel : **https://obsidian.md**
- Disponible sur Windows, macOS, Linux, iOS et Android
- Télécharge la version correspondant à ton système et installe-la normalement

### Python 3 (optionnel - uniquement pour l'import de relevés bancaires)

Si tu veux importer tes relevés PDF directement dans les Finances plutôt que de tout saisir à la main :

- Site officiel : **https://www.python.org/downloads/**
- Télécharge Python 3.10 ou version ultérieure
- Lors de l'installation sur Windows, coche **"Add Python to PATH"**
- Après installation, ouvre un terminal et tape : `pip install ttkbootstrap`

---

## 2 - Installer Obsidian et ouvrir le vault

### Étape 1 : Ouvrir le vault

1. Lance **Obsidian**
2. Sur l'écran d'accueil, clique sur **Ouvrir un dossier comme vault**
3. Navigue jusqu'au dossier `Lifetrack` et sélectionne-le
4. Obsidian s'ouvre et charge le vault - le **Dashboard** apparaît automatiquement

> Si Obsidian affiche une page blanche ou "Loading…", attends 3-5 secondes le temps que Dataview indexe les fichiers.

### Étape 2 : Avertissement sécurité

Obsidian va afficher un message d'avertissement sur les plugins communautaires. C'est normal - tous les plugins sont déjà présents dans le vault, il n'y a rien à télécharger depuis Internet.

Clique sur **"J'ai confiance dans l'auteur et désactive le mode sans échec"** (ou formulé similairement selon ta version).

---

## 3 - Activer et configurer les plugins

Va dans **Paramètres** (icône ⚙️ en bas à gauche, ou `Ctrl+,`) → **Plugins communautaires**.

Tu verras la liste des plugins installés. Active chacun en cliquant sur le toggle à droite de son nom.

### Plugins à activer

| Plugin | Toggle |
|--------|--------|
| Dataview | ✅ Activer |
| Templater | ✅ Activer |
| QuickAdd | ✅ Activer |
| Homepage | ✅ Activer |
| Obsidian Banners | ✅ Activer |
| Icon Folder | ✅ Activer |
| Style Settings | ✅ Activer |
| Advanced Tables | ✅ Activer |
| Tag Wrangler | ✅ Activer |

### Configuration de Dataview (obligatoire)

Sans cette étape, **rien ne s'affichera** dans le vault.

1. Dans **Plugins communautaires**, clique sur l'icône ⚙️ à droite de **Dataview**
2. Active les options suivantes :
   - ✅ **Enable DataviewJS Queries**
   - ✅ **Enable Inline DataviewJS**
3. Laisse le reste par défaut (Refresh interval à 2500 ms convient très bien)

### Configuration de Templater (obligatoire)

Templater applique automatiquement les bons modèles quand tu crées une fiche.

1. Clique sur l'icône ⚙️ à droite de **Templater**
2. Vérifie que ces options sont activées :
   - ✅ **Trigger Templater on new file creation** (applique le template automatiquement)
   - ✅ **Enable folder templates**
3. Le **Template folder** doit être : `_Système/Templates`

> Ces paramètres sont normalement déjà corrects dans le vault. Vérifie juste qu'ils n'ont pas été réinitialisés.

### Configuration de Homepage (recommandé)

Homepage ouvre le Dashboard automatiquement au démarrage.

1. Clique sur ⚙️ à droite de **Homepage**
2. Vérifie :
   - **Homepage** : `Dashboard`
   - **Open on startup** : ✅ activé
   - **View** : `Reading view`

### Les autres plugins

- **Obsidian Banners** - pas de config spéciale, active simplement
- **Icon Folder** - pas de config spéciale
- **Style Settings** - pas de config spéciale
- **Advanced Tables** - pas de config spéciale
- **Tag Wrangler** - pas de config spéciale

### Recharger le vault

Une fois tous les plugins activés, recharge le vault avec `Ctrl+R`. Le Dashboard s'affiche avec toutes ses sections.

---

## 4 - Se repérer dans le vault

### Le Dashboard

Le Dashboard est la **page d'accueil**. Appuie sur `Ctrl+D` pour y revenir à tout moment.

Il contient :
- Une **barre de statistiques** (nombre de médias en cours, total de notes, etc.)
- **8 cartes** cliquables vers chaque section du vault
- Une **heatmap** annuelle colorée selon ton activité jour par jour

### Structure des dossiers

```
Lifetrack/
├── 2 - Domaines/
│   ├── Médias/
│   │   ├── Films/         (sous-dossiers : À voir / En cours / Vu / Abandonné)
│   │   ├── Animés/        (sous-dossiers : À voir / En cours / Terminé / Abandonné / En pause)
│   │   ├── Séries/        (mêmes sous-dossiers que Animés)
│   │   ├── Manga & Manwha/ (sous-dossiers : À lire / En cours / Terminé / Abandonné)
│   │   ├── Romans & Livres/ (mêmes sous-dossiers)
│   │   └── Jeux Vidéo/    (sous-dossiers : Backlog / En cours / Terminé / Abandonné)
│   ├── Commandes/
│   ├── Sport/
│   │   └── Data/          (séances Hevy en JSON, ne pas modifier manuellement)
│   └── Finances/
│       └── Transactions/  (fichiers JSON auto-générés, ne pas modifier manuellement)
└── _Système/              ← NE PAS TOUCHER (templates, scripts, configs)
    └── Config.md          (ta clé API TMDB - jamais écrasée par les mises à jour)
```

> Quand tu changes le statut d'une fiche (ex : "À voir" → "En cours"), la note se déplace **automatiquement** dans le bon sous-dossier.

---

## 5 - Films

### Créer une fiche film

**Via QuickAdd (recommandé) :**

1. Appuie sur `Ctrl+Q`
2. Sélectionne **🎬 Nouveau média** → **🎬 Film**
3. Tape le titre → Entrée
4. La fiche s'ouvre en mode lecture

**Exemple concret :** je veux ajouter *Interstellar* que j'ai envie de voir.

- `Ctrl+Q` → Nouveau média → Film → tape "Interstellar" → Entrée
- La fiche s'ouvre avec le statut "À voir" par défaut
- Elle apparaît dans `2 - Domaines/Médias/Films/À voir/`

### Compléter la fiche

Une fois la fiche ouverte, clique sur **✏ Modifier** pour renseigner :

- **Cover** : va sur Google Images, cherche "Interstellar poster", clic droit sur l'image → "Copier l'adresse de l'image", colle-la dans le champ Cover
- **Genre** : Science-fiction
- **Réalisateur** : Christopher Nolan
- **Note** : laisse vide pour l'instant (tu la mettras après avoir regardé)

> **Astuce - auto-remplissage TMDB :** si tu as renseigné ta clé API TMDB dans `_Système/Config.md` (clé gratuite sur themoviedb.org), tu peux à la place renseigner l'**ID TMDB** du film (visible dans l'URL de sa fiche sur themoviedb.org) - titre, cover, genre et réalisateur se remplissent automatiquement. Même principe pour les animés avec un ID **AniList**.

### Marquer comme vu

Quand tu l'as regardé, clique sur **✏ Modifier** :
- Change le **Statut** à "Vu"
- Renseigne la **Date de visionnage**
- Mets ta **Note** (ex : 9/10)
- La fiche se déplace automatiquement dans `Films/Vu/`

---

## 6 - Animés

### Créer une fiche animé

`Ctrl+Q` → Nouveau média → **🎌 Animé** → tape le titre

Exemple : j'ajoute *Demon Slayer* que je commence à regarder.

- `Ctrl+Q` → Animé → "Demon Slayer" → Entrée
- Obsidian demande le **statut** : choisis "En cours"
- Obsidian demande le **nombre de saisons** : tape "4"
- La fiche s'ouvre dans `Animés/En cours/`

### Ajouter une session de visionnage

Après chaque session, clique sur **➕ Session** :

- **Date** : aujourd'hui (pré-rempli)
- **Saison** : 1
- **Épisode début** : 1
- **Épisode fin** : 3 (si tu en as regardé 3 d'affilée)

La session s'enregistre et apparaît dans un tableau sur la fiche. Les statistiques se mettent à jour automatiquement.

### Ajouter une bannière

Clique sur **🌅 Bannière** → colle une URL d'image au format paysage (16:9). Elle s'affiche en haut de la fiche comme une bannière décorative.

> Astuce : sur MyAnimeList, va sur la fiche de l'animé, clic droit sur l'image → "Copier l'adresse de l'image" pour la cover. Pour la bannière, utilise plutôt une image de fond de l'animé.

### Gérer les saisons

Clique sur **🎬 Saisons** pour ajuster le nombre d'épisodes par saison si besoin.

---

## 7 - Séries TV

Les séries TV fonctionnent **exactement comme les animés** - même interface, mêmes boutons, même système de sessions.

Exemple : j'ajoute *Breaking Bad* que j'ai déjà terminé.

- `Ctrl+Q` → Série TV → "Breaking Bad" → Entrée
- Statut : "Terminé" - Saisons : 5
- Dans **✏ Modifier**, mets ta note (10/10 évidemment)
- Ajoute quelques sessions rétroactives si tu veux que la heatmap reflète quand tu l'as regardée

---

## 8 - Mangas, Manwhas et Manhuas

### Créer une fiche

`Ctrl+Q` → Nouveau média → **📖 Manga / Manwha** → tape le titre

Exemple : j'ajoute *Solo Leveling* (Manwha coréen) que je lis en ce moment.

- `Ctrl+Q` → Manga / Manwha → "Solo Leveling" → Entrée
- Obsidian demande le **type** : choisis "Manwha"
- Obsidian demande le **statut** : "En cours"

### Compléter et suivre la lecture

Dans **✏ Modifier** :
- **Chapitres total** : 179 (met le nombre de chapitres de l'œuvre - ça affiche une barre de progression)
- **Cover** : URL de la couverture

### Ajouter une session de lecture

Clique sur **➕ Session** :
- **Date** : aujourd'hui
- **Chapitre début** : 1
- **Chapitre fin** : 15 (si tu as lu 15 chapitres)

Le champ **Chapitres lus** se met à jour automatiquement. Continue à ajouter des sessions au fil de ta lecture.

---

## 9 - Romans et Livres

### Créer une fiche

`Ctrl+Q` → Nouveau média → **📚 Roman & Livre** → tape le titre

Exemple : j'ajoute *Dune* de Frank Herbert.

- `Ctrl+Q` → Roman & Livre → "Dune" → Entrée
- Statut : "En cours"
- Dans **✏ Modifier** : Auteur "Frank Herbert", Pages "896", Genre "Science-fiction"

La fiche contient aussi des sections **Synopsis**, **Mon avis** et **Citations** que tu peux remplir librement en mode édition (`Ctrl+E`).

---

## 10 - Jeux Vidéo

### Créer une fiche

`Ctrl+Q` → Nouveau média → **🎮 Jeu Vidéo** → tape le titre

Exemple : j'ajoute *Elden Ring* que je commence.

- `Ctrl+Q` → Jeu Vidéo → "Elden Ring" → Entrée
- Statut : "En cours" (les jeux démarrent en "Backlog" par défaut - change-le via ✏ Modifier)
- Renseigne : Studio "FromSoftware", Plateforme "PC", Genre "Action RPG"

### Ajouter une session de jeu

Clique sur **➕ Session** :
- **Date** : aujourd'hui
- **Durée** : `2:30` pour 2h30 de jeu (format `H:MM`)

Les heures s'accumulent. Si tu joues 2h30 aujourd'hui et 1h45 demain, ta fiche affichera **4h15 jouées** au total.

> ⚠️ Format strict : toujours `H:MM`. Écris `1:30` et pas "1h30" ni "90 min" - sinon les heures ne se calculent pas.

---

## 11 - Commandes

### Créer une commande

`Ctrl+Q` → **🛒 Nouvelle commande** → tape un nom descriptif

Exemple : je commande un casque audio sur Amazon.

- `Ctrl+Q` → Nouvelle commande → "Amazon - Casque Sony WH-1000XM5" → Entrée
- Dans **✏ Modifier** (ou directement dans la fiche) :
  - **Site** : Amazon
  - **Montant** : 279.99
  - **Numéro de commande** : 123-4567890-1234567
  - **Statut** : Commandé
  - **Date de commande** : aujourd'hui
  - **Date de livraison estimée** : dans 2 jours

### Suivre la commande

Quand le colis est expédié → **✏ Modifier** → Statut : "Expédié"
Quand tu le reçois → Statut : "Livré"

La commande apparaît dans le **MOC Commandes** avec un code couleur selon son statut. Les commandes livrées sont automatiquement intégrées dans les Finances (catégorie 📦 Commandes) si le compte associé est configuré.

---

## 12 - Sport

Le dashboard `2 - Domaines/Sport/🏋️ Sport.md` suit tes séances de musculation importées depuis l'application [Hevy](https://www.hevyapp.com/).

### Importer un export Hevy

Exemple : tu viens de faire 3 mois de séances sur Hevy et veux les voir dans Lifetrack.

1. Dans l'app Hevy : **Profil → ⚙️ Paramètres → Exporter les données** - tu reçois un e-mail avec un CSV
2. Enregistre le fichier CSV quelque part sur ton ordinateur
3. Lance le script d'import :
   - **Linux** : double-clique sur `_Système/Scripts/Hevy/Import Hevy.desktop` (ou `lancer_hevy.sh`)
   - **Windows/macOS** : `cd` vers `_Système/Scripts/Hevy/` puis `python3 import_hevy.py`
4. Clique sur **📂 Choisir le fichier CSV**, sélectionne ton export, puis **⬆️ Importer**

Tes séances sont fusionnées dans `2 - Domaines/Sport/Data/hevy_<année>.json`. Réimporter un export qui se chevauche avec des données déjà présentes ne crée pas de doublons.

### Lire le dashboard Sport

- **📊 Rythme** - histogramme du nombre de séances par semaine (16 dernières semaines), avec streak (semaines consécutives)
- **📈 Progression** - sélectionne un exercice (ex : "Développé couché") pour voir la courbe de poids soulevé au fil du temps, avec ton record personnel repéré
- **📋 Séances** - liste détaillée de tes dernières séances : exercices, séries, poids, répétitions

---

## 13 - Finances

### Premier démarrage - configurer un compte

Avant tout, il faut créer au moins un compte bancaire.

1. Ouvre **💰 Finances** depuis le Dashboard
2. Clique sur **⚙️ Paramètres** (en haut à droite)
3. Onglet **Comptes** → **➕ Ajouter un compte**
4. Renseigne : Nom "Compte courant", Banque "Ma Banque", Type "courant", Solde initial

> **Solde initial** : c'est le solde de ton compte au moment où tu commences à utiliser Lifetrack. Si tu as 1 200 € sur ton compte aujourd'hui, mets 1200.

Si tu as un deuxième compte (Revolut, épargne, etc.), ajoute-le aussi.

### Les 4 types de transactions

En bas de la page Finances, 4 boutons permettent d'accéder au bon formulaire :

#### ➕ Dépense - une sortie d'argent classique

Exemples : faire ses courses, payer son loyer, acheter un jeu…

> **Exemple :** tu fais tes courses pour 67,50 €.
> - Clique sur **➕ Dépense**
> - Date : aujourd'hui
> - Libellé : "Courses Carrefour"
> - Montant : 67.50
> - Catégorie : 🛒 Alimentation
> - Compte : Compte courant

#### 💵 Revenu - une entrée d'argent

Exemples : salaire, remboursement reçu, bourse…

> **Exemple :** tu reçois ton salaire de 1 800 €.
> - Clique sur **💵 Revenu**
> - Libellé : "Salaire juin"
> - Montant : 1800
> - Catégorie : 💵 Salaire
> - Compte : Compte courant

#### 💰 Mettre de côté - épargner

Met de l'argent de côté dans ton "pot" d'épargne. Ce montant disparaît du solde courant et s'ajoute au solde épargne visible dans la section **Économies**.

> **Exemple :** tu décides de mettre 300 € de côté ce mois-ci.
> - Clique sur **💰 Mettre de côté**
> - Libellé : "Épargne juin"
> - Montant : 300
> - Catégorie : 💰 Économies (pré-sélectionnée)
> - Compte : Compte courant

#### 💸 Piocher - utiliser son épargne

Récupère de l'argent depuis ton épargne. Le montant revient dans le solde courant.

> **Exemple :** tu retires 100 € de ton épargne pour une dépense imprévue.
> - Clique sur **💸 Piocher**
> - Libellé : "Retrait épargne - réparation vélo"
> - Montant : 100
> - Catégorie : 💸 Retrait économies (pré-sélectionnée)

### Virements entre comptes

Si tu as plusieurs comptes et que tu fais un virement de l'un à l'autre, enregistre **deux transactions** pour que le solde de chaque compte soit correct - sans fausser tes stats globales.

Les catégories **🔄 Transfert interne out** et **🔄 Transfert interne in** sont automatiquement exclues des revenus et dépenses.

> **Exemple :** tu envoies 200 € de ton compte courant vers ton Revolut.
>
> **Transaction 1** (➕ Dépense) :
> - Libellé : "Virement vers Revolut"
> - Montant : 200
> - Catégorie : 🔄 Transfert interne out
> - Compte : Compte courant
>
> **Transaction 2** (💵 Revenu) :
> - Libellé : "Virement depuis compte courant"
> - Montant : 200
> - Catégorie : 🔄 Transfert interne in
> - Compte : Revolut

### Avoirs et remboursements d'achat

Quand tu retournes un article et reçois un avoir, n'enregistre pas ça comme un revenu - utilise la catégorie **🔙 Avoir / Remboursement achat**. Ce montant vient en déduction de tes dépenses, ce qui reflète fidèlement ce que tu as réellement dépensé.

> **Exemple :** tu retournes une veste achetée 89 € et reçois un avoir.
> - (💵 Revenu, mais avec catégorie avoir)
> - Libellé : "Remboursement retour veste"
> - Montant : 89
> - Catégorie : 🔙 Avoir / Remboursement achat

### Importer des relevés bancaires

Pour gagner du temps, tu peux importer directement tes relevés PDF au lieu de tout saisir manuellement.

Le script reconnaît nativement les relevés **Société Générale** et **Revolut**, avec catégorisation automatique déjà configurée (Alimentation, Transport, Abonnements, Salaire…). Pour toute autre banque, tu peux configurer manuellement le format de tes relevés (voir "Configurer ta banque" plus bas).

**Prérequis :** Python 3 installé. Les dépendances (`ttkbootstrap`, `pdfplumber`) sont installées automatiquement au premier lancement.

**Lancement :**
- **Windows** : double-clique sur `_Système/Scripts/Import Relevés.bat` (ou `lancer_import.bat`)
- **Linux** : double-clique sur `_Système/Scripts/Import Relevés.desktop` (ou `lancer_import.sh`)
- **macOS** : dans un terminal, `cd` vers `_Système/Scripts/` puis `python3 import_releves.py`

**Dans l'interface du script :**
1. Clique sur **📁** pour sélectionner le dossier du vault si ce n'est pas le bon
2. Clique sur **Ajouter un relevé** → sélectionne ton fichier PDF
3. Choisis la banque correspondante
4. Clique sur **Importer**

Les transactions apparaissent automatiquement dans Lifetrack. Tu peux corriger les catégories manuellement après import si besoin.

**Configurer ta banque :** clique sur **⚙️ Gérer les banques** pour configurer ta banque (format CSV/PDF, colonnes, format de date…).

### Comment les transactions sont stockées

Toutes les transactions sont enregistrées dans `2 - Domaines/Finances/Transactions/`, dans des fichiers JSON **un par année** :

```
Transactions/
├── 💰 2024.json
├── 💰 2025.json
└── 💰 2026.json
```

Chaque fichier regroupe à la fois les transactions importées depuis les relevés et les transactions saisies manuellement dans Lifetrack. Le script les distingue en interne - les saisies manuelles sont toujours conservées, même quand tu réimportes un relevé.

**Déduplication automatique :** le script compare chaque transaction importée avec ce qui existe déjà (date + montant + libellé). Tu peux réimporter le même relevé PDF plusieurs fois sans créer de doublons.

> Ne modifie pas ces fichiers JSON directement - passe toujours par l'interface de Lifetrack ou par le script d'import.

### Configurer des budgets mensuels

Dans **⚙️ Paramètres** → onglet **Budgets** :
- Active les catégories que tu veux suivre
- Renseigne un plafond mensuel pour chacune

> **Exemple :** Alimentation 400 €/mois, Abonnements 50 €/mois, Transport 80 €/mois.

La page Finances affiche alors une barre de progression budget/réel pour chaque catégorie.

### Changer de devise

Un bouton **💱 EUR** en haut à droite permet de basculer l'affichage en USD, CAD ou F CFA. Les taux de change sont récupérés automatiquement depuis Internet (toutes les 30 minutes). La devise de référence reste l'euro - les montants en devises étrangères sont une conversion à titre indicatif.

Pour définir une devise par défaut : **⚙️ Paramètres** → onglet **Général**.

### Mode confidentialité

Le bouton 🙈 masque tous les montants. Pratique si tu utilises Lifetrack en public. Survole un montant masqué pour le révéler temporairement.

---

## 14 - Statistiques

La page **📊 Statistiques** (accessible depuis le Dashboard) centralise toute ton activité.

### Vue globale

Choisis une période en haut de la page (Aujourd'hui, Cette semaine, Ce mois, Cette année, Tout, ou une plage personnalisée).

Les **cartes de stats** affichent :
- 🎌 Épisodes d'animés regardés
- 📺 Épisodes de séries regardés
- 🎮 Heures jouées
- 📖 Chapitres lus
- 🎬 Films vus

La **heatmap** colore chaque jour de l'année selon ton activité - plus tu as de sessions ce jour-là, plus la case est foncée. Survole une case pour voir le détail.

L'**activité récente** montre les médias que tu as consultés récemment avec leur cover.

### Vue individuelle

Clique sur **🔍 Vue individuelle**, tape un titre → les statistiques de ce média s'affichent : heatmap individuelle, graphique de sessions, liste complète des sessions.

> **Exemple :** tu veux voir combien d'épisodes de *One Piece* tu as regardé ce mois.
> - Clique sur Vue individuelle → tape "One Piece" → sélectionne
> - Change la période sur "Ce mois"
> - Les épisodes regardés ce mois apparaissent instantanément

---

## 15 - Explorateur

La page **🔍 Explorateur** permet de chercher dans tout le vault.

### Recherche par titre

Par défaut, la recherche est instantanée sur les noms de notes. Tape quelques lettres et les résultats s'affinent en temps réel.

### Filtres avancés

Clique sur **⚙ Filtres** pour affiner :
- **Domaine** : Tout / Médias / Commandes / Finances / Système
- **Statut** : En cours, Terminé, À voir…
- **Note minimale** : afficher uniquement les œuvres que tu as notées ≥ X
- **Tri** : date de modification, nom A→Z ou Z→A

> **Exemple :** tu veux retrouver tous les jeux vidéo que tu as terminés et notés au moins 8/10.
> - Domaine : Médias → Filtres → Statut "Terminé" → Note minimale 8 → Tri par nom

---

## 16 - Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+D` | Ouvrir le Dashboard |
| `Ctrl+Q` | QuickAdd - nouveau média ou commande |
| `Ctrl+O` | Ouverture rapide - chercher une note par son nom |
| `Ctrl+Shift+F` | Recherche globale dans le contenu de toutes les notes |
| `Ctrl+R` | Recharger le vault |
| `Ctrl+,` | Ouvrir les paramètres |
| `Ctrl+E` | Basculer entre mode lecture et mode édition |
| `Ctrl+\` | Afficher/masquer la barre latérale |
| `Ctrl+G` | Vue en graphe |
| `Ctrl+Alt+←` | Page précédente |
| `Ctrl+Alt+→` | Page suivante |

---

## 17 - Problèmes courants

**Le Dashboard ou les MOCs n'affichent rien**
→ Paramètres → Dataview → vérifie que **Enable DataviewJS** et **Enable Inline DataviewJS** sont activés. Recharge avec `Ctrl+R`.

**Les templates ne s'appliquent pas automatiquement**
→ Paramètres → Templater → vérifie que **Trigger Templater on new file creation** et **Enable folder templates** sont activés, et que le dossier de templates est `_Système/Templates`.

**QuickAdd ne répond pas à `Ctrl+Q`**
→ Vérifie que le plugin QuickAdd est activé. Sinon essaie `Ctrl+P` → tape "QuickAdd".

**Le Dashboard ne s'ouvre pas au démarrage**
→ Paramètres → Homepage → règle la page sur "Dashboard" et la vue sur "Reading view".

**Le script d'import de relevés ne se lance pas**
→ Vérifie que Python 3 est installé (`python3 --version` dans un terminal) et que `ttkbootstrap` est installé (`pip install ttkbootstrap`). Sur Windows, assure-toi que Python est bien dans le PATH (option à cocher lors de l'installation).

**Les covers ne s'affichent pas dans les MOCs**
→ L'URL de la cover doit pointer directement vers un fichier image (se terminant par `.jpg`, `.png`, `.webp`…). Une URL de page web (ex : page MyAnimeList) ne fonctionne pas. Procédure : clic droit sur l'image → **"Copier l'adresse de l'image"**.

**Les heures jouées ne se calculent pas correctement**
→ Le format attendu est strictement `H:MM`. Exemple : `2:30` pour 2h30, `0:45` pour 45 minutes. N'écris pas "2h30", "2.5" ou "150 min".

**Une note s'est retrouvée dans `0 - Inbox`**
→ Elle a été créée sans passer par QuickAdd et sans être dans un dossier avec template associé. Déplace-la manuellement dans le bon dossier (ex : `2 - Domaines/Médias/Animés/À voir/`).

**Le vault est lent avec beaucoup de transactions**
→ C'est normal sur le mode "Tout" des Finances avec un grand historique. Pour améliorer les performances globales : Paramètres → Dataview → **Refresh interval** → mets 5000 (5 secondes).

**Les stats des Finances n'affichent pas mes transactions importées**
→ Vérifie que le fichier JSON a bien été créé dans `2 - Domaines/Finances/Transactions/`. Le fichier doit s'appeler `💰 YYYY.json` (ex : `💰 2026.json`). Recharge le vault avec `Ctrl+R`.

---

## Conseils pratiques

- **Couvertures depuis MyAnimeList** : fiche de l'animé → clic droit sur l'image → "Copier l'adresse de l'image" → colle dans le champ Cover
- **Couvertures depuis IGDB** (jeux) : même procédé sur igdb.com
- **Couvertures depuis Goodreads** (livres) : même procédé
- **Éviter les doublons** : avant de créer une fiche, tape `Ctrl+O` et cherche le titre - si ça apparaît, c'est qu'elle existe déjà
- **Sessions rétroactives** : tu peux ajouter des sessions avec des dates passées - les statistiques et la heatmap se mettent à jour en conséquence
- **Bouton ↑** : un bouton flottant en bas à droite de chaque page longue permet de revenir en haut instantanément
- **Mobile** : le vault fonctionne sur Obsidian Mobile (iOS/Android) avec la même interface. Installe l'app, ouvre le vault via un dossier partagé (iCloud, Dropbox, Syncthing…)

---

*Guide rédigé pour Lifetrack · Version 2026-07-16*
