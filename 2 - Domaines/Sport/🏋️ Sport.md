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
// 🏋️ SPORT - Suivi performances (import Hevy)
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

// ── LOAD DATA ────────────────────────────────────────────────────
const loadWorkouts = async () => {
  const ws = []
  const files = app.vault.getFiles().filter(f =>
    f.path.startsWith(SPORT_DIR + '/') && /^hevy_\d{4}\.json$/.test(f.name)
  )
  for (const f of files.sort((a,b) => a.name < b.name ? -1 : 1)) {
    try { ws.push(...JSON.parse(await app.vault.read(f))) } catch(e) {}
  }
  return ws.sort((a,b) => a.date < b.date ? -1 : 1)
}

const ALL = await loadWorkouts()
const today = localStr(new Date())
const thisWeek = getWeekMon(today)
const thisMonth = today.slice(0,7)

// ── COULEURS ─────────────────────────────────────────────────────
const cs = getComputedStyle(document.body)
const ACCENT   = cs.getPropertyValue('--interactive-accent').trim()   || '#1e66f5'
const MUTED    = cs.getPropertyValue('--text-muted').trim()           || '#888'
const BORDER   = cs.getPropertyValue('--background-modifier-border').trim() || '#e0e0e0'
const SPORT_C  = '#40a02b'

// ── STATE ─────────────────────────────────────────────────────────
if (!window._SPORT_STATE) window._SPORT_STATE = { tab: 'rythme', exercise: null }

// ── ROOT ──────────────────────────────────────────────────────────
const root = dv.el('div', '')
root.empty()

// ── EMPTY STATE ───────────────────────────────────────────────────
if (!ALL.length) {
  const empty = root.createDiv()
  empty.style.cssText = 'text-align:center;padding:60px 20px;color:var(--text-muted);'
  empty.innerHTML = `
    <div style="font-size:3em;margin-bottom:14px;">🏋️</div>
    <div style="font-size:1.1em;font-weight:700;margin-bottom:8px;color:var(--text-normal);">Aucune séance importée</div>
    <div style="font-size:0.85em;">Lance <code>import_hevy.py</code> pour importer ton export CSV Hevy,<br>ou <code>lancer_hevy.sh</code> depuis ton terminal.</div>
  `
  return
}

// ── CALCULS GLOBAUX ──────────────────────────────────────────────
const lastW = ALL[ALL.length - 1]
const daysAgo = daysBetween(lastW.date, today)
const sessMonth = ALL.filter(w => w.date.slice(0,7) === thisMonth).length
const sessWeek  = ALL.filter(w => getWeekMon(w.date) === thisWeek).length

// Streak semaines consécutives
const weekSet = new Set(ALL.map(w => getWeekMon(w.date)))
let streak = 0, chk = new Date(thisWeek + 'T12:00:00')
while (true) {
  const wk = localStr(chk)
  if (!weekSet.has(wk)) break
  streak++; chk.setDate(chk.getDate() - 7)
}

// Tous les exercices triés par fréquence
const exMap = {}
for (const w of ALL)
  for (const ex of w.exercises||[])
    exMap[ex.name] = (exMap[ex.name]||0) + 1
const allExercises = Object.entries(exMap).sort((a,b)=>b[1]-a[1]).map(([n])=>n)
if (!window._SPORT_STATE.exercise && allExercises.length)
  window._SPORT_STATE.exercise = allExercises[0]

// ── RENDU PRINCIPAL ───────────────────────────────────────────────
const renderAll = () => {
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
  statCard('📅','Ce mois', sessMonth + ' séances', thisMonth.slice(0,7).replace('-','/'))
  const lastLabel = daysAgo === 0 ? "Aujourd'hui" : daysAgo === 1 ? 'Hier' : `il y a ${daysAgo}j`
  statCard('🕒','Dernière', lastLabel, fmtDateFr(lastW.date))
  if (streak >= 2) statCard('🔥','Streak', streak + ' sem.', 'consécutives')
  else statCard('📆','Cette sem.', sessWeek + ' séance' + (sessWeek>1?'s':''))

  // ── TABS ──────────────────────────────────────────────────────
  const tabBar = root.createDiv()
  tabBar.style.cssText = 'display:flex;gap:2px;margin-bottom:16px;border-bottom:1px solid var(--background-modifier-border);'

  for (const [id, label] of [['rythme','📊 Rythme'],['progression','📈 Progression'],['seances','📋 Séances']]) {
    const active = window._SPORT_STATE.tab === id
    const btn = tabBar.createEl('button')
    btn.textContent = label
    btn.style.cssText = `padding:7px 16px;border:none;background:none;cursor:pointer;font-size:0.88em;font-weight:600;margin-bottom:-1px;border-bottom:2px solid ${active?ACCENT:'transparent'};color:${active?ACCENT:'var(--text-muted)'};transition:color .15s;`
    btn.onclick = () => { window._SPORT_STATE.tab = id; renderAll() }
  }

  const content = root.createDiv()
  if (window._SPORT_STATE.tab === 'rythme')      renderRythme(content)
  if (window._SPORT_STATE.tab === 'progression') renderProgression(content)
  if (window._SPORT_STATE.tab === 'seances')     renderSeances(content)
}

// ══ VUE RYTHME ════════════════════════════════════════════════════
const renderRythme = cnt => {
  const N = 16
  const weeks = []
  const base = new Date(thisWeek + 'T12:00:00')
  for (let i = N-1; i >= 0; i--) {
    const d = new Date(base); d.setDate(base.getDate() - i*7)
    weeks.push(localStr(d))
  }
  const counts = weeks.map(wk => ALL.filter(w => getWeekMon(w.date) === wk).length)
  const maxC = Math.max(...counts, 1)

  const _cont = dv.container.closest('.markdown-preview-section,.markdown-rendered,.cm-preview-code-block') || dv.container.parentElement || dv.container
  const W = Math.max(380, (_cont.offsetWidth || _cont.clientWidth || 600) - 24)
  const H = 190, PAD = {top:16,right:16,bottom:46,left:32}
  const cw = W-PAD.left-PAD.right, ch = H-PAD.top-PAD.bottom
  const dpr = window.devicePixelRatio||1

  const canvas = cnt.createEl('canvas')
  canvas.width = W*dpr; canvas.height = H*dpr
  canvas.style.cssText = `width:100%;height:${H}px;display:block;margin-bottom:14px;`
  const ctx = canvas.getContext('2d'); ctx.scale(dpr,dpr)

  const barW = cw/N*0.55, gap = cw/N

  // Grille
  ctx.strokeStyle = BORDER+'66'; ctx.lineWidth = 1; ctx.setLineDash([3,3])
  for (let i=1; i<=maxC; i++) {
    const y = PAD.top+ch - (i/maxC)*ch
    ctx.beginPath(); ctx.moveTo(PAD.left,y); ctx.lineTo(W-PAD.right,y); ctx.stroke()
    ctx.fillStyle=MUTED; ctx.font='10px Inter,sans-serif'; ctx.textAlign='right'
    ctx.fillText(i, PAD.left-4, y+4)
  }
  ctx.setLineDash([])

  // Barres
  for (let i=0; i<N; i++) {
    const x = PAD.left + i*gap + gap/2 - barW/2
    const c = counts[i]
    const isCurrent = weeks[i] === thisWeek
    if (c > 0) {
      const bH = (c/maxC)*ch
      ctx.fillStyle = isCurrent ? ACCENT : SPORT_C+'bb'
      ctx.fillRect(x, PAD.top+ch-bH, barW, bH)
    } else {
      ctx.fillStyle = BORDER+'88'
      ctx.fillRect(x, PAD.top+ch-2, barW, 2)
    }
    // Label date (toutes les 4 sem. + actuelle)
    if (i%4===0 || i===N-1 || isCurrent) {
      const dt = new Date(weeks[i]+'T12:00:00')
      ctx.fillStyle = isCurrent ? ACCENT : MUTED
      ctx.font = (isCurrent?'bold ':'')+'9px Inter,sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`${dt.getDate()}/${dt.getMonth()+1}`, x+barW/2, PAD.top+ch+14)
    }
  }

  // Légende couleurs
  const legRow = cnt.createDiv()
  legRow.style.cssText = 'display:flex;gap:14px;margin-bottom:12px;font-size:0.78em;color:var(--text-muted);'
  const leg = (color, label) => {
    const r = legRow.createDiv(); r.style.cssText = 'display:flex;align-items:center;gap:5px;'
    const sq = r.createEl('span'); sq.style.cssText = `display:inline-block;width:10px;height:10px;background:${color};border-radius:2px;`
    r.createEl('span').textContent = label
  }
  leg(SPORT_C+'bb', 'Séances passées')
  leg(ACCENT, 'Semaine en cours')

  // Mini stats
  const avgW = (ALL.length/N).toFixed(1)
  const bestW = Math.max(...counts)
  const activeW = counts.filter(c=>c>0).length

  const statsRow = cnt.createDiv()
  statsRow.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;'
  const miniStat = (label, val) => {
    const c = statsRow.createDiv()
    c.style.cssText = 'flex:1;min-width:90px;background:var(--background-secondary);border-radius:8px;padding:10px 12px;text-align:center;'
    c.createEl('div',{attr:{style:'font-size:0.72em;color:var(--text-muted);margin-bottom:2px;'}}).textContent = label
    c.createEl('div',{attr:{style:'font-size:1.05em;font-weight:700;'}}).textContent = val
  }
  miniStat('Semaines actives', `${activeW} / ${N}`)
  miniStat('Moy. / semaine', avgW)
  miniStat('Meilleure semaine', bestW)
  miniStat('Cette semaine', sessWeek)
}

// ══ VUE PROGRESSION ═══════════════════════════════════════════════
const renderProgression = cnt => {
  // Sélecteur
  const selRow = cnt.createDiv()
  selRow.style.cssText = 'display:flex;align-items:center;gap:10px;margin-bottom:14px;'
  selRow.createEl('span',{attr:{style:'font-size:0.85em;color:var(--text-muted);white-space:nowrap;'}}).textContent='💪 Exercice :'

  const sel = selRow.createEl('select')
  sel.style.cssText = 'flex:1;padding:6px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.88em;cursor:pointer;max-width:380px;'
  for (const ex of allExercises) {
    const opt = sel.createEl('option',{text:ex}); opt.value = ex
    if (ex === window._SPORT_STATE.exercise) opt.selected = true
  }

  const progCnt = cnt.createDiv()
  const drawProg = name => { progCnt.empty(); _renderProgChart(progCnt, name) }
  sel.onchange = () => { window._SPORT_STATE.exercise = sel.value; drawProg(sel.value) }
  drawProg(window._SPORT_STATE.exercise)
}

const _renderProgChart = (cnt, exerciseName) => {
  const points = []
  for (const w of ALL) {
    const ex = (w.exercises||[]).find(e=>e.name===exerciseName)
    if (!ex) continue
    const sets = ex.sets||[]
    const maxW = Math.max(...sets.map(s=>s.weight_kg||0))
    if (maxW <= 0) continue
    const maxR = sets.reduce((b,s)=>s.weight_kg===maxW?Math.max(b,s.reps||0):b, 0)
    points.push({date:w.date, weight:maxW, reps:maxR})
  }

  if (!points.length) {
    const e = cnt.createDiv()
    e.style.cssText = 'text-align:center;padding:40px;color:var(--text-muted);font-size:0.9em;'
    e.textContent = 'Aucune donnée pour cet exercice.'
    return
  }

  const ws = points.map(p=>p.weight)
  const minW = Math.min(...ws), maxW2 = Math.max(...ws)
  const pr = maxW2, startW = ws[0], delta = pr - startW
  const n = points.length
  const range = maxW2 - minW || 1
  const vMin = minW - range*0.15, vMax = maxW2 + range*0.22

  const _cont = dv.container.closest('.markdown-preview-section,.markdown-rendered,.cm-preview-code-block') || dv.container.parentElement || dv.container
  const W = Math.max(380, (_cont.offsetWidth || _cont.clientWidth || 600) - 24)
  const H = 220, PAD = {top:20,right:20,bottom:38,left:54}
  const cw = W-PAD.left-PAD.right, ch = H-PAD.top-PAD.bottom
  const dpr = window.devicePixelRatio||1

  const canvas = cnt.createEl('canvas')
  canvas.width = W*dpr; canvas.height = H*dpr
  canvas.style.cssText = `width:100%;height:${H}px;display:block;margin-bottom:14px;cursor:crosshair;`
  const ctx = canvas.getContext('2d'); ctx.scale(dpr,dpr)

  const xOf = i => PAD.left + (i/(n-1||1))*cw
  const yOf = v => PAD.top + ch - ((v-vMin)/(vMax-vMin))*ch

  // Grille
  ctx.strokeStyle = BORDER+'66'; ctx.lineWidth=1; ctx.setLineDash([3,3])
  for (let i=0; i<=4; i++) {
    const v = vMin + (vMax-vMin)*(i/4), y = yOf(v)
    ctx.beginPath(); ctx.moveTo(PAD.left,y); ctx.lineTo(W-PAD.right,y); ctx.stroke()
    ctx.fillStyle=MUTED; ctx.font='10px Inter,sans-serif'; ctx.textAlign='right'
    ctx.fillText(v.toFixed(1)+' kg', PAD.left-4, y+4)
  }
  ctx.setLineDash([])

  // Dégradé
  const grad = ctx.createLinearGradient(0,PAD.top,0,PAD.top+ch)
  grad.addColorStop(0, SPORT_C+'44'); grad.addColorStop(1, SPORT_C+'06')
  ctx.beginPath(); ctx.moveTo(xOf(0),yOf(points[0].weight))
  for (let i=1;i<n;i++) ctx.lineTo(xOf(i),yOf(points[i].weight))
  ctx.lineTo(xOf(n-1),PAD.top+ch); ctx.lineTo(xOf(0),PAD.top+ch)
  ctx.closePath(); ctx.fillStyle=grad; ctx.fill()

  // Ligne
  ctx.strokeStyle=SPORT_C; ctx.lineWidth=2.5; ctx.lineJoin='round'
  ctx.beginPath(); ctx.moveTo(xOf(0),yOf(points[0].weight))
  for (let i=1;i<n;i++) ctx.lineTo(xOf(i),yOf(points[i].weight))
  ctx.stroke()

  // Points (PR en accent)
  for (let i=0;i<n;i++) {
    const isPR = points[i].weight === pr
    ctx.beginPath(); ctx.arc(xOf(i),yOf(points[i].weight), isPR?5.5:3.5, 0, Math.PI*2)
    ctx.fillStyle = isPR ? ACCENT : SPORT_C; ctx.fill()
    if (isPR) {
      ctx.fillStyle=ACCENT; ctx.font='bold 9px Inter,sans-serif'; ctx.textAlign='center'
      ctx.fillText('PR', xOf(i), yOf(points[i].weight)-9)
    }
  }

  // Labels dates (début, milieu, fin)
  const labelIdxs = [0, Math.floor(n/2), n-1].filter((v,i,a)=>a.indexOf(v)===i&&n>1)
  for (const i of labelIdxs) {
    const [y,m,d] = points[i].date.split('-')
    ctx.fillStyle=MUTED; ctx.font='9px Inter,sans-serif'; ctx.textAlign='center'
    ctx.fillText(`${d}/${m}/${y.slice(2)}`, xOf(i), PAD.top+ch+14)
  }

  // Stats PR
  const statsRow = cnt.createDiv()
  statsRow.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;'
  const miniStat = (label, val, color='') => {
    const c = statsRow.createDiv()
    c.style.cssText = 'flex:1;min-width:90px;background:var(--background-secondary);border-radius:8px;padding:10px 12px;text-align:center;'
    c.createEl('div',{attr:{style:'font-size:0.72em;color:var(--text-muted);margin-bottom:2px;'}}).textContent = label
    c.createEl('div',{attr:{style:`font-size:1.05em;font-weight:700;${color?'color:'+color:''}`}}).textContent = val
  }
  miniStat('Record (PR)', pr+' kg', ACCENT)
  miniStat('Poids initial', startW+' kg')
  miniStat('Progression', (delta>=0?'+':'')+delta+' kg', delta>=0 ? SPORT_C : '#d20f39')
  miniStat('Séances', n)
}

// ══ VUE SÉANCES ═══════════════════════════════════════════════════
const renderSeances = cnt => {
  const recent = [...ALL].reverse().slice(0, 25)

  for (const w of recent) {
    const card = cnt.createDiv()
    card.style.cssText = 'background:var(--background-secondary);border-radius:10px;padding:13px 15px;margin-bottom:9px;'

    const hdr = card.createDiv()
    hdr.style.cssText = 'display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:7px;'

    const left = hdr.createDiv()
    left.createEl('div',{attr:{style:'font-size:0.93em;font-weight:700;color:var(--text-normal);'}}).textContent = w.title || 'Séance'
    const meta = left.createDiv()
    meta.style.cssText = 'display:flex;gap:10px;margin-top:2px;'
    meta.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);'}}).textContent = fmtDateFr(w.date)
    if (w.duration_minutes > 0)
      meta.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);'}}).textContent = '⏱ '+fmtDur(w.duration_minutes)

    // Nb d'exercices
    const nbEx = (w.exercises||[]).length
    hdr.createEl('span',{attr:{style:'font-size:0.75em;color:var(--text-muted);background:var(--background-primary);padding:2px 8px;border-radius:10px;white-space:nowrap;margin-top:2px;'}}).textContent = nbEx+' exercice'+(nbEx>1?'s':'')

    // Liste exercices
    const exList = card.createDiv()
    exList.style.cssText = 'display:flex;flex-direction:column;gap:3px;'

    for (const ex of (w.exercises||[])) {
      const sets = (ex.sets||[]).filter(s=>s.type!=='warmup')
      const maxKg = Math.max(...sets.map(s=>s.weight_kg||0), 0)
      const maxR  = sets.reduce((b,s)=>s.weight_kg===maxKg?Math.max(b,s.reps||0):b, 0)
      const nbS   = sets.length

      const row = exList.createDiv()
      row.style.cssText = 'display:flex;align-items:center;gap:6px;font-size:0.8em;'
      row.createEl('span',{attr:{style:'color:'+SPORT_C+';font-size:0.85em;'}}).textContent='▸'
      row.createEl('span',{attr:{style:'flex:1;color:var(--text-normal);'}}).textContent = ex.name
      const detail = row.createEl('span',{attr:{style:'color:var(--text-muted);white-space:nowrap;'}})
      if (maxKg > 0)
        detail.textContent = `${nbS} × - max ${maxKg} kg × ${maxR} reps`
      else if (maxR > 0)
        detail.textContent = `${nbS} × - ${maxR} reps`
      else
        detail.textContent = `${nbS} série${nbS>1?'s':''}`
    }
  }

  if (ALL.length > 25) {
    const more = cnt.createDiv()
    more.style.cssText = 'text-align:center;font-size:0.8em;color:var(--text-muted);padding:8px;'
    more.textContent = `… et ${ALL.length - 25} séances plus anciennes`
  }
}

// ── GO ────────────────────────────────────────────────────────────
renderAll()
```
