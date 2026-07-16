<%*
// Script Templater - Met à jour la priorité de la note courante (projets)
// Utilisation : Ctrl+T → choisir "Mettre à jour la priorité"

const file = tp.file.find_tfile(tp.file.title);
const meta = app.metadataCache.getFileCache(file)?.frontmatter;
const currentPriorité = meta?.priorité;

const options = ["🔴 Haute", "🟡 Moyenne", "🟢 Basse"];
const values = ["haute", "moyenne", "basse"];

const newPriorité = await tp.system.suggester(options, values, false, `Priorité actuelle : ${currentPriorité || "non définie"}`);

if (newPriorité !== null) {
  await app.fileManager.processFrontMatter(file, (fm) => {
    fm.priorité = newPriorité;
  });
  new Notice(`✅ Priorité → ${newPriorité}`, 3000);
}
_%>
