"""Connecteur IA générative optionnel (compatible OpenAI).

Trois modes :
- « local » : aucune requête réseau, le moteur déterministe suffit ;
- « OpenAI-compatible » : OpenAI, Mistral, Groq, OpenRouter, Gemini, Ollama… ;
- « custom » : n'importe quelle API /chat/completions compatible.

La clé API n'est jamais écrite sur le disque : elle reste en session ou dans
les variables d'environnement.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import requests

TIMEOUT = 75

PROVIDER_PRESETS: dict[str, dict] = {
    "local": {
        "label": "Moteur local (sans IA générative)",
        "base_url": "",
        "model": "",
        "key_env": "",
        "needs_key": False,
        "help": "Analyse déterministe, 100 % hors ligne. Le plan et les conseils sont générés par Tremplin.",
    },
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_env": "OPENAI_API_KEY",
        "needs_key": True,
        "help": "Clé créée sur platform.openai.com. Modèle rapide et économique.",
    },
    "mistral": {
        "label": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-small-latest",
        "key_env": "MISTRAL_API_KEY",
        "needs_key": True,
        "help": "Très bon rapport qualité / prix pour le français.",
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "key_env": "GROQ_API_KEY",
        "needs_key": True,
        "help": "Inférence très rapide, idéale pour les démonstrations.",
    },
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "key_env": "OPENROUTER_API_KEY",
        "needs_key": True,
        "help": "Accès à de nombreux modèles via une seule clé.",
    },
    "gemini": {
        "label": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.0-flash",
        "key_env": "GEMINI_API_KEY",
        "needs_key": True,
        "help": "API compatible OpenAI exposée par Google AI Studio.",
    },
    "ollama": {
        "label": "Ollama (local, sans clé)",
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2",
        "key_env": "",
        "needs_key": False,
        "help": "Modèle exécuté sur ta machine. Aucune donnée ne quitte ton ordinateur.",
    },
    "custom": {
        "label": "API personnalisée (compatible OpenAI)",
        "base_url": "",
        "model": "",
        "key_env": "CUSTOM_API_KEY",
        "needs_key": True,
        "help": "Renseigne une URL de base qui expose /chat/completions.",
    },
}


@dataclass
class AISettings:
    provider: str = "local"
    base_url: str = ""
    model: str = ""
    api_key: str = ""
    extra_headers: dict = field(default_factory=dict)

    @property
    def enabled(self) -> bool:
        return self.provider not in ("", "local") and bool(self.base_url and self.model)

    def describe(self) -> str:
        if not self.enabled:
            return "Moteur local"
        label = PROVIDER_PRESETS.get(self.provider, {}).get("label", self.provider)
        return f"IA · {label} · {self.model}"


def resolve_settings(session_settings: dict | None = None) -> AISettings:
    """Résout la configuration depuis la session, puis les variables d'environnement."""
    session_settings = session_settings or {}
    provider = session_settings.get("provider", "local") or "local"
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["local"])
    base_url = session_settings.get("base_url") or preset.get("base_url", "")
    model = session_settings.get("model") or preset.get("model", "")
    api_key = session_settings.get("api_key", "")
    key_env = preset.get("key_env", "")
    if not api_key and key_env:
        api_key = os.environ.get(key_env, "")
    return AISettings(provider=provider, base_url=base_url, model=model, api_key=api_key)


def env_available_providers() -> list[str]:
    available = []
    for key, preset in PROVIDER_PRESETS.items():
        if key in ("local", "custom"):
            continue
        env_name = preset.get("key_env")
        if env_name and os.environ.get(env_name):
            available.append(key)
        elif key == "ollama":
            available.append(key)
    return available


def _extract_json(text: str) -> dict | None:
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None


def chat_json(system_prompt: str, user_prompt: str, settings: AISettings) -> tuple[dict | None, str]:
    """Appelle l'API et retourne (json, erreur lisible)."""
    if not settings.enabled:
        return None, "Aucun fournisseur IA configuré."
    headers = {"Content-Type": "application/json"}
    if settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"
    headers.update(settings.extra_headers or {})
    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.35,
    }
    try:
        response = requests.post(
            f"{settings.base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return None, f"Connexion impossible : {exc}"

    if response.status_code >= 400:
        detail = response.text[:300]
        return None, f"Erreur {response.status_code} : {detail}"

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        return None, f"Réponse inattendue du fournisseur ({exc})."

    parsed = _extract_json(content)
    if parsed is None:
        return None, "Le modèle n'a pas renvoyé de JSON exploitable."
    return parsed, ""


def test_connection(settings: AISettings) -> tuple[bool, str]:
    if not settings.enabled:
        return False, "Configure un fournisseur et une clé API pour tester."
    parsed, error = chat_json(
        "Tu réponds uniquement en JSON strict.",
        'Réponds exactement avec ce JSON : {"status":"ok"}',
        settings,
    )
    if error:
        return False, error
    if parsed and str(parsed.get("status", "")).lower() == "ok":
        return True, f"Connexion réussie avec {settings.model}."
    return True, "Connexion établie (réponse non standard, mais l'API répond)."


# --------------------------------------------------------------------------- #
# Prompts métier
# --------------------------------------------------------------------------- #

ENRICH_SYSTEM = (
    "Tu es un coach carrière français, bienveillant, honnête et très concret. "
    "Tu aides des étudiants à comprendre leur compatibilité avec une offre et à progresser. "
    "Tu ne changes jamais un score : tu commentes uniquement les faits fournis. "
    "Tu réponds en JSON strict, en français, sans texte autour."
)

ENRICH_SCHEMA = """{
  "narrative": "3 à 4 phrases qui résument la situation, sans flatterie",
  "watchouts": [{"title": "titre court", "detail": "pourquoi c'est un frein et comment y répondre"}],
  "cv_tips": ["conseil CV spécifique à cette offre"],
  "interview_tips": ["conseil entretien spécifique, question possible + angle de réponse"],
  "plan_focus": [{"horizon": "7 jours", "title": "action", "detail": "comment la réaliser"}]",
  "pitch": "2 phrases de pitch de candidature à l'oral"
}"""


def enrich_analysis_with_ai(result: dict, profile: dict, job: dict, settings: AISettings) -> tuple[dict | None, str]:
    """Demande à l'IA un récit, des conseils et des points de vigilance."""
    strengths = [f"{s['title']} — {s['detail']}" for s in result.get("strengths", [])[:6]]
    gaps = [f"{g['title']} ({g['severity']}, impact {g['impact_points']} pts) : {g['why']}" for g in result.get("gaps", [])[:6]]
    skills = [
        f"{d['skill']} : actuel {d['current_label']} / attendu {d['required_label']} ({d['source']})"
        for d in result.get("skills_detail", [])
    ]
    prompt = f"""
OFFRE
Titre : {job.get('title')}
Entreprise : {job.get('company')} ({job.get('company_type')})
Contrat : {job.get('contract')} — {job.get('duration')} — {job.get('location')}
Missions : {' | '.join(job.get('missions', [])[:5])}
Compétences attendues : {', '.join(f"{r['skill']} (niveau {r['level']}/5)" for r in job.get('required_skills', []))}
Qualités attendues : {', '.join(q['skill'] for q in job.get('qualities', []))}

PROFIL DE L'ÉTUDIANT
Titre : {profile.get('identity', {}).get('headline', '')}
Formation : {profile.get('education', {}).get('level', '')} — {profile.get('education', {}).get('field', '')}
Compétences déclarées : {', '.join(f"{k} ({v}/5)" for k, v in profile.get('skills', {}).items())}
Qualités déclarées : {', '.join(profile.get('qualities', []))}
Langues : {', '.join(f"{k} {v}" for k, v in profile.get('languages', {}).items())}
Projets : {len(profile.get('projects', []))} · Expériences : {len(profile.get('experiences', []))}

ANALYSE CALCULÉE PAR LE MOTEUR (ne pas modifier)
Score global : {result.get('score')}/100 ({result.get('verdict', {}).get('label')})
Sous-scores : {result.get('subscores')}
Points forts : {' | '.join(strengths) if strengths else 'aucun identifié'}
Lacunes : {' | '.join(gaps) if gaps else 'aucune majeure'}
Détail compétences : {' | '.join(skills)}
Score projeté après plan : {result.get('projected_score')}/100

Consignes :
- Reste factuel et spécifique au poste et au profil ci-dessus.
- Maximum 3 watchouts, 4 cv_tips, 4 interview_tips, 3 plan_focus.
- Si le score est élevé, insiste sur la préparation d'entretien et la différenciation.
- Si le score est faible, sois honnête mais constructif : priorise les 2 leviers les plus rentables.
- Réponds avec ce schéma JSON : {ENRICH_SCHEMA}
"""
    return chat_json(ENRICH_SYSTEM, prompt, settings)


JOB_PARSE_SYSTEM = (
    "Tu extrais les exigences d'une offre d'emploi française. "
    "Tu réponds en JSON strict, sans texte autour, et tu n'inventes rien."
)

JOB_PARSE_SCHEMA = """{
  "title": "", "company": "", "contract": "", "location": "", "duration": "",
  "summary": "2 phrases",
  "missions": ["mission"],
  "required_skills": [{"skill": "", "level": 3, "weight": 2, "nature": "indispensable|important|atout"}],
  "qualities": [{"skill": "", "weight": 3}],
  "languages": [{"name": "Anglais", "min": "B2"}],
  "education": {"min_level": "Bac+4 (Master 1)", "fields": []},
  "keywords": ["mot-clé"]
}"""


def parse_job_with_ai(text: str, known_skills: list[str], settings: AISettings) -> tuple[dict | None, str]:
    prompt = f"""
Voici une offre d'emploi ou de stage. Extrais les informations demandées.

Compétences connues à réutiliser si possible (sinon propose un libellé proche) :
{', '.join(known_skills)}

OFFRE
\"\"\"
{text[:6000]}
\"\"\"

Niveaux : 1 Notions, 2 Débutant, 3 Intermédiaire, 4 Avancé, 5 Expert.
Nature : indispensable / important / atout.
Réponds avec ce schéma : {JOB_PARSE_SCHEMA}
"""
    return chat_json(JOB_PARSE_SYSTEM, prompt, settings)


CV_PARSE_SYSTEM = (
    "Tu extrais un profil candidat depuis un CV français. "
    "Tu réponds en JSON strict, sans texte autour. Tu restes prudent sur les niveaux."
)

CV_PARSE_SCHEMA = """{
  "skills": {"Compétence": 1..5},
  "languages": {"Français": "Natif", "Anglais": "B2"},
  "certifications": [{"name": "", "issuer": "", "year": "", "status": "Obtenue|En cours"}],
  "education": {"level": "", "field": "", "school": "", "grad_year": ""},
  "experiences": [{"title": "", "company": "", "period": "", "description": "", "skills": []}],
  "projects": [{"name": "", "role": "", "description": "", "tech": [], "link": ""}],
  "identity": {"name": "", "headline": "", "email": "", "phone": "", "location": "", "linkedin": ""}
}"""


def parse_cv_with_ai(text: str, known_skills: list[str], settings: AISettings) -> tuple[dict | None, str]:
    prompt = f"""
Voici le texte d'un CV. Extrais les informations du schéma.

Utilise en priorité ces compétences connues quand c'est pertinent :
{', '.join(known_skills[:120])}

Niveaux : 1 Notions, 2 Débutant, 3 Intermédiaire, 4 Avancé, 5 Expert.
N'invente aucune expérience ni certification absente du texte.

CV
\"\"\"
{text[:9000]}
\"\"\"

Réponds avec ce schéma : {CV_PARSE_SCHEMA}
"""
    return chat_json(CV_PARSE_SYSTEM, prompt, settings)
