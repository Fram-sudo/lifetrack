---
type: sport
created: 2026-06-30
tags:
  - sport
  - hevy
  - performance
cssclasses:
  - media-page
obsidianUIMode: preview
---

# 🏋️ Sport

```dataviewjs
// ════════════════════════════════════════════════════════════════
// 🏋️ SPORT - Suivi performances (import Hevy + ajout manuel)
// ════════════════════════════════════════════════════════════════

const SPORT_DIR = "2 - Domaines/Sport/Data"

// ── HELPERS ──────────────────────────────────────────────────────
const localStr = d => {
  const y=d.getFullYear(), m=String(d.getMonth()+1).padStart(2,'0'), dd=String(d.getDate()).padStart(2,'0')
  return `${y}-${m}-${dd}`
}
const fmtDateFr = iso => {
  if(!iso) return '-'
  const [y,m,d] = iso.slice(0,10).split('-')
  return `${d}/${m}/${y}`
}
const getWeekMon = iso => {
  const d = new Date(iso + 'T12:00:00')
  const day = d.getDay() || 7
  d.setDate(d.getDate() - day + 1)
  return localStr(d)
}
const daysBetween = (a,b) => Math.round((new Date(b+' 12:00') - new Date(a+' 12:00')) / 86400000)
const fmtDur = m => m >= 60 ? `${Math.floor(m/60)}h${m%60>0?String(m%60).padStart(2,'0')+'':''}`:`${m} min`
const fmtVol = kg => kg >= 1000 ? (kg/1000).toFixed(1).replace(/\.0$/,'') + ' t' : Math.round(kg) + ' kg'
const workingSets = ex => (ex.sets||[]).filter(s => s.type !== 'warmup')
const workoutVolume = w => (w.exercises||[]).reduce((sum,ex) =>
  sum + workingSets(ex).reduce((s2,st) => s2 + (st.weight_kg||0)*(st.reps||0), 0), 0)
const slug = s => (s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')

// ── LOAD DATA (Hevy + saisie manuelle) ─────────────────────────────
const loadWorkouts = async () => {
  const ws = []
  const files = app.vault.getFiles().filter(f =>
    f.path.startsWith(SPORT_DIR + '/') && /^(hevy|manuel)_\d{4}\.json$/.test(f.name)
  )
  for (const f of files.sort((a,b) => a.name < b.name ? -1 : 1)) {
    try {
      const arr = JSON.parse(await app.vault.read(f))
      const source = f.name.startsWith('manuel_') ? 'manuel' : 'hevy'
      for (const w of arr) w._source = source
      ws.push(...arr)
    } catch(e) {}
  }
  return ws.sort((a,b) => a.date < b.date ? -1 : 1)
}

// ── Persistance des séances ajoutées manuellement ───────────────────
const manualFilePath = year => `${SPORT_DIR}/manuel_${year}.json`

const loadManualYear = async year => {
  const f = app.vault.getAbstractFileByPath(manualFilePath(year))
  if (!f) return []
  try { return JSON.parse(await app.vault.read(f)) } catch(e) { return [] }
}

const saveManualYear = async (year, arr) => {
  const path = manualFilePath(year)
  const content = JSON.stringify(arr, null, 2)
  const existing = app.vault.getAbstractFileByPath(path)
  if (existing) { await app.vault.modify(existing, content); return }
  if (!app.vault.getAbstractFileByPath(SPORT_DIR)) { try { await app.vault.createFolder(SPORT_DIR) } catch(e) {} }
  await app.vault.create(path, content)
}

// Ajoute ou met à jour une séance manuelle (déplace de fichier si l'année a changé)
const addOrUpdateManualWorkout = async (workout, previousYear) => {
  const year = workout.date.slice(0,4)
  if (previousYear && previousYear !== year) {
    const oldArr = await loadManualYear(previousYear)
    await saveManualYear(previousYear, oldArr.filter(w => w.id !== workout.id))
  }
  const arr = await loadManualYear(year)
  const idx = arr.findIndex(w => w.id === workout.id)
  if (idx >= 0) arr[idx] = workout; else arr.push(workout)
  arr.sort((a,b) => a.date < b.date ? -1 : 1)
  await saveManualYear(year, arr)
}

const deleteManualWorkout = async workout => {
  const year = workout.date.slice(0,4)
  const arr = await loadManualYear(year)
  await saveManualYear(year, arr.filter(w => w.id !== workout.id))
}

let ALL = await loadWorkouts()
const today = localStr(new Date())
const YEAR = new Date().getFullYear()
const thisWeek = getWeekMon(today)
const thisMonth = today.slice(0,7)

// ── COULEURS ─────────────────────────────────────────────────────
const cs = getComputedStyle(document.body)
const ACCENT   = cs.getPropertyValue('--interactive-accent').trim()   || '#1e66f5'
const MUTED    = cs.getPropertyValue('--text-muted').trim()           || '#888'
const BORDER   = cs.getPropertyValue('--background-modifier-border').trim() || '#e0e0e0'
const SPORT_C  = '#179299'
const GAIN_C   = '#40a02b'
const YELLOW_C = '#c4943a'
const HEVY_C   = '#1e66f5'
const HM_SCALE = ['#0f3d3f','#155c5e','#1a7a7d','#179299','#3fd0d6']
const HM_EMPTY = 'var(--background-modifier-border)'
const INPUT_STYLE = 'width:100%;padding:7px 9px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-primary);color:var(--text-normal);font-size:0.85em;box-sizing:border-box;'
const SMALL_INPUT_STYLE = INPUT_STYLE

// ── STATE ─────────────────────────────────────────────────────────
if (!window._SPORT_STATE) window._SPORT_STATE = { tab: 'apercu', exercise: null, progMode: 'volume' }

const isMobile = window.innerWidth < 700

// ── ROOT ──────────────────────────────────────────────────────────
const root = dv.el('div', '')
root.empty()

// ── EMPTY STATE (réutilisable) ──────────────────────────────────────
const renderEmptyState = () => {
  root.empty()
  const empty = root.createDiv()
  empty.style.cssText = 'text-align:center;padding:60px 20px;color:var(--text-muted);'
  empty.innerHTML = `
    <div style="font-size:3em;margin-bottom:14px;">🏋️</div>
    <div style="font-size:1.1em;font-weight:700;margin-bottom:8px;color:var(--text-normal);">Aucune séance enregistrée</div>
    <div style="font-size:0.85em;">Lance <code>import_hevy.py</code> pour importer ton export CSV Hevy,<br>ou ajoute une séance manuellement ci-dessous.</div>
  `
  const btnWrap = empty.createDiv(); btnWrap.style.cssText = 'margin-top:16px;'
  const addBtn = btnWrap.createEl('button')
  addBtn.textContent = '➕ Ajouter une séance'
  addBtn.style.cssText = `padding:9px 18px;border-radius:8px;border:none;background:${SPORT_C};color:#fff;cursor:pointer;font-size:0.88em;font-weight:700;`
  addBtn.onclick = () => openWorkoutModal(null)
}

if (!ALL.length) { renderEmptyState() }

// ── CALCULS GLOBAUX (recalculés après ajout/édition/suppression) ────
let lastW, daysAgo, sessMonth, sessWeek, totalVolume, streak, exMap, allExercises, volByDay

const computePR = name => {
  let best = null
  for (const w of ALL) {
    const ex = (w.exercises||[]).find(e => e.name === name)
    if (!ex) continue
    for (const s of workingSets(ex)) {
      const wt = s.weight_kg || 0
      if (wt <= 0) continue
      if (!best || wt > best.weight || (wt === best.weight && (s.reps||0) > best.reps))
        best = { weight: wt, reps: s.reps||0, date: w.date }
    }
  }
  return best
}

const recompute = () => {
  ALL.sort((a,b) => a.date < b.date ? -1 : 1)
  lastW = ALL[ALL.length - 1]
  daysAgo = lastW ? daysBetween(lastW.date, today) : 0
  sessMonth = ALL.filter(w => w.date.slice(0,7) === thisMonth).length
  sessWeek  = ALL.filter(w => getWeekMon(w.date) === thisWeek).length
  totalVolume = ALL.reduce((s,w) => s + workoutVolume(w), 0)

  const weekSet = new Set(ALL.map(w => getWeekMon(w.date)))
  streak = 0
  let chk = new Date(thisWeek + 'T12:00:00')
  while (true) {
    const wk = localStr(chk)
    if (!weekSet.has(wk)) break
    streak++; chk.setDate(chk.getDate() - 7)
  }

  exMap = {}
  for (const w of ALL)
    for (const ex of w.exercises||[])
      exMap[ex.name] = (exMap[ex.name]||0) + 1
  allExercises = Object.entries(exMap).sort((a,b)=>b[1]-a[1]).map(([n])=>n)
  if (!window._SPORT_STATE.exercise && allExercises.length)
    window._SPORT_STATE.exercise = allExercises[0]

  volByDay = {}
  for (const w of ALL) volByDay[w.date] = (volByDay[w.date]||0) + workoutVolume(w)
}
recompute()

// Sélecteur de date maison (même composant que dans les templates Films/Séries/etc.
// du vault, pour rester cohérent visuellement avec le reste de Lifetrack en JJ/MM/AAAA)
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

// Applique en mémoire un ajout/modification/suppression manuelle (persisté par ailleurs sur disque)
const applyLocalUpsert = workout => {
  const idx = ALL.findIndex(w => w.id === workout.id)
  if (idx >= 0) ALL[idx] = { ...workout, _source: 'manuel' }
  else ALL.push({ ...workout, _source: 'manuel' })
  recompute()
}
const applyLocalDelete = id => {
  ALL = ALL.filter(w => w.id !== id)
  recompute()
}

// ══ MODALE D'AJOUT / ÉDITION DE SÉANCE ══════════════════════════════
const openWorkoutModal = (existing) => {
  const isEdit = !!existing
  const previousYear = existing ? existing.date.slice(0,4) : null

  const state = existing ? {
    id: existing.id,
    title: existing.title || '',
    date: existing.date,
    duration_minutes: existing.duration_minutes || '',
    exercises: (existing.exercises||[]).map(ex => ({
      name: ex.name,
      sets: (ex.sets||[]).map(s => ({ weight_kg: s.weight_kg ?? '', reps: s.reps ?? '' }))
    }))
  } : {
    id: null,
    title: '',
    date: today,
    duration_minutes: '',
    exercises: [{ name:'', sets:[{weight_kg:'',reps:''}] }]
  }

  const overlay = document.body.createDiv()
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px;'
  const box = overlay.createDiv()
  box.style.cssText = 'background:var(--background-primary);border-radius:14px;padding:22px 24px;width:520px;max-width:100%;max-height:88vh;overflow-y:auto;box-shadow:0 12px 50px rgba(0,0,0,0.4);'
  box.createEl('h3',{attr:{style:'margin:0 0 16px;font-size:1em;font-weight:800;color:var(--text-normal);'}}).textContent = isEdit ? '✏️ Modifier la séance' : '➕ Nouvelle séance'

  // datalist pour l'autocomplétion des noms d'exercices
  const dlId = 'sport-manuel-exercises-list'
  let dl = document.getElementById(dlId)
  if (dl) dl.remove()
  dl = document.body.createEl('datalist'); dl.id = dlId
  for (const name of allExercises) dl.createEl('option',{attr:{value:name}})

  const mkField = (parent, label) => {
    const w = parent.createDiv()
    w.createEl('div',{attr:{style:'font-size:0.72em;color:var(--text-muted);margin-bottom:3px;font-weight:600;'}}).textContent = label
    return w
  }

  const row2 = box.createDiv(); row2.style.cssText='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;'
  const fTitre = mkField(row2, 'Titre')
  const inpTitre = fTitre.createEl('input',{attr:{type:'text',value:state.title,placeholder:'ex. Jambes, Course à pied…',style:INPUT_STYLE}})
  const fDate = mkField(row2, 'Date')
  const datePicker = mkDatePicker(fDate, state.date, v => { state.date = v }, 'Choisir une date')

  const fDur = mkField(box, 'Durée (minutes, optionnel)')
  fDur.style.marginBottom = '12px'
  const inpDur = fDur.createEl('input',{attr:{type:'number',min:'0',value:String(state.duration_minutes),placeholder:'ex. 45',style:INPUT_STYLE}})

  box.createEl('div',{attr:{style:'font-size:0.72em;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.04em;font-weight:700;margin:16px 0 8px;'}}).textContent='Exercices (optionnel)'
  const exContainer = box.createDiv()

  const renderExercises = () => {
    exContainer.empty()
    state.exercises.forEach((ex, exIdx) => {
      const exBlock = exContainer.createDiv()
      exBlock.style.cssText = `background:var(--background-secondary);border-radius:10px;padding:12px;margin-bottom:10px;border-left:3px solid ${SPORT_C};`
      const hdrRow = exBlock.createDiv(); hdrRow.style.cssText='display:flex;gap:8px;align-items:center;margin-bottom:8px;'
      const nameInp = hdrRow.createEl('input',{attr:{type:'text',value:ex.name,placeholder:"Nom de l'exercice…",list:dlId,style:INPUT_STYLE+'flex:1;'}})
      nameInp.oninput = () => { ex.name = nameInp.value }
      const rmExBtn = hdrRow.createEl('button')
      rmExBtn.textContent='✕'
      rmExBtn.style.cssText='background:none;border:none;color:#d20f39;cursor:pointer;font-size:0.95em;padding:2px 6px;'
      rmExBtn.onclick = () => { state.exercises.splice(exIdx,1); renderExercises() }

      ex.sets.forEach((s, sIdx) => {
        const setRow = exBlock.createDiv()
        setRow.style.cssText='display:grid;grid-template-columns:20px 1fr 1fr 22px;gap:6px;align-items:center;margin-bottom:6px;'
        setRow.createEl('span',{attr:{style:'font-size:0.72em;color:var(--text-muted);text-align:center;'}}).textContent = String(sIdx+1)
        const wInp = setRow.createEl('input',{attr:{type:'number',step:'0.5',min:'0',placeholder:'Poids (kg)',value:String(s.weight_kg),style:SMALL_INPUT_STYLE}})
        wInp.oninput = () => { s.weight_kg = wInp.value }
        const rInp = setRow.createEl('input',{attr:{type:'number',min:'0',placeholder:'Reps',value:String(s.reps),style:SMALL_INPUT_STYLE}})
        rInp.oninput = () => { s.reps = rInp.value }
        const rmSetBtn = setRow.createEl('button')
        rmSetBtn.textContent='✕'
        rmSetBtn.style.cssText='background:none;border:none;color:var(--text-muted);cursor:pointer;'
        rmSetBtn.onclick = () => { ex.sets.splice(sIdx,1); renderExercises() }
      })
      const addSetBtn = exBlock.createEl('button')
      addSetBtn.textContent='+ Ajouter une série'
      addSetBtn.style.cssText='font-size:0.75em;color:var(--interactive-accent);background:none;border:none;cursor:pointer;font-weight:700;padding:2px 0;'
      addSetBtn.onclick = () => { ex.sets.push({weight_kg:'',reps:''}); renderExercises() }
    })
  }
  renderExercises()

  const addExBtn = box.createEl('button')
  addExBtn.textContent='+ Ajouter un exercice'
  addExBtn.style.cssText='width:100%;padding:8px;border-radius:8px;border:1px dashed var(--background-modifier-border);background:none;color:var(--text-muted);cursor:pointer;font-size:0.82em;margin-bottom:14px;'
  addExBtn.onclick = () => { state.exercises.push({name:'',sets:[{weight_kg:'',reps:''}]}); renderExercises() }

  const actions = box.createDiv(); actions.style.cssText='display:flex;justify-content:flex-end;gap:8px;margin-top:6px;'
  const cancelBtn = actions.createEl('button')
  cancelBtn.textContent='Annuler'
  cancelBtn.style.cssText='padding:8px 16px;border-radius:8px;border:none;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.85em;font-weight:600;'
  cancelBtn.onclick = () => overlay.remove()

  const saveBtn = actions.createEl('button')
  saveBtn.textContent='Enregistrer'
  saveBtn.style.cssText=`padding:8px 16px;border-radius:8px;border:none;background:${SPORT_C};color:#fff;cursor:pointer;font-size:0.85em;font-weight:700;`
  saveBtn.onclick = async () => {
    const title = inpTitre.value.trim() || 'Séance'
    const date = datePicker.getValue() || today
    const dur = parseInt(inpDur.value) || 0

    const exercises = state.exercises
      .filter(ex => ex.name.trim())
      .map(ex => ({
        name: ex.name.trim(),
        sets: ex.sets
          .filter(s => s.weight_kg !== '' || s.reps !== '')
          .map((s,i) => ({
            index: i, type: 'normal',
            weight_kg: parseFloat(s.weight_kg) || 0,
            reps: parseInt(s.reps) || 0,
            rpe: null, duration_seconds: null
          }))
      }))
      .filter(ex => ex.sets.length)

    const id = state.id || `${date}_manuel_${slug(title)}_${Math.random().toString(36).slice(2,7)}`
    const toSave = { id, title, date, start_time:'', end_time:'', duration_minutes: dur, exercises }

    saveBtn.disabled = true; saveBtn.textContent = 'Enregistrement…'
    try {
      await addOrUpdateManualWorkout(toSave, previousYear)
      applyLocalUpsert(toSave)
      new Notice(isEdit ? 'Séance mise à jour !' : 'Séance ajoutée !', 2500)
      overlay.remove()
      renderAll()
    } catch(e) {
      new Notice("Erreur lors de l'enregistrement : " + e.message, 4000)
      saveBtn.disabled = false; saveBtn.textContent = 'Enregistrer'
    }
  }

  overlay.onclick = e => { if (e.target===overlay) overlay.remove() }
}

// Supprime une séance manuelle (avec confirmation)
const confirmDeleteWorkout = async workout => {
  const overlay = document.body.createDiv()
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;padding:16px;'
  const box = overlay.createDiv()
  box.style.cssText = 'background:var(--background-primary);border-radius:14px;padding:20px 22px;width:360px;max-width:100%;box-shadow:0 12px 50px rgba(0,0,0,0.4);'
  box.createEl('div',{attr:{style:'font-weight:700;color:var(--text-normal);margin-bottom:6px;'}}).textContent='Supprimer cette séance ?'
  box.createEl('div',{attr:{style:'font-size:0.85em;color:var(--text-muted);margin-bottom:16px;'}}).textContent = `${workout.title || 'Séance'} - ${fmtDateFr(workout.date)}`
  const actions = box.createDiv(); actions.style.cssText='display:flex;justify-content:flex-end;gap:8px;'
  const cancelBtn = actions.createEl('button')
  cancelBtn.textContent='Annuler'
  cancelBtn.style.cssText='padding:7px 14px;border-radius:8px;border:none;background:var(--background-secondary);color:var(--text-normal);cursor:pointer;font-size:0.85em;font-weight:600;'
  cancelBtn.onclick = () => overlay.remove()
  const delBtn = actions.createEl('button')
  delBtn.textContent='Supprimer'
  delBtn.style.cssText='padding:7px 14px;border-radius:8px;border:none;background:#d20f39;color:#fff;cursor:pointer;font-size:0.85em;font-weight:700;'
  delBtn.onclick = async () => {
    delBtn.disabled = true; delBtn.textContent = 'Suppression…'
    try {
      await deleteManualWorkout(workout)
      applyLocalDelete(workout.id)
      new Notice('Séance supprimée.', 2000)
      overlay.remove()
      if (!ALL.length) renderEmptyState(); else renderAll()
    } catch(e) {
      new Notice('Erreur lors de la suppression : ' + e.message, 4000)
      delBtn.disabled = false; delBtn.textContent = 'Supprimer'
    }
  }
  overlay.onclick = e => { if (e.target===overlay) overlay.remove() }
}

// ── RENDU PRINCIPAL ───────────────────────────────────────────────
const renderAll = () => {
  if (!ALL.length) { renderEmptyState(); return }
  root.empty()

  // ── HEADER STATS ──────────────────────────────────────────────
  const hdrRow = root.createDiv()
  hdrRow.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px;'

  const statCard = (icon, label, value, sub='') => {
    const c = hdrRow.createDiv()
    c.style.cssText = 'flex:1;min-width:110px;background:var(--background-secondary);border-radius:10px;padding:12px 14px;'
    c.createEl('div',{attr:{style:'font-size:0.73em;color:var(--text-muted);margin-bottom:3px;white-space:nowrap;'}}).textContent = `${icon} ${label}`
    c.createEl('div',{attr:{style:'font-size:1.25em;font-weight:700;color:var(--text-normal);'}}).textContent = value
    if(sub) c.createEl('div',{attr:{style:'font-size:0.7em;color:var(--text-faint);margin-top:2px;'}}).textContent = sub
  }

  statCard('💪','Total', ALL.length + ' séances')
  statCard('🏋️','Volume total', fmtVol(totalVolume), 'soulevés')
  statCard('📅','Ce mois', sessMonth + ' séances')
  if (streak >= 2) statCard('🔥','Streak', streak + ' sem.', 'consécutives')
  else statCard('📆','Cette sem.', sessWeek + ' séance' + (sessWeek>1?'s':''))
  const lastLabel = daysAgo === 0 ? "Aujourd'hui" : daysAgo === 1 ? 'Hier' : `il y a ${daysAgo}j`
  statCard('🕒','Dernière', lastLabel, fmtDateFr(lastW.date))

  // ── TABS + AJOUT ─────────────────────────────────────────────────
  const tabBarRow = root.createDiv()
  tabBarRow.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;border-bottom:1px solid var(--background-modifier-border);flex-wrap:wrap;'

  const tabBar = tabBarRow.createDiv()
  tabBar.style.cssText = 'display:flex;gap:2px;'

  for (const [id, label] of [['apercu','📊 Aperçu'],['progression','📈 Progression'],['records','🏆 Records'],['seances','📋 Séances']]) {
    const active = window._SPORT_STATE.tab === id
    const btn = tabBar.createEl('button')
    btn.textContent = label
    btn.style.cssText = `padding:7px 16px;border:none;background:none;cursor:pointer;font-size:0.88em;font-weight:600;margin-bottom:-1px;border-bottom:2px solid ${active?ACCENT:'transparent'};color:${active?ACCENT:'var(--text-muted)'};transition:color .15s;`
    btn.onclick = () => { window._SPORT_STATE.tab = id; renderAll() }
  }

  const addBtn = tabBarRow.createEl('button')
  addBtn.textContent = '➕ Ajouter une séance'
  addBtn.style.cssText = `padding:6px 14px;border-radius:7px;border:none;background:${SPORT_C};color:#fff;cursor:pointer;font-size:0.8em;font-weight:700;margin-bottom:6px;white-space:nowrap;`
  addBtn.onclick = () => openWorkoutModal(null)

  const content = root.createDiv()
  if (window._SPORT_STATE.tab === 'apercu')      renderApercu(content)
  if (window._SPORT_STATE.tab === 'progression') renderProgression(content)
  if (window._SPORT_STATE.tab === 'records')     renderRecords(content)
  if (window._SPORT_STATE.tab === 'seances')     renderSeances(content)
}

// ── Mini stat cards (réutilisé partout) ────────────────────────────
const miniStatsRow = (cnt, items) => {
  const row = cnt.createDiv()
  row.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;'
  for (const [label,val,color] of items) {
    const c = row.createDiv()
    c.style.cssText = 'flex:1;min-width:90px;background:var(--background-secondary);border-radius:8px;padding:9px 10px;text-align:center;'
    c.createEl('div',{attr:{style:'font-size:0.7em;color:var(--text-muted);margin-bottom:2px;'}}).textContent = label
    c.createEl('div',{attr:{style:`font-size:1em;font-weight:700;${color?'color:'+color:''}`}}).textContent = val
  }
}

// ══ ONGLET APERÇU ═══════════════════════════════════════════════
const renderApercu = cnt => {
  // ── Heatmap annuelle ────────────────────────────────────────────
  const hmBlock = cnt.createDiv()
  hmBlock.style.cssText = 'margin-bottom:20px;'
  const hmHdr = hmBlock.createDiv()
  hmHdr.style.cssText = 'display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;flex-wrap:wrap;gap:4px;'
  hmHdr.createEl('h3',{attr:{style:'font-size:0.85em;font-weight:800;color:var(--text-normal);margin:0;'}}).textContent = `Heatmap ${YEAR}`
  hmHdr.createEl('span',{attr:{style:'font-size:0.72em;color:var(--text-muted);'}}).textContent = 'couleur = volume soulevé ce jour-là'

  const jan1 = new Date(YEAR,0,1)
  const offset = (jan1.getDay()+6)%7
  const start = new Date(jan1); start.setDate(1-offset)
  const dec31 = new Date(YEAR,11,31)
  const weeks = []
  { let cur = new Date(start); while (cur<=dec31) { const w=[]; for(let i=0;i<7;i++){w.push(new Date(cur)); cur.setDate(cur.getDate()+1)}; weeks.push(w) } }

  const maxVol = Math.max(1, ...Object.entries(volByDay).filter(([d])=>d.startsWith(String(YEAR))).map(([,v])=>v))
  const colorFor = v => { if(!v) return HM_EMPTY; const r=v/maxVol; return r<.2?HM_SCALE[0]:r<.4?HM_SCALE[1]:r<.65?HM_SCALE[2]:r<.85?HM_SCALE[3]:HM_SCALE[4] }

  const hmWrapOuter = hmBlock.createDiv()
  hmWrapOuter.style.cssText = `${isMobile?'overflow-x:auto;':''}width:${isMobile?'min-content;min-width:100%':'100%'};`
  const LABEL_W = isMobile?20:26
  const MONTHS_FR = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
  const monthRow = hmWrapOuter.createDiv()
  monthRow.style.cssText = `display:flex;padding-left:${LABEL_W+4}px;margin-bottom:3px;`
  let lastM=-1
  for (const w of weeks) {
    const first = w.find(d=>d.getFullYear()===YEAR)
    const cell = monthRow.createDiv(); cell.style.cssText='flex:1;font-size:0.67em;color:var(--text-muted);white-space:nowrap;'
    if (first) { const m=first.getMonth(); if(m!==lastM && first.getDate()<=7){cell.textContent=MONTHS_FR[m]; lastM=m} }
  }
  const body = hmWrapOuter.createDiv(); body.style.cssText='display:flex;align-items:stretch;width:100%;height:116px;'
  const labelsCol = body.createDiv(); labelsCol.style.cssText=`display:flex;flex-direction:column;justify-content:space-around;width:${LABEL_W}px;flex-shrink:0;margin-right:4px;`
  for (const d of ["L","M","M","J","V","S","D"]) labelsCol.createEl('span',{attr:{style:'font-size:0.59em;color:var(--text-faint);text-align:right;line-height:1;'}}).textContent=d
  const grid = body.createDiv(); grid.style.cssText='display:flex;flex:1;gap:3px;'
  const todayD = new Date(); todayD.setHours(0,0,0,0)
  for (const w of weeks) {
    const col = grid.createDiv(); col.style.cssText='display:flex;flex-direction:column;flex:1;gap:3px;'
    for (const day of w) {
      const key = localStr(day), v = volByDay[key]||0, outYear = day.getFullYear()!==YEAR, isToday = day.getTime()===todayD.getTime()
      const cell = col.createDiv()
      cell.style.cssText = ['flex:1;border-radius:3px', `background:${outYear?'transparent':colorFor(v)}`,
        !outYear?'border:1px solid rgba(0,0,0,0.05)':'', isToday?'outline:2px solid '+ACCENT+';outline-offset:1px;':''].filter(Boolean).join(';')
      if (!outYear) cell.title = v ? `${fmtDateFr(key)} - ${fmtVol(v)} soulevés` : `${fmtDateFr(key)} - repos`
    }
  }
  const legend = hmBlock.createDiv()
  legend.style.cssText='display:flex;align-items:center;gap:4px;margin-top:10px;font-size:0.71em;color:var(--text-muted);'
  legend.createEl('span').textContent='Moins'
  for (const c of [HM_EMPTY, ...HM_SCALE]) { const sq=legend.createDiv(); sq.style.cssText=`width:11px;height:11px;border-radius:2px;background:${c};border:1px solid rgba(0,0,0,0.07);` }
  legend.createEl('span').textContent='Plus'

  const daysActive = Object.keys(volByDay).filter(d=>d.startsWith(String(YEAR))).length
  const bestDay = Math.max(0, ...Object.entries(volByDay).filter(([d])=>d.startsWith(String(YEAR))).map(([,v])=>v))
  const weeksElapsed = Math.max(1, Math.ceil(daysBetween(`${YEAR}-01-01`, today)/7))
  const sessThisYear = ALL.filter(w=>w.date.startsWith(String(YEAR))).length
  miniStatsRow(hmBlock, [
    ['Jours actifs', `${daysActive} / 365`],
    ['Streak', streak + ' sem.'],
    ['Meilleur jour', fmtVol(bestDay)],
    ['Moy. / semaine', (sessThisYear/weeksElapsed).toFixed(1)],
  ])

  // ── Top exercices + Répartition par jour ────────────────────────
  const cols = cnt.createDiv()
  cols.style.cssText = `display:grid;grid-template-columns:${isMobile?'1fr':'1.3fr 1fr'};gap:16px;`

  const card1 = cols.createDiv(); card1.style.cssText='background:var(--background-secondary);border-radius:10px;padding:14px;'
  card1.createEl('h3',{attr:{style:'font-size:0.85em;font-weight:800;color:var(--text-normal);margin:0 0 10px;'}}).textContent='Top exercices'
  const top5 = allExercises.slice(0,5)
  const maxFreq = Math.max(1, ...top5.map(n=>exMap[n]))
  for (const name of top5) {
    const row = card1.createDiv(); row.style.cssText='display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:0.78em;'
    row.createEl('span',{attr:{style:'width:130px;flex-shrink:0;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'}}).textContent=name
    const track = row.createEl('span',{attr:{style:'flex:1;height:8px;background:var(--background-modifier-border);border-radius:4px;overflow:hidden;display:inline-block;'}})
    track.createEl('span',{attr:{style:`display:block;height:100%;border-radius:4px;background:${SPORT_C};width:${exMap[name]/maxFreq*100}%;`}})
    row.createEl('span',{attr:{style:'width:20px;text-align:right;color:var(--text-muted);'}}).textContent=exMap[name]
  }
  if (!top5.length) card1.createEl('p',{attr:{style:'color:var(--text-muted);font-style:italic;font-size:0.85em;'}}).textContent='Aucun exercice.'

  const card2 = cols.createDiv(); card2.style.cssText='background:var(--background-secondary);border-radius:10px;padding:14px;'
  card2.createEl('h3',{attr:{style:'font-size:0.85em;font-weight:800;color:var(--text-normal);margin:0 0 10px;'}}).textContent='Répartition par jour'
  const dowCounts = [0,0,0,0,0,0,0]
  for (const w of ALL) dowCounts[(new Date(w.date+'T12:00:00').getDay()+6)%7]++
  const maxDow = Math.max(1, ...dowCounts)
  const dowWrap = card2.createDiv(); dowWrap.style.cssText='display:flex;gap:6px;align-items:flex-end;height:90px;'
  const DOW_LBL = ['L','M','M','J','V','S','D']
  dowCounts.forEach((n,i) => {
    const col = dowWrap.createDiv(); col.style.cssText='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px;height:100%;'
    col.createEl('span',{attr:{style:'font-size:0.65em;color:var(--text-muted);'}}).textContent = n||''
    const h = n ? Math.max(6,(n/maxDow)*70) : 2
    col.createEl('div',{attr:{style:`width:60%;border-radius:4px 4px 0 0;background:${n?ACCENT:'var(--background-modifier-border)'};height:${h}px;`}})
    col.createEl('span',{attr:{style:'font-size:0.68em;color:var(--text-muted);'}}).textContent = DOW_LBL[i]
  })
}

// ══ ONGLET PROGRESSION ══════════════════════════════════════════
const renderProgression = cnt => {
  const controls = cnt.createDiv()
  controls.style.cssText = 'display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap;'

  const toggle = controls.createDiv()
  toggle.style.cssText = 'display:flex;background:var(--background-secondary);border-radius:7px;padding:2px;gap:2px;'
  const tBtns = {}
  for (const [mode,label] of [['volume','Vue globale (volume)'],['exercise','Par exercice']]) {
    const b = toggle.createEl('button'); b.textContent = label; tBtns[mode] = b
    b.onclick = () => { window._SPORT_STATE.progMode = mode; renderProg() }
  }
  const refreshToggle = () => { for (const [m,b] of Object.entries(tBtns)) {
    const on = window._SPORT_STATE.progMode === m
    b.style.cssText = `border:none;font-size:0.78em;font-weight:700;padding:5px 12px;border-radius:5px;cursor:pointer;background:${on?ACCENT:'transparent'};color:${on?'#fff':'var(--text-muted)'};`
  }}

  const sel = controls.createEl('select')
  sel.style.cssText = 'flex:1;min-width:180px;max-width:340px;padding:6px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.85em;cursor:pointer;'
  for (const ex of allExercises) { const opt = sel.createEl('option',{text:ex}); opt.value=ex; if(ex===window._SPORT_STATE.exercise) opt.selected=true }
  sel.onchange = () => { window._SPORT_STATE.exercise = sel.value; renderProg() }

  const card = cnt.createDiv()
  card.style.cssText = 'background:var(--background-secondary);border-radius:10px;padding:14px;'
  const chartCnt = card.createDiv()

  const renderProg = () => {
    refreshToggle()
    sel.style.opacity = window._SPORT_STATE.progMode === 'exercise' ? '1' : '0.4'
    sel.style.pointerEvents = window._SPORT_STATE.progMode === 'exercise' ? 'auto' : 'none'
    chartCnt.empty()
    if (window._SPORT_STATE.progMode === 'exercise') {
      _renderExerciseChart(chartCnt, window._SPORT_STATE.exercise)
    } else {
      _renderVolumeChart(chartCnt)
    }
  }
  renderProg()
}

// Graphique générique poids / volume dans le temps
const _drawLineChart = (cnt, points, {yFmt, color}) => {
  if (!points.length) {
    cnt.createEl('p',{attr:{style:'text-align:center;padding:40px;color:var(--text-muted);font-size:0.9em;'}}).textContent='Aucune donnée.'
    return
  }
  const vals = points.map(p=>p.value)
  const minV = Math.min(...vals), maxV = Math.max(...vals)
  const pr = maxV, startV = vals[0], delta = pr - startV
  const n = points.length

  // Pas assez de variation pour tracer un axe fiable (1 seule séance, ou même
  // valeur à chaque fois) : on évite un axe avec des graduations fictives.
  if (n < 2 || minV === maxV) {
    const box = cnt.createDiv()
    box.style.cssText = 'text-align:center;padding:26px 16px;background:var(--background-primary);border-radius:8px;margin-bottom:14px;'
    box.createEl('div',{attr:{style:`font-size:1.7em;font-weight:800;color:${color};margin-bottom:4px;`}}).textContent = yFmt(vals[0])
    box.createEl('div',{attr:{style:'font-size:0.8em;color:var(--text-muted);'}}).textContent =
      n < 2 ? 'Une seule séance enregistrée - reviens après ta prochaine séance pour voir ta progression.'
            : 'Même valeur à chaque séance pour l\'instant - pas encore de progression à afficher.'
    miniStatsRow(cnt, [['Record (PR)', yFmt(pr), ACCENT], ['Séances', n]])
    return
  }

  const range = maxV-minV
  const vMin = minV-range*0.15, vMax = maxV+range*0.22

  const _cont = dv.container.closest('.markdown-preview-section,.markdown-rendered,.cm-preview-code-block') || dv.container.parentElement || dv.container
  const W = Math.max(380,(_cont.offsetWidth||_cont.clientWidth||600)-52), H=220
  const PAD={top:20,right:20,bottom:38,left:54}
  const cw=W-PAD.left-PAD.right, ch=H-PAD.top-PAD.bottom
  const dpr = window.devicePixelRatio||1
  const canvas = cnt.createEl('canvas')
  canvas.width=W*dpr; canvas.height=H*dpr
  canvas.style.cssText=`width:100%;height:${H}px;display:block;margin-bottom:14px;`
  const ctx=canvas.getContext('2d'); ctx.scale(dpr,dpr)
  const xOf = i => PAD.left+(i/(n-1||1))*cw
  const yOf = v => PAD.top+ch-((v-vMin)/(vMax-vMin))*ch

  ctx.strokeStyle=BORDER+'66'; ctx.lineWidth=1; ctx.setLineDash([3,3])
  for (let i=0;i<=4;i++) { const v=vMin+(vMax-vMin)*(i/4), y=yOf(v)
    ctx.beginPath(); ctx.moveTo(PAD.left,y); ctx.lineTo(W-PAD.right,y); ctx.stroke()
    ctx.fillStyle=MUTED; ctx.font='10px Inter,sans-serif'; ctx.textAlign='right'; ctx.fillText(yFmt(v), PAD.left-4, y+4)
  }
  ctx.setLineDash([])

  const grad=ctx.createLinearGradient(0,PAD.top,0,PAD.top+ch)
  grad.addColorStop(0,color+'44'); grad.addColorStop(1,color+'06')
  ctx.beginPath(); ctx.moveTo(xOf(0),yOf(points[0].value))
  for (let i=1;i<n;i++) ctx.lineTo(xOf(i),yOf(points[i].value))
  ctx.lineTo(xOf(n-1),PAD.top+ch); ctx.lineTo(xOf(0),PAD.top+ch); ctx.closePath()
  ctx.fillStyle=grad; ctx.fill()

  ctx.strokeStyle=color; ctx.lineWidth=2.5; ctx.lineJoin='round'
  ctx.beginPath(); ctx.moveTo(xOf(0),yOf(points[0].value))
  for (let i=1;i<n;i++) ctx.lineTo(xOf(i),yOf(points[i].value))
  ctx.stroke()

  for (let i=0;i<n;i++) {
    const isPR = points[i].value===pr && points.findIndex(p=>p.value===pr)===i
    ctx.beginPath(); ctx.arc(xOf(i),yOf(points[i].value), isPR?5.5:3.5,0,Math.PI*2)
    ctx.fillStyle = isPR?ACCENT:color; ctx.fill()
    if (isPR) {
      ctx.fillStyle=ACCENT; ctx.font='bold 9px Inter,sans-serif'
      ctx.textAlign = i===0 ? 'left' : i===n-1 ? 'right' : 'center'
      const lx = i===0 ? xOf(i)+4 : i===n-1 ? xOf(i)-4 : xOf(i)
      ctx.fillText('PR', lx, yOf(points[i].value)-9)
    }
  }

  const labelIdxs = [0, Math.floor(n/2), n-1].filter((v,i,a)=>a.indexOf(v)===i && n>1)
  for (const i of labelIdxs) {
    const [y,m,d] = points[i].date.split('-')
    ctx.fillStyle=MUTED; ctx.font='9px Inter,sans-serif'; ctx.textAlign='center'
    ctx.fillText(`${d}/${m}/${y.slice(2)}`, xOf(i), PAD.top+ch+14)
  }

  miniStatsRow(cnt, [
    ['Record (PR)', yFmt(pr), ACCENT],
    [n>1?'Valeur initiale':'-', yFmt(startV)],
    ['Progression', (delta>=0?'+':'-')+yFmt(Math.abs(delta)), delta>=0?GAIN_C:'#d20f39'],
    ['Séances', n],
  ])
}

const _renderExerciseChart = (cnt, name) => {
  const points = []
  for (const w of ALL) {
    const ex = (w.exercises||[]).find(e=>e.name===name)
    if (!ex) continue
    const sets = workingSets(ex)
    const maxW = Math.max(0, ...sets.map(s=>s.weight_kg||0))
    if (maxW<=0) continue
    points.push({date:w.date, value:maxW})
  }
  _drawLineChart(cnt, points, { yFmt: v=>v.toFixed(1).replace(/\.0$/,'')+' kg', color: SPORT_C })
}

const _renderVolumeChart = cnt => {
  const points = ALL.map(w => ({date:w.date, value:workoutVolume(w)})).filter(p=>p.value>0)
  _drawLineChart(cnt, points, { yFmt: v=>fmtVol(v), color: ACCENT })
}

// ══ ONGLET RECORDS ═══════════════════════════════════════════════
const renderRecords = cnt => {
  const hdr = cnt.createDiv(); hdr.style.cssText='display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:4px;'
  hdr.createEl('h3',{attr:{style:'font-size:0.9em;font-weight:800;color:var(--text-normal);margin:0;'}}).textContent='🏆 Records personnels'
  hdr.createEl('span',{attr:{style:'font-size:0.72em;color:var(--text-muted);'}}).textContent='meilleur poids × reps par exercice'

  if (!allExercises.length) {
    cnt.createEl('p',{attr:{style:'color:var(--text-muted);font-style:italic;font-size:0.85em;'}}).textContent='Aucun exercice enregistré.'
    return
  }

  const grid = cnt.createDiv()
  grid.style.cssText = `display:grid;grid-template-columns:${isMobile?'1fr':'repeat(2,1fr)'};gap:10px;`
  for (const name of allExercises) {
    const pr = computePR(name)
    const card = grid.createDiv()
    card.style.cssText = `background:var(--background-secondary);border-radius:10px;padding:12px 14px;border-left:3px solid ${YELLOW_C};`
    card.createEl('div',{attr:{style:'font-size:0.85em;font-weight:700;color:var(--text-normal);margin-bottom:6px;'}}).textContent = name
    if (pr) {
      const r1 = card.createDiv(); r1.style.cssText='display:flex;justify-content:space-between;font-size:0.78em;color:var(--text-muted);'
      r1.createEl('span').textContent='Record'
      r1.createEl('b',{attr:{style:`color:${YELLOW_C};`}}).textContent = `${pr.weight} kg × ${pr.reps}`
      const r2 = card.createDiv(); r2.style.cssText='display:flex;justify-content:space-between;font-size:0.78em;color:var(--text-muted);margin-top:2px;'
      r2.createEl('span').textContent='Le'
      r2.createEl('span').textContent=fmtDateFr(pr.date)
    } else {
      card.createEl('div',{attr:{style:'font-size:0.78em;color:var(--text-faint);font-style:italic;'}}).textContent='Pas de charge enregistrée'
    }
  }
}

// ══ ONGLET SÉANCES ═══════════════════════════════════════════════
const renderSeances = cnt => {
  const recent = [...ALL].reverse().slice(0, 25)

  for (const w of recent) {
    const isManual = w._source === 'manuel'
    const card = cnt.createDiv()
    card.style.cssText = 'background:var(--background-secondary);border-radius:10px;padding:13px 15px;margin-bottom:9px;'

    const hdr = card.createDiv()
    hdr.style.cssText = 'display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:7px;gap:8px;'

    const left = hdr.createDiv()
    const titleRow = left.createDiv(); titleRow.style.cssText='display:flex;align-items:center;gap:7px;flex-wrap:wrap;'
    titleRow.createEl('span',{attr:{style:'font-size:0.93em;font-weight:700;color:var(--text-normal);'}}).textContent = w.title || 'Séance'
    titleRow.createEl('span',{attr:{style:`font-size:0.65em;font-weight:700;padding:1px 7px;border-radius:9px;color:#fff;background:${isManual?YELLOW_C:HEVY_C};`}}).textContent = isManual ? 'Manuel' : 'Hevy'
    const meta = left.createDiv()
    meta.style.cssText = 'display:flex;gap:10px;margin-top:2px;flex-wrap:wrap;'
    meta.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);'}}).textContent = fmtDateFr(w.date)
    if (w.duration_minutes > 0)
      meta.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);'}}).textContent = '⏱ '+fmtDur(w.duration_minutes)
    const vol = workoutVolume(w)
    if (vol > 0)
      meta.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);'}}).textContent = '🏋️ '+fmtVol(vol)

    const rightWrap = hdr.createDiv(); rightWrap.style.cssText='display:flex;align-items:center;gap:6px;flex-shrink:0;'
    const nbEx = (w.exercises||[]).length
    if (nbEx > 0)
      rightWrap.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);background:var(--background-primary);padding:2px 8px;border-radius:10px;white-space:nowrap;'}}).textContent = nbEx+' exercice'+(nbEx>1?'s':'')
    if (isManual) {
      const editBtn = rightWrap.createEl('button')
      editBtn.textContent = '✏️'
      editBtn.title = 'Modifier'
      editBtn.style.cssText = 'background:none;border:none;cursor:pointer;font-size:0.85em;padding:2px 4px;'
      editBtn.onclick = () => openWorkoutModal(w)
      const delBtn = rightWrap.createEl('button')
      delBtn.textContent = '🗑️'
      delBtn.title = 'Supprimer'
      delBtn.style.cssText = 'background:none;border:none;cursor:pointer;font-size:0.85em;padding:2px 4px;'
      delBtn.onclick = () => confirmDeleteWorkout(w)
    }

    const exList = card.createDiv()
    exList.style.cssText = 'display:flex;flex-direction:column;gap:3px;'

    for (const ex of (w.exercises||[])) {
      const sets = workingSets(ex)
      const maxKg = Math.max(0, ...sets.map(s=>s.weight_kg||0))
      const maxR  = sets.reduce((b,s)=>s.weight_kg===maxKg?Math.max(b,s.reps||0):b, 0)
      const nbS   = sets.length

      const row = exList.createDiv()
      row.style.cssText = 'display:flex;align-items:center;gap:6px;font-size:0.8em;'
      row.createEl('span',{attr:{style:'color:'+SPORT_C+';font-size:0.85em;'}}).textContent='▸'
      row.createEl('span',{attr:{style:'flex:1;color:var(--text-normal);'}}).textContent = ex.name
      const detail = row.createEl('span',{attr:{style:'color:var(--text-muted);white-space:nowrap;'}})
      if (maxKg > 0) detail.textContent = `${nbS} × - max ${maxKg} kg × ${maxR} reps`
      else if (maxR > 0) detail.textContent = `${nbS} × - ${maxR} reps`
      else detail.textContent = `${nbS} série${nbS>1?'s':''}`
    }
    if (!nbEx) {
      exList.createEl('div',{attr:{style:'font-size:0.78em;color:var(--text-faint);font-style:italic;'}}).textContent = 'Pas de détail d\'exercice pour cette séance.'
    }
  }

  if (ALL.length > 25) {
    const more = cnt.createDiv()
    more.style.cssText = 'text-align:center;font-size:0.8em;color:var(--text-muted);padding:8px;'
    more.textContent = `… et ${ALL.length - 25} séances plus anciennes`
  }
}

// ── GO ────────────────────────────────────────────────────────────
if (ALL.length) renderAll()
```
