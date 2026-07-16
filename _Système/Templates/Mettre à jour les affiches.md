<%*
// Script Templater - Met à jour les affiches (covers) d'une fiche média
// Fonctionne pour : animé, film, manga, manwha, manhua, livre, jeu

const TYPES_CONFIG = {
  "animé":   { label: "Saison", countField: "saisons" },
  "film":    { label: "Film",   countField: null       },
  "manga":   { label: "Tome",   countField: null       },
  "manwha":  { label: "Tome",   countField: null       },
  "manhua":  { label: "Tome",   countField: null       },
  "livre":   { label: "Tome",   countField: "tomes"   },
  "jeu":     { label: "Opus",   countField: "opus"    },
}

const file = tp.file.find_tfile(tp.file.title)
const meta = app.metadataCache.getFileCache(file)?.frontmatter

const cfg = TYPES_CONFIG[meta?.type]
if (!cfg) {
  new Notice("Cette note n'est pas une fiche média reconnue", 3000)
  return
}

const currentCovers = Array.isArray(meta?.covers) ? [...meta.covers] : []

// Nombre de covers attendues (depuis le champ dédié si disponible)
const countFromField = cfg.countField ? (meta?.[cfg.countField] || 0) : 0
const nbManaged = Math.max(countFromField, currentCovers.length)

// Compléter le tableau si nécessaire
while (currentCovers.length < nbManaged) currentCovers.push("")

// Construction du menu
const menuLabels = []
const menuValues = []

if (currentCovers.length > 0) {
  menuLabels.push(`🔄 Toutes les covers (${currentCovers.length})`)
  menuValues.push("all")
  menuLabels.push("🎯 Une cover en particulier")
  menuValues.push("one")
}
menuLabels.push("➕ Ajouter une cover")
menuValues.push("add")
if (currentCovers.length > 0) {
  menuLabels.push("🗑️ Supprimer la dernière")
  menuValues.push("remove")
}

const choix = await tp.system.suggester(menuLabels, menuValues)
if (choix === null) return

let indicesToUpdate = []

if (choix === "add") {
  currentCovers.push("")
  indicesToUpdate = [currentCovers.length - 1]
} else if (choix === "remove") {
  currentCovers.pop()
  await app.fileManager.processFrontMatter(file, (fm) => { fm.covers = currentCovers })
  new Notice("Dernière cover supprimée.", 3000)
  return
} else if (choix === "all") {
  indicesToUpdate = currentCovers.map((_, i) => i)
} else {
  const labels = currentCovers.map((c, i) => `${cfg.label} ${i + 1}${c ? " ✓" : " (vide)"}`)
  const vals   = currentCovers.map((_, i) => i)
  const idx = await tp.system.suggester(labels, vals, false, "Quelle cover ?")
  if (idx === null) return
  indicesToUpdate = [idx]
}

// Mise à jour des covers sélectionnées
const newCovers = [...currentCovers]

for (const idx of indicesToUpdate) {
  const type = await tp.system.suggester(
    [`${cfg.label} ${idx + 1} - URL web`, `${cfg.label} ${idx + 1} - Fichier local`],
    ["url", "local"],
    false,
    `Cover "${cfg.label} ${idx + 1}" - source ?`
  )
  if (type === null) continue

  if (type === "url") {
    const url = await tp.system.prompt(
      `URL de la cover - ${cfg.label} ${idx + 1}`,
      currentCovers[idx] || ""
    )
    if (!url) continue
    newCovers[idx] = url.trim()

  } else {
    const filename = await tp.system.prompt(
      `Nom du fichier dans _Système/Attachments/ (ex: Mon Film.jpg)`,
      currentCovers[idx] || ""
    )
    if (!filename) continue
    const found = app.metadataCache.getFirstLinkpathDest(filename.trim(), "")
    if (!found) {
      new Notice(`"${filename}" introuvable. Place-le dans _Système/Attachments/ et réessaie.`, 5000)
      continue
    }
    newCovers[idx] = filename.trim()
  }
}

// Enregistrement
await app.fileManager.processFrontMatter(file, (fm) => {
  fm.covers = newCovers
})

new Notice("Affiches mises à jour !", 3000)
_%>
