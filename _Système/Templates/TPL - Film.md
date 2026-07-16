<%*
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//  TPL - Film  (intégration TMDB / IMDb)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// ── Statut ──────────────────────────────────────
const statut = await tp.system.suggester(
  ["👁️ À voir", "▶️ En cours", "✅ Vu", "❌ Abandonné"],
  ["à voir", "en cours", "vu", "abandonné"]
)
const _fi_sub = {"à voir":"À voir","en cours":"En cours","vu":"Vu","abandonné":"Abandonné"}[statut] || "À voir"

// ── Variables (valeurs par défaut = mode manuel) ─
let titre = tp.file.title
let titre_original = ""
let tmdb_id = ""
let réalisateur = ""
let genres = []
let covers = []
let banniere = ""
let année = ""
let saga = ""
let synopsis = ""

// ── Clé TMDB depuis Config.md ───────────────────
let _TMDB_KEY = ""
try {
  const _cf=app.vault.getAbstractFileByPath("_Système/Config.md")
  if(_cf){const _cc=app.metadataCache.getFileCache(_cf); _TMDB_KEY=_cc?.frontmatter?.tmdb_api_key||""}
} catch(_e){}

// ── Source TMDB / IMDb (optionnel) ──────────────
const _src = await tp.system.prompt("ID ou URL TMDB/IMDb ? (Entrée pour mode manuel)", "")

if (_src && _src.trim()) {
  if (!_TMDB_KEY) {
    new Notice("⚠ Clé TMDB manquante - remplis _Système/Config.md",5000)
  } else {
    const _raw = _src.trim()
    let _tmdbId = null
    try {
      const _imdbM = _raw.match(/tt\d+/)
      if (_imdbM) {
        const _fr=await fetch(`https://api.themoviedb.org/3/find/${_imdbM[0]}?api_key=${_TMDB_KEY}&external_source=imdb_id`)
        const _fd=await _fr.json()
        _tmdbId = _fd.movie_results?.[0]?.id || null
      } else {
        const _nm=_raw.match(/\/movie\/(\d+)/)||_raw.match(/^(\d+)$/)
        if(_nm) _tmdbId=parseInt(_nm[1])
      }
      if (_tmdbId) {
        const _dr=await fetch(`https://api.themoviedb.org/3/movie/${_tmdbId}?api_key=${_TMDB_KEY}&language=fr-FR&append_to_response=credits`)
        const _mov=await _dr.json()

        // Choix du titre
        const _tO=[],_tV=[]
        if(_mov.title&&_mov.title!==_mov.original_title){_tO.push("🇫🇷 "+_mov.title);_tV.push(_mov.title)}
        if(_mov.original_title){_tO.push("🌐 "+_mov.original_title);_tV.push(_mov.original_title)}
        _tO.push("✏ Saisir manuellement");_tV.push(null)
        const _chosen=await tp.system.suggester(_tO,_tV)
        titre=_chosen||await tp.system.prompt("Titre",_mov.title||tp.file.title)

        tmdb_id=String(_tmdbId)
        titre_original=_mov.original_title||""
        genres=(_mov.genres||[]).map(g=>g.name)
        année=_mov.release_date?_mov.release_date.slice(0,4):""
        covers=_mov.poster_path?[`https://image.tmdb.org/t/p/original${_mov.poster_path}`]:[]
        banniere=_mov.backdrop_path?`https://image.tmdb.org/t/p/original${_mov.backdrop_path}`:""
        réalisateur=(_mov.credits?.crew||[]).find(c=>c.job==="Director")?.name||""
        if(_mov.belongs_to_collection) saga=_mov.belongs_to_collection.name||""
        synopsis = _mov.overview || ""

        new Notice("✓ TMDB : "+titre,2000)
      } else { new Notice("Film non trouvé sur TMDB",3000) }
    } catch(_e){ new Notice("❌ TMDB : "+_e.message,5000) }
  }
}

const _coversYaml = covers.length ? '['+covers.map(c=>`"${c}"`).join(',')+']' : '[]'
const _genresYaml = genres.length ? '['+genres.map(g=>`"${g.replace(/"/g,"'")}"`).join(',')+']' : '[]'
const _safeTitre = titre.replace(/[/\\:*?"<>|]/g,"")
await tp.file.move("2 - Domaines/Médias/Films/" + _fi_sub + "/" + _safeTitre)
-%>
---
type: film
created: <% tp.date.now("YYYY-MM-DD") %>
titre: "<% titre %>"
titre_original: "<% titre_original %>"
tmdb_id: <% tmdb_id %>
covers: <% _coversYaml %>
banniere: "<% banniere %>"
année: <% année %>
réalisateur: "<% réalisateur %>"
genre: <% _genresYaml %>
saga: "<% saga %>"
statut: "<% statut %>"
note:
date_visionnage:
tags: [film, média]
obsidianUIMode: preview
---

```dataviewjs
// ── Bouton Renommer ──────────────────────────────────────────────
{ const _p = dv.current(); if (!_p?.file) return;
dv.container.style.cssText = "margin:0;padding:0;";
const _run = (_t=0) => {
  if (_t > 25) return;
  let _el = dv.container.parentElement, _d = 0;
  while (_el && _d++ < 15 && !['markdown-preview-section','markdown-rendered','markdown-preview-view'].some(c => _el.classList.contains(c))) _el = _el.parentElement;
  const _h1 = _el?.querySelector('h1');
  if (!_h1) { setTimeout(()=>_run(_t+1), 60); return; }
  _h1.style.display = 'none';
  const _row = dv.container.createDiv();
  _row.style.cssText = 'display:flex;align-items:center;gap:10px;margin:var(--h1-margin,0.5em 0 0.8em);';
  const _ttl = _row.createEl('span');
  _ttl.textContent = _p.titre || _p.file.name;
  _ttl.style.cssText = 'font-size:var(--h1-size,1.9em);font-weight:var(--h1-weight,700);color:var(--h1-color,var(--text-normal));font-family:var(--font-text);line-height:1.2;';
  const _btn = _row.createEl('button');
  _btn.textContent='✏️'; _btn.title='Renommer';
  _btn.style.cssText='font-size:0.55em;padding:2px 7px;border-radius:5px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-muted);cursor:pointer;opacity:0.4;transition:opacity 0.15s;';
  _btn.onmouseenter=()=>_btn.style.opacity='1'; _btn.onmouseleave=()=>_btn.style.opacity='0.4';
  _btn.onclick = () => {
    const _inp = document.createElement('input'); _inp.type='text';
    _inp.value = _p.titre || _p.file.name;
    _inp.style.cssText='font-size:inherit;font-weight:inherit;color:inherit;font-family:inherit;border:none;border-bottom:2px solid var(--interactive-accent);background:transparent;outline:none;min-width:160px;';
    _ttl.replaceWith(_inp); _btn.style.display='none';
    const _ok=_row.createEl('button'); _ok.textContent='✅';
    _ok.style.cssText='font-size:0.6em;padding:3px 9px;border-radius:5px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;';
    const _x=_row.createEl('button'); _x.textContent='✕';
    _x.style.cssText='font-size:0.6em;padding:3px 7px;border-radius:5px;border:1px solid var(--background-modifier-border);background:transparent;color:var(--text-muted);cursor:pointer;';
    const _cancel=()=>{ _inp.replaceWith(_ttl); _ok.remove(); _x.remove(); _btn.style.display=''; };
    const _save=async()=>{
      const _v=_inp.value.trim(); if(!_v) return;
      _ttl.textContent=_v; _inp.replaceWith(_ttl); _ok.remove(); _x.remove(); _btn.style.display='';
      try {
        const _fp=_p.file.path, _f=app.vault.getAbstractFileByPath(_fp); if(!_f) return;
        const _c=await app.vault.read(_f);
        const _nc=_c.replace(/^(titre:\s*).*$/m, (_,g)=>`${g}"${_v.replace(/"/g,'\\"')}"`);
        if(_nc!==_c) await app.vault.modify(_f,_nc);
        const _np=(_p.file.folder?_p.file.folder+'/':'')+_v+'.md';
        if(_fp!==_np){
          await new Promise(res=>{
            const _chk=(_n=0)=>{
              if(app.plugins.plugins['dataview']?.api?.page(_fp)?.titre===_v||_n>20){res();return;}
              setTimeout(()=>_chk(_n+1),100);
            };
            setTimeout(()=>_chk(),100);
          });
          const _f2=app.vault.getAbstractFileByPath(_fp);
          if(_f2) await app.fileManager.renameFile(_f2,_np);
          const _leaf=app.workspace.activeLeaf;
          await new Promise(res=>{const _w=(_n=0)=>{if(_n>30){res();return;}if(app.plugins.plugins['dataview']?.api?.page(_np)?.file){const _nf2=app.vault.getAbstractFileByPath(_np);if(_nf2&&_leaf){_leaf.openFile(_nf2).then(res);}else{res();}}else{setTimeout(()=>_w(_n+1),100);}};setTimeout(()=>_w(),150);});
        }
        new Notice('✅ '+_v);
      } catch(e){ new Notice('❌ '+e.message); }
    };
    _ok.onclick=_save; _x.onclick=_cancel;
    _inp.onkeydown=e=>{ if(e.key==='Enter')_save(); if(e.key==='Escape')_cancel(); };
    _row.append(_ok,_x); _inp.focus(); _inp.select();
  };
  _row.append(_ttl,_btn);
};
setTimeout(()=>_run(),80); }
```

# <% tp.file.title %>

```dataviewjs
const { Menu, Notice } = require('obsidian')
const p = dv.current()
if (!p?.file) { const _rr=(_n=0)=>{ if(_n>25)return; setTimeout(()=>{ const _nf=app.vault.getAbstractFileByPath(dv.currentFilePath); (_nf&&app.plugins.plugins['dataview']?.api?.page(dv.currentFilePath)?.file)?app.workspace.activeLeaf?.openFile(_nf):_rr(_n+1); },200); }; _rr(); return; }
const covers = Array.isArray(p.covers) ? p.covers : []
const file = app.vault.getAbstractFileByPath(p.file.path)

const getSrc = v => {
  if (!v) return null
  if (v.startsWith("http")) return v
  const f = app.metadataCache.getFirstLinkpathDest(v, "")
  return f ? app.vault.adapter.getResourcePath(f.path) : null
}
const moveToFolder = async (targetFolder) => {
  const f = app.vault.getAbstractFileByPath(p.file.path)
  if (!f || f.parent.path === targetFolder) return
  try { await app.vault.adapter.mkdir(targetFolder) } catch(e) {}
  await app.fileManager.renameFile(f, targetFolder + "/" + f.name)
  new Notice("Déplacé - " + targetFolder.split("/").pop(), 2000)
}

const save = async (key, val) => {
  try {
    await app.fileManager.processFrontMatter(file, fm => { fm[key] = val })
  } catch(e) { new Notice("Erreur sauvegarde : " + e.message, 4000) }
}

const showForm = (title, fields, onSubmit) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:300px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 18px;font-size:1em;font-weight:700;"}}).textContent = title
  const inputs = {}
  for (const [key, cfg] of Object.entries(fields)) {
    const g = box.createEl("div", {attr:{style:"margin-bottom:12px;"}})
    g.createEl("label", {attr:{style:"font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"}}).textContent = cfg.label
    if (cfg.type === "datepicker") {
      const mock = {value: cfg.value || ""}
      mkDatePicker(g, cfg.value || "", v => { mock.value = v }, cfg.placeholder || "Choisir une date")
      inputs[key] = mock
    } else {
      const inp = g.createEl("input", {attr:{type:cfg.type||"text",placeholder:cfg.placeholder||"",value:String(cfg.value||""),style:"width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.92em;box-sizing:border-box;"}})
      inputs[key] = inp
    }
  }
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:16px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);"}})
  cancel.textContent = "Annuler"
  cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = () => { overlay.remove(); onSubmit(Object.fromEntries(Object.entries(inputs).map(([k,v]) => [k,v.value.trim?.() ?? v.value]))) }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => Object.values(inputs).find(v => v.focus)?.focus(), 50)
}

const showTextForm = (title, currentText, onSubmit) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:340px;max-width:560px;width:92%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 14px;font-size:1em;font-weight:700;"}}).textContent = title
  const ta = box.createEl("textarea", {attr:{style:"width:100%;height:200px;padding:8px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.88em;box-sizing:border-box;resize:vertical;line-height:1.6;font-family:var(--font-text);"}})
  ta.value = currentText
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:14px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);"}})
  cancel.textContent = "Annuler"
  cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = () => { overlay.remove(); onSubmit(ta.value.trim()) }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Escape") overlay.remove() }
  setTimeout(() => ta.focus(), 50)
}

const editBodySection = async (label, keyword) => {
  const raw = await app.vault.read(file)
  const lines = raw.split('\n')
  let headIdx = -1, headLevel = 2
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s+(.*)$/)
    if (m && lines[i].toLowerCase().includes(keyword.toLowerCase())) {
      headIdx = i; headLevel = m[1].length; break
    }
  }
  if (headIdx === -1) { new Notice("Section introuvable : " + keyword, 3000); return }
  let endIdx = lines.length
  for (let i = headIdx + 1; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s/)
    if (m && m[1].length <= headLevel) { endIdx = i; break }
    if (lines[i].trim() === '---') { endIdx = i; break }
  }
  const currentContent = lines.slice(headIdx + 1, endIdx).join('\n').trim()
  showTextForm("✏ " + label, currentContent, async newContent => {
    const newLines = [...lines.slice(0, headIdx + 1), '', newContent, '', ...lines.slice(endIdx)]
    await app.vault.modify(file, newLines.join('\n'))
    new Notice("✓ " + label + " mis à jour", 2000)
  })
}

const editField = (key, label, cur, isNum) => showForm("Modifier - " + label,
  {v: {label, value: cur, type: isNum ? "number" : "text"}},
  async ({v}) => { if (v !== "") await save(key, isNum ? parseFloat(v) : v) })

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

const MOVE_MAP = {"à voir":"2 - Domaines/Médias/Films/À voir","en cours":"2 - Domaines/Médias/Films/En cours","vu":"2 - Domaines/Médias/Films/Vu","abandonné":"2 - Domaines/Médias/Films/Abandonné"}
;(function(){
  const _t = MOVE_MAP[p.statut]
  if (!_t) return
  const _f = app.vault.getAbstractFileByPath(p.file.path)
  if (_f && _f.parent && _f.parent.path !== _t) setTimeout(() => { try { moveToFolder(_t) } catch(e) {} }, 500)
})()
// ── Auto-rename : fichier = titre ────────────────
;(function(){
  if(!p?.titre||!p?.file) return
  const _safe=p.titre.replace(/[/\\:*?"<>|]/g,"")
  const _cur=p.file.name.replace(/\.md$/,"")
  if(_cur===_safe) return
  const _f=app.vault.getAbstractFileByPath(p.file.path)
  if(!_f) return
  setTimeout(async()=>{
    try{ await app.fileManager.renameFile(_f,(p.file.folder?p.file.folder+"/":"")+_safe+".md") }catch(_e){}
  },1200)
})()
const STATUS_COLOR = {"a voir":"#8839ef","en cours":"#1e66f5","vu":"#40a02b","abandonne":"#d20f39"}
const STATUS_LIST  = ["à voir","en cours","vu","abandonné"]
const STATUS_KEY   = {"à voir":"a voir","en cours":"en cours","vu":"vu","abandonné":"abandonne"}
const sColor = STATUS_COLOR[STATUS_KEY[p.statut]] || "var(--text-muted)"

const isMobile = window.innerWidth < 700

// ── Bannière ──────────────────────────────────────────
const bannSrc = p.banniere ? (p.banniere.startsWith("http") ? p.banniere : (() => { const bf = app.metadataCache.getFirstLinkpathDest(p.banniere, ""); return bf ? app.vault.adapter.getResourcePath(bf.path) : null })()) : null
if (bannSrc) {
  const bannWrap = this.container.createEl("div", {attr:{style:"margin-bottom:14px;border-radius:10px;overflow:hidden;"}})
  bannWrap.createEl("img", {attr:{src:bannSrc, style:"width:100%;max-height:200px;object-fit:cover;display:block;"}})
}

const top = this.container.createEl("div", {attr:{style:`display:flex;flex-direction:${isMobile?"column":"row"};gap:20px;margin-bottom:16px;align-items:${isMobile?"center":"flex-start"};`}})
const mainSrc = getSrc(covers[0])
if (mainSrc) {
  top.createEl("img", {attr:{src:mainSrc, style:`width:${isMobile?"120px":"150px"};flex-shrink:0;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.25);`}})
} else {
  const ph = top.createEl("div", {attr:{style:`width:${isMobile?"120px":"150px"};height:${isMobile?"168px":"210px"};flex-shrink:0;border-radius:10px;background:var(--background-modifier-border);display:flex;align-items:center;justify-content:center;font-size:2em;color:var(--text-muted);`}})
  ph.textContent = "🎬"
}
const infoCol = top.createEl("div", {attr:{style:`flex:1;display:flex;flex-direction:column;gap:6px;padding-top:${isMobile?"10px":"4px"};${isMobile?"width:100%;":""}`}})

const mkRow = (label, display, onEdit) => {
  const r = infoCol.createEl("div", {attr:{style:"display:flex;gap:10px;font-size:0.85em;align-items:center;"}})
  r.createEl("span", {attr:{style:"color:var(--text-muted);width:90px;flex-shrink:0;"}}).textContent = label
  const valWrap = r.createEl("span", {attr:{style:"display:flex;align-items:center;gap:5px;flex:1;" + (onEdit ? "cursor:pointer;" : "")}})
  const val = valWrap.createEl("span", {attr:{style:"color:var(--text-normal);font-weight:500;"}})
  val.textContent = display
  if (onEdit) {
    valWrap.addEventListener("click", onEdit)
    valWrap.title = "Cliquer pour modifier"
    valWrap.onmouseenter = () => { val.style.textDecoration = "underline"; val.style.color = "var(--interactive-accent)" }
    valWrap.onmouseleave = () => { val.style.textDecoration = ""; val.style.color = "var(--text-normal)" }
  }
}

const sRow = infoCol.createEl("div", {attr:{style:"display:flex;gap:10px;font-size:0.85em;align-items:center;"}})
sRow.createEl("span", {attr:{style:"color:var(--text-muted);width:90px;flex-shrink:0;"}}).textContent = "Statut"
const badge = sRow.createEl("span", {attr:{style:"background:" + sColor + ";color:#fff;padding:2px 9px;border-radius:10px;font-size:0.85em;font-weight:600;cursor:pointer;user-select:none;"}})
badge.textContent = p.statut || "-"
badge.onclick = e => {
  e.stopPropagation()
  const menu = new Menu()
  STATUS_LIST.forEach(s => menu.addItem(i => { i.setTitle((s === p.statut ? "✓ " : "  ") + s); i.onClick(() => save("statut", s)) }))
  menu.showAtMouseEvent(e)
}

mkRow("Année",       p.année != null ? String(p.année) : "-",  () => editField("année", "Année", p.année, true))
mkRow("Réalisateur", p.réalisateur || "-",  () => editField("réalisateur", "Réalisateur", p.réalisateur || "", false))
const _g = (v => { if (!v || v === "") return ""; if (typeof v === "string") return v; try { return [...v].filter(Boolean).join(", ") } catch(e) { return "" } })(p.genre)
mkRow("Genre", _g || "-", () => editField("genre", "Genre", _g, false))
if (p.titre_original) mkRow("Titre VO", p.titre_original, () => editField("titre_original", "Titre original (VO)", p.titre_original||"", false))
if (p.saga) mkRow("Saga", p.saga, () => editField("saga", "Saga", p.saga||"", false))
const fmtDateFr = iso => {
  if (!iso) return "-"
  const s = String(iso).slice(0, 10)
  const [y, m, d] = s.split("-")
  const M = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
  return parseInt(d) + " " + (M[parseInt(m)-1] || m) + " " + y
}
mkRow("Vu le", fmtDateFr(p.date_visionnage), () => {
  const today = new Date().toISOString().slice(0, 10)
  showForm("Modifier - Vu le", {
    date: {label:"Date de visionnage", value: String(p.date_visionnage || today), type:"datepicker"}
  }, async ({date}) => { if (date) await save("date_visionnage", date) })
})

const nRow = infoCol.createEl("div", {attr:{style:"display:flex;gap:10px;font-size:0.85em;align-items:center;"}})
nRow.createEl("span", {attr:{style:"color:var(--text-muted);width:90px;flex-shrink:0;"}}).textContent = "Note"
const sel = nRow.createEl("select", {attr:{style:"background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:6px;padding:2px 8px;color:var(--text-normal);font-size:0.88em;cursor:pointer;"}})
sel.createEl("option", {attr:{value:""}}).textContent = "-"
for (let i = 1; i <= 10; i++) {
  const opt = sel.createEl("option", {attr:{value:String(i)}})
  opt.textContent = i + " / 10"
  if (p.note === i) opt.selected = true
}
sel.onchange = () => { const v = parseInt(sel.value); if (v) save("note", v) }

const editBanniere = () => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:300px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 14px;font-size:1em;font-weight:700;"}}).textContent = "🌅 Bannière"
  const g = box.createEl("div", {attr:{style:"margin-bottom:12px;"}})
  g.createEl("label", {attr:{style:"font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"}}).textContent = "URL ou fichier (image large)"
  const inp = g.createEl("input", {attr:{type:"text",value:p.banniere||"",placeholder:"https://... ou nom-du-fichier.jpg",style:"width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;"}})
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:16px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);"}})
  cancel.textContent = "Annuler"; cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = async () => { const v = inp.value.trim(); await save("banniere", v); overlay.remove(); new Notice("Bannière mise à jour !", 2000) }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => inp.focus(), 50)
}

const actBar = this.container.createEl("div", {attr:{style:"display:flex;gap:8px;flex-wrap:wrap;padding-top:2px;margin-bottom:12px;"}})
const btnBann = actBar.createEl("button", {attr:{style:BTN}})
btnBann.textContent = "🌅 Bannière"
btnBann.onclick = () => editBanniere()
const btnMod = actBar.createEl("button", {attr:{style:BTN}})
btnMod.textContent = "✏ Modifier"
btnMod.onclick = e => {
  const menu = new Menu()
  menu.addItem(it => { it.setTitle("✏ Synopsis"); it.onClick(() => editBodySection("Synopsis", "synopsis")) })
  menu.addItem(it => { it.setTitle("✏ Mon avis"); it.onClick(() => editBodySection("Mon avis", "avis")) })
  menu.addItem(it => { it.setTitle("✏ Ce que je retiens"); it.onClick(() => editBodySection("Ce que je retiens", "retiens")) })
  menu.addItem(it => { it.setTitle("✏ Liens"); it.onClick(() => editBodySection("Liens", "liens")) })
  menu.addSeparator()
  const curC = Array.isArray(p.covers) ? [...p.covers] : []
  curC.forEach((cv, idx) => menu.addItem(it => {
    it.setTitle("🖼 Couverture " + String(idx+1).padStart(2,"0") + (cv ? " ✓" : " (vide)"))
    it.onClick(() => showForm("Modifier - Couverture " + String(idx+1).padStart(2,"0"),
      {src: {label:"URL ou fichier dans _Système/Attachments/", value:cv||""}},
      async ({src}) => {
        if (!src) return
        if (!src.startsWith("http") && !app.metadataCache.getFirstLinkpathDest(src, "")) { new Notice('"' + src + '" introuvable.', 4000); return }
        curC[idx] = src; await save("covers", curC); new Notice("Cover mise à jour !", 2000)
      }))
  }))
  menu.addItem(it => { it.setTitle("➕ Ajouter une cover"); it.onClick(() => showForm("Nouvelle cover",
    {src: {label:"URL ou fichier dans _Système/Attachments/", value:""}},
    async ({src}) => { if (!src) return; curC.push(src); await save("covers", curC); new Notice("Cover ajoutée !", 2000) })) })
  if (curC.length > 0) menu.addItem(it => { it.setTitle("🗑 Supprimer la dernière"); it.onClick(async () => { curC.pop(); await save("covers", curC); new Notice("Supprimée.", 2000) }) })
  menu.showAtMouseEvent(e)
}
```

## 🎬 Synopsis
<% synopsis %>

## 💭 Mon avis


## 💡 Ce que je retiens


## 🔗 Liens
-

---
*Ajouté le <% tp.date.now("DD/MM/YYYY") %>*
