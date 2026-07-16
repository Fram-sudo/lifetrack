<%*
// Script Templater - Met à jour le statut de la note courante
// Utilisation : Ctrl+T → choisir "Mettre à jour le statut"

const file = tp.file.find_tfile(tp.file.title);
const meta = app.metadataCache.getFileCache(file)?.frontmatter;
const currentType = meta?.type;
const currentStatut = meta?.statut;

let options = [];
let values = [];

if (currentType === "projet") {
  options = ["🟢 Actif", "⏸️ En pause", "✅ Terminé", "❌ Abandonné"];
  values = ["actif", "en pause", "terminé", "abandonné"];
} else if (currentType === "animé" || currentType === "film") {
  options = ["▶️ En cours", "👁️ À voir", "✅ Vu", "❌ Abandonné"];
  values = ["en cours", "à voir", "vu", "abandonné"];
} else if (currentType === "jeu") {
  options = ["📋 Backlog", "▶️ En cours", "✅ Terminé", "❌ Abandonné"];
  values = ["backlog", "en cours", "terminé", "abandonné"];
} else if (currentType === "manga") {
  options = ["▶️ En cours", "📖 À lire", "✅ Lu", "❌ Abandonné"];
  values = ["en cours", "à lire", "lu", "abandonné"];
} else if (currentType === "livre") {
  options = ["📖 À lire", "▶️ En cours", "✅ Lu", "❌ Abandonné"];
  values = ["à lire", "en cours", "lu", "abandonné"];
} else if (currentType === "commande") {
  options = ["🛒 Commandé", "📦 Expédié", "✅ Livré", "❌ Annulé"];
  values = ["commandé", "expédié", "livré", "annulé"];
} else {
  options = ["🟢 Actif", "▶️ En cours", "⏸️ En pause", "✅ Terminé", "❌ Abandonné"];
  values = ["actif", "en cours", "en pause", "terminé", "abandonné"];
}

const newStatut = await tp.system.suggester(options, values, false, `Statut actuel : ${currentStatut || "non défini"}`);

if (newStatut !== null) {
  await app.fileManager.processFrontMatter(file, (fm) => {
    fm.statut = newStatut;
  });
  new Notice(`✅ Statut → ${newStatut}`, 3000);
}
_%>
