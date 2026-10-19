"""Page Réglages : IA générative optionnelle, données locales et méthode."""

from __future__ import annotations

import json

import streamlit as st

from .. import llm, storage, ui
from ..matching import DOMAIN_WEIGHTS, VERDICTS
from ..data_skills import EDUCATION_LEVELS
from .common import nav_to, profile_mini_card


def _provider_changed() -> None:
    preset = llm.PROVIDER_PRESETS.get(st.session_state.get("set_provider"), {})
    st.session_state["set_base_url"] = preset.get("base_url", "")
    st.session_state["set_model"] = preset.get("model", "")


def _render_ai_tab() -> None:
    settings = storage.get_ai_settings()
    providers = list(llm.PROVIDER_PRESETS.keys())
    if "set_provider" not in st.session_state:
        st.session_state["set_provider"] = settings.get("provider", "local")
        st.session_state["set_base_url"] = settings.get("base_url", "")
        st.session_state["set_model"] = settings.get("model", "")
    st.session_state.setdefault("set_api_key", settings.get("api_key", ""))

    with st.container(border=True):
        st.markdown('<div class="tm-card-title">Fournisseur</div>', unsafe_allow_html=True)
        provider = st.selectbox(
            "Fournisseur d'IA",
            options=providers,
            format_func=lambda key: llm.PROVIDER_PRESETS[key]["label"],
            key="set_provider",
            on_change=_provider_changed,
        )
        preset = llm.PROVIDER_PRESETS[provider]
        st.caption(preset.get("help", ""))

        if provider != "local":
            col1, col2 = st.columns(2)
            with col1:
                base_url = st.text_input("URL de base (compatible OpenAI)", key="set_base_url", placeholder="https://api.exemple.com/v1")
            with col2:
                model = st.text_input("Modèle", key="set_model", placeholder="ex. : mistral-small-latest")
            api_key = st.text_input(
                "Clé API (jamais écrite sur le disque)",
                key="set_api_key",
                type="password",
                placeholder="Colle ta clé ici — elle reste dans cette session",
            )
        else:
            base_url, model, api_key = "", "", ""
            ui.note("🌿 <strong>Moteur local actif :</strong> tout fonctionne hors ligne. Active l'IA seulement si tu veux un récit personnalisé et un pitch.")

        col_a, col_b, col_c = st.columns([1.2, 1, 1.4])
        with col_a:
            if st.button("💾 Enregistrer la configuration", type="primary", width="stretch", key="set_save_ai"):
                storage.update_ai_settings(provider=provider, base_url=base_url, model=model)
                storage.update_ai_settings(api_key=api_key)  # session uniquement
                st.toast("Configuration enregistrée (sans la clé sur le disque).", icon="💾")
        with col_b:
            if st.button("🔌 Tester la connexion", width="stretch", key="set_test_ai"):
                if api_key:
                    test_settings = llm.AISettings(provider=provider, base_url=base_url, model=model, api_key=api_key)
                else:
                    test_settings = llm.resolve_settings({"provider": provider, "base_url": base_url, "model": model})
                with st.spinner("Test en cours…"):
                    ok, message = llm.test_connection(test_settings)
                if ok:
                    st.success(message, icon="✅")
                else:
                    st.error(message, icon="⚠️")

    env_providers = llm.env_available_providers()
    key_providers = [provider for provider in env_providers if provider != "ollama"]
    if key_providers:
        names = ", ".join(llm.PROVIDER_PRESETS[p]["label"] for p in key_providers)
        ui.note(f"🔑 <strong>Clés détectées dans l'environnement :</strong> {ui.esc(names)}. Elles seront utilisées automatiquement si le champ reste vide.")
    ui.note(
        "🦙 <strong>Ollama (local) :</strong> aucune clé ni connexion internet. Lance <code>ollama serve</code> puis choisis le fournisseur "
        "« Ollama » avec un modèle installé (ex. <code>llama3.1</code>) — tes données ne quittent pas ta machine."
    )

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="tm-card-title">Quand utiliser l\'IA ?</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="tm-card-sub" style="line-height:1.7">
              Le <strong>moteur local</strong> calcule toujours le score, les lacunes et le plan — l'IA ne modifie jamais les notes.<br>
              L'<strong>IA générative</strong> sert seulement à : raconter ton profil avec plus de finesse, proposer des questions d'entretien probables, et rédiger un pitch de candidature.<br>
              Aucune donnée médicale ou sensible n'est demandée : ni date de naissance, ni adresse, ni numéro de sécurité sociale.
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_data_tab() -> None:
    profile = storage.get_profile()
    left, right = st.columns([1, 1.4], gap="large")

    with left:
        st.markdown('<div class="tm-eyebrow">Ton profil</div>', unsafe_allow_html=True)
        st.markdown(profile_mini_card(), unsafe_allow_html=True)
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Modifier", width="stretch", key="set_edit_profile"):
                nav_to("profile")
        with col2:
            if st.button("🎓 Charger le profil démo", width="stretch", key="set_demo"):
                from .profile_page import clear_profile_widgets

                storage.reset_profile(use_demo=True)
                clear_profile_widgets()
                st.toast("Profil de démonstration chargé.", icon="🎓")
                nav_to("dashboard")

    with right:
        st.markdown('<div class="tm-eyebrow">Sauvegarde locale</div>', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="tm-card">
                  <div style="font-size:.86rem;color:#2E3A35;line-height:1.6">
                    Profil, analyses et progression du plan sont enregistrés dans<br>
                    <code style="background:#F2F0E8;padding:.15rem .4rem;border-radius:8px">{ui.esc(str(storage.STATE_FILE))}</code><br>
                    Aucun compte, aucun serveur : tout reste sur ta machine.
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )
        st.write("")
        export = storage.export_state()
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Exporter mes données (JSON)",
                export,
                file_name="tremplin-donnees.json",
                mime="application/json",
                width="stretch",
                key="set_export",
            )
        with col2:
            uploaded = st.file_uploader("Importer une sauvegarde", type=["json"], key="set_import_file", label_visibility="collapsed")
        if uploaded is not None:
            try:
                payload = json.loads(uploaded.read().decode("utf-8"))
                if st.button("Confirmer l'import (remplace les données actuelles)", type="primary", key="set_import_confirm"):
                    storage.import_state(payload)
                    from .profile_page import clear_profile_widgets

                    clear_profile_widgets()
                    st.toast("Sauvegarde importée.", icon="📥")
                    nav_to("dashboard")
            except (json.JSONDecodeError, UnicodeDecodeError):
                st.error("Fichier illisible : vérifie qu'il s'agit d'un export Tremplin (.json).", icon="⚠️")

    st.divider()
    st.markdown('<div class="tm-eyebrow">Zone sensible</div>', unsafe_allow_html=True)
    confirm = st.checkbox("Je comprends que ces actions sont définitives.", key="set_danger_confirm")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Effacer le profil", disabled=not confirm, width="stretch", key="set_reset_profile"):
            from .profile_page import clear_profile_widgets

            storage.reset_profile(use_demo=False)
            clear_profile_widgets()
            st.toast("Profil effacé.", icon="🗑️")
            nav_to("dashboard")
    with col2:
        if st.button("🧹 Effacer les analyses", disabled=not confirm, width="stretch", key="set_reset_analyses"):
            storage.clear_analyses()
            st.toast("Historique d'analyses effacé.", icon="🧹")
            st.rerun()
    with col3:
        if st.button("💥 Tout réinitialiser", disabled=not confirm, width="stretch", key="set_reset_all"):
            from .profile_page import clear_profile_widgets

            storage.reset_all()
            clear_profile_widgets()
            st.toast("Application réinitialisée.", icon="💥")
            nav_to("dashboard")


def _render_method_tab() -> None:
    st.markdown(
        """
        <div class="tm-card">
          <div class="tm-card-title">Comment le score est calculé</div>
          <div class="tm-card-sub" style="line-height:1.75">
            Chaque offre est décodée en exigences : compétences (avec niveau attendu et importance),
            qualités, langues, formation et certifications. Ton profil est comparé exigence par exigence,
            en tenant compte du <strong>CV importé</strong>, des <strong>projets</strong> et des <strong>expériences</strong>
            qui prouvent tes compétences — déclarer ne suffit pas.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    cols = st.columns(5)
    subs = [
        ("Compétences", "Couverture des compétences demandées, pondérée par leur importance."),
        ("Qualités", "Preuves de rigueur, communication, autonomie… dans tes expériences et projets."),
        ("Projets & expérience", "Pertinence de tes projets par rapport aux compétences de l'offre."),
        ("Langues", "Niveau CECR comparé à l'exigence (ex. B2)."),
        ("Formation & certifications", "Niveau de diplôme, filière et certifications appréciées."),
    ]
    for col, (title, text) in zip(cols, subs):
        with col:
            st.markdown(
                f"""<div class="tm-card" style="height:100%">
                      <div class="tm-card-title" style="font-size:.9rem">{title}</div>
                      <div class="tm-card-sub">{text}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

    st.write("")
    with st.expander("Pondérations par domaine"):
        rows = []
        for domain, weights in DOMAIN_WEIGHTS.items():
            rows.append(
                f"<tr><td style='padding:.3rem .5rem'>{ui.esc(domain)}</td>"
                f"<td style='padding:.3rem .5rem'>{weights['skills']*100:.0f}%</td>"
                f"<td style='padding:.3rem .5rem'>{weights['qualities']*100:.0f}%</td>"
                f"<td style='padding:.3rem .5rem'>{weights['portfolio']*100:.0f}%</td>"
                f"<td style='padding:.3rem .5rem'>{weights['languages']*100:.0f}%</td>"
                f"<td style='padding:.3rem .5rem'>{weights['formation']*100:.0f}%</td></tr>"
            )
        st.markdown(
            f"""<table style="width:100%;border-collapse:collapse;font-size:.85rem">
                  <thead><tr style="text-align:left;color:#6E7B76;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em">
                    <th style="padding:.3rem .5rem">Domaine</th><th>Compétences</th><th>Qualités</th>
                    <th>Projets</th><th>Langues</th><th>Formation</th></tr></thead>
                  <tbody>{''.join(rows)}</tbody>
                </table>""",
            unsafe_allow_html=True,
        )
        st.caption("Les autres domaines utilisent une pondération équilibrée : 40 / 15 / 20 / 10 / 15.")

    with st.expander("Seuils d'interprétation"):
        for threshold, label, tone, message in VERDICTS:
            st.markdown(f"**{threshold}+ · {label}** — {message}")

    with st.expander("Niveaux de formation et d'étude"):
        st.markdown(" · ".join(EDUCATION_LEVELS))
        st.caption("Le moteur compare ton niveau réellement renseigné au niveau minimum demandé, sans pénaliser une filière proche (une licence informatique vaut mieux qu'une filière éloignée pour un poste tech).")

    with st.expander("Confidentialité"):
        st.markdown(
            "• Profil, analyses et progression : uniquement dans `data/state.json` sur ta machine.\n\n"
            "• IA désactivée par défaut : aucune requête réseau pour le calcul du score.\n\n"
            "• Si tu actives une IA, seuls le résumé de ton profil et l'analyse nécessaire sont transmis au fournisseur choisi, jamais ton CV brut ni ta clé API sur le disque.\n\n"
            "• Tu peux exporter ou supprimer toutes tes données depuis l'onglet « Données »."
        )


def render() -> None:
    ui.hero(
        badge="Réglages",
        title_html="Ton espace,<br><em>tes règles.</em>",
        subtitle="IA optionnelle, données locales et transparence complète sur le calcul du score.",
        points=["IA désactivée par défaut", "Données 100 % locales", "Méthode expliquée"],
    )
    st.write("")

    tab_ai, tab_data, tab_method = st.tabs(["🤖 Intelligence artificielle", "💾 Données & confidentialité", "📐 Méthode & score"])
    with tab_ai:
        _render_ai_tab()
    with tab_data:
        _render_data_tab()
    with tab_method:
        _render_method_tab()
