---
type: dashboard
created: 2026-06-05
tags: [dashboard, home]
cssclasses: [dashboard]
banner: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1400&auto=format&fit=crop&q=80"
banner_y: 0.4
---

# 🎬 Lifetrack

```dataviewjs
if (app.isMobile || window.innerWidth < 700) {
  if (!document.getElementById('mb-fix')) {
    const s = document.createElement('style'); s.id='mb-fix'
    s.textContent = '.metadata-container{display:none!important}'; document.head.appendChild(s)
  }
  const fix = () => document.querySelectorAll('.obsidian-banner-wrapper').forEach(el => { el.style.setProperty('--banner-height','100px'); el.style.setProperty('padding-top','0') })
  fix(); setTimeout(fix,250); setTimeout(fix,700)
}
```

```dataviewjs
// ── BARRE DE STATS ──────────────────────────────
const nMedias = dv.pages('"2 - Domaines/Médias"').where(p => p.statut === "en cours").length
const nInbox  = dv.pages('"0 - Inbox"').length
const nTotal  = dv.pages('!"_Système"').where(p => p.type !== "dashboard").length
const bar = dv.container.createDiv()
bar.style.cssText = "display:flex;align-items:center;gap:12px;padding:10px 18px;margin:10px 0 20px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;font-size:0.87em;flex-wrap:wrap;"
const stats = [[nMedias,"médias en cours"], [nInbox,"dans l'inbox"], [nTotal,"notes au total"]]
for (let i=0; i<stats.length; i++) {
  if (i>0) { const sep=bar.createEl("span"); sep.style.cssText="color:var(--text-faint);font-size:1.1em;line-height:1;"; sep.textContent="·" }
  const s=bar.createEl("span"); const b=s.createEl("strong"); b.style.cssText="color:#5b8db8;font-size:1.08em;margin-right:4px;"; b.textContent=String(stats[i][0]); s.appendChild(document.createTextNode(stats[i][1]))
}
```

## 🗺 Hub Principal

```dataviewjs
// ── GRILLE HUB ───
const isMobile = window.innerWidth < 700
const hub = dv.container.createDiv()
hub.style.cssText = `display:grid;grid-template-columns:repeat(${isMobile?2:4},1fr);gap:10px;margin:12px 0 4px;`

let _financeCount = "..."
try {
  const _now=new Date(), _yyyy=_now.getFullYear(), _mm=String(_now.getMonth()+1).padStart(2,"0")
  const _jf=app.vault.getAbstractFileByPath("2 - Domaines/Finances/Transactions/💰 "+_yyyy+".json")
  if (_jf) {
    const _txs=JSON.parse(await app.vault.read(_jf))
    const _n=_txs.filter(t=>(t.date||"").slice(0,7)===_yyyy+"-"+_mm).length
    _financeCount=_n+" transaction"+(_n!==1?"s":"")+" ce mois"
  } else { _financeCount="Aucune transaction" }
} catch(e) { _financeCount="Configurer les finances" }

let _sportCount = "Voir mes séances"
try {
  const _sportFiles = app.vault.getFiles().filter(f =>
    f.path.startsWith("2 - Domaines/Sport/Data/") && /^hevy_\d{4}\.json$/.test(f.name)
  )
  let _totalSport = 0
  for (const _sf of _sportFiles) { _totalSport += JSON.parse(await app.vault.read(_sf)).length }
  _sportCount = _totalSport + " séance" + (_totalSport > 1 ? "s" : "")
} catch(e) {}

const sections = [
  { icon:"🎬", name:"Films, Animés & Séries", link:"MOC - Films, Animés & Séries", color:"#e07b5a", bg:"rgba(224,123,90,0.09)",
    count: dv.pages('"2 - Domaines/Médias"').where(p=>["animé","film","série"].includes(p.type)&&p.statut==="en cours").length+" en cours" },
  { icon:"📖", name:"Lectures",       link:"MOC - Lectures",        color:"#8878c3", bg:"rgba(136,120,195,0.09)",
    count: dv.pages('"2 - Domaines/Médias"').where(p=>["manga","manwha","livre"].includes(p.type)&&p.statut==="en cours").length+" en cours" },
  { icon:"🎮", name:"Jeux Vidéo",     link:"MOC - Jeux Vidéo",      color:"#4a8fa8", bg:"rgba(74,143,168,0.09)",
    count: dv.pages('"2 - Domaines/Médias/Jeux Vidéo"').where(p=>p.statut==="en cours").length+" en cours" },
  { icon:"🛒", name:"Commandes",      link:"MOC - Commandes",        color:"#fe640b", bg:"rgba(254,100,11,0.09)",
    count: dv.pages('"2 - Domaines/Commandes"').where(p=>p.type==="commande"&&p.statut!=="livré"&&p.statut!=="annulé").length+" en attente" },
  { icon:"💰", name:"Finances",       link:"💰 Finances",            color:"#40a02b", bg:"rgba(64,160,43,0.09)",
    count: _financeCount },
  { icon:"🏋️", name:"Sport",          link:"🏋️ Sport",               color:"#e85d04", bg:"rgba(232,93,4,0.09)",
    count: _sportCount },
  { icon:"🔍", name:"Explorateur",    link:"🔍 Explorateur",         color:"#7a766e", bg:"rgba(122,118,110,0.09)",
    count: "Rechercher toutes les notes" },
  { icon:"📊", name:"Statistiques",   link:"📊 Statistiques",        color:"#4a8fa8", bg:"rgba(74,143,168,0.09)",
    count: "Stats médias & activité" },
]

for (const s of sections) {
  const card=hub.createDiv()
  card.style.cssText=`padding:14px 12px 12px;border-radius:10px;border:1px solid var(--background-modifier-border);border-top:3px solid ${s.color};background:${s.bg};cursor:pointer;transition:transform 0.15s,box-shadow 0.15s;user-select:none;`
  card.onmouseenter=()=>{card.style.transform="translateY(-3px)";card.style.boxShadow="0 6px 16px rgba(0,0,0,0.10)"}
  card.onmouseleave=()=>{card.style.transform="";card.style.boxShadow=""}
  card.onclick=()=>app.workspace.openLinkText(s.link,"","tab")
  const icon=card.createDiv(); icon.style.cssText="font-size:1.5em;line-height:1;margin-bottom:8px;"; icon.textContent=s.icon
  const name=card.createDiv(); name.style.cssText="font-weight:700;font-size:0.9em;color:var(--text-normal);margin-bottom:3px;"; name.textContent=s.name
  const count=card.createDiv(); count.style.cssText="font-size:0.74em;color:var(--text-muted);"; count.textContent=s.count
}
```

## 📊 Activité

```dataviewjs
// ═══════════════════════════════════════════════════════════════
//  HEATMAP - Activité du vault (notes créées)
// ═══════════════════════════════════════════════════════════════
const YEAR=new Date().getFullYear(), today=new Date(); today.setHours(0,0,0,0)
const fmtLocal=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
const fmtDateFr=iso=>new Date(iso+"T12:00:00").toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"})
const byDay={}
for(const p of dv.pages('!"_Système"').where(p=>p.type!=="dashboard")){
  const raw=p.created, ts=raw?new Date(String(raw).slice(0,10)+"T12:00:00"):(p.file.ctime?p.file.ctime.toJSDate():null)
  if(!ts||ts.getFullYear()!==YEAR) continue
  const k=fmtLocal(ts); byDay[k]=(byDay[k]||0)+1
}
const maxVal=Math.max(1,...Object.values(byDay))
const allKeys=Object.keys(byDay).filter(k=>k.startsWith(YEAR)).sort()
let streak=0; const d0=new Date(today)
while(true){const k=fmtLocal(d0);if(!byDay[k])break;streak++;d0.setDate(d0.getDate()-1)}
const bestKey=allKeys.reduce((a,b)=>(byDay[b]||0)>(byDay[a]||0)?b:a,allKeys[0]||"")
const bestCount=bestKey?byDay[bestKey]:0, bestFmt=bestKey?bestKey.slice(8,10)+"/"+bestKey.slice(5,7):"-"
const C_EMPTY="#dde3ec", SCALE=["#d4bffe","#b79bf5","#9a78e8","#7c54d4","#5c30b8"]
const getColor=n=>{if(!n)return C_EMPTY;const r=n/maxVal;return r<.20?SCALE[0]:r<.40?SCALE[1]:r<.60?SCALE[2]:r<.80?SCALE[3]:SCALE[4]}
const jan1=new Date(YEAR,0,1), offset=(jan1.getDay()+6)%7, start=new Date(jan1); start.setDate(1-offset)
const weeks=[],cur=new Date(start),dec31=new Date(YEAR,11,31)
while(cur<=dec31){const w=[];for(let i=0;i<7;i++){w.push(new Date(cur));cur.setDate(cur.getDate()+1)};weeks.push(w)}
const MONTHS=["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"],DAYS=["L","M","M","J","V","S","D"]
const isMobile=window.innerWidth<700, LABEL_W=isMobile?20:26
const wrap=dv.container.createDiv(); wrap.style.cssText=`margin:6px 0 2px;${isMobile?"overflow-x:auto;":""}width:${isMobile?"min-content;min-width:100%":"100%"};`
const monthRow=wrap.createDiv(); monthRow.style.cssText=`display:flex;padding-left:${LABEL_W+4}px;margin-bottom:3px;`
let lastM=-1
for(let wi=0;wi<weeks.length;wi++){const first=weeks[wi].find(d=>d.getFullYear()===YEAR);const cell=monthRow.createDiv();cell.style.cssText="flex:1;font-size:0.67em;color:var(--text-muted);white-space:nowrap;overflow:visible;min-width:0;";if(first){const m=first.getMonth();if(m!==lastM&&first.getDate()<=7){cell.textContent=MONTHS[m];lastM=m}}}
const body=wrap.createDiv(); body.style.cssText="display:flex;align-items:stretch;width:100%;height:116px;"
const labelsCol=body.createDiv(); labelsCol.style.cssText=`display:flex;flex-direction:column;justify-content:space-around;width:${LABEL_W}px;flex-shrink:0;margin-right:4px;`
for(const d of DAYS){const l=labelsCol.createEl("span");l.style.cssText="font-size:0.59em;color:var(--text-faint);text-align:right;line-height:1;";l.textContent=d}
const grid=body.createDiv(); grid.style.cssText="display:flex;flex:1;gap:3px;"
for(const week of weeks){
  const col=grid.createDiv(); col.style.cssText="display:flex;flex-direction:column;flex:1;gap:3px;"
  for(const day of week){
    const key=fmtLocal(day),n=byDay[key]||0,outYear=day.getFullYear()!==YEAR,isToday=day.getTime()===today.getTime()
    const cell=col.createDiv(),emptyBg=day.getMonth()%2===0?C_EMPTY:"#cfd5e0",bg=outYear?"transparent":(n?getColor(n):emptyBg)
    cell.style.cssText=["flex:1;border-radius:3px",`background:${bg}`,!outYear?"border:1px solid rgba(0,0,0,0.05)":"",isToday?"outline:2px solid #8839ef;outline-offset:1px;":""].filter(Boolean).join(";")
    if(!outYear) cell.title=n?`${fmtDateFr(key)}  ·  ${n} action${n>1?"s":""}`:`${fmtDateFr(key)}  ·  aucune activité`
  }
}
const footer=wrap.createDiv(); footer.style.cssText="display:flex;align-items:center;justify-content:space-between;margin-top:8px;flex-wrap:wrap;gap:8px;"
const statsRow=footer.createDiv(); statsRow.style.cssText="display:flex;gap:16px;font-size:0.72em;color:var(--text-muted);"
for(const {val,lbl} of [{val:streak,lbl:`jour${streak>1?"s":""} de suite 🔥`},{val:Object.keys(byDay).length,lbl:"jours actifs"},{val:bestCount,lbl:`actions (record le ${bestFmt})`}]){
  const sp=statsRow.createEl("span"); const b=sp.createEl("strong"); b.style.cssText="color:#8839ef;margin-right:3px;"; b.textContent=String(val); sp.append(lbl)
}
const legend=footer.createDiv(); legend.style.cssText="display:flex;align-items:center;gap:4px;font-size:0.71em;color:var(--text-muted);"
legend.createEl("span").textContent="Moins"
for(const c of [C_EMPTY,...SCALE]){const sq=legend.createDiv();sq.style.cssText=`width:11px;height:11px;border-radius:2px;background:${c};border:1px solid rgba(0,0,0,0.07);flex-shrink:0;`}
legend.createEl("span").textContent="Plus"
```

## 🎮 Suivi Médias

```dataviewjs
// ╔══════════════════════════════════════════════════════════════╗
// ║  TRACKER MÉDIAS - basé sur les sessions de consommation     ║
// ║  Jeux vidéo · Animés · Films · Séries · Manga & Manwha      ║
// ╚══════════════════════════════════════════════════════════════╝
const YEAR  = new Date().getFullYear()
const today = new Date(); today.setHours(0,0,0,0)
const fmtLocal = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`

// ── Sources ───────────────────────────────────────────────────────
// computeQty : calcule les unités d'une entrée sessions (avec compat ancien format)
// unit       : libellé de l'unité (singulier)
const TRACKS = [
  { key:"jeux",   icon:"🎮", label:"Jeux vidéo",    query:'"2 - Domaines/Médias/Jeux Vidéo"',     types:["jeu"],
    unit:"heure",
    computeQty: s => {
      if (!s.h) return 0
      const str = String(s.h)
      if (str.includes(":")) {
        const [hh, mm] = str.split(":").map(Number)
        return (hh || 0) + (mm || 0) / 60
      }
      return Number(s.h) || 0
    },
    fmtQty: (s, n) => {
      const str = String(s.h || "")
      if (str.includes(":")) {
        const [hh, mm] = str.split(":")
        return mm && mm !== "00" ? `${hh}h${mm.padStart(2,"0")}` : `${hh}h`
      }
      const hh = Math.floor(n), mm = Math.round((n - hh) * 60)
      return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h`
    },
    scale:["#bbf7d0","#4ade80","#22c55e","#15803d","#14532d"] },
  { key:"animés", icon:"🎌", label:"Animés, Films & Séries", query:'"2 - Domaines/Médias/Animés"', types:["animé"],
    unit:"épisode",
    computeQty: s => s.ep_fin != null && s.ep_debut != null ? s.ep_fin - s.ep_debut + 1 : (Number(s.ep) || 0),
    fmtQty: (s, n) => {
      const de = s.ep_debut, a = s.ep_fin, sais = s.saison ? `S${s.saison} ` : ""
      return de != null && a != null
        ? (de === a ? `${sais}ep.${de}` : `${sais}ep.${de}-${a}`)
        : `${n} ep.`
    },
    scale:["#fed7aa","#fb923c","#f97316","#ea580c","#9a3412"] },
  { key:"manga",  icon:"📖", label:"Manga & Manwha", query:'"2 - Domaines/Médias/Manga & Manwha"', types:["manga","manwha","manhua"],
    unit:"chapitre",
    computeQty: s => s.ch_fin != null && s.ch_debut != null ? s.ch_fin - s.ch_debut + 1 : (Number(s.ch) || 0),
    fmtQty: (s, n) => {
      const de = s.ch_debut, a = s.ch_fin
      return de != null && a != null
        ? (de === a ? `ch.${de}` : `ch.${de}-${a}`)
        : `${n} ch.`
    },
    scale:["#bfdbfe","#60a5fa","#3b82f6","#1d4ed8","#1e3a8a"] },
]
const C_EMPTY = "#e2e5ed"

// ── Collecte : parcourt les sessions[] de chaque fiche ───────────
const allData = {}
for (const t of TRACKS) {
  const byDay = {}
  const sessionsByDay = {}
  let totalQty = 0, noteCount = 0
  for (const p of dv.pages(t.query).where(p => t.types.includes(p.type))) {
    noteCount++
    if (!p.sessions || !Array.isArray(p.sessions)) continue
    for (const s of p.sessions) {
      if (!s || !s.date) continue
      const dateStr = String(s.date).slice(0, 10)
      if (!dateStr.startsWith(String(YEAR))) continue
      const qty = t.computeQty(s)
      if (qty > 0) {
        byDay[dateStr] = (byDay[dateStr] || 0) + qty
        totalQty += qty
        if (t.key === "manga" || t.key === "jeux" || t.key === "animés") {
          if (!sessionsByDay[dateStr]) sessionsByDay[dateStr] = []
          sessionsByDay[dateStr].push({ icon: "🎌", titre: p.titre || p.file.name, fmtStr: t.fmtQty(s, qty) })
        }
      }
    }
  }
  allData[t.key] = { byDay, totalQty, noteCount, activeDays: Object.keys(byDay).length, epsByDay: t.key === "animés" ? {...byDay} : null, sessionsByDay: (t.key === "manga" || t.key === "jeux" || t.key === "animés") ? sessionsByDay : null }
}

// ── Films : injection dans le track Animés ────────────────────────
{
  const ad = allData["animés"]
  let filmCount = 0
  const filmsByDay = {}
  for (const p of dv.pages('"2 - Domaines/Médias/Films"').where(p => p.type === "film" && p.date_visionnage)) {
    const dateStr = String(p.date_visionnage).slice(0, 10)
    if (!dateStr.startsWith(String(YEAR))) continue
    ad.byDay[dateStr] = (ad.byDay[dateStr] || 0) + 1
    ad.totalQty += 1
    filmCount++
    if (!filmsByDay[dateStr]) filmsByDay[dateStr] = []
    filmsByDay[dateStr].push(p.titre || p.file.name)
  }
  ad.filmCount = filmCount
  ad.filmsByDay = filmsByDay
  ad.activeDays = Object.keys(ad.byDay).length
}

// ── Séries : injection dans le track Animés ───────────────────────
{
  const ad = allData["animés"]
  let serieCount = 0
  for (const p of dv.pages('"2 - Domaines/Médias/Séries"').where(p => p.type === "série")) {
    if (!p.sessions || !Array.isArray(p.sessions)) continue
    serieCount++
    for (const s of p.sessions) {
      if (!s || !s.date) continue
      const dateStr = String(s.date).slice(0, 10)
      if (!dateStr.startsWith(String(YEAR))) continue
      const qty = s.ep_fin != null && s.ep_debut != null ? s.ep_fin - s.ep_debut + 1 : (Number(s.ep) || 0)
      if (qty > 0) {
        ad.byDay[dateStr] = (ad.byDay[dateStr] || 0) + qty
        ad.totalQty += qty
        if (!ad.sessionsByDay[dateStr]) ad.sessionsByDay[dateStr] = []
        const sais = s.saison ? `S${s.saison} ` : ""
        const fmtStr = s.ep_debut != null && s.ep_fin != null
          ? (s.ep_debut === s.ep_fin ? `${sais}ep.${s.ep_debut}` : `${sais}ep.${s.ep_debut}-${s.ep_fin}`)
          : `${qty} ep.`
        ad.sessionsByDay[dateStr].push({ icon: "📺", titre: p.titre || p.file.name, fmtStr })
        if (!ad.epsByDay) ad.epsByDay = {}
        ad.epsByDay[dateStr] = (ad.epsByDay[dateStr] || 0) + qty
      }
    }
  }
  ad.serieCount = serieCount
  ad.activeDays = Object.keys(ad.byDay).length
}

// ── Semaines (lundi en premier) ───────────────────────────────────
const jan1   = new Date(YEAR, 0, 1)
const offset = (jan1.getDay() + 6) % 7
const start  = new Date(jan1); start.setDate(1 - offset)
const weeks  = []
const cur    = new Date(start)
const dec31  = new Date(YEAR, 11, 31)
while (cur <= dec31) {
  const w = []
  for (let i = 0; i < 7; i++) { w.push(new Date(cur)); cur.setDate(cur.getDate() + 1) }
  weeks.push(w)
}

const MONTHS  = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
const isMobile = window.innerWidth < 700
const LABEL_W = isMobile ? 60 : 100  // largeur colonne icône + label

// ── Wrapper ───────────────────────────────────────────────────────
const wrap = dv.container.createDiv()
wrap.style.cssText = `margin:6px 0;${isMobile ? "overflow-x:auto;" : ""}width:${isMobile ? "min-content;min-width:100%" : "100%"};`

// ── Stats globales (une ligne) ────────────────────────────────────
const statsRow = wrap.createDiv()
statsRow.style.cssText = "display:flex;gap:20px;font-size:0.78em;margin-bottom:14px;flex-wrap:wrap;"
const COLORS = ["#15803d","#ea580c","#1d4ed8"]
TRACKS.forEach((t, i) => {
  const { totalQty, noteCount, filmCount, serieCount } = allData[t.key]
  const el = statsRow.createEl("span")
  el.style.cssText = "display:flex;align-items:center;gap:5px;color:var(--text-muted);"
  const unitPlur = totalQty > 1 ? t.unit + "s" : t.unit
  const filmSuffix = (t.key === "animés" && filmCount) ? ` · ${filmCount} film${filmCount > 1 ? "s" : ""}` : ""
  const serieSuffix = (t.key === "animés" && serieCount) ? ` · ${serieCount} série${serieCount > 1 ? "s" : ""}` : ""
  const animéLabel = t.key === "animés" ? `${allData["animés"].noteCount} animés` : `${noteCount} ${t.label.toLowerCase()}`
  const totalDisplay = t.key === "jeux"
    ? (() => { const hh = Math.floor(totalQty), mm = Math.round((totalQty - hh) * 60); return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h` })()
    : totalQty
  const unitDisplay = t.key === "jeux" ? "" : " " + unitPlur
  el.innerHTML = `${t.icon} <strong style="color:${COLORS[i]}">${totalDisplay}</strong>${unitDisplay} · ${t.key === "animés" ? animéLabel + filmSuffix + serieSuffix : `${noteCount} ${t.label.toLowerCase()}`}`
})

// ── En-tête des mois (partagé, aligné sur la grille) ─────────────
const monthHeader = wrap.createDiv()
monthHeader.style.cssText = `display:flex;padding-left:${LABEL_W}px;margin-bottom:4px;`
let lastM = -1
for (let wi = 0; wi < weeks.length; wi++) {
  const first = weeks[wi].find(d => d.getFullYear() === YEAR)
  const cell  = monthHeader.createDiv()
  cell.style.cssText = "flex:1;min-width:0;font-size:0.66em;color:var(--text-muted);white-space:nowrap;overflow:visible;font-weight:500;"
  if (first) {
    const m = first.getMonth()
    if (m !== lastM && first.getDate() <= 7) { cell.textContent = MONTHS[m]; lastM = m }
  }
}

// ── Fonction heatmap ──────────────────────────────────────────────
const renderTrack = (t) => {
  const { byDay, totalQty, activeDays } = allData[t.key]
  const maxVal  = Math.max(1, ...Object.values(byDay))
  const getColor = n => {
    if (!n) return C_EMPTY
    const r = n / maxVal
    return r < .20 ? t.scale[0] : r < .40 ? t.scale[1] : r < .65 ? t.scale[2] : r < .85 ? t.scale[3] : t.scale[4]
  }

  const row = wrap.createDiv()
  row.style.cssText = "display:flex;align-items:stretch;height:96px;margin-bottom:6px;"

  // Colonne gauche : icône + label + stat
  const meta = row.createDiv()
  meta.style.cssText = `width:${LABEL_W}px;flex-shrink:0;display:flex;flex-direction:column;justify-content:center;padding-right:10px;`
  const iconEl = meta.createDiv()
  iconEl.style.cssText = "font-size:1.1em;line-height:1;margin-bottom:2px;"
  iconEl.textContent = t.icon
  const labelEl = meta.createDiv()
  labelEl.style.cssText = "font-size:0.72em;font-weight:700;color:var(--text-normal);line-height:1.2;"
  labelEl.textContent = t.label
  const statEl = meta.createDiv()
  statEl.style.cssText = "font-size:0.63em;color:var(--text-faint);margin-top:3px;line-height:1.4;"
  if (activeDays > 0) {
    const unitPlur = totalQty > 1 ? t.unit + "s" : t.unit
    const { filmCount, serieCount } = allData[t.key]
    const filmPart = (t.key === "animés" && filmCount) ? ` · ${filmCount} film${filmCount > 1 ? "s" : ""}` : ""
    const seriePart = (t.key === "animés" && serieCount) ? ` · ${serieCount} série${serieCount > 1 ? "s" : ""}` : ""
    const fmtHours = h => { const hh = Math.floor(h), mm = Math.round((h-hh)*60); return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h` }
    statEl.textContent = t.key === "jeux"
      ? `${fmtHours(totalQty)} · ${activeDays}j`
      : `${totalQty} ${unitPlur} · ${activeDays}j${filmPart}${seriePart}`
  } else {
    statEl.textContent = "aucune session"
  }

  // Grille
  const grid = row.createDiv()
  grid.style.cssText = "display:flex;flex:1;gap:2px;"

  for (let wi = 0; wi < weeks.length; wi++) {
    const col = grid.createDiv()
    col.style.cssText = "display:flex;flex-direction:column;flex:1;gap:2px"

    for (const day of weeks[wi]) {
      const k       = fmtLocal(day)
      const n       = byDay[k] || 0
      const outYear = day.getFullYear() !== YEAR
      const isToday = day.getTime() === today.getTime()
      const mParity = day.getMonth() % 2
      const emptyBg = mParity === 0 ? C_EMPTY : "#d4d8e2"
      const bg      = outYear ? "transparent" : (n ? getColor(n) : emptyBg)

      const cell = col.createDiv()
      cell.style.cssText = [
        "flex:1;border-radius:2px", `background:${bg}`,
        !outYear ? "border:1px solid rgba(0,0,0,0.05)" : "",
        isToday  ? "outline:2px solid #8839ef;outline-offset:1px;" : "",
      ].filter(Boolean).join(";")

      if (!outYear) {
        if (t.key === "animés") {
          const eps   = (allData["animés"].epsByDay  || {})[k] || 0
          const films = (allData["animés"].filmsByDay || {})[k] || []
          const d = new Date(k + "T12:00:00")
          const dateLabel = d.toLocaleDateString("fr-FR", { day:"numeric", month:"long", year:"numeric" })
          if (eps > 0 || films.length > 0) {
            const lines = [dateLabel]
            if (eps > 0) {
              const animeSessions = (allData["animés"].sessionsByDay || {})[k] || []
              for (const s of animeSessions) lines.push((s.icon || "🎌") + " " + s.titre + " (" + s.fmtStr + ")")
            }
            for (const f of films) lines.push("🎬 " + f)
            cell.title = lines.join("\n")
          } else {
            cell.title = dateLabel + "\nAucune activité"
          }
        } else if (t.key === "manga" || t.key === "jeux") {
          const sessions = (allData[t.key].sessionsByDay || {})[k] || []
          const d = new Date(k + "T12:00:00")
          const dateLabel = d.toLocaleDateString("fr-FR", { day:"numeric", month:"long", year:"numeric" })
          if (sessions.length > 0) {
            const icon = t.key === "manga" ? "📖" : "🎮"
            const lines = [dateLabel]
            if (t.key === "manga") {
              for (const s of sessions) lines.push(icon + " " + s.titre + " (" + s.fmtStr + ")")
            } else {
              for (const s of sessions) lines.push(icon + " " + s.titre + " (" + s.fmtStr + ")")
            }
            cell.title = lines.join("\n")
          } else {
            cell.title = dateLabel + "\nAucune activité"
          }
        } else {
          const unitPlur = n > 1 ? t.unit + "s" : t.unit
          cell.title = n ? `📅 ${k}  -  ${n} ${unitPlur}` : `📅 ${k}  -  aucune session`
        }
      }
    }
  }

  // Légende sous ce tracker
  const legRow = wrap.createDiv()
  legRow.style.cssText = `display:flex;align-items:center;gap:4px;margin-top:3px;margin-bottom:10px;font-size:0.68em;color:var(--text-muted);padding-left:${LABEL_W}px;`
  legRow.createEl("span").textContent = "Moins"
  for (const c of [C_EMPTY, ...t.scale]) {
    const sq = legRow.createDiv()
    sq.style.cssText = `width:10px;height:10px;border-radius:2px;background:${c};border:1px solid rgba(0,0,0,0.07);flex-shrink:0;`
  }
  legRow.createEl("span").textContent = "Plus"
}

for (const t of TRACKS) renderTrack(t)
```

## 🎬 En ce moment

```dataviewjs
// ── MÉDIAS EN COURS - onglets par type + pagination ──────────────
const TYPES = {
  "animé":   { icon:"🎌", label:"Animés",  color:"#e07b5a" },
  "film":    { icon:"🎬", label:"Films",   color:"#c07850" },
  "série":   { icon:"📺", label:"Séries",  color:"#7b6cb8" },
  "manga":   { icon:"📖", label:"Manga",   color:"#8878c3" },
  "manwha":  { icon:"📗", label:"Manwha",  color:"#8878c3" },
  "manhua":  { icon:"📘", label:"Manhua",  color:"#8878c3" },
  "jeu":     { icon:"🎮", label:"Jeux",    color:"#4a8fa8" },
  "livre":   { icon:"📚", label:"Livres",  color:"#4e8a5a" },
}
const ALL_COLOR = "#5b8db8"

const allMedias = dv.pages('"2 - Domaines/Médias"')
  .where(p => p.statut === "en cours")
  .sort(p => p.file.mtime, "desc")
  .array()

// Grouper par type
const byType = {}
for (const p of allMedias) {
  const k = p.type || "autre"
  if (!byType[k]) byType[k] = []
  byType[k].push(p)
}

// Construire l'ordre des onglets (Tout + types présents)
const presentTypes = Object.keys(TYPES).filter(k => byType[k]?.length > 0)
const tabs = [{ key:"tout", icon:"🎭", label:"Tout", color:ALL_COLOR, items: allMedias }]
for (const k of presentTypes) tabs.push({ key:k, ...TYPES[k], items: byType[k] })

const isMobile = window.innerWidth < 700
const PAGE_SIZE = isMobile ? 4 : 6

// ── Helpers progression ───────────────────────────────────────────
const sumAnimé = arr => !Array.isArray(arr) ? 0 : arr.reduce((t, s) => {
  if (!s) return t
  return t + (s.ep_fin != null && s.ep_debut != null ? s.ep_fin - s.ep_debut + 1 : (Number(s.ep) || 0))
}, 0)
const sumManga = arr => !Array.isArray(arr) ? 0 : arr.reduce((t, s) => {
  if (!s) return t
  return t + (s.ch_fin != null && s.ch_debut != null ? s.ch_fin - s.ch_debut + 1 : (Number(s.ch) || 0))
}, 0)
const parseH = h => { const str = String(h||""); if (str.includes(":")) { const [hh,mm]=str.split(":").map(Number); return (hh||0)+(mm||0)/60 } return parseFloat(str)||0 }
const fmtJeu = h => { const hh=Math.floor(h), mm=Math.round((h-hh)*60); return mm ? `${hh}h${String(mm).padStart(2,"0")}` : `${hh}h` }
const sumJeu = arr => !Array.isArray(arr) ? 0 : arr.reduce((t, s) => t + parseH(s?.h), 0)

const getProgression = p => {
  if (p.type === "animé") {
    const n = sumAnimé(p.sessions)
    return n > 0 ? `${n} ep.` : (p.saisons ? `${p.saisons} saison${p.saisons > 1 ? "s" : ""}` : null)
  }
  if (p.type === "manga" || p.type === "manwha" || p.type === "manhua") {
    const n = sumManga(p.sessions) || p.chapitres_lus || 0
    return n > 0 ? `Ch. ${n}${p.chapitres_total ? "/" + p.chapitres_total : ""}` : null
  }
  if (p.type === "jeu") {
    const n = sumJeu(p.sessions) || parseH(p.heures_jouées) || 0
    return n > 0 ? fmtJeu(n) + " jouées" : null
  }
  return null
}

// ── Rendu d'une card ──────────────────────────────────────────────
const mkCard = (p, grid) => {
  const t = TYPES[p.type] ?? { icon:"🎭", color:"#7a766e" }
  const card = grid.createDiv()
  card.style.cssText = [
    "padding:8px 11px",
    "background:var(--background-secondary)",
    "border:1px solid var(--background-modifier-border)",
    `border-left:3px solid ${t.color}`,
    "border-radius:8px","cursor:pointer"
  ].join(";")
  card.onmouseenter = () => card.style.boxShadow = "0 2px 8px rgba(0,0,0,0.10)"
  card.onmouseleave = () => card.style.boxShadow = ""
  card.onclick = () => app.workspace.openLinkText(p.file.path, "", "tab")

  const top = card.createDiv()
  top.style.cssText = "display:flex;align-items:baseline;justify-content:space-between;gap:6px;margin-bottom:3px;"
  const title = top.createEl("span")
  title.style.cssText = "font-weight:600;font-size:0.84em;color:var(--text-normal);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
  title.textContent = p.file.name

  const typeTag = top.createEl("span")
  typeTag.style.cssText = `font-size:0.65em;font-weight:800;letter-spacing:0.06em;color:${t.color};flex-shrink:0;`
  typeTag.textContent = t.icon

  const meta = card.createDiv()
  meta.style.cssText = "display:flex;align-items:center;gap:8px;"
  const prog = getProgression(p)
  if (prog) {
    const progEl = meta.createEl("span")
    progEl.style.cssText = "font-size:0.74em;color:var(--text-muted);"
    progEl.textContent = prog
  }
  if (p.note) {
    const noteEl = meta.createEl("span")
    noteEl.style.cssText = "font-size:0.72em;color:var(--text-muted);"
    noteEl.textContent = "⭐" + p.note
  }
}

// ── Rendu de la zone d'un onglet ──────────────────────────────────
const renderTab = (tab, page, zone) => {
  zone.empty()
  if (tab.items.length === 0) {
    zone.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.87em;padding:8px 0;"}}).textContent = "Aucun média en cours"
    return
  }
  const totalPages = Math.ceil(tab.items.length / PAGE_SIZE)
  const slice = tab.items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const grid = zone.createDiv()
  grid.style.cssText = `display:grid;grid-template-columns:repeat(${isMobile ? 1 : 2},1fr);gap:7px;margin-bottom:8px;`
  for (const p of slice) mkCard(p, grid)
  if (totalPages > 1) {
    const BTN_P = "padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.78em;color:var(--text-normal);font-family:inherit;"
    const pager = zone.createDiv()
    pager.style.cssText = "display:flex;align-items:center;justify-content:space-between;"
    const prev = pager.createEl("button", {attr:{style:BTN_P + (page===0?"opacity:0.4;":"")}})
    prev.textContent = "←"; prev.disabled = page === 0
    prev.onclick = () => renderTab(tab, page - 1, zone)
    pager.createEl("span", {attr:{style:"font-size:0.76em;color:var(--text-muted);"}}).textContent = `${page+1} / ${totalPages}`
    const next = pager.createEl("button", {attr:{style:BTN_P + (page===totalPages-1?"opacity:0.4;":"")}})
    next.textContent = "→"; next.disabled = page === totalPages - 1
    next.onclick = () => renderTab(tab, page + 1, zone)
  }
}

// ── Construction des onglets ──────────────────────────────────────
const TAB_BASE = "padding:4px 10px;border-radius:16px;border:1px solid;cursor:pointer;font-size:0.78em;font-weight:600;transition:all 0.15s;white-space:nowrap;"
const TAB_ON  = c => `${TAB_BASE}background:${c};color:#fff;border-color:${c};`
const TAB_OFF = c => `${TAB_BASE}background:transparent;color:${c};border-color:${c};opacity:0.55;`

const wrap = dv.container.createDiv()
const tabBar = wrap.createDiv()
tabBar.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;margin-bottom:10px;"
const zone = wrap.createDiv()

let activeTab = tabs[0]
const tabEls = {}

const setActive = tab => {
  activeTab = tab
  tabs.forEach(t => { if (tabEls[t.key]) tabEls[t.key].setAttribute("style", t.key === tab.key ? TAB_ON(t.color) : TAB_OFF(t.color)) })
  renderTab(tab, 0, zone)
}

for (const tab of tabs) {
  const btn = tabBar.createEl("button", {attr:{style: tab.key === activeTab.key ? TAB_ON(tab.color) : TAB_OFF(tab.color)}})
  btn.textContent = tab.icon + " " + tab.label + (tab.items.length > 0 ? " " + tab.items.length : "")
  btn.onclick = () => setActive(tab)
  tabEls[tab.key] = btn
}

renderTab(activeTab, 0, zone)
```

## ✅ Tâches

```dataviewjs
// ── Calendrier personnalisé ──────────────────────────────────────────────
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

// ── Barre supérieure tâches ──────────────────────────────────────────────
const BTN_TASK = "padding:5px 12px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;color:var(--text-normal);font-family:inherit;"
const topBarTasks = this.container.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"}})

const btnNewTask = topBarTasks.createEl("button", {attr:{style:BTN_TASK}})
btnNewTask.textContent = "➕ Tâche rapide"
btnNewTask.onclick = () => {
  const FIELD = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;"
  const LABEL = "font-size:0.75em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:320px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);display:flex;flex-direction:column;gap:11px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:1em;font-weight:700;"}}).textContent = "Nouvelle tâche"
  const g1 = box.createEl("div")
  g1.createEl("label", {attr:{style:LABEL}}).textContent = "Tâche"
  const nameInp = g1.createEl("input", {attr:{type:"text", placeholder:"Ex : Appeler le médecin", style:FIELD}})
  const g2 = box.createEl("div")
  g2.createEl("label", {attr:{style:LABEL}}).textContent = "Date d'échéance (optionnel)"
  const datePicker = mkDatePicker(g2, "", null, "Optionnel…")
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:4px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-normal);cursor:pointer;font-size:0.88em;font-family:inherit;"}})
  cancel.textContent = "Annuler"
  cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"}})
  ok.textContent = "Ajouter"
  ok.onclick = async () => {
    const name = nameInp.value.trim()
    if (!name) { nameInp.style.borderColor = "#d20f39"; nameInp.focus(); return }
    const due = datePicker.getValue() ? ` 📅 ${datePicker.getValue()}` : ""
    const line = `- [ ] ${name}${due}`
    const f = app.vault.getAbstractFileByPath("2 - Domaines/Tâches.md")
    if (f) {
      const content = await app.vault.read(f)
      await app.vault.modify(f, content.trimEnd() + "\n" + line + "\n")
      new Notice("✓ Tâche ajoutée !", 2000)
    }
    overlay.remove()
  }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => nameInp.focus(), 50)
}

const linkTaches = topBarTasks.createEl("a", {attr:{style:"font-size:0.8em;color:var(--text-muted);cursor:pointer;text-decoration:none;display:flex;align-items:center;gap:4px;"}})
linkTaches.textContent = "📋 Voir toutes les tâches ↗"
linkTaches.onclick = () => app.workspace.openLinkText("2 - Domaines/Tâches.md", "", false)

// ─────────────────────────────────────────────────────────────────────────
const pad = n => String(n).padStart(2,'0')
const now = new Date(); now.setHours(0,0,0,0)
const localToday = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`

const getDue = t => {
  if (t.due?.toFormat) return t.due.toFormat("yyyy-MM-dd")
  const m = (t.text || "").match(/\b(\d{4}-\d{2}-\d{2})\b/)
  return m ? m[1] : null
}

const allTasks = dv.pages('!"_Système"').file.tasks.where(t => !t.completed)

if (allTasks.length === 0) {
  dv.el("p", "Aucune tâche en cours 🎉", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}})
} else {
  const overdue  = allTasks.where(t => { const d = getDue(t); return d && d < localToday })
  const dueToday = allTasks.where(t => { const d = getDue(t); return d === localToday })
  const upcoming = allTasks.where(t => { const d = getDue(t); return d && d > localToday })
  const noDue    = allTasks.where(t => !getDue(t))

  const groups = [
    { key: "retard",      label: "🔴 En retard",   tasks: overdue,  color: "#d20f39" },
    { key: "aujourd'hui", label: "📅 Aujourd'hui",  tasks: dueToday, color: "#fe640b" },
    { key: "a-venir",     label: "🔜 À venir",      tasks: upcoming, color: "#1e66f5" },
    { key: "sans-date",   label: "📝 Sans date",    tasks: noDue,    color: "var(--text-muted)" },
  ]

  // Onglet actif par défaut : retard si non vide, sinon aujourd'hui, sinon premier
  let activeKey = (overdue.length > 0 ? "retard" : dueToday.length > 0 ? "aujourd'hui" : groups.find(g => g.tasks.length > 0)?.key)

  // ── Barre d'onglets ──────────────────────────────────────────────────────
  const tabBar = this.container.createEl("div", {attr:{style:"display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;"}})
  const listZone = this.container.createEl("div")

  const TAB_BASE    = "padding:5px 12px;border-radius:20px;border:1px solid;cursor:pointer;font-size:0.82em;font-weight:600;transition:all 0.15s;"
  const TAB_ACTIVE  = color => `${TAB_BASE}background:${color};color:#fff;border-color:${color};`
  const TAB_INACTIVE = color => `${TAB_BASE}background:transparent;color:${color};border-color:${color};opacity:0.6;`

  const tabEls = {}

  // ── Cochage direct ───────────────────────────────────────────────────────
  const checkTask = async task => {
    const f = app.vault.getAbstractFileByPath(task.path)
    if (!f) return
    const raw = await app.vault.read(f)
    const lines = raw.split('\n')
    const target = task.text.trim()
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].match(/^(\s*)-\s\[ \]/) && lines[i].includes(target)) {
        lines[i] = lines[i].replace('- [ ]', '- [x]')
        await app.vault.modify(f, lines.join('\n'))
        new Notice("✓ Tâche cochée !", 2000)
        return
      }
    }
  }

  // ── Rendu d'une liste de tâches ──────────────────────────────────────────
  const renderTasks = (tasks, color, page = 0) => {
    listZone.empty()
    if (tasks.length === 0) {
      listZone.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;margin:4px 0;"}}).textContent = "Aucune tâche dans cette catégorie."
      return
    }
    const PAGE_SIZE = 10
    const totalPages = Math.ceil(tasks.length / PAGE_SIZE)
    const pageTasks = tasks.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
    const ul = listZone.createEl("ul", {attr:{style:"list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:4px;"}})
    pageTasks.forEach(task => {
      const li = ul.createEl("li", {attr:{style:"display:flex;align-items:flex-start;gap:8px;padding:5px 6px;border-radius:6px;"}})
      li.onmouseenter = () => li.style.background = "var(--background-secondary)"
      li.onmouseleave = () => li.style.background = ""

      const cb = li.createEl("input", {attr:{type:"checkbox",style:"margin-top:2px;flex-shrink:0;cursor:pointer;accent-color:" + color + ";"}})
      cb.checked = false
      cb.onclick = async e => {
        e.stopPropagation()
        cb.disabled = true
        li.style.opacity = "0.4"
        await checkTask(task)
      }

      const textWrap = li.createEl("div", {attr:{style:"flex:1;min-width:0;"}})
      const taskText = task.text.replace(/\b\d{4}-\d{2}-\d{2}\b/g, "").replace(/\s+$/, "")
      const span = textWrap.createEl("span", {attr:{style:"font-size:0.88em;color:var(--text-normal);"}})
      span.textContent = taskText

      const due = getDue(task)
      const meta = textWrap.createEl("div", {attr:{style:"display:flex;gap:8px;align-items:center;margin-top:1px;"}})
      if (due) {
        meta.createEl("span", {attr:{style:"font-size:0.75em;color:" + color + ";font-weight:600;"}}).textContent = "📅 " + due
      }
      const src = textWrap.createEl("a", {attr:{style:"font-size:0.75em;color:var(--text-muted);cursor:pointer;text-decoration:none;"}})
      src.textContent = "↗ " + task.path.split("/").pop().replace(".md","")
      src.onclick = () => app.workspace.openLinkText(task.path, "", false)
      meta.appendChild(src)
    })
    if (totalPages > 1) {
      const BTN_PAG = "padding:4px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.8em;color:var(--text-normal);font-family:inherit;"
      const footer = listZone.createEl("div", {attr:{style:"display:flex;align-items:center;justify-content:space-between;margin-top:10px;padding-top:8px;border-top:1px solid var(--background-modifier-border);"}})
      const prev = footer.createEl("button", {attr:{style:BTN_PAG + (page === 0 ? "opacity:0.4;" : "")}})
      prev.textContent = "← Préc."
      prev.disabled = page === 0
      prev.onclick = () => renderTasks(tasks, color, page - 1)
      footer.createEl("span", {attr:{style:"font-size:0.8em;color:var(--text-muted);"}}).textContent = `${page * PAGE_SIZE + 1}-${Math.min((page + 1) * PAGE_SIZE, tasks.length)} / ${tasks.length} tâches`
      const next = footer.createEl("button", {attr:{style:BTN_PAG + (page === totalPages - 1 ? "opacity:0.4;" : "")}})
      next.textContent = "Suiv. →"
      next.disabled = page === totalPages - 1
      next.onclick = () => renderTasks(tasks, color, page + 1)
    }
  }

  // ── Construction des onglets ─────────────────────────────────────────────
  const setActive = key => {
    activeKey = key
    groups.forEach(g => {
      if (tabEls[g.key]) tabEls[g.key].setAttribute("style", key === g.key ? TAB_ACTIVE(g.color) : TAB_INACTIVE(g.color))
    })
    const g = groups.find(x => x.key === key)
    if (g) renderTasks(g.tasks, g.color, 0)
  }

  groups.forEach(g => {
    const btn = tabBar.createEl("button", {attr:{style: activeKey === g.key ? TAB_ACTIVE(g.color) : TAB_INACTIVE(g.color)}})
    btn.textContent = g.label + (g.tasks.length > 0 ? "  " + g.tasks.length : "")
    btn.onclick = () => setActive(g.key)
    tabEls[g.key] = btn
  })

  // Rendu initial
  const initGroup = groups.find(g => g.key === activeKey)
  if (initGroup) renderTasks(initGroup.tasks, initGroup.color, 0)
}
```

---

## 📥 Inbox

```dataview
LIST
FROM "0 - Inbox"
SORT file.ctime DESC
LIMIT 10
```

## 📦 Commandes

```dataviewjs
const { Menu, Notice } = require('obsidian')

// ── Calendrier personnalisé ───────────────────────────────────────────────
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

const BTN = "padding:5px 12px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;color:var(--text-normal);font-family:inherit;"

// ── Formulaire générique ──────────────────────────────────────────────
const showForm = (title, fields, onSubmit) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:300px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 18px;font-size:1em;font-weight:700;"}}).textContent = title
  const inputs = {}
  for (const [key, cfg] of Object.entries(fields)) {
    const g = box.createEl("div", {attr:{style:"margin-bottom:12px;"}})
    g.createEl("label", {attr:{style:"font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"}}).textContent = cfg.label
    const inp = g.createEl("input", {attr:{type:cfg.type||"text",placeholder:cfg.placeholder||"",value:String(cfg.value||""),style:"width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.92em;box-sizing:border-box;"}})
    inputs[key] = inp
  }
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:16px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);"}})
  cancel.textContent = "Annuler"
  cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = () => { overlay.remove(); onSubmit(Object.fromEntries(Object.entries(inputs).map(([k,v]) => [k,v.value.trim()]))) }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => Object.values(inputs)[0]?.focus(), 50)
}

// ── Couleurs statuts commandes ────────────────────────────────────────
const CMD_COLORS = { "commandé":"#fe640b", "expédié":"#1e66f5", "livré":"#40a02b", "annulé":"#7a766e" }
const CMD_LIST   = ["commandé","expédié","livré","annulé"]

// ── Bouton ➕ Nouvelle commande ─────────────────────────────────────
const topBar = this.container.createEl("div", {attr:{style:"display:flex;gap:8px;margin-bottom:14px;"}})
const btnNew = topBar.createEl("button", {attr:{style:BTN}})
btnNew.textContent = "➕ Nouvelle commande"
btnNew.onclick = () => {
  const today = new Date().toISOString().slice(0, 10)
  const FIELD = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;"
  const LABEL = "font-size:0.75em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"
  const mkField = (parent, label, placeholder = "", type = "text", value = "") => {
    const g = parent.createEl("div")
    g.createEl("label", {attr:{style:LABEL}}).textContent = label
    const inp = g.createEl("input", {attr:{type, placeholder, value, style:FIELD}})
    return inp
  }
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:360px;max-width:500px;width:92%;max-height:88vh;overflow-y:auto;box-shadow:0 8px 40px rgba(0,0,0,0.35);display:flex;flex-direction:column;gap:11px;"}})
  box.createEl("h3", {attr:{style:"margin:0;font-size:1em;font-weight:700;"}}).textContent = "Nouvelle commande"
  const nomInp      = mkField(box, "Nom de la commande", "ex: Commande Amazon du 17/04")
  const siteInp     = mkField(box, "Site / Vendeur", "ex: Amazon, AliExpress…")
  const commandeGrp = box.createEl("div")
  commandeGrp.createEl("label", {attr:{style:LABEL}}).textContent = "Commande passée le"
  const commandePicker = mkDatePicker(commandeGrp, today, null)
  const livraisonGrp = box.createEl("div")
  livraisonGrp.createEl("label", {attr:{style:LABEL}}).textContent = "Date de livraison estimée"
  const livraisonPicker = mkDatePicker(livraisonGrp, today, null)
  const numeroInp   = mkField(box, "N° de commande (optionnel)", "")
  // Articles
  const artLabel = box.createEl("div", {attr:{style:LABEL + "margin-bottom:6px;"}})
  artLabel.textContent = "Articles"
  const artZone = box.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;"}})
  const articleRows = []
  const totalEl = box.createEl("div", {attr:{style:"font-size:0.84em;color:var(--text-muted);text-align:right;min-height:1.2em;"}})
  const updateTotal = () => {
    const t = articleRows.reduce((s, r) => s + (parseFloat(r.qty.value)||0) * (parseFloat(r.price.value)||0), 0)
    totalEl.textContent = t > 0 ? `Total : ${t.toFixed(2)} €` : ""
  }
  const addRow = () => {
    const card = artZone.createEl("div", {attr:{style:"border:1px solid var(--background-modifier-border);border-radius:8px;padding:8px;display:flex;flex-direction:column;gap:5px;"}})
    const top = card.createEl("div", {attr:{style:"display:grid;grid-template-columns:1fr 54px 74px 22px;gap:5px;align-items:center;"}})
    const nameI  = top.createEl("input", {attr:{type:"text",  placeholder:"Nom de l'article", style:FIELD}})
    const qtyI   = top.createEl("input", {attr:{type:"number",placeholder:"Qté", value:"1",   style:FIELD}})
    const priceI = top.createEl("input", {attr:{type:"number",placeholder:"Prix €",            style:FIELD}})
    const del    = top.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1em;padding:0;line-height:1;"}})
    del.textContent = "✕"
    const urlI = card.createEl("input", {attr:{type:"text", placeholder:"URL du produit (optionnel) - https://…", style:FIELD + "font-size:0.82em;color:var(--text-muted);"}})
    const rowObj = {name:nameI, qty:qtyI, price:priceI, url:urlI}
    articleRows.push(rowObj)
    del.onclick = () => { if (articleRows.length > 1) { articleRows.splice(articleRows.indexOf(rowObj),1); card.remove(); updateTotal() } }
    qtyI.oninput = updateTotal; priceI.oninput = updateTotal
  }
  addRow()
  const addBtn = box.createEl("button",{attr:{style:"background:none;border:1px dashed var(--background-modifier-border);border-radius:7px;cursor:pointer;color:var(--text-muted);font-size:0.84em;padding:5px;text-align:center;font-family:inherit;"}})
  addBtn.textContent = "➕ Ajouter un article"
  addBtn.onclick = () => addRow()
  const btns = box.createEl("div",{attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:4px;"}})
  const cancelBtn = btns.createEl("button",{attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);font-family:inherit;"}})
  cancelBtn.textContent = "Annuler"; cancelBtn.onclick = () => overlay.remove()
  const okBtn = btns.createEl("button",{attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"}})
  okBtn.textContent = "Enregistrer"
  okBtn.onclick = async () => {
    const nom = nomInp.value.trim(); if (!nom) { nomInp.style.borderColor="red"; return }
    const site = siteInp.value.trim()
    const dateCommande = commandePicker.getValue() || today
    const livraison = livraisonPicker.getValue(), numero = numeroInp.value.trim()
    const arts = articleRows.map(r=>({
      name:r.name.value.trim(), qty:parseFloat(r.qty.value)||1,
      price:parseFloat(r.price.value)||0, url:r.url.value.trim()
    })).filter(a=>a.name)
    const total = arts.reduce((s,a)=>s+a.qty*a.price, 0)
    const artLines = arts.length ? [
      "| Article | Qté | Prix unitaire | Total |",
      "|---------|-----|---------------|-------|",
      ...arts.map(a=>{
        const nom_cell = a.url ? `[${a.name}](${a.url})` : a.name
        return `| ${nom_cell} | ${a.qty} | ${a.price>0?a.price.toFixed(2)+" €":"-"} | ${a.qty*a.price>0?(a.qty*a.price).toFixed(2)+" €":"-"} |`
      })
    ] : ["*(aucun article renseigné)*"]
const EDIT_BLOCK_LINES = [
  '```dataviewjs',
  'const p = dv.current()',
  'const file = app.vault.getAbstractFileByPath(p.file.path)',
  '',
  '// ── Helpers ──────────────────────────────────────────────',
  'const getDateStr = val => {',
  '  if (!val) return ""',
  '  if (val && val.toFormat) return val.toFormat("yyyy-MM-dd")',
  '  return String(val).slice(0, 10)',
  '}',
  'const fmtDate = str => {',
  '  if (!str) return "-"',
  '  const [y, m, d] = str.split("-")',
  '  return `${d}/${m}/${y}`',
  '}',
  '',
  '// ── Date picker ───────────────────────────────────────────',
  'const mkDatePicker = (parent, initVal, onChange) => {',
  '  const MONTHS = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]',
  '  let cur = initVal ? new Date(initVal + "T12:00:00") : new Date()',
  '  cur.setHours(12, 0, 0, 0)',
  '  let selected = initVal || null',
  '  const wrap = parent.createDiv()',
  '  wrap.style.cssText = "position:relative;display:inline-block;"',
  '  const inp = wrap.createEl("input")',
  '  inp.type = "text"; inp.readOnly = true',
  '  inp.value = initVal ? fmtDate(initVal) : ""',
  '  inp.placeholder = "jj/mm/aaaa"',
  '  inp.style.cssText = "width:130px;padding:6px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);cursor:pointer;font-size:0.88em;"',
  '  const pop = wrap.createDiv()',
  '  pop.style.cssText = "display:none;position:absolute;top:calc(100% + 4px);left:0;z-index:9999;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,0.15);padding:12px;width:240px;"',
  '  const buildCal = () => {',
  '    pop.empty()',
  '    const hdr = pop.createDiv()',
  '    hdr.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"',
  '    const prev = hdr.createEl("button"); prev.textContent = "‹"',
  '    prev.style.cssText = "background:none;border:none;cursor:pointer;font-size:1.3em;color:var(--text-muted);padding:0 6px;"',
  '    const lbl = hdr.createDiv()',
  '    lbl.style.cssText = "font-weight:600;font-size:0.88em;color:var(--text-normal);"',
  '    lbl.textContent = `${MONTHS[cur.getMonth()]} ${cur.getFullYear()}`',
  '    const next = hdr.createEl("button"); next.textContent = "›"',
  '    next.style.cssText = "background:none;border:none;cursor:pointer;font-size:1.3em;color:var(--text-muted);padding:0 6px;"',
  '    prev.onclick = e => { e.stopPropagation(); cur = new Date(cur.getFullYear(), cur.getMonth() - 1, 1, 12); buildCal() }',
  '    next.onclick = e => { e.stopPropagation(); cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1, 12); buildCal() }',
  '    const grid = pop.createDiv()',
  '    grid.style.cssText = "display:grid;grid-template-columns:repeat(7,1fr);gap:2px;text-align:center;"',
  '    for (const d of ["L","M","M","J","V","S","D"]) {',
  '      const h = grid.createDiv(); h.textContent = d',
  '      h.style.cssText = "font-size:0.7em;color:var(--text-muted);font-weight:600;padding:2px 0;"',
  '    }',
  '    const y = cur.getFullYear(), mo = cur.getMonth()',
  '    const first = new Date(y, mo, 1).getDay()',
  '    const offset = (first === 0 ? 6 : first - 1)',
  '    const days = new Date(y, mo + 1, 0).getDate()',
  '    for (let i = 0; i < offset; i++) grid.createDiv()',
  '    for (let d = 1; d <= days; d++) {',
  '      const dateStr = `${y}-${String(mo + 1).padStart(2,"0")}-${String(d).padStart(2,"0")}`',
  '      const cell = grid.createEl("button"); cell.textContent = d',
  '      const isSel = dateStr === selected',
  '      cell.style.cssText = `background:${isSel ? "#8839ef" : "none"};color:${isSel ? "#fff" : "var(--text-normal)"};border:none;border-radius:4px;cursor:pointer;font-size:0.82em;padding:4px 2px;`',
  '      cell.onclick = e => {',
  '        e.stopPropagation(); selected = dateStr',
  '        inp.value = fmtDate(dateStr); pop.style.display = "none"',
  '        if (onChange) onChange(dateStr); buildCal()',
  '      }',
  '    }',
  '  }',
  '  inp.onclick = e => {',
  '    e.stopPropagation()',
  '    const isOpen = pop.style.display !== "none"',
  '    pop.style.display = isOpen ? "none" : "block"',
  '    if (!isOpen) buildCal()',
  '  }',
  '  document.addEventListener("click", () => { pop.style.display = "none" })',
  '  return { getValue: () => selected, setValue: v => { selected = v; inp.value = v ? fmtDate(v) : "" } }',
  '}',
  '',
  '// ── Couleurs statut ───────────────────────────────────────',
  'const CMD_COLORS = {',
  '  "commandé": { bg: "rgba(30,102,245,0.12)",  color: "#1e66f5" },',
  '  "expédié":  { bg: "rgba(223,142,29,0.15)",  color: "#df8e1d" },',
  '  "livré":    { bg: "rgba(64,160,43,0.12)",   color: "#40a02b" },',
  '  "annulé":   { bg: "rgba(210,15,57,0.10)",   color: "#d20f39" },',
  '}',
  'const FIELD = "padding:6px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:0.88em;width:100%;box-sizing:border-box;"',
  'const LABEL = "display:block;font-size:0.78em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;"',
  'const BTN_S = "padding:8px 18px;border:none;border-radius:6px;background:#8839ef;color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"',
  'const BTN_G = "padding:8px 18px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.88em;"',
  '',
  '// ── Action bar ────────────────────────────────────────────',
  'const bar = dv.container.createDiv()',
  'bar.style.cssText = "display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 14px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;margin:12px 0 18px;"',
  'const statut = p.statut || "commandé"',
  'const sCol = CMD_COLORS[statut] || CMD_COLORS["commandé"]',
  'const badge = bar.createDiv()',
  'badge.textContent = statut.charAt(0).toUpperCase() + statut.slice(1)',
  'badge.style.cssText = `padding:4px 12px;border-radius:12px;font-size:0.82em;font-weight:700;background:${sCol.bg};color:${sCol.color};`',
  'const sep = () => { const s = bar.createDiv(); s.style.cssText = "width:1px;height:18px;background:var(--background-modifier-border);margin:0 2px;"; return s }',
  'sep()',
  'const chip = (icon, val) => {',
  '  const c = bar.createDiv()',
  '  c.style.cssText = "display:flex;align-items:center;gap:4px;font-size:0.82em;color:var(--text-muted);"',
  '  c.createSpan().textContent = icon',
  '  const v = c.createSpan(); v.textContent = val || "-"',
  '  v.style.cssText = "color:var(--text-normal);font-weight:500;"',
  '}',
  'chip("🏪", p.site); sep()',
  'chip("📅", fmtDate(getDateStr(p.date_commande))); sep()',
  'chip("📦", fmtDate(getDateStr(p["date_livraison_estimée"]))); sep()',
  'chip("💶", p.montant ? p.montant + " €" : "-")',
  'const spacer = bar.createDiv(); spacer.style.cssText = "flex:1;"',
  'const editBtn = bar.createEl("button")',
  'editBtn.textContent = "✏ Modifier"; editBtn.style.cssText = BTN_S',
  '',
  '// ── Modal édition ─────────────────────────────────────────',
  'const openEditModal = () => {',
  '  const overlay = document.body.createDiv()',
  '  overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:10000;display:flex;align-items:center;justify-content:center;"',
  '  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }',
  '  const modal = overlay.createDiv()',
  '  modal.style.cssText = "background:var(--background-primary);border-radius:14px;padding:28px 28px 22px;width:480px;max-width:95vw;max-height:90vh;overflow-y:auto;display:flex;flex-direction:column;gap:16px;"',
  '  modal.onclick = e => e.stopPropagation()',
  '  const ttl = modal.createEl("h3")',
  '  ttl.textContent = "Modifier la commande"',
  '  ttl.style.cssText = "margin:0 0 4px;font-size:1em;color:var(--text-normal);"',
  '  const row2 = (a, b) => { const r = modal.createDiv(); r.style.cssText = "display:grid;grid-template-columns:1fr 1fr;gap:12px;"; r.append(a, b); return r }',
  '  const field = (label, inp) => {',
  '    const g = document.createElement("div")',
  '    const l = document.createElement("label"); l.textContent = label; l.style.cssText = LABEL',
  '    g.append(l, inp); return g',
  '  }',
  '  // Nom fichier',
  '  const nomInp = document.createElement("input")',
  '  nomInp.type = "text"; nomInp.value = p.file.name; nomInp.style.cssText = FIELD',
  '  modal.append(field("Nom du fichier", nomInp))',
  '  // Site + Statut',
  '  const siteInp = document.createElement("input")',
  '  siteInp.type = "text"; siteInp.value = p.site || ""; siteInp.style.cssText = FIELD',
  '  const statutSel = document.createElement("select"); statutSel.style.cssText = FIELD',
  '  for (const [val, lbl] of [["commandé","🛒 Commandé"],["expédié","📦 Expédié"],["livré","✅ Livré"],["annulé","❌ Annulé"]]) {',
  '    const opt = document.createElement("option"); opt.value = val; opt.textContent = lbl',
  '    if (val === (p.statut || "commandé")) opt.selected = true',
  '    statutSel.append(opt)',
  '  }',
  '  modal.append(row2(field("Site", siteInp), field("Statut", statutSel)))',
  '  // Dates',
  '  const dCmdG = document.createElement("div")',
  '  const dCmdL = document.createElement("label"); dCmdL.textContent = "Date de commande"; dCmdL.style.cssText = LABEL',
  '  dCmdG.append(dCmdL)',
  '  const cmdPicker = mkDatePicker(dCmdG, getDateStr(p.date_commande), null)',
  '  const dLivG = document.createElement("div")',
  '  const dLivL = document.createElement("label"); dLivL.textContent = "Livraison estimée"; dLivL.style.cssText = LABEL',
  '  dLivG.append(dLivL)',
  '  const livPicker = mkDatePicker(dLivG, getDateStr(p["date_livraison_estimée"]), null)',
  '  modal.append(row2(dCmdG, dLivG))',
  '  // Numéro + Montant',
  '  const numInp = document.createElement("input")',
  '  numInp.type = "text"; numInp.value = p["numéro_commande"] || ""; numInp.style.cssText = FIELD',
  '  const montantInp = document.createElement("input")',
  '  montantInp.type = "number"; montantInp.step = "0.01"; montantInp.value = p.montant || ""; montantInp.style.cssText = FIELD',
  '  modal.append(row2(field("N° de commande", numInp), field("Montant (€)", montantInp)))',
  '  // Boutons',
  '  const bRow = modal.createDiv()',
  '  bRow.style.cssText = "display:flex;gap:10px;justify-content:flex-end;margin-top:4px;"',
  '  const cancelBtn = bRow.createEl("button"); cancelBtn.textContent = "Annuler"; cancelBtn.style.cssText = BTN_G',
  '  cancelBtn.onclick = () => overlay.remove()',
  '  const saveBtn = bRow.createEl("button"); saveBtn.textContent = "💾 Enregistrer"; saveBtn.style.cssText = BTN_S',
  '  saveBtn.onclick = async () => {',
  '    const newName = nomInp.value.trim()',
  '    await app.fileManager.processFrontMatter(file, f => {',
  '      f.site = siteInp.value.trim()',
  '      f.statut = statutSel.value',
  '      f.date_commande = cmdPicker.getValue() || getDateStr(p.date_commande)',
  '      f["date_livraison_estimée"] = livPicker.getValue() || getDateStr(p["date_livraison_estimée"])',
  '      f["numéro_commande"] = numInp.value.trim()',
  '      f.montant = montantInp.value ? parseFloat(montantInp.value) : p.montant',
  '    })',
  '    if (newName && newName !== p.file.name) {',
  '      const newPath = p.file.path.replace(p.file.name, newName)',
  '      await app.fileManager.renameFile(file, newPath)',
  '    }',
  '    overlay.remove()',
  '    new Notice("Commande mise à jour ✓")',
  '  }',
  '  document.body.append(overlay)',
  '}',
  '',
  'editBtn.onclick = () => openEditModal()',
  '```'
]

    const folder = "2 - Domaines/Commandes"
    const fname = nom.replace(/[\\/:*?"<>|]/g,"-").trim()
    const path = `${folder}/${fname}.md`
    const lines = [
      "---","type: commande",
      `site: "${site}"`,
      `montant: ${total>0?total.toFixed(2):""}`,
      `date_commande: ${dateCommande}`,`date_livraison_estimée: ${livraison}`,
      `numéro_commande: "${numero}"`,`statut: "commandé"`,"obsidianUIMode: preview","tags: [commande]","---","",
      `# ${nom}`,"", ...EDIT_BLOCK_LINES, "",
      "## 📦 Articles commandés","",
      ...artLines,"",
      total>0 ? `**Total : ${total.toFixed(2)} €**` : "","",
      "## 📍 Suivi","",
      `- Site : ${site||"-"}`,
      numero ? `- N° de commande : ${numero}` : "- N° de commande : ",
      "","## 🔄 Historique","",`- ${today} - Commande passée`,""
    ]
    overlay.remove()
    try {
      if (!app.vault.getAbstractFileByPath(folder)) await app.vault.createFolder(folder)
      if (app.vault.getAbstractFileByPath(path)) { new Notice("⚠ Une commande avec ce nom existe déjà.",3000); return }
      await app.vault.create(path, lines.join("\n"))
      new Notice("✓ Commande créée !",2000)
    } catch(e) { new Notice("Erreur : "+e.message,4000) }
  }
  overlay.onclick = e => { if (e.target===overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key==="Escape") overlay.remove() }
  setTimeout(()=>nomInp.focus(),50)
}

// ── Table des commandes en attente ────────────────────────────────────
const commandes = dv.pages('"2 - Domaines/Commandes"')
  .where(p => p.type === "commande" && p.statut !== "livré" && p.statut !== "annulé")
  .sort(p => p.date_commande, "desc")

if (commandes.length === 0) {
  this.container.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;margin:4px 0;"}}).textContent = "Aucune commande en attente."
} else {
  const table = this.container.createEl("table", {attr:{style:"width:100%;border-collapse:collapse;font-size:0.87em;"}})
  const hrow = table.createEl("thead").createEl("tr")
  for (const h of ["Commande","Site","Statut","Livraison","Montant"]) {
    hrow.createEl("th", {attr:{style:"text-align:left;padding:6px 10px;font-size:0.78em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:1px solid var(--background-modifier-border);"}}).textContent = h
  }
  const tbody = table.createEl("tbody")
  for (const p of commandes) {
    const tr = tbody.createEl("tr")
    tr.onmouseenter = () => tr.style.background = "var(--background-secondary)"
    tr.onmouseleave = () => tr.style.background = ""

    const a = tr.createEl("td", {attr:{style:"padding:7px 10px;"}}).createEl("a", {text:p.file.name, href:p.file.path, cls:"internal-link"})
    a.setAttribute("data-href", p.file.path)
    a.style.cssText = "color:var(--text-normal);text-decoration:none;font-weight:500;"

    const siteCell = tr.createEl("td", {attr:{style:"padding:7px 10px;"}})
    if (p.site_url) {
      const sl = siteCell.createEl("a", {attr:{href:p.site_url, style:"color:var(--text-accent);text-decoration:none;font-size:0.9em;"}})
      sl.textContent = p.site || p.site_url
    } else { siteCell.style.color="var(--text-muted)"; siteCell.textContent = p.site || "-" }

    const color = CMD_COLORS[p.statut] || "var(--text-muted)"
    const badge = tr.createEl("td", {attr:{style:"padding:7px 10px;"}}).createEl("span", {attr:{style:`background:${color};color:#fff;padding:2px 9px;border-radius:10px;font-size:0.82em;font-weight:600;cursor:pointer;user-select:none;`}})
    badge.textContent = p.statut || "-"
    badge.onclick = e => {
      const f = app.vault.getAbstractFileByPath(p.file.path)
      const menu = new Menu()
      CMD_LIST.forEach(s => menu.addItem(it => { it.setTitle((s === p.statut ? "✓ " : "  ") + s); it.onClick(() => app.fileManager.processFrontMatter(f, fm => { fm.statut = s })) }))
      menu.showAtMouseEvent(e)
    }

    const livr = p.date_livraison_estimée
    const livrStr = livr?.toFormat ? livr.toFormat("dd/MM/yyyy") : (livr ? String(livr).slice(0,10) : "-")
    tr.createEl("td", {attr:{style:"padding:7px 10px;color:var(--text-muted);font-size:0.85em;"}}).textContent = livrStr
    tr.createEl("td", {attr:{style:"padding:7px 10px;color:var(--text-muted);"}}).textContent = p.montant ? p.montant + " €" : "-"
  }
}
```

## 🕒 Notes récentes

```dataview
TABLE WITHOUT ID file.link AS "Note", choice(type,type,"-") AS "Type", dateformat(file.mtime,"dd/MM HH:mm") AS "Modifié"
FROM -"_Système" AND -"Dashboard"
WHERE type != "dashboard"
SORT file.mtime DESC
LIMIT 10
```

## ⚡ Raccourcis

| Action | Raccourci |
|---|---|
| Nouvelle note | `Ctrl+P` → QuickAdd |
| Note du jour | `Ctrl+Shift+D` |
| Recherche rapide | `Ctrl+O` |
| Graphe | `Ctrl+G` |
| Palette de commandes | `Ctrl+P` |
