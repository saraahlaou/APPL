"""Page Mon profil : identité, compétences, projets, langues, certifications et CV."""

from __future__ import annotations

import copy
import hashlib
import uuid

import pandas as pd
import streamlit as st

from .. import storage, ui
from ..cv_parser import audit_cv, detect_profile_updates, extract_text
from ..data_skills import (
    CEFR_LEVELS,
    EDUCATION_LEVELS,
    HARD_SKILLS,
    SKILLS,
    SKILL_LEVELS,
    SOFT_SKILLS,
    STUDY_FIELDS,
)
from ..llm import parse_cv_with_ai, resolve_settings
from ..matching import canonical_skill
from ..profile import completion, touch
from .common import ensure_key, get_target_job, nav_to, slugify, suggested_skills_for_job

LANGUAGE_OPTIONS = [
    "Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais",
    "Arabe", "Chinois", "Japonais", "Russe", "Coréen", "Néerlandais", "Turc",
]

CERT_STATUS = ["Obtenue", "En cours", "Prévue"]


def clear_profile_widgets() -> None:
    """Efface les widgets du profil pour recharger les valeurs depuis l'état."""
    for key in list(st.session_state.keys()):
        if str(key).startswith("pf_"):
            del st.session_state[key]


def _selector_options(base: list[str], current: str) -> list[str]:
    options = [""] + base
    return options if not current or current in options else options + [current]


def _add_skills(skills: list[str]) -> None:
    options = list(st.session_state.get("pf_skill_options", HARD_SKILLS))
    for skill in skills:
        if skill and skill not in options:
            options.append(skill)
    st.session_state.pf_skill_options = options
    selected = list(st.session_state.get("pf_skills_selected", []))
    for skill in skills:
        if skill and skill not in selected:
            selected.append(skill)
    st.session_state.pf_skills_selected = selected


def _add_custom_skill() -> None:
    raw = str(st.session_state.get("pf_custom_skill", "")).strip()
    if not raw:
        return
    skill = canonical_skill(raw) or raw
    _add_skills([skill])
    st.session_state.pf_custom_skill = ""


def _apply_cv_detected() -> None:
    detected = st.session_state.get("pf_cv_detected") or {}
    profile = storage.get_profile()

    skills = detected.get("skills", {}) or {}
    _add_skills(list(skills.keys()))
    for skill, level in skills.items():
        st.session_state[f"pf_level_{slugify(skill)}"] = int(level)

    qualities = detected.get("qualities", []) or []
    if qualities:
        current_qualities = list(profile.get("qualities", []))
        for quality in qualities:
            if quality not in current_qualities:
                current_qualities.append(quality)
        profile["qualities"] = current_qualities
        st.session_state["pf_qualities"] = current_qualities

    languages = detected.get("languages", {}) or {}
    if languages:
        current = dict(profile.get("languages", {}))
        for name, level in languages.items():
            current[name] = level
        profile["languages"] = current
        st.session_state.pop("pf_languages_editor", None)

    certifications = detected.get("certifications", []) or []
    if certifications:
        existing = {c.get("name") for c in profile.get("certifications", [])}
        merged = list(profile.get("certifications", []))
        for cert in certifications:
            if cert.get("name") not in existing:
                merged.append(cert)
        profile["certifications"] = merged
        st.session_state.pop("pf_certifications_editor", None)

    education = detected.get("education", {}) or {}
    if education.get("level"):
        st.session_state["pf_edu_level"] = education["level"] if education["level"] in EDUCATION_LEVELS else ""
    if education.get("field"):
        st.session_state["pf_edu_field"] = education["field"] if education["field"] in STUDY_FIELDS else ""

    identity = detected.get("identity", {}) or {}
    for key, widget_key in [
        ("email", "pf_email"), ("phone", "pf_phone"), ("linkedin", "pf_linkedin"), ("location", "pf_location"),
    ]:
        if identity.get(key) and not st.session_state.get(widget_key):
            st.session_state[widget_key] = identity[key]

    storage.set_profile(profile)
    st.session_state.pf_cv_applied = True
    st.toast("Éléments ajoutés au profil. Vérifie les niveaux !", icon="✅")


def _apply_ai_cv() -> None:
    detected = st.session_state.get("pf_cv_detected") or {}
    raw = st.session_state.get("pf_cv_ai_raw") or {}
    if not raw:
        return
    skills = {}
    for name, level in (raw.get("skills") or {}).items():
        canonical = canonical_skill(name) or name
        try:
            skills[canonical] = max(1, min(5, int(level)))
        except (TypeError, ValueError):
            skills[canonical] = 3
    merged = copy.deepcopy(detected)
    merged.setdefault("skills", {})
    merged["skills"].update(skills)
    for key in ("languages", "education", "identity"):
        if raw.get(key):
            merged[key] = raw[key]
    if raw.get("certifications"):
        merged["certifications"] = raw["certifications"]
    st.session_state.pf_cv_detected = merged
    _apply_cv_detected()


def _render_identity_tab(profile: dict) -> None:
    identity = profile.get("identity", {})
    education = profile.get("education", {})

    st.markdown("##### Identité")
    col1, col2 = st.columns(2)
    with col1:
        ensure_key("pf_name", identity.get("name", ""))
        st.text_input("Nom complet", key="pf_name", placeholder="Léa Moreau")
        ensure_key("pf_headline", identity.get("headline", ""))
        st.text_input("Titre / accroche", key="pf_headline", placeholder="Étudiante en Master 1 Data & IA — recherche un stage Data Analyst")
    with col2:
        ensure_key("pf_email", identity.get("email", ""))
        st.text_input("E-mail", key="pf_email", placeholder="prenom.nom@email.fr")
        ensure_key("pf_location", identity.get("location", ""))
        st.text_input("Ville / mobilité", key="pf_location", placeholder="Paris, mobile en Île-de-France")

    col3, col4, col5 = st.columns([1, 1, 1])
    with col3:
        ensure_key("pf_phone", identity.get("phone", ""))
        st.text_input("Téléphone", key="pf_phone", placeholder="06 12 34 56 78")
    with col4:
        ensure_key("pf_linkedin", identity.get("linkedin", ""))
        st.text_input("LinkedIn", key="pf_linkedin", placeholder="linkedin.com/in/…")
    with col5:
        ensure_key("pf_portfolio", identity.get("portfolio", ""))
        st.text_input("Portfolio / GitHub", key="pf_portfolio", placeholder="github.com/…")

    ensure_key("pf_bio", identity.get("bio", ""))
    st.text_area(
        "Présentation en quelques lignes",
        key="pf_bio",
        height=110,
        placeholder="Ce que tu aimes faire, tes qualités, ce que tu cherches…",
    )

    st.markdown("##### Formation")
    col6, col7, col8 = st.columns([1.2, 1.3, 1])
    with col6:
        level_options = _selector_options(EDUCATION_LEVELS, education.get("level", ""))
        ensure_key("pf_edu_level", education.get("level", "") if education.get("level") in level_options else "")
        st.selectbox("Niveau d'études", options=level_options, key="pf_edu_level")
    with col7:
        field_options = _selector_options(STUDY_FIELDS, education.get("field", ""))
        ensure_key("pf_edu_field", education.get("field", "") if education.get("field") in field_options else "")
        st.selectbox("Filière", options=field_options, key="pf_edu_field")
    with col8:
        ensure_key("pf_edu_school", education.get("school", ""))
        st.text_input("Établissement", key="pf_edu_school", placeholder="Université Paris-Dauphine")
        ensure_key("pf_edu_year", education.get("grad_year", ""))
        st.text_input("Année d'obtention", key="pf_edu_year", placeholder="2027")

    target = get_target_job()
    if target:
        ui.note(
            f"🎯 <strong>Offre cible actuelle :</strong> {ui.esc(target.get('title',''))} — {ui.esc(target.get('company',''))}. "
            "Tu peux la changer depuis l'onglet « Offres »."
        )
    else:
        ui.note(
            "🎯 Aucune offre cible sélectionnée. Va dans <strong>Offres</strong> pour choisir un stage ou une alternance, "
            "ou colle une offre réelle."
        )


def _render_skills_tab(profile: dict) -> None:
    job = get_target_job()
    suggestions = [s for s in suggested_skills_for_job(job, limit=12) if s not in st.session_state.get("pf_skills_selected", [])]

    st.markdown("##### Compétences techniques")
    st.caption("Choisis tes compétences puis règle ton niveau honnêtement : c'est la base du score de compatibilité.")
    if suggestions:
        st.markdown(
            f"<div class='tm-card-sub' style='margin-bottom:.35rem'>Suggérées pour l'offre cible : {ui.chips(suggestions, tone='lime')}</div>",
            unsafe_allow_html=True,
        )
        st.button(
            "Ajouter les compétences suggérées",
            key="pf_add_suggestions",
            on_click=_add_skills,
            args=(suggestions,),
            icon="➕",
        )

    options = list(st.session_state.get("pf_skill_options", HARD_SKILLS))
    for skill in profile.get("skills", {}):
        if skill not in options:
            options.append(skill)
    st.session_state.pf_skill_options = options
    ensure_key("pf_skills_selected", [s for s in profile.get("skills", {}) if s in options])

    st.multiselect(
        "Tes compétences",
        options=options,
        key="pf_skills_selected",
        placeholder="Recherche une compétence (ex. SQL, Figma, Excel…)",
        help="Tape pour rechercher. Tu peux ajouter une compétence personnalisée juste en dessous.",
    )
    with st.expander("➕ Ajouter une compétence personnalisée"):
        st.text_input("Nom de la compétence", key="pf_custom_skill", placeholder="Ex. Notion, SolidWorks, community management…")
        st.button("Ajouter à ma liste", key="pf_add_custom", on_click=_add_custom_skill)

    selected = st.session_state.get("pf_skills_selected", [])
    if selected:
        grouped: dict[str, list[str]] = {}
        for skill in selected:
            category = SKILLS.get(skill, {}).get("category", "Autres")
            grouped.setdefault(category, []).append(skill)
        st.markdown("###### Règle tes niveaux")
        for category, skills in grouped.items():
            with st.expander(f"{category} · {len(skills)} compétence(s)", expanded=True):
                cols = st.columns(2)
                for index, skill in enumerate(sorted(skills)):
                    key = f"pf_level_{slugify(skill)}"
                    ensure_key(key, int(profile.get("skills", {}).get(skill, 3)))
                    with cols[index % 2]:
                        value = st.slider(skill, min_value=1, max_value=5, key=key)
                        st.caption(f"Niveau {value} · {SKILL_LEVELS.get(value, '')}")
    else:
        st.info("Sélectionne au moins 3 compétences pour obtenir un score pertinent.", icon="💡")

    st.markdown("##### Qualités professionnelles")
    st.caption("Communication, rigueur, autonomie… Les soft skills pèsent environ 15 % du score et sont souvent décisives en entretien.")
    ensure_key("pf_qualities", list(profile.get("qualities", [])))
    st.multiselect(
        "Tes qualités",
        options=SOFT_SKILLS,
        key="pf_qualities",
        placeholder="Choisis 3 à 6 qualités que tu peux prouver",
    )
    if job:
        required_qualities = [q["skill"] for q in job.get("qualities", [])]
        missing = [q for q in required_qualities if q not in st.session_state.get("pf_qualities", [])]
        if missing:
            ui.note(
                "⚠️ Cette offre attend aussi : " + ui.chips(missing, tone="amber") +
                " Si c'est vrai, ajoute-les et prépare une preuve concrète pour chacune."
            )


def _render_projects_tab(profile: dict) -> None:
    st.markdown("##### Projets")
    st.caption("Un projet bien raconté vaut mieux qu'une longue liste. Décris le problème, ton action et le résultat.")
    if "pf_projects" not in st.session_state:
        st.session_state.pf_projects = copy.deepcopy(profile.get("projects", []))

    for project in st.session_state.pf_projects:
        pid = project["id"]
        title = st.session_state.get(f"pf_proj_name_{pid}", project.get("name", "")) or "Nouveau projet"
        with st.expander(f"📁 {title}", expanded=False):
            col1, col2 = st.columns([1.4, 1])
            with col1:
                ensure_key(f"pf_proj_name_{pid}", project.get("name", ""))
                st.text_input("Nom du projet", key=f"pf_proj_name_{pid}")
            with col2:
                ensure_key(f"pf_proj_role_{pid}", project.get("role", ""))
                st.text_input("Rôle", key=f"pf_proj_role_{pid}", placeholder="Binôme, chef d'équipe…")
            ensure_key(f"pf_proj_desc_{pid}", project.get("description", ""))
            st.text_area(
                "Description (problème, action, résultat chiffré)",
                key=f"pf_proj_desc_{pid}",
                height=100,
            )
            tech_value = project.get("tech", [])
            if isinstance(tech_value, str):
                tech_value = [t.strip() for t in tech_value.split(",") if t.strip()]
            col3, col4 = st.columns([1.5, 1])
            with col3:
                st.multiselect(
                    "Technologies / compétences utilisées",
                    options=sorted(set(list(SKILLS.keys()) + tech_value)),
                    key=f"pf_proj_tech_{pid}",
                    default=tech_value,
                )
            with col4:
                ensure_key(f"pf_proj_link_{pid}", project.get("link", ""))
                st.text_input("Lien (GitHub, démo…)", key=f"pf_proj_link_{pid}")
            if st.button("Supprimer ce projet", key=f"pf_proj_del_{pid}", icon="🗑️"):
                st.session_state.pf_projects = [p for p in st.session_state.pf_projects if p["id"] != pid]
                st.rerun()

    if st.button("➕ Ajouter un projet", key="pf_add_project"):
        st.session_state.pf_projects.append({
            "id": uuid.uuid4().hex[:8], "name": "", "role": "", "description": "", "tech": [], "link": "",
        })
        st.rerun()

    st.markdown("##### Expériences & engagement")
    st.caption("Stages, jobs étudiants, associations, bénévolat : tout ce qui prouve tes compétences compte.")
    if "pf_experiences" not in st.session_state:
        st.session_state.pf_experiences = copy.deepcopy(profile.get("experiences", []))

    for experience in st.session_state.pf_experiences:
        eid = experience["id"]
        title = st.session_state.get(f"pf_exp_title_{eid}", experience.get("title", "")) or "Nouvelle expérience"
        with st.expander(f"💼 {title}", expanded=False):
            col1, col2 = st.columns([1.4, 1])
            with col1:
                ensure_key(f"pf_exp_title_{eid}", experience.get("title", ""))
                st.text_input("Poste / rôle", key=f"pf_exp_title_{eid}")
            with col2:
                ensure_key(f"pf_exp_company_{eid}", experience.get("company", ""))
                st.text_input("Structure", key=f"pf_exp_company_{eid}")
            ensure_key(f"pf_exp_period_{eid}", experience.get("period", ""))
            st.text_input("Période", key=f"pf_exp_period_{eid}", placeholder="Mars — Juin 2026")
            ensure_key(f"pf_exp_desc_{eid}", experience.get("description", ""))
            st.text_area("Missions et résultats", key=f"pf_exp_desc_{eid}", height=90)
            skills_value = experience.get("skills", [])
            if isinstance(skills_value, str):
                skills_value = [s.strip() for s in skills_value.split(",") if s.strip()]
            st.multiselect(
                "Compétences mises en œuvre",
                options=sorted(set(list(SKILLS.keys()) + skills_value)),
                key=f"pf_exp_skills_{eid}",
                default=skills_value,
            )
            if st.button("Supprimer cette expérience", key=f"pf_exp_del_{eid}", icon="🗑️"):
                st.session_state.pf_experiences = [e for e in st.session_state.pf_experiences if e["id"] != eid]
                st.rerun()

    if st.button("➕ Ajouter une expérience", key="pf_add_experience"):
        st.session_state.pf_experiences.append({
            "id": uuid.uuid4().hex[:8], "title": "", "company": "", "period": "", "description": "", "skills": [],
        })
        st.rerun()


def _render_languages_tab(profile: dict) -> None:
    st.markdown("##### Langues")
    st.caption("Indique ton niveau CECR réel. Un niveau B2 non prouvé vaut mieux qu'un C1 inventé : le recruteur testera.")
    language_rows = [{"Langue": name, "Niveau": level} for name, level in profile.get("languages", {}).items()]
    language_df = pd.DataFrame(language_rows, columns=["Langue", "Niveau"])
    language_options = sorted(set(LANGUAGE_OPTIONS + [row["Langue"] for row in language_rows if row["Langue"]]))
    st.data_editor(
        language_df,
        key="pf_languages_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Langue": st.column_config.SelectboxColumn("Langue", options=language_options, required=False),
            "Niveau": st.column_config.SelectboxColumn("Niveau", options=CEFR_LEVELS, required=False),
        },
    )

    st.markdown("##### Certifications")
    st.caption("Certifications obtenues ou en cours. Ajoute l'organisme et l'année pour crédibiliser.")
    cert_rows = [
        {
            "Certification": cert.get("name", ""),
            "Organisme": cert.get("issuer", ""),
            "Année": cert.get("year", ""),
            "Statut": cert.get("status", "Obtenue"),
        }
        for cert in profile.get("certifications", [])
    ]
    cert_df = pd.DataFrame(cert_rows, columns=["Certification", "Organisme", "Année", "Statut"])
    st.data_editor(
        cert_df,
        key="pf_certifications_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Statut": st.column_config.SelectboxColumn("Statut", options=CERT_STATUS, required=False),
            "Année": st.column_config.TextColumn("Année", max_chars=9, required=False),
        },
    )
    ui.note("📜 Une certification en cours montre déjà ta motivation : indique-la avec le statut « En cours ».")


def _render_cv_tab(profile: dict) -> None:
    st.markdown("##### Import du CV")
    st.caption("PDF, DOCX ou TXT — l'analyse se fait localement sur ta machine.")
    cv = profile.get("cv", {})
    ensure_key("pf_cv_text", cv.get("text", ""))
    ensure_key("pf_cv_filename", cv.get("filename", ""))
    ensure_key("pf_cv_hash", "")

    uploaded = st.file_uploader(
        "Dépose ton CV ici",
        type=["pdf", "docx", "txt"],
        key="pf_cv_upload",
        help="Taille maximale conseillée : 5 Mo. Le texte est extrait localement.",
    )
    if uploaded is not None:
        data = uploaded.getvalue()
        file_hash = hashlib.md5(data).hexdigest()
        if st.session_state.get("pf_cv_hash") != file_hash:
            with st.spinner("Lecture et analyse locale du CV…"):
                try:
                    text = extract_text(data, uploaded.name)
                    st.session_state.pf_cv_text = text
                    st.session_state.pf_cv_hash = file_hash
                    st.session_state.pf_cv_filename = uploaded.name
                    st.session_state.pf_cv_detected = detect_profile_updates(text)
                    st.session_state.pf_cv_audit = audit_cv(text)
                    st.toast("CV importé : compétences et éléments détectés.", icon="📄")
                except ValueError as exc:
                    st.error(str(exc))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_area(
            "Texte du CV (modifiable, ou colle-le directement)",
            key="pf_cv_text",
            height=220,
            placeholder="Colle ici le contenu de ton CV si l'import ne fonctionne pas…",
        )
    with col2:
        if st.session_state.get("pf_cv_filename"):
            st.markdown(
                f"<div class='tm-card tight'><div class='tm-card-title'>📄 {ui.esc(st.session_state.pf_cv_filename)}</div>"
                f"<div class='tm-card-sub'>{len(st.session_state.get('pf_cv_text',''))} caractères extraits</div></div>",
                unsafe_allow_html=True,
            )
        if st.button("Analyser les éléments du CV", icon="🔎", width="stretch", key="pf_detect_cv"):
            text = st.session_state.get("pf_cv_text", "")
            st.session_state.pf_cv_detected = detect_profile_updates(text)
            st.session_state.pf_cv_audit = audit_cv(text)
            st.toast("Éléments détectés dans le CV.", icon="🔎")
        if st.button("Supprimer le CV", icon="🗑️", width="stretch", key="pf_remove_cv"):
            st.session_state.pf_cv_text = ""
            st.session_state.pf_cv_filename = ""
            st.session_state.pf_cv_hash = ""
            st.session_state.pf_cv_detected = {}
            st.session_state.pf_cv_audit = {}
            profile["cv"] = {"filename": "", "text": "", "uploaded_at": ""}
            storage.set_profile(profile)
            st.rerun()

    # ------------------------------------------------------------------ #
    # Détections
    # ------------------------------------------------------------------ #
    detected = st.session_state.get("pf_cv_detected") or {}
    if detected:
        skills = detected.get("skills", {})
        qualities = detected.get("qualities", [])
        languages = detected.get("languages", {})
        certifications = detected.get("certifications", [])
        education = detected.get("education", {})
        sections = detected.get("sections", [])
        st.markdown("###### Ce que Tremplin a détecté")
        cols = st.columns(3)
        with cols[0]:
            st.markdown(
                f"<div class='tm-card tight'><div class='tm-card-title'>{len(skills)} compétences · {len(qualities)} qualités</div>"
                f"<div class='tm-card-sub'>{ui.chips(list(skills.keys())[:8], tone='green')}</div></div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            lang_text = " · ".join(f"{k} {v}" for k, v in languages.items()) or "Aucune détectée"
            st.markdown(
                f"<div class='tm-card tight'><div class='tm-card-title'>Langues</div>"
                f"<div class='tm-card-sub'>{ui.esc(lang_text)}</div></div>",
                unsafe_allow_html=True,
            )
        with cols[2]:
            cert_text = ", ".join(c.get("name", "") for c in certifications) or "Aucune détectée"
            st.markdown(
                f"<div class='tm-card tight'><div class='tm-card-title'>Certifications</div>"
                f"<div class='tm-card-sub'>{ui.esc(cert_text)}</div></div>",
                unsafe_allow_html=True,
            )
        if sections:
            st.caption("Sections repérées : " + " · ".join(sections))
        if education:
            st.caption(f"Formation détectée : {education.get('level','—')} — {education.get('field','—')}")

        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.button(
                "Ajouter ces éléments à mon profil",
                type="primary",
                icon="✅",
                width="stretch",
                key="pf_apply_cv",
                on_click=_apply_cv_detected,
            )
        with col_b:
            settings = resolve_settings(storage.get_ai_settings())
            if not settings.enabled:
                st.caption("Active l'IA dans Réglages pour une extraction encore plus fine (projets, expériences).")
            elif st.button("Extraction IA avancée du CV", icon="✨", width="stretch", key="pf_ai_cv"):
                with st.spinner(f"Extraction avec {settings.model}…"):
                    data, error = parse_cv_with_ai(
                        st.session_state.get("pf_cv_text", ""), HARD_SKILLS, settings
                    )
                if error:
                    st.error(f"Extraction IA impossible : {error}")
                else:
                    st.session_state.pf_cv_ai_raw = data
                    st.session_state.pf_apply_ai_pending = True
                    st.rerun()

    # ------------------------------------------------------------------ #
    # Audit du CV
    # ------------------------------------------------------------------ #
    audit = st.session_state.get("pf_cv_audit") or {}
    if not audit and st.session_state.get("pf_cv_text"):
        audit = audit_cv(st.session_state.pf_cv_text)
        st.session_state.pf_cv_audit = audit
    if audit:
        st.markdown("###### Audit de ton CV")
        col_score, col_checks = st.columns([1, 2.2], vertical_alignment="center")
        with col_score:
            st.markdown(ui.gauge(audit.get("score", 0), "qualité CV", size=136), unsafe_allow_html=True)
        with col_checks:
            rows = []
            for check in audit.get("checks", []):
                icon = "✅" if check["passed"] else "⚠️"
                rows.append(
                    f"<div class='tm-strength'><div class='mark'>{icon}</div><div>"
                    f"<div class='title'>{ui.esc(check['label'])}</div>"
                    f"<div class='detail'>{ui.esc(check.get('hint','')) if not check['passed'] else 'Validé'}</div>"
                    f"</div></div>"
                )
            st.markdown("".join(rows), unsafe_allow_html=True)
        for suggestion in audit.get("suggestions", []):
            st.caption(f"→ {suggestion}")

    ui.note(
        "🔒 <strong>Confidentialité :</strong> ton CV est analysé dans l'application. "
        "Il n'est envoyé à un fournisseur d'IA que si tu cliques explicitement sur « Extraction IA avancée »."
    )


def _sync_from_widgets() -> None:
    profile = storage.get_profile()
    identity = profile.setdefault("identity", {})
    for widget_key, field in [
        ("pf_name", "name"), ("pf_headline", "headline"), ("pf_email", "email"),
        ("pf_phone", "phone"), ("pf_location", "location"), ("pf_linkedin", "linkedin"),
        ("pf_portfolio", "portfolio"), ("pf_bio", "bio"),
    ]:
        if widget_key in st.session_state:
            identity[field] = st.session_state[widget_key]

    education = profile.setdefault("education", {})
    for widget_key, field in [
        ("pf_edu_level", "level"), ("pf_edu_field", "field"),
        ("pf_edu_school", "school"), ("pf_edu_year", "grad_year"),
    ]:
        if widget_key in st.session_state:
            education[field] = st.session_state[widget_key]

    selected = st.session_state.get("pf_skills_selected", [])
    skills: dict[str, int] = {}
    for skill in selected:
        key = f"pf_level_{slugify(skill)}"
        skills[skill] = int(st.session_state.get(key, 3))
    profile["skills"] = skills
    profile["qualities"] = list(st.session_state.get("pf_qualities", []))

    language_df = st.session_state.get("pf_languages_editor")
    if isinstance(language_df, pd.DataFrame):
        languages: dict[str, str] = {}
        for _, row in language_df.iterrows():
            name = str(row.get("Langue", "") or "").strip()
            level = str(row.get("Niveau", "") or "").strip()
            if name:
                languages[name] = level or "B2"
        profile["languages"] = languages

    cert_df = st.session_state.get("pf_certifications_editor")
    if isinstance(cert_df, pd.DataFrame):
        certifications = []
        for _, row in cert_df.iterrows():
            name = str(row.get("Certification", "") or "").strip()
            if not name:
                continue
            certifications.append({
                "name": name,
                "issuer": str(row.get("Organisme", "") or "").strip(),
                "year": str(row.get("Année", "") or "").strip(),
                "status": str(row.get("Statut", "Obtenue") or "Obtenue").strip(),
            })
        profile["certifications"] = certifications

    projects = []
    for project in st.session_state.get("pf_projects", []):
        pid = project["id"]
        projects.append({
            "id": pid,
            "name": st.session_state.get(f"pf_proj_name_{pid}", project.get("name", "")),
            "role": st.session_state.get(f"pf_proj_role_{pid}", project.get("role", "")),
            "description": st.session_state.get(f"pf_proj_desc_{pid}", project.get("description", "")),
            "tech": st.session_state.get(f"pf_proj_tech_{pid}", project.get("tech", [])),
            "link": st.session_state.get(f"pf_proj_link_{pid}", project.get("link", "")),
        })
    profile["projects"] = projects

    experiences = []
    for experience in st.session_state.get("pf_experiences", []):
        eid = experience["id"]
        experiences.append({
            "id": eid,
            "title": st.session_state.get(f"pf_exp_title_{eid}", experience.get("title", "")),
            "company": st.session_state.get(f"pf_exp_company_{eid}", experience.get("company", "")),
            "period": st.session_state.get(f"pf_exp_period_{eid}", experience.get("period", "")),
            "description": st.session_state.get(f"pf_exp_desc_{eid}", experience.get("description", "")),
            "skills": st.session_state.get(f"pf_exp_skills_{eid}", experience.get("skills", [])),
        })
    profile["experiences"] = experiences

    cv = profile.setdefault("cv", {})
    if "pf_cv_text" in st.session_state:
        cv["text"] = st.session_state.get("pf_cv_text", "")
    if "pf_cv_filename" in st.session_state:
        cv["filename"] = st.session_state.get("pf_cv_filename", "")
    if cv.get("text") and not cv.get("uploaded_at"):
        from datetime import datetime

        cv["uploaded_at"] = datetime.now().isoformat(timespec="seconds")

    data_hash = storage.profile_hash(profile)
    if data_hash != st.session_state.get("pf_last_hash"):
        touch(profile)
        storage.set_profile(profile)
        st.session_state.pf_last_hash = data_hash
    else:
        storage.set_profile(profile, persist=False)


def render() -> None:
    if st.session_state.pop("pf_apply_ai_pending", False):
        _apply_ai_cv()
        st.toast("Extraction IA appliquée au profil. Vérifie les niveaux !", icon="✨")

    profile = storage.get_profile()
    pct, detail = completion(profile)
    missing = [item["label"] for item in detail if not item["done"]]

    ui.section_header("Mon profil", "Le socle de ton analyse", "Plus ton profil est précis, plus ton score et ton plan sont fiables.")
    col1, col2 = st.columns([1.1, 2.4], vertical_alignment="center")
    with col1:
        st.markdown(ui.gauge(pct, "profil complété", size=150), unsafe_allow_html=True)
    with col2:
        if missing:
            st.markdown(
                "**À compléter en priorité :** " + ui.chips(missing, tone="amber", limit=6),
                unsafe_allow_html=True,
            )
        else:
            ui.note("✅ Profil complet : tu peux lancer une analyse en toute confiance.")
        st.caption("💾 Enregistrement automatique après chaque modification.")

    tab_identity, tab_skills, tab_projects, tab_languages, tab_cv = st.tabs([
        "👤 Identité & formation",
        "🧠 Compétences",
        "📁 Projets & expériences",
        "🌍 Langues & certifications",
        "📄 Mon CV",
    ])
    with tab_identity:
        _render_identity_tab(profile)
    with tab_skills:
        _render_skills_tab(profile)
    with tab_projects:
        _render_projects_tab(profile)
    with tab_languages:
        _render_languages_tab(profile)
    with tab_cv:
        _render_cv_tab(profile)

    _sync_from_widgets()

    st.write("")
    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        if st.button("Choisir une offre", type="primary", width="stretch", key="profile_go_jobs", icon="🎯"):
            nav_to("jobs")
    with col_b:
        if storage.get_analyses() and st.button("Voir mon analyse", width="stretch", key="profile_go_analysis", icon="📊"):
            nav_to("analysis")
