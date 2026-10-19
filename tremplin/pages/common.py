"""Helpers partagés par les pages Streamlit."""

from __future__ import annotations

import copy
import re

import streamlit as st

from .. import storage
from ..data_jobs import JOBS, get_job
from ..data_skills import SKILLS
from ..profile import completion, ensure_shape


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-") or "item"


def nav_to(page: str, **state) -> None:
    st.session_state.page = page
    for key, value in state.items():
        st.session_state[key] = value
    st.rerun()


def ensure_key(key: str, value) -> None:
    if key not in st.session_state:
        st.session_state[key] = value


def get_target_job() -> dict | None:
    """Récupère l'offre actuellement ciblée (catalogue ou personnalisée)."""
    profile = storage.get_profile()
    custom = st.session_state.get("custom_job")
    target = profile.get("target", {})
    if target.get("type") == "custom" and custom:
        return custom
    job_id = st.session_state.get("selected_job_id") or target.get("job_id")
    if target.get("type") == "custom" and target.get("custom_job"):
        return target["custom_job"]
    if job_id:
        job = get_job(job_id)
        if job:
            return job
    if custom:
        return custom
    return None


def set_target_job(job: dict, custom: bool = False) -> None:
    profile = storage.get_profile()
    profile["target"] = {
        "type": "custom" if custom else "catalog",
        "job_id": job.get("id", ""),
        "custom_job": copy.deepcopy(job) if custom else None,
    }
    storage.set_profile(profile)
    st.session_state.selected_job_id = job.get("id", "")


def profile_mini_card() -> str:
    profile = storage.get_profile()
    pct, _ = completion(profile)
    identity = profile.get("identity", {})
    name = identity.get("name") or "Profil à compléter"
    headline = identity.get("headline") or "Ajoute ton parcours pour un score fiable."
    return f"""
    <div style="padding:.75rem .85rem;border-radius:16px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10)">
      <div style="font-weight:800;color:#F3F8F4;font-size:.92rem">{name}</div>
      <div style="color:#B9CCC2;font-size:.76rem;margin:.15rem 0 .5rem;line-height:1.35">{headline[:90]}</div>
      <div style="height:7px;border-radius:999px;background:rgba(255,255,255,.14);overflow:hidden">
        <div style="width:{pct}%;height:100%;border-radius:999px;background:#D9F55C"></div>
      </div>
      <div style="display:flex;justify-content:space-between;color:#C8D6CF;font-size:.72rem;margin-top:.35rem">
        <span>Profil complété</span><strong style="color:#D9F55C">{pct}%</strong>
      </div>
    </div>
    """


def suggested_skills_for_job(job: dict | None, limit: int = 10) -> list[str]:
    if not job:
        return []
    required = [r["skill"] for r in job.get("required_skills", [])]
    nice = list(job.get("nice_to_have", []))
    return list(dict.fromkeys(required + nice))[:limit]


def job_label(job: dict) -> str:
    return f"{job.get('title','Offre')} — {job.get('company','')}".strip(" —")


def analyses_as_options() -> dict[str, str]:
    options: dict[str, str] = {}
    for analysis in storage.get_analyses():
        label = f"{analysis.get('job_title','Offre')} · {analysis.get('score','?')}/100 · {analysis.get('created_at','')[:10]}"
        options[analysis.get("id", "")] = label
    return options


def clone_profile() -> dict:
    return copy.deepcopy(storage.get_profile())


def require_profile(min_skills: int = 1, min_completion: int = 15) -> bool:
    profile = storage.get_profile()
    pct, _ = completion(profile)
    if pct < min_completion or len(profile.get("skills", {})) < min_skills:
        st.warning(
            "Ton profil est encore trop léger pour une analyse fiable. "
            "Ajoute au moins quelques compétences et ta formation pour commencer.",
            icon="🌱",
        )
        if st.button("Compléter mon profil", type="primary", key="require_profile_btn"):
            nav_to("profile")
        return False
    return True
