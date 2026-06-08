<%*
// ── Script de démarrage - s'exécute une fois à l'ouverture d'Obsidian ──
// Bascule automatiquement en mode Lecture les notes du dossier 2 - Domaines/

const _forcePreview = leaf => {
  if (!leaf) return
  const view = leaf.view
  if (!view || view.getViewType() !== 'markdown') return
  const file = view.file
  if (!file || !file.path.startsWith('2 - Domaines/')) return
  setTimeout(() => {
    const state = leaf.getViewState()
    if (state.state?.mode === 'preview') return
    leaf.setViewState({...state, state: {...state.state, mode: 'preview'}})
  }, 50)
}

if (!window._domainesPreviewInit) {
  window._domainesPreviewInit = true

  // Cas 1 : changement d'onglet actif
  app.workspace.on('active-leaf-change', leaf => _forcePreview(leaf))

  // Cas 2 : fichier renommé/déplacé (ex : changement de statut via IIFE)
  app.vault.on('rename', (file, oldPath) => {
    if (!file.path.startsWith('2 - Domaines/')) return
    setTimeout(() => {
      const leaf = app.workspace.getActiveViewOfType(require('obsidian').MarkdownView)?.leaf
      _forcePreview(leaf)
    }, 100)
  })
}

// ── Bouton scroll-to-top flottant ──────────────────────────────────────────
if (!window._sttInit) {
  window._sttInit = true

  // Création du bouton
  const btn = document.createElement('button')
  btn.id = '__stt_global__'
  btn.textContent = '↑'
  btn.style.cssText = [
    'position:fixed', 'bottom:28px', 'right:28px',
    'width:44px', 'height:44px', 'border-radius:50%',
    'background:rgba(0,0,0,0.55)',
    'backdrop-filter:blur(6px)', '-webkit-backdrop-filter:blur(6px)',
    'color:#fff', 'border:none', 'font-size:20px', 'font-weight:bold',
    'line-height:1', 'cursor:pointer',
    'opacity:0', 'pointer-events:none',
    'transition:opacity 0.25s ease, transform 0.15s ease, box-shadow 0.15s ease',
    'z-index:9999',
    'box-shadow:0 2px 8px rgba(0,0,0,0.35)'
  ].join(';')

  btn.addEventListener('mouseenter', () => {
    btn.style.transform = 'translateY(-2px)'
    btn.style.boxShadow = '0 6px 18px rgba(0,0,0,0.5)'
  })
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = ''
    btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.35)'
  })
  document.body.appendChild(btn)

  let _sttScrollEl = null
  let _sttHandler = null

  const _sttAttach = () => {
    // Détacher l'ancien listener
    if (_sttScrollEl && _sttHandler) {
      _sttScrollEl.removeEventListener('scroll', _sttHandler)
    }
    btn.style.opacity = '0'
    btn.style.pointerEvents = 'none'
    _sttScrollEl = null
    _sttHandler = null

    // Trouver le conteneur de scroll de la leaf active
    const leaf = app.workspace.getMostRecentLeaf()
    const container = leaf?.view?.containerEl
    if (!container) return

    const el = container.querySelector('.markdown-preview-view')
      || container.querySelector('.view-content')
    if (!el) return

    _sttScrollEl = el
    _sttHandler = () => {
      const show = (_sttScrollEl.scrollTop || 0) > 150
      btn.style.opacity = show ? '1' : '0'
      btn.style.pointerEvents = show ? 'auto' : 'none'
    }
    _sttScrollEl.addEventListener('scroll', _sttHandler, { passive: true })
    _sttHandler() // vérification initiale
  }

  btn.addEventListener('click', () => {
    _sttScrollEl?.scrollTo({ top: 0, behavior: 'smooth' })
  })

  app.workspace.on('active-leaf-change', _sttAttach)
  // Attendre que le workspace soit prêt
  setTimeout(_sttAttach, 300)
}
%>
