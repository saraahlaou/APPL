"""Page Analyse : score de compatibilité, lacunes, forces et enrichissement IA."""

from __future__ import annotations

import streamlit as st

from .. import llm, report, storage, ui
from ..matching import analyze
from .common import get_target_job, job_label, nav_to, require_profile

SUBCORE_WEIGHT_KEYS = {
    "Compétences": "skills",
    "Qualités": "qualities",
    "Projets & expérience": "portfolio",
    "Langues": "languages",
    "Formation & certifications": "formation",
}

STEPS = [
    ("📄", "Lecture de ton profil", "Compétences, projets, langues, certifications, CV…"),
    ("🎯", "Décodage de l'offre", "Exigences, niveaux attendus et critères de présélection."),
    ("⚖️", "Comparaison", "Couverture de chaque compétence et détection des écarts."),
    ("🧮", "Calcul du score", "Pondération selon le domaine : le score s'explique, il ne se devine pas."),
    ("🗺️", "Génération du plan", "Actions concrètes 7 / 30 / 90 jours avec ressources réelles."),
]


def _needs_analysis(profile: dict, job: dict) -> bool:
    if st.session_state.pop("auto_analyze", False):
        return True
    current = storage.get_analysis(st.session_state.get("current_analysis_id"))
    if not current:
        return True
    if current.get("profile_hash") != storage.profile_hash(profile):
        return True
    return current.get("job_id") != job.get("id")


def _run_analysis(profile: dict, job: dict) -> dict:
    with st.status("Analyse en cours…", expanded=True) as status:
        for icon, title, detail in STEPS:
            st.write(f"{icon} **{title}** — {detail}")
        result = analyze(profile, job, with_plan=True)
        result["profile_hash"] = storage.profile_hash(profile)
        storage.add_analysis(result)
        done = storage.plan_completion(result)[1]
        status.update(label=f"Analyse terminée — {result['score']}/100 · {done} actions planifiées", state="complete", expanded=False)
    return result


def _render_ai_section(result: dict, profile: dict) -> None:
    ai_settings = llm.resolve_settings(st.session_state.get("ai_settings"))
    st.write("")
    ui.section_header("Coach IA (optionnel)", "Un regard humain en plus des chiffres")
    if not ai_settings.enabled:
        ui.note(
            "🤖 <strong>IA générative non configurée.</strong> Le moteur local te donne déjà score, lacunes et plan. "
            "Si tu veux un récit personnalisé, des questions d'entretien probables et un pitch, configure ton fournisseur dans <em>Réglages</em>."
        )
        if st.button("Configurer l'IA", key="an_go_settings"):
            nav_to("settings")
        return

    col1, col2 = st.columns([1.2, 1])
    with col1:
        if st.button("✨ Enrichir cette analyse avec l'IA", type="primary", width="stretch", key="an_enrich_ai"):
            with st.spinner(f"Appel à {ai_settings.model}…"):
                ai, error = llm.enrich_analysis_with_ai(result, profile, result.get("job", {}))
            if error:
                st.error(f"IA indisponible : {error}", icon="⚠️")
            else:
                result["ai"] = ai
                analyses = storage.get_analyses()
                for index, item in enumerate(analyses):
                    if item.get("id") == result.get("id"):
                        analyses[index] = result
                        break
                st.session_state.analyses = analyses
                storage.save_state()
                st.toast("Analyse enrichie par l'IA.", icon="✨")
                st.rerun()
    with col2:
        st.caption(f"Fournisseur actif : {ai_settings.describe()}")

    ai = result.get("ai")
    if not ai:
        return
    if ai.get("narrative"):
        ui.note(f"🧠 {ai['narrative']}")
    watchouts = ai.get("watchouts", [])
    if watchouts:
        for watchout in watchouts:
            st.markdown(
                f"""<div class="tm-gap important">
                      <div class="head"><div class="title">⚠️ {ui.esc(watchout.get('title',''))}</div></div>
                      <div class="why">{ui.esc(watchout.get('detail',''))}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
    if ai.get("pitch"):
        ui.note(f"🎤 <strong>Pitch de candidature :</strong> {ui.esc(ai['pitch'])}")


def _render_subscores(result: dict) -> None:
    weights = result.get("weights", {})
    total_weight = sum(weights.values()) or 1
    rows = []
    for label, value in result.get("subscores", {}).items():
        weight = weights.get(SUBCORE_WEIGHT_KEYS.get(label, ""), 0)
        rows.append((label, value, weight / total_weight * 100))
    cols = st.columns(len(rows), gap="medium")
    for col, (label, value, weight_pct) in zip(cols, rows):
        with col:
            st.markdown(
                f"""
                <div class="tm-card" style="text-align:center;padding:.8rem .6rem">
                  <div style="font-size:1.5rem;font-weight:800;color:{ui.score_color(value)}">{value}</div>
                  <div style="font-size:.78rem;font-weight:700;color:#2E3A35">{ui.esc(label)}</div>
                  <div style="font-size:.7rem;color:#6E7B76">poids {weight_pct:.0f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(ui.progress_bar(value, ui.score_tone(value)), unsafe_allow_html=True)


def _render_result(result: dict, profile: dict) -> None:
    job = result.get("job", {})
    score = result.get("score", 0)
    verdict = result.get("verdict", {})
    projected = result.get("projected_score") or score
    tone = ui.score_tone(score)

    identity = profile.get("identity", {})
    st.markdown(
        f"""
        <div class="tm-eyebrow">{ui.esc(job.get('domain',''))} · {ui.esc(job.get('contract',''))} · {ui.esc(job.get('location',''))}</div>
        <h2 style="margin:.2rem 0 0;font-family:Fraunces,serif;color:#10231F">{ui.esc(result.get('job_title',''))}</h2>
        <div class="tm-card-sub">{ui.esc(result.get('company',''))} · analysé le {ui.esc(result.get('created_at','')[:10])} pour {ui.esc(identity.get('name','toi'))}</div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    left, right = st.columns([1, 1.5], gap="large", vertical_alignment="center")
    with left:
        st.markdown(ui.gauge(score, "compatibilité"), unsafe_allow_html=True)
        st.markdown(
            f"""<div style="text-align:center;margin-top:-.4rem">
                  <span class="tm-chip {tone}">{ui.esc(verdict.get('label',''))}</span>
                  <div style="font-size:.74rem;color:#6E7B76;margin-top:.4rem">Confiance de l'analyse : {result.get('confidence',0)}%</div>
                </div>""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="tm-card">
              <div class="tm-card-title">Ce que dit ton score</div>
              <div class="tm-card-sub" style="line-height:1.65">{ui.esc(result.get('narrative',''))}</div>
              <div style="display:flex;gap:1.5rem;margin-top:.8rem">
                <div><div style="font-size:.72rem;color:#6E7B76;text-transform:uppercase;letter-spacing:.08em">Aujourd'hui</div>
                     <div style="font-size:1.5rem;font-weight:800;color:{ui.score_color(score)}">{score}<span style="font-size:.8rem;color:#6E7B76">/100</span></div></div>
                <div><div style="font-size:.72rem;color:#6E7B76;text-transform:uppercase;letter-spacing:.08em">Après ton plan</div>
                     <div style="font-size:1.5rem;font-weight:800;color:{ui.score_color(projected)}">{projected}<span style="font-size:.8rem;color:#6E7B76">/100</span></div></div>
                <div><div style="font-size:.72rem;color:#6E7B76;text-transform:uppercase;letter-spacing:.08em">Score visé</div>
                     <div style="font-size:1.5rem;font-weight:800;color:#17795E">+{max(0, projected - score)}</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    _render_subscores(result)

    st.write("")
    col_radar, col_read = st.columns([1, 1.2], gap="large")
    with col_radar:
        with st.container(border=True):
            st.markdown('<div class="tm-card-title" style="text-align:center">Ton profil face à l\'offre</div>', unsafe_allow_html=True)
            st.markdown(ui.radar(result.get("subscores", {})), unsafe_allow_html=True)
    with col_read:
        with st.container(border=True):
            st.markdown('<div class="tm-card-title">Lecture express</div>', unsafe_allow_html=True)
            strong = result.get("strengths", [])[:3]
            gaps = result.get("gaps", [])[:3]
            html_parts = ['<div class="tm-eyebrow" style="margin-top:.3rem">Tes atouts pour cette offre</div>']
            for item in strong:
                html_parts.append(f'<div class="tm-strength"><div class="mark">✓</div><div><div class="title">{ui.esc(item["title"])}</div><div class="detail">{ui.esc(item["detail"])}</div></div></div>')
            if not strong:
                html_parts.append('<div class="tm-card-sub">Complète ton profil pour faire ressortir tes points forts.</div>')
            html_parts.append('<div class="tm-eyebrow" style="margin-top:.8rem">Tes 3 priorités</div>')
            for gap in gaps:
                html_parts.append(f'<div style="margin:.35rem 0;color:#2E3A35;font-size:.87rem">→ <strong>{ui.esc(gap["title"])}</strong> <span style="color:#6E7B76">(+{gap.get("impact_points",0):.0f} pts possibles)</span></div>')
            if not gaps:
                html_parts.append('<div class="tm-card-sub">Aucune lacune majeure : mise sur l\'entretien et le réseau.</div>')
            st.markdown("".join(html_parts), unsafe_allow_html=True)

    st.write("")
    tab_strengths, tab_gaps, tab_skills, tab_soft, tab_portfolio, tab_tips = st.tabs(
        ["✅ Points forts", "🚧 Lacunes & priorités", "🧩 Compétences", "💬 Qualités & langues", "📁 Formation & projets", "📝 CV & entretien"]
    )
    with tab_strengths:
        st.markdown(ui.strength_items(result.get("strengths", [])), unsafe_allow_html=True)
        if result.get("bonus_opportunities"):
            st.write("")
            st.markdown('<div class="tm-eyebrow">Atouts bonus à mentionner</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:.4rem">{ui.chips(result["bonus_opportunities"], tone="lime")}</div>', unsafe_allow_html=True)
        if result.get("keywords"):
            st.write("")
            st.markdown('<div class="tm-eyebrow">Mots-clés de l\'offre</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:.4rem">{ui.chips(result["keywords"], tone="ghost")}</div>', unsafe_allow_html=True)
    with tab_gaps:
        st.markdown(ui.gap_cards(result.get("gaps", [])), unsafe_allow_html=True)
        st.write("")
        ui.note("👉 Chaque lacune est transformée en action dans ta page <strong>Plan</strong>, avec formations et projets concrets.")
        if st.button("Voir mon plan d'action", type="primary", key="an_go_plan"):
            nav_to("plan")
    with tab_skills:
        st.markdown(ui.skill_matrix_rows(result.get("skills_detail", [])), unsafe_allow_html=True)
    with tab_soft:
        cols = st.columns(2)
        with cols[0]:
            st.markdown('<div class="tm-eyebrow">Qualités</div>', unsafe_allow_html=True)
            for detail in result.get("qualities_detail", []):
                coverage = detail.get("coverage", 0) * 100
                st.markdown(
                    f"""<div style="margin:.5rem 0">
                          <div style="display:flex;justify-content:space-between;font-size:.86rem"><strong>{ui.esc(detail['skill'])}</strong>
                          <span style="color:#6E7B76">{coverage:.0f}%</span></div>
                          {ui.progress_bar(coverage, ui.score_tone(coverage))}
                          <div style="font-size:.74rem;color:#6E7B76;margin-top:.15rem">{ui.esc(detail.get('source',''))}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )
        with cols[1]:
            st.markdown('<div class="tm-eyebrow">Langues</div>', unsafe_allow_html=True)
            for detail in result.get("languages_detail", []):
                coverage = detail.get("coverage", 0) * 100
                st.markdown(
                    f"""<div style="margin:.5rem 0">
                          <div style="display:flex;justify-content:space-between;font-size:.86rem">
                            <strong>{ui.esc(detail['language'])} · {ui.esc(detail.get('current','Non renseigné'))}</strong>
                            <span style="color:#6E7B76">attendu {ui.esc(detail.get('min','—'))}</span></div>
                          {ui.progress_bar(coverage, ui.score_tone(coverage))}
                          <div style="font-size:.74rem;color:#6E7B76;margin-top:.15rem">{ui.esc(detail.get('status',''))}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )
    with tab_portfolio:
        portfolio = result.get("portfolio_detail", {})
        formation = result.get("formation_detail", {})
        cols = st.columns(2)
        with cols[0]:
            st.markdown('<div class="tm-eyebrow">Formation & certifications</div>', unsafe_allow_html=True)
            st.markdown(
                f"""<div class="tm-card">
                      <div style="font-size:.86rem;color:#2E3A35;line-height:1.6">
                        <strong>Niveau actuel :</strong> {ui.esc(formation.get('current_level') or 'non renseigné')}<br>
                        <strong>Attendu :</strong> {ui.esc(formation.get('min_level') or 'non précisé')} — couverture {formation.get('level_coverage',0)*100:.0f}%<br>
                        <strong>Filière :</strong> {ui.esc(formation.get('current_field') or 'non renseignée')}
                      </div>
                    </div>""",
                unsafe_allow_html=True,
            )
            for cert in formation.get("certifications", []):
                tone_cert = "green" if cert.get("matched") else "amber"
                state = "déjà obtenue ✓" if cert.get("matched") else "à envisager"
                st.markdown(f'<div style="margin:.3rem 0">{ui.chips([f"{cert['name']} — {state}"], tone=tone_cert)}</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown('<div class="tm-eyebrow">Projets & expériences</div>', unsafe_allow_html=True)
            st.markdown(
                f"""<div class="tm-card">
                      <div style="font-size:.86rem;color:#2E3A35;line-height:1.6">
                        <strong>{portfolio.get('project_count',0)}</strong> projet(s) · <strong>{portfolio.get('experience_count',0)}</strong> expérience(s)<br>
                        Pertinence maximale d'un projet pour cette offre : <strong>{portfolio.get('max_project_relevance',0)*100:.0f}%</strong>
                      </div>
                    </div>""",
                unsafe_allow_html=True,
            )
            for item in portfolio.get("projects", [])[:4]:
                st.markdown(
                    f"""<div style="margin:.4rem 0;font-size:.85rem">
                          <strong>{ui.esc(item.get('name',''))}</strong> — pertinence {item.get('relevance',0)*100:.0f}%
                          <div style="color:#6E7B76;font-size:.78rem">{ui.esc((item.get('skills') or [])[:5] and ', '.join(item['skills'][:5]) or '')}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )
    with tab_tips:
        cols = st.columns(2)
        with cols[0]:
            st.markdown('<div class="tm-eyebrow">Optimiser ton CV pour cette offre</div>', unsafe_allow_html=True)
            for tip in result.get("cv_tips", []):
                st.markdown(f'<div style="margin:.4rem 0;color:#2E3A35;font-size:.88rem">📝 {ui.esc(tip)}</div>', unsafe_allow_html=True)
        with cols[1]:
            st.markdown('<div class="tm-eyebrow">Préparer l\'entretien</div>', unsafe_allow_html=True)
            for tip in result.get("interview_tips", []):
                st.markdown(f'<div style="margin:.4rem 0;color:#2E3A35;font-size:.88rem">🎤 {ui.esc(tip)}</div>', unsafe_allow_html=True)

    _render_ai_section(result, profile)

    st.write("")
    st.divider()
    profile_state = storage.get_profile()
    md = report.analysis_markdown(result, profile_state)
    html = report.analysis_html(result, profile_state)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("⬇️ Rapport Markdown", md, file_name=f"tremplin-{result.get('id','analyse')}.md", mime="text/markdown", width="stretch", key="an_dl_md")
    with col2:
        st.download_button("⬇️ Rapport imprimable (HTML)", html, file_name=f"tremplin-{result.get('id','analyse')}.html", mime="text/html", width="stretch", key="an_dl_html")
    with col3:
        if st.button("🗺️ Mon plan d'action", width="stretch", key="an_plan_bottom"):
            nav_to("plan")
    with col4:
        if st.button("🎯 Changer d'offre", width="stretch", key="an_change_job"):
            nav_to("jobs")

    if score >= 80:
        st.balloons()


def render() -> None:
    profile = storage.get_profile()
    job = get_target_job()

    if not job:
        ui.empty_state("🎯", "Aucune offre cible", "Choisis une offre dans le catalogue ou colle la tienne pour lancer une analyse.")
        st.write("")
        if st.button("Choisir une offre", type="primary", icon="🎯", key="an_pick_job"):
            nav_to("jobs")
        return

    if not require_profile():
        return

    st.markdown(
        f'<div class="tm-eyebrow">Analyse de compatibilité</div><h2 style="font-family:Fraunces,serif;color:#10231F;margin:.2rem 0 .4rem">'
        f'{ui.esc(job_label(job))}</h2>',
        unsafe_allow_html=True,
    )

    if _needs_analysis(profile, job):
        result = _run_analysis(profile, job)
    else:
        result = storage.get_analysis(st.session_state.get("current_analysis_id"))

    st.write("")
    _render_result(result, profile)
