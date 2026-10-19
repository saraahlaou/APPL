"""Modèle de profil étudiant, calcul de complétion et profil de démonstration."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime
from typing import Any

from .data_skills import SKILLS, CEFR_LEVELS, EDUCATION_LEVELS


def _uid() -> str:
    return uuid.uuid4().hex[:8]


def new_profile() -> dict:
    return {
        "identity": {
            "name": "",
            "headline": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "portfolio": "",
            "bio": "",
        },
        "education": {
            "level": "",
            "field": "",
            "school": "",
            "grad_year": "",
        },
        "skills": {},           # compétence -> niveau 1..5
        "qualities": [],        # qualités sélectionnées
        "languages": {},        # langue -> niveau CECR
        "certifications": [],
        "experiences": [],
        "projects": [],
        "cv": {"filename": "", "text": "", "uploaded_at": ""},
        "target": {"type": "catalog", "job_id": "", "custom_job": None},
        "is_demo": False,
        "updated_at": "",
    }


def ensure_shape(profile: dict) -> dict:
    """Complète un profil ancien ou partiel avec les clés manquantes."""
    base = new_profile()
    profile = profile or {}
    for key, value in base.items():
        if key not in profile:
            profile[key] = copy.deepcopy(value)
        elif isinstance(value, dict) and isinstance(profile.get(key), dict):
            for sub_key, sub_value in value.items():
                if sub_key not in profile[key]:
                    profile[key][sub_key] = copy.deepcopy(sub_value)
    return profile


def touch(profile: dict) -> dict:
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    return profile


def profile_to_text(profile: dict) -> str:
    """Concatène tout le contenu textuel exploitables par le moteur."""
    parts: list[str] = []
    identity = profile.get("identity", {})
    parts += [identity.get("headline", ""), identity.get("bio", ""), identity.get("location", "")]
    education = profile.get("education", {})
    parts += [education.get("level", ""), education.get("field", ""), education.get("school", "")]
    for exp in profile.get("experiences", []):
        parts += [
            exp.get("title", ""),
            exp.get("company", ""),
            exp.get("description", ""),
            " ".join(exp.get("skills", []) or []),
        ]
    for project in profile.get("projects", []):
        tech = project.get("tech", [])
        if isinstance(tech, str):
            tech = [tech]
        parts += [
            project.get("name", ""),
            project.get("role", ""),
            project.get("description", ""),
            " ".join(tech or []),
        ]
    for cert in profile.get("certifications", []):
        parts.append(cert.get("name", ""))
    parts.append(profile.get("cv", {}).get("text", ""))
    return "\n".join(part for part in parts if part)


# --------------------------------------------------------------------------- #
# Complétion du profil
# --------------------------------------------------------------------------- #

COMPLETION_ITEMS = [
    ("Nom et titre du profil", 8),
    ("Adresse e-mail", 4),
    ("Ville / mobilité", 3),
    ("Formation (niveau + filière)", 12),
    ("Au moins 5 compétences", 18),
    ("Au moins 3 qualités", 8),
    ("Au moins 1 langue", 8),
    ("Au moins 1 projet", 14),
    ("Au moins 1 expérience", 8),
    ("Au moins 1 certification", 5),
    ("CV importé ou collé", 7),
    ("Objectif professionnel sélectionné", 5),
]


def completion(profile: dict) -> tuple[int, list[dict]]:
    """Retourne le pourcentage de complétion et le détail par critère."""
    profile = ensure_shape(profile)
    identity = profile["identity"]
    checks = {
        "Nom et titre du profil": bool(identity.get("name")) and bool(identity.get("headline")),
        "Adresse e-mail": bool(identity.get("email")),
        "Ville / mobilité": bool(identity.get("location")),
        "Formation (niveau + filière)": bool(profile["education"].get("level")) and bool(profile["education"].get("field")),
        "Au moins 5 compétences": len(profile["skills"]) >= 5,
        "Au moins 3 qualités": len(profile["qualities"]) >= 3,
        "Au moins 1 langue": len(profile["languages"]) >= 1,
        "Au moins 1 projet": len(profile["projects"]) >= 1,
        "Au moins 1 expérience": len(profile["experiences"]) >= 1,
        "Au moins 1 certification": len(profile["certifications"]) >= 1,
        "CV importé ou collé": bool(profile["cv"].get("text")),
        "Objectif professionnel sélectionné": bool(profile["target"].get("job_id") or profile["target"].get("custom_job")),
    }
    total = sum(points for label, points in COMPLETION_ITEMS)
    earned = sum(points for label, points in COMPLETION_ITEMS if checks.get(label))
    detail = [
        {"label": label, "points": points, "done": checks.get(label, False)}
        for label, points in COMPLETION_ITEMS
    ]
    return round(100 * earned / total), detail


def next_steps(profile: dict, limit: int = 3) -> list[dict]:
    """Retourne les prochaines actions utiles selon l'état du profil."""
    _, detail = completion(profile)
    labels = [item["label"] for item in detail if not item["done"]]
    guidance = {
        "Nom et titre du profil": ("Complète ton identité", "Un recruteur doit comprendre qui tu es en 5 secondes."),
        "Adresse e-mail": ("Ajoute ton e-mail", "Indispensable pour postuler et recevoir les réponses."),
        "Ville / mobilité": ("Précise ta mobilité", "Stage à Casablanca, hybride à Rabat ? Dis-le clairement."),
        "Formation (niveau + filière)": ("Renseigne ta formation", "Le niveau et la filière pèsent dans le matching."),
        "Au moins 5 compétences": ("Ajoute tes compétences", "C'est le cœur du score de compatibilité."),
        "Au moins 3 qualités": ("Choisis tes qualités", "Les soft skills font souvent la différence en entretien."),
        "Au moins 1 langue": ("Déclare tes langues", "Beaucoup d'offres exigent un niveau d'anglais précis."),
        "Au moins 1 projet": ("Ajoute un projet", "Un projet concret prouve tes compétences mieux qu'une liste."),
        "Au moins 1 expérience": ("Ajoute une expérience", "Stage, job, association : tout compte."),
        "Au moins 1 certification": ("Ajoute une certification", "Même en cours, elle montre ton engagement."),
        "CV importé ou collé": ("Importe ton CV", "L'analyse détecte automatiquement tes compétences."),
        "Objectif professionnel sélectionné": ("Choisis une offre cible", "Sans cible, pas de comparaison possible."),
    }
    steps = []
    for label in labels[:limit]:
        title, why = guidance.get(label, (label, "Complète cette section pour affiner l'analyse."))
        steps.append({"label": label, "title": title, "why": why})
    if not steps:
        steps.append({
            "label": "Analyse",
            "title": "Lance une nouvelle analyse",
            "why": "Ton profil est complet : compare-le à une offre pour préparer ta candidature.",
        })
    return steps


# --------------------------------------------------------------------------- #
# Profil de démonstration
# --------------------------------------------------------------------------- #

DEMO_CV = """YASMINE EL AMRANI
Étudiante en Master 1 Data & Intelligence Artificielle — Casablanca, Maroc
yasmine.elamrani@email.ma · 06 61 23 45 67 · linkedin.com/in/yasmine-elamrani

FORMATION
Master 1 Data & Intelligence Artificielle — Université Hassan II, Faculté des Sciences Ben M'Sik, Casablanca (2025-2027)
Licence Sciences Mathématiques & Informatique (SMI) — Université Mohammed V de Rabat (2022-2025)

EXPÉRIENCE
Stagiaire Data Analyst — Chari, e-commerce B2B (Casablanca, mars-juin 2026)
- Extraction et nettoyage de données de ventes avec SQL et Python (Pandas) sur 80 000 commandes.
- Création de 3 tableaux de bord Power BI suivis chaque semaine par l'équipe commerciale.
- Analyse de la rétention client : segmentation en 4 groupes et recommandations (+8 % de réactivation).

Trésorière — Club Informatique & Data, Faculté des Sciences Ben M'Sik (2024-2025)
- Gestion d'un budget de 80 000 MAD sous Excel, suivi des dépenses et reporting mensuel.
- Organisation de 3 événements (hackathon, ateliers Python) réunissant 120 participants.

PROJETS
Analyse des ventes d'une place de marché marocaine — Python, Pandas, Power BI
- Analyse exploratoire de 120 000 transactions, nettoyage des données, segmentation de 4 profils clients et tableau de bord de synthèse présenté devant un jury.

Prédiction du prix des logements à Casablanca — Python, scikit-learn
- Comparaison de 3 modèles de machine learning (régression linéaire, random forest, gradient boosting), R² de 0,84 et interprétation des résultats.

COMPÉTENCES
Python, SQL, Pandas, Power BI, Excel, Statistiques, Analyse de données, Git, Machine Learning

LANGUES
Arabe : langue maternelle · Français : C1 · Anglais : B2 (TOEIC 850)

CERTIFICATIONS
Google Data Analytics Professional Certificate — Coursera (2025)

CENTRES D'INTÉRÊT
Mentorat de lycéennes en programmation, course à pied, veille sur l'IA au Maroc.
"""


def demo_profile() -> dict:
    """Profil réaliste pour découvrir l'application immédiatement."""
    return ensure_shape({
        "identity": {
            "name": "Yasmine El Amrani",
            "headline": "Étudiante en Master 1 Data & IA — en recherche d'un stage Data Analyst à Casablanca",
            "email": "yasmine.elamrani@email.ma",
            "phone": "06 61 23 45 67",
            "location": "Casablanca, Maroc",
            "linkedin": "linkedin.com/in/yasmine-elamrani",
            "portfolio": "github.com/yasmine-elamrani",
            "bio": (
                "Étudiante en Master 1 Data & Intelligence Artificielle à Casablanca, "
                "passionnée par l'analyse de données et la visualisation. Mon premier "
                "stage dans une startup marocaine m'a appris à transformer des données "
                "brutes en décisions concrètes."
            ),
        },
        "education": {
            "level": "Bac+4 (Master 1)",
            "field": "Data & Intelligence artificielle",
            "school": "Université Hassan II — Faculté des Sciences Ben M'Sik, Casablanca",
            "grad_year": "2027",
        },
        "skills": {
            "Python": 3,
            "SQL": 4,
            "Excel": 3,
            "Pandas": 4,
            "Power BI": 2,
            "Data visualisation": 2,
            "Statistiques": 4,
            "Analyse de données": 4,
            "Git": 3,
            "Machine Learning": 2,
        },
        "qualities": [
            "Rigueur", "Esprit d'analyse", "Communication", "Curiosité",
            "Travail en équipe", "Organisation",
        ],
        "languages": {"Arabe": "Natif", "Français": "C1", "Anglais": "B2"},
        "certifications": [
            {"name": "Google Data Analytics Professional Certificate", "issuer": "Coursera / Google", "year": "2025", "status": "Obtenue"},
        ],
        "experiences": [
            {
                "id": _uid(),
                "title": "Stagiaire Data Analyst",
                "company": "Chari (Casablanca)",
                "period": "Mars — Juin 2026",
                "description": (
                    "Extraction et nettoyage de données de ventes avec SQL et Python. "
                    "Création de 3 tableaux de bord Power BI et analyse de la rétention "
                    "client avec recommandations (+8 % de réactivation)."
                ),
                "skills": ["SQL", "Python", "Power BI", "Excel"],
            },
            {
                "id": _uid(),
                "title": "Trésorière",
                "company": "Club Informatique & Data — Faculté des Sciences Ben M'Sik",
                "period": "2024 — 2025",
                "description": (
                    "Gestion d'un budget de 80 000 MAD sous Excel, suivi des dépenses, "
                    "reporting mensuel et organisation d'événements avec 120 participants."
                ),
                "skills": ["Excel", "Organisation", "Communication"],
            },
        ],
        "projects": [
            {
                "id": _uid(),
                "name": "Analyse des ventes d'une place de marché marocaine",
                "role": "Projet académique en binôme",
                "description": (
                    "Analyse exploratoire de 120 000 transactions : nettoyage des données, "
                    "segmentation de 4 profils clients et dashboard de synthèse Power BI "
                    "présenté devant un jury."
                ),
                "tech": ["Python", "Pandas", "Power BI", "SQL"],
                "link": "github.com/yasmine-elamrani/analyse-marche",
            },
            {
                "id": _uid(),
                "name": "Prédiction du prix des logements à Casablanca",
                "role": "Projet personnel",
                "description": (
                    "Comparaison de 3 modèles de machine learning (régression linéaire, "
                    "random forest, gradient boosting), évaluation et interprétation "
                    "des résultats — R² de 0,84."
                ),
                "tech": ["Python", "Pandas", "Machine Learning"],
                "link": "github.com/yasmine-elamrani/prix-logements",
            },
        ],
        "cv": {"filename": "CV_Yasmine_El_Amrani.pdf", "text": DEMO_CV, "uploaded_at": datetime.now().isoformat(timespec="seconds")},
        "target": {"type": "catalog", "job_id": "data-analyst-stage", "custom_job": None},
        "is_demo": True,
    })


def skill_label(level: int | float | None) -> str:
    from .data_skills import SKILL_LEVELS

    if level is None:
        return "Non renseigné"
    return SKILL_LEVELS.get(int(round(level)), "Non renseigné")
