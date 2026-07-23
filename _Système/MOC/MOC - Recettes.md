---
type: moc
tags: [moc, recettes, cuisine]
cssclasses: [dashboard]
obsidianUIMode: preview
---

# 🍳 Recettes

```dataviewjs
// ── STATS GLOBALES ────────────────────────────────────────────────────
const all = dv.pages('"2 - Domaines/Recettes"').where(p => p.type === "recette")

let totalRecettes = all.length
let plats     = all.where(p => p.categorie === "Plat").length
let desserts  = all.where(p => p.categorie === "Dessert").length
const notees  = all.where(p => p.note)
const moyNote = notees.length
  ? (notees.map(p => p.note).array().reduce((a, b) => a + b, 0) / notees.length).toFixed(1)
  : "-"

const bar = dv.container.createDiv()
bar.style.cssText = "display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--background-modifier-border);margin:10px 0 24px;font-size:0.85em;"

const cells = [
  { val: totalRecettes, label: "recettes",     bg: "rgba(91,141,184,0.10)",  color: "#5b8db8" },
  { val: plats,         label: "plats",         bg: "rgba(64,160,43,0.10)",   color: "#40a02b" },
  { val: desserts,      label: "desserts",      bg: "rgba(254,100,11,0.10)",  color: "#fe640b" },
  { val: moyNote,       label: "note moyenne",  bg: "rgba(196,148,58,0.10)",  color: "#c4943a" },
]
for (const c of cells) {
  const cell = bar.createDiv()
  cell.style.cssText = `flex:1;padding:12px 8px;background:${c.bg};text-align:center;border-right:1px solid var(--background-modifier-border);`
  const val = cell.createDiv()
  val.style.cssText = `font-size:1.4em;font-weight:800;color:${c.color};line-height:1;margin-bottom:4px;`
  val.textContent = String(c.val)
  const lbl = cell.createDiv()
  lbl.style.cssText = "font-size:0.78em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;"
  lbl.textContent = c.label
}
bar.lastChild.style.borderRight = "none"
```

```dataviewjs
// ── GALERIE AVEC FILTRES ──────────────────────────────────────────────
const TABS = [
  { label: "Tout",             filter: p => true },
  { label: "Plats",            filter: p => p.categorie === "Plat" },
  { label: "Desserts",         filter: p => p.categorie === "Dessert" },
  { label: "Petit déj",        filter: p => p.categorie === "Petit dejeuner" },
  { label: "Collations",       filter: p => p.categorie === "Collation" },
  { label: "Meilleures notes", filter: p => p.note >= 8 },
]

const CAT_CFG = {
  "Plat":            { icon:"🍽", color:"#40a02b", bg:"rgba(64,160,43,0.12)"   },
  "Dessert":         { icon:"🍰", color:"#fe640b", bg:"rgba(254,100,11,0.12)"  },
  "Petit dejeuner":  { icon:"🥐", color:"#c4943a", bg:"rgba(196,148,58,0.12)"  },
  "Collation":       { icon:"🍪", color:"#8878c3", bg:"rgba(136,120,195,0.12)" },
  "Entree":          { icon:"🥗", color:"#4a8fa8", bg:"rgba(74,143,168,0.12)"  },
  "Boisson":         { icon:"🥤", color:"#1e66f5", bg:"rgba(30,102,245,0.12)"  },
  "Autre":           { icon:"🍴", color:"#7a766e", bg:"rgba(122,118,110,0.12)" },
  default:           { icon:"🍳", color:"#c4943a", bg:"rgba(196,148,58,0.12)"  },
}

const DIFF_COLORS = { "Facile": "#40a02b", "Moyen": "#fe640b", "Difficile": "#d20f39" }
const GRID_STYLE = "display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px;margin:14px 0 10px;"

let activeTab    = 0
let activeSearch = ""
const allRecettes = dv.pages('"2 - Domaines/Recettes"').where(p => p.type === "recette").array()

const wrap = dv.container.createDiv()

// ── Barre de recherche ────────────────────────────────────────────────
const searchInput = wrap.createEl("input")
searchInput.type = "search"
searchInput.placeholder = "🔍 Rechercher une recette…"
searchInput.style.cssText = "width:100%;padding:8px 13px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;margin-bottom:14px;font-family:inherit;outline:none;"
searchInput.oninput = () => { activeSearch = searchInput.value.toLowerCase().trim(); renderGrid() }

// Onglets
const tabBar = wrap.createDiv()
tabBar.style.cssText = "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px;"

const contentDiv = wrap.createDiv()

const makeCard = (grid, page) => {
  const cfg = CAT_CFG[page.categorie] || CAT_CFG.default
  const card = grid.createDiv()
  card.style.cssText = [
    "background:var(--background-secondary)",
    "border:1px solid var(--background-modifier-border)",
    "border-radius:10px",
    "overflow:hidden",
    "display:flex",
    "flex-direction:column",
    "cursor:pointer",
    "transition:transform 0.15s,box-shadow 0.15s",
  ].join(";")
  card.onmouseenter = () => { card.style.transform = "translateY(-4px)"; card.style.boxShadow = "0 8px 20px rgba(0,0,0,0.13)" }
  card.onmouseleave = () => { card.style.transform = ""; card.style.boxShadow = "" }
  card.onclick = () => app.workspace.openLinkText(page.file.path, "", false)

  // Image
  const imgBox = card.createDiv()
  imgBox.style.cssText = "width:100%;aspect-ratio:4/3;overflow:hidden;flex-shrink:0;position:relative;"

  const rawCover = page.cover
  let coverSrc = null
  if (rawCover) {
    if (rawCover.startsWith("http")) {
      coverSrc = rawCover
    } else {
      const f = app.metadataCache.getFirstLinkpathDest(rawCover, "")
      coverSrc = f ? app.vault.adapter.getResourcePath(f.path) : null
    }
  }
  if (coverSrc) {
    const img = imgBox.createEl("img")
    img.src = coverSrc
    img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;"
    img.onerror = () => { img.style.display = "none"; showPh() }
  } else {
    showPh()
  }

  function showPh() {
    imgBox.style.background = cfg.bg
    const ph = imgBox.createDiv()
    ph.style.cssText = "display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:6px;"
    ph.createDiv().textContent = cfg.icon
    ph.lastChild.style.cssText = "font-size:2.5em;line-height:1;"
  }

  // Badge difficulte
  if (page.difficulte) {
    const dc = DIFF_COLORS[page.difficulte] || "#7a766e"
    const badge = imgBox.createDiv()
    badge.style.cssText = `position:absolute;bottom:6px;left:6px;padding:2px 7px;border-radius:12px;font-size:0.67em;font-weight:700;color:#fff;background:${dc}ee;`
    badge.textContent = page.difficulte
  }

  // Infos
  const info = card.createDiv()
  info.style.cssText = "padding:9px 10px;flex:1;display:flex;flex-direction:column;gap:3px;"

  if (page.note) {
    const stars = info.createDiv()
    stars.style.cssText = "font-size:0.75em;color:#c4943a;"
    const full = Math.round(page.note / 2)
    stars.textContent = "★".repeat(full) + "☆".repeat(5 - full) + "  " + page.note + "/10"
  }

  const titleEl = info.createDiv()
  titleEl.style.cssText = "font-weight:700;font-size:0.85em;color:var(--text-normal);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35;"
  titleEl.textContent = page.file.name

  // Temps total
  const total = (page.temps_prep || 0) + (page.temps_cuisson || 0)
  if (total > 0) {
    const t = info.createDiv()
    t.style.cssText = "font-size:0.72em;color:var(--text-muted);"
    t.textContent = `⏱ ${total} min`
  }
}

const renderGrid = () => {
  contentDiv.empty()
  let filtered = allRecettes.filter(TABS[activeTab].filter)
  if (activeSearch) filtered = filtered.filter(p => p.file.name.toLowerCase().includes(activeSearch))

  if (filtered.length === 0) {
    contentDiv.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent = "Aucune recette dans cette catégorie."
    return
  }

  const grid = contentDiv.createDiv()
  grid.style.cssText = GRID_STYLE
  for (const p of filtered) makeCard(grid, p)
}

// Onglets
const tabRefs = []
TABS.forEach((t, i) => {
  const btn = tabBar.createEl("button")
  const isActive = () => activeTab === i
  const refreshBtn = () => {
    btn.style.cssText = isActive()
      ? "padding:5px 14px;border-radius:20px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.84em;font-weight:700;font-family:inherit;"
      : "padding:5px 14px;border-radius:20px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;"
  }
  btn.textContent = t.label
  btn.onclick = () => { activeTab = i; tabRefs.forEach(r => r()); renderGrid() }
  refreshBtn()
  tabRefs.push(refreshBtn)
})

renderGrid()
```
