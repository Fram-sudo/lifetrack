<%*
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
//  TPL - Animé  (intégration AniList)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// ── Statut ──────────────────────────────────────
const statut = await tp.system.suggester(
  ["▶️ En cours", "👁️ À voir", "✅ Vu", "❌ Abandonné", "⏸️ En pause"],
  ["en cours", "à voir", "vu", "abandonné", "en pause"]
)
const _an_sub = {"en cours":"En cours","à voir":"À voir","vu":"Terminé","abandonné":"Abandonné","en pause":"En pause"}[statut] || "À voir"

// ── Variables (valeurs par défaut = mode manuel) ─
let titre = tp.file.title
let titre_original = ""
let anilist_id = ""
let studio = ""
let genres = []
let covers = []
let banniere = ""
let année = ""
let nbSaisons = 1
let saga = ""
let saga_num = 1
let saison_precedente = ""
let saison_suivante = ""
let épisodes = ""
let synopsis = ""

// ── Nettoyage HTML + traduction FR (descriptions AniList) ──
const _cleanTranslate = async (html) => {
  if (!html) return ""
  const _t = html.replace(/<br\s*\/?>/gi,' ').replace(/~![\s\S]*?!~/g,'').replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim()
  if (!_t) return ""
  try {
    const _r = await fetch('https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=fr&dt=t&q='+encodeURIComponent(_t))
    const _d = await _r.json()
    return _d[0].map(s=>s[0]).join('')
  } catch(_e) { return _t }
}

// ── Source AniList (optionnel) ───────────────────
const _src = await tp.system.prompt("ID ou URL AniList ? (Entrée pour mode manuel)", "")

if (_src && _src.trim()) {
  const _m = _src.trim().match(/(\d+)/)
  const _aid = _m ? parseInt(_m[1]) : null
  if (_aid) {
    try {
      const _q = `query($id:Int){Media(id:$id,type:ANIME){id title{romaji english native}format genres studios{nodes{name isAnimationStudio}}seasonYear episodes description coverImage{extraLarge}bannerImage relations{edges{relationType node{id title{romaji english native}type format seasonYear}}}}}`
      const _resp = await fetch("https://graphql.anilist.co",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:_q,variables:{id:_aid}})})
      const _data = await _resp.json()
      const _med = _data.data.Media

      // ── Choix du titre ──
      const _tO=[], _tV=[]
      if(_med.title.english){_tO.push("🇬🇧 "+_med.title.english);_tV.push(_med.title.english)}
      if(_med.title.romaji){_tO.push("🎌 "+_med.title.romaji);_tV.push(_med.title.romaji)}
      if(_med.title.native){_tO.push("🇯🇵 "+_med.title.native);_tV.push(_med.title.native)}
      _tO.push("✏ Saisir manuellement");_tV.push(null)
      const _chosen = await tp.system.suggester(_tO, _tV)
      titre = _chosen || await tp.system.prompt("Titre", _med.title.romaji || tp.file.title)
      // Langue choisie → utilisée pour les titres des notes saga liées
      const _langPref = (_med.title.english && titre === _med.title.english) ? 'english' : (_med.title.native && titre === _med.title.native) ? 'native' : 'romaji'
      const _getLinkedTitle = (t) => _langPref==='english' ? (t.english||t.romaji||t.native||'') : _langPref==='native' ? (t.native||t.romaji||t.english||'') : (t.romaji||t.english||t.native||'')

      // ── Infos ──
      anilist_id = String(_aid)
      titre_original = _med.title.romaji || ""
      genres = _med.genres || []
      studio = _med.studios?.nodes?.find(s=>s.isAnimationStudio)?.name || ""
      covers = _med.coverImage?.extraLarge ? [_med.coverImage.extraLarge, _med.coverImage.extraLarge] : []
      banniere = _med.bannerImage || ""
      année = _med.seasonYear ? String(_med.seasonYear) : ""
      nbSaisons = 1 // chaque entrée AniList = 1 saison
      épisodes = _med.episodes ? String(_med.episodes) : ""
      synopsis = await _cleanTranslate(_med.description || "")

      // ── Relations (prequels/sequels — saisons principales uniquement) ──
      const _MAIN_FMT = ["TV","TV_SHORT","ONA"]
      const _seqs=(_med.relations?.edges||[]).filter(e=>e.relationType==="SEQUEL"&&e.node.type==="ANIME"&&_MAIN_FMT.includes(e.node.format)).sort((a,b)=>(a.node.seasonYear||0)-(b.node.seasonYear||0))
      const _pres=(_med.relations?.edges||[]).filter(e=>e.relationType==="PREQUEL"&&e.node.type==="ANIME"&&_MAIN_FMT.includes(e.node.format)).sort((a,b)=>(a.node.seasonYear||0)-(b.node.seasonYear||0))

      if (_pres.length+_seqs.length > 0) {
        const _allRels=[..._pres,..._seqs]
        const _relLbls=_allRels.map(r=>`${r.relationType==="PREQUEL"?"⬅":"➡"} ${_getLinkedTitle(r.node.title)} (${r.node.seasonYear||"?"})`)
        const _doCreate = await tp.system.suggester(
          [`✅ Oui - créer ${_allRels.length} saison(s) liée(s) (${_relLbls.join(", ")})`, "⬜ Non - note courante uniquement"],
          [true, false]
        )
        if (_doCreate) {
          const _tplFile = app.vault.getAbstractFileByPath("_Système/Templates/TPL - Animé.md")
          const _rawTpl = await app.vault.read(_tplFile)
          const _tplEndTag='-'+'%'+'>'; let _bi=_rawTpl.indexOf(_tplEndTag)+_tplEndTag.length
          let _dc=0
          for(let _i=_bi;_i<_rawTpl.length-2;_i++){if(_rawTpl[_i]==='-'&&_rawTpl[_i+1]==='-'&&_rawTpl[_i+2]==='-'){_dc++;if(_dc===2){_bi=_i+3;break}_i+=2}}
          const _tplBody = _rawTpl.slice(_bi)
            .replace(new RegExp('^# <' + '% tp\\.file\\.title ' + '%' + '>$','m'),"# __TITRE__")
            .replace(new RegExp('<' + '%\\* for \\(let i = 1; i <= nbSaisons; i\\+\\+\\) \\{ -' + '%' + '>\\n','g'),"")
            .replace(new RegExp('## Saison <' + '% i ' + '%' + '>','g'),"## Saison 1")
            .replace(new RegExp('<' + '%\\* \\} -' + '%' + '>\\n','g'),"")
            .replace(new RegExp('<' + '% tp\\.date\\.now\\("DD\\/MM\\/YYYY"\\) ' + '%' + '>','g'),new Date().toLocaleDateString("fr-FR",{day:"2-digit",month:"2-digit",year:"numeric"}))

          const _allNotes=[
            ..._pres.map(r=>({titre:_getLinkedTitle(r.node.title),aid:r.node.id,year:r.node.seasonYear||0})),
            {titre,aid:_aid,year:_med.seasonYear||0},
            ..._seqs.map(r=>({titre:_getLinkedTitle(r.node.title),aid:r.node.id,year:r.node.seasonYear||0}))
          ].sort((a,b)=>a.year-b.year)

          // ── Détection saga existante dans le vault ──
          const _dvApi = app.plugins.plugins['dataview']?.api
          if (_dvApi) {
            for(const _rn of _allNotes){
              if(_rn.aid===_aid) continue
              const _ep=_dvApi.pages('"2 - Domaines/Médias/Animés"').where(p=>String(p.anilist_id)===String(_rn.aid)).first()
              if(_ep?.saga){saga=_ep.saga;break}
            }
          }
          if(!saga) saga=titre

          // ── Position chronologique (saga_num) ──
          const _myIdx=_allNotes.findIndex(n=>n.aid===_aid)
          saga_num = _myIdx>=0 ? _myIdx+1 : 1

          const _today=new Date().toISOString().slice(0,10)
          const _bf="2 - Domaines/Médias/Animés/À voir"
          // Cherche une note animé existante dans tous les sous-dossiers
          const _findAnime = (sn) => { for(const _sf of ["À voir","En cours","Terminé","Abandonné","En pause"]){const _f=app.vault.getAbstractFileByPath(`2 - Domaines/Médias/Animés/${_sf}/${sn}.md`);if(_f)return _f}; return null }

          let _nbCreated=0,_nbUpdated=0
          for(let _ni=0;_ni<_allNotes.length;_ni++){
            const _n=_allNotes[_ni]
            const _sn=_n.titre.replace(/[/\\:*?"<>|]/g,"")
            const _nPrev=_ni>0?`[[${_allNotes[_ni-1].titre}]]`:""
            const _nNext=_ni<_allNotes.length-1?`[[${_allNotes[_ni+1].titre}]]`:""
            if(_n.aid===_aid){
              if(_ni>0) saison_precedente=_nPrev
              if(_ni<_allNotes.length-1) saison_suivante=_nNext
              continue
            }
            const _existingFile=_findAnime(_sn)
            if(_existingFile){
              // Note existante : mise à jour des liens + saga_num
              try{
                await app.fileManager.processFrontMatter(_existingFile,fm=>{
                  fm.saison_precedente=_nPrev
                  fm.saison_suivante=_nNext
                  fm.saga=saga
                  fm.saga_num=_ni+1
                })
                _nbUpdated++
              }catch(_e){new Notice("❌ MAJ "+_n.titre+": "+_e.message,4000)}
              continue
            }
            // Note inexistante : récupération AniList et création
            let _nC=[],_nB="",_nS="",_nG=[],_nA="",_nR="",_nEp="",_nSyn=""
            try{
              const _qn=`query($id:Int){Media(id:$id,type:ANIME){title{romaji}genres studios{nodes{name isAnimationStudio}}seasonYear episodes description coverImage{extraLarge}bannerImage}}`
              const _rn=await fetch("https://graphql.anilist.co",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:_qn,variables:{id:_n.aid}})})
              const _dn=await _rn.json();const _mn=_dn.data.Media
              _nC=_mn.coverImage?.extraLarge?[_mn.coverImage.extraLarge,_mn.coverImage.extraLarge]:[]
              _nB=_mn.bannerImage||""
              _nS=_mn.studios?.nodes?.find(s=>s.isAnimationStudio)?.name||""
              _nG=_mn.genres||[]
              _nA=_mn.seasonYear?String(_mn.seasonYear):""
              _nR=_mn.title?.romaji||""
              _nEp=_mn.episodes?String(_mn.episodes):""
              _nSyn=await _cleanTranslate(_mn.description||"")
            }catch(_e){}
            const _nCY=_nC.length?'['+_nC.map(c=>`"${c}"`).join(',')+']\n':'[]\n'
            const _nGY=_nG.length?'['+_nG.map(g=>`"${g.replace(/"/g,"'")}"`).join(',')+']':'[]'
            const _nFm=`---\ntype: animé\ncreated: ${_today}\ntitre: "${_n.titre.replace(/"/g,"'")}"\ntitre_original: "${_nR.replace(/"/g,"'")}"\nanilist_id: ${_n.aid}\ncovers: ${_nCY}banniere: "${_nB}"\nstudio: "${_nS.replace(/"/g,"'")}"\ngenre: ${_nGY}\nannée: ${_nA}\nstatut: "à voir"\nnote:\nsaga: "${saga.replace(/"/g,"'")}"\nsaga_num: ${_ni+1}\nsaison_precedente: "${_nPrev}"\nsaison_suivante: "${_nNext}"\nsessions: []\ntags: [animé, média]\nobsidianUIMode: preview\n---`
            const _nBody=_tplBody.replace("# __TITRE__","# "+_n.titre).replace(new RegExp('<'+'% épisodes '+'%'+'>'),_nEp).replace(new RegExp('<'+'% synopsis '+'%'+'>'),_nSyn)
            try{
              await app.vault.adapter.mkdir(_bf)
              await app.vault.create(`${_bf}/${_sn}.md`,_nFm+_nBody)
              _nbCreated++
            }catch(_e){new Notice("❌ "+_n.titre+": "+_e.message,4000)}
          }
          const _parts=[]
          if(_nbCreated>0) _parts.push(`${_nbCreated} créée(s)`)
          if(_nbUpdated>0) _parts.push(`${_nbUpdated} mise(s) à jour`)
          if(_parts.length) new Notice(`✓ Saga : ${_parts.join(", ")}`,3000)
        }
      }
      // ── Saga standalone (sans relations ou refus de création) ──
      if(!saga) saga=titre
      new Notice("✓ AniList : "+titre,2000)
    } catch(_e){ new Notice("❌ AniList : "+_e.message,5000) }
  } else {
    new Notice("ID AniList invalide",3000)
    nbSaisons = parseInt(await tp.system.prompt("Nombre de saisons","1"))||1
    if(!saga) saga=titre
  }
} else {
  nbSaisons = parseInt(await tp.system.prompt("Nombre de saisons","1"))||1
  if(!saga) saga=titre
}

const _coversYaml = covers.length ? '['+covers.map(c=>`"${c}"`).join(',')+']' : '[]'
const _genresYaml = genres.length ? '['+genres.map(g=>`"${g.replace(/"/g,"'")}"`).join(',')+']' : '[]'
const _safeTitre = titre.replace(/[/\\:*?"<>|]/g,"")
await tp.file.move("2 - Domaines/Médias/Animés/" + _an_sub + "/" + _safeTitre)
-%>
---
type: animé
created: <% tp.date.now("YYYY-MM-DD") %>
titre: "<% titre %>"
titre_original: "<% titre_original %>"
anilist_id: <% anilist_id %>
covers: <% _coversYaml %>
banniere: "<% banniere %>"
studio: "<% studio %>"
genre: <% _genresYaml %>
année: <% année %>
statut: "<% statut %>"
note:
saga: "<% saga %>"
saga_num: <% saga_num %>
saison_precedente: "<% saison_precedente %>"
saison_suivante: "<% saison_suivante %>"
sessions: []
tags: [animé, média]
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

const MOVE_MAP = {"en cours":"2 - Domaines/Médias/Animés/En cours","à voir":"2 - Domaines/Médias/Animés/À voir","vu":"2 - Domaines/Médias/Animés/Terminé","abandonné":"2 - Domaines/Médias/Animés/Abandonné","en pause":"2 - Domaines/Médias/Animés/En pause"}
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
const STATUS_COLOR = {"en cours":"#1e66f5","a voir":"#8839ef","vu":"#40a02b","abandonne":"#d20f39","en pause":"#fe640b"}
const STATUS_LIST  = ["en cours","à voir","vu","abandonné","en pause"]
const STATUS_KEY   = {"en cours":"en cours","à voir":"a voir","vu":"vu","abandonné":"abandonne","en pause":"en pause"}
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
  ph.textContent = "🎌"
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

mkRow("Studio",  p.studio || "-",  () => editField("studio", "Studio", p.studio || "", false))
const _g = (v => { if (!v || v === "") return ""; if (typeof v === "string") return v; try { return [...v].filter(Boolean).join(", ") } catch(e) { return "" } })(p.genre)
mkRow("Genre", _g || "-", () => editField("genre", "Genre", _g, false))
mkRow("Saisons", p.saisons != null ? String(p.saisons) : "-", () => editField("saisons", "Saisons", p.saisons, true))

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

// ── Titre VO & Année ──
if (p.titre_original) mkRow("Titre VO", p.titre_original, () => editField("titre_original", "Titre original (VO)", p.titre_original||"", false))
mkRow("Année", p.année != null ? String(p.année) : "-", () => editField("année", "Année", p.année||"", true))
// ── Saga & Navigation saisons ──
if (p.saga || p.saison_precedente || p.saison_suivante) {
  const _ol = lnk => { const _m=String(lnk||"").match(/\[\[([^\]|]+)/); if(_m) app.workspace.openLinkText(_m[1],"") }
  const _sw = infoCol.createDiv(); _sw.style.cssText="background:var(--background-secondary);border-radius:8px;padding:7px 10px;margin-top:2px;"
  if (p.saga) { const _sl=_sw.createEl("div"); _sl.style.cssText="font-size:0.72em;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:5px;"; _sl.textContent="🎯 SAGA : "+p.saga }
  const _nr=_sw.createDiv(); _nr.style.cssText="display:flex;gap:6px;"
  if (p.saison_precedente) { const _b=_nr.createEl("button",{attr:{style:"padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:transparent;cursor:pointer;font-size:0.8em;color:var(--text-muted);font-family:inherit;"}}); _b.textContent="← Précédent"; _b.onclick=()=>_ol(p.saison_precedente) }
  if (p.saison_suivante) { const _b=_nr.createEl("button",{attr:{style:"padding:3px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:transparent;cursor:pointer;font-size:0.8em;color:var(--text-muted);font-family:inherit;"}}); _b.textContent="Suivant →"; _b.onclick=()=>_ol(p.saison_suivante) }
}

const nbSais = p.saisons || 1
const saisonCovers = covers.slice(1)
const nbThumb = Math.max(nbSais, saisonCovers.length)
if (nbThumb > 0) {
  const thumbRow = this.container.createEl("div", {attr:{style:"display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;"}})
  for (let i = 0; i < nbThumb; i++) {
    const src = getSrc(saisonCovers[i])
    const col = thumbRow.createEl("div", {attr:{style:"display:flex;flex-direction:column;align-items:center;gap:4px;"}})
    if (src) {
      col.createEl("img", {attr:{src, style:"width:110px;height:155px;object-fit:cover;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.2);"}})
    } else {
      const phd = col.createEl("div", {attr:{style:"width:110px;height:155px;border-radius:8px;background:var(--background-modifier-border);display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:1.4em;"}})
      phd.textContent = "?"
    }
    col.createEl("span", {attr:{style:"font-size:0.72em;color:var(--text-muted);font-weight:600;"}}).textContent = "Saison " + String(i+1).padStart(2,"0")
  }
}

const editCover = (idx, label, curC) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:300px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 14px;font-size:1em;font-weight:700;"}}).textContent = "🖼 " + label
  const g = box.createEl("div", {attr:{style:"margin-bottom:12px;"}})
  g.createEl("label", {attr:{style:"font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"}}).textContent = "URL ou fichier dans _Système/Attachments/"
  const inp = g.createEl("input", {attr:{type:"text",value:curC[idx]||"",placeholder:"https://... ou nom-du-fichier.jpg",style:"width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;"}})
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;align-items:center;justify-content:flex-end;margin-top:16px;"}})
  if (idx > 0) {
    const del = btns.createEl("button", {attr:{style:"padding:6px 12px;border-radius:7px;border:1px solid #d20f39;color:#d20f39;background:transparent;cursor:pointer;font-size:0.85em;margin-right:auto;"}})
    del.textContent = "🗑 Supprimer"
    del.onclick = async () => {
      overlay.remove(); curC.splice(idx, 1); await save("covers", curC)
      if (idx >= 1 && p.type === "animé" && window.confirm(`Supprimer aussi la section "Saison ${idx}" du corps de la note ?`)) {
        const _rc = await app.vault.read(file)
        const _re = new RegExp(`\\n## Saison ${idx}\\n[\\s\\S]*?(?=\\n## |$)`)
        const _rnc = _rc.replace(_re, '')
        if (_rnc !== _rc) await app.vault.modify(file, _rnc)
      }
      new Notice("Cover supprimée.", 2000)
    }
  }
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);"}})
  cancel.textContent = "Annuler"; cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = async () => {
    const src = inp.value.trim()
    if (!src) return
    if (!src.startsWith("http") && !app.metadataCache.getFirstLinkpathDest(src, "")) { new Notice('"' + src + '" introuvable.', 4000); return }
    const _isNew = idx >= 1 && p.type === "animé" && !curC[idx]
    while (curC.length <= idx) curC.push("")
    curC[idx] = src; await save("covers", curC)
    if (_isNew) {
      const _ac = await app.vault.read(file)
      if (!_ac.includes(`## Saison ${idx}`)) {
        const _ns = `\n## Saison ${idx}\n\n**Épisodes :**\n**Synopsis :**\n`
        const _im = _ac.search(/\n## (?!Saison )/)
        const _anc = _im >= 0 ? _ac.slice(0, _im) + _ns + _ac.slice(_im) : _ac + _ns
        await app.vault.modify(file, _anc)
      }
    }
    overlay.remove(); new Notice("Cover mise à jour !", 2000)
  }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => inp.focus(), 50)
}

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


const showSaisonsModal = () => {
  let _curSaisons = p.saisons || 1
  let _curCovers = Array.isArray(p.covers) ? [...p.covers] : []
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:320px;max-width:480px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);max-height:80vh;overflow-y:auto;"}})
  box.createEl("h3", {attr:{style:"margin:0 0 16px;font-size:1em;font-weight:700;"}}).textContent = "🎬 Saisons"
  const rowsDiv = box.createEl("div")
  const renderRows = () => {
    rowsDiv.empty()
    const nbRows = Math.max(_curSaisons, _curCovers.length > 1 ? _curCovers.length - 1 : 0)
    for (let i = 1; i <= nbRows; i++) {
      const _i = i
      const hasCover = !!(_curCovers[_i] && _curCovers[_i] !== "")
      const row = rowsDiv.createEl("div", {attr:{style:"display:flex;align-items:center;gap:6px;padding:8px 0;border-bottom:1px solid var(--background-modifier-border);"}})
      row.createEl("span", {attr:{style:"flex:1;font-size:0.88em;font-weight:600;color:var(--text-normal);"}}).textContent = "Saison " + _i
      const coverBtn = row.createEl("button", {attr:{style:"padding:4px 10px;border-radius:6px;border:1px solid " + (hasCover ? "var(--interactive-accent)" : "var(--background-modifier-border)") + ";background:var(--background-secondary);cursor:pointer;font-size:0.78em;color:" + (hasCover ? "var(--interactive-accent)" : "var(--text-muted)") + ";font-family:inherit;"}})
      coverBtn.textContent = hasCover ? "📷 ✓" : "📷"
      coverBtn.title = "Modifier la cover"
      coverBtn.onclick = () => { overlay.remove(); editCover(_i, "Cover Saison " + _i, _curCovers) }
      const secBtn = row.createEl("button", {attr:{style:"padding:4px 10px;border-radius:6px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.78em;color:var(--text-muted);font-family:inherit;"}})
      secBtn.textContent = "✏"
      secBtn.title = "Éditer la section"
      secBtn.onclick = () => { overlay.remove(); editBodySection("Saison " + _i, "saison " + _i) }
      const delBtn = row.createEl("button", {attr:{style:"padding:4px 10px;border-radius:6px;border:1px solid rgba(210,15,57,0.35);background:transparent;cursor:pointer;font-size:0.78em;color:#d20f39;font-family:inherit;"}})
      delBtn.textContent = "🗑"
      delBtn.title = "Supprimer"
      delBtn.onclick = async () => {
        if (!window.confirm("Supprimer la Saison " + _i + " ?")) return
        _curSaisons = Math.max(1, _curSaisons - 1)
        if (_curCovers.length > _i) { _curCovers.splice(_i, 1) } else { _curCovers[_i] = "" }
        while (_curCovers.length > 1 && _curCovers[_curCovers.length - 1] === "") _curCovers.pop()
        await app.fileManager.processFrontMatter(file, fm => { fm.saisons = _curSaisons; fm.covers = _curCovers })
        if (window.confirm("Supprimer aussi la section \"Saison " + _i + "\" dans la note ?")) {
          const _rc = await app.vault.read(file)
          const _re = new RegExp("\\n## Saison " + _i + "\\b[\\s\\S]*?(?=\\n## |\\n---\\s*$|$)")
          const _rnc = _rc.replace(_re, "")
          if (_rnc !== _rc) await app.vault.modify(file, _rnc)
        }
        new Notice("Saison " + _i + " supprimée.", 2000)
        renderRows()
      }
    }
    const addRow = rowsDiv.createEl("div", {attr:{style:"padding:12px 0 0;"}})
    const addBtn = addRow.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.84em;color:var(--text-normal);font-family:inherit;width:100%;"}})
    addBtn.textContent = "➕ Ajouter une saison"
    addBtn.onclick = async () => {
      const _newN = _curSaisons + 1
      _curSaisons = _newN
      await app.fileManager.processFrontMatter(file, fm => { fm.saisons = _curSaisons })
      const _ac = await app.vault.read(file)
      if (!_ac.includes("## Saison " + _newN)) {
        const _ns = `\n## Saison ${_newN}\n\n**Épisodes :**\n**Synopsis :**\n`
        const _im = _ac.search(/\n## (?!Saison )/)
        const _anc = _im >= 0 ? _ac.slice(0, _im) + _ns + _ac.slice(_im) : _ac + _ns
        await app.vault.modify(file, _anc)
      }
      new Notice("Saison " + _newN + " ajoutée !", 2000)
      renderRows()
    }
  }
  renderRows()
  const closeBtns = box.createEl("div", {attr:{style:"display:flex;justify-content:flex-end;margin-top:16px;"}})
  const closeBtn = closeBtns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);font-family:inherit;"}})
  closeBtn.textContent = "Fermer"
  closeBtn.onclick = () => overlay.remove()
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Escape") overlay.remove() }
}
const actBar = this.container.createEl("div", {attr:{style:"display:flex;gap:8px;flex-wrap:wrap;padding-top:2px;margin-bottom:12px;"}})
const btnSess = actBar.createEl("button", {attr:{style:BTN}})
btnSess.textContent = "➕ Session"
btnSess.onclick = () => {
  const today = new Date().toISOString().slice(0, 10)
  showForm("Ajouter une session", {
    date:   {label:"Date", value:today, type:"datepicker"},
    saison: {label:"Saison (numéro)", value:"1", type:"number"},
    ep_deb: {label:"Épisode début", value:"", type:"number"},
    ep_fin: {label:"Épisode fin (facultatif)", value:"", type:"number"},
  }, async ({date, saison, ep_deb, ep_fin}) => {
    if (!date || !ep_deb) return
    const sess = {date, saison: parseInt(saison) || 1}
    sess["ep_debut"] = parseInt(ep_deb) || null
    sess["ep_fin"]   = parseInt(ep_fin || ep_deb) || null
    await app.fileManager.processFrontMatter(file, fm => {
      if (!Array.isArray(fm.sessions)) fm.sessions = []
      fm.sessions.push(sess)
    })
    new Notice("Session ajoutée !", 2000)
  })
}
const btnBann = actBar.createEl("button", {attr:{style:BTN}})
btnBann.textContent = "🌅 Bannière"
btnBann.onclick = () => editBanniere()
const btnSais = actBar.createEl("button", {attr:{style:BTN}})
btnSais.textContent = "🎬 Saisons"
btnSais.onclick = () => showSaisonsModal()
const btnMod = actBar.createEl("button", {attr:{style:BTN}})
btnMod.textContent = "✏ Modifier"
btnMod.onclick = e => {
  const menu = new Menu()
  menu.addItem(it => { it.setTitle("✏ Animés similaires"); it.onClick(() => editBodySection("Animés similaires", "similaires")) })
  menu.addItem(it => { it.setTitle("✏ Impressions"); it.onClick(() => editBodySection("Impressions", "impressions")) })
  menu.addItem(it => { it.setTitle("✏ Ce que je retiens"); it.onClick(() => editBodySection("Ce que je retiens", "retiens")) })
  menu.addSeparator()
  menu.addItem(it => { it.setTitle("🌅 Bannière" + (p.banniere ? " ✓" : " (vide)")); it.onClick(() => editBanniere()) })
  menu.addSeparator()
  const curC = Array.isArray(p.covers) ? [...p.covers] : []
  menu.addItem(it => {
    it.setTitle("🖼 Cover principale" + (curC[0] ? " ✓" : " (vide)"))
    it.onClick(() => editCover(0, "Cover principale", curC))
  })
  menu.showAtMouseEvent(e)
}
```

<%* for (let i = 1; i <= nbSaisons; i++) { -%>

## Saison <% i %>
**Épisodes :** <% épisodes %>
**Synopsis :** <% synopsis %>

<%* } -%>
## 🔗 Animés similaires
<!-- Relie les animés similaires avec [[Titre de l'animé]] -->
-

## Impressions

## Ce que je retiens

---

## Historique des sessions

```dataviewjs
const { Notice } = require('obsidian')
const p = dv.current()
if (!p?.file) { const _rr=(_n=0)=>{ if(_n>25)return; setTimeout(()=>{ const _nf=app.vault.getAbstractFileByPath(dv.currentFilePath); (_nf&&app.plugins.plugins['dataview']?.api?.page(dv.currentFilePath)?.file)?app.workspace.activeLeaf?.openFile(_nf):_rr(_n+1); },200); }; _rr(); return; }
const file = app.vault.getAbstractFileByPath(p.file.path)

const showSessionForm = (title, fields, onSubmit) => {
  const overlay = document.body.createEl("div", {attr:{style:"position:fixed;inset:0;background:rgba(0,0,0,0.45);z-index:9998;display:flex;align-items:center;justify-content:center;"}})
  const box = overlay.createEl("div", {attr:{style:"background:var(--background-primary);border-radius:14px;padding:22px 24px;min-width:300px;max-width:420px;width:90%;box-shadow:0 8px 40px rgba(0,0,0,0.35);"}})
  box.createEl("h3", {attr:{style:"margin:0 0 18px;font-size:1em;font-weight:700;"}}).textContent = title
  const inputs = {}
  for (const [key, cfg] of Object.entries(fields)) {
    const g = box.createEl("div", {attr:{style:"margin-bottom:12px;"}})
    g.createEl("label", {attr:{style:"font-size:0.78em;color:var(--text-muted);display:block;margin-bottom:4px;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;"}}).textContent = cfg.label
    if (cfg.type === "datepicker") {
      const _MFR=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],_DFR=["Lu","Ma","Me","Je","Ve","Sa","Di"]
      let _sel=String(cfg.value||"").slice(0,10)
      const _fmt=iso=>{if(!iso)return cfg.placeholder||"Choisir une date";const[y,m,d]=iso.split("-");return`${d}/${m}/${y}`}
      const _wrap=g.createEl("div")
      const _btn=_wrap.createEl("button",{attr:{style:"display:flex;align-items:center;gap:8px;width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.9em;box-sizing:border-box;font-family:inherit;cursor:pointer;text-align:left;"}})
      _btn.createEl("span").textContent="📅"
      const _lbl=_btn.createEl("span",{attr:{style:"flex:1;"}})
      _lbl.style.color=_sel?"var(--text-normal)":"var(--text-muted)"
      _lbl.textContent=_sel?_fmt(_sel):(cfg.placeholder||"Choisir une date")
      let _cal=null
      const _mock={value:_sel}
      _btn.onclick=e=>{
        e.stopPropagation()
        if(_cal){_cal.remove();_cal=null;return}
        const _sd=_sel?new Date(_sel+"T00:00:00"):new Date()
        let _vY=_sd.getFullYear(),_vM=_sd.getMonth()
        _cal=document.body.createEl("div",{attr:{style:"position:fixed;z-index:10000;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.25);padding:14px;width:240px;"}})
        const _rect=_btn.getBoundingClientRect()
        _cal.style.left=Math.min(_rect.left,window.innerWidth-256)+"px"
        if(window.innerHeight-_rect.bottom>270){_cal.style.top=(_rect.bottom+6)+"px"}
        else{_cal.style.top=(_rect.top-6)+"px";_cal.style.transform="translateY(-100%)"}
        const _today=new Date().toISOString().slice(0,10)
        const _render=()=>{
          _cal.empty()
          const _hdr=_cal.createEl("div",{attr:{style:"display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;"}})
          const _pb=_hdr.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
          _pb.textContent="‹";_pb.onclick=e2=>{e2.stopPropagation();_vM--;if(_vM<0){_vM=11;_vY--};_render()}
          _hdr.createEl("span",{attr:{style:"font-weight:700;font-size:0.88em;"}}).textContent=_MFR[_vM]+" "+_vY
          const _nb=_hdr.createEl("button",{attr:{style:"background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1.2em;padding:2px 8px;border-radius:5px;"}})
          _nb.textContent="›";_nb.onclick=e2=>{e2.stopPropagation();_vM++;if(_vM>11){_vM=0;_vY++};_render()}
          const _dh=_cal.createEl("div",{attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:2px;margin-bottom:4px;"}})
          _DFR.forEach(d=>{const c=_dh.createEl("div",{attr:{style:"text-align:center;font-size:0.68em;color:var(--text-muted);font-weight:600;padding:2px 0;"}});c.textContent=d})
          const _dg=_cal.createEl("div",{attr:{style:"display:grid;grid-template-columns:repeat(7,1fr);gap:3px;"}})
          const _fdow=(new Date(_vY,_vM,1).getDay()+6)%7
          const _dim=new Date(_vY,_vM+1,0).getDate()
          for(let i=0;i<_fdow;i++)_dg.createEl("div")
          for(let day=1;day<=_dim;day++){
            const iso=`${_vY}-${String(_vM+1).padStart(2,"0")}-${String(day).padStart(2,"0")}`
            const isS=iso===_sel,isT=iso===_today
            const c=_dg.createEl("div",{attr:{style:"text-align:center;padding:5px 2px;border-radius:6px;cursor:pointer;font-size:0.84em;line-height:1;"+(isS?"background:var(--interactive-accent);color:#fff;font-weight:700;":isT?"border:1.5px solid var(--interactive-accent);color:var(--interactive-accent);font-weight:600;":"")}})
            c.textContent=day
            if(!isS){c.onmouseenter=()=>{c.style.background="var(--background-secondary)"};c.onmouseleave=()=>{c.style.background=""}}
            c.onclick=e2=>{e2.stopPropagation();_sel=iso;_mock.value=iso;_lbl.textContent=_fmt(iso);_lbl.style.color="var(--text-normal)";if(_hdlr)document.removeEventListener("click",_hdlr,true);_cal.remove();_cal=null}
          }
        }
        _render()
        let _hdlr;_hdlr=e2=>{if(_cal&&!_cal.contains(e2.target)&&e2.target!==_btn){_cal.remove();_cal=null;document.removeEventListener("click",_hdlr,true)}}
        setTimeout(()=>document.addEventListener("click",_hdlr,true),10)
      }
      inputs[key]=_mock
    } else {
      const inp = g.createEl("input", {attr:{type:cfg.type||"text",value:String(cfg.value||""),style:"width:100%;padding:7px 10px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);color:var(--text-normal);font-size:0.92em;box-sizing:border-box;font-family:inherit;"}})
      inputs[key] = inp
    }
  }
  const btns = box.createEl("div", {attr:{style:"display:flex;gap:8px;justify-content:flex-end;margin-top:16px;"}})
  const cancel = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:1px solid var(--background-modifier-border);background:var(--background-secondary);cursor:pointer;font-size:0.88em;color:var(--text-normal);font-family:inherit;"}})
  cancel.textContent = "Annuler"; cancel.onclick = () => overlay.remove()
  const ok = btns.createEl("button", {attr:{style:"padding:6px 14px;border-radius:7px;border:none;background:var(--interactive-accent);color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;font-family:inherit;"}})
  ok.textContent = "Enregistrer"
  ok.onclick = () => {
    const vals = {}
    for (const [k,v] of Object.entries(inputs)) vals[k] = v.value.trim()
    overlay.remove(); onSubmit(vals)
  }
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  box.onkeydown = e => { if (e.key === "Enter") ok.click(); if (e.key === "Escape") overlay.remove() }
  setTimeout(() => Object.values(inputs)[0]?.focus(), 50)
}

const ICOBTN = "background:none;border:1px solid var(--background-modifier-border);border-radius:5px;cursor:pointer;font-size:0.78em;padding:2px 6px;color:var(--text-muted);line-height:1;font-family:inherit;"
const TD = "padding:6px 8px;border-bottom:1px solid var(--background-modifier-border);vertical-align:middle;"

let sessions = Array.isArray(p.sessions) ? [...p.sessions] : []
const tableWrap = dv.container.createDiv()

const totalAnime = () => sessions.reduce((t, s) => {
  const de = s["ep_debut"] ?? s["ep_début"] ?? null, a = s["ep_fin"] ?? de
  return t + (de != null && a != null ? a - de + 1 : Number(s.ep) || 0)
}, 0)

const renderAnime = () => {
  tableWrap.empty()
  if (sessions.length === 0) {
    tableWrap.createEl("p", {attr:{style:"color:var(--text-muted);font-style:italic;font-size:0.88em;"}}).textContent = "Aucune session. Utilise le bouton ➕ Session ci-dessus."
    return
  }
  const table = tableWrap.createEl("table", {attr:{style:"width:100%;border-collapse:collapse;font-size:0.87em;"}})
  const hrow = table.createEl("thead").createEl("tr")
  for (const h of ["Date","Saison","Épisodes","Nb",""]) {
    const th = hrow.createEl("th")
    th.style.cssText = "text-align:left;padding:5px 8px;font-size:0.78em;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:var(--text-muted);border-bottom:2px solid var(--background-modifier-border);"
    if (h === "") th.style.width = "70px"
    th.textContent = h
  }
  const tbody = table.createEl("tbody")
  const sorted = sessions.map((s, i) => ({s, i})).slice().sort((a, b) => String(b.s.date||"").slice(0,10).localeCompare(String(a.s.date||"").slice(0,10)))
  for (const {s, i} of sorted) {
    const date = String(s.date || "").slice(0, 10)
    const de = s["ep_debut"] ?? s["ep_début"] ?? null, a = s["ep_fin"] ?? de
    const count = de != null && a != null ? a - de + 1 : (s.ep ?? "?")
    const plage = de == null ? "-" : de === a ? "ep. " + de : "ep. " + de + " → " + a
    const tr = tbody.createEl("tr")
    tr.onmouseenter = () => tr.style.background = "var(--background-secondary)"
    tr.onmouseleave = () => tr.style.background = ""
    tr.createEl("td", {attr:{style:TD}}).textContent = date
    tr.createEl("td", {attr:{style:TD}}).textContent = s.saison != null ? "S" + s.saison : "-"
    tr.createEl("td", {attr:{style:TD}}).textContent = plage
    tr.createEl("td", {attr:{style:TD + "color:var(--text-muted);"}}).textContent = typeof count === "number" ? count + " ep." : count
    const tdA = tr.createEl("td", {attr:{style:TD + "text-align:right;white-space:nowrap;"}})
    const editBtn = tdA.createEl("button", {attr:{style:ICOBTN + "margin-right:4px;"}})
    editBtn.textContent = "✏"; editBtn.title = "Modifier"
    editBtn.onclick = () => showSessionForm("Modifier la session", {
      date:   {label:"Date", value:date, type:"datepicker"},
      saison: {label:"Saison", value:s.saison ?? 1, type:"number"},
      ep_deb: {label:"Épisode début", value:de ?? "", type:"number"},
      ep_fin: {label:"Épisode fin", value:a ?? "", type:"number"},
    }, async ({date:d2, saison:s2, ep_deb, ep_fin}) => {
      if (!d2) return
      sessions[i] = {date:d2, saison:parseInt(s2)||1, ep_debut:parseInt(ep_deb)||null, ep_fin:parseInt(ep_fin||ep_deb)||null}
      await app.fileManager.processFrontMatter(file, fm => { fm.sessions = sessions })
      new Notice("Session modifiée !", 2000); renderAnime()
    })
    const delBtn = tdA.createEl("button", {attr:{style:ICOBTN + "color:#d20f39;border-color:rgba(210,15,57,0.3);"}})
    delBtn.textContent = "🗑"; delBtn.title = "Supprimer"
    delBtn.onclick = async () => {
      if (!window.confirm("Supprimer cette session ?")) return
      sessions = sessions.filter((_, idx) => idx !== i)
      await app.fileManager.processFrontMatter(file, fm => { fm.sessions = sessions })
      new Notice("Session supprimée.", 2000); renderAnime()
    }
  }
  const tot = totalAnime()
  tableWrap.createEl("p", {attr:{style:"font-size:0.82em;color:var(--text-muted);margin-top:6px;"}}).innerHTML = "<strong>" + tot + "</strong> épisode" + (tot > 1 ? "s" : "") + " au total"
}
renderAnime()
```

---
*Ajouté le <% tp.date.now("DD/MM/YYYY") %>*
