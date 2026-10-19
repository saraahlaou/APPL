"""Génération du plan d'action personnalisé et du récit d'analyse.

Le plan est construit à partir des lacunes détectées par le moteur :
- Sprint 1 (7 jours) : quick wins de candidature et première montée en compétence ;
- Sprint 2 (30 jours) : formations ciblées et projets qui prouvent les compétences ;
- Sprint 3 (90 jours) : certification, portfolio, réseau et candidature finale.
"""

from __future__ import annotations

from .data_courses import COURSES, CERTIFICATIONS, courses_for, project_idea, search_fallback
from .matching import normalize, simulate_improvement


def _action(action_id: str, title: str, detail: str, action_type: str, horizon: str,
            skill: str, impact: float, effort_hours: float = 4.0,
            resource: dict | None = None, optional: bool = False) -> dict:
    return {
        "id": action_id,
        "title": title,
        "detail": detail,
        "type": action_type,
        "horizon": horizon,
        "skill": skill,
        "impact_points": round(impact, 1),
        "effort_hours": effort_hours,
        "resource": resource,
        "optional": optional,
        "done": False,
    }


def _course_resource(course) -> dict:
    return {
        "title": course.title,
        "provider": course.provider,
        "url": course.url,
        "duration": course.duration,
        "price": course.price,
        "kind": course.kind,
    }


def _course_hours(course) -> float:
    duration = course.duration or ""
    if "h" in duration:
        try:
            value = float(duration.lower().replace("h", "").replace(",", ".").strip())
            return max(2.0, value)
        except ValueError:
            pass
    if "mois" in duration:
        return 40.0
    return 8.0


def _find_certification(name: str):
    target = normalize(name)
    for cert in CERTIFICATIONS:
        if normalize(cert.name) == target:
            return cert
        if target and target in normalize(cert.name):
            return cert
        for alias in cert.aliases:
            if normalize(alias) == target:
                return cert
    return None


def _top_course(skill: str):
    courses = courses_for(skill, limit=2)
    if courses:
        return courses[0]
    fallback = search_fallback(skill)
    return fallback[0] if fallback else None


def build_plan(result: dict, profile: dict, job: dict) -> dict:
    gaps = sorted(result.get("gaps", []), key=lambda gap: gap["impact_points"], reverse=True)
    skills_detail = {d["skill"]: d for d in result.get("skills_detail", [])}
    keywords = result.get("keywords", [])
    keyword_text = ", ".join(keywords[:8]) if keywords else "les compétences clés de l'offre"

    sprints = {
        "7 jours": [],
        "30 jours": [],
        "90 jours": [],
    }
    seen: set[str] = set()

    def add(horizon: str, action: dict) -> None:
        if action["id"] in seen:
            return
        seen.add(action["id"])
        sprints[horizon].append(action)

    # ------------------------------------------------------------------ #
    # Quick wins systématiques
    # ------------------------------------------------------------------ #
    add("7 jours", _action(
        "quick-cv", "Décliner ton CV pour cette offre",
        f"Réécris tes 3 premières puces en reprenant les mots-clés : {keyword_text}. "
        "Chaque puce doit commencer par un verbe d'action et finir par un résultat mesuré.",
        "CV", "7 jours", "CV", impact=5.0, effort_hours=2.0,
    ))
    add("7 jours", _action(
        "quick-linkedin", "Mettre à jour LinkedIn et ton portfolio",
        "Alignements : titre, accroche, compétences mises en avant, lien vers tes projets. "
        "Un recruteur qui reçoit ton CV vérifie presque toujours ton profil LinkedIn.",
        "CV", "7 jours", "CV", impact=2.0, effort_hours=1.5,
    ))
    add("7 jours", _action(
        "quick-star", "Préparer 3 histoires STAR",
        "Situation, Tâche, Action, Résultat : 3 exemples choisis parmi tes projets et expériences "
        "pour prouver tes compétences clés en entretien.",
        "Entretien", "7 jours", "Communication", impact=3.0, effort_hours=2.0,
    ))
    add("7 jours", _action(
        "quick-network", "Contacter 2 professionnels ou alumni",
        "Demande 20 minutes d'échange sur leur métier, pas un poste. C'est le meilleur moyen "
        "d'obtenir une recommandation ou des conseils de préparation.",
        "Réseau", "7 jours", "Réseau", impact=2.5, effort_hours=1.5,
    ))

    # ------------------------------------------------------------------ #
    # Actions issues des lacunes
    # ------------------------------------------------------------------ #
    skill_gaps = [g for g in gaps if g["type"] == "competence"]
    quality_gaps = [g for g in gaps if g["type"] == "qualite"]
    language_gaps = [g for g in gaps if g["type"] == "langue"]
    cert_gaps = [g for g in gaps if g["type"] == "certification"]
    formation_gaps = [g for g in gaps if g["type"] == "formation"]
    portfolio_gaps = [g for g in gaps if g["type"] == "projet"]

    for index, gap in enumerate(skill_gaps):
        skill = gap["skill"]
        course = _top_course(skill)
        detail = skills_detail.get(skill, {})
        current = detail.get("current_label", "Non renseigné")
        required = detail.get("required_label", "Intermédiaire")
        horizon = "30 jours" if index < 4 else "90 jours"

        if course:
            add(horizon, _action(
                f"course-{normalize(skill).replace(' ', '-')}",
                f"Formation : {course.title}",
                f"Monte de « {current} » vers « {required} » avec un parcours guidé, "
                "puis applique immédiatement sur un mini-exercice.",
                "Formation", horizon, skill,
                impact=gap["impact_points"] * 0.6,
                effort_hours=_course_hours(course),
                resource=_course_resource(course),
            ))

        if index < 5:
            add("30 jours" if index < 3 else "90 jours", _action(
                f"project-{normalize(skill).replace(' ', '-')}",
                f"Projet prouvant : {skill}",
                f"Construis {project_idea(skill)}. Ajoute-le à ton portfolio et à ton CV "
                "avec une puce « Projet — résultat ».",
                "Projet", "30 jours" if index < 3 else "90 jours", skill,
                impact=gap["impact_points"] * 0.4,
                effort_hours=14.0,
            ))

        if index == 0:
            add("7 jours", _action(
                f"start-{normalize(skill).replace(' ', '-')}",
                f"Démarre dès cette semaine sur {skill}",
                "Bloque 2 créneaux de 45 minutes dans ton agenda et termine le premier module. "
                "La régularité vaut mieux qu'une session marathon.",
                "Formation", "7 jours", skill,
                impact=gap["impact_points"] * 0.15,
                effort_hours=1.5,
                resource=_course_resource(course) if course else None,
            ))

    for gap in quality_gaps:
        add("30 jours", _action(
            f"proof-{normalize(gap['skill']).replace(' ', '-')}",
            f"Documenter la qualité « {gap['skill']} »",
            f"Crée une preuve concrète : {project_idea(gap['skill'])}. "
            "Puis raconte-la en 4 lignes dans ton CV ou ton portfolio.",
            "Preuve", "30 jours", gap["skill"],
            impact=gap["impact_points"] * 0.8,
            effort_hours=4.0,
        ))

    for gap in language_gaps:
        language = gap["skill"]
        course = _top_course(language)
        add("30 jours", _action(
            f"lang-course-{normalize(language)}",
            f"Renforcer {language} — objectif {gap['required_label']}",
            f"20 minutes par jour : une formation structurée + une série ou un podcast en {language}. "
            "Tiens un carnet des expressions professionnelles.",
            "Formation", "30 jours", language,
            impact=gap["impact_points"] * 0.6,
            effort_hours=20.0,
            resource=_course_resource(course) if course else None,
        ))
        cert_name = {"Anglais": "TOEIC", "Espagnol": "IELTS"}.get(language, "")
        certification = _find_certification(cert_name) if cert_name else None
        add("90 jours", _action(
            f"lang-cert-{normalize(language)}",
            f"Passer un test de niveau en {language}",
            "Un score officiel (TOEIC, IELTS…) rassure immédiatement le recruteur et te fixe un objectif daté.",
            "Certification", "90 jours", language,
            impact=gap["impact_points"] * 0.4,
            effort_hours=25.0,
            resource={"title": certification.name, "provider": certification.issuer,
                       "url": certification.url, "duration": "Score visé : " + gap["required_label"],
                       "price": "Payant", "kind": "Certification"} if certification else None,
        ))

    for gap in cert_gaps:
        certification = _find_certification(gap["skill"])
        add("90 jours", _action(
            f"cert-{normalize(gap['skill'])[:30].replace(' ', '-')}",
            f"Préparer la certification : {gap['skill']}",
            "Planifie l'examen dans 8 à 10 semaines, prépare-le par blocs de 2 h et "
            "ajoute la mention « en préparation » sur ton CV dès maintenant.",
            "Certification", "90 jours", gap["skill"],
            impact=gap["impact_points"] * 0.9,
            effort_hours=35.0,
            resource={"title": certification.name, "provider": certification.issuer,
                       "url": certification.url, "duration": certification.flexibility,
                       "price": "Payant", "kind": "Certification"} if certification else None,
        ))

    for gap in formation_gaps:
        add("90 jours", _action(
            "formation-module",
            "Valider un module ou une formation complémentaire",
            "Choisis un module universitaire, un MOOC certifiant ou une alternance qui "
            "te manque sur le papier, et documente-le dans ton CV.",
            "Formation", "90 jours", "Formation",
            impact=gap["impact_points"] * 0.7, effort_hours=40.0,
        ))

    for gap in portfolio_gaps:
        add("30 jours", _action(
            "portfolio-project",
            "Créer un projet aligné avec l'offre",
            f"Construis {project_idea(job.get('domain', 'le métier visé'))} en lien direct "
            "avec les missions de l'offre, puis publie-le avec une synthèse de 5 slides.",
            "Projet", "30 jours", "Projets",
            impact=gap["impact_points"] * 0.7, effort_hours=18.0,
        ))

    # ------------------------------------------------------------------ #
    # Bonus : compétences « atout » de l'offre
    # ------------------------------------------------------------------ #
    for skill in result.get("bonus_opportunities", [])[:2]:
        course = _top_course(skill)
        add("90 jours", _action(
            f"bonus-{normalize(skill).replace(' ', '-')}",
            f"Atout différenciant : {skill}",
            f"Cette compétence n'est pas obligatoire, mais elle te distinguerait des autres candidats. "
            f"Découvre-la avec une ressource courte puis mentionne-la si elle devient solide.",
            "Bonus", "90 jours", skill,
            impact=1.5, effort_hours=5.0,
            resource=_course_resource(course) if course else None,
            optional=True,
        ))

    phases = [
        {
            "key": "7 jours",
            "title": "Sprint 1 — Quick wins",
            "subtitle": "Cette semaine, tu maximises ta candidature et tu démarres ta progression.",
            "actions": sprints["7 jours"][:6],
        },
        {
            "key": "30 jours",
            "title": "Sprint 2 — Monter en compétences",
            "subtitle": "Formations ciblées et projets qui transforment tes lacunes en preuves.",
            "actions": sprints["30 jours"][:7],
        },
        {
            "key": "90 jours",
            "title": "Sprint 3 — Prouver et candidater",
            "subtitle": "Certification, portfolio, réseau : tu arrives en entretien avec des faits.",
            "actions": sprints["90 jours"][:7],
        },
    ]

    all_actions = [action for phase in phases for action in phase["actions"]]
    total_hours = sum(action["effort_hours"] for action in all_actions)

    return {
        "phases": phases,
        "total_actions": len(all_actions),
        "total_hours": round(total_hours),
        "generated_at": result.get("created_at", ""),
    }


def local_narrative(result: dict, profile: dict, job: dict) -> str:
    score = result["score"]
    verdict = result["verdict"]["label"].lower()
    job_title = job.get("title", "cette offre")
    company = job.get("company", "")
    company_text = f" chez {company}" if company else ""
    strengths = result.get("strengths", [])
    gaps = result.get("gaps", [])
    projected = result.get("projected_score") or score

    strength_names = ", ".join(item["title"] for item in strengths[:3]) or "ta motivation"
    gap_names = ", ".join(gap["title"] for gap in gaps[:2]) or "quelques détails à ajuster"

    parts = [
        f"Avec un score de {score}/100, ton profil présente une {verdict} avec {job_title}{company_text}.",
        f"Tes principaux atouts sont {strength_names}.",
    ]
    if gaps:
        parts.append(
            f"Pour franchir un cap, concentre-toi d'abord sur {gap_names} : "
            "ce sont les leviers qui feront bouger ton score le plus vite."
        )
    else:
        parts.append("Ton profil est déjà très aligné : mise sur la préparation d'entretien et le réseau.")
    parts.append(
        f"En suivant le plan proposé, tu peux viser environ {projected}/100 et surtout "
        "arriver avec des preuves concrètes, ce que les recruteurs regardent en premier."
    )
    return " ".join(parts)


def local_cv_tips(result: dict, profile: dict, job: dict) -> list[str]:
    tips: list[str] = []
    keywords = result.get("keywords", [])
    if keywords:
        tips.append(f"Intègre ces mots-clés naturellement dans tes puces : {', '.join(keywords[:8])}.")
    tips.append("Quantifie chaque réalisation : pourcentage, nombre, budget, délai ou volume.")
    for gap in result.get("gaps", [])[:3]:
        if gap["type"] == "competence":
            tips.append(
                f"Crée une puce dédiée à « {gap['skill']} » : même un projet académique compte "
                "s'il est décrit avec une action et un résultat."
            )
    tips.append("Place les compétences les plus attendues par l'offre dans les 6 premières lignes du CV.")
    if profile.get("cv", {}).get("text"):
        tips.append("Mets ton CV en une page si tu as moins de 2 ans d'expérience, et supprime les mentions inutiles.")
    return tips[:5]


def local_interview_tips(result: dict, profile: dict, job: dict) -> list[str]:
    tips: list[str] = []
    top_skills = [d["skill"] for d in result.get("skills_detail", []) if d["coverage"] >= 0.85][:3]
    if top_skills:
        tips.append(f"Prépare une histoire STAR pour chacune de ces forces : {', '.join(top_skills)}.")
    for gap in result.get("gaps", [])[:2]:
        if gap["type"] == "competence":
            tips.append(
                f"Anticipe la question sur « {gap['skill']} » : montre ce que tu as déjà fait, "
                "ce que tu apprends actuellement et comment en 30 jours tu deviens opérationnel."
            )
    tips.append("Prépare 2 questions sur les missions réelles et les indicateurs de succès du poste.")
    languages = [d for d in result.get("languages_detail", []) if d["status"] != "acquise"]
    if languages:
        tips.append("Entraîne-toi à présenter ton parcours en anglais en 2 minutes, sans lire tes notes.")
    tips.append("Envoie un message de remerciement personnalisé dans les 24 h après chaque entretien.")
    return tips[:5]


def enrich_analysis(result: dict, profile: dict, job: dict) -> dict:
    """Ajoute le plan, le récit, les conseils et le score projeté à l'analyse."""
    result["plan"] = build_plan(result, profile, job)
    result["projected_score"] = simulate_improvement(result, profile, job)
    result["narrative"] = local_narrative(result, profile, job)
    result["cv_tips"] = local_cv_tips(result, profile, job)
    result["interview_tips"] = local_interview_tips(result, profile, job)
    return result
