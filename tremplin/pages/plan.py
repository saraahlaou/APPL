"""Page Plan : feuille de route 7 / 30 / 90 jours avec progression persistée."""

from __future__ import annotations

import streamlit as st

from .. import report, storage, ui
from .common import analyses_as_options, nav_to

TYPE_ICONS = {
    "CV": "📝",
    "Entretien": "🎤",
    "Formation": "🎓",
    "Projet": "🛠️",
    "Certification": "🏅",
    "Réseau": "🤝",
    "Recherche": "🔎",
    "Langue": "🌍",
    "Qualité": "💬",
}
TYPE_LABELS = {
    "CV": "CV",
    "Entretien": "Entretien",
    "Formation": "Formation",
    "Projet": "Projet",
    "Certification": "Certification",
    "Réseau": "Réseau",
    "Recherche": "Recherche",
    "Langue": "Langue",
    "Qualité": "Qualité",
}


def _current_analysis() -> dict | None:
    analysis = storage.get_analysis(st.session_state.get("current_analysis_id"))
    if analysis and (analysis.get("plan") or {}).get("phases"):
        return analysis
    for item in storage.get_analyses():
        if (item.get("plan") or {}).get("phases"):
            return item
    return None


def _render_progress_banner(analysis: dict) -> None:
    done, total = storage.plan_completion(analysis)
    pct = (done / total * 100) if total else 0
    score = analysis.get("score", 0)
    projected = analysis.get("projected_score") or score
    hours_left = 0
    for phase in analysis["plan"]["phases"]:
        for action in phase.get("actions", []):
            if not storage.is_action_done(analysis.get("id", ""), action["id"]):
                hours_left += action.get("effort_hours", 0)
    ui.stat_grid([
        {"label": "Progression du plan", "value": f"{pct:.0f}%", "sub": f"{done} / {total} actions réalisées"},
        {"label": "Effort restant", "value": f"{hours_left:.0f} h", "sub": "À répartir sur tes semaines"},
        {"label": "Score actuel", "value": f"{score}/100", "sub": ui.esc(analysis.get("verdict", {}).get("label", ""))},
        {"label": "Score visé", "value": f"{projected}/100", "sub": "Si tu suis ce plan"},
    ])
    st.markdown(ui.progress_bar(pct, ui.score_tone(pct)), unsafe_allow_html=True)


def _render_action(analysis: dict, action: dict, phase_key: str) -> None:
    analysis_id = analysis.get("id", "")
    done_key = f"plan_{analysis_id}_{action['id']}"
    completed = storage.is_action_done(analysis_id, action["id"])
    icon = TYPE_ICONS.get(action.get("type", ""), "•")
    cols = st.columns([0.06, 1], vertical_alignment="top")
    with cols[0]:
        checked = st.checkbox(
            "Fait",
            value=completed,
            key=done_key,
            label_visibility="collapsed",
            help="Marquer cette action comme réalisée",
        )
        if checked != completed:
            storage.set_action_done(analysis_id, action["id"], checked)
            st.rerun()
    with cols[1]:
        strike = "text-decoration:line-through;color:#9AA7A1" if completed else "color:#10231F"
        impact = action.get("impact_points", 0)
        effort = action.get("effort_hours", 0)
        st.markdown(
            f"""<div style="display:flex;justify-content:space-between;gap:.6rem;align-items:flex-start">
                  <div>
                    <div style="font-weight:700;font-size:.94rem;{strike}">{icon} {ui.esc(action['title'])}</div>
                    <div style="color:#3D4C46;font-size:.84rem;line-height:1.6;margin-top:.15rem">{ui.esc(action['detail'])}</div>
                  </div>
                  <div style="text-align:right;white-space:nowrap">
                    {ui.chips([TYPE_LABELS.get(action.get('type',''), action.get('type',''))], tone='ghost')}
                    <div style="font-size:.72rem;color:#6E7B76;margin-top:.25rem">+{impact:.0f} pts · ~{effort:.0f} h</div>
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )
        resource = action.get("resource") or {}
        if resource.get("url"):
            label = f"🎓 {resource.get('title','Ressource')} · {resource.get('provider','')}"
            st.link_button(label[:80], resource["url"], help=f"{resource.get('kind','')} · {resource.get('duration','')} · {resource.get('price','')}")
        st.write("")


def _render_plan(analysis: dict) -> None:
    job = analysis.get("job", {})
    st.markdown(
        f"""
        <div class="tm-eyebrow">Plan personnalisé</div>
        <h2 style="margin:.2rem 0 0;font-family:Fraunces,serif;color:#10231F">{ui.esc(analysis.get('job_title',''))}</h2>
        <div class="tm-card-sub">{ui.esc(analysis.get('company',''))} — généré le {ui.esc(analysis.get('created_at','')[:10])}</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    _render_progress_banner(analysis)
    st.write("")

    if not analysis.get("plan", {}).get("phases"):
        ui.note("Cette analyse ne contient pas de plan. Relance une analyse complète depuis la page Offres.")
        if st.button("Relancer une analyse", type="primary", key="plan_relaunch"):
            nav_to("jobs")
        return

    tabs = st.tabs([f"{phase['title']}" for phase in analysis["plan"]["phases"]])
    for tab, phase in zip(tabs, analysis["plan"]["phases"]):
        with tab:
            st.markdown(f'<div class="tm-card-sub" style="margin-bottom:.6rem">{ui.esc(phase.get("subtitle",""))}</div>', unsafe_allow_html=True)
            done, total = 0, len(phase.get("actions", []))
            for action in phase.get("actions", []):
                _render_action(analysis, action, phase["key"])

    st.divider()
    done, total = storage.plan_completion(analysis)
    col1, col2, col3 = st.columns([1.3, 1, 1])
    profile = storage.get_profile()
    with col1:
        st.download_button(
            "⬇️ Exporter le plan (Markdown)",
            report.analysis_markdown(analysis, profile),
            file_name=f"tremplin-plan-{analysis.get('id','')}.md",
            mime="text/markdown",
            width="stretch",
            key="plan_dl_md",
        )
    with col2:
        if st.button("🔁 Revoir l'analyse", width="stretch", key="plan_back_analysis"):
            st.session_state.current_analysis_id = analysis.get("id")
            nav_to("analysis")
    with col3:
        if st.button("♻️ Réinitialiser la progression", width="stretch", key="plan_reset"):
            progress = storage.get_plan_progress()
            prefix = f"{analysis.get('id','')}:"
            for key in [k for k in progress if k.startswith(prefix)]:
                progress.pop(key, None)
            for key in [k for k in st.session_state.keys() if str(k).startswith(f"plan_{analysis.get('id','')}_")]:
                del st.session_state[key]
            storage.save_state()
            st.toast("Progression du plan réinitialisée.", icon="♻️")
            st.rerun()

    if done and done == total:
        ui.note("🎉 <strong>Plan terminé à 100 % !</strong> Tu peux relancer une analyse pour constater ta progression, ou tout réinitialiser pour recommencer un cycle.")
        st.balloons()
    elif done:
        ui.note(f"💪 <strong>{done} action(s) réalisée(s).</strong> Pense à mettre à jour ton profil (compétences, projets) : le score évoluera dès la prochaine analyse.")
    else:
        ui.note("🌱 <strong>Commence par une action du sprint 7 jours.</strong> Une seule action cochée, c'est déjà un plan qui avance.")


def render() -> None:
    analyses = storage.get_analyses()
    if not analyses:
        ui.empty_state("🗺️", "Pas encore de plan", "Lance une analyse depuis une offre : Tremplin génère une feuille de route 7 / 30 / 90 jours adaptée à tes lacunes.")
        st.write("")
        if st.button("Analyser une offre", type="primary", icon="🚀", key="plan_pick_job"):
            nav_to("jobs")
        return

    ui.hero(
        badge="Plan d'action",
        title_html="Des actions concrètes,<br><em>pas des vœux pieux.</em>",
        subtitle="Coche chaque action réalisée : ta progression est sauvegardée automatiquement.",
        points=["Sprints 7 / 30 / 90 jours", "Formations avec liens réels", "Progression persistée"],
    )
    st.write("")

    options = analyses_as_options()
    ids = list(options.keys())
    current = st.session_state.get("current_analysis_id") or ids[0]
    if current not in options:
        current = ids[0]
    with st.container(border=True):
        choice = st.selectbox(
            "Analyse à afficher",
            options=ids,
            index=ids.index(current),
            format_func=lambda key: options[key],
            key="plan_analysis_select",
        )
        if choice != st.session_state.get("current_analysis_id"):
            st.session_state.current_analysis_id = choice

    analysis = _current_analysis()
    if analysis:
        st.write("")
        _render_plan(analysis)
