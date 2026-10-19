"""Moteur de compatibilité profil / offre.

Le moteur est local, déterministe et explicable : chaque score peut être
justifié par une compétence déclarée, détectée dans le CV ou approchée par
une compétence proche. L'IA générative vient ensuite enrichir le récit et le
plan, sans modifier le score calculé.
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from datetime import datetime

from .data_courses import CERT_ALIAS_INDEX, CERTIFICATIONS
from .data_skills import (
    ALIAS_INDEX,
    CEFR_VALUE,
    EDUCATION_VALUE,
    SKILLS,
    field_relevance,
)
from .profile import ensure_shape, profile_to_text

# --------------------------------------------------------------------------- #
# Constantes de scoring
# --------------------------------------------------------------------------- #

NATURE_MULTIPLIER = {"indispensable": 1.0, "important": 0.75, "atout": 0.4}

DEFAULT_WEIGHTS = {
    "skills": 0.40,
    "qualities": 0.15,
    "portfolio": 0.20,
    "languages": 0.10,
    "formation": 0.15,
}

DOMAIN_WEIGHTS = {
    "Data & IA": {"skills": 0.45, "qualities": 0.12, "portfolio": 0.20, "languages": 0.10, "formation": 0.13},
    "Développement logiciel": {"skills": 0.45, "qualities": 0.12, "portfolio": 0.20, "languages": 0.10, "formation": 0.13},
    "Cybersécurité & Cloud": {"skills": 0.45, "qualities": 0.12, "portfolio": 0.20, "languages": 0.10, "formation": 0.13},
    "Produit & Gestion de projet": {"skills": 0.35, "qualities": 0.18, "portfolio": 0.20, "languages": 0.10, "formation": 0.17},
    "Design & UX": {"skills": 0.35, "qualities": 0.18, "portfolio": 0.20, "languages": 0.10, "formation": 0.17},
    "Marketing & Communication": {"skills": 0.35, "qualities": 0.18, "portfolio": 0.20, "languages": 0.10, "formation": 0.17},
    "Finance & Conseil": {"skills": 0.35, "qualities": 0.18, "portfolio": 0.20, "languages": 0.10, "formation": 0.17},
}

SUBS_COLORS = {
    "Compétences": "#17795E",
    "Qualités": "#D98324",
    "Projets & expérience": "#4B5D9E",
    "Langues": "#2E7D9A",
    "Formation & certifications": "#8A5CC6",
}

# Correspondance entre les clés de pondération (internes) et les libellés affichés.
WEIGHT_TO_SUBSCORE = {
    "skills": "Compétences",
    "qualities": "Qualités",
    "portfolio": "Projets & expérience",
    "languages": "Langues",
    "formation": "Formation & certifications",
}

VERDICTS = [
    (80, "Excellente correspondance", "success", "Ton profil coche l'essentiel des attentes. Candidature à préparer dès maintenant."),
    (65, "Bonne correspondance", "good", "Tu as de vrais atouts. Quelques preuves à renforcer pour passer devant les autres."),
    (50, "Correspondance partielle", "warning", "Le poste est accessible, mais tu dois combler des lacunes ciblées avant de postuler."),
    (0, "Écart important", "danger", "Le poste demande un socle que tu n'as pas encore. Un plan progressif est indispensable."),
]


# --------------------------------------------------------------------------- #
# Utilitaires texte
# --------------------------------------------------------------------------- #

def normalize(text: str) -> str:
    """Minuscules, sans accents, ponctuation simplifiée."""
    if text is None:
        return ""
    text = str(text).lower().replace("’", "'").replace("œ", "oe")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9+#./'\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


ALIAS_INDEX_NORM: dict[str, str] = {normalize(alias): skill for alias, skill in ALIAS_INDEX.items()}
CANONICAL_NORM: dict[str, str] = {normalize(name): name for name in SKILLS}


def canonical_skill(value: str) -> str | None:
    if not value:
        return None
    norm = normalize(value)
    if norm in ALIAS_INDEX_NORM:
        return ALIAS_INDEX_NORM[norm]
    if norm in CANONICAL_NORM:
        return CANONICAL_NORM[norm]
    return None


def extract_skills(text: str) -> dict[str, int]:
    """Détecte les compétences citées dans un texte libre (CV, projet, offre)."""
    counts: dict[str, int] = {}
    if not text:
        return counts
    normalized = " " + normalize(text) + " "
    for alias, skill in sorted(ALIAS_INDEX_NORM.items(), key=lambda item: -len(item[0])):
        if len(alias) < 2:
            continue
        pattern = r"(?<![a-z0-9+#/])" + re.escape(alias).replace(r"\ ", r"\s+") + r"(?![a-z0-9+#/])"
        matches = re.findall(pattern, normalized)
        if matches:
            counts[skill] = counts.get(skill, 0) + len(matches)
    return counts


LANGUAGE_ALIASES: dict[str, list[str]] = {
    "Français": ["francais", "french", "langue maternelle", "langue natale"],
    "Anglais": ["anglais", "english"],
    "Espagnol": ["espagnol", "spanish"],
    "Allemand": ["allemand", "german", "deutsch"],
    "Italien": ["italien", "italian"],
    "Portugais": ["portugais", "portuguese"],
    "Arabe": ["arabe", "arabic"],
    "Chinois": ["chinois", "chinese", "mandarin"],
    "Japonais": ["japonais", "japanese"],
}

# Jetons de niveau CECR reconnus dans un texte libre et leur niveau canonique.
LEVEL_TOKENS = [
    ("langue maternelle", "Natif"), ("natif", "Natif"), ("bilingue", "C2"),
    ("c2", "C2"), ("c1", "C1"), ("b2", "B2"), ("b1", "B1"), ("a2", "A2"), ("a1", "A1"),
    ("courant", "C1"), ("professionnel", "C1"), ("intermediaire", "B1"), ("scolaire", "A2"),
]


def detect_languages(text: str) -> dict[str, str]:
    """Détecte les langues et niveaux CECR dans un texte.

    Le niveau est cherché d'abord juste après le nom de la langue
    (« Anglais : B2 »), puis juste avant (« B2 en anglais ») — sans
    mélanger deux langues voisines (« Anglais B2, espagnol »).
    """
    found: dict[str, str] = {}
    if not text:
        return found
    normalized = normalize(text)
    all_aliases = [alias for aliases in LANGUAGE_ALIASES.values() for alias in aliases]

    def level_from(segment: str) -> str | None:
        for token, value in LEVEL_TOKENS:
            if token in segment:
                return value
        return None

    for language, aliases in LANGUAGE_ALIASES.items():
        found_level = None
        for alias in aliases:
            for match in re.finditer(r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])", normalized):
                right = normalized[match.end(): match.end() + 30]
                found_level = level_from(right)
                if found_level:
                    break
                left = normalized[max(0, match.start() - 18): match.start()]
                # Ignore la fenêtre gauche si une autre langue y est citée.
                if not any(other in left for other in all_aliases if other not in aliases):
                    found_level = level_from(left)
                    if found_level:
                        break
                if alias in ("langue maternelle", "langue natale"):
                    found_level = "Natif"
                    break
            if found_level:
                break
        if found_level:
            found[language] = found_level
    return found


def detect_certifications(text: str) -> list[dict]:
    """Détecte les certifications connues dans un texte."""
    if not text:
        return []
    normalized = normalize(text)
    found: list[dict] = []
    seen: set[str] = set()
    for alias, cert in CERT_ALIAS_INDEX.items():
        alias_norm = normalize(alias)
        if len(alias_norm) < 4:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(alias_norm).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            if cert.name not in seen:
                seen.add(cert.name)
                found.append({"name": cert.name, "issuer": cert.issuer, "year": "", "status": "Obtenue"})
    return found


def _contains_word(normalized: str, key: str) -> bool:
    """Vrai si le motif apparaît comme mot entier (évite « synthese » → « these »)."""
    key = key.strip()
    if not key:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(key).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, normalized) is not None


def detect_education(text: str) -> dict:
    """Estime le niveau et la filière depuis un texte de CV."""
    if not text:
        return {}
    normalized = normalize(text)
    level = ""
    patterns = [
        ("Doctorat", ["doctorat", "these", "phd", "these de doctorat"]),
        ("Bac+5 (Master 2 / Ingénieur)", ["master 2", "master2", "m2", "diplome d'ingenieur", "ecole d'ingenieur", "ingenieur diplome", "bac+5", "bac +5"]),
        ("Bac+4 (Master 1)", ["master 1", "master1", "m1", "bac+4", "bac +4"]),
        ("Bac+3 (Licence / BUT3)", ["licence", "licence 3", "l3", "but 3", "but3", "bachelor", "bac+3", "bac +3"]),
        ("Bac+2 (BTS / BUT2)", ["bts", "dut", "but 2", "but2", "bac+2", "bac +2"]),
        ("Bac", ["baccalaureat", "bac"]),
    ]
    for label, keys in patterns:
        if any(_contains_word(normalized, key) for key in keys):
            level = label
            break
    from .data_skills import EDUCATION_FIELD_KEYWORDS

    # Score pondéré : les mots-clés courts (« ui », « ia ») exigent un mot entier,
    # les expressions longues sont cherchées telles quelles.
    field = ""
    best_score = 0
    for candidate, keywords in EDUCATION_FIELD_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if len(keyword) <= 4:
                if _contains_word(normalized, keyword):
                    score += len(keyword) + 6
            elif keyword in normalized:
                score += len(keyword)
        if score > best_score:
            best_score, field = score, candidate
    return {"level": level, "field": field}


def _word_overlap(text: str, required: set[str]) -> set[str]:
    return set(extract_skills(text)) & required


# --------------------------------------------------------------------------- #
# Collecte des preuves
# --------------------------------------------------------------------------- #

def collect_evidence(profile: dict) -> dict:
    profile = ensure_shape(profile)
    texts: list[str] = []
    identity = profile["identity"]
    texts += [identity.get("headline", ""), identity.get("bio", "")]
    education = profile["education"]
    texts += [education.get("level", ""), education.get("field", ""), education.get("school", "")]
    for experience in profile.get("experiences", []):
        texts += [
            experience.get("title", ""),
            experience.get("company", ""),
            experience.get("description", ""),
            " ".join(experience.get("skills", []) or []),
        ]
    for project in profile.get("projects", []):
        tech = project.get("tech", [])
        if isinstance(tech, str):
            tech = [tech]
        texts += [
            project.get("name", ""),
            project.get("role", ""),
            project.get("description", ""),
            " ".join(tech or []),
        ]
    for cert in profile.get("certifications", []):
        texts.append(cert.get("name", ""))
    texts.append(profile.get("cv", {}).get("text", ""))

    blob = "\n".join(texts)
    mentions = extract_skills(blob)
    for cert in profile.get("certifications", []):
        canonical = canonical_certification(cert.get("name", ""))
        cert_skills = canonical.skills if canonical else ()
        for skill in cert_skills:
            if skill in SKILLS:
                mentions.setdefault(skill, 0)
                mentions[skill] += 1
    return {
        "mentions": mentions,
        "languages": detect_languages(blob),
        "certifications": detect_certifications(blob),
        "blob": blob,
    }


def canonical_certification(name: str):
    if not name:
        return None
    normalized = normalize(name)
    if normalized in CERT_ALIAS_INDEX:
        return CERT_ALIAS_INDEX[normalized]
    # Recherche par inclusion
    for alias, cert in CERT_ALIAS_INDEX.items():
        alias_norm = normalize(alias)
        if len(alias_norm) >= 5 and (alias_norm in normalized or normalized in alias_norm):
            return cert
    for cert in CERTIFICATIONS:
        name_norm = normalize(cert.name)
        if normalized and (normalized in name_norm or name_norm in normalized):
            return cert
    return None


# --------------------------------------------------------------------------- #
# Sous-scores
# --------------------------------------------------------------------------- #

def score_skills(profile: dict, job: dict, evidence: dict) -> tuple[float, list[dict]]:
    details: list[dict] = []
    declared = profile.get("skills", {})
    mentions = evidence["mentions"]
    total_weight = 0.0
    earned = 0.0

    for requirement in job.get("required_skills", []):
        skill = requirement["skill"]
        required_level = max(1, int(requirement.get("level", 3)))
        weight = max(1, int(requirement.get("weight", 2)))
        nature = requirement.get("nature", "important")
        effective_weight = weight * NATURE_MULTIPLIER.get(nature, 0.75)

        current = declared.get(skill)
        count = mentions.get(skill, 0)
        related_source = ""
        related_coverage = 0.0
        for related, factor in SKILLS.get(skill, {}).get("related", {}).items():
            related_level = declared.get(related)
            if related_level:
                cov = min(1.0, related_level / required_level) * factor
                if cov > related_coverage:
                    related_coverage, related_source = cov, related
            elif mentions.get(related):
                cov = 0.35 * factor
                if cov > related_coverage:
                    related_coverage, related_source = cov, related

        if current:
            coverage = min(1.0, current / required_level)
            source = "déclarée"
            if coverage < 1:
                source = "déclarée (niveau à renforcer)"
        elif count:
            coverage = min(0.75, 0.55 + 0.05 * (count - 1))
            source = "détectée dans le CV / les projets"
        elif related_coverage:
            coverage = min(0.5, related_coverage)
            source = f"approchée via {related_source}"
        else:
            coverage = 0.0
            source = "absente"

        total_weight += effective_weight
        earned += effective_weight * coverage

        if coverage >= 1:
            status = "acquise"
        elif coverage >= 0.75:
            status = "presque"
        elif coverage > 0:
            status = "partielle"
        else:
            status = "manquante"

        details.append({
            "skill": skill,
            "required_level": required_level,
            "required_label": {1: "Notions", 2: "Débutant", 3: "Intermédiaire", 4: "Avancé", 5: "Expert"}.get(required_level, "Intermédiaire"),
            "current_level": current,
            "current_label": {1: "Notions", 2: "Débutant", 3: "Intermédiaire", 4: "Avancé", 5: "Expert"}.get(current, "Non renseigné") if current else "Non renseigné",
            "mentions": count,
            "coverage": round(coverage, 3),
            "status": status,
            "source": source,
            "nature": nature,
            "weight": weight,
            "effective_weight": effective_weight,
        })

    score = 100 * earned / total_weight if total_weight else 0.0
    return score, details


def score_qualities(profile: dict, job: dict, evidence: dict) -> tuple[float, list[dict]]:
    details: list[dict] = []
    selected = set(profile.get("qualities", []))
    mentions = evidence["mentions"]
    total = 0.0
    earned = 0.0
    for requirement in job.get("qualities", []):
        skill = requirement["skill"]
        weight = max(1, int(requirement.get("weight", 2)))
        total += weight
        if skill in selected:
            coverage = 1.0
            source = "déclarée + assumée"
        elif mentions.get(skill):
            coverage = 0.7 if mentions[skill] < 2 else 0.8
            source = "détectée dans tes expériences / projets"
        else:
            coverage = 0.0
            source = "non documentée"
            related = SKILLS.get(skill, {}).get("related", {})
            for related_skill, factor in related.items():
                if related_skill in selected:
                    coverage = max(coverage, 0.4 * factor + 0.2)
                    source = f"approchée via {related_skill}"
        earned += weight * coverage
        details.append({
            "skill": skill,
            "weight": weight,
            "coverage": round(coverage, 3),
            "status": "acquise" if coverage >= 0.9 else ("partielle" if coverage > 0 else "manquante"),
            "source": source,
        })
    score = 100 * earned / total if total else 100.0
    return score, details


def score_languages(profile: dict, job: dict, evidence: dict) -> tuple[float, list[dict]]:
    details: list[dict] = []
    declared = dict(profile.get("languages", {}))
    for language, level in evidence.get("languages", {}).items():
        declared.setdefault(language, level)
    total = 0.0
    earned = 0.0
    for requirement in job.get("languages", []):
        name = requirement["name"]
        minimum = requirement["min"]
        weight = max(1, int(requirement.get("weight", 2)))
        total += weight
        current = declared.get(name)
        min_value = CEFR_VALUE.get(minimum, 4)
        if not current:
            coverage = 0.0
            source = "non renseignée"
        else:
            current_value = CEFR_VALUE.get(current, 0)
            if current_value >= min_value:
                coverage = 1.0
                source = f"{name} {current} (attendu : {minimum})"
            else:
                coverage = max(0.15, current_value / min_value)
                source = f"{name} {current} — niveau {minimum} attendu"
        earned += weight * coverage
        details.append({
            "language": name,
            "min": minimum,
            "current": current or "Non renseigné",
            "coverage": round(coverage, 3),
            "status": "acquise" if coverage >= 1 else ("partielle" if coverage > 0 else "manquante"),
            "source": source,
            "weight": weight,
        })
    score = 100 * earned / total if total else 100.0
    return score, details


def score_formation(profile: dict, job: dict) -> tuple[float, dict]:
    education = profile.get("education", {})
    job_education = job.get("education", {}) or {}
    current_level = education.get("level", "")
    min_level = job_education.get("min_level", "")
    current_value = EDUCATION_VALUE.get(current_level, 0)
    min_value = EDUCATION_VALUE.get(min_level, 3)

    if not current_value:
        level_coverage = 0.25
    else:
        level_coverage = min(1.0, current_value / min_value)

    relevance = field_relevance(education.get("field", ""), job_education.get("fields", []))
    education_score = 100 * (0.7 * level_coverage + 0.3 * relevance)

    cert_requirements = job.get("certifications", [])
    profile_certs = profile.get("certifications", [])
    cert_details = []

    if cert_requirements:
        total = 0.0
        earned = 0.0
        importance_multiplier = {"indispensable": 1.0, "souhaitee": 0.85, "atout": 0.55}
        for requirement in cert_requirements:
            name = requirement.get("name", "")
            importance = requirement.get("importance", "souhaitee")
            weight = importance_multiplier.get(importance, 0.8)
            total += weight
            matched = False
            for cert in profile_certs:
                canonical = canonical_certification(cert.get("name", ""))
                if canonical and normalize(canonical.name) == normalize(name):
                    matched = True
                    break
                if name and normalize(name) in normalize(cert.get("name", "")):
                    matched = True
                    break
                if canonical and any(normalize(name) == normalize(alias) for alias in canonical.aliases):
                    matched = True
                    break
            if matched:
                earned += weight
            cert_details.append({"name": name, "importance": importance, "matched": matched})
        certification_score = 100 * earned / total if total else 100.0
    else:
        required_skills = {r["skill"] for r in job.get("required_skills", [])}
        relevant = 0
        for cert in profile_certs:
            canonical = canonical_certification(cert.get("name", ""))
            skills = set(canonical.skills) if canonical else set()
            if skills & required_skills:
                relevant += 1
        certification_score = min(100.0, 70.0 + 15.0 * relevant)
        cert_details = [{"name": cert.get("name", ""), "importance": "bonus", "matched": True} for cert in profile_certs]

    formation_score = 0.65 * education_score + 0.35 * certification_score
    detail = {
        "education_score": round(education_score, 1),
        "certification_score": round(certification_score, 1),
        "level_coverage": round(level_coverage, 2),
        "field_relevance": round(relevance, 2),
        "current_level": current_level or "Non renseigné",
        "min_level": min_level or "Non précisé",
        "current_field": education.get("field", "") or "Non renseignée",
        "required_fields": job_education.get("fields", []),
        "certifications": cert_details,
    }
    return formation_score, detail


def portfolio_relevance(item: dict, required_skills: set[str]) -> float:
    if not required_skills:
        return 0.0
    tech = item.get("tech", item.get("skills", []))
    if isinstance(tech, str):
        tech = [tech]
    tech_canonical = {canonical_skill(t) for t in tech if t}
    text = " ".join([
        item.get("name", item.get("title", "")),
        item.get("role", ""),
        item.get("description", ""),
        item.get("company", ""),
        " ".join(str(t) for t in tech),
    ])
    mentioned = set(extract_skills(text))
    matched = (mentioned | {t for t in tech_canonical if t}) & required_skills
    return min(1.0, len(matched) / max(1, len(required_skills)))


def score_portfolio(profile: dict, job: dict) -> tuple[float, dict]:
    projects = profile.get("projects", [])
    experiences = profile.get("experiences", [])
    required = {r["skill"] for r in job.get("required_skills", [])}

    project_relevances = [portfolio_relevance(p, required) for p in projects]
    experience_relevances = [portfolio_relevance(e, required) for e in experiences]
    max_project_rel = max(project_relevances, default=0.0)
    max_experience_rel = max(experience_relevances, default=0.0)

    project_score = 0.0
    if projects:
        base = {1: 52, 2: 68}.get(min(len(projects), 2), 78)
        quality_bonus = 0
        if any(len(p.get("description", "")) >= 120 for p in projects):
            quality_bonus += 6
        if any(p.get("link") for p in projects):
            quality_bonus += 6
        project_score = min(100.0, base + 25 * max_project_rel + quality_bonus)

    experience_score = 0.0
    if experiences:
        base = 50 if len(experiences) == 1 else 66
        experience_score = min(100.0, base + 30 * max_experience_rel)

    if projects and experiences:
        score = 0.55 * project_score + 0.45 * experience_score
    elif projects:
        score = project_score
    elif experiences:
        score = experience_score
    else:
        score = 15.0

    detail = {
        "project_count": len(projects),
        "experience_count": len(experiences),
        "max_project_relevance": round(max_project_rel, 2),
        "max_experience_relevance": round(max_experience_rel, 2),
        "project_score": round(project_score, 1),
        "experience_score": round(experience_score, 1),
    }
    return score, detail


# --------------------------------------------------------------------------- #
# Score global
# --------------------------------------------------------------------------- #

def weights_for(job: dict) -> dict:
    return dict(DOMAIN_WEIGHTS.get(job.get("domain", ""), DEFAULT_WEIGHTS))


def verdict_for(score: float) -> dict:
    for threshold, label, tone, message in VERDICTS:
        if score >= threshold:
            return {"label": label, "tone": tone, "message": message, "threshold": threshold}
    return {"label": "Écart important", "tone": "danger", "message": "", "threshold": 0}


def _weighted_total(subscores: dict, weights: dict) -> float:
    total_weight = sum(weights.values()) or 1
    total = 0.0
    for key, weight in weights.items():
        label = WEIGHT_TO_SUBSCORE.get(key, key)
        value = subscores.get(label, subscores.get(key, 0))
        total += value * weight
    return total / total_weight


def confidence_for(profile: dict, evidence: dict) -> int:
    from .profile import completion

    pct, _ = completion(profile)
    confidence = 38 + 0.55 * pct
    if profile.get("cv", {}).get("text"):
        confidence += 7
    if len(profile.get("projects", [])) >= 2:
        confidence += 4
    return int(max(30, min(97, confidence)))


# --------------------------------------------------------------------------- #
# Analyse complète
# --------------------------------------------------------------------------- #

def build_gaps(subscores: dict, weights: dict, skills_details: list[dict],
               qualities_details: list[dict], languages_details: list[dict],
               formation_detail: dict, portfolio_detail: dict) -> list[dict]:
    gaps: list[dict] = []

    total_skill_weight = sum(d["effective_weight"] for d in skills_details) or 1
    for detail in skills_details:
        if detail["coverage"] >= 0.85:
            continue
        impact = weights["skills"] * (detail["effective_weight"] / total_skill_weight) * (1 - detail["coverage"]) * 100
        if detail["coverage"] == 0 and detail["nature"] == "indispensable":
            severity = "critique"
        elif detail["coverage"] < 0.5:
            severity = "critique" if detail["nature"] != "atout" else "important"
        elif detail["coverage"] < 0.85:
            severity = "important"
        else:
            severity = "bonus"
        if detail["nature"] == "atout":
            severity = "bonus" if detail["coverage"] >= 0.3 else "important"
        gaps.append({
            "id": f"skill-{normalize(detail['skill']).replace(' ', '-')}",
            "type": "competence",
            "skill": detail["skill"],
            "title": detail["skill"],
            "severity": severity,
            "impact_points": round(impact, 1),
            "coverage": detail["coverage"],
            "current_label": detail["current_label"],
            "required_label": detail["required_label"],
            "nature": detail["nature"],
            "why": (
                f"L'offre attend un niveau « {detail['required_label']} » et tu es "
                f"aujourd'hui « {detail['current_label']} »."
                if detail["current_level"] else
                "Cette compétence n'apparaît ni dans ton profil ni dans tes preuves (CV, projets, expériences)."
            ),
            "how": "",
        })

    total_quality_weight = sum(d["weight"] for d in qualities_details) or 1
    for detail in qualities_details:
        if detail["coverage"] >= 0.8:
            continue
        impact = weights["qualities"] * (detail["weight"] / total_quality_weight) * (1 - detail["coverage"]) * 100
        gaps.append({
            "id": f"quality-{normalize(detail['skill']).replace(' ', '-')}",
            "type": "qualite",
            "skill": detail["skill"],
            "title": detail["skill"],
            "severity": "important" if detail["weight"] >= 3 else "bonus",
            "impact_points": round(impact, 1),
            "coverage": detail["coverage"],
            "current_label": "Non documentée" if detail["coverage"] == 0 else "Partiellement documentée",
            "required_label": "Attendue par l'offre",
            "nature": "important",
            "why": "Les recruteurs cherchent des preuves concrètes, pas seulement une qualité affirmée.",
            "how": "",
        })

    total_lang_weight = sum(d["weight"] for d in languages_details) or 1
    for detail in languages_details:
        if detail["coverage"] >= 1:
            continue
        from .data_skills import CEFR_VALUE as _CV

        current_value = _CV.get(detail["current"], 0)
        min_value = _CV.get(detail["min"], 4)
        impact = weights["languages"] * (detail["weight"] / total_lang_weight) * (1 - detail["coverage"]) * 100
        gaps.append({
            "id": f"lang-{normalize(detail['language'])}",
            "type": "langue",
            "skill": detail["language"],
            "title": f"{detail['language']} — niveau {detail['min']} attendu",
            "severity": "critique" if min_value - current_value >= 2 else "important",
            "impact_points": round(impact, 1),
            "coverage": detail["coverage"],
            "current_label": detail["current"],
            "required_label": detail["min"],
            "nature": "important",
            "why": f"L'offre exige un niveau {detail['min']} en {detail['language']}.",
            "how": "",
        })

    for cert in formation_detail.get("certifications", []):
        if cert.get("matched"):
            continue
        if cert.get("importance") == "atout":
            continue
        impact = weights["formation"] * 0.25 * 0.9
        gaps.append({
            "id": f"cert-{normalize(cert['name'])[:40]}",
            "type": "certification",
            "skill": cert["name"],
            "title": cert["name"],
            "severity": "important" if cert.get("importance") == "souhaitee" else "critique",
            "impact_points": round(impact, 1),
            "coverage": 0.0,
            "current_label": "Non obtenue",
            "required_label": "Appréciée par l'offre",
            "nature": "important",
            "why": "Cette certification est un signal de motivation et de compétence pour ce type de poste.",
            "how": "",
        })

    if formation_detail.get("level_coverage", 1) < 0.75:
        impact = weights["formation"] * 0.65 * (1 - formation_detail["level_coverage"]) * 100
        gaps.append({
            "id": "formation-level",
            "type": "formation",
            "skill": "Formation",
            "title": f"Formation — {formation_detail.get('min_level')} attendu",
            "severity": "critique" if formation_detail["level_coverage"] < 0.5 else "important",
            "impact_points": round(impact, 1),
            "coverage": formation_detail["level_coverage"],
            "current_label": formation_detail.get("current_level", "Non renseigné"),
            "required_label": formation_detail.get("min_level", "Non précisé"),
            "nature": "important",
            "why": "Le niveau de diplôme est un critère de présélection fréquent en France.",
            "how": "",
        })

    if portfolio_detail.get("project_count", 0) == 0 and portfolio_detail.get("experience_count", 0) == 0:
        impact = weights["portfolio"] * 0.85 * 100
        gaps.append({
            "id": "portfolio-empty",
            "type": "projet",
            "skill": "Projets",
            "title": "Aucune preuve concrète (projet ou expérience)",
            "severity": "critique",
            "impact_points": round(impact, 1),
            "coverage": 0.15,
            "current_label": "Aucun projet",
            "required_label": "Preuves attendues",
            "nature": "important",
            "why": "Sans projet ni expérience, tes compétences restent théoriques aux yeux du recruteur.",
            "how": "",
        })
    elif portfolio_detail.get("max_project_relevance", 0) < 0.35 and portfolio_detail.get("project_count", 0) > 0:
        impact = weights["portfolio"] * 0.35 * 100
        gaps.append({
            "id": "portfolio-relevance",
            "type": "projet",
            "skill": "Projets",
            "title": "Projets peu connectés à cette offre",
            "severity": "important",
            "impact_points": round(impact, 1),
            "coverage": 0.4,
            "current_label": "Projets génériques",
            "required_label": "Projets en lien avec le poste",
            "nature": "important",
            "why": "Tes projets existent mais ne démontrent pas les compétences demandées par cette offre.",
            "how": "",
        })

    gaps.sort(key=lambda g: (g["impact_points"], g["severity"] == "critique"), reverse=True)
    return gaps


def analyze(profile: dict, job: dict, with_plan: bool = True) -> dict:
    """Analyse complète d'un profil face à une offre."""
    profile = ensure_shape(profile)
    evidence = collect_evidence(profile)

    skills_score, skills_details = score_skills(profile, job, evidence)
    qualities_score, qualities_details = score_qualities(profile, job, evidence)
    languages_score, languages_details = score_languages(profile, job, evidence)
    formation_score, formation_detail = score_formation(profile, job)
    portfolio_score, portfolio_detail = score_portfolio(profile, job)

    weights = weights_for(job)
    subscores = {
        "Compétences": skills_score,
        "Qualités": qualities_score,
        "Projets & expérience": portfolio_score,
        "Langues": languages_score,
        "Formation & certifications": formation_score,
    }
    total_score = _weighted_total(subscores, weights)
    confidence = confidence_for(profile, evidence)
    verdict = verdict_for(total_score)

    strengths = build_strengths(
        skills_details, qualities_details, languages_details, formation_detail, portfolio_detail
    )
    gaps = build_gaps(
        subscores, weights, skills_details, qualities_details, languages_details,
        formation_detail, portfolio_detail,
    )

    required_names = {r["skill"] for r in job.get("required_skills", [])}
    bonus_opportunities = [
        skill for skill in job.get("nice_to_have", [])
        if skill in SKILLS and skill not in required_names and skill not in profile.get("skills", {})
    ][:5]

    result = {
        "id": uuid.uuid4().hex[:10],
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "job_id": job.get("id", "custom"),
        "job_title": job.get("title", "Offre"),
        "company": job.get("company", ""),
        "job": job,
        "score": int(round(total_score)),
        "confidence": confidence,
        "verdict": verdict,
        "subscores": {key: int(round(value)) for key, value in subscores.items()},
        "subscores_raw": {key: round(value, 1) for key, value in subscores.items()},
        "weights": weights,
        "skills_detail": skills_details,
        "qualities_detail": qualities_details,
        "languages_detail": languages_details,
        "formation_detail": formation_detail,
        "portfolio_detail": portfolio_detail,
        "strengths": strengths,
        "gaps": gaps,
        "bonus_opportunities": bonus_opportunities,
        "keywords": list(dict.fromkeys(
            (job.get("keywords", []) + [r["skill"] for r in job.get("required_skills", [])])
        ))[:14],
        "projected_score": None,
        "narrative": "",
        "cv_tips": [],
        "interview_tips": [],
        "ai": None,
    }

    if with_plan:
        from .planner import enrich_analysis

        result = enrich_analysis(result, profile, job)

    return result


def build_strengths(skills_details: list[dict], qualities_details: list[dict],
                    languages_details: list[dict], formation_detail: dict,
                    portfolio_detail: dict) -> list[dict]:
    strengths: list[dict] = []
    for detail in sorted(skills_details, key=lambda d: d["effective_weight"], reverse=True):
        if detail["coverage"] >= 0.85:
            source = "compétence déclarée" if detail["coverage"] >= 1 else "compétence détectée"
            strengths.append({
                "type": "competence",
                "title": detail["skill"],
                "detail": f"Niveau {detail['current_label']} (attendu : {detail['required_label']}) — {source}",
                "impact": detail["effective_weight"],
            })
    for detail in qualities_details:
        if detail["coverage"] >= 0.9:
            strengths.append({
                "type": "qualite",
                "title": detail["skill"],
                "detail": detail["source"],
                "impact": detail["weight"],
            })
    for detail in languages_details:
        if detail["coverage"] >= 1:
            strengths.append({
                "type": "langue",
                "title": f"{detail['language']} {detail['current']}",
                "detail": f"Niveau attendu : {detail['min']} — atteint",
                "impact": detail["weight"],
            })
    if formation_detail.get("level_coverage", 0) >= 1 and formation_detail.get("field_relevance", 0) >= 0.8:
        strengths.append({
            "type": "formation",
            "title": formation_detail.get("current_level", "Formation alignée"),
            "detail": f"Filière {formation_detail.get('current_field', '')} pertinente pour l'offre",
            "impact": 4,
        })
    if portfolio_detail.get("max_project_relevance", 0) >= 0.5 and portfolio_detail.get("project_count", 0):
        strengths.append({
            "type": "projet",
            "title": "Projets pertinents",
            "detail": "Tes projets démontrent déjà une partie des compétences demandées",
            "impact": 3,
        })

    strengths.sort(key=lambda item: item["impact"], reverse=True)
    # Regroupe les compétences pour éviter une liste trop longue
    seen: set[str] = set()
    unique: list[dict] = []
    for item in strengths:
        if item["title"] in seen:
            continue
        seen.add(item["title"])
        unique.append(item)
    return unique[:7]


def simulate_improvement(result: dict, profile: dict, job: dict) -> int:
    """Score potentiel si les lacunes prioritaires sont comblées."""
    profile = ensure_shape(profile)
    simulated = {
        "skills": dict(profile.get("skills", {})),
        "qualities": list(profile.get("qualities", [])),
        "languages": dict(profile.get("languages", {})),
        "certifications": list(profile.get("certifications", [])),
        "levels_gain": {},
    }
    for gap in result.get("gaps", [])[:8]:
        if gap["type"] == "competence":
            required = next((d["required_level"] for d in result["skills_detail"] if d["skill"] == gap["skill"]), 3)
            simulated["skills"][gap["skill"]] = required
        elif gap["type"] == "qualite":
            if gap["skill"] not in simulated["qualities"]:
                simulated["qualities"].append(gap["skill"])
        elif gap["type"] == "langue":
            requirement = next((l for l in result["languages_detail"] if l["language"] == gap["skill"]), None)
            if requirement:
                simulated["languages"][gap["skill"]] = requirement["min"]

    simulated_profile = dict(profile)
    simulated_profile["skills"] = simulated["skills"]
    simulated_profile["qualities"] = simulated["qualities"]
    simulated_profile["languages"] = simulated["languages"]
    # Les certifications et la formation ne sont pas simulées : trop longues.

    evidence = collect_evidence(simulated_profile)
    skills_score, _ = score_skills(simulated_profile, job, evidence)
    qualities_score, _ = score_qualities(simulated_profile, job, evidence)
    languages_score, _ = score_languages(simulated_profile, job, evidence)
    formation_score, _ = score_formation(simulated_profile, job)
    portfolio_score, _ = score_portfolio(simulated_profile, job)
    subscores = {
        "Compétences": skills_score,
        "Qualités": qualities_score,
        "Projets & expérience": portfolio_score,
        "Langues": languages_score,
        "Formation & certifications": formation_score,
    }
    weights = weights_for(job)
    return int(min(97, round(_weighted_total(subscores, weights))))
