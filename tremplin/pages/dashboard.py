"""Page Tableau de bord : point d'entrée, progression et recommandations."""

from __future__ import annotations

import json

import streamlit as st

from .. import storage, ui
from ..data_jobs import JOBS, get_job
from ..matching import analyze
from ..profile import completion, next_steps
from .common import nav_to, get_target_job, job_label


@st.cache_data(show_spinner=False)
def _quick_score(profile_json: str, job_id: str) -> dict:
    profile = json.loads(profile_json)
    job = get_job(job_id)
    if not job:
        return {"score": 0, "verdict": ""}
    result = analyze(profile, job, with_plan=False)
    return {"score": result["score"], "verdict": result["verdict"]["label"]}


def _step_card(number: str, title: str, text: str) -> str:
    return f"""
    <div class="tm-card" style="height:100%">
      <div class="tm-chip green">{number}</div>
      <div class="tm-card-title" style="margin-top:.6rem">{title}</div>
      <div class="tm-card-sub">{text}</div>
    </div>
    """


def render_onboarding() -> None:
    ui.hero(
        badge="Bienvenue sur Tremplin",
        title_html="Ne postule plus<br><em>au hasard.</em>",
        subtitle=(
            "Décris ton parcours, choisis un stage ou une alternance, et découvre en quelques "
            "secondes ta compatibilité réelle — avec les lacunes à combler et un plan d'action daté."
        ),
        points=["Score expliqué", "Lacunes priorisées", "Plan 7 / 30 / 90 jours", "Fonctionne hors ligne"],
    )
    st.write("")
    col1, col2, col3, _ = st.columns([1, 1.45, 1, 0.55])
    with col1:
        if st.button("Créer mon profil", type="primary", icon="🙋"):
            nav_to("profile")
    with col2:
        if st.button("Charger le profil de démo", icon="⚡"):
            from .profile_page import clear_profile_widgets

            storage.reset_profile(use_demo=True)
            clear_profile_widgets()
            st.toast("Profil de démonstration chargé : explore librement !", icon="🎓")
            nav_to("dashboard")
    with col3:
        if st.button("Voir les offres", icon="🎯"):
            nav_to("jobs")

    ui.section_header("Méthode", "Comment Tremplin calcule ton score", "Un moteur transparent, pas une boîte noire.")
    steps = [
        _step_card("1", "Tu décris ton profil", "CV importé ou saisi à la main : compétences, projets, langues, certifications."),
        _step_card("2", "Tu choisis une offre", "Catalogue de stages et alternances, ou colle n'importe quelle offre pour l'analyser."),
        _step_card("3", "Tu reçois un plan", "Score détaillé, lacunes priorisées et actions concrètes avec formations et projets."),
    ]
    cols = st.columns(3, gap="medium")
    for col, card in zip(cols, steps):
        with col:
            st.markdown(card, unsafe_allow_html=True)

    st.write("")
    ui.note(
        "🔒 <strong>Tes données restent sur ta machine.</strong> Le moteur local fonctionne sans connexion. "
        "Si tu actives l'IA générative, seuls les éléments nécessaires à l'analyse sont envoyés au fournisseur que tu choisis."
    )


def render_dashboard_filled(profile: dict) -> None:
    identity = profile.get("identity", {})
    first_name = (identity.get("name") or "").split(" ")[0]
    pct, _ = completion(profile)
    target = get_target_job()
    analyses = storage.get_analyses()
    best = max((a.get("score", 0) for a in analyses), default=None)

    greeting = f"Bonjour {first_name}" if first_name else "Bonjour"
    target_text = (
        f"Ta cible actuelle : {job_label(target)}."
        if target else
        "Choisis une offre cible pour lancer une analyse."
    )
    ui.hero(
        badge=f"{greeting} 👋",
        title_html="Ton profil a de la valeur.<br><em>Trouvons où il compte le plus.</em>",
        subtitle=target_text,
        points=[f"Profil complété à {pct}%", f"{len(profile.get('skills', {}))} compétences", f"{len(analyses)} analyse(s)"],
    )

    st.write("")
    ui.stat_grid([
        {"label": "Profil complété", "value": f"{pct}%", "sub": "Objectif : 80% pour un score fiable"},
        {"label": "Meilleur score", "value": f"{best}/100" if best is not None else "—", "sub": "Sur tes analyses passées"},
        {"label": "Analyses", "value": str(len(analyses)), "sub": "Historique conservé localement"},
        {
            "label": "Cible",
            "value": (target or {}).get("contract", "—"),
            "sub": (target or {}).get("title", "Aucune offre sélectionnée")[:46],
        },
    ])

    st.write("")
    left, right = st.columns([1.25, 1], gap="large")

    with left:
        ui.section_header("Dernière analyse", "Où en es-tu ?")
        latest = analyses[0] if analyses else None
        if latest:
            score = latest.get("score", 0)
            tone = ui.score_tone(score)
            with st.container(border=True):
                col_gauge, col_text = st.columns([1, 1.5], vertical_alignment="center")
                with col_gauge:
                    st.markdown(ui.gauge(score, "compatibilité", size=150), unsafe_allow_html=True)
                with col_text:
                    st.markdown(
                        f"""
                        <div class="tm-eyebrow">{ui.esc(latest.get('verdict',{}).get('label',''))}</div>
                        <div class="tm-card-title" style="font-size:1.15rem;margin-top:.2rem">{ui.esc(latest.get('job_title',''))}</div>
                        <div class="tm-card-sub">{ui.esc(latest.get('company',''))} · {ui.esc(latest.get('created_at','')[:10])}</div>
                        <div style="margin-top:.6rem">{ui.chips([g['title'] for g in latest.get('gaps', [])[:3]], tone='amber')}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                cta1, cta2, cta3 = st.columns(3)
                if cta1.button("Voir l'analyse", type="primary", width="stretch", key="dash_view_analysis"):
                    st.session_state.current_analysis_id = latest.get("id")
                    nav_to("analysis")
                if cta2.button("Mon plan", width="stretch", key="dash_view_plan"):
                    nav_to("plan")
                if cta3.button("Nouvelle analyse", width="stretch", key="dash_new_analysis"):
                    nav_to("jobs")
        else:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="tm-card-title">Aucune analyse pour l'instant</div>
                    <div class="tm-card-sub">Ton profil est chargé : il ne reste plus qu'à choisir une offre.</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Choisir une offre cible", type="primary", icon="🚀", width="stretch"):
                    nav_to("jobs")

    with right:
        ui.section_header("Prochaines étapes", "Ton raccourci vers un meilleur score")
        for step in next_steps(profile, limit=4):
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="tm-card-title">{ui.esc(step['title'])}</div>
                    <div class="tm-card-sub">{ui.esc(step['why'])}</div>
                    """,
                    unsafe_allow_html=True,
                )
        if st.button("Continuer mon profil", width="stretch", key="dash_profile"):
            nav_to("profile")

    # ------------------------------------------------------------------ #
    # Offres recommandées
    # ------------------------------------------------------------------ #
    ui.section_header(
        "Recommandations",
        "Les offres où ton profil performe déjà",
        "Score estimé à partir de tes compétences actuelles — lance une analyse pour le détail.",
    )
    profile_json = json.dumps(profile, ensure_ascii=False, sort_keys=True, default=str)
    scored = []
    for job in JOBS:
        quick = _quick_score(profile_json, job["id"])
        scored.append((quick["score"], job, quick["verdict"]))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:3]
    cols = st.columns(3, gap="medium")
    for col, (score, job, verdict) in zip(cols, top):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:.5rem">
                      <div>
                        <div class="tm-eyebrow">{ui.esc(job.get('domain',''))}</div>
                        <div class="tm-card-title" style="margin-top:.15rem">{ui.esc(job.get('title',''))}</div>
                        <div class="tm-card-sub">{ui.esc(job.get('company',''))} · {ui.esc(job.get('location',''))}</div>
                      </div>
                      {ui.score_pill(score)}
                    </div>
                    <div style="margin-top:.55rem">{ui.chips([r['skill'] for r in job.get('required_skills', [])], tone='ghost', limit=4)}</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Analyser", key=f"dash_analyze_{job['id']}", width="stretch"):
                    st.session_state.selected_job_id = job["id"]
                    st.session_state.custom_job = None
                    st.session_state.auto_analyze = True
                    nav_to("analysis")

    st.write("")
    ui.note(
        "💡 <strong>Astuce :</strong> plus ton profil contient de preuves (projets, expériences, CV), "
        "plus le score est fiable. Un score bas n'est pas un verdict : c'est une carte des progrès à faire."
    )


def render() -> None:
    profile = storage.get_profile()
    identity = profile.get("identity", {})
    is_empty = not identity.get("name") and not profile.get("skills")
    if is_empty:
        render_onboarding()
    else:
        render_dashboard_filled(profile)
