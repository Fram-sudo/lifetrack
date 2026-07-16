#!/usr/bin/env python3
"""
create_fiches_medias.py
Crée des fiches médias Obsidian (animés, films, séries) en masse à partir des
APIs AniList et TMDB, à partir d'identifiants que tu renseignes ci-dessous.

Usage :
    1. Renseigne ta clé TMDB dans _Système/Config.md (tmdb_api_key).
    2. Remplis les listes ANIMÉS_VU / ANIMÉS_EN_COURS / FILMS_À_VOIR / SÉRIES_À_VOIR
       ci-dessous avec tes propres identifiants AniList / TMDB.
    3. Lance : python3 create_fiches_medias.py

Prérequis :
    Python 3.8+, accès internet, aucune dépendance externe.

Ce script lit les templates depuis _Système/Templates/ et crée les notes
dans les sous-dossiers corrects de 2 - Domaines/Médias/.

Note : pour créer des fiches une par une, utilise plutôt les templates
TPL - Film / Série / Animé via QuickAdd (auto-remplissage TMDB/AniList) -
ce script sert à l'import en masse.
"""

import json, os, re, sys, time, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
VAULT       = SCRIPT_DIR.parent.parent   # _Système/Scripts/ → vault root
TODAY_ISO   = datetime.today().strftime("%Y-%m-%d")
TODAY_FR    = datetime.today().strftime("%d/%m/%Y")

def load_tmdb_key():
    """Lit la clé TMDB depuis _Système/Config.md (frontmatter tmdb_api_key)."""
    cfg_path = VAULT / "_Système" / "Config.md"
    if not cfg_path.exists():
        return ""
    text = cfg_path.read_text(encoding="utf-8")
    m = re.search(r'^tmdb_api_key:\s*["\']?([^"\'\n]*)["\']?\s*$', text, re.MULTILINE)
    return m.group(1).strip() if m else ""

TMDB_KEY = load_tmdb_key()

# ── Médias à créer ────────────────────────────────────────────────────
# Renseigne ici tes propres identifiants (AniList pour les animés, TMDB pour
# films/séries). Laisse les listes vides si tu préfères créer tes fiches une
# par une avec les templates QuickAdd.
ANIMÉS_VU = [
    # 180523, 187901, ...
]
ANIMÉS_EN_COURS = [
    # 146850, 151970, ...
]
FILMS_À_VOIR = [
    # 557, 558, 559, ...
]
SÉRIES_À_VOIR = [
    # 96677, 94997, ...
]

# ── Helpers HTTP ──────────────────────────────────────────────────────
def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def http_post(url, payload, timeout=20):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

# ── Nettoyage HTML + traduction FR ────────────────────────────────────
def clean_html(text):
    if not text: return ""
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'~![\s\S]*?!~', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def translate_fr(text):
    cleaned = clean_html(text)
    if not cleaned: return ""
    try:
        url = ("https://translate.googleapis.com/translate_a/single"
               "?client=gtx&sl=auto&tl=fr&dt=t&q=" + urllib.parse.quote(cleaned))
        result = http_get(url)
        return "".join(seg[0] for seg in result[0] if seg and seg[0])
    except Exception as e:
        print(f"    [translate] erreur : {e}")
        return cleaned

# ── YAML helpers ──────────────────────────────────────────────────────
def yq(s):
    return str(s).replace('"', "'") if s else ""

def covers_yaml(lst):
    if not lst: return "[]"
    return "[" + ",".join(f'"{c}"' for c in lst if c) + "]"

def genres_yaml(lst):
    if not lst: return "[]"
    return "[" + ",".join(f'"{g.replace(chr(34), chr(39))}"' for g in lst) + "]"

def safe_name(s):
    return re.sub(r'[/\\:*?"<>|]', '', s).strip()

# ── Lecture des templates ─────────────────────────────────────────────
def read_template_body(tpl_name):
    path = VAULT / "_Système" / "Templates" / tpl_name
    content = path.read_text(encoding="utf-8")
    idx = content.find("-%>")
    return content[idx + 3:] if idx != -1 else content

def expand_for_loop(body, seasons_data):
    """Remplace le bloc <%* for ... { -%> ... <%* } -%> par les sections expansées."""
    pattern = r'<%\*\s*for\s*\(let i = 1; i <= nbSaisons; i\+\+\)\s*\{.*?-%>\n([\s\S]*?)<%\*\s*\}.*?-%>\n'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return body
    inner = match.group(1)
    expanded = ""
    for i in sorted(seasons_data.keys()):
        chunk = inner
        chunk = chunk.replace("<% i %>", str(i))
        chunk = chunk.replace("<% épisodes %>", yq(seasons_data[i].get("episodes", "")))
        chunk = chunk.replace("<% synopsis %>", yq(seasons_data[i].get("synopsis", "")))
        expanded += chunk
    return body[:match.start()] + expanded + body[match.end():]

def apply_vars(body, replacements):
    for k, v in replacements.items():
        body = body.replace(k, str(v))
    return body

# ── Création des notes ────────────────────────────────────────────────
ANIME_SUBFOLDERS = {
    "vu": "Terminé", "à voir": "À voir", "en cours": "En cours",
    "abandonné": "Abandonné", "en pause": "En pause",
}
FILM_SUBFOLDERS = {
    "à voir": "À voir", "en cours": "En cours",
    "vu": "Vu", "abandonné": "Abandonné",
}

def create_anime_note(aid, statut, body_tpl):
    print(f"\n  [Animé {aid}] fetch AniList…")
    q = """query($id:Int){Media(id:$id,type:ANIME){
        id title{romaji english native}
        genres studios{nodes{name isAnimationStudio}}
        seasonYear episodes description
        coverImage{extraLarge} bannerImage
    }}"""
    try:
        data = http_post("https://graphql.anilist.co", {"query": q, "variables": {"id": aid}})
        med = data["data"]["Media"]
    except Exception as e:
        print(f"    ERREUR AniList : {e}")
        return False

    titre = med["title"].get("english") or med["title"].get("romaji") or f"Anime_{aid}"
    titre_original = med["title"].get("romaji", "")
    genres = med.get("genres", [])
    studio = next((n["name"] for n in (med.get("studios", {}).get("nodes") or [])
                   if n.get("isAnimationStudio")), "")
    cover_url = (med.get("coverImage") or {}).get("extraLarge", "")
    covers = [cover_url, cover_url] if cover_url else []
    banniere = med.get("bannerImage", "") or ""
    annee = str(med["seasonYear"]) if med.get("seasonYear") else ""
    episodes_str = str(med["episodes"]) if med.get("episodes") else ""

    print(f"    {titre} | {episodes_str} éps | traduction synopsis…")
    synopsis = translate_fr(med.get("description", ""))
    time.sleep(0.4)

    subfolder = ANIME_SUBFOLDERS.get(statut, "À voir")
    folder = VAULT / "2 - Domaines" / "Médias" / "Animés" / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    filename = safe_name(titre)
    filepath = folder / f"{filename}.md"
    if filepath.exists():
        print(f"    DÉJÀ EXISTANT, ignoré.")
        return True

    seasons_data = {1: {"episodes": episodes_str, "synopsis": synopsis}}
    body = expand_for_loop(body_tpl, seasons_data)
    body = apply_vars(body, {
        '<% tp.date.now("YYYY-MM-DD") %>': TODAY_ISO,
        '<% tp.date.now("DD/MM/YYYY") %>': TODAY_FR,
        '<% tp.file.title %>': titre,
        '<% titre %>': yq(titre),
        '<% titre_original %>': yq(titre_original),
        '<% anilist_id %>': str(aid),
        '<% _coversYaml %>': covers_yaml(covers),
        '<% banniere %>': yq(banniere),
        '<% studio %>': yq(studio),
        '<% _genresYaml %>': genres_yaml(genres),
        '<% année %>': annee,
        '<% statut %>': statut,
        '<% saga %>': "",
        '<% saison_precedente %>': "",
        '<% saison_suivante %>': "",
    })

    filepath.write_text(body, encoding="utf-8")
    print(f"    ✓  {filename}.md  ({subfolder})")
    return True


def create_film_note(tmdb_id, statut, body_tpl):
    print(f"\n  [Film {tmdb_id}] fetch TMDB…")
    try:
        url = (f"https://api.themoviedb.org/3/movie/{tmdb_id}"
               f"?api_key={TMDB_KEY}&language=fr-FR&append_to_response=credits")
        mov = http_get(url)
    except Exception as e:
        print(f"    ERREUR TMDB : {e}")
        return False

    titre = mov.get("title") or mov.get("original_title") or f"Film_{tmdb_id}"
    titre_original = mov.get("original_title", "")
    genres = [g["name"] for g in mov.get("genres", [])]
    director = next((c["name"] for c in ((mov.get("credits") or {}).get("crew") or [])
                     if c.get("job") == "Director"), "")
    poster = mov.get("poster_path", "")
    cover_url = f"https://image.tmdb.org/t/p/original{poster}" if poster else ""
    covers = [cover_url] if cover_url else []
    backdrop = mov.get("backdrop_path", "")
    banniere = f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else ""
    annee = mov.get("release_date", "")[:4] if mov.get("release_date") else ""
    synopsis = mov.get("overview", "") or ""
    saga = (mov.get("belongs_to_collection") or {}).get("name", "") or ""

    print(f"    {titre} ({annee}) | réal. {director}")

    subfolder = FILM_SUBFOLDERS.get(statut, "À voir")
    folder = VAULT / "2 - Domaines" / "Médias" / "Films" / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    filename = safe_name(titre)
    filepath = folder / f"{filename}.md"
    if filepath.exists():
        print(f"    DÉJÀ EXISTANT, ignoré.")
        return True

    body = apply_vars(body_tpl, {
        '<% tp.date.now("YYYY-MM-DD") %>': TODAY_ISO,
        '<% tp.date.now("DD/MM/YYYY") %>': TODAY_FR,
        '<% tp.file.title %>': titre,
        '<% titre %>': yq(titre),
        '<% titre_original %>': yq(titre_original),
        '<% tmdb_id %>': str(tmdb_id),
        '<% _coversYaml %>': covers_yaml(covers),
        '<% banniere %>': yq(banniere),
        '<% réalisateur %>': yq(director),
        '<% _genresYaml %>': genres_yaml(genres),
        '<% année %>': annee,
        '<% statut %>': statut,
        '<% saga %>': yq(saga),
        '<% synopsis %>': yq(synopsis),
    })

    filepath.write_text(body, encoding="utf-8")
    print(f"    ✓  {filename}.md  ({subfolder})")
    return True


def create_serie_note(tmdb_id, statut, body_tpl):
    print(f"\n  [Série {tmdb_id}] fetch TMDB…")
    try:
        url = (f"https://api.themoviedb.org/3/tv/{tmdb_id}"
               f"?api_key={TMDB_KEY}&language=fr-FR")
        tv = http_get(url)
    except Exception as e:
        print(f"    ERREUR TMDB : {e}")
        return False

    titre = tv.get("name") or tv.get("original_name") or f"Serie_{tmdb_id}"
    titre_original = tv.get("original_name", "")
    genres = [g["name"] for g in tv.get("genres", [])]
    poster = tv.get("poster_path", "")
    cover_url = f"https://image.tmdb.org/t/p/original{poster}" if poster else ""
    backdrop = tv.get("backdrop_path", "")
    banniere = f"https://image.tmdb.org/t/p/original{backdrop}" if backdrop else ""
    annee = tv.get("first_air_date", "")[:4] if tv.get("first_air_date") else ""
    nb_saisons = tv.get("number_of_seasons", 1)
    plateforme = ", ".join(n["name"] for n in (tv.get("networks") or []))

    covers = [cover_url] if cover_url else [""]
    scovers = sorted([s for s in (tv.get("seasons") or [])
                      if s.get("season_number", 0) > 0 and s.get("poster_path")],
                     key=lambda s: s["season_number"])
    if scovers:
        max_s = scovers[-1]["season_number"]
        while len(covers) <= max_s:
            covers.append("")
        for s in scovers:
            covers[s["season_number"]] = f"https://image.tmdb.org/t/p/original{s['poster_path']}"

    seasons_data = {}
    for s in (tv.get("seasons") or []):
        sn = s.get("season_number", 0)
        if sn > 0:
            seasons_data[sn] = {
                "episodes": str(s["episode_count"]) if s.get("episode_count") is not None else "",
                "synopsis": s.get("overview", "") or "",
            }

    print(f"    {titre} | {nb_saisons} saison(s) | {plateforme}")

    subfolder = ANIME_SUBFOLDERS.get(statut, "À voir")
    folder = VAULT / "2 - Domaines" / "Médias" / "Séries" / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    filename = safe_name(titre)
    filepath = folder / f"{filename}.md"
    if filepath.exists():
        print(f"    DÉJÀ EXISTANT, ignoré.")
        return True

    body = expand_for_loop(body_tpl, seasons_data or {1: {"episodes": "", "synopsis": ""}})
    body = apply_vars(body, {
        '<% tp.date.now("YYYY-MM-DD") %>': TODAY_ISO,
        '<% tp.date.now("DD/MM/YYYY") %>': TODAY_FR,
        '<% tp.file.title %>': titre,
        '<% titre %>': yq(titre),
        '<% titre_original %>': yq(titre_original),
        '<% tmdb_id %>': str(tmdb_id),
        '<% _coversYaml %>': covers_yaml(covers),
        '<% banniere %>': yq(banniere),
        '<% _genresYaml %>': genres_yaml(genres),
        '<% année %>': annee,
        '<% nbSaisons %>': str(nb_saisons),
        '<% statut %>': statut,
        '<% saga %>': "",
        '<% saison_precedente %>': "",
        '<% saison_suivante %>': "",
        '<% plateforme %>': yq(plateforme),
    })

    filepath.write_text(body, encoding="utf-8")
    print(f"    ✓  {filename}.md  ({subfolder})")
    return True


# ── Main ──────────────────────────────────────────────────────────────
def main():
    print(f"Vault : {VAULT}")
    print(f"Date  : {TODAY_ISO}\n")

    if not TMDB_KEY and (FILMS_À_VOIR or SÉRIES_À_VOIR):
        print("⚠ Clé TMDB manquante - renseigne tmdb_api_key dans _Système/Config.md\n")

    if not (ANIMÉS_VU or ANIMÉS_EN_COURS or FILMS_À_VOIR or SÉRIES_À_VOIR):
        print("Aucun identifiant renseigné dans les listes ANIMÉS_VU / ANIMÉS_EN_COURS /")
        print("FILMS_À_VOIR / SÉRIES_À_VOIR en haut du script. Rien à faire.")
        return

    print("Chargement des templates…")
    tpl_anime = read_template_body("TPL - Animé.md")
    tpl_film  = read_template_body("TPL - Film.md")
    tpl_serie = read_template_body("TPL - Série.md")
    print("  ✓ Templates chargés\n")

    ok = err = 0

    if ANIMÉS_VU:
        print("=" * 55)
        print(f"ANIMÉS - VU ({len(ANIMÉS_VU)})")
        print("=" * 55)
        for aid in ANIMÉS_VU:
            if create_anime_note(aid, "vu", tpl_anime): ok += 1
            else: err += 1
            time.sleep(0.5)

    if ANIMÉS_EN_COURS:
        print("\n" + "=" * 55)
        print(f"ANIMÉS - EN COURS ({len(ANIMÉS_EN_COURS)})")
        print("=" * 55)
        for aid in ANIMÉS_EN_COURS:
            if create_anime_note(aid, "en cours", tpl_anime): ok += 1
            else: err += 1
            time.sleep(0.5)

    if FILMS_À_VOIR:
        print("\n" + "=" * 55)
        print(f"FILMS - À VOIR ({len(FILMS_À_VOIR)})")
        print("=" * 55)
        for fid in FILMS_À_VOIR:
            if create_film_note(fid, "à voir", tpl_film): ok += 1
            else: err += 1
            time.sleep(0.3)

    if SÉRIES_À_VOIR:
        print("\n" + "=" * 55)
        print(f"SÉRIES - À VOIR ({len(SÉRIES_À_VOIR)})")
        print("=" * 55)
        for sid in SÉRIES_À_VOIR:
            if create_serie_note(sid, "à voir", tpl_serie): ok += 1
            else: err += 1
            time.sleep(0.3)

    print(f"\n{'=' * 55}")
    print(f"Résultat : {ok} créées, {err} erreur(s)")
    print("Recharge Obsidian (Ctrl+R) pour voir les nouvelles fiches.")

if __name__ == "__main__":
    main()
