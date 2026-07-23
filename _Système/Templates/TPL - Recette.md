<%*
// QuickAdd place déjà la note dans Plats/ ou Desserts/ ou Autres/
// On lit le dossier parent pour régler automatiquement la catégorie
const parentFolder = tp.file.folder(true).split("/").pop()
let categorie = ""
if (parentFolder === "Plats") {
  categorie = "Plat"
} else if (parentFolder === "Desserts") {
  categorie = "Dessert"
} else if (parentFolder === "Petit déjeuner") {
  categorie = "Petit dejeuner"
} else if (parentFolder === "Collations & Goûters") {
  categorie = "Collation"
} else {
  // Dans Autres/ → on pose une seule question de précision
  const subLabels = ["🥗 Entrée", "🥤 Boisson", "🍴 Autre"]
  const subValues = ["Entree", "Boisson", "Autre"]
  categorie = await tp.system.suggester(subLabels, subValues, false, "Précise la catégorie")
  if (!categorie) { new Notice("Création annulée"); return }
}
-%>
---
type: recette
created: <% tp.date.now("YYYY-MM-DD") %>
tags: [recette]
categorie: "<% categorie %>"
difficulte: ""
temps_prep: 
temps_cuisson: 
portions: 
note: 
macros: ""
cover: ""
source: ""
remarque: ""
ingredients: []
etapes: []
---

```dataviewjs
// ── Bouton Renommer ──────────────────────────────────────────────
{ const _p = dv.current(); if (!_p?.file) return;
dv.container.style.cssText = "margin:0;padding:0;";
const _run = (_t=0) => {
  if (_t > 25) return;
  let _el = dv.container.parentElement, _d = 0;
  while (_el && _d++ < 15 && !['markdown-preview-section','markdown-rendered','markdown-preview-view'].some(c => _el.classList.contains(c))) _el = _el.parentElement;
  const _h1 = _el?.querySelector('h1');
  if (!_h1) { setTimeout(()=>_run(_t+1), 60); return; }
  _h1.style.display = 'none';
  const _row = dv.container.createDiv();
  _row.style.cssText = 'display:flex;align-items:center;gap:10px;margin:var(--h1-margin,0.5em 0 0.8em);';
  const _ttl = _row.createEl('span');
  _ttl.textContent = _p.file.name;
  _ttl.style.cssText = 'font-size:var(--h1-size,1.9em);font-weight:var(--h1-weight,700);color:var(--h1-color,var(--text-normal));font-family:var(--font-text);line-height:1.2;';
  const _btn = _row.createEl('button');
  _btn.textContent='✏️'; _btn.title='Renommer';
  _btn.style.cssText='font-size:0.55em;padding:2px 7px;border-radius:5px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-muted);cursor:pointer;opacity:0.4;transition:opacity 0.15s;';
  _btn.onmouseenter=()=>_btn.style.opacity='1'; _btn.onmouseleave=()=>_btn.style.opacity='0.4';
  _btn.onclick = () => {
    const _inp = document.createElement('input'); _inp.type='text';
    _inp.value = _p.file.name;
    _inp.style.cssText='font-size:inherit;font-weight:inherit;color:inherit;font-family:inherit;border:none;border-bottom:2px solid var(--interactive-accent);background:transparent;outline:none;min-width:160px;';
    _ttl.replaceWith(_inp); _btn.style.display='none';
    const _ok=_row.createEl('button'); _ok.textContent='✅';
    _ok.style.cssText='font-size:0.6em;padding:3px 9px;border-radius:5px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;';
    const _x=_row.createEl('button'); _x.textContent='✕';
    _x.style.cssText='font-size:0.6em;padding:3px 7px;border-radius:5px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-muted);cursor:pointer;';
    const _cancel=()=>{ _inp.replaceWith(_ttl); _ok.remove(); _x.remove(); _btn.style.display=''; };
    const _save=async()=>{
      const _v=_inp.value.trim(); if(!_v||_v===_p.file.name){ _cancel(); return; }
      _ttl.textContent=_v; _inp.replaceWith(_ttl); _ok.remove(); _x.remove(); _btn.style.display='';
      try {
        const _f=app.vault.getAbstractFileByPath(_p.file.path); if(!_f) return;
        const _np=(_p.file.folder?_p.file.folder+'/':'')+_v+'.md';
        await app.fileManager.renameFile(_f,_np);
        const _leaf=app.workspace.activeLeaf;
        await new Promise(res=>{const _w=(_n=0)=>{if(_n>30){res();return;}if(app.plugins.plugins['dataview']?.api?.page(_np)?.file){const _nf2=app.vault.getAbstractFileByPath(_np);if(_nf2&&_leaf){_leaf.openFile(_nf2).then(res);}else{res();}}else{setTimeout(()=>_w(_n+1),100);}};setTimeout(()=>_w(),150);});
        new Notice('✅ '+_v);
      } catch(e){ new Notice('❌ '+e.message); }
    };
    _ok.onclick=_save; _x.onclick=_cancel;
    _inp.onkeydown=e=>{ if(e.key==='Enter')_save(); if(e.key==='Escape')_cancel(); };
    _row.append(_ok,_x); _inp.focus(); _inp.select();
  };
  _row.append(_ttl,_btn);
};
setTimeout(()=>_run(),80); }
```

```dataviewjs
// ═══════════════════════════════════════════════════════════════════
//  TPL - Recette  (DataviewJS interactif)
// ═══════════════════════════════════════════════════════════════════
const { Notice } = require('obsidian')
const p = dv.current()
if (!p?.file) { const _rr=(_n=0)=>{ if(_n>25)return; setTimeout(()=>{ const _nf=app.vault.getAbstractFileByPath(dv.currentFilePath); (_nf&&app.plugins.plugins['dataview']?.api?.page(dv.currentFilePath)?.file)?app.workspace.activeLeaf?.openFile(_nf):_rr(_n+1); },200); }; _rr(); return; }
const filePath = p.file.path

// Dataview réexécute ce bloc à chaque sauvegarde de frontmatter (ajout/suppression
// d'ingrédient, badge modifié...), ce qui effacerait normalement les variables
// locales. On garde le mode édition et les portions choisies sur `window`
// (comme _SPORT_STATE dans 🏋️ Sport.md) pour rester en mode Modifier tant qu'on
// n'a pas cliqué sur "Terminé", même en enchaînant plusieurs modifications.
if (!window._RECETTE_UI) window._RECETTE_UI = {}
const _ui = window._RECETTE_UI[filePath] || (window._RECETTE_UI[filePath] = {})

// ── helpers ──────────────────────────────────────────────────────────
const save = async (updates) => {
  await app.fileManager.processFrontMatter(
    app.vault.getAbstractFileByPath(filePath),
    fm => { for (const [k, v] of Object.entries(updates)) fm[k] = v }
  )
}

const LABEL  = "font-size:0.75em;color:var(--text-muted);font-weight:600;letter-spacing:0.04em;text-transform:uppercase;display:block;margin-bottom:4px;"
const FIELD  = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;"
const HINT   = "font-size:0.72em;color:var(--text-muted);position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;"
const BTN_S  = "padding:5px 13px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.84em;font-weight:600;font-family:inherit;"
const BTN_G  = "padding:5px 13px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.84em;font-family:inherit;"
const ADD_S  = "background:none;border:1px dashed var(--background-modifier-border);border-radius:7px;cursor:pointer;color:var(--text-muted);font-size:0.83em;padding:5px;text-align:center;font-family:inherit;width:100%;"

const editField = (key, label, current, isNumber = false) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:300px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = label
  const inp = box.createEl("input", {attr:{type: isNumber ? "number" : "text", value: current || "", style:FIELD, placeholder: label}})
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button", {attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button", {attr:{style:BTN_S}}); ok.textContent = "Enregistrer"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => {
    const v = isNumber ? (parseFloat(inp.value) || null) : inp.value.trim()
    await save({[key]: v})
    overlay.remove()
    new Notice(`${label} mis a jour`, 2000)
  }
  inp.addEventListener("keydown", e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() })
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(() => inp.focus(), 50)
}

const selectField = (key, label, options, current, onSelect) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:280px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = label
  const list = box.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:6px;"}})
  for (const opt of options) {
    const btn = list.createEl("button", {attr:{style: opt === current ? BTN_S : BTN_G}})
    btn.textContent = opt
    btn.onclick = async () => {
      await save({[key]: opt})
      if (onSelect) await onSelect(opt)
      overlay.remove()
      new Notice(`${label} mis à jour`, 2000)
    }
  }
  const cancel = box.createEl("button", {attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  cancel.onclick = () => overlay.remove()
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  overlay.append(box)
}


// ── Déplacement automatique selon catégorie ───────────────────────────────
const FOLDER_MAP = {
  "Plat":            "2 - Domaines/Recettes/Plats",
  "Dessert":         "2 - Domaines/Recettes/Desserts",
  "Petit dejeuner":  "2 - Domaines/Recettes/Petit déjeuner",
  "Collation":       "2 - Domaines/Recettes/Collations & Goûters",
  "Entree":          "2 - Domaines/Recettes/Autres",
  "Boisson":         "2 - Domaines/Recettes/Autres",
  "Autre":           "2 - Domaines/Recettes/Autres",
}
const moveToFolder = async (newCat) => {
  const targetFolder = FOLDER_MAP[newCat] || "2 - Domaines/Recettes/Autres"
  const currentFile = app.vault.getAbstractFileByPath(filePath)
  if (!currentFile) return
  if (!app.vault.getAbstractFileByPath(targetFolder)) await app.vault.createFolder(targetFolder)
  const newPath = targetFolder + "/" + currentFile.name
  if (currentFile.path !== newPath) {
    await app.fileManager.renameFile(currentFile, newPath)
    new Notice("📁 Déplacée dans " + targetFolder.split("/").pop(), 2000)
  }
}
// ── Mode lecture / édition ──────────────────────────────────────────────
// Par défaut en lecture seule : évite de modifier ou supprimer un élément
// par erreur en consultant simplement la recette (ex. depuis le MOC).
// Le calculateur de portions plus bas reste actif quel que soit le mode,
// puisqu'il ne modifie jamais les données enregistrées.
let editMode = _ui.editMode || false
const modeRow = dv.container.createDiv()
modeRow.style.cssText = "display:flex;justify-content:flex-end;margin-bottom:8px;"
const modeBtn = modeRow.createEl("button")
modeBtn.onclick = () => { editMode = !editMode; _ui.editMode = editMode; refreshEditMode() }

// ── En-tête avec cover ────────────────────────────────────────────────
const header = dv.container.createDiv()
header.style.cssText = "display:flex;gap:18px;margin-bottom:20px;align-items:flex-start;"

// Cover
const coverBox = header.createDiv()
coverBox.style.cssText = "width:130px;min-width:130px;aspect-ratio:4/3;border-radius:10px;overflow:hidden;background:var(--background-secondary);display:flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0;"
coverBox.title = "Cliquer pour modifier la photo"

let coverSrc = null
const rawCover = p.cover
if (rawCover) {
  if (rawCover.startsWith("http")) {
    coverSrc = rawCover
  } else {
    const f = app.metadataCache.getFirstLinkpathDest(rawCover, "")
    coverSrc = f ? app.vault.adapter.getResourcePath(f.path) : null
  }
}
if (coverSrc) {
  const img = coverBox.createEl("img")
  img.src = coverSrc
  img.style.cssText = "width:100%;height:100%;object-fit:cover;"
} else {
  const ph = coverBox.createDiv()
  ph.style.cssText = "display:flex;flex-direction:column;align-items:center;gap:4px;"
  ph.createDiv().textContent = "📸"
  const lbl = ph.createDiv(); lbl.style.cssText = "font-size:0.65em;color:var(--text-muted);"
  lbl.textContent = "Photo"
}
coverBox.addEventListener("click", () => { if (!editMode) return; editField("cover", "URL ou nom du fichier photo", p.cover || "") })

// Infos droite
const infoRight = header.createDiv()
infoRight.style.cssText = "flex:1;display:flex;flex-direction:column;gap:8px;"

// Titre
const titreEl = infoRight.createEl("h1")
titreEl.style.cssText = "margin:0;font-size:1.4em;cursor:pointer;"
titreEl.textContent = p.file.name
titreEl.title = "Cliquer pour renommer"
titreEl.addEventListener("click", () => { if (!editMode) return; editField("titre", "Titre", p.file.name) })

// Macros (juste sous le titre)
const macrosRow = infoRight.createDiv()
macrosRow.addEventListener("click", () => { if (!editMode) return; editField("macros", "Macros (ex: 320 kcal - 25g proteines - 40g glucides - 10g lipides)", p.macros || "") })
const renderMacros = () => {
  macrosRow.empty()
  const cur = editMode ? "pointer" : "default"
  if (p.macros) {
    macrosRow.style.display = ""
    macrosRow.style.cssText = `font-size:0.8em;color:var(--text-muted);cursor:${cur};`
    macrosRow.textContent = "🔥 " + p.macros
    macrosRow.title = "Cliquer pour modifier les macros"
  } else if (editMode) {
    macrosRow.style.display = ""
    macrosRow.style.cssText = "font-size:0.8em;color:var(--text-muted);cursor:pointer;font-style:italic;"
    macrosRow.textContent = "+ Ajouter les macros"
  } else {
    macrosRow.style.display = "none"
  }
}
renderMacros()

// Badges infos
const badges = infoRight.createDiv()
badges.style.cssText = "display:flex;gap:8px;flex-wrap:wrap;"

// Difficulte badge
const DIFF_COLORS = { "Facile": "#40a02b", "Moyen": "#fe640b", "Difficile": "#d20f39" }
const diffVal = p.difficulte || "-"
const diffBadge = badges.createEl("span")
const diffColor = DIFF_COLORS[diffVal] || "var(--text-muted)"
diffBadge.style.cssText = `background:${diffColor}22;color:${diffColor};padding:3px 10px;border-radius:10px;font-size:0.8em;font-weight:700;cursor:pointer;`
diffBadge.textContent = "⚡ " + diffVal
diffBadge.title = "Cliquer pour modifier la difficulte"
diffBadge.addEventListener("click", () => { if (!editMode) return; selectField("difficulte", "Difficulte", ["Facile","Moyen","Difficile"], p.difficulte) })

// Temps total
const tempsTotal = (p.temps_prep || 0) + (p.temps_cuisson || 0)
const tempsBadge = badges.createEl("span")
tempsBadge.style.cssText = "background:rgba(74,143,168,0.15);color:#4a8fa8;padding:3px 10px;border-radius:10px;font-size:0.8em;font-weight:700;cursor:pointer;"
const _fmtT = m => m >= 60 ? `${Math.floor(m/60)}h${String(m%60).padStart(2,"0")}` : `${m} min`
tempsBadge.textContent = tempsTotal > 0 ? `⏱ ${_fmtT(tempsTotal)}` : "⏱ - min"
tempsBadge.title = "Cliquer pour modifier les temps"

// Portions
const portionsBadge = badges.createEl("span")
portionsBadge.style.cssText = "background:rgba(136,120,195,0.15);color:#8878c3;padding:3px 10px;border-radius:10px;font-size:0.8em;font-weight:700;cursor:pointer;"
portionsBadge.textContent = p.portions ? `🍽 ${p.portions} portions` : "🍽 - portions"
portionsBadge.title = "Cliquer pour modifier les portions"
portionsBadge.addEventListener("click", () => { if (!editMode) return; editField("portions", "Nombre de portions", p.portions, true) })

// Note
const noteVal = p.note
const noteBadge = badges.createEl("span")
noteBadge.style.cssText = "background:rgba(196,148,58,0.15);color:#c4943a;padding:3px 10px;border-radius:10px;font-size:0.8em;font-weight:700;cursor:pointer;"
if (noteVal) {
  const full = Math.round(noteVal / 2)
  noteBadge.textContent = "★".repeat(full) + "☆".repeat(5 - full) + " " + noteVal + "/10"
} else {
  noteBadge.textContent = "★ Note"
}
noteBadge.title = "Cliquer pour noter"
noteBadge.addEventListener("click", () => {
  if (!editMode) return
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:280px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Note /10"
  const inp = box.createEl("input", {attr:{type:"number",min:"0",max:"10",step:"0.5",value:noteVal||"",style:FIELD,placeholder:"Ex: 8.5"}})
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button",{attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button",{attr:{style:BTN_S}}); ok.textContent = "Enregistrer"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => { await save({note: parseFloat(inp.value)||null}); overlay.remove(); new Notice("Note mise a jour",2000) }
  inp.addEventListener("keydown", e => { if(e.key==="Enter") ok.click(); if(e.key==="Escape") overlay.remove() })
  overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(()=>inp.focus(),50)
})

// Catégorie
const catVal = p.categorie || "-"
const catBadge = badges.createEl("span")
catBadge.style.cssText = "background:var(--background-secondary);color:var(--text-muted);padding:3px 10px;border-radius:10px;font-size:0.8em;cursor:pointer;border:1px solid var(--background-modifier-border);"
catBadge.textContent = "📂 " + catVal
catBadge.title = "Cliquer pour modifier la categorie"
catBadge.addEventListener("click", () => { if (!editMode) return; selectField("catégorie", "Catégorie", ["Plat","Dessert","Petit dejeuner","Collation","Entree","Boisson","Autre"], p.categorie, moveToFolder) })

// Temps prep/cuisson detail au clic
tempsBadge.addEventListener("click", () => {
  if (!editMode) return
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:300px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Temps (en minutes)"
  const g1 = box.createEl("div"); g1.createEl("label",{attr:{style:LABEL}}).textContent = "Preparation"; const inp1 = g1.createEl("input",{attr:{type:"number",min:"0",value:p.temps_prep||"",style:FIELD,placeholder:"Ex: 15"}})
  const g2 = box.createEl("div"); g2.createEl("label",{attr:{style:LABEL}}).textContent = "Cuisson"; const inp2 = g2.createEl("input",{attr:{type:"number",min:"0",value:p.temps_cuisson||"",style:FIELD,placeholder:"Ex: 30"}})
  const btns = box.createEl("div",{attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button",{attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button",{attr:{style:BTN_S}}); ok.textContent = "Enregistrer"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => { await save({temps_prep: parseFloat(inp1.value)||null, temps_cuisson: parseFloat(inp2.value)||null}); overlay.remove(); new Notice("Temps mis a jour",2000) }
  overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(()=>inp1.focus(),50)
})

// ── Source ─────────────────────────────────────────────────────────────
let srcRow = null
if (p.source) {
  srcRow = infoRight.createDiv()
  srcRow.style.cssText = "font-size:0.8em;color:var(--text-muted);cursor:pointer;"
  srcRow.textContent = "🔗 " + p.source
  srcRow.title = "Cliquer pour modifier la source"
  srcRow.addEventListener("click", () => { if (!editMode) return; editField("source", "Source / URL de la recette", p.source) })
} else {
  srcRow = infoRight.createDiv()
  srcRow.style.cssText = "font-size:0.8em;color:var(--text-muted);cursor:pointer;font-style:italic;"
  srcRow.textContent = "+ Ajouter une source"
  srcRow.addEventListener("click", () => { if (!editMode) return; editField("source", "Source / URL de la recette", "") })
}

// ── Ingrédients ────────────────────────────────────────────────────────
const ingrHeader = dv.container.createDiv()
ingrHeader.style.cssText = "display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;"
ingrHeader.createEl("h2", {attr:{style:"margin:0;"}}).textContent = "🥘 Ingrédients"

// ── Calculateur de portions ──────────────────────────────────────────────
// Recalcule uniquement l'affichage (jamais les données enregistrées) : repère
// le nombre en tête de chaque ligne d'ingrédient et le multiplie par le ratio
// portions choisies / portions de base. Les lignes sans quantité chiffrée
// ("sel, poivre") restent inchangées.
const basePortions = Number(p.portions) > 0 ? Number(p.portions) : null
let currentPortions = (_ui.currentPortions != null) ? _ui.currentPortions : basePortions

const _FRACTIONS = { "½":0.5, "⅓":1/3, "⅔":2/3, "¼":0.25, "¾":0.75, "⅕":0.2, "⅖":0.4, "⅗":0.6, "⅘":0.8, "⅙":1/6, "⅚":5/6, "⅛":0.125, "⅜":0.375, "⅝":0.625, "⅞":0.875 }
const parseLeadingQty = str => {
  const m = String(str).match(/^\s*(\d+\s*\/\s*\d+|\d+[.,]\d+|\d+|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])(\s*)([\s\S]*)$/)
  if (!m) return null
  const raw = m[1]
  let qty
  if (raw.includes("/")) { const [a, b] = raw.split("/").map(s => parseFloat(s.trim())); qty = b ? a / b : null }
  else if (_FRACTIONS[raw] !== undefined) qty = _FRACTIONS[raw]
  else qty = parseFloat(raw.replace(",", "."))
  if (qty === null || qty === undefined || isNaN(qty)) return null
  return { qty, sep: m[2], rest: m[3] }
}
const formatQty = n => {
  const r = Math.round(n * 100) / 100
  return (r % 1 === 0) ? String(r) : String(r).replace(".", ",")
}
const scaleIngredient = (str, ratio) => {
  if (ratio === 1) return str
  const parsed = parseLeadingQty(str)
  if (!parsed) return str
  return formatQty(parsed.qty * ratio) + parsed.sep + parsed.rest
}

const portionsCtrl = ingrHeader.createDiv()
portionsCtrl.style.cssText = "display:flex;align-items:center;gap:6px;"

const BTN_ROUND = "width:24px;height:24px;padding:0;border-radius:50%;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.9em;line-height:1;"

const renderPortionsCtrl = () => {
  portionsCtrl.empty()
  if (!basePortions) {
    const hint = portionsCtrl.createEl("span")
    if (editMode) {
      hint.textContent = "🍽 Définir les portions pour activer le calculateur"
      hint.style.cssText = "font-size:0.78em;color:var(--text-muted);cursor:pointer;font-style:italic;"
      hint.addEventListener("click", () => editField("portions", "Nombre de portions", p.portions, true))
    } else {
      hint.textContent = "🍽 Portions non renseignées"
      hint.style.cssText = "font-size:0.78em;color:var(--text-faint);font-style:italic;"
    }
    return
  }
  portionsCtrl.createEl("span", {attr:{style:"font-size:0.78em;color:var(--text-muted);"}}).textContent = "Portions"
  const minusBtn = portionsCtrl.createEl("button", {attr:{style:BTN_ROUND}})
  minusBtn.textContent = "−"
  minusBtn.disabled = currentPortions <= 1
  minusBtn.onclick = () => { if (currentPortions > 1) { currentPortions--; _ui.currentPortions = currentPortions; renderPortionsCtrl(); renderIngredients() } }
  portionsCtrl.createEl("span", {attr:{style:"min-width:18px;text-align:center;font-weight:700;font-size:0.88em;"}}).textContent = String(currentPortions)
  const plusBtn = portionsCtrl.createEl("button", {attr:{style:BTN_ROUND}})
  plusBtn.textContent = "+"
  plusBtn.onclick = () => { currentPortions++; _ui.currentPortions = currentPortions; renderPortionsCtrl(); renderIngredients() }
  if (currentPortions !== basePortions) {
    const resetBtn = portionsCtrl.createEl("button")
    resetBtn.textContent = "↺"
    resetBtn.title = "Revenir aux portions d'origine"
    resetBtn.style.cssText = "background:none;border:none;color:var(--interactive-accent);cursor:pointer;font-size:0.95em;padding:0 2px;"
    resetBtn.onclick = () => { currentPortions = basePortions; _ui.currentPortions = currentPortions; renderPortionsCtrl(); renderIngredients() }
  }
}
renderPortionsCtrl()

const rawIngr = p.ingredients
const ingrArr = rawIngr
  ? (Array.isArray(rawIngr) ? [...rawIngr] : typeof rawIngr === "string" ? [rawIngr] : [...rawIngr]).filter(v => v !== null && v !== undefined && v !== "")
  : []

const ingrBox = dv.container.createDiv()
ingrBox.style.cssText = "display:flex;flex-direction:column;gap:4px;margin:10px 0 20px;"

const renderIngredients = () => {
  ingrBox.empty()
  const ratio = (basePortions && currentPortions) ? currentPortions / basePortions : 1
  for (let idx = 0; idx < ingrArr.length; idx++) {
    const original = ingrArr[idx]
    const scaled = scaleIngredient(original, ratio)

    const row = ingrBox.createDiv()
    row.style.cssText = "display:flex;align-items:center;gap:8px;padding:6px 10px;background:var(--background-secondary);border-radius:6px;font-size:0.9em;"
    const dot = row.createSpan(); dot.textContent = "•"; dot.style.cssText = "color:var(--interactive-accent);font-weight:700;flex-shrink:0;"
    const txt = row.createSpan(); txt.textContent = scaled; txt.style.cssText = "flex:1;"
    if (ratio !== 1 && scaled !== original) {
      const badge = row.createSpan()
      badge.textContent = "×" + formatQty(ratio)
      badge.style.cssText = "font-size:0.68em;color:var(--interactive-accent);background:var(--background-primary);padding:1px 6px;border-radius:6px;flex-shrink:0;"
    }
    if (editMode) {
      const delBtn = row.createEl("button")
      delBtn.textContent = "×"; delBtn.title = "Supprimer"
      delBtn.style.cssText = "background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.1em;padding:0 4px;border-radius:4px;flex-shrink:0;"
      delBtn.onmouseenter = () => { delBtn.style.color = "#d20f39"; delBtn.style.background = "rgba(210,15,57,0.1)" }
      delBtn.onmouseleave = () => { delBtn.style.color = "var(--text-muted)"; delBtn.style.background = "none" }
      const capturedIdx = idx
      delBtn.onclick = async () => {
        ingrArr.splice(capturedIdx, 1)
        await app.fileManager.processFrontMatter(app.vault.getAbstractFileByPath(filePath), fm => { fm.ingredients = [...ingrArr] })
        renderIngredients()
      }
    }
  }
  if (!editMode) {
    if (basePortions && currentPortions !== basePortions) {
      const note = ingrBox.createEl("p")
      note.textContent = `Recette de base pour ${basePortions} portion${basePortions>1?'s':''}. Le recalcul n'affecte que l'affichage, pas les données enregistrées.`
      note.style.cssText = "font-size:0.72em;color:var(--text-muted);margin:4px 0 0;"
    }
    return
  }
  const addBtn = ingrBox.createEl("button")
  addBtn.textContent = "+ Ajouter un ingrédient"; addBtn.style.cssText = ADD_S
  addBtn.onclick = () => {
    const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
    const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:320px;display:flex;flex-direction:column;gap:10px;"}})
    box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Ajouter un ingrédient"
    const inp = box.createEl("input", {attr:{type:"text", placeholder:"Ex: 200g de farine", style:FIELD}})
    if (basePortions && currentPortions !== basePortions) {
      const hint = box.createEl("p", {attr:{style:"margin:0;font-size:0.75em;color:var(--text-muted);"}})
      hint.textContent = `Saisis la quantité pour la recette de base (${basePortions} portion${basePortions>1?'s':''}) - la vue revient aux portions d'origine après ajout.`
    }
    const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
    const cancel = btns.createEl("button", {attr:{style:BTN_G}}); cancel.textContent = "Annuler"
    const ok = btns.createEl("button", {attr:{style:BTN_S}}); ok.textContent = "Ajouter"
    cancel.onclick = () => overlay.remove()
    ok.onclick = async () => {
      const v = inp.value.trim(); if (!v) return
      ingrArr.push(v)
      await app.fileManager.processFrontMatter(app.vault.getAbstractFileByPath(filePath), fm => { fm.ingredients = [...ingrArr] })
      if (basePortions && currentPortions !== basePortions) { currentPortions = basePortions; _ui.currentPortions = currentPortions; renderPortionsCtrl() }
      overlay.remove(); renderIngredients(); new Notice("Ingrédient ajouté", 2000)
    }
    inp.addEventListener("keydown", e => { if(e.key==="Enter") ok.click(); if(e.key==="Escape") overlay.remove() })
    overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
    overlay.append(box); setTimeout(() => inp.focus(), 50)
  }
  if (basePortions && currentPortions !== basePortions) {
    const note2 = ingrBox.createEl("p")
    note2.textContent = `Recette de base pour ${basePortions} portion${basePortions>1?'s':''}. Le recalcul n'affecte que l'affichage, pas les données enregistrées.`
    note2.style.cssText = "font-size:0.72em;color:var(--text-muted);margin:4px 0 0;"
  }
}
renderIngredients()

// ── Étapes ─────────────────────────────────────────────────────────────
dv.container.createEl("h2").textContent = "📋 Étapes"

const rawEtapes = p.etapes
const etapesArr = rawEtapes
  ? (Array.isArray(rawEtapes) ? [...rawEtapes] : typeof rawEtapes === "string" ? [rawEtapes] : [...rawEtapes]).filter(v => v !== null && v !== undefined && v !== "")
  : []

const etapesBox = dv.container.createDiv()
etapesBox.style.cssText = "display:flex;flex-direction:column;gap:6px;margin-bottom:20px;"

const renderEtapes = () => {
  etapesBox.empty()
  for (let idx = 0; idx < etapesArr.length; idx++) {
    const row = etapesBox.createDiv()
    row.style.cssText = "display:flex;align-items:flex-start;gap:10px;padding:8px 12px;background:var(--background-secondary);border-radius:8px;font-size:0.9em;"
    const num = row.createDiv(); num.textContent = idx + 1
    num.style.cssText = "min-width:24px;height:24px;background:var(--interactive-accent);color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.78em;font-weight:700;flex-shrink:0;margin-top:2px;"
    const txt = row.createDiv(); txt.textContent = etapesArr[idx]; txt.style.cssText = "flex:1;line-height:1.5;"
    if (editMode) {
      const delBtn = row.createEl("button")
      delBtn.textContent = "×"; delBtn.title = "Supprimer cette étape"
      delBtn.style.cssText = "background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.1em;padding:0 4px;border-radius:4px;flex-shrink:0;"
      delBtn.onmouseenter = () => { delBtn.style.color = "#d20f39"; delBtn.style.background = "rgba(210,15,57,0.1)" }
      delBtn.onmouseleave = () => { delBtn.style.color = "var(--text-muted)"; delBtn.style.background = "none" }
      const capturedIdx = idx
      delBtn.onclick = async () => {
        etapesArr.splice(capturedIdx, 1)
        await app.fileManager.processFrontMatter(app.vault.getAbstractFileByPath(filePath), fm => { fm.etapes = [...etapesArr] })
        renderEtapes()
      }
    }
  }
  if (!editMode) return
  const addBtn = etapesBox.createEl("button")
  addBtn.textContent = "+ Ajouter une étape"; addBtn.style.cssText = ADD_S
  addBtn.onclick = () => {
    const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
    const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:360px;display:flex;flex-direction:column;gap:10px;"}})
    box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = `Étape ${etapesArr.length + 1}`
    const inp = box.createEl("textarea", {attr:{placeholder:"Décrivez cette étape...", style:FIELD + "min-height:80px;resize:vertical;"}})
    const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
    const cancel = btns.createEl("button", {attr:{style:BTN_G}}); cancel.textContent = "Annuler"
    const ok = btns.createEl("button", {attr:{style:BTN_S}}); ok.textContent = "Ajouter"
    cancel.onclick = () => overlay.remove()
    ok.onclick = async () => {
      const v = inp.value.trim(); if (!v) return
      etapesArr.push(v)
      await app.fileManager.processFrontMatter(app.vault.getAbstractFileByPath(filePath), fm => { fm.etapes = [...etapesArr] })
      overlay.remove(); renderEtapes(); new Notice("Étape ajoutée", 2000)
    }
    inp.addEventListener("keydown", e => { if(e.key==="Escape") overlay.remove() })
    overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
    overlay.append(box); setTimeout(() => inp.focus(), 50)
  }
}
renderEtapes()

// ── Note personnelle ─────────────────────────────────────────────────
dv.container.createEl("h2").textContent = "📝 Note"

const noteBox = dv.container.createDiv()
noteBox.style.cssText = "margin-bottom:20px;"

const editRemarque = () => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:340px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Note personnelle"
  const inp = box.createEl("textarea", {attr:{placeholder:"Ex: Prochaine fois, moins de sucre...", style:FIELD + "min-height:90px;resize:vertical;"}})
  inp.value = p.remarque || ""
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button", {attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button", {attr:{style:BTN_S}}); ok.textContent = "Enregistrer"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => {
    const v = inp.value.trim()
    await save({ remarque: v })
    overlay.remove()
    new Notice("Note mise a jour", 2000)
  }
  inp.addEventListener("keydown", e => { if (e.key === "Escape") overlay.remove() })
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(() => inp.focus(), 50)
}

const renderRemarque = () => {
  noteBox.empty()
  if (p.remarque) {
    const txt = noteBox.createEl("p")
    txt.textContent = p.remarque
    txt.style.cssText = `font-size:0.9em;color:var(--text-normal);white-space:pre-wrap;line-height:1.5;background:var(--background-secondary);border-radius:8px;padding:10px 12px;margin:0;cursor:${editMode ? "pointer" : "default"};`
    txt.title = "Cliquer pour modifier la note"
    txt.addEventListener("click", () => { if (!editMode) return; editRemarque() })
  } else if (editMode) {
    const addBtn = noteBox.createEl("button")
    addBtn.textContent = "+ Ajouter une note"; addBtn.style.cssText = ADD_S
    addBtn.onclick = () => editRemarque()
  }
}
renderRemarque()

// ── Liens externes ─────────────────────────────────────────────────────
dv.container.createEl("h2").textContent = "🔗 Liens utiles"

const linksVal = p.liens || []
const linksArr = typeof linksVal === "string" ? [linksVal] : (Array.isArray(linksVal) ? linksVal : [...linksVal].filter(Boolean))

const linksBox = dv.container.createDiv()
linksBox.style.cssText = "display:flex;flex-direction:column;gap:6px;margin-bottom:12px;"

for (const lien of linksArr) {
  if (!lien) continue
  const row = linksBox.createDiv()
  row.style.cssText = "display:flex;align-items:center;gap:8px;font-size:0.88em;"
  const a = row.createEl("a", {attr:{href: lien, style:"color:var(--interactive-accent);text-decoration:none;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:90%;"}})
  a.textContent = lien
}

const addLienBtn = linksBox.createEl("button", {attr:{style:ADD_S}})
addLienBtn.textContent = "+ Ajouter un lien"
addLienBtn.addEventListener("click", () => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:300px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Ajouter un lien"
  const inp = box.createEl("input", {attr:{type:"url", placeholder:"https://...", style:FIELD}})
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button",{attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button",{attr:{style:BTN_S}}); ok.textContent = "Ajouter"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => {
    const url = inp.value.trim()
    if (!url) return
    const newLinks = [...linksArr, url]
    await save({ liens: newLinks })
    overlay.remove()
    new Notice("Lien ajoute", 2000)
  }
  inp.addEventListener("keydown", e => { if(e.key==="Enter") ok.click(); if(e.key==="Escape") overlay.remove() })
  overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(()=>inp.focus(),50)
})

// ── Photos ─────────────────────────────────────────────────────────────
dv.container.createEl("h2").textContent = "📸 Photos"

const photosVal = p.photos || []
const photosArr = typeof photosVal === "string" ? [photosVal] : (Array.isArray(photosVal) ? photosVal : [...photosVal].filter(Boolean))

const photosBox = dv.container.createDiv()
photosBox.style.cssText = "display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-bottom:12px;"

for (const photo of photosArr) {
  if (!photo) continue
  let src = photo.startsWith("http") ? photo : (() => { const f = app.metadataCache.getFirstLinkpathDest(photo, ""); return f ? app.vault.adapter.getResourcePath(f.path) : null })()
  if (!src) continue
  const imgBox = photosBox.createDiv()
  imgBox.style.cssText = "aspect-ratio:4/3;border-radius:8px;overflow:hidden;"
  const img = imgBox.createEl("img")
  img.src = src
  img.style.cssText = "width:100%;height:100%;object-fit:cover;"
}

const addPhotoBtn = dv.container.createEl("button", {attr:{style:ADD_S}})
addPhotoBtn.textContent = "+ Ajouter une photo"
addPhotoBtn.addEventListener("click", () => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:12px;padding:20px 22px;min-width:300px;display:flex;flex-direction:column;gap:10px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:0.95em;font-weight:700;"}}).textContent = "Ajouter une photo"
  const inp = box.createEl("input", {attr:{type:"text", placeholder:"URL ou nom du fichier (ex: photo.jpg)", style:FIELD}})
  const hint = box.createEl("p", {attr:{style:"margin:0;font-size:0.78em;color:var(--text-muted);"}})
  hint.textContent = "Collez une URL ou entrez le nom d'un fichier image dans votre vault."
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
  const cancel = btns.createEl("button",{attr:{style:BTN_G}}); cancel.textContent = "Annuler"
  const ok = btns.createEl("button",{attr:{style:BTN_S}}); ok.textContent = "Ajouter"
  cancel.onclick = () => overlay.remove()
  ok.onclick = async () => {
    const val = inp.value.trim()
    if (!val) return
    const newPhotos = [...photosArr, val]
    await save({ photos: newPhotos })
    overlay.remove()
    new Notice("Photo ajoutee", 2000)
  }
  inp.addEventListener("keydown", e => { if(e.key==="Enter") ok.click(); if(e.key==="Escape") overlay.remove() })
  overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
  overlay.append(box)
  setTimeout(()=>inp.focus(),50)
})

// ── Applique le mode lecture / édition à tous les éléments interactifs ──
const refreshEditMode = () => {
  modeBtn.textContent = editMode ? "✅ Terminé" : "✏️ Modifier"
  modeBtn.style.cssText = `padding:5px 14px;border-radius:20px;border:${editMode ? "none" : "1px solid var(--background-modifier-border)"};cursor:pointer;font-size:0.8em;font-weight:700;font-family:inherit;background:${editMode ? "var(--interactive-accent)" : "var(--background-secondary)"};color:${editMode ? "#fff" : "var(--text-normal)"};`
  const cur = editMode ? "pointer" : "default"
  coverBox.style.cursor = cur
  titreEl.style.cursor = cur
  diffBadge.style.cursor = cur
  tempsBadge.style.cursor = cur
  portionsBadge.style.cursor = cur
  noteBadge.style.cursor = cur
  catBadge.style.cursor = cur
  if (srcRow) srcRow.style.cursor = cur
  addLienBtn.style.display = editMode ? "" : "none"
  addPhotoBtn.style.display = editMode ? "" : "none"
  renderMacros()
  renderPortionsCtrl()
  renderIngredients()
  renderEtapes()
  renderRemarque()
}
refreshEditMode()
```
