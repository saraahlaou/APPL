"""Persistance locale de l'état de l'application (JSON).

Le fichier `data/state.json` contient le profil, l'historique des analyses,
l'avancement du plan et les préférences (hors clé API). Il est créé
automatiquement au premier lancement.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from .profile import demo_profile, ensure_shape, new_profile

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STATE_FILE = DATA_DIR / "state.json"

STATE_VERSION = 2
MAX_ANALYSES = 30


def _empty_state() -> dict:
    return {
        "version": STATE_VERSION,
        "profile": new_profile(),
        "analyses": [],
        "plan_progress": {},
        "ai_settings": {"provider": "local", "base_url": "", "model": ""},
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def load_state() -> dict:
    if not STATE_FILE.exists():
        return _empty_state()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _empty_state()
    state = _empty_state()
    state.update(data)
    state["profile"] = ensure_shape(state.get("profile") or {})
    state["analyses"] = state.get("analyses") or []
    state["plan_progress"] = state.get("plan_progress") or {}
    state["ai_settings"] = state.get("ai_settings") or {"provider": "local", "base_url": "", "model": ""}
    return state


def save_state() -> None:
    """Écrit l'état courant de la session dans le fichier JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state = {
        "version": STATE_VERSION,
        "profile": st.session_state.get("profile", new_profile()),
        "analyses": st.session_state.get("analyses", []),
        "plan_progress": st.session_state.get("plan_progress", {}),
        "ai_settings": st.session_state.get("ai_settings", {"provider": "local", "base_url": "", "model": ""}),
        "created_at": st.session_state.get("state_created_at", datetime.now().isoformat(timespec="seconds")),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(DATA_DIR), prefix="state-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, STATE_FILE)
    except OSError:
        # En cas de souci d'écriture, l'applicationcontinue de fonctionner en session.
        pass


def init_state() -> None:
    if "state_loaded" in st.session_state:
        return
    state = load_state()
    st.session_state.profile = state["profile"]
    st.session_state.analyses = state["analyses"]
    st.session_state.plan_progress = state["plan_progress"]
    st.session_state.ai_settings = {**state["ai_settings"], "api_key": ""}
    st.session_state.state_created_at = state.get("created_at", "")
    st.session_state.state_loaded = True
    st.session_state.setdefault("page", "dashboard")
    st.session_state.setdefault("selected_job_id", st.session_state.profile.get("target", {}).get("job_id", ""))
    st.session_state.setdefault("current_analysis_id", None)


def get_profile() -> dict:
    return ensure_shape(st.session_state.get("profile", new_profile()))


def set_profile(profile: dict, persist: bool = True) -> None:
    st.session_state.profile = ensure_shape(profile)
    if persist:
        save_state()


def reset_profile(use_demo: bool = False) -> None:
    st.session_state.profile = demo_profile() if use_demo else new_profile()
    st.session_state.selected_job_id = st.session_state.profile.get("target", {}).get("job_id", "")
    st.session_state.current_analysis_id = None
    save_state()


def add_analysis(result: dict) -> None:
    analyses = st.session_state.get("analyses", [])
    # Évite les doublons stricts (même offre + même score + même profil)
    signature = (result.get("job_id"), result.get("score"), result.get("profile_hash"))
    analyses = [a for a in analyses if (a.get("job_id"), a.get("score"), a.get("profile_hash")) != signature]
    analyses.insert(0, result)
    st.session_state.analyses = analyses[:MAX_ANALYSES]
    st.session_state.current_analysis_id = result.get("id")
    save_state()


def get_analyses() -> list[dict]:
    return st.session_state.get("analyses", [])


def get_analysis(analysis_id: str | None) -> dict | None:
    if not analysis_id:
        return None
    for analysis in get_analyses():
        if analysis.get("id") == analysis_id:
            return analysis
    return None


def delete_analysis(analysis_id: str) -> None:
    st.session_state.analyses = [a for a in get_analyses() if a.get("id") != analysis_id]
    save_state()


def clear_analyses() -> None:
    st.session_state.analyses = []
    st.session_state.current_analysis_id = None
    save_state()


def profile_hash(profile: dict) -> str:
    payload = json.dumps(profile, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def get_plan_progress() -> dict:
    return st.session_state.setdefault("plan_progress", {})


def set_action_done(analysis_id: str, action_id: str, done: bool) -> None:
    progress = get_plan_progress()
    progress[f"{analysis_id}:{action_id}"] = bool(done)
    save_state()


def is_action_done(analysis_id: str, action_id: str) -> bool:
    return bool(get_plan_progress().get(f"{analysis_id}:{action_id}", False))


def plan_completion(analysis: dict) -> tuple[int, int]:
    phases = (analysis.get("plan") or {}).get("phases", [])
    actions = [action for phase in phases for action in phase.get("actions", [])]
    if not actions:
        return 0, 0
    done = sum(1 for action in actions if is_action_done(analysis.get("id", ""), action["id"]))
    return done, len(actions)


def get_ai_settings() -> dict:
    settings = st.session_state.setdefault("ai_settings", {"provider": "local", "base_url": "", "model": "", "api_key": ""})
    settings.setdefault("api_key", "")
    return settings


def update_ai_settings(**kwargs) -> None:
    settings = get_ai_settings()
    settings.update(kwargs)
    st.session_state.ai_settings = settings
    if "api_key" not in kwargs:
        save_state()


def export_state() -> str:
    export = {
        "profile": copy.deepcopy(st.session_state.get("profile", {})),
        "analyses": st.session_state.get("analyses", []),
        "plan_progress": st.session_state.get("plan_progress", {}),
        "exported_at": datetime.now().isoformat(timespec="seconds"),
    }
    return json.dumps(export, ensure_ascii=False, indent=2)


def import_state(payload: dict) -> None:
    st.session_state.profile = ensure_shape(payload.get("profile") or new_profile())
    st.session_state.analyses = payload.get("analyses") or []
    st.session_state.plan_progress = payload.get("plan_progress") or {}
    st.session_state.current_analysis_id = None
    st.session_state.selected_job_id = st.session_state.profile.get("target", {}).get("job_id", "")
    save_state()


def reset_all() -> None:
    st.session_state.profile = new_profile()
    st.session_state.analyses = []
    st.session_state.plan_progress = {}
    st.session_state.ai_settings = {"provider": "local", "base_url": "", "model": "", "api_key": ""}
    st.session_state.current_analysis_id = None
    st.session_state.selected_job_id = ""
    save_state()
