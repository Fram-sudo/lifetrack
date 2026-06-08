---
type: moc
tags: [moc, stats]
cssclasses: [media-page]
obsidianUIMode: preview
---

# 📊 Statistiques Médias

```dataviewjs
// ═══════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════
const parseH = h => {
  const s = String(h || "")
  if (s.includes(":")) { const [hh,mm] = s.split(":").map(Number); return (hh||0)+(mm||0)/60 }
  return parseFloat(s) || 0
}
const fmtH = h => {
  const hh = Math.floor(h||0), mm = Math.round(((h||0)-hh)*60)
  return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h`
}
const toJSDate = d => {
  if (!d) return null
  if (d instanceof Date) return d
  if (d?.toJSDate) return d.toJSDate()
  if (typeof d === "string" || typeof d === "number") { const r = new Date(d); return isNaN(r) ? null : r }
  return null
}
const dateStr = d => {
  const j = toJSDate(d); if (!j) return null
  const y=j.getFullYear(), m=String(j.getMonth()+1).padStart(2,"0"), day=String(j.getDate()).padStart(2,"0")
  return `${y}-${m}-${day}`
}
const fmtDateFr = d => {
  const j = toJSDate(d); if (!j) return "-"
  return j.toLocaleDateString("fr-FR", { day:"numeric", month:"short", year:"numeric" })
}
const hexRgb = hex => {
  const h = hex.replace("#","")
  return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)].join(",")
}

// ═══════════════════════════════════════════════════════════════
// DATE UTILS
// ═══════════════════════════════════════════════════════════════
const now = new Date()
const todayStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}-${String(now.getDate()).padStart(2,"0")}`
const MONTHS_FR = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

const getWeekStart = () => {
  const d = new Date(now); const dow = d.getDay()
  d.setDate(d.getDate() - (dow === 0 ? 6 : dow - 1)); d.setHours(0,0,0,0); return d
}
const isInPeriod = (ds, period) => {
  if (!ds) return false
  const d = new Date(ds); if (isNaN(d)) return false
  switch (period) {
    case "today": return ds === todayStr
    case "week": { const ws = getWeekStart(), we = new Date(ws); we.setDate(ws.getDate()+6); we.setHours(23,59,59,999); return d >= ws && d <= we }
    case "month": return d.getFullYear()===now.getFullYear() && d.getMonth()===now.getMonth()
    case "year":  return d.getFullYear()===now.getFullYear()
    case "range": {
      const from = st.rangeFrom ? new Date(st.rangeFrom) : null
      const to   = st.rangeTo   ? new Date(st.rangeTo)   : null
      if (from) from.setHours(0,0,0,0)
      if (to)   to.setHours(23,59,59,999)
      if (from && d < from) return false
      if (to   && d > to)   return false
      return true
    }
    default: return true
  }
}

// ═══════════════════════════════════════════════════════════════
// TYPE CONFIG
// ═══════════════════════════════════════════════════════════════
const TYPE_CFG = {
  "animé":  { icon:"🎌", label:"Animé",         color:"#e07b5a", unit:(n)=>`${n} ép.`,    unitLong:"épisodes"  },
  "film":   { icon:"🎬", label:"Film",           color:"#c4943a", unit:(n)=>`${n} film`,   unitLong:"films vus" },
  "série":  { icon:"📺", label:"Série TV",       color:"#df8e1d", unit:(n)=>`${n} ép.`,    unitLong:"épisodes" },
  "jeu":    { icon:"🎮", label:"Jeu vidéo",      color:"#4a8fa8", unit:(n)=>fmtH(n),       unitLong:"heures jouées" },
  "manga":  { icon:"📖", label:"Manga",          color:"#8878c3", unit:(n)=>`${n} ch.`,    unitLong:"chapitres" },
  "manwha": { icon:"📗", label:"Manwha",         color:"#5f8dd3", unit:(n)=>`${n} ch.`,    unitLong:"chapitres" },
  "manhua": { icon:"📘", label:"Manhua",         color:"#6a9fd8", unit:(n)=>`${n} ch.`,    unitLong:"chapitres" },
  "livre":  { icon:"📚", label:"Roman & Livre",  color:"#4e8a5a", unit:(n)=>`${n} ch.`,    unitLong:"chapitres" },
}

// ═══════════════════════════════════════════════════════════════
// DATA LOADING + SESSION NORMALISATION
// ═══════════════════════════════════════════════════════════════
const allAnimes   = dv.pages('"2 - Domaines/Médias/Animés"').where(p=>p.type==="animé").array()
const allFilms    = dv.pages('"2 - Domaines/Médias/Films"').where(p=>p.type==="film").array()
const allJeux     = dv.pages('"2 - Domaines/Médias/Jeux Vidéo"').where(p=>p.type==="jeu").array()
const allSeries   = dv.pages('"2 - Domaines/Médias/Séries"').where(p=>p.type==="série").array()
const allLectures = dv.pages('"2 - Domaines/Médias/Manga & Manwha"')
  .where(p=>["manga","manwha","manhua","livre"].includes(p.type)).array()
const allMedia    = [...allAnimes, ...allFilms, ...allJeux, ...allSeries, ...allLectures]

// Flat normalised sessions list (one entry per session)
const allSessions = []
for (const p of allAnimes) {
  for (const s of (Array.isArray(p.sessions)?p.sessions:[])) {
    const ds = dateStr(s?.date); if (!ds) continue
    const eps = (s.ep_fin!=null && s.ep_debut!=null) ? s.ep_fin - s.ep_debut + 1 : 1
    allSessions.push({ date:ds, type:"animé", title:p.titre||p.file.name, page:p, metric:eps, label:`S${s.saison||"?"} Ép.${s.ep_debut}${s.ep_fin!==s.ep_debut?`→${s.ep_fin}`:""} (${eps} ép.)` })
  }
}
for (const p of allFilms) {
  const ds = dateStr(p.date_visionnage); if (!ds) continue
  allSessions.push({ date:ds, type:"film", title:p.titre||p.file.name, page:p, metric:1, label:`Visionné le ${fmtDateFr(p.date_visionnage)}` })
}
for (const p of allSeries) {
  for (const s of (Array.isArray(p.sessions)?p.sessions:[])) {
    const ds = dateStr(s?.date); if (!ds) continue
    const eps = (s.ep_fin!=null && s.ep_debut!=null) ? s.ep_fin - s.ep_debut + 1 : 1
    allSessions.push({ date:ds, type:"série", title:p.titre||p.file.name, page:p, metric:eps, label:`S${s.saison||"?"} Ép.${s.ep_debut}${s.ep_fin!==s.ep_debut?`→${s.ep_fin}`:""} (${eps} ép.)` })
  }
}
for (const p of allJeux) {
  for (const s of (Array.isArray(p.sessions)?p.sessions:[])) {
    const ds = dateStr(s?.date); if (!ds) continue
    const h = parseH(s.h)
    allSessions.push({ date:ds, type:"jeu", title:p.titre||p.file.name, page:p, metric:h, label:`${fmtH(h)} jouées` })
  }
}
for (const p of allLectures) {
  for (const s of (Array.isArray(p.sessions)?p.sessions:[])) {
    const ds = dateStr(s?.date); if (!ds) continue
    const chs = (s.ch_fin!=null && s.ch_debut!=null) ? s.ch_fin - s.ch_debut + 1 : 1
    allSessions.push({ date:ds, type:p.type, title:p.titre||p.file.name, page:p, metric:chs, label:`Ch.${s.ch_debut}${s.ch_fin!==s.ch_debut?`→${s.ch_fin}`:""} (${chs} ch.)` })
  }
}

// ═══════════════════════════════════════════════════════════════
// DATE PICKER (identique au MOC Commandes)
// ═══════════════════════════════════════════════════════════════
const mkDatePicker = (parent, initVal, onChange, placeholder) => {
  placeholder = placeholder || "Choisir une date"
  const MFR = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
  const DFR = ["Lu","Ma","Me","Je","Ve","Sa","Di"]
  let sel = initVal || ""
  const fmt = iso => { if (!iso) return placeholder; const [y,m,d] = iso.split("-"); return `${d}/${m}/${y}` }
  const wrap = parent.createEl("div")
  const btn = wrap.createEl("button", {attr:{style:"display:flex;align-items:center;gap:8px;padding:7px 12px;border-radius:20px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.84em;box-sizing:border-box;font-family:inherit;cursor:pointer;text-align:left;white-space:nowrap;"}})
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
    const renderCal = () => {
      cal.empty()
      const hdr = cal.createEl("div", {attr:{style:"display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;"}})
      const pb = hdr.createEl("button", {attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
      pb.textContent = "‹"; pb.onclick = e2 => { e2.stopPropagation(); vM--; if (vM<0){vM=11;vY--}; renderCal() }
      hdr.createEl("span", {attr:{style:"font-weight:700;font-size:0.88em;"}}).textContent = MFR[vM] + " " + vY
      const nb = hdr.createEl("button", {attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
      nb.textContent = "›"; nb.onclick = e2 => { e2.stopPropagation(); vM++; if (vM>11){vM=0;vY++}; renderCal() }
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
    renderCal()
    let hdlr; hdlr = e2 => { if(cal && !cal.contains(e2.target) && e2.target!==btn){cal.remove();cal=null;document.removeEventListener("click",hdlr,true)} }
    setTimeout(() => document.addEventListener("click", hdlr, true), 10)
  }
  return { getValue: () => sel }
}

// ═══════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════
if (!window._statsMedia) window._statsMedia = { mode:"global", period:"month", search:"", selectedItem:null, browseType:"all", modalPeriod:"all", rangeFrom:"", rangeTo:"" }
const MONTHS_1L = ["J","F","M","A","M","J","J","A","S","O","N","D"]
const st = window._statsMedia

// ═══════════════════════════════════════════════════════════════
// ROOT
// ═══════════════════════════════════════════════════════════════
dv.container.style.cssText = "margin:0;padding:0;"
const root = dv.container.createDiv()

const render = () => {
  root.empty()
  renderControls()
  if (st.mode === "global") renderGlobal()
  else renderIndividual()
}

// ═══════════════════════════════════════════════════════════════
// CONTROLS (mode toggle + period selector)
// ═══════════════════════════════════════════════════════════════
const renderControls = () => {
  // Mode toggle
  const mw = root.createDiv()
  mw.style.cssText = "display:flex;gap:8px;margin-bottom:14px;align-items:center;flex-wrap:wrap;"
  for (const [key, icon, label] of [["global","🌍","Vue globale"],["individual","🔍","Vue individuelle"]]) {
    const btn = mw.createEl("button")
    const active = st.mode === key
    btn.style.cssText = `padding:6px 16px;border-radius:20px;border:1px solid ${active?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${active?"var(--interactive-accent)":"var(--background-secondary)"};color:${active?"var(--text-on-accent)":"var(--text-normal)"};cursor:pointer;font-size:0.85em;font-family:inherit;font-weight:${active?"700":"400"};transition:all 0.15s;`
    btn.textContent = `${icon} ${label}`
    btn.onclick = () => { st.mode = key; render() }
  }
  // Period selector (global view only)
  if (st.mode === "global") {
    const pw = root.createDiv()
    pw.style.cssText = "display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap;align-items:center;"
    for (const [key, label] of [["today","Aujourd'hui"],["week","Cette semaine"],["month","Ce mois"],["year","Cette année"],["all","Tout"]]) {
      const btn = pw.createEl("button")
      const active = st.period === key
      btn.style.cssText = `padding:5px 13px;border-radius:16px;border:1px solid ${active?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${active?"rgba(74,143,168,0.12)":"transparent"};color:${active?"var(--interactive-accent)":"var(--text-muted)"};cursor:pointer;font-size:0.82em;font-family:inherit;font-weight:${active?"700":"400"};`
      btn.textContent = label
      btn.onclick = () => { st.period = key; render() }
    }
    // Plage personnalisée
    const rangeBtn = pw.createEl("button")
    const rangeActive = st.period === "range"
    rangeBtn.style.cssText = `padding:5px 13px;border-radius:16px;border:1px solid ${rangeActive?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${rangeActive?"rgba(74,143,168,0.12)":"transparent"};color:${rangeActive?"var(--interactive-accent)":"var(--text-muted)"};cursor:pointer;font-size:0.82em;font-family:inherit;font-weight:${rangeActive?"700":"400"};`
    rangeBtn.textContent = "📅 Plage…"
    rangeBtn.onclick = () => { st.period = "range"; render() }

    // Pickers de date (visibles seulement si period === "range")
    if (st.period === "range") {
      const rangeRow = root.createDiv()
      rangeRow.style.cssText = "display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap;"
      const lbl1 = rangeRow.createEl("span"); lbl1.textContent = "Du"; lbl1.style.cssText = "font-size:0.82em;color:var(--text-muted);font-weight:500;"
      mkDatePicker(rangeRow, st.rangeFrom, v => { st.rangeFrom = v; render() }, "jj/mm/aaaa")
      const arrow = rangeRow.createEl("span"); arrow.textContent = "→"; arrow.style.cssText = "color:var(--text-muted);font-size:1em;"
      const lbl2 = rangeRow.createEl("span"); lbl2.textContent = "au"; lbl2.style.cssText = "font-size:0.82em;color:var(--text-muted);font-weight:500;"
      mkDatePicker(rangeRow, st.rangeTo, v => { st.rangeTo = v; render() }, "jj/mm/aaaa")
    } else {
      root.createDiv().style.cssText = "margin-bottom:14px;"
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// GLOBAL VIEW
// ═══════════════════════════════════════════════════════════════
const renderGlobal = () => {
  const filtered = allSessions.filter(s => isInPeriod(s.date, st.period))

  // Stat cards
  const eps     = filtered.filter(s=>s.type==="animé").reduce((a,s)=>a+s.metric,0)
  const seriesEps = filtered.filter(s=>s.type==="série").reduce((a,s)=>a+s.metric,0)
  const hours = filtered.filter(s=>s.type==="jeu").reduce((a,s)=>a+s.metric,0)
  const chs   = filtered.filter(s=>["manga","manwha","manhua","livre"].includes(s.type)).reduce((a,s)=>a+s.metric,0)
  const films = filtered.filter(s=>s.type==="film").length

  const grid = root.createDiv()
  grid.style.cssText = "display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:24px;"
  for (const [val, icon, color, label] of [
    [eps,                         "🎌", "#e07b5a", "ép. animés"],
    [seriesEps,                   "📺", "#df8e1d", "ép. séries"],
    [hours>0 ? fmtH(hours) : "0h","🎮", "#4a8fa8", "heures jouées"],
    [chs,                         "📖", "#8878c3", "chapitres lus"],
    [films,                       "🎬", "#c4943a", films>1?"films vus":"film vu"],
  ]) {
    const card = grid.createDiv()
    card.style.cssText = `background:rgba(${hexRgb(color)},0.08);border:1px solid var(--background-modifier-border);border-radius:12px;padding:14px 10px;text-align:center;`
    card.createDiv().innerHTML = `<div style="font-size:1.3em;margin-bottom:5px;">${icon}</div><div style="font-size:1.7em;font-weight:800;color:${color};line-height:1;margin-bottom:3px;">${val}</div><div style="font-size:0.72em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.04em;">${label}</div>`
  }

  renderBarChart(root, filtered)
  renderHeatmap(root)
  renderRecentActivity(root, filtered)
}

// ═══════════════════════════════════════════════════════════════
// BAR CHART (global)
// ═══════════════════════════════════════════════════════════════
const renderBarChart = (container, filtered) => {
  const wrap = container.createDiv()
  wrap.style.cssText = "margin-bottom:24px;"
  const ttl = wrap.createEl("h4")
  ttl.style.cssText = "margin:0 0 12px;font-size:0.8em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
  ttl.textContent = "📊 Activité par période"

  // Build buckets
  let buckets = []
  if (st.period === "today") {
    buckets = [{ label:"Aujourd'hui", value:filtered.reduce((a,s)=>a+1,0) }]
  } else if (st.period === "week") {
    const ws = getWeekStart()
    const days = ["Lun","Mar","Mer","Jeu","Ven","Sam","Dim"]
    buckets = Array.from({length:7},(_,i)=>{
      const d = new Date(ws); d.setDate(ws.getDate()+i)
      const ds = d.toISOString().split("T")[0]
      return { label:days[i], value:filtered.filter(s=>s.date===ds).length }
    })
  } else if (st.period === "month") {
    const dim = new Date(now.getFullYear(), now.getMonth()+1, 0).getDate()
    buckets = Array.from({length:dim},(_,i)=>{
      const ds = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}-${String(i+1).padStart(2,"0")}`
      const isToday = ds === todayStr
      return { label:String(i+1), value:filtered.filter(s=>s.date===ds).length, highlight:isToday }
    })
  } else if (st.period === "year") {
    buckets = MONTHS_FR.map((m,i)=>{
      return { label:m, value:allSessions.filter(s=>{ const d=new Date(s.date); return d.getFullYear()===now.getFullYear()&&d.getMonth()===i }).length }
    })
  } else if (st.period === "range" && (st.rangeFrom || st.rangeTo)) {
    const from = st.rangeFrom ? new Date(st.rangeFrom) : new Date(allSessions.reduce((a,s)=>s.date<a?s.date:a, todayStr))
    const to   = st.rangeTo   ? new Date(st.rangeTo)   : now
    const daysDiff = Math.round((to - from) / (1000*60*60*24))
    if (daysDiff < 56) {
      // Par jour
      const cur = new Date(from)
      while (cur <= to) {
        const ds = cur.toISOString().split("T")[0]
        buckets.push({ label:String(cur.getDate()), title:fmtDateFr(ds), value:filtered.filter(s=>s.date===ds).length, highlight:ds===todayStr })
        cur.setDate(cur.getDate()+1)
      }
    } else if (daysDiff <= 548) {
      // Par mois
      const cur = new Date(from.getFullYear(), from.getMonth(), 1)
      while (cur <= to) {
        const y = cur.getFullYear(), m = cur.getMonth()
        buckets.push({ label:MONTHS_1L[m], title:`${MONTHS_FR[m]} ${y}`, value:filtered.filter(s=>{ const d=new Date(s.date); return d.getFullYear()===y&&d.getMonth()===m }).length })
        cur.setMonth(cur.getMonth()+1)
      }
    } else {
      // Par trimestre
      const cur = new Date(from.getFullYear(), Math.floor(from.getMonth()/3)*3, 1)
      while (cur <= to) {
        const y = cur.getFullYear(), q = Math.floor(cur.getMonth()/3)
        buckets.push({ label:`Q${q+1}`, title:`Q${q+1} ${y}`, value:filtered.filter(s=>{ const d=new Date(s.date); return d.getFullYear()===y&&Math.floor(d.getMonth()/3)===q }).length })
        cur.setMonth(cur.getMonth()+3)
      }
    }
  } else {
    // all → last 12 months, single-letter labels
    buckets = Array.from({length:12},(_,i)=>{
      const d = new Date(now.getFullYear(), now.getMonth()-11+i, 1)
      return { label:MONTHS_FR[d.getMonth()], value:allSessions.filter(s=>{ const sd=new Date(s.date); return sd.getFullYear()===d.getFullYear()&&sd.getMonth()===d.getMonth() }).length, title:`${MONTHS_FR[d.getMonth()]} ${d.getFullYear()}` }
    })
  }

  const maxV = Math.max(...buckets.map(b=>b.value), 1)
  const box = wrap.createDiv()
  box.style.cssText = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:12px;padding:16px 14px 10px;"

  const useGlobalScroll = buckets.length > 35
  const barsOuter = useGlobalScroll ? box.createDiv() : box
  if (useGlobalScroll) barsOuter.style.cssText = "overflow-x:auto;padding-bottom:2px;"

  const barsEl = barsOuter.createDiv()
  barsEl.style.cssText = useGlobalScroll
    ? `display:flex;align-items:flex-end;justify-content:flex-start;gap:3px;height:180px;min-width:${buckets.length * 16}px;`
    : "display:flex;align-items:flex-end;justify-content:center;gap:4px;height:180px;"

  for (const b of buckets) {
    const col = barsEl.createDiv()
    col.style.cssText = useGlobalScroll
      ? "display:flex;flex-direction:column;align-items:center;flex:0 0 12px;gap:2px;position:relative;"
      : "display:flex;flex-direction:column;align-items:center;flex:1;min-width:0;max-width:48px;gap:3px;position:relative;"
    const inner = col.createDiv()
    inner.style.cssText = "width:100%;display:flex;align-items:flex-end;height:150px;"
    const bar = inner.createDiv()
    const pct = b.value > 0 ? Math.max(6, Math.round((b.value/maxV)*146)) : 2
    const barColor = b.highlight ? "#c4943a" : "var(--interactive-accent)"
    bar.style.cssText = `width:100%;height:${pct}px;background:${b.value>0?barColor:"var(--background-modifier-border)"};border-radius:3px 3px 0 0;opacity:${b.value>0?"0.82":"0.25"};transition:opacity 0.15s;`
    const tipLabel = b.title || b.label
    if (b.value > 0) {
      bar.title = `${tipLabel} : ${b.value} session${b.value>1?"s":""}`
      bar.style.cursor = "pointer"
      bar.onmouseenter = () => { bar.style.opacity="1" }
      bar.onmouseleave = () => { bar.style.opacity="0.82" }
    } else {
      bar.title = tipLabel
    }
    if (!useGlobalScroll) {
      const lbl = col.createEl("span")
      lbl.style.cssText = "font-size:0.68em;color:var(--text-muted);text-align:center;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:100%;"
      lbl.textContent = b.label
    }
  }
  if (useGlobalScroll) {
    const scrollHint = box.createDiv()
    scrollHint.style.cssText = "font-size:0.68em;color:var(--text-faint);text-align:right;margin-top:6px;"
    scrollHint.textContent = `← ${buckets.length} jours - survoler les barres pour les détails →`
  }
}

// ═══════════════════════════════════════════════════════════════
// HEATMAP (helper partagé)
// ═══════════════════════════════════════════════════════════════
const buildHeatmap = (container, actMap, color, CELL=12) => {
  const YEAR = now.getFullYear()
  const today = new Date(now); today.setHours(0,0,0,0)
  const maxAct = Math.max(...Object.values(actMap), 1)
  const SCALE = [
    `rgba(${hexRgb(color)},0.18)`,
    `rgba(${hexRgb(color)},0.38)`,
    `rgba(${hexRgb(color)},0.58)`,
    `rgba(${hexRgb(color)},0.78)`,
    color
  ]
  const getColor = n => {
    if (!n) return null
    const r = n / maxAct
    return r < .20 ? SCALE[0] : r < .40 ? SCALE[1] : r < .60 ? SCALE[2] : r < .80 ? SCALE[3] : SCALE[4]
  }
  const C_EVEN = "#dde3ec", C_ODD = "#cfd5e0"
  const GAP = 3

  // Build weeks (monday-first)
  const jan1 = new Date(YEAR, 0, 1)
  const offset = (jan1.getDay() + 6) % 7
  const start = new Date(jan1); start.setDate(1 - offset)
  const weeks = []
  const cur = new Date(start)
  const dec31 = new Date(YEAR, 11, 31)
  while (cur <= dec31) {
    const w = []
    for (let i = 0; i < 7; i++) { w.push(new Date(cur)); cur.setDate(cur.getDate()+1) }
    weeks.push(w)
  }

  const MONTHS = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
  const DAYS   = ["L","M","M","J","V","S","D"]
  const LABEL_W = 22

  const box = container.createDiv()
  box.style.cssText = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:12px;padding:14px 14px 10px;overflow-x:auto;"

  // Month header row (flex, one cell per week)
  const monthRow = box.createDiv()
  monthRow.style.cssText = `display:flex;padding-left:${LABEL_W+4}px;margin-bottom:3px;`
  let lastM = -1
  for (let wi = 0; wi < weeks.length; wi++) {
    const first = weeks[wi].find(d => d.getFullYear() === YEAR)
    const cell = monthRow.createDiv()
    cell.style.cssText = "flex:1;font-size:0.62em;color:var(--text-muted);white-space:nowrap;overflow:visible;min-width:0;"
    if (first) {
      const m = first.getMonth()
      if (m !== lastM && first.getDate() <= 7) { cell.textContent = MONTHS[m]; lastM = m }
    }
  }

  // Body: day labels + grid
  const body = box.createDiv()
  body.style.cssText = `display:flex;align-items:stretch;height:${7*CELL + 6*GAP}px;`

  const labelsCol = body.createDiv()
  labelsCol.style.cssText = `display:flex;flex-direction:column;justify-content:space-around;width:${LABEL_W}px;flex-shrink:0;margin-right:4px;`
  for (const d of DAYS) {
    const l = labelsCol.createEl("span")
    l.style.cssText = "font-size:0.59em;color:var(--text-faint);text-align:right;line-height:1;"
    l.textContent = d
  }

  const grid = body.createDiv()
  grid.style.cssText = `display:flex;flex:1;gap:${GAP}px;`

  for (let wi = 0; wi < weeks.length; wi++) {
    const col = grid.createDiv()
    col.style.cssText = `display:flex;flex-direction:column;flex:1;gap:${GAP}px;`
    for (const day of weeks[wi]) {
      const ds = `${day.getFullYear()}-${String(day.getMonth()+1).padStart(2,"0")}-${String(day.getDate()).padStart(2,"0")}`
      const n = actMap[ds] || 0
      const outYear = day.getFullYear() !== YEAR
      const isFuture = day > today
      const isToday = day.getTime() === today.getTime()
      const mParity = day.getMonth() % 2
      const emptyBg = mParity === 0 ? C_EVEN : C_ODD
      const bg = outYear ? "transparent" : (n ? getColor(n) : emptyBg)
      const cell = col.createDiv()
      const styles = [`flex:1;border-radius:3px;background:${bg}`]
      if (!outYear) styles.push("border:1px solid rgba(0,0,0,0.05)")
      if (isToday) styles.push("outline:2px solid var(--interactive-accent);outline-offset:1px")
      cell.style.cssText = styles.join(";")
      if (!outYear) cell.title = n ? `${fmtDateFr(day)} - ${n} session${n>1?"s":""}` : fmtDateFr(day)
    }
  }

  // Legend
  const leg = box.createDiv()
  leg.style.cssText = "display:flex;align-items:center;gap:4px;margin-top:8px;justify-content:flex-end;"
  const lbl1 = leg.createEl("span"); lbl1.textContent = "Moins"; lbl1.style.cssText = "font-size:0.62em;color:var(--text-muted);"
  for (const bg of [C_EVEN, ...SCALE]) {
    const sq = leg.createDiv(); sq.style.cssText = `width:10px;height:10px;border-radius:2px;background:${bg};`
  }
  const lbl2 = leg.createEl("span"); lbl2.textContent = "Plus"; lbl2.style.cssText = "font-size:0.62em;color:var(--text-muted);"
}

// ═══════════════════════════════════════════════════════════════
// HEATMAP GLOBALE
// ═══════════════════════════════════════════════════════════════
const renderHeatmap = (container) => {
  const wrap = container.createDiv()
  wrap.style.cssText = "margin-bottom:24px;"
  const ttl = wrap.createEl("h4")
  ttl.style.cssText = "margin:0 0 12px;font-size:0.8em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
  ttl.textContent = `🗓 Activité ${now.getFullYear()}`
  const actMap = {}
  for (const s of allSessions) {
    if (!s.date) continue
    if (new Date(s.date).getFullYear() !== now.getFullYear()) continue
    actMap[s.date] = (actMap[s.date]||0) + 1
  }
  buildHeatmap(wrap, actMap, "#4a8fa8", 12)
}

// ═══════════════════════════════════════════════════════════════
// RECENT ACTIVITY
// ═══════════════════════════════════════════════════════════════
const renderRecentActivity = (container, filtered) => {
  const wrap = container.createDiv()
  const ttl = wrap.createEl("h4")
  ttl.style.cssText = "margin:0 0 12px;font-size:0.8em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
  ttl.textContent = "⚡ Activité récente"

  if (filtered.length === 0) {
    const empty = wrap.createDiv()
    empty.style.cssText = "text-align:center;padding:28px;color:var(--text-muted);font-size:0.88em;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;"
    empty.textContent = "Aucune activité sur cette période."
    return
  }

  // Group by title, keep most recent sessions
  const grouped = {}
  for (const s of filtered) {
    if (!grouped[s.title]) grouped[s.title] = { ...s, total:0, count:0, lastDate:"", lastMetric:0 }
    grouped[s.title].total += s.metric
    grouped[s.title].count += 1
    if (s.date > grouped[s.title].lastDate) {
      grouped[s.title].lastDate = s.date
      grouped[s.title].lastMetric = s.metric
    }
  }
  const sorted = Object.values(grouped).sort((a,b)=>b.lastDate.localeCompare(a.lastDate)).slice(0,16)

  const grid = wrap.createDiv()
  grid.style.cssText = "display:grid;grid-template-columns:repeat(8,1fr);gap:14px;"

  for (const item of sorted) {
    const cfg = TYPE_CFG[item.type] || { icon:"📁", color:"#888", unit:n=>String(n) }
    const p = item.page
    const rawCover = Array.isArray(p.covers) ? p.covers[0] : p.cover

    const card = grid.createDiv()
    card.style.cssText = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;"
    card.onmouseenter = () => { card.style.transform="translateY(-4px)"; card.style.boxShadow="0 8px 20px rgba(0,0,0,0.13)" }
    card.onmouseleave = () => { card.style.transform=""; card.style.boxShadow="" }
    card.onclick = () => openItemModal(p)

    // Cover image
    const imgWrap = card.createDiv()
    imgWrap.style.cssText = "width:100%;aspect-ratio:2/3;overflow:hidden;flex-shrink:0;position:relative;background:var(--background-modifier-border);"
    if (rawCover && rawCover.startsWith("http")) {
      const img = imgWrap.createEl("img"); img.src = rawCover
      img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;"
      img.onerror = () => { img.style.display="none"; const fb=imgWrap.createDiv(); fb.style.cssText="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:1.6em;"; fb.textContent=cfg.icon }
    } else {
      const fb = imgWrap.createDiv(); fb.style.cssText="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:1.6em;"; fb.textContent=cfg.icon
    }

    // Status badge
    if (p.statut) {
      const STATUS = {
        "en cours":{ bg:"rgba(74,143,168,0.92)", txt:"▶ En cours" },
        "backlog":  { bg:"rgba(122,118,110,0.92)",txt:"⊙ Backlog"  },
        "terminé":  { bg:"rgba(78,138,90,0.92)",  txt:"✓ Terminé"  },
        "abandonné":{ bg:"rgba(184,64,64,0.92)",  txt:"✕ Abandonné"},
        "vu":       { bg:"rgba(78,138,90,0.92)",  txt:"✓ Vu"       },
        "à voir":   { bg:"rgba(122,118,110,0.92)",txt:"⊙ À voir"   },
        "lu":       { bg:"rgba(78,138,90,0.92)",  txt:"✓ Lu"       },
        "à lire":   { bg:"rgba(122,118,110,0.92)",txt:"⊙ À lire"   },
      }
      const s = STATUS[p.statut.toLowerCase()]
      if (s) {
        const badge = imgWrap.createEl("span")
        badge.style.cssText = `position:absolute;bottom:6px;left:6px;padding:2px 7px;border-radius:12px;font-size:0.67em;font-weight:700;color:#fff;background:${s.bg};letter-spacing:0.03em;`
        badge.textContent = s.txt
      }
    }

    // Info block
    const info = card.createDiv()
    info.style.cssText = "padding:9px 10px;flex:1;display:flex;flex-direction:column;gap:3px;"
    const titleEl = info.createDiv()
    titleEl.textContent = item.title
    titleEl.style.cssText = "font-weight:700;font-size:0.85em;color:var(--text-normal);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35;"
    const sub = info.createDiv()
    sub.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-top:2px;"
    const dateEl = sub.createEl("span"); dateEl.textContent = fmtDateFr(item.lastDate); dateEl.style.cssText = "font-size:0.72em;color:var(--text-muted);"
    if (item.type === "jeu") {
      const allTimeH = allSessions.filter(s => s.title === item.title && s.type === "jeu").reduce((a,s) => a+s.metric, 0)
      const valWrap = sub.createDiv()
      valWrap.style.cssText = "display:flex;flex-direction:column;align-items:flex-end;gap:1px;"
      const totalEl = valWrap.createEl("span")
      totalEl.textContent = fmtH(allTimeH)
      totalEl.style.cssText = `font-size:0.78em;font-weight:700;color:${cfg.color};`
      if (item.lastMetric > 0) {
        const deltaEl = valWrap.createEl("span")
        deltaEl.textContent = `↑ +${fmtH(item.lastMetric)}`
        deltaEl.style.cssText = "font-size:0.68em;color:var(--text-muted);"
      }
    } else {
      const valEl = sub.createEl("span")
      valEl.textContent = `+${Math.round(item.total)}`
      valEl.style.cssText = `font-size:0.78em;font-weight:700;color:${cfg.color};`
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// INDIVIDUAL VIEW
// ═══════════════════════════════════════════════════════════════
const renderIndividual = () => {
  const lectureTypes = ["manga","manwha","manhua","livre"]

  // Search
  const sinput = root.createEl("input")
  sinput.type = "text"; sinput.placeholder = "🔍 Filtrer par titre…"; sinput.value = st.search||""
  sinput.style.cssText = "width:100%;padding:10px 14px;border-radius:10px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;font-family:inherit;box-sizing:border-box;margin-bottom:10px;"

  // Type filter tabs - container recreated on each renderTypeTabs() call
  const typeWrap = root.createDiv()
  typeWrap.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px;"

  // Card grid container
  const gridWrap = root.createDiv()
  gridWrap.style.cssText = "min-height:60px;"

  const renderList = () => {
    gridWrap.empty()
    const query = (st.search||"").toLowerCase()
    let items = [...allMedia]
    if (st.browseType === "lectures") items = items.filter(p => lectureTypes.includes(p.type))
    else if (st.browseType !== "all") items = items.filter(p => p.type === st.browseType)
    if (query) items = items.filter(p => (p.titre||p.file.name).toLowerCase().includes(query))
    items.sort((a,b) => (a.titre||a.file.name).localeCompare(b.titre||b.file.name))
    if (items.length === 0) {
      const empty = gridWrap.createDiv()
      empty.style.cssText = "padding:24px;text-align:center;color:var(--text-muted);font-size:0.85em;"
      empty.textContent = "Aucun résultat"
      return
    }
    const grid = gridWrap.createDiv()
    grid.style.cssText = "display:grid;grid-template-columns:repeat(9,1fr);gap:14px;"
    for (const p of items) {
      const cfg = TYPE_CFG[p.type] || { icon:"📁", color:"#888", label:p.type }
      const rawCover = Array.isArray(p.covers) ? p.covers[0] : p.cover
      const card = grid.createDiv()
      card.style.cssText = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;"
      card.onmouseenter = () => { card.style.transform="translateY(-4px)"; card.style.boxShadow="0 8px 20px rgba(0,0,0,0.13)" }
      card.onmouseleave = () => { card.style.transform=""; card.style.boxShadow="" }
      card.onclick = () => openItemModal(p)

      // Cover image (aspect-ratio 2/3)
      const imgWrap = card.createDiv()
      imgWrap.style.cssText = "width:100%;aspect-ratio:2/3;overflow:hidden;flex-shrink:0;position:relative;background:var(--background-modifier-border);"
      if (rawCover && rawCover.startsWith("http")) {
        const img = imgWrap.createEl("img"); img.src = rawCover
        img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;"
        img.onerror = () => {
          img.style.display = "none"
          const fb = imgWrap.createDiv()
          fb.style.cssText = "width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:1.6em;"
          fb.textContent = cfg.icon
        }
      } else {
        const fb = imgWrap.createDiv()
        fb.style.cssText = "width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:1.6em;"
        fb.textContent = cfg.icon
      }

      // Status badge overlay (bottom-left of image)
      if (p.statut) {
        const STATUS = {
          "en cours":  { bg:"rgba(74,143,168,0.92)",  txt:"▶ En cours"  },
          "backlog":   { bg:"rgba(122,118,110,0.92)", txt:"⊙ Backlog"   },
          "terminé":   { bg:"rgba(78,138,90,0.92)",   txt:"✓ Terminé"   },
          "abandonné": { bg:"rgba(184,64,64,0.92)",   txt:"✕ Abandonné" },
          "vu":        { bg:"rgba(78,138,90,0.92)",   txt:"✓ Vu"        },
          "à voir":    { bg:"rgba(122,118,110,0.92)", txt:"⊙ À voir"    },
          "lu":        { bg:"rgba(78,138,90,0.92)",   txt:"✓ Lu"        },
          "à lire":    { bg:"rgba(122,118,110,0.92)", txt:"⊙ À lire"    },
        }
        const s = STATUS[p.statut.toLowerCase()]
        if (s) {
          const badge = imgWrap.createEl("span")
          badge.style.cssText = `position:absolute;bottom:6px;left:6px;padding:2px 7px;border-radius:12px;font-size:0.67em;font-weight:700;color:#fff;background:${s.bg};letter-spacing:0.03em;`
          badge.textContent = s.txt
        }
      }

      // Title below image - same structure as MOC cards
      const info = card.createDiv()
      info.style.cssText = "padding:9px 10px;flex:1;display:flex;flex-direction:column;gap:3px;"
      const titleEl = info.createDiv()
      titleEl.textContent = p.titre||p.file.name
      titleEl.style.cssText = "font-weight:700;font-size:0.85em;color:var(--text-normal);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35;"
    }
  }

  // Re-render tabs (updates active highlight) + list
  const renderTypeTabs = () => {
    typeWrap.empty()
    for (const [key, label] of [["all","Tous"],["animé","🎌 Animé"],["film","🎬 Film"],["série","📺 Série"],["jeu","🎮 Jeu"],["lectures","📖 Lectures"]]) {
      const btn = typeWrap.createEl("button")
      const active = st.browseType === key
      btn.style.cssText = `padding:4px 11px;border-radius:14px;border:1px solid ${active?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${active?"rgba(74,143,168,0.12)":"transparent"};color:${active?"var(--interactive-accent)":"var(--text-muted)"};cursor:pointer;font-size:0.78em;font-family:inherit;font-weight:${active?"700":"400"};`
      btn.textContent = label
      btn.onclick = () => {
        st.browseType = key
        st.search = ""
        sinput.value = ""
        renderTypeTabs()
        renderList()
      }
    }
  }

  sinput.oninput = () => { st.search = sinput.value; renderList() }
  renderTypeTabs()
  renderList()
}

// ═══════════════════════════════════════════════════════════════
// ITEM MODAL
// ═══════════════════════════════════════════════════════════════
const openItemModal = (p) => {
  const cfg = TYPE_CFG[p.type] || { icon:"📁", label:p.type, color:"#888", unit:n=>String(n), unitLong:"" }

  // Build sessions once
  let itemSessions = []
  if (p.type === "film") {
    const ds = dateStr(p.date_visionnage)
    if (ds) itemSessions = [{ date:ds, metric:1, label:`Visionné le ${fmtDateFr(p.date_visionnage)}` }]
  } else {
    for (const s of (Array.isArray(p.sessions)?p.sessions:[])) {
      const ds = dateStr(s?.date); if (!ds) continue
      let metric=1, label=""
      if (p.type==="animé" || p.type==="série") {
        metric = s.ep_fin!=null && s.ep_debut!=null ? s.ep_fin-s.ep_debut+1 : 1
        label = `S${s.saison||"?"} - Ép.${s.ep_debut}${s.ep_fin!==s.ep_debut?`→${s.ep_fin}`:""} (${metric} ép.)`
      } else if (p.type==="jeu") {
        metric = parseH(s.h); label = `${fmtH(metric)} jouées`
      } else {
        metric = s.ch_fin!=null && s.ch_debut!=null ? s.ch_fin-s.ch_debut+1 : 1
        label = `Ch.${s.ch_debut}${s.ch_fin!==s.ch_debut?`→${s.ch_fin}`:""} (${metric} ch.)`
      }
      itemSessions.push({ date:ds, metric, label })
    }
    itemSessions.sort((a,b)=>a.date.localeCompare(b.date))
  }

  // Chart granularity (auto-select based on session count)
  const autoGran = itemSessions.length <= 30 ? "session" : itemSessions.length <= 90 ? "week" : "month"
  let chartGran = autoGran

  const groupSessionsByGran = (sessions, gran) => {
    if (gran === "session") return sessions.map(s => ({ ...s, barLabel:`${new Date(s.date).getDate()}/${new Date(s.date).getMonth()+1}`, count:1 }))
    const buckets = {}
    for (const s of sessions) {
      const d = new Date(s.date)
      let key, barLabel, label
      if (gran === "week") {
        const dow = (d.getDay() + 6) % 7
        const mon = new Date(d); mon.setDate(d.getDate() - dow)
        key = mon.toISOString().split("T")[0]
        barLabel = `${mon.getDate()}/${mon.getMonth()+1}`
        label = `Sem. ${mon.getDate()}/${mon.getMonth()+1}`
      } else {
        key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`
        barLabel = MONTHS_FR[d.getMonth()]
        label = `${MONTHS_FR[d.getMonth()]} ${d.getFullYear()}`
      }
      if (!buckets[key]) buckets[key] = { date:key, metric:0, count:0, barLabel, label }
      buckets[key].metric += s.metric
      buckets[key].count++
    }
    return Object.values(buckets).sort((a,b) => a.date.localeCompare(b.date))
  }

  // Overlay
  const overlay = document.body.createEl("div")
  overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.52);z-index:9998;display:flex;align-items:flex-start;justify-content:center;padding:32px 16px;overflow-y:auto;"
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }

  const box = overlay.createEl("div")
  box.style.cssText = "background:var(--background-primary);border-radius:16px;padding:28px 36px 36px;width:100%;max-width:min(1100px,94vw);max-height:92vh;overflow-y:auto;box-shadow:0 16px 56px rgba(0,0,0,0.38);position:relative;margin:auto;"

  // Close button
  const closeBtn = box.createEl("button")
  closeBtn.style.cssText = "position:absolute;top:14px;right:14px;width:26px;height:26px;border-radius:50%;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.85em;display:flex;align-items:center;justify-content:center;font-family:inherit;line-height:1;padding:0;"
  closeBtn.textContent = "✕"
  closeBtn.onclick = () => overlay.remove()

  // Header
  const header = box.createDiv()
  header.style.cssText = "display:flex;gap:14px;margin-bottom:14px;padding-right:28px;"
  const rawCover = Array.isArray(p.covers) ? p.covers[0] : p.cover
  if (rawCover && rawCover.startsWith("http")) {
    const img = header.createEl("img"); img.src = rawCover
    img.style.cssText = "width:62px;height:88px;object-fit:cover;border-radius:8px;flex-shrink:0;"
    img.onerror = () => img.style.display="none"
  }
  const info = header.createDiv(); info.style.cssText = "flex:1;min-width:0;"
  const ht = info.createEl("h3"); ht.textContent = p.titre||p.file.name
  ht.style.cssText = "margin:0 0 8px;font-size:1.2em;font-weight:700;cursor:pointer;"
  ht.onclick = () => { overlay.remove(); app.workspace.openLinkText(p.file.path,"") }
  const metaRow = info.createDiv(); metaRow.style.cssText = "display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px;"
  const tb = metaRow.createEl("span"); tb.textContent = `${cfg.icon} ${cfg.label}`
  tb.style.cssText = `background:rgba(${hexRgb(cfg.color)},0.13);color:${cfg.color};padding:3px 10px;border-radius:10px;font-size:0.82em;font-weight:600;`
  if (p.statut) { const sb = metaRow.createEl("span"); sb.textContent=p.statut; sb.style.cssText="background:var(--background-modifier-border);color:var(--text-muted);padding:3px 10px;border-radius:10px;font-size:0.82em;" }
  if (p.note) { const nb = metaRow.createEl("span"); nb.textContent=`★ ${p.note}/10`; nb.style.cssText="color:#c4943a;font-size:0.88em;font-weight:700;" }
  const subline = info.createDiv(); subline.style.cssText = "font-size:0.86em;color:var(--text-muted);display:flex;gap:10px;flex-wrap:wrap;"
  if (p.type==="jeu" && p.heures_jouées) subline.createEl("span").textContent = `⏱ ${fmtH(parseH(p.heures_jouées))} total`
  if ((p.type==="animé" || p.type==="série") && p.saisons) subline.createEl("span").textContent = `${p.saisons} saison${p.saisons>1?"s":""}`
  if (["manga","manwha","manhua"].includes(p.type) && p.chapitres_lus) subline.createEl("span").textContent = `${p.chapitres_lus} ch. lus${p.chapitres_total?` / ${p.chapitres_total}`:""}`

  // Period tabs (modal-local)
  const periodWrap = box.createDiv()
  periodWrap.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;margin-bottom:16px;"
  const content = box.createDiv()

  const renderContent = () => {
    content.empty()
    const mp = st.modalPeriod
    const filteredSess = itemSessions.filter(s=>isInPeriod(s.date, mp))

    // Key metric
    if (filteredSess.length > 0) {
      const total = filteredSess.reduce((a,s)=>a+s.metric,0)
      const mc = content.createDiv()
      mc.style.cssText = `background:rgba(${hexRgb(cfg.color)},0.07);border:1px solid var(--background-modifier-border);border-radius:10px;padding:11px 14px;margin-bottom:14px;display:flex;align-items:center;gap:14px;`
      const mv = mc.createDiv(); mv.style.cssText = `font-size:2em;font-weight:800;color:${cfg.color};line-height:1;`
      mv.textContent = p.type==="jeu" ? fmtH(total) : Math.round(total)
      mc.createDiv().innerHTML = `<div style="font-size:0.95em;color:var(--text-normal);font-weight:600;">${cfg.unitLong}</div><div style="font-size:0.84em;color:var(--text-muted);margin-top:3px;">${filteredSess.length} session${filteredSess.length>1?"s":""} sur cette période</div>`
    } else if (itemSessions.length > 0) {
      const none = content.createDiv(); none.style.cssText = "text-align:center;padding:8px;color:var(--text-muted);font-size:0.8em;margin-bottom:10px;"
      none.textContent = `Aucune session sur cette période - ${itemSessions.length} au total`
    }

    // Per-item heatmap
    if (itemSessions.length > 0) renderItemHeatmap(content, itemSessions, cfg)

    // Sessions chart
    if (itemSessions.length > 1) {
      const cttl = content.createEl("h4")
      cttl.style.cssText = "margin:0 0 8px;font-size:0.88em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
      cttl.textContent = "📊 Sessions"

      // Granularity toggle
      const granWrap = content.createDiv()
      granWrap.style.cssText = "display:flex;gap:4px;margin-bottom:8px;align-items:center;"
      for (const [key, label] of [["session","Session"],["week","Semaine"],["month","Mois"]]) {
        const btn = granWrap.createEl("button")
        const active = chartGran === key
        btn.style.cssText = `padding:3px 9px;border-radius:10px;border:1px solid ${active?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${active?"rgba(74,143,168,0.12)":"transparent"};color:${active?"var(--interactive-accent)":"var(--text-muted)"};cursor:pointer;font-size:0.75em;font-family:inherit;font-weight:${active?"700":"400"};`
        btn.textContent = label + (key === autoGran ? " ●" : "")
        btn.title = key === autoGran ? "Sélection automatique" : ""
        btn.onclick = () => { chartGran = key; renderContent() }
      }

      const chartBox = content.createDiv()
      chartBox.style.cssText = "background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:12px;margin-bottom:14px;"

      const grouped = groupSessionsByGran(itemSessions, chartGran)
      const maxV = Math.max(...grouped.map(g=>g.metric), 1)
      const useScroll = chartGran === "session" && grouped.length > 35

      const barsWrap = useScroll ? chartBox.createDiv() : chartBox
      if (useScroll) barsWrap.style.cssText = "overflow-x:auto;padding-bottom:2px;"

      const barsEl = barsWrap.createDiv()
      barsEl.style.cssText = useScroll
        ? `display:flex;align-items:flex-end;gap:3px;height:160px;min-width:${grouped.length * 11}px;`
        : "display:flex;align-items:flex-end;gap:4px;height:160px;"

      for (const g of grouped) {
        const inP = chartGran === "session" ? isInPeriod(g.date, mp) : true
        const col = barsEl.createDiv()
        col.style.cssText = useScroll
          ? "display:flex;flex-direction:column;align-items:center;flex:0 0 8px;gap:2px;"
          : "display:flex;flex-direction:column;align-items:center;flex:1;min-width:0;max-width:44px;gap:3px;"
        const inner = col.createDiv()
        inner.style.cssText = "width:100%;display:flex;align-items:flex-end;height:130px;"
        const bar = inner.createDiv()
        const pct = Math.max(4, Math.round((g.metric/maxV)*126))
        bar.style.cssText = `width:100%;height:${pct}px;background:${cfg.color};border-radius:3px 3px 0 0;opacity:${inP?"0.85":"0.18"};transition:opacity 0.15s;cursor:pointer;`
        bar.title = chartGran === "session"
          ? `${fmtDateFr(g.date)} - ${g.label}`
          : `${g.label} : ${p.type==="jeu" ? fmtH(g.metric) : `${Math.round(g.metric)} ${cfg.unitLong}`} - ${g.count} session${g.count>1?"s":""}`
        bar.onmouseenter = () => bar.style.opacity = inP?"1":"0.35"
        bar.onmouseleave = () => bar.style.opacity = inP?"0.85":"0.18"
        if (!useScroll) {
          const lbl = col.createEl("span")
          lbl.style.cssText = "font-size:0.68em;color:var(--text-muted);text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;width:100%;"
          lbl.textContent = g.barLabel
        }
      }
    }

    // Sessions list
    const stitle = content.createEl("h4"); stitle.style.cssText = "margin:0 0 10px;font-size:0.88em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
    const dispSess = filteredSess.length > 0 ? filteredSess : itemSessions
    stitle.textContent = `📋 Sessions${filteredSess.length < itemSessions.length ? ` (${filteredSess.length} / ${itemSessions.length})` : ` - ${itemSessions.length} au total`}`
    if (itemSessions.length === 0) {
      const ns = content.createDiv(); ns.style.cssText = "text-align:center;padding:20px;color:var(--text-muted);font-size:0.85em;background:var(--background-secondary);border-radius:8px;"
      ns.textContent = p.type==="film" ? "Aucune date de visionnage." : "Aucune session enregistrée."
      return
    }
    const slist = content.createDiv()
    slist.style.cssText = "display:flex;flex-direction:column;gap:4px;"
    for (const s of [...dispSess].reverse()) {
      const row = slist.createDiv()
      row.style.cssText = "display:flex;align-items:center;gap:10px;padding:7px 11px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:7px;"
      const dateEl = row.createEl("span"); dateEl.textContent = fmtDateFr(s.date); dateEl.style.cssText = "font-size:0.88em;color:var(--text-muted);min-width:100px;flex-shrink:0;"
      const lblEl = row.createDiv(); lblEl.textContent = s.label; lblEl.style.cssText = "flex:1;font-size:0.93em;color:var(--text-normal);"
      const metEl = row.createEl("span"); metEl.textContent = p.type==="jeu" ? fmtH(s.metric) : `+${Math.round(s.metric)}`
      metEl.style.cssText = `font-size:0.92em;font-weight:700;color:${cfg.color};flex-shrink:0;`
    }
    if (filteredSess.length === 0 && itemSessions.length > 0) {
      const info = content.createDiv(); info.style.cssText = "text-align:center;padding:12px;color:var(--text-muted);font-size:0.8em;margin-top:4px;"
      info.textContent = `Aucune session sur cette période - ${itemSessions.length} au total`
    }
  }

  const renderPeriodTabs = () => {
    periodWrap.empty()
    for (const [key, label] of [["today","Aujourd'hui"],["week","Semaine"],["month","Ce mois"],["year","Cette année"],["all","Tout"]]) {
      const btn = periodWrap.createEl("button")
      const active = st.modalPeriod === key
      btn.style.cssText = `padding:5px 14px;border-radius:14px;border:1px solid ${active?"var(--interactive-accent)":"var(--background-modifier-border)"};background:${active?"rgba(74,143,168,0.12)":"transparent"};color:${active?"var(--interactive-accent)":"var(--text-muted)"};cursor:pointer;font-size:0.88em;font-family:inherit;font-weight:${active?"700":"400"};`
      btn.textContent = label
      btn.onclick = () => { st.modalPeriod = key; renderPeriodTabs(); renderContent() }
    }
  }

  renderPeriodTabs()
  renderContent()
}

// ═══════════════════════════════════════════════════════════════
// PER-ITEM HEATMAP
// ═══════════════════════════════════════════════════════════════
const renderItemHeatmap = (container, sessions, cfg) => {
  const actMap = {}
  for (const s of sessions) {
    if (!s.date) continue
    if (new Date(s.date).getFullYear() !== now.getFullYear()) continue
    actMap[s.date] = (actMap[s.date]||0) + 1
  }
  if (!Object.keys(actMap).length) return
  const wrap = container.createDiv(); wrap.style.cssText = "margin-bottom:14px;"
  const ttl = wrap.createEl("h4"); ttl.style.cssText = "margin:0 0 8px;font-size:0.77em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"
  ttl.textContent = `🗓 Activité ${now.getFullYear()}`
  buildHeatmap(wrap, actMap, cfg.color, 11)
}

// ═══════════════════════════════════════════════════════════════
// GO
// ═══════════════════════════════════════════════════════════════
render()
```
