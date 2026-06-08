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
const nTotal  = dv.pages('!"_Système"').where(p => p.type !== "dashboard").length
const bar = dv.container.createDiv()
bar.style.cssText = "display:flex;align-items:center;gap:12px;padding:10px 18px;margin:10px 0 20px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;font-size:0.87em;flex-wrap:wrap;"
for (let i=0; i<2; i++) {
  if (i>0) { const sep=bar.createEl("span"); sep.style.cssText="color:var(--text-faint);font-size:1.1em;line-height:1;"; sep.textContent="·" }
  const [val,lbl] = i===0 ? [nMedias,"médias en cours"] : [nTotal,"notes au total"]
  const s=bar.createEl("span"); const b=s.createEl("strong"); b.style.cssText="color:#5b8db8;font-size:1.08em;margin-right:4px;"; b.textContent=String(val); s.appendChild(document.createTextNode(lbl))
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

const sections = [
  { icon:"🎬", name:"Films & Animés", link:"MOC - Films & Animés", color:"#e07b5a", bg:"rgba(224,123,90,0.09)",
    count: dv.pages('"2 - Domaines/Médias"').where(p=>["animé","film"].includes(p.type)&&p.statut==="en cours").length+" en cours" },
  { icon:"📺", name:"Séries TV",      link:"MOC - Séries",         color:"#df8e1d", bg:"rgba(223,142,29,0.09)",
    count: dv.pages('"2 - Domaines/Médias/Séries"').where(p=>p.type==="série"&&p.statut==="en cours").length+" en cours" },
  { icon:"📖", name:"Lectures",       link:"MOC - Lectures",        color:"#8878c3", bg:"rgba(136,120,195,0.09)",
    count: dv.pages('"2 - Domaines/Médias"').where(p=>["manga","manwha","livre"].includes(p.type)&&p.statut==="en cours").length+" en cours" },
  { icon:"🎮", name:"Jeux Vidéo",     link:"MOC - Jeux Vidéo",      color:"#4a8fa8", bg:"rgba(74,143,168,0.09)",
    count: dv.pages('"2 - Domaines/Médias/Jeux Vidéo"').where(p=>p.statut==="en cours").length+" en cours" },
  { icon:"🛒", name:"Commandes",      link:"MOC - Commandes",        color:"#fe640b", bg:"rgba(254,100,11,0.09)",
    count: dv.pages('"2 - Domaines/Commandes"').where(p=>p.type==="commande"&&p.statut!=="livré"&&p.statut!=="annulé").length+" en attente" },
  { icon:"💰", name:"Finances",       link:"💰 Finances",            color:"#40a02b", bg:"rgba(64,160,43,0.09)",
    count: _financeCount },
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
