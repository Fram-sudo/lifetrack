---
type: moc
tags: [moc, explorateur]
cssclasses: [dashboard]
obsidianUIMode: preview
---

# 🔍 Explorateur

```dataviewjs
// ══════════════════════════════════════════════════════════════════════════
//  EXPLORATEUR - toutes les pages du vault, double mode de recherche
// ══════════════════════════════════════════════════════════════════════════

// ── Domaines ──────────────────────────────────────────────────────────────
const DOMAINS = [
  { key:"tout",     label:"Tout",      icon:"🌐", color:"#5b8db8", match: p => true },
  { key:"media",    label:"Médias",    icon:"🎬", color:"#e07b5a",
    match: p => p.file.path.startsWith("2 - Domaines/Médias") &&
                ["animé","série","manga","manwha","manhua","film","jeu","livre"].includes(p.type) },
  { key:"commande", label:"Commandes", icon:"🛒", color:"#fe640b", match: p => p.type === "commande" },
  { key:"finance",  label:"Finances",  icon:"💰", color:"#40a02b", match: p => p.file.path.startsWith("2 - Domaines/Finances") },
  { key:"systeme",  label:"Système",   icon:"⚙️", color:"#888888", match: p => p.file.path.startsWith("_Système") },
]

// ── Tris ──────────────────────────────────────────────────────────────────
const SORTS = [
  { label:"Modif. ↓", fn:(a,b) => getMtime(b) - getMtime(a) },
  { label:"Modif. ↑", fn:(a,b) => getMtime(a) - getMtime(b) },
  { label:"Nom A→Z",  fn:(a,b) => a.file.name.localeCompare(b.file.name, "fr") },
  { label:"Nom Z→A",  fn:(a,b) => b.file.name.localeCompare(a.file.name, "fr") },
]

// ── Notes : labels qualitatifs → seuils numériques ────────────────────────
const NOTE_OPTS = [
  { v:0, l:"Toutes"        },
  { v:5, l:"Correct (≥5)"  },
  { v:7, l:"Bien (≥7)"     },
  { v:9, l:"Excellent (≥9)"},
]

const TYPE_LABELS = {
  "animé":"🎌 Animé","série":"📺 Série","manga":"📖 Manga","manwha":"📗 Manwha","manhua":"📘 Manhua",
  "film":"🎬 Film","jeu":"🎮 Jeu","livre":"📚 Livre","commande":"🛒 Commande",
  "moc":"🗂 MOC","dashboard":"📊 Dashboard",
}

// Tags système à exclure (non porteurs d'information métier)
const SYSTEM_TAGS = new Set([
  "moc","dashboard","home","médias","commandes","animés","mangas","finances","budget","suivi","série","guide","lifetrack"
])

// ── Helpers ───────────────────────────────────────────────────────────────
const getMtime    = p => { const m = p.file.mtime; return m ? (m.toMillis ? m.toMillis() : new Date(m).getTime()) : 0 }
const fmtDate     = ts => { const d = new Date(ts); return `${String(d.getDate()).padStart(2,"0")}/${String(d.getMonth()+1).padStart(2,"0")}/${d.getFullYear()}` }
const getPageTags = p => {
  if (!p.tags) return []
  return (Array.isArray(p.tags) ? p.tags : [p.tags]).map(String).filter(t => t && !SYSTEM_TAGS.has(t.toLowerCase()))
}

// ── Chargement de TOUTES les pages du vault (sans exclusion) ──────────────
const allPages = dv.pages().array()

// ── État ──────────────────────────────────────────────────────────────────
let activeDomain    = "tout"
let activeSort      = 0
let activeSearch    = ""
let activeSearchMode = "titre"  // "titre" | "contenu"
let activeStatut    = ""
let activePeriode   = ""
let activeNote      = 0
let activeTag       = ""
let panelOpen       = false
let _searchId       = 0  // annulation recherche contenu en cours

// ── Styles ────────────────────────────────────────────────────────────────
const S_PILL_A  = c => `padding:4px 12px;border-radius:16px;border:none;cursor:pointer;font-size:0.81em;font-weight:700;font-family:inherit;background:${c};color:#fff;`
const S_PILL_I  = "padding:4px 12px;border-radius:16px;border:1px solid var(--background-modifier-border);cursor:pointer;font-size:0.81em;font-family:inherit;background:var(--background-secondary);color:var(--text-muted);"
const S_ROW     = "display:flex;align-items:center;gap:7px;flex-wrap:wrap;padding:7px 10px;border-radius:8px;margin-bottom:5px;"
const S_LABEL   = "font-size:0.72em;font-weight:700;color:var(--text-muted);white-space:nowrap;min-width:60px;text-transform:uppercase;letter-spacing:0.05em;"
const S_SEL     = "padding:4px 8px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.81em;font-family:inherit;cursor:pointer;outline:none;"
const S_BTN_N   = "padding:7px 14px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.85em;font-family:inherit;display:flex;align-items:center;gap:6px;white-space:nowrap;"
const S_BTN_A   = "padding:7px 14px;border-radius:8px;border:1px solid var(--interactive-accent);background:rgba(var(--interactive-accent-rgb,99,102,241),0.12);color:var(--interactive-accent);cursor:pointer;font-size:0.85em;font-family:inherit;display:flex;align-items:center;gap:6px;white-space:nowrap;font-weight:700;"
const S_MODE_A  = "padding:6px 13px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.82em;font-family:inherit;font-weight:700;"
const S_MODE_I  = "padding:6px 13px;border:none;background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.82em;font-family:inherit;"

// ── DOM principal ─────────────────────────────────────────────────────────
const wrap = dv.container.createDiv()

// ── Barre principale ──────────────────────────────────────────────────────
const toolbar = wrap.createDiv()
toolbar.style.cssText = "display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap;"

// Champ de recherche
const searchInput = toolbar.createEl("input")
searchInput.type = "search"
searchInput.placeholder = "Rechercher…"
searchInput.style.cssText = "flex:1;min-width:160px;padding:8px 14px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.92em;font-family:inherit;outline:none;"
searchInput.oninput = () => { activeSearch = searchInput.value.toLowerCase().trim(); renderResults() }

// ── Toggle mode de recherche ──────────────────────────────────────────────
const modeWrap = toolbar.createDiv()
modeWrap.style.cssText = "display:flex;border:1px solid var(--background-modifier-border);border-radius:8px;overflow:hidden;flex-shrink:0;"
const modeTitle   = modeWrap.createEl("button"); modeTitle.textContent   = "🔤 Titre"
const modeContent = modeWrap.createEl("button"); modeContent.textContent = "📄 Contenu"
const updateModeBtns = () => {
  modeTitle.style.cssText   = activeSearchMode === "titre"   ? S_MODE_A : S_MODE_I
  modeContent.style.cssText = activeSearchMode === "contenu" ? S_MODE_A : S_MODE_I
}
modeTitle.onclick   = () => { activeSearchMode = "titre";   updateModeBtns(); renderResults() }
modeContent.onclick = () => { activeSearchMode = "contenu"; updateModeBtns(); renderResults() }
updateModeBtns()

// Bouton Filtres
const filterBtn = toolbar.createEl("button")
filterBtn.style.cssText = S_BTN_N
filterBtn.onclick = () => { panelOpen = !panelOpen; filterPanel.style.display = panelOpen ? "block" : "none"; updateFilterBtn() }

// Tri
const sortSel = toolbar.createEl("select")
sortSel.style.cssText = "padding:7px 10px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.85em;font-family:inherit;cursor:pointer;outline:none;"
SORTS.forEach((s,i) => { const o = sortSel.createEl("option",{attr:{value:String(i)}}); o.textContent = s.label })
sortSel.onchange = () => { activeSort = Number(sortSel.value); renderResults() }

// ── Panneau de filtres (caché par défaut) ─────────────────────────────────
const filterPanel = wrap.createDiv()
filterPanel.style.cssText = "display:none;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:12px 14px;margin-bottom:10px;"
const dynDiv = filterPanel.createDiv()

// ── Compteur + résultats ──────────────────────────────────────────────────
const countEl = wrap.createDiv()
countEl.style.cssText = "font-size:0.78em;color:var(--text-muted);margin-bottom:8px;min-height:1.2em;"
const contentDiv = wrap.createDiv()

// ── Nb de filtres actifs ──────────────────────────────────────────────────
const countActiveFilters = () => {
  let n = 0
  if (activeDomain  !== "tout") n++
  if (activeStatut  !== "")     n++
  if (activePeriode !== "")     n++
  if (activeNote    >   0)      n++
  if (activeTag     !== "")     n++
  return n
}

const updateFilterBtn = () => {
  const n = countActiveFilters()
  filterBtn.textContent = ""
  filterBtn.createEl("span").textContent = "🎚"
  filterBtn.createEl("span").textContent = "Filtres"
  if (n > 0) {
    const badge = filterBtn.createEl("span")
    badge.style.cssText = "background:var(--interactive-accent);color:#fff;border-radius:10px;padding:1px 7px;font-size:0.78em;font-weight:800;"
    badge.textContent = String(n)
    filterBtn.style.cssText = S_BTN_A
  } else {
    filterBtn.style.cssText = S_BTN_N
  }
}

// ── Pages du domaine actif ────────────────────────────────────────────────
const getDomainPages = () => {
  const dom = DOMAINS.find(d => d.key === activeDomain) || DOMAINS[0]
  return allPages.filter(dom.match)
}

// ── Application des filtres hors recherche ────────────────────────────────
const applyFilters = pages => {
  let out = pages

  if (activeStatut) out = out.filter(p => p.statut === activeStatut)

  if (activePeriode) {
    const todayStart = new Date(); todayStart.setHours(0,0,0,0)
    const cutoff = activePeriode === "today" ? todayStart.getTime()
      : activePeriode === "week"  ? Date.now() - 7  * 86400000
      : activePeriode === "month" ? Date.now() - 30 * 86400000 : 0
    if (cutoff) out = out.filter(p => getMtime(p) >= cutoff)
  }

  if (activeNote > 0) out = out.filter(p => p.note != null && Number(p.note) >= activeNote)

  if (activeTag) out = out.filter(p => getPageTags(p).includes(activeTag))

  return out
}

// ── Rendu du tableau de résultats ─────────────────────────────────────────
const renderTable = (pages, highlightQuery) => {
  contentDiv.empty()
  const sorted = [...pages].sort(SORTS[activeSort].fn)

  countEl.textContent = sorted.length + " note" + (sorted.length !== 1 ? "s" : "") + " trouvée" + (sorted.length !== 1 ? "s" : "")

  if (sorted.length === 0) {
    const e = contentDiv.createEl("div")
    e.style.cssText = "text-align:center;padding:32px 0;color:var(--text-muted);font-size:0.9em;"
    e.textContent = "Aucun résultat pour ces filtres."
    return
  }

  const table = contentDiv.createEl("table"); table.style.cssText = "width:100%;border-collapse:collapse;font-size:0.87em;"
  const hrow = table.createEl("thead").createEl("tr")
  for (const h of ["Nom","Type","Statut / Catégorie","Modifié","Dossier"]) {
    const th = hrow.createEl("th")
    th.style.cssText = "text-align:left;padding:6px 10px;font-size:0.76em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:2px solid var(--background-modifier-border);white-space:nowrap;"
    th.textContent = h
  }

  const tbody = table.createEl("tbody")
  for (const p of sorted) {
    const tr = tbody.createEl("tr"); tr.style.cursor = "pointer"
    tr.onmouseenter = () => tr.style.background = "var(--background-secondary)"
    tr.onmouseleave = () => tr.style.background = ""
    tr.onclick = () => app.workspace.openLinkText(p.file.path, "", false)
    const TD = "padding:7px 10px;border-bottom:1px solid var(--background-modifier-border);vertical-align:middle;"

    // Nom
    const tdN = tr.createEl("td",{attr:{style:TD+"font-weight:600;max-width:260px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;"}})
    tdN.textContent = p.titre || p.file.name

    // Type
    tr.createEl("td",{attr:{style:TD+"white-space:nowrap;font-size:0.82em;color:var(--text-muted);"}}).textContent = TYPE_LABELS[p.type] || (p.type ? "📄 "+p.type : "-")

    // Statut / catégorie + étoile si note
    const tdS = tr.createEl("td",{attr:{style:TD}})
    const stVal = p.statut || p.categorie || ""
    if (stVal) {
      const sp = tdS.createEl("span")
      sp.style.cssText = "font-size:0.8em;padding:2px 8px;border-radius:10px;background:var(--background-secondary);color:var(--text-muted);border:1px solid var(--background-modifier-border);"
      sp.textContent = stVal
    }
    if (p.note != null && !isNaN(Number(p.note))) {
      const ns = tdS.createEl("span")
      ns.style.cssText = "font-size:0.78em;color:#c4943a;margin-left:" + (stVal ? "6px" : "0") + ";"
      ns.textContent = "★ " + p.note + "/10"
    }
    if (!stVal && (p.note == null || isNaN(Number(p.note)))) { tdS.textContent = "-"; tdS.style.color = "var(--text-faint)" }

    // Modifié
    tr.createEl("td",{attr:{style:TD+"color:var(--text-muted);font-size:0.84em;white-space:nowrap;"}}).textContent = fmtDate(getMtime(p))

    // Dossier
    const tdF = tr.createEl("td",{attr:{style:TD+"color:var(--text-faint);font-size:0.8em;max-width:180px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;"}})
    tdF.textContent = p.file.folder
  }
}

// ── Construction du panneau de filtres ────────────────────────────────────
const renderFilters = () => {
  dynDiv.empty()
  const dp = getDomainPages()

  // ── Domaine ────────────────────────────────────────────────────────────
  const domRow = dynDiv.createDiv()
  domRow.style.cssText = S_ROW + "background:rgba(91,141,184,0.05);border:1px solid rgba(91,141,184,0.12);"
  domRow.createEl("span",{attr:{style:S_LABEL}}).textContent = "Domaine"
  const domPills = domRow.createDiv(); domPills.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;"
  const domRefs = []
  for (const d of DOMAINS) {
    const btn = domPills.createEl("button"); btn.textContent = d.icon + " " + d.label
    const ref = () => { btn.style.cssText = activeDomain === d.key ? S_PILL_A(d.color) : S_PILL_I }
    btn.onclick = () => {
      activeDomain = d.key; activeStatut = ""; activeTag = ""
      domRefs.forEach(r => r()); renderFilters(); renderResults(); updateFilterBtn()
    }
    ref(); domRefs.push(ref)
  }

  // ── Statut ────────────────────────────────────────────────────────────
  const statuts = [...new Set(dp.map(p => p.statut).filter(Boolean))].sort()
  if (statuts.length > 0) {
    if (!statuts.includes(activeStatut)) activeStatut = ""
    const row = dynDiv.createDiv()
    row.style.cssText = S_ROW + "background:rgba(254,100,11,0.04);border:1px solid rgba(254,100,11,0.12);"
    row.createEl("span",{attr:{style:S_LABEL}}).textContent = "Statut"
    const pDiv = row.createDiv(); pDiv.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;"
    const refs = []
    for (const s of ["", ...statuts]) {
      const btn = pDiv.createEl("button"); btn.textContent = s || "Tous"
      const ref = () => { btn.style.cssText = activeStatut === s ? S_PILL_A("#fe640b") : S_PILL_I }
      btn.onclick = () => { activeStatut = s; refs.forEach(r => r()); renderResults(); updateFilterBtn() }
      ref(); refs.push(ref)
    }
  } else { activeStatut = "" }

  // ── Période ───────────────────────────────────────────────────────────
  const perRow = dynDiv.createDiv()
  perRow.style.cssText = S_ROW + "background:rgba(136,120,195,0.05);border:1px solid rgba(136,120,195,0.12);"
  perRow.createEl("span",{attr:{style:S_LABEL}}).textContent = "Période"
  const perDiv = perRow.createDiv(); perDiv.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;"
  const PERS = [{k:"",l:"Tout"},{k:"today",l:"Aujourd'hui"},{k:"week",l:"7 jours"},{k:"month",l:"30 jours"}]
  const perRefs = []
  for (const per of PERS) {
    const btn = perDiv.createEl("button"); btn.textContent = per.l
    const ref = () => { btn.style.cssText = activePeriode === per.k ? S_PILL_A("#8878c3") : S_PILL_I }
    btn.onclick = () => { activePeriode = per.k; perRefs.forEach(r => r()); renderResults(); updateFilterBtn() }
    ref(); perRefs.push(ref)
  }

  // ── Note ──────────────────────────────────────────────────────────────
  const hasNote = dp.some(p => p.note != null && !isNaN(Number(p.note)))
  if (hasNote) {
    const noteRow = dynDiv.createDiv()
    noteRow.style.cssText = S_ROW + "background:rgba(196,148,58,0.05);border:1px solid rgba(196,148,58,0.12);"
    noteRow.createEl("span",{attr:{style:S_LABEL}}).textContent = "Note"
    const nDiv = noteRow.createDiv(); nDiv.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;"
    const nRefs = []
    for (const n of NOTE_OPTS) {
      const btn = nDiv.createEl("button"); btn.textContent = n.l
      const ref = () => { btn.style.cssText = activeNote === n.v ? S_PILL_A("#c4943a") : S_PILL_I }
      btn.onclick = () => { activeNote = n.v; nRefs.forEach(r => r()); renderResults(); updateFilterBtn() }
      ref(); nRefs.push(ref)
    }
  } else { activeNote = 0 }

  // ── Tags ──────────────────────────────────────────────────────────────
  const allTags = [...new Set(dp.flatMap(getPageTags))].sort()
  if (allTags.length > 0) {
    if (!allTags.includes(activeTag)) activeTag = ""
    const tagRow = dynDiv.createDiv()
    tagRow.style.cssText = S_ROW + "background:rgba(78,138,90,0.05);border:1px solid rgba(78,138,90,0.12);"
    tagRow.createEl("span",{attr:{style:S_LABEL}}).textContent = "Tag"
    const tagSel = tagRow.createEl("select",{attr:{style:S_SEL}})
    tagSel.createEl("option",{attr:{value:""}}).textContent = "Tous les tags"
    for (const t of allTags) { const o = tagSel.createEl("option",{attr:{value:t}}); o.textContent = "#" + t }
    tagSel.value = activeTag
    tagSel.onchange = () => { activeTag = tagSel.value; renderResults(); updateFilterBtn() }
  } else { activeTag = "" }

  // ── Réinitialiser ─────────────────────────────────────────────────────
  if (countActiveFilters() > 0) {
    const resetRow = dynDiv.createDiv()
    resetRow.style.cssText = "display:flex;justify-content:flex-end;margin-top:6px;padding-top:6px;border-top:1px solid var(--background-modifier-border);"
    const resetBtn = resetRow.createEl("button")
    resetBtn.textContent = "✕ Réinitialiser les filtres"
    resetBtn.style.cssText = "background:none;border:none;cursor:pointer;font-size:0.8em;color:var(--text-muted);font-family:inherit;padding:2px 4px;text-decoration:underline;"
    resetBtn.onmouseenter = () => resetBtn.style.color = "var(--text-normal)"
    resetBtn.onmouseleave = () => resetBtn.style.color = "var(--text-muted)"
    resetBtn.onclick = () => {
      activeDomain = "tout"; activeStatut = ""; activePeriode = ""
      activeNote = 0; activeTag = ""
      renderFilters(); renderResults(); updateFilterBtn()
    }
  }
}

// ── Rendu des résultats (dispatch selon mode) ─────────────────────────────
const renderResults = () => {
  let pages = applyFilters(getDomainPages())

  // ── Mode TITRE : filtre synchrone sur nom / titre / tags ──────────────
  if (activeSearchMode === "titre") {
    if (activeSearch) pages = pages.filter(p =>
      p.file.name.toLowerCase().includes(activeSearch) ||
      (p.titre && String(p.titre).toLowerCase().includes(activeSearch)) ||
      getPageTags(p).some(t => t.toLowerCase().includes(activeSearch))
    )
    renderTable(pages)
    return
  }

  // ── Mode CONTENU : lecture asynchrone de chaque fichier ───────────────
  if (!activeSearch) {
    // Pas de requête → affichage normal sans filtre contenu
    renderTable(pages)
    return
  }

  const sid = ++_searchId
  contentDiv.empty()
  countEl.textContent = "🔍 Recherche dans le contenu des notes…"
  const loader = contentDiv.createEl("div")
  loader.style.cssText = "padding:20px 0;color:var(--text-muted);font-size:0.88em;text-align:center;"
  loader.textContent = "Analyse en cours…";

  (async () => {
    const matched = []
    const q = activeSearch
    for (const p of pages) {
      if (sid !== _searchId) return  // requête annulée
      try {
        const tfile = app.vault.getAbstractFileByPath(p.file.path)
        if (!tfile) continue
        const raw = await app.vault.read(tfile)
        if (raw.toLowerCase().includes(q)) matched.push(p)
      } catch(e) {}
    }
    if (sid !== _searchId) return
    renderTable(matched)
  })()
}

// ── Init ──────────────────────────────────────────────────────────────────
updateFilterBtn()
renderFilters()
renderResults()
```
