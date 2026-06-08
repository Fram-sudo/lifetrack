<%*
const statut = await tp.system.suggester(
  ["🛒 Commandé", "📦 Expédié", "✅ Livré", "❌ Annulé"],
  ["commandé", "expédié", "livré", "annulé"]
);
-%>
---
type: commande
statut: "<% statut %>"
site: 
date_commande: <% tp.date.now("YYYY-MM-DD") %>
date_livraison_estimée: 
date_livraison_réelle: 
montant: 
numéro_commande: 
tags: [commande, suivi]
obsidianUIMode: preview
---

# <% tp.file.title %>

```dataviewjs
const p = dv.current()
if (!p?.file) { const _rr=(_n=0)=>{ if(_n>25)return; setTimeout(()=>{ const _nf=app.vault.getAbstractFileByPath(dv.currentFilePath); (_nf&&app.plugins.plugins['dataview']?.api?.page(dv.currentFilePath)?.file)?app.workspace.activeLeaf?.openFile(_nf):_rr(_n+1); },200); }; _rr(); return; }
const file = app.vault.getAbstractFileByPath(p.file.path)

// ── Helpers ──────────────────────────────────────────────
const getDateStr = val => {
  if (!val) return ""
  if (val && val.toFormat) return val.toFormat("yyyy-MM-dd")
  return String(val).slice(0, 10)
}
const fmtDate = str => {
  if (!str) return "-"
  const [y, m, d] = str.split("-")
  return `${d}/${m}/${y}`
}

// ── Date picker ───────────────────────────────────────────
const mkDatePicker = (parent, initVal, onChange) => {
  const MONTHS = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
  let cur = initVal ? new Date(initVal + "T12:00:00") : new Date()
  cur.setHours(12, 0, 0, 0)
  let selected = initVal || null
  const wrap = parent.createDiv()
  wrap.style.cssText = "position:relative;display:inline-block;"
  const inp = wrap.createEl("input")
  inp.type = "text"; inp.readOnly = true
  inp.value = initVal ? fmtDate(initVal) : ""
  inp.placeholder = "jj/mm/aaaa"
  inp.style.cssText = "width:130px;padding:6px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);cursor:pointer;font-size:0.88em;"
  const pop = wrap.createDiv()
  pop.style.cssText = "display:none;position:absolute;top:calc(100% + 4px);left:0;z-index:9999;background:var(--background-primary);border:1px solid var(--background-modifier-border);border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,0.15);padding:12px;width:240px;"
  const buildCal = () => {
    pop.empty()
    const hdr = pop.createDiv()
    hdr.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"
    const prev = hdr.createEl("button"); prev.textContent = "‹"
    prev.style.cssText = "background:none;border:none;cursor:pointer;font-size:1.3em;color:var(--text-muted);padding:0 6px;"
    const lbl = hdr.createDiv()
    lbl.style.cssText = "font-weight:600;font-size:0.88em;color:var(--text-normal);"
    lbl.textContent = `${MONTHS[cur.getMonth()]} ${cur.getFullYear()}`
    const next = hdr.createEl("button"); next.textContent = "›"
    next.style.cssText = "background:none;border:none;cursor:pointer;font-size:1.3em;color:var(--text-muted);padding:0 6px;"
    prev.onclick = e => { e.stopPropagation(); cur = new Date(cur.getFullYear(), cur.getMonth() - 1, 1, 12); buildCal() }
    next.onclick = e => { e.stopPropagation(); cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1, 12); buildCal() }
    const grid = pop.createDiv()
    grid.style.cssText = "display:grid;grid-template-columns:repeat(7,1fr);gap:2px;text-align:center;"
    for (const d of ["L","M","M","J","V","S","D"]) {
      const h = grid.createDiv(); h.textContent = d
      h.style.cssText = "font-size:0.7em;color:var(--text-muted);font-weight:600;padding:2px 0;"
    }
    const y = cur.getFullYear(), mo = cur.getMonth()
    const first = new Date(y, mo, 1).getDay()
    const offset = (first === 0 ? 6 : first - 1)
    const days = new Date(y, mo + 1, 0).getDate()
    for (let i = 0; i < offset; i++) grid.createDiv()
    for (let d = 1; d <= days; d++) {
      const dateStr = `${y}-${String(mo + 1).padStart(2,"0")}-${String(d).padStart(2,"0")}`
      const cell = grid.createEl("button"); cell.textContent = d
      const isSel = dateStr === selected
      cell.style.cssText = `background:${isSel ? "#8839ef" : "none"};color:${isSel ? "#fff" : "var(--text-normal)"};border:none;border-radius:4px;cursor:pointer;font-size:0.82em;padding:4px 2px;`
      cell.onclick = e => {
        e.stopPropagation(); selected = dateStr
        inp.value = fmtDate(dateStr); pop.style.display = "none"
        if (onChange) onChange(dateStr); buildCal()
      }
    }
  }
  inp.onclick = e => {
    e.stopPropagation()
    const isOpen = pop.style.display !== "none"
    pop.style.display = isOpen ? "none" : "block"
    if (!isOpen) buildCal()
  }
  document.addEventListener("click", () => { pop.style.display = "none" })
  return { getValue: () => selected, setValue: v => { selected = v; inp.value = v ? fmtDate(v) : "" } }
}

// ── Couleurs statut ───────────────────────────────────────
const CMD_COLORS = {
  "commandé": { bg: "rgba(30,102,245,0.12)",  color: "#1e66f5" },
  "expédié":  { bg: "rgba(223,142,29,0.15)",  color: "#df8e1d" },
  "livré":    { bg: "rgba(64,160,43,0.12)",   color: "#40a02b" },
  "annulé":   { bg: "rgba(210,15,57,0.10)",   color: "#d20f39" },
}
const FIELD = "padding:6px 10px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-primary);color:var(--text-normal);font-size:0.88em;width:100%;box-sizing:border-box;"
const LABEL = "display:block;font-size:0.78em;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;"
const BTN_S = "padding:8px 18px;border:none;border-radius:6px;background:#8839ef;color:#fff;cursor:pointer;font-size:0.88em;font-weight:600;"
const BTN_G = "padding:8px 18px;border:1px solid var(--background-modifier-border);border-radius:6px;background:var(--background-secondary);color:var(--text-muted);cursor:pointer;font-size:0.88em;"

// ── Action bar ────────────────────────────────────────────
const bar = dv.container.createDiv()
bar.style.cssText = "display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 14px;background:var(--background-secondary);border:1px solid var(--background-modifier-border);border-radius:10px;margin:12px 0 18px;"
const statut = p.statut || "commandé"
const sCol = CMD_COLORS[statut] || CMD_COLORS["commandé"]
const badge = bar.createDiv()
badge.textContent = statut.charAt(0).toUpperCase() + statut.slice(1)
badge.style.cssText = `padding:4px 12px;border-radius:12px;font-size:0.82em;font-weight:700;background:${sCol.bg};color:${sCol.color};`
const sep = () => { const s = bar.createDiv(); s.style.cssText = "width:1px;height:18px;background:var(--background-modifier-border);margin:0 2px;"; return s }
sep()
const chip = (icon, val) => {
  const c = bar.createDiv()
  c.style.cssText = "display:flex;align-items:center;gap:4px;font-size:0.82em;color:var(--text-muted);"
  c.createSpan().textContent = icon
  const v = c.createSpan(); v.textContent = val || "-"
  v.style.cssText = "color:var(--text-normal);font-weight:500;"
}
chip("🏪", p.site); sep()
chip("📅", fmtDate(getDateStr(p.date_commande))); sep()
chip("📦", fmtDate(getDateStr(p["date_livraison_estimée"]))); sep()
chip("💶", p.montant ? p.montant + " €" : "-")
const spacer = bar.createDiv(); spacer.style.cssText = "flex:1;"
const editBtn = bar.createEl("button")
editBtn.textContent = "✏ Modifier"; editBtn.style.cssText = BTN_S

// ── Modal édition ─────────────────────────────────────────
const openEditModal = () => {
  const overlay = document.body.createDiv()
  overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:10000;display:flex;align-items:center;justify-content:center;"
  overlay.onclick = e => { if (e.target === overlay) overlay.remove() }
  const modal = overlay.createDiv()
  modal.style.cssText = "background:var(--background-primary);border-radius:14px;padding:28px 28px 22px;width:480px;max-width:95vw;max-height:90vh;overflow-y:auto;display:flex;flex-direction:column;gap:16px;"
  modal.onclick = e => e.stopPropagation()
  const ttl = modal.createEl("h3")
  ttl.textContent = "Modifier la commande"
  ttl.style.cssText = "margin:0 0 4px;font-size:1em;color:var(--text-normal);"
  const row2 = (a, b) => { const r = modal.createDiv(); r.style.cssText = "display:grid;grid-template-columns:1fr 1fr;gap:12px;"; r.append(a, b); return r }
  const field = (label, inp) => {
    const g = document.createElement("div")
    const l = document.createElement("label"); l.textContent = label; l.style.cssText = LABEL
    g.append(l, inp); return g
  }
  // Nom fichier
  const nomInp = document.createElement("input")
  nomInp.type = "text"; nomInp.value = p.file.name; nomInp.style.cssText = FIELD
  modal.append(field("Nom du fichier", nomInp))
  // Site + Statut
  const siteInp = document.createElement("input")
  siteInp.type = "text"; siteInp.value = p.site || ""; siteInp.style.cssText = FIELD
  const statutSel = document.createElement("select"); statutSel.style.cssText = FIELD
  for (const [val, lbl] of [["commandé","🛒 Commandé"],["expédié","📦 Expédié"],["livré","✅ Livré"],["annulé","❌ Annulé"]]) {
    const opt = document.createElement("option"); opt.value = val; opt.textContent = lbl
    if (val === (p.statut || "commandé")) opt.selected = true
    statutSel.append(opt)
  }
  modal.append(row2(field("Site", siteInp), field("Statut", statutSel)))
  // Dates
  const dCmdG = document.createElement("div")
  const dCmdL = document.createElement("label"); dCmdL.textContent = "Date de commande"; dCmdL.style.cssText = LABEL
  dCmdG.append(dCmdL)
  const cmdPicker = mkDatePicker(dCmdG, getDateStr(p.date_commande), null)
  const dLivG = document.createElement("div")
  const dLivL = document.createElement("label"); dLivL.textContent = "Livraison estimée"; dLivL.style.cssText = LABEL
  dLivG.append(dLivL)
  const livPicker = mkDatePicker(dLivG, getDateStr(p["date_livraison_estimée"]), null)
  modal.append(row2(dCmdG, dLivG))
  // Numéro + Montant
  const numInp = document.createElement("input")
  numInp.type = "text"; numInp.value = p["numéro_commande"] || ""; numInp.style.cssText = FIELD
  const montantInp = document.createElement("input")
  montantInp.type = "number"; montantInp.step = "0.01"; montantInp.value = p.montant || ""; montantInp.style.cssText = FIELD
  modal.append(row2(field("N° de commande", numInp), field("Montant (€)", montantInp)))
  // Boutons
  const bRow = modal.createDiv()
  bRow.style.cssText = "display:flex;gap:10px;justify-content:flex-end;margin-top:4px;"
  const cancelBtn = bRow.createEl("button"); cancelBtn.textContent = "Annuler"; cancelBtn.style.cssText = BTN_G
  cancelBtn.onclick = () => overlay.remove()
  const saveBtn = bRow.createEl("button"); saveBtn.textContent = "💾 Enregistrer"; saveBtn.style.cssText = BTN_S
  saveBtn.onclick = async () => {
    const newName = nomInp.value.trim()
    await app.fileManager.processFrontMatter(file, f => {
      f.site = siteInp.value.trim()
      f.statut = statutSel.value
      f.date_commande = cmdPicker.getValue() || getDateStr(p.date_commande)
      f["date_livraison_estimée"] = livPicker.getValue() || getDateStr(p["date_livraison_estimée"])
      f["numéro_commande"] = numInp.value.trim()
      f.montant = montantInp.value ? parseFloat(montantInp.value) : p.montant
    })
    if (newName && newName !== p.file.name) {
      const newPath = p.file.path.replace(p.file.name, newName)
      await app.fileManager.renameFile(file, newPath)
    }
    overlay.remove()
    new Notice("Commande mise à jour ✓")
  }
  document.body.append(overlay)
}

editBtn.onclick = () => openEditModal()
```

## 📦 Détails

| Champ | Valeur |
|-------|--------|
| Site | `=this.site` |
| N° commande | `=this.numéro_commande` |
| Statut | `=this.statut` |
| Commandé le | `=this.date_commande` |
| Livraison estimée | `=this.date_livraison_estimée` |
| Montant | `=this.montant` € |

## 🛒 Articles commandés
| Article | Qté | Prix unitaire |
|---------|-----|---------------|
|  | 1 |  |

## 📍 Suivi
<!-- Coller le numéro de suivi et l'URL de tracking -->
- Numéro de suivi : 
- URL tracking : 

## 📝 Notes
<!-- Raison de l'achat, contexte, remarques à la livraison -->


## 🔄 Historique
- <% tp.date.now("YYYY-MM-DD") %> - Commande passée
- 

---
*Statut actuel : `=this.statut`*
