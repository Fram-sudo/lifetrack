<%*
const statut = await tp.system.suggester(
  ["📖 À lire", "▶️ En cours", "✅ Lu", "❌ Abandonné"],
  ["à lire", "en cours", "lu", "abandonné"]
);

const _lv_sub = {"à lire":"À lire","en cours":"En cours","lu":"Terminé","abandonné":"Abandonné"}[statut] || "À lire"
await tp.file.move("2 - Domaines/Médias/Romans & Livres/" + _lv_sub + "/" + tp.file.title)
-%>
---
type: livre
created: <% tp.date.now("YYYY-MM-DD") %>
titre: "<% tp.file.title %>"
covers: []
auteur: ""
genre: []
tomes: 1
pages:
pages_lues: 0
statut: "<% statut %>"
note:
date_début: <% tp.date.now("YYYY-MM-DD") %>
date_fin:
tags: [livre, média]
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

const MOVE_MAP = {"à lire":"2 - Domaines/Médias/Romans & Livres/À lire","en cours":"2 - Domaines/Médias/Romans & Livres/En cours","lu":"2 - Domaines/Médias/Romans & Livres/Terminé","abandonné":"2 - Domaines/Médias/Romans & Livres/Abandonné"}
;(function(){
  const _t = MOVE_MAP[p.statut]
  if (!_t) return
  const _f = app.vault.getAbstractFileByPath(p.file.path)
  if (_f && _f.parent && _f.parent.path !== _t) setTimeout(() => { try { moveToFolder(_t) } catch(e) {} }, 500)
})()
const STATUS_COLOR = {"a lire":"#8839ef","en cours":"#1e66f5","lu":"#40a02b","abandonne":"#d20f39"}
const STATUS_LIST  = ["à lire","en cours","lu","abandonné"]
const STATUS_KEY   = {"à lire":"a lire","en cours":"en cours","lu":"lu","abandonné":"abandonne"}
const sColor = STATUS_COLOR[STATUS_KEY[p.statut]] || "var(--text-muted)"

const isMobile = window.innerWidth < 700
const top = this.container.createEl("div", {attr:{style:`display:flex;flex-direction:${isMobile?"column":"row"};gap:20px;margin-bottom:16px;align-items:${isMobile?"center":"flex-start"};`}})
const mainSrc = getSrc(covers[0])
if (mainSrc) {
  top.createEl("img", {attr:{src:mainSrc, style:`width:${isMobile?"120px":"150px"};flex-shrink:0;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.25);`}})
} else {
  const ph = top.createEl("div", {attr:{style:`width:${isMobile?"120px":"150px"};height:${isMobile?"168px":"210px"};flex-shrink:0;border-radius:10px;background:var(--background-modifier-border);display:flex;align-items:center;justify-content:center;font-size:2em;color:var(--text-muted);`}})
  ph.textContent = "📚"
}
const infoCol = top.createEl("div", {attr:{style:`flex:1;display:flex;flex-direction:column;gap:6px;padding-top:${isMobile?"10px":"4px"};${isMobile?"width:100%;":""}`}})

const mkRow = (label, display, onEdit) => {
  const r = infoCol.createEl("div", {attr:{style:"display:flex;gap:10px;font-size:0.85em;align-items:center;"}})
  r.createEl("span", {attr:{style:"color:var(--text-muted);width:65px;flex-shrink:0;"}}).textContent = label
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
sRow.createEl("span", {attr:{style:"color:var(--text-muted);width:65px;flex-shrink:0;"}}).textContent = "Statut"
const badge = sRow.createEl("span", {attr:{style:"background:" + sColor + ";color:#fff;padding:2px 9px;border-radius:10px;font-size:0.85em;font-weight:600;cursor:pointer;user-select:none;"}})
badge.textContent = p.statut || "-"
badge.onclick = e => {
  e.stopPropagation()
  const menu = new Menu()
  STATUS_LIST.forEach(s => menu.addItem(i => { i.setTitle((s === p.statut ? "✓ " : "  ") + s); i.onClick(() => save("statut", s)) }))
  menu.showAtMouseEvent(e)
}

mkRow("Auteur", p.auteur || "-", () => editField("auteur", "Auteur", p.auteur || "", false))
const _g = (v => { if (!v || v === "") return ""; if (typeof v === "string") return v; try { return [...v].filter(Boolean).join(", ") } catch(e) { return "" } })(p.genre)
mkRow("Genre", _g || "-", () => editField("genre", "Genre", _g, false))
mkRow("Tomes",  p.tomes != null ? String(p.tomes) : "-", () => editField("tomes", "Nombre de tomes", p.tomes, true))
mkRow("Pages",  p.pages ? (p.pages_lues || 0) + " / " + p.pages + " p." : "-", () => editField("pages_lues", "Pages lues", p.pages_lues, true))
mkRow("Terminé le", p.date_fin || "-", () => {
  const today = new Date().toISOString().slice(0, 10)
  showForm("Modifier - Terminé le", {
    date: {label:"Date de fin", value: String(p.date_fin || today), type:"datepicker"}
  }, async ({date}) => { if (date) await save("date_fin", date) })
})

const nRow = infoCol.createEl("div", {attr:{style:"display:flex;gap:10px;font-size:0.85em;align-items:center;"}})
nRow.createEl("span", {attr:{style:"color:var(--text-muted);width:65px;flex-shrink:0;"}}).textContent = "Note"
const sel = nRow.createEl("select", {attr:{style:"background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:6px;padding:2px 8px;color:var(--text-normal);font-size:0.88em;cursor:pointer;"}})
sel.createEl("option", {attr:{value:""}}).textContent = "-"
for (let i = 1; i <= 10; i++) {
  const opt = sel.createEl("option", {attr:{value:String(i)}})
  opt.textContent = i + " / 10"
  if (p.note === i) opt.selected = true
}
sel.onchange = () => { const v = parseInt(sel.value); if (v) save("note", v) }

const nb = Math.max(p.tomes || 1, covers.length)
if (nb > 1) {
  const thumbRow = this.container.createEl("div", {attr:{style:"display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;"}})
  for (let i = 0; i < nb; i++) {
    const src = getSrc(covers[i])
    const col = thumbRow.createEl("div", {attr:{style:"display:flex;flex-direction:column;align-items:center;gap:4px;"}})
    if (src) {
      col.createEl("img", {attr:{src, style:"width:110px;height:155px;object-fit:cover;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.2);"}})
    } else {
      const phd = col.createEl("div", {attr:{style:"width:110px;height:155px;border-radius:8px;background:var(--background-modifier-border);display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:1.4em;"}})
      phd.textContent = "?"
    }
    col.createEl("span", {attr:{style:"font-size:0.72em;color:var(--text-muted);font-weight:600;"}}).textContent = "Tome " + String(i+1).padStart(2,"0")
  }
}

const actBar = this.container.createEl("div", {attr:{style:"display:flex;gap:8px;flex-wrap:wrap;padding-top:2px;margin-bottom:12px;"}})
const btnMod = actBar.createEl("button", {attr:{style:BTN}})
btnMod.textContent = "✏ Modifier"
btnMod.onclick = e => {
  const menu = new Menu()
  menu.addItem(it => { it.setTitle("✏ Résumé"); it.onClick(() => editBodySection("Résumé", "résumé")) })
  menu.addItem(it => { it.setTitle("✏ Mon avis"); it.onClick(() => editBodySection("Mon avis", "avis")) })
  menu.addItem(it => { it.setTitle("✏ Citations"); it.onClick(() => editBodySection("Citations", "citations")) })
  menu.addItem(it => { it.setTitle("✏ Idées"); it.onClick(() => editBodySection("Idées", "idées")) })
  menu.addItem(it => { it.setTitle("✏ Liens"); it.onClick(() => editBodySection("Liens", "liens")) })
  menu.addSeparator()
  const curC = Array.isArray(p.covers) ? [...p.covers] : []
  while (curC.length < (p.tomes || 0)) curC.push("")
  curC.forEach((cv, idx) => menu.addItem(it => {
    it.setTitle("🖼 Tome " + String(idx+1).padStart(2,"0") + (cv ? " ✓" : " (vide)"))
    it.onClick(() => showForm("Modifier - Tome " + String(idx+1).padStart(2,"0"),
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

## 📚 Résumé


## 💭 Mon avis


## 📝 Citations & Extraits
>

## 💡 Idées & réflexions


## 🔗 Liens
-

---
*Ajouté le <% tp.date.now("DD/MM/YYYY") %>*
