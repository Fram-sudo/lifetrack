<%*
// -----------------------------------------------------------------
//  Script Templater - Ajouter une session media
//  Utilisation : Ctrl+T -> "Ajouter une session"
//  Compatible : animé (saison + ep_début/ep_fin)
//               manga / manwha / manhua (ch_début/ch_fin)
//               jeu (h)
// -----------------------------------------------------------------

const file = tp.file.find_tfile(tp.file.title)
const type = tp.frontmatter.type

const MEDIA_TYPES = ["animé", "jeu", "manga", "manwha", "manhua"]
if (!MEDIA_TYPES.includes(type)) {
  new Notice("❌ Cette note n'est pas une fiche média (animé, jeu, manga...)", 4000)
  return
}

// Date
const dateStr = await tp.system.prompt(
  "Date de la session (YYYY-MM-DD)",
  tp.date.now("YYYY-MM-DD")
)
if (!dateStr || !dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
  new Notice("❌ Date invalide - format attendu : YYYY-MM-DD", 4000)
  return
}

let entry = { date: dateStr }
let noticeText = ""

// ── Animé ──────────────────────────────────────────────────────────
if (type === "animé") {

  const saisonStr = await tp.system.prompt(
    "Saison (laisser vide si non applicable)", ""
  )
  if (saisonStr === null) return
  if (saisonStr.trim()) {
    const s = parseInt(saisonStr)
    if (!isNaN(s) && s > 0) entry.saison = s
  }

  const epDeStr = await tp.system.prompt("Episode de départ")
  if (!epDeStr) return
  const epDe = parseInt(epDeStr)
  if (isNaN(epDe) || epDe < 1) { new Notice("❌ Episode invalide", 3000); return }
  entry.ep_debut = epDe

  const epFinStr = await tp.system.prompt(
    "Episode de fin (même valeur si épisode unique)",
    String(epDe)
  )
  if (!epFinStr) return
  const epFin = parseInt(epFinStr)
  if (isNaN(epFin) || epFin < epDe) { new Notice("❌ Episode de fin invalide", 3000); return }
  entry.ep_fin = epFin

  const count  = epFin - epDe + 1
  const saison = entry.saison ? ` S${entry.saison}` : ""
  const plage  = epDe === epFin ? `ep. ${epDe}` : `ep. ${epDe}-${epFin}`
  noticeText   = `${saison} ${plage} (${count} ep.) le ${dateStr}`.trim()

// ── Manga / Manwha / Manhua ────────────────────────────────────────
} else if (["manga", "manwha", "manhua"].includes(type)) {

  const chDeStr = await tp.system.prompt("Chapitre de départ")
  if (!chDeStr) return
  const chDe = parseInt(chDeStr)
  if (isNaN(chDe) || chDe < 1) { new Notice("❌ Chapitre invalide", 3000); return }
  entry.ch_début = chDe

  const chFinStr = await tp.system.prompt(
    "Chapitre de fin (même valeur si chapitre unique)",
    String(chDe)
  )
  if (!chFinStr) return
  const chFin = parseInt(chFinStr)
  if (isNaN(chFin) || chFin < chDe) { new Notice("❌ Chapitre de fin invalide", 3000); return }
  entry.ch_fin = chFin

  const count = chFin - chDe + 1
  const plage = chDe === chFin ? `ch. ${chDe}` : `ch. ${chDe}-${chFin}`
  noticeText  = `${plage} (${count} ch.) le ${dateStr}`

// ── Jeu ────────────────────────────────────────────────────────────
} else {

  const hStr = await tp.system.prompt("Heures jouées (ex: 2 ou 1.5)")
  if (!hStr) return
  const h = parseFloat(hStr.replace(",", "."))
  if (isNaN(h) || h <= 0) { new Notice("❌ Durée invalide", 3000); return }
  entry.h    = h
  noticeText = `${h}h le ${dateStr}`
}

// ── Enregistrement dans le frontmatter ────────────────────────────
await app.fileManager.processFrontMatter(file, (fm) => {
  if (!fm.sessions || !Array.isArray(fm.sessions)) fm.sessions = []
  fm.sessions.push(entry)
})

new Notice(`✅ Session ajoutée : ${noticeText}`, 4000)
_%>
