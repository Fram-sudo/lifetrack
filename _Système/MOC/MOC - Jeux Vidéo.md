---
type: moc
tags: [moc, médias]
cssclasses: [media-page]
obsidianUIMode: preview
---

# 🎮 Jeux Vidéo

```dataviewjs
const parseH = h => { const str = String(h||""); if (str.includes(":")) { const [hh,mm]=str.split(":").map(Number); return (hh||0)+(mm||0)/60 } return parseFloat(str)||0 }
const fmtH = h => { const hh=Math.floor(h||0), mm=Math.round(((h||0)-hh)*60); return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h` }
const all = dv.pages('"2 - Domaines/Médias/Jeux Vidéo"').where(p => p.type === "jeu")
const enCours  = all.where(p => p.statut === "en cours").length
const termines = all.where(p => p.statut === "terminé").length
const backlog  = all.where(p => p.statut === "backlog").length
const totalH   = all.array().reduce((t, p) => t + parseH(p.heures_jouées), 0)
const moyNote  = (() => { const n = all.where(p=>p.note); return n.length ? (n.map(p=>p.note).array().reduce((a,b)=>a+b,0)/n.length).toFixed(1) : "-" })()
const bar = dv.container.createDiv()
bar.style.cssText = "display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--background-modifier-border);margin:10px 0 24px;font-size:0.85em;"
for (const c of [
  { val:all.length,                            label:"jeux",      bg:"rgba(74,143,168,0.10)",  color:"#4a8fa8" },
  { val:enCours,                               label:"en cours",  bg:"rgba(30,102,245,0.10)",  color:"#1e66f5" },
  { val:termines,                              label:"terminés",  bg:"rgba(78,138,90,0.10)",   color:"#4e8a5a" },
  { val:backlog,                               label:"backlog",   bg:"rgba(122,118,110,0.10)", color:"#7a766e" },
  { val:totalH > 0 ? fmtH(totalH) : "-",      label:"jouées",    bg:"rgba(136,120,195,0.10)", color:"#8878c3" },
  { val:moyNote,                               label:"note moy.", bg:"rgba(196,148,58,0.10)",  color:"#c4943a" },
]) {
  const cell = bar.createDiv()
  cell.style.cssText = `flex:1;padding:12px 8px;background:${c.bg};text-align:center;border-right:1px solid var(--background-modifier-border);`
  const val = cell.createDiv(); val.style.cssText = `font-size:1.4em;font-weight:800;color:${c.color};line-height:1;margin-bottom:4px;`; val.textContent = String(c.val)
  const lbl = cell.createDiv(); lbl.style.cssText = "font-size:0.78em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;"; lbl.textContent = c.label
}
bar.lastChild.style.borderRight = "none"
```

```dataviewjs
const parseH = h => { const str = String(h||""); if (str.includes(":")) { const [hh,mm]=str.split(":").map(Number); return (hh||0)+(mm||0)/60 } return parseFloat(str)||0 }
const fmtH = h => { const hh=Math.floor(h||0), mm=Math.round(((h||0)-hh)*60); return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h` }

const CFG_JEU = { type:"jeu", icon:"🎮", label:"Jeu", color:"#4a8fa8", bg:"rgba(74,143,168,0.12)" }

function makeCard(grid, page) {
  const card = grid.createDiv()
  card.style.cssText = ["background:var(--background-secondary)","border:1px solid var(--background-modifier-border)","border-radius:10px","overflow:hidden","display:flex","flex-direction:column","cursor:pointer","transition:transform 0.15s,box-shadow 0.15s"].join(";")
  card.onmouseenter = () => { card.style.transform = "translateY(-4px)"; card.style.boxShadow = "0 8px 20px rgba(0,0,0,0.13)" }
  card.onmouseleave = () => { card.style.transform = ""; card.style.boxShadow = "" }
  card.onclick = () => app.workspace.openLinkText(page.file.path, "")
  const imgBox = card.createDiv()
  imgBox.style.cssText = "width:100%;aspect-ratio:2/3;overflow:hidden;flex-shrink:0;position:relative;"
  const rawCover = Array.isArray(page.covers) ? page.covers[0] : page.cover
  let coverSrc = null
  if (rawCover) {
    if (rawCover.startsWith("http")) { coverSrc = rawCover }
    else { const f = app.metadataCache.getFirstLinkpathDest(rawCover, ""); coverSrc = f ? app.vault.adapter.getResourcePath(f.path) : null }
  }
  if (coverSrc) {
    const img = imgBox.createEl("img")
    img.src = coverSrc
    img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;"
    img.onerror = () => { img.style.display = "none"; showPlaceholder(imgBox) }
  } else { showPlaceholder(imgBox) }
  if (page.statut) {
    const STATUS = {
      "en cours":  { bg:"rgba(74,143,168,0.92)",  txt:"▶ En cours"  },
      "backlog":   { bg:"rgba(122,118,110,0.92)",  txt:"⊙ Backlog"   },
      "terminé":   { bg:"rgba(78,138,90,0.92)",    txt:"✓ Terminé"   },
      "abandonné": { bg:"rgba(184,64,64,0.92)",    txt:"✕ Abandonné" },
    }
    const s = STATUS[page.statut.toLowerCase()]
    if (s) {
      const badge = imgBox.createDiv()
      badge.style.cssText = `position:absolute;bottom:6px;left:6px;padding:2px 7px;border-radius:12px;font-size:0.67em;font-weight:700;color:#fff;background:${s.bg};letter-spacing:0.03em;`
      badge.textContent = s.txt
    }
  }
  const info = card.createDiv()
  info.style.cssText = "padding:9px 10px;flex:1;display:flex;flex-direction:column;gap:3px;"
  if (page.note) {
    const stars = info.createDiv()
    stars.style.cssText = "font-size:0.78em;color:#c4943a;letter-spacing:0.02em;"
    const full = Math.round(page.note / 2)
    stars.textContent = "★".repeat(full) + "☆".repeat(5-full) + "  " + page.note + "/10"
  }
  const titleEl = info.createDiv()
  titleEl.style.cssText = "font-weight:700;font-size:0.85em;color:var(--text-normal);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35;"
  titleEl.textContent = page.titre || page.file.name
  if (page.heures_jouées) {
    const subEl = info.createDiv()
    subEl.style.cssText = "font-size:0.73em;color:var(--text-muted);"
    subEl.textContent = fmtH(parseH(page.heures_jouées)) + " jouées"
  }
}

function showPlaceholder(box) {
  box.style.background = CFG_JEU.bg
  const ph = box.createDiv()
  ph.style.cssText = "display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:8px;"
  ph.createDiv().style.cssText = "font-size:2.8em;line-height:1;"
  ph.firstChild.textContent = CFG_JEU.icon
  const lbl = ph.createDiv()
  lbl.style.cssText = `font-size:0.65em;font-weight:800;letter-spacing:0.08em;color:${CFG_JEU.color};text-transform:uppercase;opacity:0.8;`
  lbl.textContent = CFG_JEU.label
}

const GRID_STYLE = "display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:14px;margin:12px 0 28px;"

const FILTERS = [
  { label:"Tout",       key:"tout"      },
  { label:"En cours",   key:"en_cours"  },
  { label:"Terminés",   key:"termines"  },
  { label:"Backlog",    key:"backlog"   },
  { label:"Abandonné",  key:"abandonne" },
  { label:"Notes",      key:"notes"     },
]

let activeFilter = "tout"
let activeSearch  = ""

const allMedias = dv.pages('"2 - Domaines/Médias/Jeux Vidéo"').where(p => p.type === "jeu").array()

const wrap = dv.container.createDiv()
const searchInput = wrap.createEl("input")
searchInput.type = "search"
searchInput.placeholder = "🔍 Rechercher un jeu…"
searchInput.style.cssText = "width:100%;padding:8px 13px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;margin-bottom:14px;font-family:inherit;outline:none;"
searchInput.oninput = () => { activeSearch = searchInput.value.toLowerCase().trim(); renderGrid() }

const tabBar = wrap.createDiv()
tabBar.style.cssText = "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:20px;"
const contentDiv = wrap.createDiv()

const renderGrid = () => {
  contentDiv.empty()
  const sf = activeSearch ? allMedias.filter(p => (p.titre || p.file.name).toLowerCase().includes(activeSearch)) : allMedias

  let filtered
  if (activeFilter === "tout")         filtered = sf
  else if (activeFilter === "en_cours")   filtered = sf.filter(p => p.statut === "en cours")
  else if (activeFilter === "termines")   filtered = sf.filter(p => p.statut === "terminé")
  else if (activeFilter === "backlog")    filtered = sf.filter(p => p.statut === "backlog")
  else if (activeFilter === "abandonne")  filtered = sf.filter(p => p.statut === "abandonné")
  else if (activeFilter === "notes")      filtered = sf.filter(p => p.note).sort((a,b) => (b.note||0)-(a.note||0))
  else filtered = sf

  if (activeFilter === "tout") {
    const enCoursList = sf.filter(p => p.statut === "en cours").sort((a,b) => b.file.mtime-a.file.mtime)
    if (enCoursList.length > 0) {
      contentDiv.createEl("h2").textContent = "🔥 En cours"
      const grid = contentDiv.createDiv(); grid.style.cssText = GRID_STYLE
      for (const p of enCoursList) makeCard(grid, p)
    }
    for (const sub of [
      { title:"⊙ Backlog",    filter: p => p.statut === "backlog"   },
      { title:"✓ Terminés",   filter: p => p.statut === "terminé"   },
      { title:"✕ Abandonnés", filter: p => p.statut === "abandonné" },
    ]) {
      const subPages = sf.filter(sub.filter)
      if (subPages.length === 0) continue
      contentDiv.createEl("h2").textContent = sub.title
      const grid = contentDiv.createDiv(); grid.style.cssText = GRID_STYLE
      for (const p of subPages) makeCard(grid, p)
    }
    return
  }
  if (filtered.length === 0) { contentDiv.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent = "Aucun jeu dans cette catégorie."; return }
  const grid = contentDiv.createDiv(); grid.style.cssText = GRID_STYLE
  for (const p of filtered) makeCard(grid, p)
}

const tabRefs = []
for (const f of FILTERS) {
  const btn = tabBar.createEl("button")
  const refreshBtn = () => { btn.style.cssText = activeFilter === f.key ? "padding:5px 14px;border-radius:20px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.84em;font-weight:700;font-family:inherit;" : "padding:5px 14px;border-radius:20px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;" }
  btn.textContent = f.label
  btn.onclick = () => { activeFilter = f.key; tabRefs.forEach(r => r()); renderGrid() }
  refreshBtn(); tabRefs.push(refreshBtn)
}

renderGrid()
```
