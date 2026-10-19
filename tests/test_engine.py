"""Test rapide du moteur, exécutable sans Streamlit.

Usage :  py tests/test_engine.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tremplin import report  # noqa: E402
from tremplin.data_jobs import JOBS, empty_custom_job  # noqa: E402
from tremplin.matching import (  # noqa: E402
    analyze,
    detect_education,
    detect_languages,
    extract_skills,
    simulate_improvement,
)
from tremplin.profile import demo_profile  # noqa: E402


def main() -> int:
    profile = demo_profile()
    print(f"Profil démo : {profile['identity']['name']} · {len(profile['skills'])} compétences")

    errors = 0
    for job in JOBS:
        try:
            result = analyze(profile, job)
            plan = result.get("plan", {})
            actions = sum(len(phase["actions"]) for phase in plan.get("phases", []))
            markdown = report.analysis_markdown(result, profile)
            html = report.analysis_html(result, profile)
            assert markdown and html, "exports vides"
            assert 0 <= result["score"] <= 100
            assert result["projected_score"] >= result["score"] or result["score"] > 90
            print(
                f"{job['id'][:30]:32s} score={result['score']:3d} conf={result['confidence']:2d} "
                f"gaps={len(result['gaps']):2d} actions={actions:2d} proj={result['projected_score']:3d}"
            )
        except Exception as exc:  # noqa: BLE001
            errors += 1
            import traceback

            print(f"ERREUR sur {job['id']}")
            traceback.print_exc()

    # Offre personnalisée minimale
    custom = empty_custom_job()
    custom.update({
        "title": "Data Analyst junior",
        "company": "Test",
        "domain": "Data & IA",
        "required_skills": [{"skill": "SQL", "level": 4, "weight": 3, "nature": "indispensable"}],
        "keywords": ["data analyst"],
    })
    custom_result = analyze(profile, custom)
    print(f"Offre personnalisée : score={custom_result['score']}")

    # Détections locales
    skills = extract_skills("Python, SQL, Power BI, React, RGPD")
    languages = detect_languages("Anglais B2, espagnol courant")
    education = detect_education("Master 1 en data science")
    print("Compétences détectées :", ", ".join(skills))
    print("Langues détectées :", languages)
    print("Formation détectée :", education)
    assert "SQL" in skills and "Python" in skills
    assert languages.get("Anglais") == "B2"
    assert languages.get("Espagnol") == "C1"
    assert education.get("level", "").startswith("Bac+4")

    # Pièges de détection
    assert detect_education("dashboard de synthèse et thèses de marché")["level"] != "Doctorat"
    assert detect_languages("Anglais B2, espagnol B1")["Espagnol"] == "B1"
    print("Pièges de détection : OK")

    print(f"\n{'OK' if errors == 0 else 'ECHEC'} — {errors} erreur(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
