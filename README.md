# 🌱 Tremplin

**Trouve le stage (ou le premier poste) où ton profil fait la différence.**

Tremplin est une application web en français, pensée pour les **étudiants au Maroc** : tu décris ton parcours (CV, compétences, projets, langues, certifications), tu choisis une offre cible — ou tu colles la tienne — et l'application te renvoie :

- un **score de compatibilité** expliqué (5 sous-scores pondérés selon le domaine du poste) ;
- tes **lacunes priorisées** avec le gain de points potentiel ; 
- un **plan d'action personnalisé 7 / 30 / 90 jours**, avec formations réelles, certifications et projets concrets.

## Démarrage rapide

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

L'application s'ouvre sur http://localhost:8501. Aucune clé API n'est nécessaire : le moteur d'analyse est **100 % local**.

> Astuce : sur le tableau de bord, clique sur **« Charger le profil de démo »** pour explorer toutes les fonctionnalités en 10 secondes.

## Fonctionnalités

| Écran | Ce que tu y fais |
| --- | --- |
| 🏠 Tableau de bord | Progression du profil, dernière analyse, offres où tu performes déjà |
| 👤 Mon profil | Identité, formation, compétences, projets & expériences, langues, certifications + **import de CV** (PDF, DOCX, TXT) avec détection automatique |
| 🎯 Offres & cibles | Catalogue filtrable (18 offres : sociétés marocaines + quelques offres à l'international), score estimé instantané, détail des exigences, **offre personnalisée collée** puis analysée |
| 📊 Analyse | Score, radar des sous-scores, tableau des compétences, points forts, lacunes, conseils CV / entretien, exports Markdown & HTML |
| 🗺️ Plan d'action | Sprints 7 / 30 / 90 jours avec cases à cocher persistées, formations liées, progression et score visé |
| ⚙️ Réglages | IA générative optionnelle, export / import / suppression des données, méthode de calcul |

## Comment le score est calculé

Chaque offre est décodée en exigences : compétences (niveau attendu 1–5 + importance), qualités, langues (CECR), formation et certifications. Ton profil est comparé exigence par exigence, en tenant compte des **preuves** (CV importé, projets, expériences) — déclarer une compétence ne suffit pas, la prouver vaut mieux.

Cinq sous-scores sont pondérés selon le domaine du poste :

- **Compétences** (35–45 %) · **Qualités** (12–18 %) · **Projets & expérience** (20 %) · **Langues** (10 %) · **Formation & certifications** (13–17 %).

Le résultat inclut un indice de **confiance** (finesse des données fournies) et un **score projeté** si tu suis le plan. Le moteur est déterministe et explicable : chaque écart est justifiable.

## IA générative (optionnelle)

Par défaut, tout fonctionne hors ligne. Si tu veux un récit personnalisé, des questions d'entretien probables et un pitch de candidature, active un fournisseur dans **Réglages → Intelligence artificielle** : OpenAI, Mistral, Groq, OpenRouter, Gemini, **Ollama** (local, sans clé) ou toute API compatible `/chat/completions`.

- La clé API reste en session ou dans une variable d'environnement (`OPENAI_API_KEY`, `MISTRAL_API_KEY`, etc.) — **jamais écrite sur le disque**.
- L'IA **ne modifie jamais le score** : elle commente uniquement les faits calculés par le moteur.

## Confidentialité

En local, profil, analyses et progression sont enregistrés dans `data/state.json`, sur ta machine uniquement. En ligne (Streamlit Community Cloud), rien n'est écrit sur le serveur : chaque visiteur a sa **propre session**, en mémoire. Aucun compte, aucune télémétrie. Tu peux tout exporter ou tout effacer depuis l'onglet **Données & confidentialité**.

## Déployer sur Streamlit Community Cloud

1. Pousse le dépôt sur GitHub (branche `main`).
2. Va sur [share.streamlit.io](https://share.streamlit.io) → **Create app** → choisis le dépôt, la branche `main` et le fichier principal `app.py`.
3. Clique sur **Deploy** : les dépendances de `requirements.txt` sont installées automatiquement.

En ligne, chaque visiteur dispose de sa propre session (profil en mémoire, jamais partagé entre visiteurs). Pour l'IA optionnelle, chacun colle sa clé API dans **Réglages** — elle reste en session et n'est jamais stockée sur le serveur.

## Stack

- [Streamlit](https://streamlit.io) — interface
- Moteur de matching maison (pur Python, sans dépendance)
- `pypdf` + `python-docx` — import de CV
- `requests` — connexion IA optionnelle

## Structure

```
app.py                  # point d'entrée + navigation
tremplin/
  data_skills.py        # référentiel compétences, langues, formation
  data_jobs.py          # catalogue d'offres
  data_courses.py       # formations, certifications, idées de projets
  matching.py           # moteur de score et de lacunes
  planner.py            # plan 7 / 30 / 90 jours
  cv_parser.py          # extraction et détection CV
  llm.py                # connecteur IA optionnel
  storage.py            # état local (JSON)
  report.py             # exports Markdown / HTML
  ui.py                 # design system (CSS + composants)
  pages/                # dashboard, profil, offres, analyse, plan, réglages
```
