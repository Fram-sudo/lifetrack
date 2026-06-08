---
type: moc
tags: [moc, commandes]
cssclasses: [dashboard]
obsidianUIMode: preview
---

# 🛒 Commandes

```dataviewjs
const { Notice } = require('obsidian')

// ── mkDatePicker ──────────────────────────────────────────────────────────
const mkDatePicker = (parent, initVal, onChange, placeholder) => {
  placeholder = placeholder || "Choisir une date"
  const MFR = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
  const DFR = ["Lu","Ma","Me","Je","Ve","Sa","Di"]
  let sel = initVal || ""
  const fmt = iso => { if (!iso) return placeholder; const [y,m,d] = iso.split("-"); return `${d}/${m}/${y}` }
  const wrap = parent.createEl("div")
  const btn = wrap.createEl("button", {attr:{style:"display:flex;align-items:center;gap:8px;width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;cursor:pointer;text-align:left;"}})
  btn.createEl("span").textContent = "📅"
  const lbl = btn.createEl("span", {attr:{style:"flex:1;"}})
  lbl.style.color = sel ? "var(--text-normal)" : "var(--text-muted)"
  lbl.textContent = sel ? fmt(sel) : placeholder
  let cal = null
  btn.onclick = e => {
    e.stopPropagation()
    if (cal) { cal.remove(); cal = null; return }
    const sd = sel ? new Date(sel + "T00:00:00") : new Date()
    let vY = sd.getFullYear(), vM = sd.getMonth()
    cal = document.body.createEl("div", {attr:{style:"position:fixed;z-index:10000;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.25);padding:14px;width:240px;"}})
    const rect = btn.getBoundingClientRect()
    cal.style.left = Math.min(rect.left, window.innerWidth - 256) + "px"
    if (window.innerHeight - rect.bottom > 270) { cal.style.top = (rect.bottom + 6) + "px" }
    else { cal.style.top = (rect.top - 6) + "px"; cal.style.transform = "translateY(-100%)" }
    const todayStr = new Date().toISOString().slice(0, 10)
    const render = () => {
      cal.empty()
      const hdr = cal.createEl("div", {attr:{style:"display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;"}})
      const pb = hdr.createEl("button", {attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
      pb.textContent = "‹"; pb.onclick = e2 => { e2.stopPropagation(); vM--; if (vM<0){vM=11;vY--}; render() }
      hdr.createEl("span", {attr:{style:"font-weight:700;font-size:0.88em;"}}).textContent = MFR[vM] + " " + vY
      const nb = hdr.createEl("button", {attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
      nb.textContent = "›"; nb.onclick = e2 => { e2.stopPropagation(); vM++; if (vM>11){vM=0;vY++}; render() }
      const dh = cal.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:4px;"}})
      DFR.forEach(d => { const c = dh.createEl("div", {attr:{style:"text-align:center;font-size:0.68em;color:var(--text-muted);font-weight:600;padding:2px 0;"}}); c.textContent = d })
      const g = cal.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:3px;"}})
      const firstDow = (new Date(vY, vM, 1).getDay() + 6) % 7
      const dim = new Date(vY, vM+1, 0).getDate()
      for (let i=0; i<firstDow; i++) g.createEl("div")
      for (let day=1; day<=dim; day++) {
        const iso = `${vY}-${String(vM+1).padStart(2,"0")}-${String(day).padStart(2,"0")}`
        const isS = iso===sel, isT = iso===todayStr
        const c = g.createEl("div", {attr:{style:"text-align:center;padding:5px 2px;border-radius:6px;cursor:pointer;font-size:0.84em;line-height:1;" + (isS ? "background:var(--interactive-accent);color:#fff;font-weight:700;" : isT ? "border:1.5px solid var(--interactive-accent);color:var(--interactive-accent);font-weight:600;" : "")}})
        c.textContent = day
        if (!isS) { c.onmouseenter = () => { c.style.background="var(--background-secondary)" }; c.onmouseleave = () => { c.style.background="" } }
        c.onclick = e2 => { e2.stopPropagation(); sel=iso; lbl.textContent=fmt(iso); lbl.style.color="var(--text-normal)"; if(onChange)onChange(iso); cal.remove(); cal=null; if(hdlr) document.removeEventListener("click",hdlr,true) }
      }
    }
    render()
    let hdlr; hdlr = e2 => { if(cal && !cal.contains(e2.target) && e2.target!==btn){cal.remove();cal=null;document.removeEventListener("click",hdlr,true)} }
    setTimeout(() => document.addEventListener("click", hdlr, true), 10)
  }
  return { getValue: () => sel }
}

// ── Helpers ───────────────────────────────────────────────────────────────
const getDateStr = val => {
  if (!val) return ""
  if (typeof val === "string") return val.slice(0, 10)
  if (val.toFormat) return val.toFormat("yyyy-MM-dd")
  return String(val).slice(0, 10)
}

const fmtDate = iso => {
  if (!iso) return "-"
  const s = String(iso).slice(0, 10)
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/)
  return m ? `${m[3]}/${m[2]}/${m[1]}` : s
}

const CMD_COLORS = {
  "commandé": { bg:"rgba(254,100,11,0.15)",  color:"#fe640b",  label:"🛒 Commandé" },
  "expédié":  { bg:"rgba(30,102,245,0.15)",  color:"#1e66f5",  label:"📦 Expédié"  },
  "livré":    { bg:"rgba(64,160,43,0.15)",   color:"#40a02b",  label:"✅ Livré"    },
  "annulé":   { bg:"rgba(122,118,110,0.15)", color:"#7a766e",  label:"❌ Annulé"   },
}

const FIELD = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;"
const LABEL = "font-size:0.75em;color:var(--text-muted);font-weight:600;letter-spacing:0.04em;text-transform:uppercase;display:block;margin-bottom:4px;"
const BTN_S = "padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"
const BTN_G = "padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.88em;font-family:inherit;"

// Ligne 1 Statut : pills colorées par statut
const PILL_BASE = "padding:5px 14px;border-radius:20px;border:none;cursor:pointer;font-size:0.84em;font-weight:600;font-family:inherit;transition:opacity 0.1s;"
const PILL_COLORS = {
  "Tout":     { active:"background:#4c4f69;color:#fff;",               inactive:"background:rgba(76,79,105,0.12);color:#6c6f85;border:1px solid rgba(76,79,105,0.2);" },
  "Commandé": { active:"background:#fe640b;color:#fff;border:none;",   inactive:"background:rgba(254,100,11,0.12);color:#fe640b;border:1px solid rgba(254,100,11,0.3);" },
  "Expédié":  { active:"background:#1e66f5;color:#fff;border:none;",   inactive:"background:rgba(30,102,245,0.12);color:#1e66f5;border:1px solid rgba(30,102,245,0.3);" },
  "Livré":    { active:"background:#40a02b;color:#fff;border:none;",   inactive:"background:rgba(64,160,43,0.12);color:#40a02b;border:1px solid rgba(64,160,43,0.3);" },
  "Annulé":   { active:"background:#7a766e;color:#fff;border:none;",   inactive:"background:rgba(122,118,110,0.12);color:#7a766e;border:1px solid rgba(122,118,110,0.3);" },
}

// Ligne 2 Année : segment control
const TAB_YEAR_A = "padding:5px 14px;border-radius:7px;border:2px solid var(--text-normal);background:var(--text-normal);color:var(--background-primary);cursor:pointer;font-size:0.84em;font-weight:700;font-family:inherit;"
const TAB_YEAR_I = "padding:5px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;"

// Ligne 3 Mois & Site
const SEL_S = "padding:5px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.84em;font-family:inherit;cursor:pointer;"
const SEL_LABEL = "font-size:0.78em;font-weight:600;color:var(--text-muted);white-space:nowrap;"

// ── Données ───────────────────────────────────────────────────────────────
const allPages = dv.pages('"2 - Domaines/Commandes"')
  .where(p => p.type === "commande")
  .sort(p => p.date_commande, "desc")
  .array()

const currentYear = String(new Date().getFullYear())
const dataYears = [...new Set(
  allPages.map(p => getDateStr(p.date_commande).slice(0, 4)).filter(y => /^\d{4}$/.test(y))
)]
const years = [...new Set([currentYear, ...dataYears])].sort((a, b) => Number(b) - Number(a))
const sites = [...new Set(allPages.map(p => p.site).filter(Boolean))].sort()
const MOIS_LABELS = ["Tous les mois","Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

// ── État des filtres ──────────────────────────────────────────────────────
let activeStatut = "Tout"
let activeYear   = "Toutes"
let activeMois   = ""
let activeSite   = ""
let activeSearch = ""

// ── DOM principal ─────────────────────────────────────────────────────────
const wrap = dv.container.createDiv()

// ── Stats bar dynamique ───────────────────────────────────────────────────
const bar = wrap.createDiv()
bar.style.cssText = "display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--background-modifier-border);margin:10px 0 24px;font-size:0.85em;"

const STAT_CELLS = [
  { key:"total",    label:"total",    bg:"rgba(91,141,184,0.10)",  color:"#5b8db8" },
  { key:"commandé", label:"commandé", bg:"rgba(254,100,11,0.10)",  color:"#fe640b" },
  { key:"expédié",  label:"expédié",  bg:"rgba(30,102,245,0.10)",  color:"#1e66f5" },
  { key:"livré",    label:"livré",    bg:"rgba(64,160,43,0.10)",   color:"#40a02b" },
  { key:"dépensé",  label:"dépensé",  bg:"rgba(136,120,195,0.10)", color:"#8878c3" },
]

// Créer les cellules et garder une référence vers l'élément valeur de chacune
const statValEls = {}
for (const c of STAT_CELLS) {
  const cell = bar.createDiv()
  cell.style.cssText = `flex:1;padding:12px 8px;background:${c.bg};text-align:center;border-right:1px solid var(--background-modifier-border);`
  const val = cell.createDiv()
  val.style.cssText = `font-size:1.4em;font-weight:800;color:${c.color};line-height:1;margin-bottom:4px;`
  val.textContent = "-"
  const lbl = cell.createDiv()
  lbl.style.cssText = "font-size:0.78em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;"
  lbl.textContent = c.label
  statValEls[c.key] = val
}
bar.lastChild.style.borderRight = "none"

const ROW_WRAP = "display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 12px;border-radius:8px;margin-bottom:6px;"

// ── Barre de recherche ────────────────────────────────────────────────────
const searchInput = wrap.createEl("input")
searchInput.type = "search"
searchInput.placeholder = "🔍 Rechercher une commande…"
searchInput.style.cssText = "width:100%;padding:8px 13px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;margin-bottom:8px;font-family:inherit;outline:none;"
searchInput.oninput = () => { activeSearch = searchInput.value.toLowerCase().trim(); renderTable() }

// ── Ligne 1 : Statut ──────────────────────────────────────────────────────
const statusRow = wrap.createDiv()
statusRow.style.cssText = ROW_WRAP + "background:rgba(136,57,239,0.04);border:1px solid rgba(136,57,239,0.12);"
const statusLabel = statusRow.createEl("span")
statusLabel.textContent = "Statut"
statusLabel.style.cssText = SEL_LABEL + "margin-right:4px;min-width:38px;"
const statusBar = statusRow.createDiv()
statusBar.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;"

// ── Ligne 2 : Année ───────────────────────────────────────────────────────
const yearRow = wrap.createDiv()
yearRow.style.cssText = ROW_WRAP + "background:rgba(76,79,105,0.04);border:1px solid rgba(76,79,105,0.12);"
const yearLabel = yearRow.createEl("span")
yearLabel.textContent = "Année"
yearLabel.style.cssText = SEL_LABEL + "margin-right:4px;min-width:38px;"
const yearBar = yearRow.createDiv()
yearBar.style.cssText = "display:flex;gap:4px;flex-wrap:wrap;"

// ── Ligne 3 : Mois & Site ─────────────────────────────────────────────────
const filterRow = wrap.createDiv()
filterRow.style.cssText = ROW_WRAP + "background:rgba(30,102,245,0.04);border:1px solid rgba(30,102,245,0.12);gap:14px;"

const moisGrp = filterRow.createDiv()
moisGrp.style.cssText = "display:flex;align-items:center;gap:6px;"
moisGrp.createEl("span", {attr:{style:SEL_LABEL}}).textContent = "📅 Mois"
const moisSel = moisGrp.createEl("select", {attr:{style:SEL_S}})
MOIS_LABELS.forEach((m, i) => {
  const opt = moisSel.createEl("option", {attr:{value: i === 0 ? "" : String(i).padStart(2, "0")}})
  opt.textContent = m
})
moisSel.onchange = () => { activeMois = moisSel.value; renderTable() }

const siteGrp = filterRow.createDiv()
siteGrp.style.cssText = "display:flex;align-items:center;gap:6px;"
siteGrp.createEl("span", {attr:{style:SEL_LABEL}}).textContent = "🏪 Site"
const siteSel = siteGrp.createEl("select", {attr:{style:SEL_S}})
siteSel.createEl("option", {attr:{value:""}}).textContent = "Tous"
for (const s of sites) {
  siteSel.createEl("option", {attr:{value:s}}).textContent = s
}
siteSel.onchange = () => { activeSite = siteSel.value; renderTable() }

// Tableau
const tableWrapper = wrap.createDiv()

// ── Rendu de la table + mise à jour des stats ─────────────────────────────
const renderTable = () => {
  tableWrapper.empty()

  const filtered = allPages.filter(p => {
    if (activeSearch && !p.file.name.toLowerCase().includes(activeSearch)) return false
    if (activeStatut !== "Tout" && (p.statut || "").toLowerCase() !== activeStatut.toLowerCase()) return false
    const d = getDateStr(p.date_commande)
    if (activeYear !== "Toutes" && !d.startsWith(activeYear)) return false
    if (activeMois && d.slice(5, 7) !== activeMois) return false
    if (activeSite && (p.site || "") !== activeSite) return false
    return true
  })

  // ── Mise à jour des stats selon le filtrage actuel ────────────────────
  let totalMontant = 0
  for (const p of filtered) if (p.montant) totalMontant += parseFloat(p.montant) || 0
  statValEls["total"].textContent    = String(filtered.length)
  statValEls["commandé"].textContent = String(filtered.filter(p => p.statut === "commandé").length)
  statValEls["expédié"].textContent  = String(filtered.filter(p => p.statut === "expédié").length)
  statValEls["livré"].textContent    = String(filtered.filter(p => p.statut === "livré").length)
  statValEls["dépensé"].textContent  = totalMontant > 0 ? totalMontant.toFixed(2) + " €" : "-"

  if (filtered.length === 0) {
    tableWrapper.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;margin:4px 0;"}}).textContent = "Aucune commande pour ces filtres."
    return
  }

  const table = tableWrapper.createEl("table", {attr:{style:"width:100%;border-collapse:collapse;font-size:0.87em;"}})
  const hrow = table.createEl("thead").createEl("tr")
  for (const h of ["Commande","Site","Statut","Commandé le","Livraison","Montant",""]) {
    const th = hrow.createEl("th")
    th.style.cssText = "text-align:left;padding:6px 10px;font-size:0.78em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:1px solid var(--background-modifier-border);"
    if (h === "") th.style.width = "40px"
    th.textContent = h
  }

  const tbody = table.createEl("tbody")
  for (const p of filtered) {
    const tr = tbody.createEl("tr")
    tr.onmouseenter = () => tr.style.background = "var(--background-secondary)"
    tr.onmouseleave = () => tr.style.background = ""
    const TD = "padding:8px 10px;border-bottom:1px solid var(--background-modifier-border);vertical-align:middle;"

    // Nom (cliquable → ouvrir la note)
    const tdNom = tr.createEl("td", {attr:{style:TD + "font-weight:600;cursor:pointer;"}})
    tdNom.textContent = p.file.name
    tdNom.onclick = () => app.workspace.openLinkText(p.file.path, "", false)

    // Site
    tr.createEl("td", {attr:{style:TD + "color:var(--text-muted);"}}).textContent = p.site || "-"

    // Statut badge
    const tdSt = tr.createEl("td", {attr:{style:TD}})
    const sc = CMD_COLORS[(p.statut || "").toLowerCase()]
    if (sc) {
      const badge = tdSt.createEl("span")
      badge.style.cssText = `background:${sc.bg};color:${sc.color};padding:2px 8px;border-radius:10px;font-size:0.8em;font-weight:700;white-space:nowrap;`
      badge.textContent = sc.label
    } else { tdSt.textContent = p.statut || "-" }

    // Dates
    tr.createEl("td", {attr:{style:TD + "color:var(--text-muted);font-size:0.85em;white-space:nowrap;"}}).textContent = fmtDate(getDateStr(p.date_commande))
    tr.createEl("td", {attr:{style:TD + "color:var(--text-muted);font-size:0.85em;white-space:nowrap;"}}).textContent = fmtDate(getDateStr(p["date_livraison_estimée"]))

    // Montant
    const tdM = tr.createEl("td", {attr:{style:TD + "text-align:right;font-weight:600;white-space:nowrap;"}})
    tdM.textContent = p.montant ? parseFloat(p.montant).toFixed(2) + " €" : "-"

    // Boutons actions (éditer + supprimer)
    const tdE = tr.createEl("td", {attr:{style:TD + "text-align:center;white-space:nowrap;"}})
    const editBtn = tdE.createEl("button", {attr:{style:"background:none;border:1px solid var(--background-modifier-border);border-radius:6px;cursor:pointer;color:var(--text-muted);font-size:0.82em;padding:3px 8px;font-family:inherit;line-height:1;"}})
    editBtn.textContent = "✏"
    editBtn.title = "Modifier"
    editBtn.addEventListener("click", e => { e.stopPropagation(); openEditModal(p) })
    const delBtn = tdE.createEl("button", {attr:{style:"background:none;border:1px solid rgba(210,15,57,0.3);border-radius:6px;cursor:pointer;color:#d20f39;font-size:0.82em;padding:3px 8px;font-family:inherit;line-height:1;margin-left:5px;"}})
    delBtn.textContent = "🗑"
    delBtn.title = "Supprimer"
    let delConfirm = false
    delBtn.onclick = async e => {
      e.stopPropagation()
      if (!delConfirm) {
        delConfirm = true
        delBtn.textContent = "✓?"
        delBtn.style.background = "rgba(210,15,57,0.12)"
        delBtn.title = "Cliquer à nouveau pour confirmer"
        setTimeout(() => {
          if (delConfirm) { delConfirm = false; delBtn.textContent = "🗑"; delBtn.style.background = "none"; delBtn.title = "Supprimer" }
        }, 3000)
      } else {
        const file = app.vault.getAbstractFileByPath(p.file.path)
        if (file) { await app.vault.trash(file, true); new Notice("Commande supprimée.", 2000) }
      }
    }
  }
}

// ── Modale d'édition ──────────────────────────────────────────────────────
const openEditModal = (p) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:360px;max-width:500px;width:92%;max-height:88vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,0.35);display:flex;flex-direction:column;gap:11px;"}})

  box.createEl("h3", {attr:{style:"margin:0;font-size:1em;font-weight:700;"}}).textContent = "Modifier la commande"

  const mkGrp = (label) => {
    const g = box.createEl("div")
    g.createEl("label", {attr:{style:LABEL}}).textContent = label
    return g
  }

  const g1 = mkGrp("Nom de la commande")
  const nomInp = g1.createEl("input", {attr:{type:"text", value: p.file.name, style:FIELD}})

  const g2 = mkGrp("Site / Vendeur")
  const siteInp = g2.createEl("input", {attr:{type:"text", value: p.site || "", style:FIELD, placeholder:"Ex: Amazon, Uniqlo…"}})

  const g3 = mkGrp("Statut")
  const statutSel = g3.createEl("select", {attr:{style:FIELD}})
  for (const s of ["commandé","expédié","livré","annulé"]) {
    const opt = statutSel.createEl("option", {attr:{value:s}})
    opt.textContent = s.charAt(0).toUpperCase() + s.slice(1)
    if ((p.statut || "").toLowerCase() === s) opt.selected = true
  }

  const g4 = mkGrp("Commande passée le")
  const cmdPicker = mkDatePicker(g4, getDateStr(p.date_commande), null)

  const g5 = mkGrp("Livraison estimée")
  const livPicker = mkDatePicker(g5, getDateStr(p["date_livraison_estimée"]), null)

  const g6 = mkGrp("N° de commande")
  const numInp = g6.createEl("input", {attr:{type:"text", value: p["numéro_commande"] || "", style:FIELD, placeholder:"Optionnel"}})

  const g7 = mkGrp("Montant total (€)")
  const montantInp = g7.createEl("input", {attr:{type:"number", step:"0.01", min:"0", value: p.montant || "", style:FIELD, placeholder:"Ex: 49.90"}})

  box.createEl("p", {attr:{style:"margin:0;font-size:0.78em;color:var(--text-muted);font-style:italic;border-top:1px solid var(--background-modifier-border);padding-top:10px;"}}).textContent = "Pour modifier les articles, ouvre la note directement (Ctrl+E)."

  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:4px;"}})
  const cancelBtn = btns.createEl("button", {attr:{style:BTN_G}}); cancelBtn.textContent = "Annuler"
  cancelBtn.onclick = () => overlay.remove()
  const okBtn = btns.createEl("button", {attr:{style:BTN_S}}); okBtn.textContent = "Enregistrer"

  okBtn.onclick = async () => {
    try {
      const newNom = nomInp.value.trim()
      if (!newNom) { nomInp.style.borderColor = "red"; return }

      // Capture all values BEFORE removing the overlay
      const newSite    = siteInp.value.trim()
      const newStatut  = statutSel.value
      const newDateCmd = cmdPicker.getValue()
      const newDateLiv = livPicker.getValue()
      const newNum     = numInp.value.trim()
      const newMontant = montantInp.value

      overlay.remove()

      const sanitize = s => s.replace(/[\\/:*?"<>|]/g, "-").trim()
      const parentPath = p.file.folder   // p.file.folder est le chemin du dossier en Dataview
      let targetPath = p.file.path

      if (newNom !== p.file.name) {
        const file = app.vault.getAbstractFileByPath(p.file.path)
        if (file) {
          const newPath = parentPath + "/" + sanitize(newNom) + ".md"
          try {
            await app.fileManager.renameFile(file, newPath)
            targetPath = newPath
          } catch(e) {
            new Notice("Erreur renommage : " + e.message, 4000)
            return
          }
        }
      }

      const targetFile = app.vault.getAbstractFileByPath(targetPath)
      if (targetFile) {
        await app.fileManager.processFrontMatter(targetFile, fm => {
          fm.site = newSite
          fm.statut = newStatut
          fm.date_commande = newDateCmd
          fm["date_livraison_estimée"] = newDateLiv
          fm["numéro_commande"] = newNum
          const m = parseFloat(newMontant)
          fm.montant = (!isNaN(m) && m > 0) ? parseFloat(m.toFixed(2)) : ""
        })
        new Notice("Commande mise à jour.", 2000)
      } else {
        new Notice("Erreur : fichier introuvable.", 3000)
      }
    } catch(err) {
      new Notice("Erreur : " + err.message, 5000)
    }
  }

  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Escape") overlay.remove() }
  setTimeout(() => nomInp.focus(), 50)
}

// ── Onglets Statut ────────────────────────────────────────────────────────
const statusRefs = []
const STATUS_LABELS = { "Tout":"Tout", "Commandé":"🛒 Commandé", "Expédié":"📦 Expédié", "Livré":"✅ Livré", "Annulé":"❌ Annulé" }
for (const t of ["Tout","Commandé","Expédié","Livré","Annulé"]) {
  const btn = statusBar.createEl("button")
  btn.textContent = STATUS_LABELS[t]
  const pc = PILL_COLORS[t]
  const ref = () => {
    const s = activeStatut === t ? pc.active : pc.inactive
    btn.style.cssText = PILL_BASE + s
  }
  btn.onclick = () => { activeStatut = t; statusRefs.forEach(r => r()); renderTable() }
  ref(); statusRefs.push(ref)
}

// ── Onglets Année ─────────────────────────────────────────────────────────
const yearRefs = []
for (const y of ["Toutes", ...years]) {
  const btn = yearBar.createEl("button")
  btn.textContent = y
  const ref = () => { btn.style.cssText = activeYear === y ? TAB_YEAR_A : TAB_YEAR_I }
  btn.onclick = () => { activeYear = y; yearRefs.forEach(r => r()); renderTable() }
  ref(); yearRefs.push(ref)
}

renderTable()
```
