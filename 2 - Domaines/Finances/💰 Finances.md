---
type: finances
created: 2026-06-01
tags:
  - finances
  - budget
  - suivi
cssclasses:
  - media-page
obsidianUIMode: preview
compte_commandes: courant
comptes: []
budgets:
  - categorie: 📦 Commandes
    montant: 0
categories:
  - nom: 💵 Revenus
    type: revenu
  - nom: 💵 Salaire
    type: revenu
  - nom: 💵 Remboursement out
    type: dépense
  - nom: 💰 Économies
    type: épargne
  - nom: 💸 Retrait économies
    type: épargne-retrait
  - nom: 🛒 Alimentation
    type: dépense
  - nom: 🎮 Jeux & Loisirs
    type: dépense
  - nom: 📺 Abonnements
    type: dépense
  - nom: 🚗 Transport
    type: dépense
  - nom: 🏠 Logement
    type: dépense
  - nom: 💊 Santé
    type: dépense
  - nom: 🎓 Formation
    type: dépense
  - nom: 🔧 Divers
    type: dépense
  - nom: 🔄 Transfert interne in
    type: revenu
  - nom: 🔄 Transfert interne out
    type: dépense
  - nom: 💸 Envoi d'argent
    type: dépense
  - nom: 🔙 Avoir / Remboursement achat
    type: avoir
  - nom: 💵 Remboursement in
    type: revenu
  - nom: 🏧 Retrait espèces
    type: dépense
  - nom: 💇 Coiffure & Beauté
    type: dépense
  - nom: 🏋️ Sport & Activités
    type: dépense
  - nom: 🎁 Dons & Cadeaux
    type: dépense
  - nom: 🎓 Bourse & Aides sociales
    type: revenu
  - nom: 💳 Frais bancaires
    type: dépense
devise_systeme: EUR
---

# 💰 Finances

```dataviewjs
// ════════════════════════════════════════════════════════════════
// 💰 FINANCES - Suivi des dépenses, revenus et épargne
// ════════════════════════════════════════════════════════════════

const { Notice } = require('obsidian')
const _p = dv.current()
if (!_p?.file) {
  const _rr=(_n=0)=>{ if(_n>25)return; setTimeout(()=>{ const _nf=app.vault.getAbstractFileByPath(dv.currentFilePath); (_nf&&app.plugins.plugins['dataview']?.api?.page(dv.currentFilePath)?.file)?app.workspace.activeLeaf?.openFile(_nf):_rr(_n+1); },200); }; _rr(); return
}
const _file = app.vault.getAbstractFileByPath(_p.file.path)

// ════ HELPERS ════════════════════════════════════════════════════
// Convertit n'importe quelle valeur date en "YYYY-MM-DD" LOCAL (pas UTC)
const getDateStr = v => {
  if (!v) return ""
  if (typeof v === "string") return v.slice(0,10)
  if (v?.toFormat) return v.toFormat("yyyy-MM-dd")    // Luxon DateTime (DataviewJS)
  if (v instanceof Date) {
    const y=v.getFullYear(), mo=String(v.getMonth()+1).padStart(2,"0"), d=String(v.getDate()).padStart(2,"0")
    return `${y}-${mo}-${d}`
  }
  return String(v).slice(0,10)
}
// Date locale en string YYYY-MM-DD (évite le décalage UTC de .toISOString())
const localStr = d => {
  const y=d.getFullYear(), mo=String(d.getMonth()+1).padStart(2,"0"), dy=String(d.getDate()).padStart(2,"0")
  return `${y}-${mo}-${dy}`
}
const fmtDateFr = iso => {
  if (!iso) return "-"
  const [y,m,d] = String(iso).slice(0,10).split("-")
  return `${d}/${m}/${y}`
}
const fmtEur = v => Math.abs(v).toLocaleString("fr-FR", {minimumFractionDigits:2, maximumFractionDigits:2}) + " €"
const fmtSigned = v => (v >= 0 ? "+" : "-") + fmtEur(v)
const FX_SYMS = {USD:"USD", CAD:"CAD", XOF:"F CFA"}
// Crée un élément montant : ligne principale (devise choisie) + ligne EUR si devise ≠ EUR
const mkAmountEl = (parent, eurValue, opts={}) => {
  // opts: { signed, abs, color, fontSize, subSize }
  const val = opts.abs ? Math.abs(eurValue) : eurValue
  const fmt2 = v => Math.abs(v).toLocaleString("fr-FR",{minimumFractionDigits:2,maximumFractionDigits:2})
  const sign = s => opts.signed ? (s>=0?"+":"-") : ""
  const eurStr = sign(val) + fmt2(val) + " €"
  const fs = opts.fontSize || "inherit"
  const ss = opts.subSize  || "0.72em"
  if (S_DEVISE === "EUR" || !FX_RATES[S_DEVISE]) {
    const el = parent.createEl("span",{attr:{style:`font-size:${fs};`}}); el.textContent = eurStr
    if (opts.color) el.style.color = opts.color
    el.classList.add('fin-amount')
    return el
  }
  const rate = FX_RATES[S_DEVISE]
  const conv = val * rate
  const sym  = FX_SYMS[S_DEVISE]||S_DEVISE
  const convStr = sign(conv) + fmt2(conv) + " " + sym
  const wrap = parent.createEl("span",{attr:{style:"display:inline-flex;flex-direction:column;gap:1px;"}})
  wrap.classList.add('fin-amount')
  const m = wrap.createEl("span",{attr:{style:`font-size:${fs};`}}); m.textContent = convStr
  if (opts.color) m.style.color = opts.color
  wrap.createEl("span",{attr:{style:`font-size:${ss};color:var(--text-muted);font-weight:400;`}}).textContent = eurStr
  return wrap
}
const MONTHS_LONG = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
const DFR = ["Lu","Ma","Me","Je","Ve","Sa","Di"]

// ════ CONFIG DEPUIS FRONTMATTER ═══════════════════════════════════
let CFG_COMPTES    = Array.isArray(_p.comptes)      ? _p.comptes      : []
let CFG_BUDGETS    = Array.isArray(_p.budgets)      ? _p.budgets      : []
const COMPTE_CMD     = _p.compte_commandes || (CFG_COMPTES[0]?.id || "courant")

// ════ FICHIERS ANNUELS ════════════════════════════════════════════
const FINANCES_DIR = "2 - Domaines/Finances/Transactions"

// Charge les transactions :
// Lecture depuis les 💰 YYYY.json (relevés bancaires + saisies manuelles)
// Les transactions manuelles ont _manual:true dans le JSON.
const loadYearlyTx = async () => {
  const txs = []
  const jsonFiles = app.vault.getFiles().filter(f =>
    f.path.startsWith(FINANCES_DIR + "/") && /^💰 \d{4}\.json$/.test(f.name)
  )
  for (const jf of jsonFiles.sort((a,b) => a.name < b.name ? -1 : 1)) {
    try {
      const raw = await app.vault.read(jf)
      const data = JSON.parse(raw)
      for (const t of data) {
        txs.push({
          date:      getDateStr(t.date),
          label:     t.label     || '',
          montant:   parseFloat(t.montant) || 0,
          categorie: t.categorie || '',
          type:      t.type      || '',
          compte:    t.compte    || '',
          _auto:     !t._manual,   // relevé bancaire → _auto:true ; saisie manuelle → _auto:false
          _yearFile: jf.path,
        })
      }
    } catch(e) { console.error('loadYearlyTx', jf.path, e) }
  }
  return txs.sort((a,b) => a.date < b.date ? -1 : 1)
}

// Transactions chargées (auto JSON + manuelles YAML)
let TX_MANUEL = await loadYearlyTx()

// ════ COMMANDES AUTO ══════════════════════════════════════════════
const _cmdLivrees = dv.pages('"2 - Domaines/Commandes"')
  .where(c => c.type === "commande" && c.statut === "livré" && c.montant)
  .array()
const _cmdEnAttente = dv.pages('"2 - Domaines/Commandes"')
  .where(c => c.type === "commande" && (c.statut === "commandé" || c.statut === "expédié") && c.montant)
  .array()

const TX_CMD = _cmdLivrees.map(c => ({
  date:      getDateStr(c.date_commande),
  label:     c.file.name,
  montant:   -Math.abs(parseFloat(c.montant)||0),
  categorie: "📦 Commandes",
  type:      "dépense",
  compte:    COMPTE_CMD,
  _auto:     true,
  _path:     c.file.path
})).filter(t => t.date)

// ════ FUSION TOUTES TRANSACTIONS ══════════════════════════════════
// TX_CMD exclu : les paiements sont déjà dans les relevés bancaires
// (double-comptage sinon). TX_CMD sert uniquement au suivi des commandes.
const rebuildAllTx = () => [...TX_MANUEL]
  .filter(t => t.date)
  .sort((a,b) => a.date < b.date ? -1 : 1)

let ALL_TX = rebuildAllTx()

// ════ CATEGORIES ══════════════════════════════════════════════════
let CFG_CATEGORIES = Array.isArray(_p.categories) ? _p.categories : []
let CATS_DEPENSE = CFG_CATEGORIES.filter(c=>c.type==="dépense").map(c=>c.nom)
let CATS_REVENU  = CFG_CATEGORIES.filter(c=>c.type==="revenu").map(c=>c.nom)
let CATS_EPARGNE = CFG_CATEGORIES.filter(c=>c.type==="épargne").map(c=>c.nom)
let CATS_EPARGNE_RETRAIT = CFG_CATEGORIES.filter(c=>c.type==="épargne-retrait").map(c=>c.nom)
let CATS_AVOIR   = CFG_CATEGORIES.filter(c=>c.type==="avoir").map(c=>c.nom)
let ALL_CATS     = [...CATS_REVENU, ...CATS_EPARGNE, ...CATS_EPARGNE_RETRAIT, ...CATS_AVOIR, ...CATS_DEPENSE, "📦 Commandes"]
// Transferts internes entre comptes - exclus des stats revenus/dépenses
const CATS_VIREMENT = ["🔄 Transfert interne in", "🔄 Transfert interne out"]
const isVirement = t => CATS_VIREMENT.includes(t.categorie)
// Avoirs / remboursements d'achat - viennent en déduction des dépenses (pas un vrai revenu)
const isAvoir = t => t.type === "avoir" || CATS_AVOIR.includes(t.categorie)
// Économies (dépôt et retrait) - exclus des stats revenus/dépenses
const isEpargne = t => t.type === "épargne" || t.type === "épargne-retrait"
const rebuildCats = () => {
  CATS_DEPENSE = CFG_CATEGORIES.filter(c=>c.type==="dépense").map(c=>c.nom)
  CATS_REVENU  = CFG_CATEGORIES.filter(c=>c.type==="revenu").map(c=>c.nom)
  CATS_EPARGNE = CFG_CATEGORIES.filter(c=>c.type==="épargne").map(c=>c.nom)
  CATS_EPARGNE_RETRAIT = CFG_CATEGORIES.filter(c=>c.type==="épargne-retrait").map(c=>c.nom)
  CATS_AVOIR   = CFG_CATEGORIES.filter(c=>c.type==="avoir").map(c=>c.nom)
  ALL_CATS     = [...CATS_REVENU, ...CATS_EPARGNE, ...CATS_EPARGNE_RETRAIT, ...CATS_AVOIR, ...CATS_DEPENSE, "📦 Commandes"]
}

// ════ STATE ══════════════════════════════════════════════════════
const now      = new Date()
const todayStr = localStr(now)
// Persistance via window pour survivre aux re-renders Dataview (processFrontMatter recharge le bloc)
if (!window._FINANCES_STATE) window._FINANCES_STATE = { compte:"tout", period:"mois", offset:0, cstart:"", cend:"", devise:(_p.devise_systeme||"EUR") }
let S_COMPTE       = window._FINANCES_STATE.compte
let S_PERIOD       = window._FINANCES_STATE.period
let S_MONTH_OFFSET = window._FINANCES_STATE.offset
let S_CSTART       = window._FINANCES_STATE.cstart
let S_CEND         = window._FINANCES_STATE.cend
let S_DEVISE       = window._FINANCES_STATE.devise || "EUR"
// Helpers devise - lisent depuis window pour éviter les closures périmées
const currSym = () => { const d=window._FINANCES_STATE?.devise||"EUR"; return d==="EUR"?"€":(FX_SYMS[d]||d) }
const toC     = v  => { const d=window._FINANCES_STATE?.devise||"EUR",r=window._FX_CACHE?.rates||{}; return (d==="EUR"||!r[d])?v:v*(r[d]||1) }
const fmtC    = v  => { const cv=toC(v),s=currSym(); return Math.abs(cv).toLocaleString("fr-FR",{minimumFractionDigits:2,maximumFractionDigits:2})+" "+s }
const fmtC0   = v  => { const cv=toC(v),s=currSym(); return Math.abs(v)<0.5?"0":Math.abs(cv).toLocaleString("fr-FR",{maximumFractionDigits:0})+" "+s }
// Taille de police adaptative pour les labels d'axe (PAD.left reste fixe à 72)
const _axisFont = () => { try { const t=document.createElement("canvas").getContext("2d"),s="1 234 567 "+currSym(); let sz=14; t.font=sz+"px 'Inter',sans-serif"; while(t.measureText(s).width>66&&sz>9){sz--;t.font=sz+"px 'Inter',sans-serif"} return sz } catch(e){ return 11 } }
let S_BLUR         = window._FINANCES_STATE.blur   ?? true
// Cache persistant via window pour survivre aux re-renders Dataview
if (!window._FX_CACHE) window._FX_CACHE = { rates:{XOF:655.957}, updated:null, error:false }
let FX_RATES   = window._FX_CACHE.rates
let FX_UPDATED = window._FX_CACHE.updated
let FX_ERROR   = window._FX_CACHE.error

// ════ TAUX DE CHANGE ══════════════════════════════════════════════
// Plusieurs APIs en cascade + XOF hardcodé (parité fixe officielle EUR/CFA depuis 1999)
const fetchRates = async () => {
  const APIS = [
    async () => {
      const r = await fetch("https://api.frankfurter.app/latest?from=EUR&to=USD,CAD")
      if(!r.ok) throw new Error()
      const d = await r.json(); return d.rates
    },
    async () => {
      const r = await fetch("https://open.er-api.com/v6/latest/EUR")
      if(!r.ok) throw new Error()
      const d = await r.json(); return {USD:d.rates.USD, CAD:d.rates.CAD}
    },
    async () => {
      const r = await fetch("https://api.exchangerate-api.com/v4/latest/EUR")
      if(!r.ok) throw new Error()
      const d = await r.json(); return {USD:d.rates.USD, CAD:d.rates.CAD}
    }
  ]
  for (const api of APIS) {
    try {
      const rates = await api()
      FX_RATES = { ...rates, XOF: 655.957 }
      FX_UPDATED = new Date()
      FX_ERROR = false
      window._FX_CACHE = { rates:FX_RATES, updated:FX_UPDATED, error:false }
      return
    } catch(e) { /* essaie le suivant */ }
  }
  // Toutes les APIs ont échoué - on garde le cache existant
  FX_ERROR = true
  window._FX_CACHE.error = true
}
// Ne re-fetch que si les taux ont plus de 30 min ou sont absents
const cacheAge = FX_UPDATED ? (Date.now()-FX_UPDATED.getTime())/60000 : Infinity
if (cacheAge > 30 || !FX_RATES.USD) fetchRates()

// ════ PERIOD HELPERS ═════════════════════════════════════════════
const getActiveMois = () => {
  // Retourne {year, month} du mois affiché selon S_MONTH_OFFSET
  const d = new Date(now.getFullYear(), now.getMonth() + S_MONTH_OFFSET, 1)
  return { year: d.getFullYear(), month: d.getMonth() }
}
const getMoisLabel = () => {
  if (S_MONTH_OFFSET === 0) return "Ce mois"
  const { year, month } = getActiveMois()
  return MONTHS_LONG[month] + " " + year
}

const getPeriodRange = () => {
  if (S_PERIOD === "mois") {
    const { year: y, month: m } = getActiveMois()
    return [localStr(new Date(y,m,1)), localStr(new Date(y,m+1,0))]
  }
  const y = now.getFullYear(), m = now.getMonth()
  if (S_PERIOD === "trimestre") { const q=Math.floor(m/3); return [localStr(new Date(y,q*3,1)), localStr(new Date(y,q*3+3,0))] }
  if (S_PERIOD === "annee")      return [localStr(new Date(y,0,1)), localStr(new Date(y,11,31))]
  if (/^\d{4}$/.test(S_PERIOD)) return [S_PERIOD+"-01-01", S_PERIOD+"-12-31"]
  if (S_PERIOD === "tout")       return ["", ""]
  if (S_PERIOD === "custom")     return [S_CSTART||todayStr, S_CEND||todayStr]
  return ["",""]
}

const filterTx = list => {
  const [s,e] = getPeriodRange()
  return list.filter(t => {
    if (S_COMPTE !== "tout" && normCompte(t.compte) !== normCompte(S_COMPTE)) return false
    if (s && t.date < s) return false
    if (e && t.date > e) return false
    return true
  })
}

const normCompte = s => (s||"").toLowerCase().replace(/[\s-]+/g," ").trim()
const getTxForCompte = () => S_COMPTE === "tout" ? ALL_TX : ALL_TX.filter(t => normCompte(t.compte) === normCompte(S_COMPTE))

const getSoldeInitial = () =>
  S_COMPTE === "tout"
    ? CFG_COMPTES.reduce((s,c) => s + (parseFloat(c.solde_initial)||0), 0)
    : parseFloat(CFG_COMPTES.find(c=>c.id===S_COMPTE)?.solde_initial)||0

const getSoldeCourant = () =>
  getSoldeInitial() + getTxForCompte().reduce((s,t) => s + (parseFloat(t.montant)||0), 0)

// ════ SAVE ════════════════════════════════════════════════════════
const saveComptes = async newComptes => {
  await app.fileManager.processFrontMatter(_file, fm => { fm.comptes = newComptes })
  CFG_COMPTES = newComptes
}
const saveBudgets = async newBudgets => {
  await app.fileManager.processFrontMatter(_file, fm => { fm.budgets = newBudgets })
  CFG_BUDGETS = newBudgets
}
const saveCategories = async newCats => {
  await app.fileManager.processFrontMatter(_file, fm => { fm.categories = newCats })
  CFG_CATEGORIES = newCats
  rebuildCats()
}
const saveDeviseSysteme = async devise => {
  await app.fileManager.processFrontMatter(_file, fm => { fm.devise_systeme = devise })
}
const saveTx = async newList => {
  const manualOnly = newList.filter(t => !t._auto)

  // Grouper les transactions manuelles par année
  const byYear = {}
  for (const t of manualOnly) {
    const year = (t.date || String(new Date().getFullYear())).slice(0, 4)
    if (!byYear[year]) byYear[year] = []
    const { _auto, _path, _yearFile, _manual, ...rest } = t
    byYear[year].push({ ...rest, _manual: true })
  }

  // Années concernées = années avec nouvelles saisies + tous les JSON existants
  const existingJsonFiles = app.vault.getFiles().filter(f =>
    f.path.startsWith(FINANCES_DIR + "/") && /^💰 \d{4}\.json$/.test(f.name)
  )

  for (const year of new Set([...Object.keys(byYear), ...existingJsonFiles.map(f => f.name.replace("💰 ","").replace(".json",""))])) {
    const yearPath = FINANCES_DIR + "/💰 " + year + ".json"
    let yearFile = app.vault.getAbstractFileByPath(yearPath)

    let bankTxs = []
    if (yearFile) {
      try {
        const raw = await app.vault.read(yearFile)
        bankTxs = JSON.parse(raw).filter(t => !t._manual)
      } catch(e) {}
    }

    const newManual = byYear[year] || []
    const combined = [...bankTxs, ...newManual]
      .sort((a,b) => a.date < b.date ? -1 : 1)
    const content = JSON.stringify(combined)

    if (yearFile) {
      await app.vault.modify(yearFile, content)
    } else {
      await app.vault.create(yearPath, content)
    }
  }

  // Recharger depuis le JSON pour avoir banque + manuelles en mémoire
  TX_MANUEL = await loadYearlyTx()
  ALL_TX = rebuildAllTx()
}

// ════ DATE PICKER ═════════════════════════════════════════════════
const mkDatePicker = (parent, initVal, onChange, placeholder) => {
  placeholder = placeholder || "Choisir une date"
  let sel = String(initVal||"").slice(0,10)
  const fmt = iso => { if (!iso) return placeholder; const [y,m,d]=iso.split("-"); return `${d}/${m}/${y}` }
  const wrap = parent.createEl("div")
  const btn = wrap.createEl("button",{attr:{style:"display:flex;align-items:center;gap:8px;width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;cursor:pointer;text-align:left;"}})
  btn.createEl("span").textContent = "📅"
  const lbl = btn.createEl("span",{attr:{style:"flex:1;"}})
  lbl.style.color = sel ? "var(--text-normal)" : "var(--text-muted)"
  lbl.textContent = fmt(sel)
  let cal = null
  btn.onclick = e => {
    e.stopPropagation()
    if (cal) { cal.remove(); cal=null; return }
    const sd = sel ? new Date(sel+"T00:00:00") : new Date()
    let vY=sd.getFullYear(), vM=sd.getMonth()
    cal = document.body.createEl("div",{attr:{style:"position:fixed;z-index:10000;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.25);padding:14px;width:240px;"}})
    const rect = btn.getBoundingClientRect()
    cal.style.left = Math.min(rect.left, window.innerWidth-256)+"px"
    if (window.innerHeight-rect.bottom > 270) { cal.style.top=(rect.bottom+6)+"px" }
    else { cal.style.top=(rect.top-6)+"px"; cal.style.transform="translateY(-100%)" }
    const todStr = new Date().toISOString().slice(0,10)
    const render = () => {
      cal.empty()
      const hdr=cal.createEl("div",{attr:{style:"display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;"}})
      const pb=hdr.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}}); pb.textContent="‹"
      pb.onclick=e2=>{e2.stopPropagation();vM--;if(vM<0){vM=11;vY--};render()}
      hdr.createEl("span",{attr:{style:"font-weight:700;font-size:0.88em;"}}).textContent=MONTHS_LONG[vM]+" "+vY
      const nb=hdr.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}}); nb.textContent="›"
      nb.onclick=e2=>{e2.stopPropagation();vM++;if(vM>11){vM=0;vY++};render()}
      const dh=cal.createEl("div",{attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:4px;"}})
      DFR.forEach(d=>{const c=dh.createEl("div",{attr:{style:"text-align:center;font-size:0.68em;color:var(--text-muted);font-weight:600;padding:2px 0;"}});c.textContent=d})
      const g=cal.createEl("div",{attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:3px;"}})
      const firstDow=(new Date(vY,vM,1).getDay()+6)%7, dim=new Date(vY,vM+1,0).getDate()
      for(let i=0;i<firstDow;i++) g.createEl("div")
      for(let day=1;day<=dim;day++){
        const iso=`${vY}-${String(vM+1).padStart(2,"0")}-${String(day).padStart(2,"0")}`
        const isS=iso===sel, isT=iso===todStr
        const c=g.createEl("div",{attr:{style:"text-align:center;padding:5px 2px;border-radius:6px;cursor:pointer;font-size:0.84em;line-height:1;"+(isS?"background:var(--interactive-accent);color:#fff;font-weight:700;":isT?"border:1.5px solid var(--interactive-accent);color:var(--interactive-accent);font-weight:600;":"")}})
        c.textContent=day
        if(!isS){c.onmouseenter=()=>{c.style.background="var(--background-secondary)"};c.onmouseleave=()=>{c.style.background=""}}
        c.onclick=e2=>{e2.stopPropagation();sel=iso;lbl.textContent=fmt(iso);lbl.style.color="var(--text-normal)";if(onChange)onChange(iso);cal.remove();cal=null;if(hdlr)document.removeEventListener("click",hdlr,true)}
      }
    }
    render()
    let hdlr; hdlr=e2=>{if(cal&&!cal.contains(e2.target)&&e2.target!==btn){cal.remove();cal=null;document.removeEventListener("click",hdlr,true)}}
    setTimeout(()=>document.addEventListener("click",hdlr,true),10)
  }
  return { getValue:()=>sel }
}

// ════ FORMULAIRE TRANSACTION ══════════════════════════════════════
const LABEL_S = "font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"
const INP_S   = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.92em;box-sizing:border-box;font-family:inherit;"

const showTxForm = (title, defaults, onSubmit) => {
  const overlay = document.body.createEl("div",{attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div",{attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:320px;max-width:440px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);display:flex;flex-direction:column;gap:12px;"}})
  box.createEl("h3",{attr:{style:"margin:0;font-size:1em;font-weight:700;"}}).textContent = title

  // Description
  const g1=box.createEl("div"); g1.createEl("label",{attr:{style:LABEL_S}}).textContent="Description"
  const inpLabel=g1.createEl("input",{attr:{type:"text",placeholder:"Ex: Courses, Loyer, Salaire…",value:defaults.label||"",style:INP_S}})

  // Montant
  const g2=box.createEl("div"); g2.createEl("label",{attr:{style:LABEL_S}}).textContent="Montant (€)"
  const inpMontant=g2.createEl("input",{attr:{type:"number",step:"0.01",min:"0.01",placeholder:"Ex: 45.50",value:defaults.montant!=null?Math.abs(defaults.montant):"",style:INP_S}})

  // Catégorie selon forceType
  const g3=box.createEl("div"); g3.createEl("label",{attr:{style:LABEL_S}}).textContent="Catégorie"
  const selCat=g3.createEl("select",{attr:{style:INP_S}})
  const availCats = defaults.forceType === "revenu"          ? CATS_REVENU
                  : defaults.forceType === "épargne"         ? CATS_EPARGNE
                  : defaults.forceType === "épargne-retrait" ? CATS_EPARGNE_RETRAIT
                  : defaults.forceType === "avoir"           ? CATS_AVOIR
                  : defaults.forceType === "dépense"         ? CATS_DEPENSE
                  : [...CATS_REVENU, ...CATS_EPARGNE, ...CATS_EPARGNE_RETRAIT, ...CATS_AVOIR, ...CATS_DEPENSE]
  for (const c of availCats) {
    const opt=selCat.createEl("option",{attr:{value:c}}); opt.textContent=c
    if (defaults.categorie===c) opt.selected=true
  }

  // Date
  const g4=box.createEl("div"); g4.createEl("label",{attr:{style:LABEL_S}}).textContent="Date"
  const dpMock={value:String(defaults.date||todayStr).slice(0,10)}
  const dp=mkDatePicker(g4, dpMock.value, v=>{dpMock.value=v})

  // Compte (si plusieurs comptes)
  let selCompte=null
  if (CFG_COMPTES.length > 1) {
    const g5=box.createEl("div"); g5.createEl("label",{attr:{style:LABEL_S}}).textContent="Compte"
    selCompte=g5.createEl("select",{attr:{style:INP_S}})
    const defaultCompte = defaults.compte || (S_COMPTE!=="tout" ? S_COMPTE : CFG_COMPTES[0]?.id)
    for (const c of CFG_COMPTES) {
      const opt=selCompte.createEl("option",{attr:{value:c.id}}); opt.textContent=c.label
      if (c.id===defaultCompte) opt.selected=true
    }
  }

  const btns=box.createEl("div",{attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:4px;"}})
  const cancelBtn=btns.createEl("button",{attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);font-family:inherit;"}})
  cancelBtn.textContent="Annuler"; cancelBtn.onclick=()=>overlay.remove()
  const okBtn=btns.createEl("button",{attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"}})
  okBtn.textContent="Enregistrer"

  okBtn.onclick = () => {
    const rawM=parseFloat(inpMontant.value)
    if (!inpLabel.value.trim() || isNaN(rawM) || rawM<=0 || !dpMock.value) { new Notice("Remplis tous les champs obligatoires.",2000); return }
    const cat=selCat.value
    const type = CATS_AVOIR.includes(cat) ? "avoir" : CATS_REVENU.includes(cat) ? "revenu" : CATS_EPARGNE.includes(cat) ? "épargne" : CATS_EPARGNE_RETRAIT.includes(cat) ? "épargne-retrait" : "dépense"
    const montant = (type==="dépense" || type==="épargne") ? -rawM : rawM
    overlay.remove()
    onSubmit({ date:dpMock.value, label:inpLabel.value.trim(), montant, categorie:cat, type, compte:selCompte?selCompte.value:(CFG_COMPTES[0]?.id||"courant"), _auto:false })
  }
  overlay.onclick=e=>{if(e.target===overlay)overlay.remove()}
  box.onkeydown=e=>{if(e.key==="Enter")okBtn.click();if(e.key==="Escape")overlay.remove()}
  setTimeout(()=>inpLabel.focus(),50)
}

// ════ MODALE PARAMÈTRES ═══════════════════════════════════════════
const TYPE_COMPTES = ["courant","épargne","économies","investissement","autre"]
const openSettings = () => {
  const overlay = document.body.createEl("div",{attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;padding:32px 16px;box-sizing:border-box;"}})
  overlay.onclick = e => { if(e.target===overlay) overlay.remove() }
  const modal = overlay.createEl("div",{attr:{style:"background:var(--background-primary);border-radius:16px;padding:0;width:580px;max-width:95vw;max-height:88vh;display:flex;flex-direction:column;box-shadow:0 12px 48px rgba(0,0,0,0.3);overflow:hidden;"}})
  modal.onclick = e => e.stopPropagation()

  // En-tête modal : titre + bouton fermer
  const mHead = modal.createEl("div",{attr:{style:"display:flex;align-items:center;justify-content:space-between;padding:18px 24px 0;flex-shrink:0;"}})
  mHead.createEl("span",{attr:{style:"font-size:1em;font-weight:700;color:var(--text-normal);"}}).textContent="⚙️ Paramètres"
  const closeBtn = mHead.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;font-size:1.2em;color:var(--text-muted);padding:0 4px;line-height:1;font-family:inherit;"}})
  closeBtn.textContent="✕"; closeBtn.onclick=()=>overlay.remove()

  // Tabs header - sticky, ne scroll pas avec le contenu
  let activeTab = "general"
  const tabBar = modal.createEl("div",{attr:{style:"display:flex;border-bottom:1px solid var(--background-modifier-border);padding:0 20px;flex-shrink:0;background:var(--background-primary);margin-top:12px;"}})
  const body   = modal.createEl("div",{attr:{style:"flex:1;overflow-y:auto;padding:20px 24px 24px;min-height:0;"}})

  const mkTab = (id, label) => {
    const t = tabBar.createEl("button",{attr:{style:`padding:12px 16px;border:none;background:none;cursor:pointer;font-size:0.9em;font-family:inherit;font-weight:600;border-bottom:2px solid transparent;margin-bottom:-1px;color:var(--text-muted);`}})
    t.textContent = label
    t.onclick = () => { activeTab=id; renderTabs(); renderBody() }
    return t
  }
  const tabs = {general: mkTab("general","⚙️ Général"), comptes: mkTab("comptes","🏦 Comptes"), budgets: mkTab("budgets","📊 Budgets"), categories: mkTab("categories","🏷 Catégories")}

  const renderTabs = () => {
    for(const [id,t] of Object.entries(tabs)){
      t.style.color      = activeTab===id ? "var(--text-normal)" : "var(--text-muted)"
      t.style.borderBottomColor = activeTab===id ? "var(--interactive-accent)" : "transparent"
    }
  }

  const INP = "width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.88em;box-sizing:border-box;font-family:inherit;"
  const LBL = "font-size:0.75em;font-weight:700;color:var(--text-muted);letter-spacing:0.05em;text-transform:uppercase;display:block;margin-bottom:4px;"
  const BTN_P = "padding:5px 13px;border:none;border-radius:7px;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.83em;font-weight:600;font-family:inherit;"
  const BTN_G = "padding:5px 13px;border:1px solid var(--background-modifier-border);border-radius:7px;background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.83em;font-family:inherit;"
  const BTN_D = "padding:4px 8px;border:1px solid rgba(210,15,57,0.35);border-radius:6px;background:none;color:#d20f39;cursor:pointer;font-size:0.78em;font-family:inherit;"

  // ── FORM COMPTE ──────────────────────────────────────────────────
  const showCompteForm = (existing, onSave) => {
    body.empty()
    const back = body.createEl("button",{attr:{style:BTN_G+"margin-bottom:16px;"}}); back.textContent="← Retour"; back.onclick=renderBody

    const f = (lbl,inp) => { const g=body.createEl("div",{attr:{style:"margin-bottom:12px;"}}); g.createEl("label",{attr:{style:LBL}}).textContent=lbl; g.append(inp); return inp }
    const inp = t => document.createElement("input"); 

    const nomI   = f("Nom du compte",    Object.assign(document.createElement("input"),{type:"text",   value:existing?.label||"",style:INP,placeholder:"Ex: Compte principal"}))
    const banqueI= f("Banque / Organisme",Object.assign(document.createElement("input"),{type:"text",  value:existing?.banque||"",style:INP,placeholder:"Ex: BNP, Boursorama, Livret A…"}))
    const typeG  = body.createEl("div",{attr:{style:"margin-bottom:12px;"}}); typeG.createEl("label",{attr:{style:LBL}}).textContent="Type de compte"
    const typeS  = typeG.createEl("select",{attr:{style:INP}})
    for(const t of TYPE_COMPTES){ const o=typeS.createEl("option",{attr:{value:t}}); o.textContent=t.charAt(0).toUpperCase()+t.slice(1); if((existing?.type||"courant")===t)o.selected=true }
    const soldeI = f("Solde initial (€)", Object.assign(document.createElement("input"),{type:"number",step:"0.01",value:existing?.solde_initial??0,style:INP}))

    // Helper solde
    const helpBox = body.createEl("div",{attr:{style:"background:rgba(30,102,245,0.07);border:1px solid rgba(30,102,245,0.2);border-radius:8px;padding:10px 13px;font-size:0.8em;color:var(--text-muted);margin-bottom:16px;line-height:1.5;"}})
    helpBox.innerHTML = `💡 <b>Comment calculer le solde initial ?</b><br>Solde initial = ton solde bancaire réel actuel + total des dépenses déjà importées automatiquement (commandes).<br>Exemple : solde réel <b>500 €</b>, commandes importées <b>952 €</b> → solde initial = <b>1 452 €</b>`

    const row = body.createEl("div",{attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:4px;"}})
    const cancel = row.createEl("button",{attr:{style:BTN_G}}); cancel.textContent="Annuler"; cancel.onclick=renderBody
    const save   = row.createEl("button",{attr:{style:BTN_P}}); save.textContent="💾 Enregistrer"
    save.onclick = async () => {
      const nom = nomI.value.trim()
      if(!nom){new Notice("Le nom est requis.",2000);return}
      const c = {
        id:            existing?.id || nom.toLowerCase().replace(/\s+/g,"-").replace(/[^a-z0-9-]/g,""),
        label:         nom,
        banque:        banqueI.value.trim()||"",
        type:          typeS.value,
        solde_initial: parseFloat(soldeI.value)||0
      }
      let updated
      if(existing) { updated = CFG_COMPTES.map(x => x.id===existing.id ? c : x) }
      else         { updated = [...CFG_COMPTES, c] }
      await saveComptes(updated)
      new Notice(existing?"Compte modifié ✓":"Compte ajouté ✓",2000)
      renderBody()
    }
  }

  // ── ONGLET COMPTES ───────────────────────────────────────────────
  const renderComptes = () => {
    body.empty()
    body.createEl("p",{attr:{style:"font-size:0.82em;color:var(--text-muted);margin-bottom:14px;"}}).textContent="Gérez vos comptes bancaires et leurs soldes initiaux."
    for(const c of CFG_COMPTES){
      const row = body.createEl("div",{attr:{style:"display:flex;align-items:center;gap:10px;padding:10px 12px;border:1px solid var(--background-modifier-border);border-radius:9px;margin-bottom:8px;background:var(--background-secondary);"}})
      const info = row.createEl("div",{attr:{style:"flex:1;min-width:0;"}}); 
      info.createEl("div",{attr:{style:"font-weight:700;font-size:0.9em;"}}).textContent=c.label
      const sub = info.createEl("div",{attr:{style:"font-size:0.77em;color:var(--text-muted);display:flex;gap:8px;margin-top:2px;flex-wrap:wrap;"}})
      if(c.banque) sub.createEl("span").textContent="🏛 "+c.banque
      sub.createEl("span").textContent="📋 "+(c.type||"courant")
      sub.createEl("span").textContent="💶 Solde initial : "+fmtEur(parseFloat(c.solde_initial)||0)
      const editB = row.createEl("button",{attr:{style:BTN_G}}); editB.textContent="✏"; editB.onclick=()=>showCompteForm(c,renderBody)
      const delB  = row.createEl("button",{attr:{style:BTN_D}});  delB.textContent="🗑"
      delB.onclick = async () => {
        if(!confirm(`Supprimer le compte "${c.label}" ?`))return
        await saveComptes(CFG_COMPTES.filter(x=>x.id!==c.id))
        new Notice("Compte supprimé.",2000); renderBody()
      }
    }
    const addBtn = body.createEl("button",{attr:{style:BTN_P+"width:100%;margin-top:6px;padding:8px;"}}); addBtn.textContent="+ Ajouter un compte"
    addBtn.onclick = () => showCompteForm(null, renderBody)
  }

  // ── ONGLET BUDGETS ───────────────────────────────────────────────
  const renderBudgets = () => {
    body.empty()
    body.createEl("p",{attr:{style:"font-size:0.82em;color:var(--text-muted);margin-bottom:14px;"}}).textContent="Activez les catégories à suivre et définissez leur plafond mensuel."

    // Liste complète : dépenses dynamiques + 📦 Commandes (toujours actif) + budgets orphelins
    const CAT_COMMANDES = "📦 Commandes"
    const baseCats = [...CATS_DEPENSE]
    if(!baseCats.includes(CAT_COMMANDES)) baseCats.push(CAT_COMMANDES)
    const orphans = CFG_BUDGETS.map(b=>b.categorie).filter(c=>!baseCats.includes(c))
    const allBudgetCats = [...baseCats, ...orphans]

    if(allBudgetCats.length===0){
      body.createEl("p",{attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.85em;"}}).textContent="Ajoutez d'abord des catégories de type dépense dans l'onglet Catégories."
      return
    }

    for(const cat of allBudgetCats){
      const isCommandes = cat === CAT_COMMANDES
      const isOrphan    = orphans.includes(cat)
      const existing    = CFG_BUDGETS.find(b=>b.categorie===cat)
      const isActive    = isCommandes ? true : !!existing
      const borderColor = isOrphan ? "#c4943a" : isActive ? "var(--interactive-accent)" : "var(--background-modifier-border)"
      const bgColor     = isOrphan ? "rgba(196,148,58,0.06)" : isActive ? "rgba(30,102,245,0.04)" : "var(--background-secondary)"

      const row = body.createEl("div",{attr:{style:`display:flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid ${borderColor};border-radius:9px;margin-bottom:7px;background:${bgColor};`}})

      // Toggle - verrouillé pour Commandes
      const toggle = row.createEl("input",{attr:{type:"checkbox",style:`width:16px;height:16px;accent-color:var(--interactive-accent);flex-shrink:0;${isCommandes?"cursor:not-allowed;opacity:0.6;":"cursor:pointer;"}`}})
      toggle.checked  = isActive
      toggle.disabled = isCommandes

      // Nom + badges
      const nameWrap = row.createEl("span",{attr:{style:"flex:1;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"}})
      nameWrap.createEl("span",{attr:{style:`font-size:0.9em;font-weight:600;color:${isActive?"var(--text-normal)":"var(--text-muted)"};`}}).textContent=cat
      if(isCommandes){
        nameWrap.createEl("span",{attr:{style:"font-size:0.72em;padding:1px 6px;border-radius:8px;background:rgba(30,102,245,0.12);color:var(--interactive-accent);font-weight:700;white-space:nowrap;"}}).textContent="lié aux commandes"
      }
      if(isOrphan){
        nameWrap.createEl("span",{attr:{style:"font-size:0.72em;padding:1px 6px;border-radius:8px;background:rgba(196,148,58,0.15);color:#c4943a;font-weight:700;white-space:nowrap;"}}).textContent="⚠️ catégorie supprimée"
      }

      // Montant
      const amtWrap=row.createEl("div",{attr:{style:"display:flex;align-items:center;gap:5px;"}})
      const mI=amtWrap.createEl("input",{attr:{type:"number",step:"1",min:"0",value:existing?parseFloat(existing.montant)||"":"",placeholder:"0",style:`width:80px;${INP}width:80px;text-align:right;opacity:${isActive?1:0.35};`}})
      if(!isActive) mI.disabled=true
      amtWrap.createEl("span",{attr:{style:`font-size:0.85em;color:var(--text-muted);opacity:${isActive?1:0.4};`}}).textContent="€/mois"

      const persistBudget = async () => {
        const filtered=CFG_BUDGETS.filter(b=>b.categorie!==cat)
        if(toggle.checked) await saveBudgets([...filtered,{categorie:cat,montant:parseFloat(mI.value)||0}])
        else await saveBudgets(filtered)
        renderBody()
      }

      if(!isCommandes){
        toggle.onchange = async () => {
          if(toggle.checked){ mI.disabled=false; mI.style.opacity="1"; setTimeout(()=>mI.focus(),30) }
          else { mI.disabled=true; mI.style.opacity="0.35" }
          await persistBudget()
        }
      } else if(!existing){
        // Assurer que le budget Commandes existe en frontmatter dès le premier affichage
        saveBudgets([...CFG_BUDGETS,{categorie:CAT_COMMANDES,montant:0}])
      }
      mI.onblur    = async () => { if(toggle.checked) await persistBudget() }
      mI.onkeydown = async e => { if(e.key==="Enter"&&toggle.checked) mI.blur() }
    }
  }

  // ── ONGLET CATÉGORIES ────────────────────────────────────────────
  const CAT_TYPES = ["dépense","revenu","épargne","avoir"]
  const CAT_TYPE_LABELS = { dépense:"💸 Dépense", revenu:"💵 Revenu", épargne:"💰 Épargne", avoir:"🔙 Avoir" }

  const renderCategories = () => {
    body.empty()
    body.createEl("p",{attr:{style:"font-size:0.82em;color:var(--text-muted);margin-bottom:14px;"}}).textContent="Gérez vos catégories. Elles seront disponibles lors de la saisie de transactions."
    const currentCats = Array.isArray(_p.categories) ? [..._p.categories] : []
    for(let i=0;i<currentCats.length;i++){
      const cat=currentCats[i]
      const row=body.createEl("div",{attr:{style:"display:flex;align-items:center;gap:8px;padding:7px 12px;border:1px solid var(--background-modifier-border);border-radius:9px;margin-bottom:7px;background:var(--background-secondary);"}})
      const nomI=row.createEl("input",{attr:{type:"text",value:cat.nom||"",placeholder:"Nom (ex: 🛒 Alimentation)",style:INP+"flex:1;min-width:0;"}})
      const typeS=row.createEl("select",{attr:{style:INP+"flex-shrink:0;width:115px;"}})
      for(const t of CAT_TYPES){const o=typeS.createEl("option",{attr:{value:t}});o.textContent=CAT_TYPE_LABELS[t];if(cat.type===t)o.selected=true}
      const saveB=row.createEl("button",{attr:{style:BTN_G+"padding:4px 9px;font-size:0.8em;"}});saveB.textContent="💾"
      saveB.title="Enregistrer"
      saveB.onclick=async()=>{
        const nom=nomI.value.trim()
        if(!nom){new Notice("Le nom est requis.",2000);return}
        const updated=currentCats.map((c,j)=>j===i?{nom,type:typeS.value}:c)
        await saveCategories(updated)
        new Notice("Catégorie modifiée ✓",2000); renderBody()
      }
      const delB=row.createEl("button",{attr:{style:BTN_D}});delB.textContent="🗑"
      delB.onclick=async()=>{
        if(!confirm(`Supprimer la catégorie "${cat.nom}" ?`))return
        await saveCategories(currentCats.filter((_,j)=>j!==i))
        new Notice("Catégorie supprimée.",2000); renderBody()
      }
    }
    // Ajouter une catégorie
    const addRow=body.createEl("div",{attr:{style:"display:flex;gap:8px;margin-top:10px;align-items:center;"}})
    const newNomI=addRow.createEl("input",{attr:{type:"text",placeholder:"Nom (ex: 🎁 Cadeaux)",style:INP+"flex:1;min-width:0;"}})
    const newTypeS=addRow.createEl("select",{attr:{style:INP+"flex-shrink:0;width:115px;"}})
    for(const t of CAT_TYPES){const o=newTypeS.createEl("option",{attr:{value:t}});o.textContent=CAT_TYPE_LABELS[t]}
    const addB=addRow.createEl("button",{attr:{style:BTN_P}});addB.textContent="+ Ajouter"
    addB.onclick=async()=>{
      const nom=newNomI.value.trim()
      if(!nom){new Notice("Le nom est requis.",2000);return}
      const currentCats2=Array.isArray(_p.categories)?[..._p.categories]:[]
      await saveCategories([...currentCats2,{nom,type:newTypeS.value}])
      new Notice("Catégorie ajoutée ✓",2000); renderBody()
    }
  }

  // ── ONGLET GÉNÉRAL ──────────────────────────────────────────────
  const DEVISES_LIST = [
    {id:"EUR", label:"🇪🇺 Euro (EUR)", sym:"€"},
    {id:"USD", label:"🇺🇸 Dollar US (USD)", sym:"USD"},
    {id:"CAD", label:"🇨🇦 Dollar canadien (CAD)", sym:"CAD"},
    {id:"XOF", label:"🌍 Franc CFA (XOF)", sym:"F CFA"}
  ]
  const renderGeneral = () => {
    body.empty()
    body.createEl("p",{attr:{style:"font-size:0.82em;color:var(--text-muted);margin-bottom:18px;line-height:1.5;"}}).textContent="Paramètres globaux du suivi financier."

    const section = body.createEl("div",{attr:{style:"background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:16px 18px;margin-bottom:14px;"}})
    section.createEl("div",{attr:{style:"font-weight:700;font-size:0.9em;margin-bottom:4px;"}}).textContent="💱 Devise système"
    section.createEl("div",{attr:{style:"font-size:0.78em;color:var(--text-muted);margin-bottom:12px;line-height:1.4;"}}).textContent="Devise utilisée par défaut à chaque ouverture. Vous pouvez toujours basculer temporairement via le bouton 💱 dans la barre d'outils."

    let currentDevise = _p.devise_systeme || "EUR"
    const grid = section.createEl("div",{attr:{style:"display:grid;grid-template-columns:1fr 1fr;gap:8px;"}})
    const devBtns = {}
    const renderDevBtns = () => {
      for(const [id, btn] of Object.entries(devBtns)){
        const active = id === currentDevise
        btn.style.borderColor = active ? "var(--interactive-accent)" : "var(--background-modifier-border)"
        btn.style.background  = active ? "rgba(30,102,245,0.08)" : "var(--background-primary)"
        btn.style.color       = active ? "var(--text-normal)" : "var(--text-muted)"
        btn.style.fontWeight  = active ? "700" : "400"
      }
    }
    for(const d of DEVISES_LIST){
      const btn = grid.createEl("button",{attr:{style:"padding:10px 14px;border-radius:9px;border:1.5px solid var(--background-modifier-border);background:var(--background-primary);cursor:pointer;font-size:0.87em;font-family:inherit;text-align:left;transition:all 0.12s;"}})
      btn.textContent = d.label
      devBtns[d.id] = btn
      btn.onclick = () => {
        if(currentDevise === d.id) return
        currentDevise = d.id
        renderDevBtns()
      }
    }
    renderDevBtns()

    const info = body.createEl("div",{attr:{style:"font-size:0.78em;color:var(--text-muted);margin-top:10px;padding:8px 12px;background:rgba(30,102,245,0.05);border-radius:7px;border:1px solid rgba(30,102,245,0.15);line-height:1.4;"}})
    info.innerHTML = "ℹ️ La devise système est chargée à l'ouverture du vault. Pour l'appliquer immédiatement à cette session, cliquez sur <b>Appliquer maintenant</b>."
    const applyBtn = body.createEl("button",{attr:{style:BTN_P+"margin-top:10px;"}})
    applyBtn.textContent = "⚡ Appliquer maintenant"
    applyBtn.onclick = async () => {
      await saveDeviseSysteme(currentDevise)
      S_DEVISE = currentDevise
      window._FINANCES_STATE.devise = currentDevise
      devBtnT.textContent = "💱 " + currentDevise
      devBtnT.style.borderColor = currentDevise!=="EUR" ? "var(--interactive-accent)" : "var(--background-modifier-border)"
      devBtnT.style.color       = currentDevise!=="EUR" ? "var(--interactive-accent)" : "var(--text-muted)"
      devBtnT.title = "Devise affichée : " + currentDevise + " · Changer dans Paramètres"
      if(currentDevise!=="EUR" && !FX_RATES[currentDevise]) fetchRates().then(renderAll)
      else renderAll()
      new Notice("Devise système enregistrée et appliquée : " + currentDevise + " ✓", 2500)
    }
  }

  const renderBody = () => {
    if(activeTab==="general") renderGeneral()
    else if(activeTab==="comptes") renderComptes()
    else if(activeTab==="budgets") renderBudgets()
    else renderCategories()
  }

  renderTabs(); renderBody()
  document.body.append(overlay)
}

// ════ CSS BLUR CONFIDENTIALITÉ ════════════════════════════════════
const _BLUR_STYLE_ID = 'fin-privacy-blur'
if (!document.getElementById(_BLUR_STYLE_ID)) {
  const _bs = document.createElement('style'); _bs.id = _BLUR_STYLE_ID
  _bs.textContent = [
    '.fin-blur .fin-amount { filter:blur(6px); transition:filter 0.15s; cursor:pointer; user-select:none; }',
    '.fin-blur .fin-amount:hover { filter:none; }',
    '.fin-blur canvas.fin-amount { filter:blur(8px); transition:filter 0.2s; cursor:pointer; }',
    '.fin-blur canvas.fin-amount:hover { filter:none; }'
  ].join(' ')
  document.head.appendChild(_bs)
}

// ════ WRAP PRINCIPAL ══════════════════════════════════════════════
const page = dv.container.createDiv()
page.style.cssText = "position:relative;"

// ── Toolbar fixe en haut à droite (hors renderAll) ────────────────
const toolbar = page.createDiv()
toolbar.style.cssText = "position:absolute;top:0;right:0;display:flex;gap:8px;align-items:center;z-index:10;"

const ICON_BTN = "padding:5px 11px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;"
// Bouton mode confidentialité
const blurBtnT = toolbar.createEl("button",{attr:{style:ICON_BTN+(S_BLUR?";border-color:var(--interactive-accent);color:var(--interactive-accent);":"")}})
blurBtnT.textContent = S_BLUR ? "🙈" : "👁"
blurBtnT.onclick = () => {
  S_BLUR = !S_BLUR
  window._FINANCES_STATE.blur = S_BLUR
  blurBtnT.textContent = S_BLUR ? "🙈" : "👁"
  blurBtnT.style.borderColor = S_BLUR ? "var(--interactive-accent)" : "var(--background-modifier-border)"
  blurBtnT.style.color       = S_BLUR ? "var(--interactive-accent)" : "var(--text-muted)"
  wrap.classList.toggle('fin-blur', S_BLUR)
}

const settBtnT = toolbar.createEl("button",{attr:{style:ICON_BTN}}); settBtnT.textContent="⚙️ Paramètres"
settBtnT.onclick = () => openSettings()

const devWrapT = toolbar.createEl("div",{attr:{style:"position:relative;display:inline-block;"}})
const _devSys = _p.devise_systeme || "EUR"
const devBtnT  = devWrapT.createEl("button",{attr:{style:ICON_BTN+(S_DEVISE!=="EUR"?";border-color:var(--interactive-accent);color:var(--interactive-accent);":"")}})
devBtnT.textContent = "💱 " + S_DEVISE
devBtnT.title = "Devise affichée : " + S_DEVISE + (S_DEVISE !== _devSys ? " (défaut : " + _devSys + ")" : " · Changer dans Paramètres")
const devMenuT = devWrapT.createEl("div",{attr:{style:"display:none;position:absolute;top:calc(100%+4px);right:0;z-index:999;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,0.15);padding:6px;min-width:160px;"}})
const DEVISES = [{id:"EUR",label:"🇪🇺 Euro (EUR)"},{id:"USD",label:"🇺🇸 Dollar US (USD)"},{id:"CAD",label:"🇨🇦 Dollar CA (CAD)"},{id:"XOF",label:"🌍 Franc CFA (XOF)"}]
for(const d of DEVISES){
  const opt = devMenuT.createEl("div",{attr:{style:"padding:6px 10px;border-radius:7px;cursor:pointer;font-size:0.85em;"+(S_DEVISE===d.id?"font-weight:700;background:var(--background-secondary);":"")}})
  opt.textContent = d.label
  opt.onmouseenter=()=>{if(S_DEVISE!==d.id)opt.style.background="var(--background-secondary)"}
  opt.onmouseleave=()=>{if(S_DEVISE!==d.id)opt.style.background=""}
  opt.onclick = () => {
    S_DEVISE = d.id
    devBtnT.textContent = "💱 " + S_DEVISE
    devBtnT.style.borderColor = S_DEVISE!=="EUR" ? "var(--interactive-accent)" : "var(--background-modifier-border)"
    devBtnT.style.color       = S_DEVISE!=="EUR" ? "var(--interactive-accent)" : "var(--text-muted)"
    saveDeviseSysteme(S_DEVISE)
    if(S_DEVISE!=="EUR" && !FX_RATES[S_DEVISE]) fetchRates().then(renderAll)
    devMenuT.style.display="none"
    renderAll()
  }
}
devBtnT.onclick = e => { e.stopPropagation(); devMenuT.style.display = devMenuT.style.display==="none"?"block":"none" }
document.addEventListener("click",()=>{devMenuT.style.display="none"},{once:true})

const wrap = page.createDiv()
wrap.style.cssText = "display:flex;flex-direction:column;gap:20px;padding-top:40px;"

// ════ RENDER ══════════════════════════════════════════════════════
const renderAll = () => {
  // Sauvegarder la navigation dans window pour survivre aux re-renders processFrontMatter
  window._FINANCES_STATE = { compte:S_COMPTE, period:S_PERIOD, offset:S_MONTH_OFFSET, cstart:S_CSTART, cend:S_CEND, devise:S_DEVISE, blur:S_BLUR }
  wrap.empty()
  if (S_BLUR) wrap.classList.add('fin-blur')
  ALL_TX = rebuildAllTx()
  _renderHeader()
  _renderStats()
  _renderEconomies()
  _renderChart()
  _renderDonut()
  _renderMonthly()
  _renderBudgets()
  _renderHistory()
}

// ── HEADER : sélecteurs compte + période ──────────────────────────
const _renderHeader = () => {
  const sec = wrap.createDiv()
  sec.style.cssText = "display:flex;flex-direction:column;gap:10px;"

  // Ligne 1 : comptes + période
  const row1 = sec.createDiv()
  row1.style.cssText = "display:flex;gap:8px;align-items:center;flex-wrap:wrap;"

  // Comptes
  if (CFG_COMPTES.length > 0) {
    const cWrap=row1.createDiv(); cWrap.style.cssText="display:flex;gap:4px;flex-wrap:wrap;"
    for (const opt of [{id:"tout",label:"🏦 Tous comptes",banque:null}, ...CFG_COMPTES]) {
      const active = S_COMPTE===opt.id
      const btn = cWrap.createEl("button")
      btn.style.cssText = (active
        ? "padding:20px 24px;border-radius:10px;border:none;background:var(--interactive-accent);color:#fff;"
        : "padding:20px 24px;border-radius:10px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);")
        + "cursor:pointer;font-size:0.9em;font-family:inherit;display:flex;flex-direction:column;align-items:center;line-height:1.2;"
      btn.createEl("span",{attr:{style:"font-weight:"+(active?"700":"600")+";"}}).textContent = opt.label
      if(opt.banque) btn.createEl("span",{attr:{style:"font-size:0.78em;color:"+(active?"rgba(255,255,255,0.75)":"var(--text-muted)")+";font-weight:400;margin-top:3px;"}}).textContent = opt.banque
      btn.onclick=()=>{S_COMPTE=opt.id;renderAll()}
    }
  }

  // Séparateur
  const sep=row1.createDiv(); sep.style.cssText="flex:1;"

  // Périodes
  const pWrap=row1.createDiv(); pWrap.style.cssText="display:flex;gap:4px;flex-wrap:wrap;align-items:center;"
  const PILL_A="padding:5px 13px;border-radius:20px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.84em;font-weight:700;font-family:inherit;"
  const PILL_I="padding:5px 13px;border-radius:20px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.84em;font-family:inherit;"
  const ARR_S ="padding:4px 9px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.9em;font-family:inherit;line-height:1;"

  for (const [key,baseLabel] of [["mois",""],["trimestre","Trimestre"],["annee",""],["custom","Personnalisé"]]) {
    if (key === "mois") {
      // Flèche gauche
      const prev=pWrap.createEl("button",{attr:{style:ARR_S}}); prev.textContent="‹"; prev.title="Mois précédent"
      prev.onclick=()=>{S_PERIOD="mois";S_MONTH_OFFSET--;renderAll()}
      // Pill mois avec label dynamique
      const mBtn=pWrap.createEl("button"); mBtn.textContent=getMoisLabel()
      mBtn.style.cssText=S_PERIOD==="mois"?PILL_A:PILL_I
      mBtn.style.minWidth="130px"; mBtn.style.textAlign="center"
      mBtn.onclick=()=>{S_PERIOD="mois";S_MONTH_OFFSET=0;renderAll()}
      // Flèche droite (désactivée si mois courant ou futur)
      const next=pWrap.createEl("button",{attr:{style:ARR_S+(S_MONTH_OFFSET>=0?";opacity:0.3;cursor:default;":"")}}); next.textContent="›"; next.title="Mois suivant"
      next.onclick=()=>{if(S_MONTH_OFFSET>=0)return;S_PERIOD="mois";S_MONTH_OFFSET++;renderAll()}
    } else if (key === "annee") {
      // Dropdown : Cette année / années spécifiques / Tout
      const isYearActive=S_PERIOD==="annee"||S_PERIOD==="tout"||/^\d{4}$/.test(S_PERIOD)
      const anneeLabel=S_PERIOD==="tout"?"Tout":/^\d{4}$/.test(S_PERIOD)?S_PERIOD:"Cette année"
      const ddWrap=pWrap.createEl("div",{attr:{style:"position:relative;display:inline-block;"}})
      const ddBtn=ddWrap.createEl("button")
      ddBtn.textContent=anneeLabel+" ▾"
      ddBtn.style.cssText=isYearActive?PILL_A:PILL_I
      const ddMenu=ddWrap.createEl("div",{attr:{style:"display:none;position:absolute;top:calc(100% + 4px);left:0;z-index:999;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,0.15);padding:6px;min-width:150px;"}})
      const availYears=[...new Set(ALL_TX.map(t=>t.date.slice(0,4)))].sort((a,b)=>b-a)
      const curYearStr=String(now.getFullYear())
      const ddItem=(label,period)=>{
        const isAct=S_PERIOD===period
        const it=ddMenu.createEl("div",{attr:{style:"padding:7px 12px;border-radius:7px;cursor:pointer;font-size:0.85em;"+(isAct?"font-weight:700;background:var(--background-secondary);":"")}})
        it.textContent=label
        it.onmouseenter=()=>{if(!isAct)it.style.background="var(--background-secondary)"}
        it.onmouseleave=()=>{if(!isAct)it.style.background=""}
        it.onclick=e=>{e.stopPropagation();S_PERIOD=period;S_MONTH_OFFSET=0;ddMenu.style.display="none";renderAll()}
      }
      ddItem("Cette année","annee")
      for(const yr of availYears){if(yr!==curYearStr)ddItem(yr,yr)}
      ddItem("Tout","tout")
      ddBtn.onclick=e=>{
        e.stopPropagation()
        const opening=ddMenu.style.display==="none"
        ddMenu.style.display=opening?"block":"none"
        if(opening){
          const closeMenu=ev=>{if(!ddMenu.contains(ev.target)&&ev.target!==ddBtn){ddMenu.style.display="none";document.removeEventListener("click",closeMenu,true)}}
          setTimeout(()=>document.addEventListener("click",closeMenu,true),10)
        }
      }
    } else {
      const btn=pWrap.createEl("button"); btn.textContent=baseLabel
      btn.style.cssText=S_PERIOD===key?PILL_A:PILL_I
      btn.onclick=()=>{S_PERIOD=key;S_MONTH_OFFSET=0;renderAll()}
    }
  }

  // Plage personnalisée
  if (S_PERIOD==="custom") {
    const row2=sec.createDiv(); row2.style.cssText="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:8px 12px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:8px;"
    row2.createEl("span",{attr:{style:"font-size:0.84em;color:var(--text-muted);font-weight:600;"}}).textContent="Du"
    mkDatePicker(row2, S_CSTART, v=>{S_CSTART=v;renderAll()}, "Date début")
    row2.createEl("span",{attr:{style:"font-size:0.84em;color:var(--text-muted);font-weight:600;"}}).textContent="au"
    mkDatePicker(row2, S_CEND, v=>{S_CEND=v;renderAll()}, "Date fin")
  }

  // Commandes en attente
  if (_cmdEnAttente.length > 0) {
    const total=_cmdEnAttente.reduce((s,c)=>s+(parseFloat(c.montant)||0),0)
    const warn=sec.createDiv(); warn.style.cssText="display:flex;align-items:center;gap:8px;padding:8px 13px;background:rgba(254,100,11,0.06);border:1px solid rgba(254,100,11,0.2);border-radius:8px;font-size:0.82em;color:var(--text-muted);"
    warn.textContent=`⏳ ${_cmdEnAttente.length} commande${_cmdEnAttente.length>1?"s":""} en attente de livraison - ${fmtC(total)} non encore comptabilisé${_cmdEnAttente.length>1?"es":"e"}`
  }
}

// ── STATS BAR ─────────────────────────────────────────────────────
const _renderStats = () => {
  const sec=wrap.createDiv()
  const txP=filterTx(ALL_TX)
  const depenses_brut = txP.filter(t=>t.type==="dépense"&&!isVirement(t)&&!isEpargne(t)).reduce((s,t)=>s+Math.abs(t.montant),0)
  const avoirs_sum    = txP.filter(t=>isAvoir(t)).reduce((s,t)=>s+Math.abs(t.montant),0)
  const depenses      = depenses_brut - avoirs_sum
  const revenus       = txP.filter(t=>t.type==="revenu"&&!isVirement(t)).reduce((s,t)=>s+t.montant,0)
  const eco_depot     = txP.filter(t=>t.type==="épargne").reduce((s,t)=>s+Math.abs(t.montant),0)
  const eco_retrait   = txP.filter(t=>t.type==="épargne-retrait").reduce((s,t)=>s+t.montant,0)
  const solde_eco     = eco_depot - eco_retrait
  const solde         = getSoldeCourant()
  // Solde économies ALL TIME (indépendant de la période)
  const eco_total_depot   = ALL_TX.filter(t=>t.type==="épargne").reduce((s,t)=>s+Math.abs(t.montant),0)
  const eco_total_retrait = ALL_TX.filter(t=>t.type==="épargne-retrait").reduce((s,t)=>s+t.montant,0)
  const solde_eco_total   = eco_total_depot - eco_total_retrait

  const bar=sec.createDiv(); bar.style.cssText="display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--background-modifier-border);"
  const cells=[
    {label:"Solde actuel",   eur:solde,          color:solde>=0?"#40a02b":"#d20f39", bg:solde>=0?"rgba(64,160,43,0.08)":"rgba(210,15,57,0.08)", mode:"plain"},
    {label:"Dépenses",       eur:depenses,        color:"#d20f39", bg:"rgba(210,15,57,0.06)",   mode:"abs", sub: avoirs_sum>0?`avoirs : -${fmtC(avoirs_sum)}`:null},
    {label:"Revenus",        eur:revenus,         color:"#40a02b", bg:"rgba(64,160,43,0.06)",   mode:"plain"},
    {label:"Mis de côté",    eur:eco_depot,       color:"#8878c3", bg:"rgba(136,120,195,0.06)", mode:"plain", sub: eco_retrait>0?`pioché : -${fmtC(eco_retrait)}`:null},
    {label:"Solde économies",eur:solde_eco_total, color:"#8878c3", bg:"rgba(136,120,195,0.04)", mode:"plain"},
  ]
  cells.forEach((c,i)=>{
    const cell=bar.createDiv(); cell.style.cssText=`flex:1;padding:14px 8px;background:${c.bg};text-align:center;border-right:1px solid var(--background-modifier-border);`
    if(i===cells.length-1) cell.style.borderRight="none"
    const vEl=cell.createDiv(); vEl.style.cssText=`font-size:1.05em;font-weight:800;color:${c.color};line-height:1;margin-bottom:4px;display:flex;flex-direction:column;align-items:center;`
    if(c.mode==="rate"){ vEl.textContent=c.val; vEl.classList.add('fin-amount') }
    else mkAmountEl(vEl, c.eur, {abs:c.mode==="abs", color:c.color, fontSize:"1em"})
    const lEl=cell.createDiv(); lEl.style.cssText="font-size:0.7em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;"; lEl.textContent=c.label
    if(c.sub){ const subColor=c.label==="Économies"?"#d20f39":"#40a02b"; const subEl=cell.createEl("div",{attr:{style:`font-size:0.68em;color:${subColor};margin-top:3px;font-weight:600;`}}); subEl.textContent=c.sub; subEl.classList.add('fin-amount') }
  })
}

// ── ÉCONOMIES ─────────────────────────────────────────────────────
const _renderEconomies = () => {
  const txP = filterTx(ALL_TX)
  if (!ALL_TX.some(t=>t.type==="épargne"||t.type==="épargne-retrait"||isVirement(t))) return

  const sec = wrap.createDiv()

  // Titre section
  sec.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-bottom:10px;"}}).textContent="💰 Économies"

  // Mouvements : épargne + épargne-retrait + virements internes, triés par date desc
  const mvts = txP.filter(t=>t.type==="épargne"||t.type==="épargne-retrait"||isVirement(t))
    .slice().sort((a,b)=>b.date.localeCompare(a.date))
  if (!mvts.length) return

  // Config d'affichage par type
  const mvtStyle = t => {
    if (t.type==="épargne")         return {ico:"💰", color:"#8878c3", signed: 1}
    if (t.type==="épargne-retrait") return {ico:"💸", color:"#d20f39", signed:-1}
    if (isVirement(t)) {
      const isIn = parseFloat(t.montant) >= 0
      return {ico:"🔄", color:"#1e66f5", signed: isIn ? 1 : -1}
    }
    return {ico:"•", color:"var(--text-muted)", signed:1}
  }

  const PREVIEW = 2
  let expanded = false

  // Titre cliquable
  const histHeader = sec.createDiv()
  histHeader.style.cssText="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;cursor:pointer;user-select:none;"
  histHeader.title="Cliquer pour voir tous les mouvements"

  const histTitleEl = histHeader.createEl("span")
  histTitleEl.style.cssText="font-size:0.78em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"

  const histHint = histHeader.createEl("span")
  histHint.style.cssText="font-size:0.75em;color:var(--interactive-accent);font-weight:600;display:flex;align-items:center;gap:3px;"

  const listEl = sec.createDiv()

  const renderMvts = () => {
    listEl.empty()
    const toShow = expanded ? mvts : mvts.slice(0, PREVIEW)
    const hidden = mvts.length - PREVIEW

    // Mise à jour titre et hint
    histTitleEl.textContent = "Mouvements"
    if (expanded) {
      histHint.textContent = "Réduire ↑"
    } else if (hidden > 0) {
      histHint.textContent = `Voir tout (${mvts.length}) ↓`
    } else {
      histHint.textContent = ""
    }

    for (const t of toShow) {
      const st = mvtStyle(t)
      const row = listEl.createDiv()
      row.style.cssText="display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;margin-bottom:4px;background:var(--background-secondary);"

      const ico = row.createEl("span"); ico.style.cssText="font-size:1em;flex-shrink:0;"
      ico.textContent = st.ico

      const info = row.createDiv(); info.style.cssText="flex:1;min-width:0;"
      const lbl = info.createDiv(); lbl.style.cssText="font-weight:500;font-size:0.88em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
      lbl.textContent = t.label
      const dt = info.createDiv(); dt.style.cssText="font-size:0.75em;color:var(--text-muted);"
      // Pour virements : afficher aussi le compte
      if (isVirement(t)) {
        const cptLabel = CFG_COMPTES.find(c=>c.id===t.compte)?.label || t.compte || ""
        dt.textContent = fmtDateFr(t.date) + (cptLabel ? "  ·  " + cptLabel : "")
      } else {
        dt.textContent = fmtDateFr(t.date)
      }

      const mEl = row.createDiv(); mEl.style.cssText="font-weight:700;font-size:0.92em;flex-shrink:0;"
      const mVal = st.signed * Math.abs(parseFloat(t.montant)||0)
      mkAmountEl(mEl, mVal, {signed:true, color:st.color, fontSize:"0.92em"})
    }
  }

  histHeader.onclick = () => { expanded = !expanded; renderMvts() }
  renderMvts()
}

// ── GRAPHIQUE INTERACTIF ──────────────────────────────────────────
const _renderChart = () => {
  const sec=wrap.createDiv()
  sec.style.cssText="position:relative;"
  const [startStr,endStr]=getPeriodRange()

  // ── Vue "Tout" : graphique mensuel agrégé ─────────────────────
  if (S_PERIOD === "tout") {
    const txForCompte=getTxForCompte()
    if(!txForCompte.length) return
    const titleRow=sec.createDiv(); titleRow.style.cssText="display:flex;align-items:center;margin-bottom:10px;"
    titleRow.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"}}).textContent="📈 Évolution du solde - vue globale"
    const allDates=txForCompte.map(t=>t.date).sort()
    const firstMo=allDates[0].slice(0,7), lastMo=allDates[allDates.length-1].slice(0,7)
    const months=[]
    let [my,mm]=[parseInt(firstMo.slice(0,4)),parseInt(firstMo.slice(5,7))]
    const [ey,em]=[parseInt(lastMo.slice(0,4)),parseInt(lastMo.slice(5,7))]
    while(my<ey||(my===ey&&mm<=em)){months.push(`${my}-${String(mm).padStart(2,'0')}`);mm++;if(mm>12){mm=1;my++}}
    const txByMonth={}
    for(const t of txForCompte){
      const mo=t.date.slice(0,7)
      if(!txByMonth[mo])txByMonth[mo]={income:0,expense:0,net:0}
      const m=parseFloat(t.montant)||0; txByMonth[mo].net+=m
      if(m>0)txByMonth[mo].income+=m; else txByMonth[mo].expense+=Math.abs(m)
    }
    let bal=getSoldeInitial()
    const points=[{month:null,balance:bal}]
    for(const mo of months){const md=txByMonth[mo];bal+=md?md.net:0;points.push({month:mo,balance:bal,monthData:md||null})}
    const _cont=dv.container.closest(".markdown-preview-section,.markdown-rendered,.cm-preview-code-block")||dv.container.parentElement||dv.container
    const W=Math.max(400,(_cont.offsetWidth||_cont.clientWidth||dv.container.offsetWidth||window.innerWidth)-24)
    const BAR_AREA=50,X_LBL_H=20,H=300
    const PAD={top:20,right:20,bottom:X_LBL_H+BAR_AREA+14,left:72}
    const cw=W-PAD.left-PAD.right, ch=H-PAD.top-PAD.bottom
    const dpr=window.devicePixelRatio||1
    const canvas=sec.createEl("canvas")
    canvas.width=W*dpr; canvas.height=H*dpr
    canvas.style.cssText="width:100%;height:"+H+"px;display:block;cursor:crosshair;"
    canvas.classList.add('fin-amount')
    const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr)
    const n=points.length
    const vals=points.map(p=>p.balance)
    const minV=Math.min(...vals),maxV=Math.max(...vals)
    const range=maxV-minV||Math.abs(maxV)||1
    const vMin=minV-range*0.18,vMax=maxV+range*0.18
    const xOf=i=>PAD.left+(i/(n-1||1))*cw
    const yOf=v=>PAD.top+ch-((v-vMin)/(vMax-vMin))*ch
    const cs=getComputedStyle(document.body)
    const borderC=cs.getPropertyValue("--background-modifier-border").trim()||"#e0e0e0"
    const mutedC=cs.getPropertyValue("--text-muted").trim()||"#888"
    const lineC=cs.getPropertyValue("--interactive-accent").trim()||"#1e66f5"
    const RED_C="#d20f39"
    ctx.strokeStyle=borderC+"55"; ctx.lineWidth=1; ctx.setLineDash([])
    for(let i=0;i<=3;i++){
      const v=vMin+(vMax-vMin)*(i/3),y=yOf(v)
      ctx.beginPath();ctx.moveTo(PAD.left,y);ctx.lineTo(W-PAD.right,y);ctx.stroke()
      ctx.fillStyle=v<-0.5?RED_C:mutedC; ctx.font=_axisFont()+"px 'Inter',sans-serif"; ctx.textAlign="right"
      ctx.fillText(fmtC0(v),PAD.left-5,y+4)
    }
    if(vMin<0&&vMax>0){ctx.strokeStyle=RED_C+"55";ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(PAD.left,yOf(0));ctx.lineTo(W-PAD.right,yOf(0));ctx.stroke();ctx.setLineDash([])}
    const grad=ctx.createLinearGradient(0,PAD.top,0,PAD.top+ch)
    grad.addColorStop(0,lineC+"44"); grad.addColorStop(1,lineC+"04")
    ctx.beginPath();ctx.moveTo(xOf(0),yOf(points[0].balance))
    for(let i=1;i<n;i++)ctx.lineTo(xOf(i),yOf(points[i].balance))
    ctx.lineTo(xOf(n-1),PAD.top+ch);ctx.lineTo(xOf(0),PAD.top+ch);ctx.closePath();ctx.fillStyle=grad;ctx.fill()
    ctx.lineWidth=2.5;ctx.lineJoin="round";ctx.setLineDash([])
    const y0=yOf(0)
    for(let i=1;i<n;i++){
      const p0=points[i-1],p1=points[i],neg0=p0.balance<0,neg1=p1.balance<0
      if(neg0===neg1){ctx.strokeStyle=neg0?RED_C:lineC;ctx.beginPath();ctx.moveTo(xOf(i-1),yOf(p0.balance));ctx.lineTo(xOf(i),yOf(p1.balance));ctx.stroke()}
      else{const b0=p0.balance,b1=p1.balance,t=b0/(b0-b1),xC=xOf(i-1)+t*(xOf(i)-xOf(i-1));ctx.strokeStyle=neg0?RED_C:lineC;ctx.beginPath();ctx.moveTo(xOf(i-1),yOf(b0));ctx.lineTo(xC,y0);ctx.stroke();ctx.strokeStyle=neg1?RED_C:lineC;ctx.beginPath();ctx.moveTo(xC,y0);ctx.lineTo(xOf(i),yOf(b1));ctx.stroke()}
    }
    const lastBal=points[n-1].balance,lx=xOf(n-1),ly=yOf(lastBal),bubbleC=lastBal<0?RED_C:lineC
    ctx.beginPath();ctx.arc(lx,ly,4.5,0,Math.PI*2);ctx.fillStyle=bubbleC;ctx.fill()
    const labelText=(lastBal<0?"-":"")+fmtC(lastBal); ctx.font="bold 13px 'Inter',sans-serif"
    const tw=ctx.measureText(labelText).width,lPad=7,lH=20,lR=5
    const bY=ly-14-lH/2>=PAD.top?ly-14:ly+24
    const bX=Math.min(lx,W-PAD.right-tw/2-lPad-2)
    const rx=bX-tw/2-lPad,ry=bY-lH/2,rw=tw+lPad*2,rh=lH
    ctx.fillStyle=bubbleC;ctx.beginPath();ctx.moveTo(rx+lR,ry);ctx.lineTo(rx+rw-lR,ry);ctx.arcTo(rx+rw,ry,rx+rw,ry+lR,lR);ctx.lineTo(rx+rw,ry+rh-lR);ctx.arcTo(rx+rw,ry+rh,rx+rw-lR,ry+rh,lR);ctx.lineTo(rx+lR,ry+rh);ctx.arcTo(rx,ry+rh,rx,ry+rh-lR,lR);ctx.lineTo(rx,ry+lR);ctx.arcTo(rx,ry,rx+lR,ry,lR);ctx.closePath();ctx.fill()
    ctx.fillStyle="#fff";ctx.textAlign="center";ctx.fillText(labelText,bX,bY+4)
    const xLabelY=PAD.top+ch+X_LBL_H-4
    ctx.fillStyle=mutedC; ctx.font="13px 'Inter',sans-serif"; ctx.textAlign="center"; ctx.setLineDash([])
    for(let i=1;i<n;i++){
      const mo=points[i].month; if(!mo) continue
      const [yr,m]=mo.split('-'); const mInt=parseInt(m)
      if(m==="01"||(n<=13)||(n<=25&&mInt%6===1)){ctx.fillText(m==="01"?yr:MONTHS_LONG[mInt-1].slice(0,3),xOf(i),xLabelY)}
    }
    const barAreaTop=PAD.top+ch+X_LBL_H+6,barAreaBot=H-6,barMid=(barAreaTop+barAreaBot)/2,barHalfH=(barAreaBot-barAreaTop)/2-2
    ctx.strokeStyle=borderC+"66";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(PAD.left,barAreaTop-3);ctx.lineTo(W-PAD.right,barAreaTop-3);ctx.stroke()
    const maxBarV=Math.max(...Object.values(txByMonth).map(d=>Math.max(d.income,d.expense)),0.01)
    const barW=Math.max(2,Math.min(14,(cw/Math.max(months.length,1))*0.65))
    for(let i=1;i<n;i++){const mo=points[i].month;if(!mo)continue;const md=txByMonth[mo];if(!md)continue;const bx=xOf(i);if(md.income>0){const bh=Math.max(2,(md.income/maxBarV)*barHalfH);ctx.fillStyle="#40a02b99";ctx.fillRect(bx-barW/2,barMid-bh,barW,bh)}if(md.expense>0){const bh=Math.max(2,(md.expense/maxBarV)*barHalfH);ctx.fillStyle="#d20f3999";ctx.fillRect(bx-barW/2,barMid,barW,bh)}}
    ctx.font="11px 'Inter',sans-serif";ctx.textAlign="right";ctx.fillStyle="#40a02bbb";ctx.fillText("↑",PAD.left-5,barMid-3);ctx.fillStyle="#d20f39bb";ctx.fillText("↓",PAD.left-5,barMid+13)
    const cursorLine=sec.createEl("div"); cursorLine.style.cssText="display:none;position:absolute;width:1px;background:var(--text-muted);opacity:0.35;pointer-events:none;"
    const tooltip=sec.createEl("div"); tooltip.style.cssText="display:none;position:absolute;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:9px 13px;font-size:0.8em;pointer-events:none;z-index:100;box-shadow:0 4px 18px rgba(0,0,0,0.2);min-width:150px;max-width:230px;"
    canvas.addEventListener("mousemove",e=>{
      const rect=canvas.getBoundingClientRect(),scaleX=W/rect.width,scaleY=H/rect.height
      const mx=(e.clientX-rect.left)*scaleX
      if(mx<PAD.left||mx>W-PAD.right){tooltip.style.display="none";cursorLine.style.display="none";return}
      const idx=Math.max(0,Math.min(n-1,Math.round((mx-PAD.left)/cw*(n-1))))
      const pt=points[idx]; tooltip.empty()
      if(pt.month){const[yr,m]=pt.month.split('-');tooltip.createEl("div",{attr:{style:"font-weight:700;margin-bottom:5px;color:var(--text-normal);border-bottom:1px solid var(--background-modifier-border);padding-bottom:5px;"}}).textContent=MONTHS_LONG[parseInt(m)-1]+" "+yr}
      const balColor=pt.balance>=0?"#40a02b":RED_C
      const bRow=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:3px;"}}); bRow.createEl("span",{attr:{style:"color:var(--text-muted);"}}).textContent="Solde"; bRow.createEl("span",{attr:{style:`font-weight:700;color:${balColor};`}}).textContent=fmtC(pt.balance)
      if(pt.monthData){const md=pt.monthData;if(md.income>0){const r=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:2px;"}});r.createEl("span",{attr:{style:"color:#40a02b;"}}).textContent="↑ Entrées";r.createEl("span",{attr:{style:"font-weight:600;color:#40a02b;"}}).textContent="+"+fmtC(md.income)}if(md.expense>0){const r=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;"}});r.createEl("span",{attr:{style:"color:#d20f39;"}}).textContent="↓ Sorties";r.createEl("span",{attr:{style:"font-weight:600;color:#d20f39;"}}).textContent="-"+fmtC(md.expense)}}
      const ptXDisp=xOf(idx)/scaleX,canvTop=canvas.offsetTop,canvLeft=canvas.offsetLeft
      let txLeft=canvLeft+ptXDisp+14; if(txLeft+230>sec.offsetWidth-4)txLeft=canvLeft+ptXDisp-230-14
      tooltip.style.display="block"; tooltip.style.left=Math.max(0,txLeft)+"px"; tooltip.style.top=(canvTop+PAD.top/scaleY)+"px"
      cursorLine.style.display="block"; cursorLine.style.left=(canvLeft+ptXDisp)+"px"; cursorLine.style.top=(canvTop+PAD.top/scaleY)+"px"; cursorLine.style.height=(ch/scaleY)+"px"
    })
    canvas.addEventListener("mouseleave",()=>{tooltip.style.display="none";cursorLine.style.display="none"})
    return
  }

  if(!startStr||!endStr) return

  const titleRow=sec.createDiv(); titleRow.style.cssText="display:flex;align-items:center;margin-bottom:10px;"
  titleRow.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"}}).textContent="📈 Évolution du solde"

  const txForCompte=getTxForCompte()
  const txBefore=txForCompte.filter(t=>t.date<startStr)
  let balStart=getSoldeInitial()+txBefore.reduce((s,t)=>s+(parseFloat(t.montant)||0),0)

  const days=[]
  const cur=new Date(startStr+"T00:00:00"), endD=new Date(endStr+"T00:00:00")
  while(cur<=endD){days.push(localStr(cur));cur.setDate(cur.getDate()+1)}
  if(days.length===0){sec.createEl("p",{attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent="Aucune donnée.";return}

  const txByDate={}
  for(const t of txForCompte.filter(t=>t.date>=startStr&&t.date<=endStr)){
    if(!txByDate[t.date])txByDate[t.date]={income:0,expense:0,net:0,items:[]}
    const m=parseFloat(t.montant)||0
    txByDate[t.date].net+=m
    if(m>0) txByDate[t.date].income+=m
    else txByDate[t.date].expense+=Math.abs(m)
    txByDate[t.date].items.push(t)
  }

  let bal=balStart
  const points=[{date:startStr,balance:balStart,hasTx:false,dayData:null}]
  for(const d of days){
    const dd=txByDate[d]
    bal+=dd?dd.net:0
    points.push({date:d,balance:bal,hasTx:!!dd,dayData:dd||null})
  }

  const _cont=dv.container.closest(".markdown-preview-section,.markdown-rendered,.cm-preview-code-block")||dv.container.parentElement||dv.container
  const W=Math.max(400,(_cont.offsetWidth||_cont.clientWidth||dv.container.offsetWidth||window.innerWidth)-24)
  const BAR_AREA=50, X_LBL_H=20, H=300
  const PAD={top:20,right:20,bottom:X_LBL_H+BAR_AREA+14,left:72}
  const cw=W-PAD.left-PAD.right, ch=H-PAD.top-PAD.bottom

  const dpr=window.devicePixelRatio||1
  const canvas=sec.createEl("canvas")
  canvas.width=W*dpr; canvas.height=H*dpr
  canvas.style.cssText="width:100%;height:"+H+"px;display:block;cursor:crosshair;"
  canvas.classList.add('fin-amount')
  const ctx=canvas.getContext("2d")
  ctx.scale(dpr,dpr)

  const vals=points.map(p=>p.balance)
  const minV=Math.min(...vals), maxV=Math.max(...vals)
  const range=maxV-minV||Math.abs(maxV)||1
  const vMin=minV-range*0.18, vMax=maxV+range*0.18

  const xOf=i=>PAD.left+(i/(points.length-1||1))*cw
  const yOf=v=>PAD.top+ch-((v-vMin)/(vMax-vMin))*ch

  const cs=getComputedStyle(document.body)
  const borderC=cs.getPropertyValue("--background-modifier-border").trim()||"#e0e0e0"
  const mutedC =cs.getPropertyValue("--text-muted").trim()||"#888"
  const bgPrimC=cs.getPropertyValue("--background-primary").trim()||"#fff"
  // Couleur neutre = accent du thème (pas rouge/vert selon direction du solde)
  const lineC=cs.getPropertyValue("--interactive-accent").trim()||"#1e66f5"

  const RED_C = "#d20f39"
  // Grid
  ctx.strokeStyle=borderC+"55"; ctx.lineWidth=1; ctx.setLineDash([])
  const gridN=3
  for(let i=0;i<=gridN;i++){
    const v=vMin+(vMax-vMin)*(i/gridN), y=yOf(v)
    ctx.beginPath();ctx.moveTo(PAD.left,y);ctx.lineTo(W-PAD.right,y);ctx.stroke()
    const isNeg=v<-0.5
    ctx.fillStyle=isNeg?RED_C:mutedC; ctx.font=_axisFont()+"px 'Inter',sans-serif"; ctx.textAlign="right"
    ctx.fillText(fmtC0(v),PAD.left-5,y+4)
  }
  if(vMin<0&&vMax>0){
    ctx.strokeStyle=RED_C+"55"; ctx.setLineDash([4,3])
    ctx.beginPath();ctx.moveTo(PAD.left,yOf(0));ctx.lineTo(W-PAD.right,yOf(0));ctx.stroke()
    ctx.setLineDash([])
  }

  // Gradient fill
  const grad=ctx.createLinearGradient(0,PAD.top,0,PAD.top+ch)
  grad.addColorStop(0,lineC+"44"); grad.addColorStop(1,lineC+"04")
  ctx.beginPath(); ctx.moveTo(xOf(0),yOf(points[0].balance))
  for(let i=1;i<points.length;i++) ctx.lineTo(xOf(i),yOf(points[i].balance))
  ctx.lineTo(xOf(points.length-1),PAD.top+ch); ctx.lineTo(xOf(0),PAD.top+ch)
  ctx.closePath(); ctx.fillStyle=grad; ctx.fill()

  // Ligne solde - bleue au-dessus de 0, rouge en dessous, avec interpolation au passage à zéro
  ctx.lineWidth=2.5; ctx.lineJoin="round"; ctx.setLineDash([])
  const y0=yOf(0)
  let segStart=0
  const drawLineSeg=(from,to)=>{
    if(from>=to) return
    const p0=points[from], p1=points[to]
    const neg0=p0.balance<0, neg1=p1.balance<0
    // Même signe sur tout le segment
    if(neg0===neg1){
      ctx.strokeStyle=neg0?RED_C:lineC
      ctx.beginPath(); ctx.moveTo(xOf(from),yOf(p0.balance))
      for(let k=from+1;k<=to;k++) ctx.lineTo(xOf(k),yOf(points[k].balance))
      ctx.stroke()
    } else {
      // Interpolation du point de croisement zéro
      const x0=xOf(from),x1=xOf(to),b0=p0.balance,b1=p1.balance
      const t=b0/(b0-b1), xCross=x0+t*(x1-x0)
      // Premier demi-segment
      ctx.strokeStyle=neg0?RED_C:lineC
      ctx.beginPath(); ctx.moveTo(x0,yOf(b0)); ctx.lineTo(xCross,y0); ctx.stroke()
      // Second demi-segment
      ctx.strokeStyle=neg1?RED_C:lineC
      ctx.beginPath(); ctx.moveTo(xCross,y0); ctx.lineTo(x1,yOf(b1)); ctx.stroke()
    }
  }
  // Dessiner chaque transition de point en point
  for(let i=1;i<points.length;i++) drawLineSeg(i-1,i)

  // Marqueurs jours avec transactions (vert si entrée nette, rouge si sortie nette)
  for(let i=1;i<points.length;i++){
    if(!points[i].hasTx) continue
    const mx=xOf(i), my=yOf(points[i].balance)
    const dotC=points[i].dayData.net>=0?"#40a02b":"#d20f39"
    ctx.beginPath(); ctx.arc(mx,my,4.5,0,Math.PI*2)
    ctx.fillStyle=bgPrimC; ctx.fill()
    ctx.strokeStyle=dotC; ctx.lineWidth=2; ctx.stroke()
  }

  // Bulle solde final
  const lastBal=points[points.length-1].balance
  const lx=xOf(points.length-1), ly=yOf(lastBal)
  const bubbleC=lastBal<0?RED_C:lineC
  ctx.beginPath();ctx.arc(lx,ly,4.5,0,Math.PI*2);ctx.fillStyle=bubbleC;ctx.fill()
  const labelText=(lastBal<0?"-":"")+fmtC(lastBal)
  ctx.font="bold 13px 'Inter',sans-serif"
  const tw=ctx.measureText(labelText).width
  const lPad=7,lH=20,lR=5
  const aboveY=ly-14,belowY=ly+24
  const bubbleY=aboveY-lH/2>=PAD.top?aboveY:belowY
  const bubbleX=Math.min(lx,W-PAD.right-tw/2-lPad-2)
  const rx=bubbleX-tw/2-lPad,ry=bubbleY-lH/2,rw=tw+lPad*2,rh=lH
  ctx.fillStyle=bubbleC; ctx.beginPath()
  ctx.moveTo(rx+lR,ry); ctx.lineTo(rx+rw-lR,ry)
  ctx.arcTo(rx+rw,ry,rx+rw,ry+lR,lR); ctx.lineTo(rx+rw,ry+rh-lR)
  ctx.arcTo(rx+rw,ry+rh,rx+rw-lR,ry+rh,lR); ctx.lineTo(rx+lR,ry+rh)
  ctx.arcTo(rx,ry+rh,rx,ry+rh-lR,lR); ctx.lineTo(rx,ry+lR)
  ctx.arcTo(rx,ry,rx+lR,ry,lR); ctx.closePath(); ctx.fill()
  ctx.fillStyle="#fff"; ctx.textAlign="center"
  ctx.fillText(labelText,bubbleX,bubbleY+4)

  // Labels axe X
  const xLabelY=PAD.top+ch+X_LBL_H-4
  const maxLbl=Math.min(10,days.length)
  const stepX=Math.max(1,Math.floor(days.length/maxLbl))
  ctx.fillStyle=mutedC; ctx.font="14px 'Inter',sans-serif"; ctx.textAlign="center"; ctx.setLineDash([])
  for(let i=1;i<points.length;i+=stepX){
    const [,m,d]=points[i].date.split("-")
    ctx.fillText(`${d}/${m}`,xOf(i),xLabelY)
  }

  // Mini barres revenus/dépenses
  const barAreaTop=PAD.top+ch+X_LBL_H+6, barAreaBot=H-6
  const barMid=(barAreaTop+barAreaBot)/2, barHalfH=(barAreaBot-barAreaTop)/2-2
  ctx.strokeStyle=borderC+"66"; ctx.lineWidth=1
  ctx.beginPath();ctx.moveTo(PAD.left,barAreaTop-3);ctx.lineTo(W-PAD.right,barAreaTop-3);ctx.stroke()
  const allDayVals=Object.values(txByDate)
  const maxBarV=Math.max(...allDayVals.map(d=>Math.max(d.income,d.expense)),0.01)
  const barW=Math.max(2,Math.min(14,(cw/Math.max(days.length,1))*0.65))
  for(let i=1;i<points.length;i++){
    const d=points[i].date, dd=txByDate[d]; if(!dd) continue
    const bx=xOf(i)
    if(dd.income>0){const bh=Math.max(2,(dd.income/maxBarV)*barHalfH);ctx.fillStyle="#40a02b99";ctx.fillRect(bx-barW/2,barMid-bh,barW,bh)}
    if(dd.expense>0){const bh=Math.max(2,(dd.expense/maxBarV)*barHalfH);ctx.fillStyle="#d20f3999";ctx.fillRect(bx-barW/2,barMid,barW,bh)}
  }
  ctx.font="11px 'Inter',sans-serif"; ctx.textAlign="right"
  ctx.fillStyle="#40a02bbb"; ctx.fillText("↑",PAD.left-5,barMid-3)
  ctx.fillStyle="#d20f39bb"; ctx.fillText("↓",PAD.left-5,barMid+13)

  // Curseur + Tooltip
  const cursorLine=sec.createEl("div")
  cursorLine.style.cssText="display:none;position:absolute;width:1px;background:var(--text-muted);opacity:0.35;pointer-events:none;"
  const tooltip=sec.createEl("div")
  tooltip.style.cssText="display:none;position:absolute;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:9px 13px;font-size:0.8em;pointer-events:none;z-index:100;box-shadow:0 4px 18px rgba(0,0,0,0.2);min-width:150px;max-width:230px;"

  canvas.addEventListener("mousemove",e=>{
    const rect=canvas.getBoundingClientRect()
    const scaleX=W/rect.width, scaleY=H/rect.height
    const mx=(e.clientX-rect.left)*scaleX
    if(mx<PAD.left||mx>W-PAD.right){tooltip.style.display="none";cursorLine.style.display="none";return}
    const idx=Math.max(0,Math.min(points.length-1,Math.round((mx-PAD.left)/cw*(points.length-1))))
    const pt=points[idx]
    tooltip.empty()
    const [yr,mo,dy]=pt.date.split("-")
    tooltip.createEl("div",{attr:{style:"font-weight:700;margin-bottom:5px;color:var(--text-normal);border-bottom:1px solid var(--background-modifier-border);padding-bottom:5px;"}}).textContent=`${dy}/${mo}/${yr}`
    const balColor=pt.balance>=0?"#40a02b":"#d20f39"
    const bRow=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:3px;"}})
    bRow.createEl("span",{attr:{style:"color:var(--text-muted);"}}).textContent="Solde"
    bRow.createEl("span",{attr:{style:`font-weight:700;color:${balColor};`}}).textContent=fmtC(pt.balance)
    if(pt.hasTx&&pt.dayData){
      const dd=pt.dayData
      if(dd.income>0){const r=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:2px;"}});r.createEl("span",{attr:{style:"color:#40a02b;"}}).textContent="↑ Entrées";r.createEl("span",{attr:{style:"font-weight:600;color:#40a02b;"}}).textContent="+"+fmtC(dd.income)}
      if(dd.expense>0){const r=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:2px;"}});r.createEl("span",{attr:{style:"color:#d20f39;"}}).textContent="↓ Sorties";r.createEl("span",{attr:{style:"font-weight:600;color:#d20f39;"}}).textContent="-"+fmtC(dd.expense)}
      tooltip.createEl("div",{attr:{style:"border-top:1px solid var(--background-modifier-border);margin-top:5px;padding-top:4px;"}})
      for(const tx of dd.items.slice(0,4)){
        const txRow=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:8px;margin-top:2px;"}})
        txRow.createEl("span",{attr:{style:"color:var(--text-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;"}}).textContent=tx.label
        const tm=parseFloat(tx.montant)||0
        txRow.createEl("span",{attr:{style:"font-weight:600;white-space:nowrap;color:"+(tm>=0?"#40a02b":"#d20f39")+";"}}).textContent=(tm>=0?"+":"")+fmtC(tm)
      }
      if(dd.items.length>4) tooltip.createEl("div",{attr:{style:"font-size:0.85em;color:var(--text-muted);margin-top:2px;"}}).textContent=`+${dd.items.length-4} autre(s)…`
    }
    const ptXDisp=xOf(idx)/scaleX, ptYDisp=yOf(pt.balance)/scaleY
    const canvTop=canvas.offsetTop, canvLeft=canvas.offsetLeft
    let txLeft=canvLeft+ptXDisp+14
    if(txLeft+230>sec.offsetWidth-4) txLeft=canvLeft+ptXDisp-230-14
    tooltip.style.display="block"
    tooltip.style.left=Math.max(0,txLeft)+"px"
    tooltip.style.top=Math.max(canvTop,canvTop+ptYDisp-20)+"px"
    cursorLine.style.display="block"
    cursorLine.style.left=(canvLeft+ptXDisp)+"px"
    cursorLine.style.top=(canvTop+PAD.top/scaleY)+"px"
    cursorLine.style.height=(ch/scaleY)+"px"
  })
  canvas.addEventListener("mouseleave",()=>{tooltip.style.display="none";cursorLine.style.display="none"})
}

// ── DONUT RÉPARTITION DÉPENSES ────────────────────────────────────
const _renderDonut = () => {
  const txP = filterTx(ALL_TX).filter(t => t.type === "dépense" && !isVirement(t))
  if (!txP.length) return

  // Palette — couleurs stables par catégorie (ordre du frontmatter en priorité, puis hash pour les nouvelles)
  const PAL = ["#1e66f5","#8839ef","#d20f39","#fe640b","#df8e1d","#40a02b","#04a5e5","#ea76cb","#179299","#dd7878","#7287fd","#e64553"]
  const knownOrder = [...CATS_DEPENSE, "📦 Commandes"]
  const catColorMap = {}
  knownOrder.forEach((c, i) => { catColorMap[c] = PAL[i % PAL.length] })
  // Couleur déterministe pour une catégorie inconnue (hash → palette)
  const hashColor = s => { let h=0; for(const c of s) h=(h*31+c.charCodeAt(0))>>>0; return PAL[h % PAL.length] }
  const getColor = c => c === "Autre" ? "#a0a0a0" : (catColorMap[c] ?? hashColor(c))

  // Agrégation dynamique : toutes les catégories présentes dans les transactions
  // Seules les transactions sans catégorie ou avec "❓ Autre" vont dans le bucket "Autre"
  const bycat = {}
  for (const t of txP) {
    const c = (t.categorie && t.categorie !== "❓ Autre") ? t.categorie : "Autre"
    bycat[c] = (bycat[c]||0) + Math.abs(t.montant)
  }
  const total = Object.values(bycat).reduce((s,v)=>s+v, 0)
  if (!total) return

  // Ordre : catégories du frontmatter d'abord (si présentes), puis nouvelles catégories triées par montant, "Autre" en dernier
  const knownPresent = knownOrder.filter(c => (bycat[c]||0) > 0).map(c => [c, bycat[c]])
  const extraCats = Object.entries(bycat)
    .filter(([c]) => !knownOrder.includes(c) && c !== "Autre")
    .sort((a,b) => b[1] - a[1])
  const autreBucket = bycat["Autre"] > 0 ? [["Autre", bycat["Autre"]]] : []
  const ents = [...knownPresent, ...extraCats, ...autreBucket]
  const colors = ents.map(([c]) => getColor(c))

  const cs=getComputedStyle(document.body)
  const textNorm=cs.getPropertyValue("--text-normal").trim()||"#333"
  const textMut =cs.getPropertyValue("--text-muted").trim()||"#888"
  const bgPrim  =cs.getPropertyValue("--background-primary").trim()||"#fff"

  let cum=0
  const segs=ents.map(([cat,val],i)=>{
    const a=(val/total)*Math.PI*2
    const sg={cat,val,s:cum,e:cum+a,col:colors[i]}; cum+=a; return sg
  })

  // ── MODE TOUT : donut agrandi centré avec hover interactif ────────
  if (S_PERIOD === "tout") {
    const sec=wrap.createDiv()
    const _compteLabel = S_COMPTE === "tout" ? "tous les comptes" : (CFG_COMPTES.find(c=>c.id===S_COMPTE)?.label || S_COMPTE)
    sec.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-bottom:14px;"}}).textContent="🥧 Répartition des dépenses · " + _compteLabel

    const _cont=dv.container.closest(".markdown-preview-section,.markdown-rendered,.cm-preview-code-block")||dv.container.parentElement||dv.container
    const availW=Math.max(400,(_cont.offsetWidth||_cont.clientWidth||window.innerWidth)-24)
    const SZ=Math.min(400,Math.max(180,Math.round(availW*0.45)))
    const _tcG=document.createElement("canvas").getContext("2d"),_amtStrG=fmtC(total)
    let _ctrFzG=Math.round(SZ*0.075)
    {const hole=(SZ/2-12)*0.52*2;while(_ctrFzG>11){_tcG.font=`bold ${_ctrFzG}px 'Inter',sans-serif`;if(_tcG.measureText(_amtStrG).width<=hole*0.82)break;_ctrFzG--}}
    const _subFzG=Math.min(Math.round(SZ*0.057),Math.max(10,_ctrFzG-2)),_dyG1=Math.round(_ctrFzG/2+3),_dyG2=Math.round(_subFzG/2+4)
    const dpr=window.devicePixelRatio||1
    const cx=SZ/2, cy=SZ/2, R=SZ/2-12, ri=R*0.52

    const outer=sec.createDiv(); outer.style.cssText="display:flex;gap:32px;align-items:center;flex-wrap:wrap;justify-content:center;"
    const canvasWrap=outer.createDiv(); canvasWrap.style.cssText="position:relative;flex-shrink:0;"
    const canvas=canvasWrap.createEl("canvas")
    canvas.width=SZ*dpr; canvas.height=SZ*dpr
    canvas.style.cssText=`width:${SZ}px;height:${SZ}px;display:block;cursor:default;`
    canvas.classList.add('fin-amount')
    const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr)

    const legRows=[]

    // ── Animation state ───────────────────────────────────────────
    const N=segs.length
    const alphas=new Float32Array(N).fill(1)
    const exps  =new Float32Array(N).fill(0)
    let hovIdx=-1, animId=null
    const EASE=0.16, EXP_MAX=8

    const drawFrame=()=>{
      if(!canvas.isConnected){animId=null;return}
      ctx.clearRect(0,0,SZ,SZ)
      for(let i=0;i<N;i++){
        const sg=segs[i], exp=exps[i]
        const mid=(sg.s+sg.e)/2-Math.PI/2
        ctx.beginPath()
        ctx.moveTo(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid))
        ctx.arc(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid),R,sg.s-Math.PI/2,sg.e-Math.PI/2)
        ctx.arc(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid),ri,sg.e-Math.PI/2,sg.s-Math.PI/2,true)
        ctx.closePath()
        ctx.globalAlpha=alphas[i]; ctx.fillStyle=sg.col; ctx.fill()
        ctx.globalAlpha=1; ctx.strokeStyle=bgPrim; ctx.lineWidth=2; ctx.stroke()
      }
      ctx.textAlign="center"; ctx.textBaseline="middle"
      const hs=hovIdx>=0?segs[hovIdx]:null
      const ta=hovIdx>=0?alphas[hovIdx]:1  // fade text proportionnellement
      ctx.globalAlpha=ta
      if(hs){
        ctx.font=`bold ${_ctrFzG}px 'Inter',sans-serif`; ctx.fillStyle=textNorm
        ctx.fillText(fmtC(hs.val),cx,cy-_dyG1)
        ctx.font=`bold ${Math.round(SZ*0.065)}px 'Inter',sans-serif`; ctx.fillStyle=hs.col
        ctx.fillText(Math.round((hs.val/total)*100)+"%",cx,cy+10)
        ctx.font=`${Math.round(SZ*0.052)}px 'Inter',sans-serif`; ctx.fillStyle=textMut
        ctx.fillText(hs.cat.length>18?hs.cat.slice(0,17)+"…":hs.cat,cx,cy+28)
      } else {
        ctx.font=`bold ${_ctrFzG}px 'Inter',sans-serif`; ctx.fillStyle=textNorm
        ctx.fillText(fmtC(total),cx,cy-_dyG1)
        ctx.font=`${_subFzG}px 'Inter',sans-serif`; ctx.fillStyle=textMut
        ctx.fillText("total dépenses",cx,cy+_dyG2)
      }
      ctx.globalAlpha=1
    }

    const animate=()=>{
      if(!canvas.isConnected){animId=null;return}
      let busy=false
      for(let i=0;i<N;i++){
        const tA=hovIdx>=0&&i!==hovIdx?0.18:1
        const tE=hovIdx===i?EXP_MAX:0
        const na=alphas[i]+(tA-alphas[i])*EASE
        const ne=exps[i]  +(tE-exps[i])  *EASE
        if(Math.abs(na-alphas[i])>0.002||Math.abs(ne-exps[i])>0.05) busy=true
        alphas[i]=na; exps[i]=ne
      }
      // Légende : CSS transition s'en charge
      legRows.forEach((r,i)=>{r.style.opacity=hovIdx>=0&&i!==hovIdx?"0.2":"1"})
      drawFrame()
      animId=busy?requestAnimationFrame(animate):null
    }

    const setHover=(idx)=>{
      if(idx===hovIdx)return
      hovIdx=idx
      if(!animId) animId=requestAnimationFrame(animate)
    }

    canvas.addEventListener("mousemove",e=>{
      const rect=canvas.getBoundingClientRect(), scaleX=SZ/rect.width
      const mx=(e.clientX-rect.left)*scaleX-cx, my=(e.clientY-rect.top)*scaleX-cy
      const dist=Math.sqrt(mx*mx+my*my)
      if(dist<ri||dist>R+10){setHover(-1);return}
      let a=(Math.atan2(my,mx)+Math.PI/2+Math.PI*4)%(Math.PI*2)
      setHover(segs.findIndex(sg=>a>=sg.s&&a<sg.e))
    })
    canvas.addEventListener("mouseleave",()=>setHover(-1))
    drawFrame()

    // Légende
    const leg=outer.createDiv()
    leg.style.cssText="display:grid;grid-template-columns:repeat(2,auto);gap:6px 24px;align-content:start;"
    for(const [i,[cat,val]] of ents.entries()){
      const pct=Math.round((val/total)*100)
      const row=leg.createDiv(); row.style.cssText="display:flex;align-items:center;gap:7px;min-width:0;cursor:default;transition:opacity 0.18s;"
      legRows.push(row)
      row.createDiv().style.cssText=`width:10px;height:10px;border-radius:50%;background:${colors[i]};flex-shrink:0;`
      const lbl=row.createDiv(); lbl.style.cssText="font-size:0.82em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-normal);"
      lbl.textContent=cat
      const amtSpan=row.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);white-space:nowrap;margin-left:2px;"}}); amtSpan.textContent=fmtC(val); amtSpan.classList.add('fin-amount')
      const pctSpan=row.createEl("span",{attr:{style:"font-size:0.76em;color:var(--text-muted);opacity:0.7;white-space:nowrap;"}}); pctSpan.textContent=" "+pct+"%"; pctSpan.classList.add('fin-amount')
      row.addEventListener("mouseenter",()=>setHover(i))
      row.addEventListener("mouseleave",()=>setHover(-1))
    }
    return
  }

  // ── MODE NORMAL : donut compact ───────────────────────────────────
  const sec = wrap.createDiv()
  sec.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-bottom:10px;"}}).textContent="🥧 Répartition des dépenses"
  const cont = sec.createDiv(); cont.style.cssText="display:inline-flex;gap:24px;align-items:center;flex-wrap:wrap;max-width:100%;"

  const dpr=window.devicePixelRatio||1
  const _tc=document.createElement("canvas").getContext("2d"),_amtStr=fmtC(total)
  const SZ=190
  let _ctrFz=Math.round(SZ*0.09)
  {const hole=(SZ/2-8)*0.54*2;while(_ctrFz>10){_tc.font=`bold ${_ctrFz}px 'Inter',sans-serif`;if(_tc.measureText(_amtStr).width<=hole*0.82)break;_ctrFz--}}
  const _subFz2=Math.min(Math.round(SZ*0.075),Math.max(9,_ctrFz-1)),_dy1=Math.round(_ctrFz/2+2),_dy2=Math.round(_subFz2/2+3)
  const canvas=cont.createEl("canvas")
  canvas.width=SZ*dpr; canvas.height=SZ*dpr
  canvas.style.cssText=`width:${SZ}px;height:${SZ}px;flex-shrink:0;cursor:default;`
  canvas.classList.add('fin-amount')
  const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr)
  const cx=SZ/2, cy=SZ/2, R=SZ/2-8, ri=R*0.54

  const N2=segs.length
  const alphas2=new Float32Array(N2).fill(1)
  const exps2  =new Float32Array(N2).fill(0)
  let hovIdx2=-1, animId2=null
  const EASE2=0.16, EXP2=5

  const legRows2=[]

  const drawFrame2=()=>{
    if(!canvas.isConnected){animId2=null;return}
    ctx.clearRect(0,0,SZ,SZ)
    for(let i=0;i<N2;i++){
      const sg=segs[i], exp=exps2[i]
      const mid=(sg.s+sg.e)/2-Math.PI/2
      ctx.beginPath()
      ctx.moveTo(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid))
      ctx.arc(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid),R,sg.s-Math.PI/2,sg.e-Math.PI/2)
      ctx.arc(cx+exp*Math.cos(mid),cy+exp*Math.sin(mid),ri,sg.e-Math.PI/2,sg.s-Math.PI/2,true)
      ctx.closePath()
      ctx.globalAlpha=alphas2[i]; ctx.fillStyle=sg.col; ctx.fill()
      ctx.globalAlpha=1; ctx.strokeStyle=bgPrim; ctx.lineWidth=1.5; ctx.stroke()
    }
    ctx.textAlign="center"; ctx.textBaseline="middle"
    const hs=hovIdx2>=0?segs[hovIdx2]:null
    ctx.globalAlpha=hovIdx2>=0?alphas2[hovIdx2]:1
    if(hs){
      ctx.font=`bold ${_ctrFz}px 'Inter',sans-serif`; ctx.fillStyle=textNorm
      ctx.fillText(fmtC(hs.val),cx,cy-_dy1)
      ctx.font=`${_subFz2}px 'Inter',sans-serif`; ctx.fillStyle=textMut
      ctx.fillText(Math.round((hs.val/total)*100)+"%",cx,cy+_dy2)
    } else {
      ctx.font=`bold ${_ctrFz}px 'Inter',sans-serif`; ctx.fillStyle=textNorm
      ctx.fillText(fmtC(total),cx,cy-_dy1)
      ctx.font=`${_subFz2}px 'Inter',sans-serif`; ctx.fillStyle=textMut
      ctx.fillText("dépenses",cx,cy+_dy2)
    }
    ctx.globalAlpha=1
  }

  const animate2=()=>{
    if(!canvas.isConnected){animId2=null;return}
    let busy=false
    for(let i=0;i<N2;i++){
      const tA=hovIdx2>=0&&i!==hovIdx2?0.18:1
      const tE=hovIdx2===i?EXP2:0
      const na=alphas2[i]+(tA-alphas2[i])*EASE2
      const ne=exps2[i]  +(tE-exps2[i])  *EASE2
      if(Math.abs(na-alphas2[i])>0.002||Math.abs(ne-exps2[i])>0.05) busy=true
      alphas2[i]=na; exps2[i]=ne
    }
    legRows2.forEach((r,i)=>{r.style.opacity=hovIdx2>=0&&i!==hovIdx2?"0.2":"1"})
    drawFrame2()
    animId2=busy?requestAnimationFrame(animate2):null
  }

  const setHover2=(idx)=>{
    if(idx===hovIdx2)return
    hovIdx2=idx
    if(!animId2) animId2=requestAnimationFrame(animate2)
  }

  canvas.addEventListener("mousemove",e=>{
    const rect=canvas.getBoundingClientRect(), scaleX=SZ/rect.width
    const mx=(e.clientX-rect.left)*scaleX-cx, my=(e.clientY-rect.top)*scaleX-cy
    const dist=Math.sqrt(mx*mx+my*my)
    if(dist<ri||dist>R+8){setHover2(-1);return}
    let a=(Math.atan2(my,mx)+Math.PI/2+Math.PI*4)%(Math.PI*2)
    setHover2(segs.findIndex(sg=>a>=sg.s&&a<sg.e))
  })
  canvas.addEventListener("mouseleave",()=>setHover2(-1))
  drawFrame2()

  // Légende - grille 2 colonnes si ≥5 entrées, sinon colonne simple
  const use2col = ents.length >= 5
  const leg=cont.createDiv()
  leg.style.cssText = use2col
    ? "display:grid;grid-template-columns:repeat(2,auto);gap:4px 20px;align-content:start;"
    : "display:flex;flex-direction:column;gap:5px;"
  for(const [i,[cat,val]] of ents.entries()){
    const pct=Math.round((val/total)*100)
    const row=leg.createDiv(); row.style.cssText="display:flex;align-items:center;gap:6px;min-width:0;transition:opacity 0.18s;"
    legRows2.push(row)
    row.createDiv().style.cssText=`width:8px;height:8px;border-radius:50%;background:${colors[i]};flex-shrink:0;`
    const lbl=row.createDiv(); lbl.style.cssText="font-size:0.82em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-normal);"
    lbl.textContent=cat
    const amtSpan=row.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);white-space:nowrap;margin-left:4px;"}}); amtSpan.textContent=fmtC(val); amtSpan.classList.add('fin-amount')
    const pctSpan=row.createEl("span",{attr:{style:"font-size:0.76em;color:var(--text-muted);opacity:0.7;white-space:nowrap;"}}); pctSpan.textContent=" "+pct+"%"; pctSpan.classList.add('fin-amount')
    row.addEventListener("mouseenter",()=>setHover2(i))
    row.addEventListener("mouseleave",()=>setHover2(-1))
  }
}

// ── COMPARAISON MENSUELLE ─────────────────────────────────────────
const _renderMonthly = () => {
  if (S_PERIOD === "tout") return

  const sec=wrap.createDiv(); sec.style.cssText="position:relative;"

  // Dériver l'année/mois de référence depuis le filtre actif
  const isFullYear = S_PERIOD === "annee" || /^\d{4}$/.test(S_PERIOD)
  const chartYear  = /^\d{4}$/.test(S_PERIOD) ? parseInt(S_PERIOD)
                   : S_PERIOD === "annee"      ? now.getFullYear()
                   : S_PERIOD === "mois"       ? getActiveMois().year
                   : S_PERIOD === "custom" && S_CSTART ? parseInt(S_CSTART.slice(0,4))
                   : now.getFullYear()
  const chartMo    = S_PERIOD === "mois" ? getActiveMois().month : now.getMonth()

  const yearLabel  = isFullYear ? ` - ${chartYear}` : ""
  sec.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-bottom:10px;"}}).textContent=`📅 Revenus & dépenses par mois${yearLabel}`

  const months=[]
  if (isFullYear) {
    // 12 mois Jan→Déc de l'année du filtre
    for(let m=0;m<12;m++) months.push({year:chartYear,month:m,label:MONTHS_LONG[m].slice(0,3)})
  } else {
    // 6 mois glissants se terminant au mois de référence
    for(let i=5;i>=0;i--){
      const d=new Date(chartYear,chartMo-i,1)
      months.push({year:d.getFullYear(),month:d.getMonth(),label:MONTHS_LONG[d.getMonth()].slice(0,3)})
    }
  }
  const mData=months.map(({year,month,label})=>{
    const mS=localStr(new Date(year,month,1)), mE=localStr(new Date(year,month+1,0))
    const txM=ALL_TX.filter(t=>t.date>=mS&&t.date<=mE&&(S_COMPTE==="tout"||t.compte===S_COMPTE))
    return { label,
      revenus: txM.filter(t=>t.type==="revenu" &&!isVirement(t)).reduce((s,t)=>s+t.montant,0),
      depenses: txM.filter(t=>t.type==="dépense"&&!isVirement(t)).reduce((s,t)=>s+Math.abs(t.montant),0)
             - txM.filter(t=>isAvoir(t)).reduce((s,t)=>s+Math.abs(t.montant),0)
    }
  })

  const _cont=dv.container.closest(".markdown-preview-section,.markdown-rendered,.cm-preview-code-block")||dv.container.parentElement||dv.container
  const W=Math.max(400,(_cont.offsetWidth||_cont.clientWidth||dv.container.offsetWidth||window.innerWidth)-24)
  const H=220, PAD={top:16,right:16,bottom:36,left:72}
  const cw=W-PAD.left-PAD.right, ch=H-PAD.top-PAD.bottom

  const dpr=window.devicePixelRatio||1
  const canvas=sec.createEl("canvas")
  canvas.width=W*dpr; canvas.height=H*dpr
  canvas.style.cssText=`width:100%;height:${H}px;display:block;cursor:default;`
  canvas.classList.add('fin-amount')
  const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr)

  const maxV=Math.max(...mData.map(m=>Math.max(m.revenus,m.depenses)),1)
  const vMax=maxV*1.15
  const yOf=v=>PAD.top+ch-((v/vMax)*ch)

  const cs=getComputedStyle(document.body)
  const borderC=cs.getPropertyValue("--background-modifier-border").trim()||"#e0e0e0"
  const mutedC =cs.getPropertyValue("--text-muted").trim()||"#888"

  // Grid
  ctx.strokeStyle=borderC+"55"; ctx.lineWidth=1
  const gridN=3
  for(let i=0;i<=gridN;i++){
    const v=vMax*(i/gridN), y=yOf(v)
    ctx.beginPath(); ctx.moveTo(PAD.left,y); ctx.lineTo(W-PAD.right,y); ctx.stroke()
    ctx.fillStyle=mutedC; ctx.font=_axisFont()+"px 'Inter',sans-serif"; ctx.textAlign="right"
    ctx.fillText(fmtC0(v),PAD.left-5,y+4)
  }

  // Barres
  const groupW=cw/months.length
  const barW=Math.min(26,groupW*0.32)
  const gap=3

  const hitAreas=[]
  for(let i=0;i<mData.length;i++){
    const m=mData[i]
    const gCx=PAD.left+groupW*i+groupW/2
    const rh=Math.max(2,(m.revenus/vMax)*ch), dh=Math.max(2,(m.depenses/vMax)*ch)
    ctx.fillStyle="#40a02b99"; ctx.fillRect(gCx-barW-gap/2,yOf(m.revenus),barW,rh)
    ctx.fillStyle="#d20f3999"; ctx.fillRect(gCx+gap/2,yOf(m.depenses),barW,dh)
    ctx.fillStyle=mutedC; ctx.font="13px 'Inter',sans-serif"; ctx.textAlign="center"
    ctx.fillText(m.label,gCx,H-8)
    hitAreas.push({x:PAD.left+groupW*i,w:groupW,data:m})
  }

  // Tooltip
  const tooltip=sec.createEl("div")
  tooltip.style.cssText="display:none;position:absolute;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;padding:9px 13px;font-size:0.8em;pointer-events:none;z-index:100;box-shadow:0 4px 18px rgba(0,0,0,0.2);min-width:140px;"

  canvas.addEventListener("mousemove",e=>{
    const rect=canvas.getBoundingClientRect(), scaleX=W/rect.width
    const mx=(e.clientX-rect.left)*scaleX
    const hit=hitAreas.find(h=>mx>=h.x&&mx<h.x+h.w)
    if(!hit){tooltip.style.display="none";return}
    tooltip.empty()
    tooltip.createEl("div",{attr:{style:"font-weight:700;margin-bottom:5px;color:var(--text-normal);border-bottom:1px solid var(--background-modifier-border);padding-bottom:4px;"}}).textContent=hit.data.label
    const r1=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;margin-bottom:2px;"}})
    r1.createEl("span",{attr:{style:"color:#40a02b;"}}).textContent="↑ Revenus"
    r1.createEl("span",{attr:{style:"font-weight:700;color:#40a02b;"}}).textContent=fmtC(hit.data.revenus)
    const r2=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;"}})
    r2.createEl("span",{attr:{style:"color:#d20f39;"}}).textContent="↓ Dépenses"
    r2.createEl("span",{attr:{style:"font-weight:700;color:#d20f39;"}}).textContent=fmtC(hit.data.depenses)
    const net=hit.data.revenus-hit.data.depenses
    const r3=tooltip.createEl("div",{attr:{style:"display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--background-modifier-border);margin-top:4px;padding-top:4px;"}})
    r3.createEl("span",{attr:{style:"color:var(--text-muted);"}}).textContent="Net"
    r3.createEl("span",{attr:{style:`font-weight:700;color:${net>=0?"#40a02b":"#d20f39"};`}}).textContent=(net>=0?"+":"")+fmtC(net)
    tooltip.style.display="block"
    const gCx=hitAreas.indexOf(hit)
    tooltip.style.left=Math.min((hit.x+hit.w/2)/scaleX+canvas.offsetLeft,sec.offsetWidth-160)+"px"
    tooltip.style.top=(canvas.offsetTop+10)+"px"
  })
  canvas.addEventListener("mouseleave",()=>{tooltip.style.display="none"})

  // Légende
  const legRow=sec.createDiv(); legRow.style.cssText="display:flex;gap:16px;justify-content:center;margin-top:6px;"
  const mkLeg=(col,lbl)=>{
    const r=legRow.createDiv(); r.style.cssText="display:flex;align-items:center;gap:5px;"
    r.createDiv().style.cssText=`width:12px;height:12px;border-radius:3px;background:${col};`
    r.createEl("span",{attr:{style:"font-size:0.78em;color:var(--text-muted);"}}).textContent=lbl
  }
  mkLeg("#40a02b99","Revenus"); mkLeg("#d20f3999","Dépenses")
}

// ── BUDGETS ───────────────────────────────────────────────────────
const _renderBudgets = () => {
  if(S_PERIOD === "tout") return
  if(CFG_BUDGETS.length===0) return
  const sec=wrap.createDiv()
  sec.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;display:block;margin-bottom:10px;"}}).textContent="📊 Budgets mensuels"

  // Budgets : utiliser le mois affiché si filtre = "mois", sinon mois courant
  const budgetMois = S_PERIOD === "mois" ? getActiveMois() : { year:now.getFullYear(), month:now.getMonth() }
  const mStart=localStr(new Date(budgetMois.year, budgetMois.month, 1))
  const mEnd  =localStr(new Date(budgetMois.year, budgetMois.month+1, 0))
  const txMois=ALL_TX.filter(t=>t.date>=mStart&&t.date<=mEnd&&(S_COMPTE==="tout"||t.compte===S_COMPTE))

  const grid=sec.createDiv(); grid.style.cssText="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;"
  for(const budget of CFG_BUDGETS){
    const spent=txMois.filter(t=>t.categorie===budget.categorie&&t.type==="dépense").reduce((s,t)=>s+Math.abs(t.montant),0)
    const max=parseFloat(budget.montant)||0
    const pct=max>0?Math.min(100,(spent/max)*100):0
    const over=max>0&&spent>max

    const card=grid.createDiv(); card.style.cssText="background:var(--background-secondary);border:1px solid "+(over?"rgba(210,15,57,0.35)":"var(--background-modifier-border)")+";border-radius:9px;padding:10px 13px;"
    const top=card.createDiv(); top.style.cssText="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;"
    top.createEl("span",{attr:{style:"font-size:0.86em;font-weight:600;"}}).textContent=budget.categorie
    const amtEl=top.createEl("span",{attr:{style:`font-size:0.8em;font-weight:700;color:${over?"#d20f39":"var(--text-muted)"};display:inline-flex;flex-direction:column;align-items:flex-end;gap:1px;`}}); amtEl.classList.add('fin-amount')
    const amtMain=amtEl.createEl("span")
    if(S_DEVISE!=="EUR"&&FX_RATES[S_DEVISE]){
      const r=FX_RATES[S_DEVISE]; const sym=FX_SYMS[S_DEVISE]
      const fmt2=v=>Math.abs(v).toLocaleString("fr-FR",{maximumFractionDigits:0})
      amtMain.textContent=fmt2(spent*r)+" "+sym+" / "+fmt2(max*r)+" "+sym+(over?" ⚠️":"")
      amtEl.createEl("span",{attr:{style:"font-size:0.82em;color:var(--text-muted);font-weight:400;"}}).textContent=fmtC(spent)+" / "+fmtC(max)
    } else {
      amtMain.textContent=fmtC(spent)+" / "+fmtC(max)+(over?" ⚠️":"")
    }
    const bg=card.createDiv(); bg.style.cssText="height:7px;border-radius:4px;background:var(--background-modifier-border);overflow:hidden;"
    const fill=bg.createDiv(); fill.style.cssText=`height:100%;width:${pct}%;border-radius:4px;background:${over?"#d20f39":pct>80?"#df8e1d":"var(--interactive-accent)"};`
  }
}

// ── HISTORIQUE ────────────────────────────────────────────────────
const _renderHistory = () => {
  const sec=wrap.createDiv()

  // Boutons d'action
  const actBar=sec.createDiv(); actBar.style.cssText="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;"
  const BTN="padding:6px 14px;border-radius:8px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.83em;color:var(--text-normal);font-family:inherit;"

  const mkBtn=(lbl,forceType)=>{
    const btn=actBar.createEl("button",{attr:{style:BTN}}); btn.textContent=lbl
    btn.onclick=()=>{
      showTxForm(lbl,{forceType,date:todayStr,compte:S_COMPTE!=="tout"?S_COMPTE:CFG_COMPTES[0]?.id},async tx=>{
        const newList=[...TX_MANUEL.filter(t=>!t._auto).map(({_auto,...r})=>r),{date:tx.date,label:tx.label,montant:tx.montant,categorie:tx.categorie,type:tx.type,compte:tx.compte}]
        await saveTx(newList.map(t=>({...t,_auto:false})))
        new Notice("Transaction ajoutée ✓",2000); renderAll()
      })
    }
  }
  mkBtn("➕ Dépense","dépense"); mkBtn("💵 Revenu","revenu"); mkBtn("💰 Mettre de côté","épargne"); mkBtn("💸 Piocher","épargne-retrait")

  // Titre + total
  const txP=filterTx(ALL_TX).slice().reverse()
  const titRow=sec.createDiv(); titRow.style.cssText="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"
  titRow.createEl("span",{attr:{style:"font-size:0.82em;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;"}}).textContent="🧾 Transactions"
  titRow.createEl("span",{attr:{style:"font-size:0.8em;color:var(--text-muted);"}}).textContent=txP.length+" entrée"+(txP.length!==1?"s":"")

  if(txP.length===0){
    sec.createEl("p",{attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;padding:12px 0;"}}).textContent="Aucune transaction pour cette période. Utilise les boutons ci-dessus pour en ajouter."
    return
  }

  // ── Mode sélection ────────────────────────────────────────────
  let selMode=false
  const selected=new Set()
  const manualTxP=txP.filter(t=>!t._auto)

  const selBar=sec.createDiv(); selBar.style.cssText="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;"

  const BTN_SEL="padding:5px 12px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.82em;color:var(--text-muted);font-family:inherit;"
  const selBtn=selBar.createEl("button",{attr:{style:BTN_SEL}}); selBtn.textContent="☑ Sélectionner"

  // Éléments visibles seulement en mode sélection
  const selAllBtn=selBar.createEl("button",{attr:{style:BTN_SEL+"display:none;"}}); selAllBtn.textContent="Tout sélectionner"
  const deselAllBtn=selBar.createEl("button",{attr:{style:BTN_SEL+"display:none;"}}); deselAllBtn.textContent="Tout désélectionner"
  const delSelBtn=selBar.createEl("button",{attr:{style:"display:none;padding:5px 12px;border-radius:7px;border:1px solid rgba(210,15,57,0.4);background:transparent;cursor:pointer;font-size:0.82em;color:#d20f39;font-family:inherit;font-weight:600;"}}); delSelBtn.textContent="🗑 Supprimer (0)"

  const updateSelUI=()=>{
    const n=selected.size
    delSelBtn.textContent=`🗑 Supprimer (${n})`
    delSelBtn.style.opacity=n>0?"1":"0.4"
    delSelBtn.style.cursor=n>0?"pointer":"default"
  }

  const enterSelMode=()=>{
    selMode=true
    selBtn.style.background="var(--interactive-accent)"; selBtn.style.color="#fff"; selBtn.style.borderColor="var(--interactive-accent)"
    selAllBtn.style.display=""; deselAllBtn.style.display=""; delSelBtn.style.display=""
    // Ajouter colonne checkbox dans le header
    thCheck.style.display=""
    tbody.querySelectorAll("tr").forEach(tr=>tr.querySelector(".tx-check-cell")?.style?.setProperty("display",""))
  }
  const exitSelMode=()=>{
    selMode=false; selected.clear()
    selBtn.style.background="var(--background-secondary)"; selBtn.style.color="var(--text-muted)"; selBtn.style.borderColor="var(--background-modifier-border)"
    selAllBtn.style.display="none"; deselAllBtn.style.display="none"; delSelBtn.style.display="none"
    thCheck.style.display="none"
    tbody.querySelectorAll("tr").forEach(tr=>{
      tr.querySelector(".tx-check-cell")?.style?.setProperty("display","none")
      tr.style.background=""
    })
    updateSelUI()
  }

  selBtn.onclick=()=>{ if(selMode) exitSelMode(); else enterSelMode() }

  selAllBtn.onclick=()=>{
    manualTxP.forEach(tx=>selected.add(tx))
    tbody.querySelectorAll("input[type=checkbox]").forEach(cb=>cb.checked=true)
    tbody.querySelectorAll("tr").forEach(tr=>{ if(tr.dataset.manual) tr.style.background="rgba(210,15,57,0.06)" })
    updateSelUI()
  }
  deselAllBtn.onclick=()=>{
    selected.clear()
    tbody.querySelectorAll("input[type=checkbox]").forEach(cb=>cb.checked=false)
    tbody.querySelectorAll("tr").forEach(tr=>tr.style.background="")
    updateSelUI()
  }

  delSelBtn.onclick=async()=>{
    if(selected.size===0) return
    const n=selected.size
    const overlay=document.body.createEl("div",{attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9999;display:flex;align-items:center;justify-content:center;"}})
    const box=overlay.createEl("div",{attr:{style:"background:var(--background-primary);border-radius:14px;padding:24px 28px;max-width:380px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.3);"}})
    box.createEl("p",{attr:{style:"margin:0 0 8px;font-weight:700;font-size:1em;"}}).textContent="Confirmer la suppression"
    box.createEl("p",{attr:{style:"margin:0 0 20px;font-size:0.88em;color:var(--text-muted);"}}).textContent=`Tu es sur le point de supprimer ${n} transaction${n>1?"s":""} de façon définitive.`
    const btns=box.createEl("div",{attr:{style:"display:flex;gap:8px;justify-content:flex-end;"}})
    const cancelB=btns.createEl("button",{attr:{style:"padding:7px 16px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;font-family:inherit;"}}); cancelB.textContent="Annuler"
    const confirmB=btns.createEl("button",{attr:{style:"padding:7px 16px;border-radius:7px;border:none;background:#d20f39;color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"}}); confirmB.textContent=`Supprimer ${n} transaction${n>1?"s":""}`
    cancelB.onclick=()=>overlay.remove()
    confirmB.onclick=async()=>{
      overlay.remove()
      const manualTxsBulk=TX_MANUEL.filter(t=>!t._auto)
      const toDelete=new Set(Array.from(selected).map(tx=>manualTxsBulk.findIndex(t=>t.date===tx.date&&t.label===tx.label&&parseFloat(t.montant)===parseFloat(tx.montant))))
      const newList=manualTxsBulk.map(({_auto,...r})=>r).filter((_,i)=>!toDelete.has(i))
      await saveTx(newList.map(t=>({...t,_auto:false})))
      new Notice(`${n} transaction${n>1?"s":""} supprimée${n>1?"s":""} ✓`,2500); renderAll()
    }
    overlay.onclick=e=>{if(e.target===overlay)overlay.remove()}
  }

  // ── Tableau ───────────────────────────────────────────────────
  const table=sec.createEl("table",{attr:{style:"width:100%;border-collapse:collapse;font-size:0.87em;"}})
  const hrow=table.createEl("thead").createEl("tr")
  const TH="text-align:left;padding:6px 10px;font-size:0.78em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:2px solid var(--background-modifier-border);"
  const TH_R="text-align:right;padding:6px 10px;font-size:0.78em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:2px solid var(--background-modifier-border);"

  // Colonne checkbox (cachée par défaut)
  const thCheck=hrow.createEl("th",{attr:{style:TH+"width:36px;display:none;"}})

  for(const [h,st] of [["Date",TH],["Description",TH],["Catégorie",TH],["Compte",TH],["Montant",TH_R],["",TH]]){
    const th=hrow.createEl("th",{attr:{style:st}})
    if(h==="")th.style.cssText+=";width:70px;"
    th.textContent=h
  }

  const tbody=table.createEl("tbody")
  const TD="padding:7px 10px;border-bottom:1px solid var(--background-modifier-border);vertical-align:middle;"

  for(const tx of txP){
    const tr=tbody.createEl("tr")
    if(!tx._auto) tr.dataset.manual="1"
    tr.onmouseenter=()=>{ if(!selected.has(tx)) tr.style.background="var(--background-secondary)" }
    tr.onmouseleave=()=>{ if(!selected.has(tx)) tr.style.background="" }

    // Cellule checkbox (cachée par défaut)
    const tdCheck=tr.createEl("td",{attr:{style:TD+"width:36px;text-align:center;display:none;"}})
    tdCheck.className="tx-check-cell"
    if(!tx._auto){
      const cb=tdCheck.createEl("input",{attr:{type:"checkbox",style:"width:15px;height:15px;cursor:pointer;accent-color:#d20f39;"}})
      cb.onchange=()=>{
        if(cb.checked){ selected.add(tx); tr.style.background="rgba(210,15,57,0.06)" }
        else { selected.delete(tx); tr.style.background="" }
        updateSelUI()
      }
    }

    tr.createEl("td",{attr:{style:TD+"white-space:nowrap;color:var(--text-muted);font-size:0.85em;"}}).textContent=fmtDateFr(tx.date)

    const tdLbl=tr.createEl("td",{attr:{style:TD+"font-weight:500;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"}})
    tdLbl.textContent=tx.label

    const tdCat=tr.createEl("td",{attr:{style:TD}})
    const catBadge=tdCat.createEl("span"); catBadge.textContent=tx.categorie||"-"
    catBadge.style.cssText="font-size:0.78em;padding:2px 7px;border-radius:10px;background:var(--background-modifier-border);color:var(--text-muted);white-space:nowrap;"

    const cptLabel=CFG_COMPTES.find(c=>c.id===tx.compte)?.label||tx.compte||"-"
    tr.createEl("td",{attr:{style:TD+"color:var(--text-muted);font-size:0.82em;"}}).textContent=cptLabel

    const m=parseFloat(tx.montant)||0
    const mColor=m>=0?"#40a02b":"#d20f39"
    const tdM=tr.createEl("td",{attr:{style:TD+`text-align:right;font-weight:700;white-space:nowrap;`}})
    mkAmountEl(tdM, m, {signed:true, color:mColor, fontSize:"0.95em"})

    const tdA=tr.createEl("td",{attr:{style:TD+"text-align:right;white-space:nowrap;"}})

    if(!tx._auto){
      const manualTxs=TX_MANUEL.filter(t=>!t._auto)
      const idx=manualTxs.findIndex(t=>t.date===tx.date&&t.label===tx.label&&parseFloat(t.montant)===parseFloat(tx.montant))

      const editBtn=tdA.createEl("button",{attr:{style:"background:none;border:1px solid var(--background-modifier-border);border-radius:5px;cursor:pointer;font-size:0.78em;padding:2px 6px;color:var(--text-muted);font-family:inherit;margin-right:4px;"}})
      editBtn.textContent="✏"; editBtn.title="Modifier"
      editBtn.onclick=()=>{
        showTxForm("Modifier la transaction",{
          label:tx.label, montant:Math.abs(m), categorie:tx.categorie,
          date:tx.date, compte:tx.compte, forceType:null
        },async updated=>{
          if(idx<0){new Notice("Erreur : transaction introuvable.",3000);return}
          const newList=manualTxs.map(({_auto,...r})=>r)
          newList[idx]={date:updated.date,label:updated.label,montant:updated.montant,categorie:updated.categorie,type:updated.type,compte:updated.compte}
          await saveTx(newList.map(t=>({...t,_auto:false})))
          new Notice("Transaction modifiée ✓",2000); renderAll()
        })
      }

      const delBtn=tdA.createEl("button",{attr:{style:"background:none;border:1px solid rgba(210,15,57,0.3);border-radius:5px;cursor:pointer;font-size:0.78em;padding:2px 6px;color:#d20f39;font-family:inherit;"}})
      delBtn.textContent="🗑"; delBtn.title="Supprimer"
      delBtn.onclick=async()=>{
        if(!confirm("Supprimer cette transaction ?"))return
        if(idx<0){new Notice("Erreur : transaction introuvable.",3000);return}
        const newList=manualTxs.map(({_auto,...r})=>r).filter((_,i)=>i!==idx)
        await saveTx(newList.map(t=>({...t,_auto:false})))
        new Notice("Supprimée.",2000); renderAll()
      }
    }
  }
}

// ════ GO ══════════════════════════════════════════════════════════
renderAll()
```

