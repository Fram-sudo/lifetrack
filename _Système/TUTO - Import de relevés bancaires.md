# 📥 Tuto - Import de relevés bancaires

> Script : `_Système/Scripts/import_releves.py`  
> Lanceur Linux : `lancer_import.sh` - Lanceur Windows : `Import Relevés.bat`

---

## 🚀 Lancement

**Linux** - double-clic sur `lancer_import.sh`, ou depuis un terminal :
```bash
cd ~/Documents/Obsidian/Lifetrack/_Système/Scripts
./lancer_import.sh
```

**Windows** - double-clic sur `Import Relevés.bat`.

Le script installe automatiquement les dépendances manquantes (`pdfplumber`, `ttkbootstrap`) au premier lancement.

---

## 🗺️ Vue d'ensemble

```
Étape 1 - Ajouter les PDFs
        ↓
Étape 2 - Analyser (détection auto du type de relevé)
        ↓
Étape 3 - Vérifier les résultats (nouvelles tx, doublons, recatégorisations)
        ↓
Étape 4 - Importer → JSON annuels dans Transactions/
```

---

## ÉTAPE 1 - Ajouter des PDFs

Clique sur **＋ Ajouter des PDFs**. Tu peux sélectionner plusieurs fichiers en même temps (Ctrl+clic).

Chaque PDF reçoit automatiquement un badge coloré :

| Badge | Signification |
|-------|--------------|
| 🟣 **Nom banque** | Banque configurée manuellement |
| ⬜ **?** | Banque inconnue - à configurer |

Pour retirer un PDF : clique dessus pour le sélectionner, puis **✕ Retirer**.

> Tu peux importer un relevé "All Time" sans crainte : le système de déduplication bloque automatiquement les transactions déjà présentes, même si les libellés ont légèrement changé entre deux exports.

---

## ÉTAPE 2 - Analyser

Clique sur **🔍 Analyser les PDFs**.

### Banque connue (badge coloré)
Le relevé est parsé automatiquement avec ta configuration et tes règles de catégorisation.

### Banque inconnue (badge **?**)
Une fenêtre de configuration s'ouvre automatiquement.

#### Configurer une nouvelle banque

1. **Visualise le tableau** extrait du PDF. Les colonnes s'affichent en haut avec des menus déroulants.
2. **Assigne les rôles** à chaque colonne via les menus :
   - `Date` - la colonne contenant les dates
   - `Libellé` - la description de l'opération
   - `Montant (+/-)` - si un seul montant signé
   - `Débit (négatif)` + `Crédit (positif)` - si deux colonnes séparées
   - `Ignorer` - pour les colonnes inutiles
3. **Remplis les champs** :
   - *Nom de la banque* - ex: `BNP Paribas`
   - *Nom du compte* - ex: `Compte courant BNP`
   - *Format de date* - choisis dans la liste (ex: `31/12/2024`)
   - *Lignes d'en-tête* - nombre de lignes à ignorer en haut du tableau (généralement 1)
   - *Texte de reconnaissance* - texte présent dans tous les PDFs de cette banque (utilisé pour la détection automatique future)
4. Clique **🔍 Tester la config** - vérifie que les transactions s'extraient correctement.
5. *(Optionnel)* Clique **✏ Configurer les règles** pour configurer la catégorisation (voir section dédiée).
6. Clique **💾 Enregistrer** - la config est sauvegardée dans `bank_configs.json` pour les prochains imports.

---

## ÉTAPE 3 - Vérifier les résultats

Quatre onglets peuvent s'afficher :

### ✅ Nouvelles
Transactions qui n'existent pas encore dans les JSON. Clique sur les en-têtes de colonnes pour trier.

### ⚠️ Doublons
Transactions détectées à la fois dans le relevé **et** dans une saisie manuelle existante.
- **Coché ✓** → remplace la saisie manuelle par la donnée du relevé *(recommandé)*
- **Décoché** → conserve ta version manuelle

### 🔄 Catégories modifiées
Transactions déjà dans les JSON dont la catégorie **changerait** avec les règles actuelles. Apparaît uniquement si des règles ont été ajoutées ou modifiées depuis le dernier import.

Chaque ligne montre : date · libellé · montant · ancienne catégorie (rouge) → nouvelle catégorie (verte).
- **Coché ✓** → met à jour la catégorie dans les JSON *(recommandé)*
- **Décoché** → conserve l'ancienne catégorie

Utilise "Tout cocher / décocher" pour traiter toutes les lignes d'un coup.

### 📋 Manuelles
Saisies manuelles qui ne correspondent à aucun doublon. Elles sont toujours conservées.

---

## ÉTAPE 4 - Importer

Clique sur **✓ Importer** (barre du bas).

Un résumé s'affiche : nouvelles transactions, doublons remplacés, fichiers JSON mis à jour.

Confirme → les fichiers `💰 YYYY.json` dans `Transactions/` sont mis à jour.

**Ensuite** : rafraîchis la page Finances dans Obsidian (Ctrl+R sur la note).

---

## ⚙️ Gérer les banques

Accessible via le bouton **⚙️ Gérer les banques** en bas à gauche.

### Banques configurées
- **✏ Modifier** - changer le nom, compte, fingerprint, format date, ou règles
- **🗑 Supprimer** - supprimer la configuration (les transactions déjà importées ne sont pas affectées)

---

## 🏷️ Règles de catégorisation

Accessibles via **📋 Règles** dans "Gérer les banques", ou lors de la configuration d'une nouvelle banque.

### Structure d'une règle

| Champ | Rôle |
|-------|------|
| **N°** | Numéro d'ordre - les règles sont vérifiées du haut vers le bas, la première qui correspond gagne |
| **Mots-clés** | Mots séparés par des virgules, cherchés dans le libellé (insensible à la casse et aux espaces) |
| **Catégorie** | Catégorie assignée si un mot-clé correspond |
| **Direction** | `Tous` / `Crédit ↑` / `Débit ↓` - permet de distinguer vente vs achat pour le même marchand |

**Exemple :** `VINTED` en `Crédit ↑` → `💰 Revenus divers` et `VINTED` en `Débit ↓` → `🛍️ Shopping`

### Réordonner les règles

Clique et **glisse la poignée `⠿`** à gauche de chaque règle pour la déplacer à la position souhaitée. Le numéro de chaque règle se met à jour automatiquement.

### Avertissement de conflits

Si un mot-clé d'une règle est **contenu dans** le mot-clé d'une règle suivante, un avertissement apparaît en bas de la fenêtre :

> ⚠️ « AMAZON » (règle 1) masque « AMAZON PRIME » (règle 15) - placez la règle 15 au-dessus.

Cela se produit parce que le matching fonctionne par substring : "AMAZON" matche aussi "AMAZONPRIME". Il faut toujours mettre la règle la plus spécifique **avant** la plus générale.

### Pré-remplissage automatique (nouvelle banque)
Après avoir testé une config avec **🔍 Tester**, le bouton **✏ Configurer les règles** indique le nombre de libellés disponibles. En cliquant dessus, tu peux pré-remplir les règles avec tous les libellés détectés - plus qu'à choisir la catégorie et la direction pour chacun.

---

## 🔄 Déduplication - comment ça marche

Le script empêche les doublons en deux passes lors de l'analyse :

**Passe 1 - exacte :** vérifie si la transaction existe déjà par sa clé précise `(date + montant + libellé normalisé)`.

**Passe 2 - souple :** si la clé exacte ne matche pas mais qu'une transaction avec le même `(date + montant)` existe déjà, elle est considérée comme un doublon. Protège contre les légères variations de libellé entre deux exports du même compte.

**Comptage :** si tu as deux vraies transactions à 15€ le même jour, les deux passent - le système compte les occurrences disponibles et n'en bloque que les excédents.

> **En pratique :** tu peux importer un relevé "All Time" à n'importe quel moment sans créer de doublons.

---

## 📁 Fichiers produits

```
2 - Domaines/Finances/Transactions/
├── 💰 2023.json
├── 💰 2024.json
├── 💰 2025.json
└── 💰 2026.json
```

Chaque transaction JSON :
```json
{
  "date":         "2024-11-15",
  "label":        "NETFLIX",
  "montant":      -13.99,
  "categorie":    "📺 Abonnements",
  "type":         "dépense",
  "compte":       "courant"
}
```

| Champ | Valeurs possibles |
|-------|-------------------|
| `montant` | Positif = entrée d'argent, négatif = sortie |
| `type` | `revenu` / `dépense` / `épargne` / `épargne-retrait` / `avoir` |
| `compte` | Identifiant du compte défini lors de la configuration de la banque |
| `_manual` | `true` si saisie manuelle - jamais écrasée par import auto |

---

## 💰 Finances.md - comment le solde est calculé

```
Solde affiché = solde_initial + somme de tous les montants du compte
```

Le `solde_initial` est configurable dans Finances.md > Paramètres > Comptes.

**Ce qui est compté dans "Revenus" :** toutes les transactions avec `type = "revenu"` sauf les virements internes (`🔄 Transfert interne in/out`). Catégories concernées : Salaire, Revenus divers, Remboursement in, Bourse & Aides sociales.

---

## ❓ Problèmes fréquents

**"Aucune table détectée"** → Le PDF est scanné (image), pas natif. Ces PDFs ne sont pas supportés - il faut un PDF avec du texte sélectionnable.

**Mauvais format de date** → Dans la config, change le format date et clique à nouveau sur **🔍 Tester**.

**Toutes les transactions en "❓ Autre"** → Aucune règle ne correspond. Ouvre les règles de catégorisation et ajoute les mots-clés manquants.

**La banque n'est pas reconnue automatiquement** → Le *texte de reconnaissance* (fingerprint) dans la config ne correspond pas au contenu du PDF. Ouvre le PDF, copie un texte court et unique présent sur toutes les pages, et mets-le comme fingerprint.

**Solde négatif ou incohérent** → Vérifier si des transactions ont été importées en double (plusieurs imports de PDFs à plages chevauchantes). Solution : purger les transactions du compte dans les JSON et réimporter depuis un relevé "All Time" complet.

**"🔄 Catégories modifiées" affiche des faux positifs** → La transaction avait une catégorie manuelle différente de celle calculée par les règles. Si tu veux garder ta catégorie manuelle, décoche simplement la case.
