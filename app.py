"""Tremplin — trouve le stage où ton profil fait la différence.

Lancement :  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Tremplin — ton profil face aux offres",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

from tremplin import llm, storage, ui  # noqa: E402
from tremplin.pages import analysis, dashboard, jobs, plan, profile_page, settings  # noqa: E402
from tremplin.pages.common import nav_to, profile_mini_card  # noqa: E402

NAV_ITEMS = [
    ("dashboard", "Tableau de bord", "🏠"),
    ("profile", "Mon profil", "👤"),
    ("jobs", "Offres & cibles", "🎯"),
    ("analysis", "Analyse", "📊"),
    ("plan", "Plan d'action", "🗺️"),
    ("settings", "Réglages", "⚙️"),
]

PAGES = {
    "dashboard": dashboard.render,
    "profile": profile_page.render,
    "jobs": jobs.render,
    "analysis": analysis.render,
    "plan": plan.render,
    "settings": settings.render,
}


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="tm-brand">
              <div class="tm-logo">🌱</div>
              <div>
                <div class="tm-brand-name">Tremplin</div>
                <div class="tm-brand-tag">Ton avenir, calculé juste</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ai_settings = llm.resolve_settings(st.session_state.get("ai_settings"))
        if ai_settings.enabled:
            status = f'<span class="tm-ai-state on">● IA active · {ui.esc(ai_settings.model)}</span>'
        else:
            status = '<span class="tm-ai-state">● Moteur local — 100 % hors ligne</span>'
        st.markdown(status, unsafe_allow_html=True)
        st.write("")

        current = st.session_state.get("page", "dashboard")
        for key, label, icon in NAV_ITEMS:
            if st.button(
                label,
                key=f"nav_{key}",
                icon=icon,
                type="primary" if key == current else "secondary",
                width="stretch",
            ):
                if key != current:
                    nav_to(key)

        st.divider()
        st.markdown(profile_mini_card(), unsafe_allow_html=True)
        st.write("")
        if st.button("＋ Nouvelle analyse", key="nav_new_analysis", icon="🚀", width="stretch"):
            nav_to("jobs")

        st.markdown(
            """
            <div class="tm-side-foot">
              Données stockées <strong>localement</strong>.<br>
              Aucun compte requis · IA optionnelle.
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    storage.init_state()
    ui.inject_css()
    _render_sidebar()

    page = st.session_state.get("page", "dashboard")
    render = PAGES.get(page, dashboard.render)
    render()


if __name__ == "__main__":
    main()
