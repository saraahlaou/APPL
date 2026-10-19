"""Page Offres : catalogue filtrable, détail d'une offre et offre personnalisée."""

from __future__ import annotations

import json

import streamlit as st

from .. import llm, storage, ui
from ..data_jobs import JOBS, empty_custom_job, get_job, job_search_text
from ..data_skills import CEFR_LEVELS, EDUCATION_LEVELS, SKILL_NAMES, TARGET_DOMAINS
from ..matching import analyze, detect_education, detect_languages, extract_skills
from .common import get_target_job, job_label, nav_to, require_profile, set_target_job


@st.cache_data(show_spinner=False)
def _quick_score(profile_json: str, job_id: str) -> int:
    job = get_job(job_id)
    if not job:
        return 0
    result = analyze(json.loads(profile_json), job, with_plan=False)
    return result["score"]


def _is_target(job: dict) -> bool:
    target = storage.get_profile().get("target", {})
    if target.get("type") == "custom":
        return bool(job.get("is_custom"))
    return target.get("job_id") == job.get("id") and not job.get("is_custom")


def _go_analyze(job: dict, custom: bool = False) -> None:
    st.session_state.selected_job_id = job.get("id", "")
    st.session_state.custom_job = job if custom else None
    st.session_state.auto_analyze = True
    nav_to("analysis")


# --------------------------------------------------------------------------- #
# Détail d'une offre du catalogue
# --------------------------------------------------------------------------- #

def _render_job_detail(job: dict, profile: dict, custom: bool = False) -> None:
    if st.button("← Retour aux offres", key="job_back"):
        st.session_state.job_view_id = None
        st.rerun()

    profile_json = json.dumps(profile, ensure_ascii=False, sort_keys=True, default=str)
    score = None if custom else _quick_score(profile_json, job["id"])
    st.markdown(ui.job_header(job, score), unsafe_allow_html=True)

    left, right = st.columns([1.4, 1], gap="large")
    with left:
        if job.get("description"):
            ui.section_header("Le poste", "Description")
            st.markdown(
                f'<div class="tm-card-sub" style="line-height:1.7">{ui.esc(job["description"])}</div>',
                unsafe_allow_html=True,
            )
        if job.get("missions"):
            ui.section_header("Au quotidien", "Tes missions")
            items = "".join(f"<li>{ui.esc(m)}</li>" for m in job["missions"])
            st.markdown(
                f'<ul style="line-height:1.75;color:#2E3A35;padding-left:1.1rem">{items}</ul>',
                unsafe_allow_html=True,
            )
        if job.get("is_custom") and job.get("raw_text"):
            with st.expander("Texte original de l'offre"):
                st.text(job["raw_text"][:4000])

    with right:
        st.markdown('<div class="tm-eyebrow">Exigences</div>', unsafe_allow_html=True)
        rows = []
        for req in job.get("required_skills", []):
            nature = {"indispensable": "green", "important": "amber", "atout": "blue"}.get(req.get("nature", "important"), "")
            rows.append(
                f"""<div style="display:flex;justify-content:space-between;align-items:center;
                border-bottom:1px solid #EFECE2;padding:.45rem 0">
                  <div><strong style="color:#10231F">{ui.esc(req['skill'])}</strong>
                  <span class="tm-chip {nature}" style="margin-left:.4rem">{ui.esc(req.get('nature',''))}</span></div>
                  <div style="white-space:nowrap;color:#6E7B76;font-size:.8rem">
                    {ui.dots(req.get('level',3))} <strong style="color:#10231F">{int(req.get('level',3))}/5</strong></div>
                </div>"""
            )
        st.markdown("".join(rows) or '<div class="tm-card-sub">Compétences non précisées.</div>', unsafe_allow_html=True)

        if job.get("qualities"):
            st.markdown('<div class="tm-eyebrow" style="margin-top:1rem">Qualités attendues</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:.3rem">{ui.chips([q["skill"] for q in job["qualities"]], limit=8)}</div>',
                unsafe_allow_html=True,
            )
        if job.get("languages"):
            st.markdown('<div class="tm-eyebrow" style="margin-top:1rem">Langues</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:.3rem">{ui.chips([f"{l['name']} · {l['min']}" for l in job["languages"]], tone="ghost")}</div>',
                unsafe_allow_html=True,
            )
        education = job.get("education", {})
        if education.get("min_level"):
            fields = ", ".join(education.get("fields", [])[:3]) or "filière ouverte"
            st.markdown('<div class="tm-eyebrow" style="margin-top:1rem">Formation</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tm-card-sub" style="margin-top:.2rem"><strong style="color:#10231F">{ui.esc(education["min_level"])}</strong><br>{ui.esc(fields)}</div>',
                unsafe_allow_html=True,
            )
        if job.get("certifications"):
            st.markdown('<div class="tm-eyebrow" style="margin-top:1rem">Certifications appréciées</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:.3rem">{ui.chips([c["name"] for c in job["certifications"]], tone="lime")}</div>',
                unsafe_allow_html=True,
            )

    st.write("")
    target = _is_target(job)
    col1, col2, col3 = st.columns([1.4, 1, 1])
    with col1:
        if require_profile():
            if st.button("🚀 Analyser ma compatibilité", type="primary", width="stretch", key="job_analyze"):
                _go_analyze(job, custom)
    with col2:
        if target:
            st.button("✓ Offre cible actuelle", disabled=True, width="stretch", key="job_target_done")
        else:
            if st.button("Définir comme cible", width="stretch", key="job_set_target"):
                set_target_job(job, custom=custom)
                st.toast("Offre cible enregistrée.", icon="🎯")
                st.rerun()
    with col3:
        if st.button("Voir le plan type", width="stretch", key="job_plan_hint"):
            nav_to("plan")

    if job.get("nice_to_have"):
        ui.note(f"🌱 <strong>Bonus :</strong> {ui.esc(', '.join(job['nice_to_have'][:6]))} — des atouts qui font la différence si tu les mentionnes.")

    st.write("")
    ui.note(
        "💡 Le score estimé compare <strong>tes données actuelles</strong> à cette offre. "
        "L'analyse complète détaille chaque écart et propose un plan 7 / 30 / 90 jours."
    )


# --------------------------------------------------------------------------- #
# Offre personnalisée
# --------------------------------------------------------------------------- #

def _local_parse_offer(text: str, fallback_title: str) -> dict:
    counts = extract_skills(text)
    ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    skills = []
    for name, count in ordered[:10]:
        skills.append({
            "skill": name,
            "level": 4 if count >= 3 else 3,
            "weight": 3 if count >= 3 else 2,
            "nature": "indispensable" if count >= 3 else "important",
        })
    languages = detect_languages(text)
    if not languages:
        languages = {"Anglais": "B2"}
    education = detect_education(text)
    lines = [line.strip(" -•·\t") for line in text.splitlines() if len(line.strip()) > 3]
    missions = [line for line in lines if line.lower().startswith(("concevoir", "développer", "analyser", "participer", "construire", "réaliser", "assurer", "contribuer", "rédiger", "suivre", "produire", "gérer", "metric", "mission"))][:6]
    keywords = [skill for skill, _ in ordered[:8]] or [fallback_title]
    return {
        "skills": skills,
        "languages": languages,
        "education": education,
        "missions": missions,
        "keywords": keywords,
    }


def _render_custom_job(profile: dict) -> None:
    ui.section_header(
        "Offre personnalisée",
        "Colle une offre réelle, Tremplin l'analyse",
        "Le moteur extrait automatiquement compétences, langues et formation. Tu ajustes avant de lancer l'analyse.",
    )
    if not require_profile():
        return

    text = st.text_area(
        "Texte de l'offre (LinkedIn, Welcome to the Jungle, PDF…)",
        height=220,
        key="custom_raw_text",
        placeholder="Colle ici l'intitulé, la description du poste et les compétences demandées…",
    )

    col1, col2, col3 = st.columns([1.4, 1, 1])
    with col1:
        title = st.text_input("Intitulé du poste *", key="custom_title", placeholder="Ex. : Data Analyst — Stage")
    with col2:
        company = st.text_input("Entreprise", key="custom_company", placeholder="Ex. : NovaPay")
    with col3:
        contract = st.selectbox("Contrat", ["Stage", "Alternance", "CDI junior", "CDD / Freelance"], key="custom_contract")

    col4, col5, col6 = st.columns([1.2, 1, 1])
    with col4:
        domain = st.selectbox("Domaine", TARGET_DOMAINS, index=0, key="custom_domain")
    with col5:
        location = st.text_input("Lieu", key="custom_location", placeholder="Ex. : Lyon")
    with col6:
        min_level = st.selectbox("Diplôme attendu", EDUCATION_LEVELS, index=2, key="custom_level")

    ai_settings = llm.resolve_settings(st.session_state.get("ai_settings"))
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        parse_clicked = st.button("Detecter les exigences (moteur local)", type="secondary", width="stretch", key="custom_parse")
    with col_b:
        ai_clicked = st.button(
            "Affiner avec l'IA" if ai_settings.enabled else "IA non configurée",
            disabled=not ai_settings.enabled,
            width="stretch",
            key="custom_parse_ai",
            help="Active un fournisseur IA dans les réglages pour utiliser cette option.",
        )

    if parse_clicked or ai_clicked:
        if len(text.strip()) < 60:
            st.warning("Colle d'abord le texte de l'offre (au moins quelques lignes).", icon="⚠️")
        elif ai_clicked:
            with st.spinner("L'IA analyse l'offre…"):
                parsed, error = llm.parse_job_with_ai(text, SKILL_NAMES, ai_settings)
            if error:
                st.error(f"IA indisponible : {error}. Utilise la détection locale.")
            else:
                st.session_state.custom_preview = {**(_local_parse_offer(text, title)), **{k: v for k, v in parsed.items() if v}}
                st.session_state.custom_preview["_source"] = "IA"
                st.toast("Exigences extraites par l'IA.", icon="🤖")
        else:
            local = _local_parse_offer(text, title or "Offre")
            st.session_state.custom_preview = {**local, "_source": "local"}
            st.toast("Exigences détectées localement.", icon="🔎")

    preview = st.session_state.get("custom_preview")
    if preview:
        st.write("")
        source = "l'IA" if preview.get("_source") == "IA" else "le moteur local"
        st.markdown(f'<div class="tm-eyebrow">Exigences extraites par {source} — vérifie et ajuste</div>', unsafe_allow_html=True)
        detected = [s["skill"] for s in preview.get("skills", [])]
        chosen_skills = st.multiselect(
            "Compétences exigées",
            options=SKILL_NAMES,
            default=[s for s in detected if s in SKILL_NAMES],
            key="custom_skills_select",
        )
        col_l, col_e = st.columns(2)
        with col_l:
            chosen_langs = st.multiselect(
                "Langues exigées",
                options=["Anglais", "Français", "Espagnol", "Allemand", "Italien", "Chinois", "Arabe", "Portugais"],
                default=list((preview.get("languages") or {}).keys()),
                key="custom_langs_select",
            )
            lang_level = st.selectbox("Niveau minimum en langue", CEFR_LEVELS, index=3, key="custom_lang_level")
        with col_e:
            education = preview.get("education") or {}
            st.caption("Formation : " + (education.get("level") or "non détectée"))
            summary = st.text_area("Résumé (affiché dans l'analyse)", key="custom_summary", height=84,
                                   value=(preview.get("summary") or text.strip().split("\n")[0][:220]))

        if st.button("📊 Créer l'offre et lancer l'analyse", type="primary", width="stretch", key="custom_create"):
            raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
            final_title = title.strip() or (raw_lines[0][:90] if raw_lines else "Offre personnalisée")
            job = empty_custom_job()
            job.update({
                "id": "custom",
                "title": final_title,
                "company": company.strip() or "Entreprise non précisée",
                "company_type": "Offre importée",
                "domain": domain,
                "contract": contract,
                "location": location.strip(),
                "summary": summary.strip(),
                "description": text.strip()[:1200],
                "missions": preview.get("missions", []),
                "keywords": [k for k in (preview.get("keywords") or []) if k][:10],
                "raw_text": text.strip(),
            })
            job["required_skills"] = [
                {"skill": skill, "level": 3, "weight": 2, "nature": "important"}
                for skill in chosen_skills[:12]
            ]
            job["languages"] = [{"name": lang, "min": lang_level, "weight": 2} for lang in chosen_langs]
            job["education"] = {"min_level": min_level, "fields": [domain] if domain != "Autre" else []}
            st.session_state.custom_job = job
            st.session_state.custom_preview = None
            _go_analyze(job, custom=True)
    else:
        ui.note("ℹ️ Colle l'offre puis lance la détection : tu pourras modifier les exigences avant l'analyse, sans aucune obligation d'IA.")


# --------------------------------------------------------------------------- #
# Catalogue
# --------------------------------------------------------------------------- #

def _job_card(job: dict, score: int | None, profile: dict) -> None:
    is_target = _is_target(job)
    target_badge = '<span class="tm-chip lime">Cible</span>' if is_target else ""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:.5rem">
              <div>
                <div class="tm-eyebrow">{ui.esc(job.get('domain',''))}</div>
                <div class="tm-card-title" style="margin-top:.15rem">{ui.esc(job.get('title',''))}</div>
                <div class="tm-card-sub">{ui.esc(job.get('company',''))} · {ui.esc(job.get('company_type',''))} · {ui.esc(job.get('location',''))}</div>
              </div>
              <div style="text-align:right">{target_badge}{ui.score_pill(score, 'estimé') if score is not None else ''}</div>
            </div>
            <div style="margin-top:.55rem">{ui.chips([r['skill'] for r in job.get('required_skills', [])], tone='ghost', limit=5)}</div>
            <div style="margin-top:.4rem">{ui.chips([m for m in [job.get('contract'), job.get('duration'), job.get('remote')] if m], limit=3)}</div>
            """,
            unsafe_allow_html=True,
        )
        if score is not None:
            st.markdown(ui.progress_bar(score, ui.score_tone(score)), unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.4])
        with c1:
            if st.button("Détail", key=f"job_detail_{job['id']}", width="stretch"):
                st.session_state.job_view_id = job["id"]
                st.rerun()
        with c2:
            if st.button("Analyser", key=f"job_go_{job['id']}", type="primary", width="stretch"):
                if require_profile():
                    _go_analyze(job)


def _render_catalog(profile: dict) -> None:
    ui.section_header(
        "Catalogue",
        "Choisis ton terrain de jeu",
        "Des offres réalistes de stage, d'alternance et de premier emploi — ou colle la tienne.",
    )
    jobs = [j for j in JOBS if not j.get("is_custom")]
    with st.container(border=True):
        search = st.text_input(
            "Recherche",
            key="jobs_search",
            placeholder="Poste, entreprise, compétence (ex. : data, React, marketing)…",
            label_visibility="collapsed",
        )
        col1, col2, col3 = st.columns([1.1, 1.3, 1])
        with col1:
            contract_filter = st.pills(
                "Contrat",
                options=["Tous", "Stage", "Alternance", "CDI junior"],
                default="Tous",
                key="jobs_contract",
            )
        with col2:
            domain_filter = st.selectbox("Domaine", ["Tous les domaines"] + TARGET_DOMAINS, key="jobs_domain")
        with col3:
            sort_mode = st.selectbox("Tri", ["Compatibilité estimée", "Nom", "Contrat"], key="jobs_sort")

    filtered = []
    search_norm = search.strip().lower()
    for job in jobs:
        if search_norm and search_norm not in job_search_text(job).lower():
            continue
        if contract_filter and contract_filter != "Tous" and job.get("contract") != contract_filter:
            continue
        if domain_filter and domain_filter != "Tous les domaines" and job.get("domain") != domain_filter:
            continue
        filtered.append(job)

    profile_json = json.dumps(profile, ensure_ascii=False, sort_keys=True, default=str)
    has_profile = bool(profile.get("skills")) or bool(profile.get("identity", {}).get("name"))
    scored = [(job, _quick_score(profile_json, job["id"]) if has_profile else None) for job in filtered]

    if sort_mode == "Compatibilité estimée" and has_profile:
        scored.sort(key=lambda item: item[1] or 0, reverse=True)
    elif sort_mode == "Nom":
        scored.sort(key=lambda item: item[0].get("title", ""))
    elif sort_mode == "Contrat":
        scored.sort(key=lambda item: (item[0].get("contract", ""), -1 * (item[1] or 0)))

    st.write("")
    if not scored:
        ui.empty_state("🔍", "Aucune offre ne correspond", "Élargis la recherche ou réinitialise les filtres.")
        return

    st.caption(f"{len(scored)} offre(s) — {'scores estimés avec ton profil actuel' if has_profile else 'complète ton profil pour voir les scores'}")
    for index in range(0, len(scored), 2):
        pair = scored[index:index + 2]
        cols = st.columns(2, gap="medium")
        for col, (job, score) in zip(cols, pair):
            with col:
                _job_card(job, score, profile)


# --------------------------------------------------------------------------- #
# Entrée de page
# --------------------------------------------------------------------------- #

def render() -> None:
    profile = storage.get_profile()

    view_id = st.session_state.get("job_view_id")
    if view_id:
        job = get_job(view_id)
        if job:
            _render_job_detail(job, profile)
            return
        st.session_state.job_view_id = None

    ui.hero(
        badge="Offres & cibles",
        title_html="Trouve le poste<br><em>où tu peux gagner.</em>",
        subtitle=(
            "Explore le catalogue : des offres au Maroc (Casablanca, Rabat, Tanger…) "
            "et quelques opportunités à l'international — ou colle une offre réelle pour l'analyser."
        ),
        points=[f"{len(JOBS)} offres réalistes", "Score estimé instantané", "Offre collée = analyse immédiate"],
    )
    st.write("")

    tab_catalog, tab_custom = st.tabs(["📚 Catalogue", "📋 Offre personnalisée"])
    with tab_catalog:
        _render_catalog(profile)
        target = get_target_job()
        if target:
            st.write("")
            ui.note(f"🎯 <strong>Ta cible actuelle :</strong> {ui.esc(job_label(target))} — lance une analyse pour voir le détail des écarts.")
    with tab_custom:
        _render_custom_job(profile)
