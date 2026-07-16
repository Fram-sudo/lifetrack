---
type: moc
tags:
  - moc
  - médias
cssclasses:
  - media-page
obsidianUIMode: preview
aliases:
---

# 🎬 Films, Animés & Séries

```dataviewjs
const TYPES_CFG = {
  "animé": { icon:"🎌", label:"Animé", color:"#e07b5a", bg:"rgba(224,123,90,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vus" },
  "film":  { icon:"🎬", label:"Film",  color:"#c07850", bg:"rgba(192,120,80,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vus" },
  "série": { icon:"📺", label:"Série", color:"#7b6cb8", bg:"rgba(123,108,184,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vues" },
}

// Toggle state (shared between blocks via window)
if (!window._mocFilmsAnimes) window._mocFilmsAnimes = { type: "animé" }

const activeType = () => window._mocFilmsAnimes.type
const cfg = () => TYPES_CFG[activeType()]

const allAnimés = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "animé").array()
const allFilms  = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "film").array()
const allSéries = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "série").array()
const getPages  = () => activeType() === "animé" ? allAnimés : activeType() === "film" ? allFilms : allSéries

// --- STATS BAR ---
const barWrap = dv.container.createDiv()

const renderBar = () => {
  barWrap.empty()
  const pages = getPages()
  const c = cfg()
  const enCours  = pages.filter(p => p.statut === "en cours").length
  const finis    = pages.filter(p => c.statuts_finis.includes(p.statut)).length
  const aVoir    = pages.filter(p => p.statut === c.statut_voir).length
  const moyNote  = (() => {
    const n = pages.filter(p => p.note)
    return n.length ? (n.reduce((a,b) => a + b.note, 0) / n.length).toFixed(1) : "-"
  })()
  const bar = barWrap.createDiv()
  bar.style.cssText = "display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--background-modifier-border);margin:10px 0 24px;font-size:0.85em;"
  for (const s of [
    { val:pages.length, label:"total",        bg:"rgba(91,141,184,0.10)",  color:"#5b8db8" },
    { val:enCours,      label:"en cours",     bg:"rgba(74,143,168,0.10)",  color:"#4a8fa8" },
    { val:finis,        label:c.label_finis,  bg:"rgba(78,138,90,0.10)",   color:"#4e8a5a" },
    { val:aVoir,        label:c.label_voir,   bg:"rgba(196,148,58,0.10)",  color:"#c4943a" },
    { val:moyNote,      label:"note moyenne", bg:"rgba(136,120,195,0.10)", color:"#8878c3" },
  ]) {
    const cell = bar.createDiv()
    cell.style.cssText = `flex:1;padding:12px 8px;background:${s.bg};text-align:center;border-right:1px solid var(--background-modifier-border);`
    const val = cell.createDiv(); val.style.cssText = `font-size:1.4em;font-weight:800;color:${s.color};line-height:1;margin-bottom:4px;`; val.textContent = String(s.val)
    const lbl = cell.createDiv(); lbl.style.cssText = "font-size:0.78em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;"; lbl.textContent = s.label
  }
  bar.lastChild.style.borderRight = "none"
}

renderBar()
window._mocFilmsAnimes._renderBar = renderBar
```

```dataviewjs
const TYPES_CFG = {
  "animé": { type:"animé", icon:"🎌", label:"Animé", color:"#e07b5a", bg:"rgba(224,123,90,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vus",
    placeholder:"🔍 Rechercher un animé…" },
  "film":  { type:"film",  icon:"🎬", label:"Film",  color:"#c07850", bg:"rgba(192,120,80,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vus",
    placeholder:"🔍 Rechercher un film…" },
  "série": { type:"série", icon:"📺", label:"Série", color:"#7b6cb8", bg:"rgba(123,108,184,0.12)",
    statuts_finis:["vu"], statut_voir:"à voir", label_voir:"À voir", label_finis:"Vues",
    placeholder:"🔍 Rechercher une série…" },
}

if (!window._mocFilmsAnimes) window._mocFilmsAnimes = { type: "animé" }

const allAnimés = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "animé").array()
const allFilms  = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "film").array()
const allSéries = dv.pages('"2 - Domaines/Médias"').where(p => p.type === "série").array()

let activeFilter = "tout"
let activeSearch  = ""
let activeLetter  = ""
let sortMode      = "natural"
let sortDir       = "desc"

const activeType = () => window._mocFilmsAnimes.type
const cfg        = () => TYPES_CFG[activeType()]
const getPages   = () => activeType() === "animé" ? allAnimés : activeType() === "film" ? allFilms : allSéries

// ── Tri alphabétique ──────────────────────────────
const sortAlpha = (arr) => {
  return [...arr].sort((a, b) => {
    const ka = (a.saga || a.titre || a.file.name).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")
    const kb = (b.saga || b.titre || b.file.name).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")
    const c = ka.localeCompare(kb, 'fr')
    if (c !== 0) return c
    return (a.saga_num || a.année || 0) - (b.saga_num || b.année || 0)
  })
}

// ── Lettre de tri d'une entrée ───────────────────
const getAlphaKey = (p) => {
  const raw = (p.saga || p.titre || p.file.name || "").trim().normalize("NFD").replace(/[̀-ͯ]/g,"")
  // Ignorer les articles courants
  const stripped = raw.replace(/^(the |a |an |le |la |les |l'|un |une |des )\s*/i,"")
  const ch = (stripped[0] || raw[0] || "").toUpperCase()
  return /[A-Z]/.test(ch) ? ch : "#"
}

// ── Tri naturel (saga → saga_num → année pour animés ; année pour le reste) ──
const sortNatural = arr => {
  if (activeType() === "animé") return [...arr].sort((a,b) => {
    const ka = (a.saga||a.titre||"").normalize("NFD").replace(/[̀-ͯ]/g,"")
    const kb = (b.saga||b.titre||"").normalize("NFD").replace(/[̀-ͯ]/g,"")
    const sa = sortDir === "desc" ? kb.localeCompare(ka,"fr") : ka.localeCompare(kb,"fr")
    if (sa !== 0) return sa
    const nd = ((a.saga_num||9999)-(b.saga_num||9999)) || ((a.année||0)-(b.année||0))
    return sortDir === "desc" ? -nd : nd
  })
  return [...arr].sort((a,b) => sortDir === "desc" ? (b.année||0)-(a.année||0) : (a.année||0)-(b.année||0))
}

// ── Toutes les lettres présentes dans un tableau ──
const getLettersIn = (arr) => {
  const s = new Set(arr.map(getAlphaKey))
  return ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","#"].filter(l => s.has(l))
}

const wrap = dv.container.createDiv()

// --- TOGGLE ---
const toggleRow = wrap.createDiv()
toggleRow.style.cssText = "display:flex;gap:0;margin-bottom:20px;border-radius:8px;overflow:hidden;border:1px solid var(--background-modifier-border);width:fit-content;"

const toggleBtns = {}
for (const [key, c] of Object.entries(TYPES_CFG)) {
  const btn = toggleRow.createEl("button")
  btn.style.cssText = "padding:7px 22px;border:none;cursor:pointer;font-size:0.88em;font-weight:700;font-family:inherit;transition:background 0.15s,color 0.15s;"
  btn.innerHTML = `${c.icon} ${c.label}s`
  toggleBtns[key] = btn
  btn.onclick = () => {
    window._mocFilmsAnimes.type = key
    activeFilter = "tout"
    activeSearch  = ""
    activeLetter  = ""
    searchInput.value = ""
    searchInput.placeholder = cfg().placeholder
    refreshToggle()
    refreshTabs()
    refreshAlphaBar()
    refreshSortToggle()
    renderGrid()
    if (window._mocFilmsAnimes._renderBar) window._mocFilmsAnimes._renderBar()
  }
}

const refreshToggle = () => {
  for (const [key, btn] of Object.entries(toggleBtns)) {
    if (key === activeType()) {
      btn.style.background = "var(--interactive-accent)"
      btn.style.color = "#fff"
    } else {
      btn.style.background = "var(--background-secondary)"
      btn.style.color = "var(--text-muted)"
    }
  }
}
refreshToggle()

// --- SEARCH ---
const searchInput = wrap.createEl("input")
searchInput.type = "search"
searchInput.placeholder = cfg().placeholder
searchInput.style.cssText = "width:100%;padding:8px 13px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;margin-bottom:10px;font-family:inherit;outline:none;"
searchInput.oninput = () => { activeSearch = searchInput.value.toLowerCase().trim(); activeLetter = ""; refreshAlphaBar(); renderGrid() }

// --- SORT TOGGLE ---
const sortRow = wrap.createDiv()
sortRow.style.cssText = "display:flex;gap:4px;align-items:center;margin-bottom:10px;"
const sortLbl = sortRow.createEl("span"); sortLbl.style.cssText = "font-size:0.78em;color:var(--text-muted);margin-right:2px;"; sortLbl.textContent = "Tri :"
const sortBtns = {}
const refreshSortToggle = () => {
  const base = activeType() === "animé" ? "Saga" : "Date"
  if (sortBtns.natural) sortBtns.natural.textContent = base + (sortMode === "natural" ? (sortDir === "desc" ? " ↓" : " ↑") : "")
  for (const [k,b] of Object.entries(sortBtns)) {
    const on = k === sortMode
    b.style.cssText = `padding:3px 11px;border-radius:5px;border:1px solid ${on?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${on?"var(--interactive-accent)":"var(--background-secondary)"};color:${on?"#fff":"var(--text-muted)"};cursor:pointer;font-size:0.8em;font-weight:700;font-family:inherit;transition:background 0.1s;`
  }
}
for (const [k, lbl] of [["natural","Date"],["alpha","A-Z"]]) {
  const btn = sortRow.createEl("button"); btn.textContent = lbl; sortBtns[k] = btn
  btn.onclick = () => {
    if (k === "natural" && sortMode === "natural") sortDir = sortDir === "desc" ? "asc" : "desc"
    else sortMode = k
    refreshSortToggle(); renderGrid()
  }
}
refreshSortToggle()

// --- BARRE ALPHABET ──────────────────────────────
const alphaBarWrap = wrap.createDiv()
alphaBarWrap.style.cssText = "margin-bottom:14px;"
const alphaBar = alphaBarWrap.createDiv()
alphaBar.style.cssText = "display:flex;flex-wrap:wrap;gap:3px;"
const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#".split("")
const alphaBtns = {}

const refreshAlphaBar = () => {
  const pages = getPages()
  const sf = activeSearch ? pages.filter(p => (p.titre || p.file.name).toLowerCase().includes(activeSearch)) : pages
  let filtered = sf
  if (activeFilter !== "tout") {
    const c = cfg()
    if      (activeFilter === "en_cours") filtered = sf.filter(p => p.statut === "en cours")
    else if (activeFilter === "termines") filtered = sf.filter(p => c.statuts_finis.includes(p.statut))
    else if (activeFilter === "a_voir")   filtered = sf.filter(p => p.statut === c.statut_voir)
    else if (activeFilter === "notes")    filtered = sf.filter(p => p.note)
    else if (activeFilter === "abandonne") filtered = sf.filter(p => p.statut === "abandonné")
  }
  const available = new Set(filtered.map(getAlphaKey))
  for (const l of LETTERS) {
    const btn = alphaBtns[l]
    if (!btn) continue
    const active = activeLetter === l
    const has = available.has(l)
    btn.disabled = !has
    btn.style.cssText = `min-width:24px;padding:3px 5px;border-radius:5px;border:1px solid ${active ? "var(--interactive-accent)" : has ? "var(--background-modifier-border)" : "transparent"};background:${active ? "var(--interactive-accent)" : "transparent"};color:${active ? "#fff" : has ? "var(--text-normal)" : "var(--text-faint)"};cursor:${has ? "pointer" : "default"};font-size:0.78em;font-weight:${active||has ? "700" : "400"};font-family:inherit;transition:background 0.1s;text-align:center;`
  }
}

for (const l of LETTERS) {
  const btn = alphaBar.createEl("button")
  btn.textContent = l
  alphaBtns[l] = btn
  btn.onclick = () => {
    if (btn.disabled) return
    activeLetter = activeLetter === l ? "" : l
    refreshAlphaBar()
    renderGrid()
    // Scroll vers l'ancre si elle existe
    setTimeout(() => {
      const anchor = document.getElementById("alpha-anchor-" + l)
      if (anchor) anchor.scrollIntoView({behavior:"smooth", block:"start"})
    }, 80)
  }
}
refreshAlphaBar()

// --- FILTERS ---
const FILTERS = [
  { label:()=>"Tout",                    key:"tout"     },
  { label:()=>"En cours",               key:"en_cours" },
  { label:()=>cfg().label_finis,         key:"termines" },
  { label:()=>cfg().label_voir,          key:"a_voir"   },
  { label:()=>"Notes",                   key:"notes"    },
]
const tabBar = wrap.createDiv()
tabBar.style.cssText = "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:20px;"

const tabRefs = []
const refreshTabs = () => tabRefs.forEach(r => r())

for (const f of FILTERS) {
  const btn = tabBar.createEl("button")
  const refreshBtn = () => {
    btn.style.cssText = activeFilter === f.key
      ? "padding:5px 14px;border-radius:20px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.84em;font-weight:700;font-family:inherit;"
      : "padding:5px 14px;border-radius:20px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;"
    btn.textContent = f.label()
  }
  btn.onclick = () => { activeFilter = f.key; activeLetter = ""; refreshTabs(); refreshAlphaBar(); renderGrid() }
  refreshBtn(); tabRefs.push(refreshBtn)
}

// --- GRID ---
const contentDiv = wrap.createDiv()
const GRID_STYLE = "display:grid;grid-template-columns:repeat(auto-fill,minmax(145px,1fr));gap:14px;margin:4px 0 28px;"

// ── Séparateur alphabétique ───────────────────────
const makeSep = (letter) => {
  const sep = contentDiv.createDiv()
  sep.id = "alpha-anchor-" + letter
  sep.style.cssText = "display:flex;align-items:center;gap:10px;margin:16px 0 6px;scroll-margin-top:60px;"
  const lbl = sep.createEl("span")
  lbl.style.cssText = "font-size:1em;font-weight:800;color:var(--text-muted);min-width:20px;"
  lbl.textContent = letter
  const line = sep.createEl("div")
  line.style.cssText = "flex:1;height:1px;background:var(--background-modifier-border);"
  return sep
}

// ── Rendu en grille avec séparateurs ─────────────
const renderWithSeparators = (arr) => {
  if (!arr.length) return
  const sorted = sortMode === "alpha" ? sortAlpha(arr) : sortNatural(arr)
  // Si lettre active, filtrer
  const toRender = activeLetter ? sorted.filter(p => getAlphaKey(p) === activeLetter) : sorted
  if (!toRender.length) return
  // Séparateurs uniquement en mode A-Z, plusieurs lettres et assez de cartes
  const letters = getLettersIn(toRender)
  const useSeps = sortMode === "alpha" && letters.length > 1 && toRender.length >= 8
  if (!useSeps) {
    const grid = contentDiv.createDiv(); grid.style.cssText = GRID_STYLE
    for (const p of toRender) makeCard(grid, p)
    return
  }
  let curLetter = null
  let curGrid = null
  for (const p of toRender) {
    const l = getAlphaKey(p)
    if (l !== curLetter) {
      curLetter = l
      makeSep(l)
      curGrid = contentDiv.createDiv(); curGrid.style.cssText = GRID_STYLE
    }
    makeCard(curGrid, p)
  }
}

function showPlaceholder(box) {
  const c = cfg()
  box.style.background = c.bg
  const ph = box.createDiv(); ph.style.cssText = "display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:8px;"
  ph.createDiv().style.cssText = "font-size:2.8em;line-height:1;"; ph.firstChild.textContent = c.icon
  const lbl = ph.createDiv(); lbl.style.cssText = `font-size:0.65em;font-weight:800;letter-spacing:0.08em;color:${c.color};text-transform:uppercase;opacity:0.8;`; lbl.textContent = c.label
}

function makeCard(grid, page) {
  const c = cfg()
  const card = grid.createDiv()
  card.style.cssText = ["background:var(--background-secondary)","border:1px solid var(--background-modifier-border)","border-radius:10px","overflow:hidden","display:flex","flex-direction:column","cursor:pointer","transition:transform 0.15s,box-shadow 0.15s"].join(";")
  card.onmouseenter = () => { card.style.transform = "translateY(-4px)"; card.style.boxShadow = "0 8px 20px rgba(0,0,0,0.13)" }
  card.onmouseleave = () => { card.style.transform = ""; card.style.boxShadow = "" }
  card.onclick = () => app.workspace.openLinkText(page.file.path, "")
  const imgBox = card.createDiv(); imgBox.style.cssText = "width:100%;aspect-ratio:2/3;overflow:hidden;flex-shrink:0;position:relative;"
  const rawCover = Array.isArray(page.covers) ? page.covers[0] : page.cover
  let coverSrc = null
  if (rawCover) {
    if (rawCover.startsWith("http")) { coverSrc = rawCover }
    else { const f = app.metadataCache.getFirstLinkpathDest(rawCover, ""); coverSrc = f ? app.vault.adapter.getResourcePath(f.path) : null }
  }
  if (coverSrc) {
    const img = imgBox.createEl("img"); img.src = coverSrc; img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;"
    img.onerror = () => { img.style.display = "none"; showPlaceholder(imgBox) }
  } else { showPlaceholder(imgBox) }
  if (page.statut) {
    const STATUS = {
      "en cours":  { bg:"rgba(74,143,168,0.92)",  txt:"▶ En cours"  },
      "à voir":    { bg:"rgba(196,148,58,0.92)",   txt:"◯ À voir"    },
      "vu":        { bg:"rgba(78,138,90,0.92)",    txt:"✓ Vu"        },
      "terminé":   { bg:"rgba(78,138,90,0.92)",    txt:"✓ Terminé"   },
      "terminée":  { bg:"rgba(78,138,90,0.92)",    txt:"✓ Terminé"   },
      "abandonné": { bg:"rgba(184,64,64,0.92)",    txt:"✕ Abandonné" },
    }
    const s = STATUS[page.statut.toLowerCase()]
    if (s) {
      const badge = imgBox.createDiv()
      badge.style.cssText = `position:absolute;bottom:6px;left:6px;padding:2px 7px;border-radius:12px;font-size:0.67em;font-weight:700;color:#fff;background:${s.bg};letter-spacing:0.03em;`
      badge.textContent = s.txt
    }
  }
  const info = card.createDiv(); info.style.cssText = "padding:9px 10px;flex:1;display:flex;flex-direction:column;gap:3px;"
  if (page.note) {
    const stars = info.createDiv(); stars.style.cssText = "font-size:0.78em;color:#c4943a;letter-spacing:0.02em;"
    const full = Math.round(page.note / 2); stars.textContent = "★".repeat(full) + "☆".repeat(5-full) + "  " + page.note + "/10"
  }
  const titleEl = info.createDiv(); titleEl.style.cssText = "font-weight:700;font-size:0.85em;color:var(--text-normal);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35;"; titleEl.textContent = page.titre || page.file.name
  let sub = ""
  if (activeType() === "animé") {
    if (page.saga) {
      const _cnt = allAnimés.filter(p => p.saga === page.saga).length
      if (_cnt >= 1) sub = _cnt > 1 ? `${_cnt} saisons` : `${_cnt} saison`
    }
  } else if (activeType() === "film" && page.année) sub = String(page.année)
  else if (activeType() === "série") {
    const parts = []
    if (page.saisons) parts.push(page.saisons > 1 ? `${page.saisons} saisons` : `${page.saisons} saison`)
    if (page.plateforme) parts.push(page.plateforme)
    sub = parts.join(" · ")
  }
  if (sub) { const subEl = info.createDiv(); subEl.style.cssText = "font-size:0.73em;color:var(--text-muted);"; subEl.textContent = sub }
}

const renderGrid = () => {
  contentDiv.empty()
  const pages = getPages()
  const c = cfg()
  const sf = activeSearch ? pages.filter(p => (p.titre || p.file.name).toLowerCase().includes(activeSearch)) : pages

  let filtered
  if      (activeFilter === "tout")     filtered = sf
  else if (activeFilter === "en_cours") filtered = sf.filter(p => p.statut === "en cours")
  else if (activeFilter === "termines") filtered = sf.filter(p => c.statuts_finis.includes(p.statut))
  else if (activeFilter === "a_voir")   filtered = sf.filter(p => p.statut === c.statut_voir)
  else if (activeFilter === "notes")    filtered = sf.filter(p => p.note).sort((a,b) => (b.note||0)-(a.note||0))
  else filtered = sf

  // Filtre lettre active (en dehors du mode "notes" qui a son propre tri)
  if (activeLetter && activeFilter !== "notes") {
    filtered = filtered.filter(p => getAlphaKey(p) === activeLetter)
  }

  if (activeFilter === "tout") {
    const _lf = arr => activeLetter ? arr.filter(p => getAlphaKey(p) === activeLetter) : arr
    const enCoursList = _lf(sf.filter(p => p.statut === "en cours"))
    if (enCoursList.length) {
      contentDiv.createEl("h2").textContent = "🔥 En cours"
      renderWithSeparators(enCoursList)
    }
    const aVoirList = _lf(sf.filter(p => p.statut === c.statut_voir))
    if (aVoirList.length) {
      contentDiv.createEl("h2").textContent = `◯ ${c.label_voir}`
      renderWithSeparators(aVoirList)
    }
    const finisList = _lf(sf.filter(p => c.statuts_finis.includes(p.statut)))
    if (finisList.length) {
      contentDiv.createEl("h2").textContent = `✓ ${c.label_finis}`
      renderWithSeparators(finisList)
    }
    const abandList = _lf(sf.filter(p => p.statut === "abandonné"))
    if (abandList.length) {
      contentDiv.createEl("h2").textContent = "✕ Abandonnés"
      renderWithSeparators(abandList)
    }
    if (!sf.length) contentDiv.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent = `Aucun ${c.label.toLowerCase()} dans le vault.`
    return
  }

  if (!filtered.length) {
    contentDiv.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent = "Aucun contenu dans cette catégorie."
    return
  }
  if (activeFilter === "notes") {
    const grid = contentDiv.createDiv(); grid.style.cssText = GRID_STYLE
    for (const p of filtered) makeCard(grid, p)
  } else {
    renderWithSeparators(filtered)
  }
}

renderGrid()
```
