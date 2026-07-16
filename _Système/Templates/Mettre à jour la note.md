<%*
// Script Templater - Met à jour la note de la fiche courante
// Utilisation : Ctrl+T -> "Mettre à jour la note"

const file = tp.file.find_tfile(tp.file.title)
const meta = app.metadataCache.getFileCache(file)?.frontmatter
const current = meta?.note

const input = await tp.system.prompt(
  `Note actuelle : ${current ?? "non définie"} -- Entre un chiffre entre 1 et 10`,
  current != null ? String(current) : ""
)

if (input === null) return

const note = parseFloat(input.replace(",", "."))
if (isNaN(note) || note < 1 || note > 10) {
  new Notice("Note invalide - entre 1 et 10", 3000)
  return
}

const val = Number.isInteger(note) ? note : Math.round(note * 10) / 10

await app.fileManager.processFrontMatter(file, (fm) => {
  fm.note = val
})

new Notice(`Note -> ${val}/10`, 3000)
_%>
