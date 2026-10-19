"""Catalogue de formations, certifications et idées de projets.

Ces ressources alimentent le plan d'amélioration généré pour chaque lacune.
Les URL pointent vers des ressources reconnues (Coursera, OpenClassrooms,
Coursera, Skillshop, Microsoft Learn, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Course:
    title: str
    provider: str
    url: str
    duration: str
    price: str
    level: str
    skills: tuple[str, ...]
    kind: str = "Formation"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Certification:
    name: str
    issuer: str
    url: str
    skills: tuple[str, ...]
    aliases: tuple[str, ...] = ()
    flexibility: str = "Préparée en 4 à 10 semaines"

    def to_dict(self) -> dict:
        return asdict(self)


def _c(title: str, provider: str, url: str, duration: str, price: str, level: str,
       skills: tuple[str, ...], kind: str = "Formation") -> Course:
    return Course(title, provider, url, duration, price, level, skills, kind)


# --------------------------------------------------------------------------- #
# Formations par compétence
# --------------------------------------------------------------------------- #

COURSES: list[Course] = [
    # Programmation
    _c("Apprenez les bases du langage Python", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7168871-apprenez-les-bases-du-langage-python",
       "10 h", "Gratuit", "Débutant", ("Python",)),
    _c("Scientific Computing with Python", "freeCodeCamp",
       "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
       "35 h", "Gratuit", "Intermédiaire", ("Python", "Algorithmique")),
    _c("Python for Data Science", "Coursera — IBM",
       "https://www.coursera.org/learn/python-for-applied-data-science-ai",
       "20 h", "Audit gratuit", "Débutant", ("Python", "Pandas", "Analyse de données")),
    _c("Maîtrisez les requêtes SQL", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/6971126-modelisez-vos-donnees-avec-une-base-de-donnees-sql",
       "8 h", "Gratuit", "Débutant", ("SQL",)),
    _c("SQL for Data Science", "Coursera — UC Davis",
       "https://www.coursera.org/learn/sql-for-data-science",
       "14 h", "Audit gratuit", "Débutant", ("SQL", "Analyse de données")),
    _c("SQLBolt — Interactive SQL lessons", "SQLBolt",
       "https://sqlbolt.com/", "3 h", "Gratuit", "Débutant", ("SQL",)),
    _c("Apprenez à programmer en JavaScript", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7696886-apprenez-a-programmer-avec-javascript",
       "20 h", "Gratuit", "Débutant", ("JavaScript", "HTML/CSS")),
    _c("Responsive Web Design", "freeCodeCamp",
       "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
       "30 h", "Gratuit", "Débutant", ("HTML/CSS", "Accessibilité", "UI Design")),
    _c("Développez une application web avec React", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7008001-developpez-avec-react",
       "25 h", "Gratuit", "Intermédiaire", ("React", "JavaScript", "HTML/CSS")),
    _c("Meta Front-End Developer", "Coursera — Meta",
       "https://www.coursera.org/professional-certificates/meta-front-end-developer",
       "7 mois", "Certifiant payant", "Débutant", ("React", "JavaScript", "HTML/CSS", "Git")),
    _c("Git & GitHub : la base indispensable", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7162856-gerez-du-code-avec-git-et-github",
       "6 h", "Gratuit", "Débutant", ("Git",)),
    _c("Concevez votre API REST", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/6573181-adoptez-les-api-rest-pour-vos-projets-web",
       "10 h", "Gratuit", "Intermédiaire", ("API REST", "Python", "Node.js")),
    _c("Django : développez des applications web", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7172076-developpez-une-application-web-avec-django",
       "25 h", "Gratuit", "Intermédiaire", ("Django", "Python", "SQL", "API REST")),
    _c("TypeScript for Beginners", "Total TypeScript",
       "https://www.totaltypescript.com/tutorials/beginners-typescript",
       "4 h", "Gratuit", "Débutant", ("TypeScript", "JavaScript")),
    # Data & IA
    _c("Initiez-vous à Excel", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7168336-maitrisez-les-fondamentaux-d-excel",
       "6 h", "Gratuit", "Débutant", ("Excel",)),
    _c("Excel Skills for Business", "Coursera — Macquarie",
       "https://www.coursera.org/specializations/excel",
       "6 mois", "Audit gratuit", "Débutant", ("Excel", "Power Query", "Analyse de données")),
    _c("Analysez vos données avec Power BI", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7110891-realisez-des-tableaux-de-bord-avec-power-bi",
       "12 h", "Gratuit", "Intermédiaire", ("Power BI", "Data visualisation", "Reporting")),
    _c("Get started with Power BI", "Microsoft Learn",
       "https://learn.microsoft.com/fr-fr/training/paths/get-started-power-bi/",
       "8 h", "Gratuit", "Débutant", ("Power BI", "Data visualisation")),
    _c("Data Visualization with Tableau", "Coursera — UC Davis",
       "https://www.coursera.org/specializations/data-visualization",
       "5 mois", "Audit gratuit", "Débutant", ("Tableau", "Data visualisation")),
    _c("Introduction aux statistiques", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7411626-initiez-vous-aux-statistiques",
       "8 h", "Gratuit", "Débutant", ("Statistiques", "Analyse de données")),
    _c("Statistics with R", "Coursera — Duke",
       "https://www.coursera.org/specializations/statistics",
       "5 mois", "Audit gratuit", "Intermédiaire", ("Statistiques", "R")),
    _c("Pandas : manipulez vos données", "Kaggle Learn",
       "https://www.kaggle.com/learn/pandas",
       "4 h", "Gratuit", "Débutant", ("Pandas", "Python", "Analyse de données")),
    _c("Intro to Machine Learning", "Kaggle Learn",
       "https://www.kaggle.com/learn/intro-to-machine-learning",
       "4 h", "Gratuit", "Débutant", ("Machine Learning", "Scikit-learn", "Python")),
    _c("Machine Learning Specialization", "Coursera — DeepLearning.AI & Stanford",
       "https://www.coursera.org/specializations/machine-learning-introduction",
       "2-3 mois", "Audit gratuit", "Intermédiaire", ("Machine Learning", "Scikit-learn", "Statistiques")),
    _c("Deep Learning Specialization", "Coursera — DeepLearning.AI",
       "https://www.coursera.org/specializations/deep-learning",
       "3 mois", "Audit gratuit", "Avancé", ("Deep Learning", "TensorFlow", "PyTorch")),
    _c("Hugging Face NLP Course", "Hugging Face",
       "https://huggingface.co/learn/nlp-course",
       "20 h", "Gratuit", "Intermédiaire", ("NLP", "LLM", "Deep Learning")),
    _c("ChatGPT Prompt Engineering for Developers", "DeepLearning.AI",
       "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/",
       "2 h", "Gratuit", "Débutant", ("Prompt Engineering", "LLM")),
    _c("PyTorch for Deep Learning", "freeCodeCamp",
       "https://www.youtube.com/watch?v=V_xro1bcAuA",
       "25 h", "Gratuit", "Intermédiaire", ("PyTorch", "Deep Learning")),
    _c("Data Engineering Foundations", "Coursera — IBM",
       "https://www.coursera.org/professional-certificates/ibm-data-engineer",
       "5 mois", "Certifiant payant", "Intermédiaire", ("ETL", "SQL", "Python", "Big Data")),
    # Design & UX
    _c("Prenez en main Figma", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7936891-creez-une-maquette-avec-figma",
       "8 h", "Gratuit", "Débutant", ("Figma", "Prototypage", "UI Design")),
    _c("Google UX Design", "Coursera — Google",
       "https://www.coursera.org/professional-certificates/google-ux-design",
       "6 mois", "Certifiant payant", "Débutant", ("UX Research", "UI Design", "Figma", "Prototypage")),
    _c("Concevez une interface utilisateur", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/6212351-concevez-une-interface-utilisateur-mobile",
       "15 h", "Gratuit", "Intermédiaire", ("UI Design", "Figma", "Accessibilité")),
    _c("Design Systems avec Figma", "freeCodeCamp",
       "https://www.freecodecamp.org/news/how-to-build-a-design-system-with-figma/",
       "3 h", "Gratuit", "Intermédiaire", ("Design System", "Figma", "UI Design")),
    _c("Accessibilité numérique : les bases", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/6691346-concevez-un-contenu-web-accessible",
       "6 h", "Gratuit", "Débutant", ("Accessibilité", "HTML/CSS", "UI Design")),
    # Marketing & Croissance
    _c("Réussir son référencement naturel (SEO)", "Google Skillshop",
       "https://skillshop.withgoogle.com/", "4 h", "Gratuit", "Débutant", ("SEO", "Content Marketing")),
    _c("Google Ads Search Certification", "Google Skillshop",
       "https://skillshop.withgoogle.com/", "6 h", "Gratuit", "Débutant", ("Google Ads", "SEA")),
    _c("Google Analytics Certification", "Google Skillshop",
       "https://skillshop.withgoogle.com/", "5 h", "Gratuit", "Débutant", ("Analytics", "Looker Studio")),
    _c("Rédigez pour le web", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/4929476-redigez-pour-le-web",
       "8 h", "Gratuit", "Débutant", ("Copywriting", "Content Marketing", "SEO")),
    _c("Content Marketing Certification", "HubSpot Academy",
       "https://academy.hubspot.com/courses/content-marketing",
       "6 h", "Gratuit", "Débutant", ("Content Marketing", "Copywriting", "SEO")),
    _c("Social Media Marketing", "HubSpot Academy",
       "https://academy.hubspot.com/courses/social-media",
       "5 h", "Gratuit", "Débutant", ("Réseaux sociaux", "Content Marketing", "Meta Ads")),
    _c("Marketing digital", "Google Ateliers Numériques",
       "https://learndigital.withgoogle.com/ateliersnumeriques",
       "30 h", "Gratuit", "Débutant", ("SEO", "Analytics", "Réseaux sociaux", "Email marketing")),
    _c("Email Marketing Certification", "HubSpot Academy",
       "https://academy.hubspot.com/courses/email-marketing",
       "4 h", "Gratuit", "Débutant", ("Email marketing", "Marketing Automation", "CRM")),
    _c("Salesforce Trailhead — Administrateur", "Salesforce",
       "https://trailhead.salesforce.com/", "20 h", "Gratuit", "Débutant", ("CRM", "Salesforce")),
    # Gestion & Produit
    _c("Initiez-vous à la gestion de projet", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/4452741-initiez-vous-a-la-gestion-de-projet",
       "8 h", "Gratuit", "Débutant", ("Gestion de projet", "Organisation")),
    _c("Google Project Management", "Coursera — Google",
       "https://www.coursera.org/professional-certificates/google-project-management",
       "6 mois", "Certifiant payant", "Débutant", ("Gestion de projet", "Agile/Scrum", "Reporting")),
    _c("Scrum : les fondamentaux", "Scrum.org",
       "https://www.scrum.org/resources/scrum-guide", "4 h", "Gratuit", "Débutant", ("Agile/Scrum", "Gestion de projet")),
    _c("Product Management Fundamentals", "Coursera — University of Maryland",
       "https://www.coursera.org/learn/product-management-fundamentals",
       "15 h", "Audit gratuit", "Débutant", ("Product Discovery", "Roadmap", "UX Research")),
    _c("Jira et Confluence : les bases", "Atlassian University",
       "https://university.atlassian.com/student/catalog",
       "5 h", "Gratuit", "Débutant", ("Jira", "Agile/Scrum", "Gestion de projet")),
    _c("Comptabilité générale", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7332396-initiez-vous-a-la-comptabilite",
       "10 h", "Gratuit", "Débutant", ("Comptabilité", "Analyse financière")),
    _c("Analyse financière", "Coursera — IESE",
       "https://www.coursera.org/learn/finance-for-non-finance-professionals",
       "12 h", "Audit gratuit", "Débutant", ("Analyse financière", "Contrôle de gestion", "Excel")),
    # Outils & Cloud
    _c("Prenez en main Linux", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7176551-installez-et-configurez-une-machine-linux",
       "12 h", "Gratuit", "Débutant", ("Linux", "Scripting", "Administration système")),
    _c("Docker : démarrez avec les conteneurs", "Docker",
       "https://docs.docker.com/get-started/", "6 h", "Gratuit", "Débutant", ("Docker", "CI/CD", "Linux")),
    _c("Kubernetes pour les débutants", "KodeKloud",
       "https://kodekloud.com/courses/kubernetes-for-beginners/",
       "12 h", "Payant", "Intermédiaire", ("Kubernetes", "Docker", "Cloud")),
    _c("AWS Cloud Practitioner Essentials", "AWS Skill Builder",
       "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
       "12 h", "Gratuit", "Débutant", ("AWS", "Cloud")),
    _c("Introduction to Cybersecurity", "Cisco Networking Academy",
       "https://www.netacad.com/courses/cybersecurity/introduction-cybersecurity",
       "6 h", "Gratuit", "Débutant", ("Cybersécurité", "Réseaux")),
    _c("Cybersecurity Essentials", "Cisco Networking Academy",
       "https://www.netacad.com/courses/cybersecurity/cybersecurity-essentials",
       "30 h", "Gratuit", "Intermédiaire", ("Cybersécurité", "Réseaux", "SIEM")),
    _c("TryHackMe — Cyber Security 101", "TryHackMe",
       "https://tryhackme.com/path/outline/cybersecurity101",
       "20 h", "Freemium", "Débutant", ("Cybersécurité", "Linux", "SIEM")),
    _c("Introduction aux réseaux", "Cisco Networking Academy",
       "https://www.netacad.com/courses/networking/networking-basics",
       "25 h", "Gratuit", "Débutant", ("Réseaux", "Administration système")),
    # Soft skills & langues
    _c("Communication efficace au travail", "Coursera — Google",
       "https://www.coursera.org/learn/effective-communication",
       "10 h", "Audit gratuit", "Débutant", ("Communication", "Prise de parole")),
    _c("Travail en équipe et collaboration", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/6378866-travaillez-en-equipe-a-distance",
       "4 h", "Gratuit", "Débutant", ("Travail en équipe", "Communication", "Organisation")),
    _c("Prise de parole en public", "Coursera — University of Washington",
       "https://www.coursera.org/learn/public-speaking",
       "12 h", "Audit gratuit", "Débutant", ("Prise de parole", "Communication")),
    _c("English for Career Development", "Coursera — Penn",
       "https://www.coursera.org/learn/career-development-english",
       "20 h", "Audit gratuit", "Intermédiaire", ("Communication", "Anglais")),
    _c("Améliorez votre anglais professionnel", "OpenClassrooms",
       "https://openclassrooms.com/fr/courses/7750151-developpez-votre-anglais-professionnel",
       "10 h", "Gratuit", "Intermédiaire", ("Anglais", "Communication")),
]


def courses_for(skill: str, limit: int = 3) -> list[Course]:
    """Retourne les formations liées à une compétence (correspondance exacte puis proche)."""
    exact = [c for c in COURSES if skill in c.skills]
    if exact:
        return exact[:limit]
    # Compétences liées
    from .data_skills import SKILLS

    related = SKILLS.get(skill, {}).get("related", {})
    related_names = sorted(related, key=related.get, reverse=True)
    found: list[Course] = []
    for name in related_names:
        for course in COURSES:
            if name in course.skills and course not in found:
                found.append(course)
        if len(found) >= limit:
            break
    return found[:limit]


def search_fallback(skill: str) -> list[Course]:
    """Propose des recherches génériques quand aucune formation curatée n'existe."""
    from urllib.parse import quote_plus

    q = quote_plus(skill)
    return [
        Course(f"Trouver une formation « {skill} »", "Coursera",
               f"https://www.coursera.org/search?query={q}", "Variable", "Audit gratuit",
               "Tous niveaux", (skill,), "Recherche"),
        Course(f"Trouver un cours « {skill} »", "OpenClassrooms",
               f"https://openclassrooms.com/fr/search?query={q}", "Variable", "Gratuit",
               "Tous niveaux", (skill,), "Recherche"),
        Course(f"Tutoriels « {skill} »", "YouTube",
               f"https://www.youtube.com/results?search_query={q}+tutoriel+francais",
               "Variable", "Gratuit", "Tous niveaux", (skill,), "Vidéo"),
    ]


# --------------------------------------------------------------------------- #
# Certifications
# --------------------------------------------------------------------------- #

CERTIFICATIONS: list[Certification] = [
    Certification("Google Data Analytics Professional Certificate", "Google / Coursera",
                  "https://www.coursera.org/professional-certificates/google-data-analytics",
                  ("Excel", "SQL", "Tableau", "Data visualisation", "Analyse de données", "Reporting"),
                  ("google data analytics", "certificat google data analytics", "google data")),
    Certification("Microsoft Certified: Power BI Data Analyst (PL-300)", "Microsoft",
                  "https://learn.microsoft.com/fr-fr/credentials/certifications/power-bi-data-analyst-associate/",
                  ("Power BI", "Data visualisation", "Analyse de données", "Reporting"),
                  ("pl-300", "power bi data analyst", "microsoft power bi")),
    Certification("AWS Certified Cloud Practitioner", "Amazon Web Services",
                  "https://aws.amazon.com/fr/certification/certified-cloud-practitioner/",
                  ("AWS", "Cloud"), ("cloud practitioner", "aws certified", "aws ccp")),
    Certification("CompTIA Security+", "CompTIA",
                  "https://www.comptia.org/fr/certifications/security",
                  ("Cybersécurité", "Réseaux", "SIEM"), ("security+", "comptia security")),
    Certification("Cisco Certified Network Associate (CCNA)", "Cisco",
                  "https://www.cisco.com/site/us/en/learn/training-certifications/certifications/enterprise/ccna/index.html",
                  ("Réseaux", "Cybersécurité", "Administration système"), ("ccna", "cisco certified")),
    Certification("Professional Scrum Master I (PSM I)", "Scrum.org",
                  "https://www.scrum.org/assessments/professional-scrum-master-i-certification",
                  ("Agile/Scrum", "Gestion de projet"), ("psm", "scrum master", "scrum.org")),
    Certification("Google Project Management Professional Certificate", "Google / Coursera",
                  "https://www.coursera.org/professional-certificates/google-project-management",
                  ("Gestion de projet", "Agile/Scrum", "Reporting", "Communication"),
                  ("google project management", "certificat gestion de projet google")),
    Certification("Google UX Design Professional Certificate", "Google / Coursera",
                  "https://www.coursera.org/professional-certificates/google-ux-design",
                  ("UX Research", "UI Design", "Figma", "Prototypage", "Accessibilité"),
                  ("google ux", "certificat ux google")),
    Certification("Google Digital Marketing & E-commerce", "Google / Coursera",
                  "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce",
                  ("SEO", "Google Ads", "Analytics", "Email marketing", "Réseaux sociaux"),
                  ("google digital marketing", "marketing digital google")),
    Certification("Google Analytics Certification (GA4)", "Google Skillshop",
                  "https://skillshop.withgoogle.com/",
                  ("Analytics", "Looker Studio", "A/B testing"), ("google analytics", "ga4 certification")),
    Certification("Google Ads Search Certification", "Google Skillshop",
                  "https://skillshop.withgoogle.com/", ("Google Ads", "SEA"), ("google ads", "adwords")),
    Certification("HubSpot Content Marketing Certification", "HubSpot Academy",
                  "https://academy.hubspot.com/courses/content-marketing",
                  ("Content Marketing", "Copywriting", "SEO"), ("hubspot content marketing", "inbound marketing")),
    Certification("Meta Certified Digital Marketing Associate", "Meta",
                  "https://www.facebook.com/business/learn/certification",
                  ("Meta Ads", "Réseaux sociaux", "Analytics"), ("meta blueprint", "meta certified")),
    Certification("Salesforce Certified Administrator", "Salesforce",
                  "https://trailhead.salesforce.com/credentials/administrator",
                  ("Salesforce", "CRM"), ("salesforce admin", "salesforce administrator")),
    Certification("TOEIC", "ETS Global",
                  "https://www.etsglobal.org/fr/fr/programmes/tests/toeic-tests",
                  ("Anglais",), ("toeic",), "Score visé : 785+ (B2) à 945+ (C1)"),
    Certification("IELTS", "British Council / IDP",
                  "https://www.ielts.org/", ("Anglais",), ("ielts",), "Score visé : 6.5+ (B2/C1)"),
    Certification("TOEFL iBT", "ETS",
                  "https://www.ets.org/toefl.html", ("Anglais",), ("toefl",), "Score visé : 90+ (B2/C1)"),
    Certification("CAPM — Certified Associate in Project Management", "PMI",
                  "https://www.pmi.org/certifications/certified-associate-capm",
                  ("Gestion de projet", "Agile/Scrum"), ("capm",)),
]

CERT_ALIAS_INDEX: dict[str, Certification] = {}
for _cert in CERTIFICATIONS:
    CERT_ALIAS_INDEX[_cert.name.lower()] = _cert
    for _alias in _cert.aliases:
        CERT_ALIAS_INDEX[_alias.lower()] = _cert


# --------------------------------------------------------------------------- #
# Idées de projets par compétence
# --------------------------------------------------------------------------- #

PROJECT_IDEAS: dict[str, str] = {
    "Python": "un script qui nettoie et analyse un jeu de données public (data.gouv.fr), publié sur GitHub avec un README clair",
    "SQL": "une base de données d'entreprise fictive : crée les tables, insère des données et écris 10 requêtes d'analyse commentées",
    "Excel": "un tableau de bord budgétaire automatisé avec segments, formules et un onglet de synthèse",
    "Power BI": "un rapport Power BI de 3 pages connecté à un fichier Excel, avec mesures DAX et narratif",
    "Tableau": "un tableau de bord interactif sur un jeu de données ouvert (santé, transport, sport)",
    "Pandas": "un notebook d'analyse exploratoire complet : nettoyage, statistiques descriptives et 5 visualisations",
    "Statistiques": "une étude A/B simulée : hypothèses, test statistique, interprétation et recommandation",
    "Machine Learning": "un modèle de prédiction entraîné sur Kaggle, avec comparaison de 3 algorithmes et matrice de confusion",
    "Deep Learning": "un petit réseau de neurones de classification d'images ou de texte, entraîné et documenté",
    "NLP": "un prototype qui classe ou résume des avis clients en français avec un modèle Hugging Face",
    "LLM": "un assistant documentaire qui répond à des questions sur une base d'articles avec un modèle de langage",
    "Prompt Engineering": "un guide de 10 prompts testés et comparés pour automatiser une tâche métier",
    "PyTorch": "un modèle PyTorch commenté, avec boucle d'entraînement, évaluation et visualisations",
    "ETL": "un pipeline qui récupère une API publique, la transforme et charge les données dans une base SQL",
    "Figma": "la refonte de 3 écrans d'une application réelle, avec maquettes avant/après et principes de design expliqués",
    "UX Research": "un mini-rapport de recherche utilisateur : 5 entretiens, synthèse, personas et recommandations",
    "UI Design": "une interface mobile complète en mode clair/sombre avec une documentation des choix graphiques",
    "Prototypage": "un prototype cliquable Figma de 8 écrans testé auprès de 3 utilisateurs, avec itérations",
    "Design System": "un mini design system : couleurs, typographies, 12 composants et leurs états",
    "Accessibilité": "un audit d'accessibilité de 2 sites avec relevé des problèmes RGAA et propositions de correction",
    "JavaScript": "une application web interactive (quiz, budget, météo) en JavaScript vanilla, déployée en ligne",
    "React": "une application React de gestion de tâches ou de suivi de dépenses, avec API et déploiement Vercel",
    "TypeScript": "la migration d'un projet JavaScript vers TypeScript, avec typage strict documenté",
    "Git": "un dépôt GitHub bien structuré : commits conventionnels, branches, pull request et README",
    "API REST": "une API REST documentée avec Swagger, tests et déploiement sur un service cloud gratuit",
    "HTML/CSS": "un site vitrine responsive et accessible (Lighthouse > 95) hébergé sur GitHub Pages",
    "SEO": "un audit SEO complet d'un site : mots-clés, structure, contenu et plan d'action priorisé",
    "Google Ads": "une simulation de campagne Google Ads : structure, annonces, mots-clés et budget prévisionnel",
    "Analytics": "un tableau de bord GA4 connecté à un site de test, avec 5 KPI et une recommandation",
    "Content Marketing": "un calendrier éditorial de 4 semaines et 3 articles publiés sur un blog ou LinkedIn",
    "Copywriting": "un portfolio de 5 textes optimisés (landing page, email, post LinkedIn) avec avant/après",
    "Réseaux sociaux": "un plan de contenu de 30 jours pour une marque fictive, avec visuels et indicateurs",
    "Email marketing": "une séquence de 5 emails automatisée dans Brevo/Mailchimp, avec test A/B d'objet",
    "CRM": "un mini CRM Salesforce/Trailhead configuré avec pipeline, rapports et automatisations",
    "Gestion de projet": "un projet encadré de bout en bout : périmètre, planning Gantt, budget, risques et bilan",
    "Agile/Scrum": "la simulation d'un sprint : backlog, user stories, estimation, daily et rétrospective documentée",
    "Product Discovery": "une discovery produit complète : problème, recherche, hypothèses et MVP priorisé",
    "Roadmap": "une roadmap produit sur 6 mois avec priorisation RICE expliquée",
    "Jira": "un projet Jira complet : backlog, sprint, workflows et tableau de bord d'avancement",
    "Reporting": "un reporting automatisé de 4 KPI avec graphiques et commentaires de tendance",
    "Analyse financière": "un business plan simplifié sur 3 ans : hypothèses, compte de résultat, trésorerie et ratios",
    "Comptabilité": "un jeu d'écritures complet et un bilan/ compte de résultat commenté pour une PME fictive",
    "Contrôle de gestion": "un budget prévisionnel et un analyse d'écarts sur 6 mois, avec recommandations",
    "Linux": "un serveur Linux configuré de A à Z (utilisateurs, services, sauvegardes), documenté",
    "Docker": "une application conteneurisée avec Dockerfile et docker-compose, publiée sur GitHub",
    "Kubernetes": "un déploiement Kubernetes local (minikube) d'une application avec scaling et health checks",
    "CI/CD": "un pipeline GitHub Actions qui teste, construit et déploie automatiquement une application",
    "Cloud": "un projet déployé sur AWS ou GCP avec architecture, coûts estimés et captures d'écran",
    "Terraform": "une infrastructure as code décrite en Terraform pour un site statique + base de données",
    "Réseaux": "une maquette réseau Packet Tracer documentée : VLAN, routage, DHCP et sécurité",
    "Cybersécurité": "un rapport de tests d'intrusion éthiques sur une machine vulnérable (TryHackMe), avec remédiations",
    "SIEM": "un mini laboratoire SIEM (Splunk/Elastic) : ingestion de logs, 3 règles et 2 tableaux de bord",
    "Administration système": "un environnement virtualisé avec Active Directory, GPO et script d'automatisation",
    "Communication": "un pitch de 2 minutes et une présentation de 5 slides sur ton projet le plus abouti",
    "Travail en équipe": "un projet collaboratif documenté : rôles, outils, rituels et bilan d'équipe",
    "Autonomie": "un projet mené seul de l'idée au résultat, avec un journal de bord des décisions",
    "Rigueur": "une checklist qualité + une procédure de relecture appliquée à un de tes livrables",
    "Curiosité": "une veille de 4 semaines : 8 sources suivies, 4 fiches de synthèse publiées",
    "Créativité": "un portfolio de 3 concepts originaux répondant à un même brief, avec argumentation",
    "Esprit d'analyse": "une étude de cas chiffrée : problème, données, analyse, recommandation et limites",
    "Esprit critique": "une analyse contradictoire : 2 sources opposées, hypothèses, biais et conclusion nuancée",
    "Organisation": "un système de gestion de tâches (Notion/Trello) + un planning de 4 semaines respecté",
    "Adaptabilité": "un retour d'expérience sur un changement de périmètre ou d'outil géré en cours de projet",
    "Leadership": "l'organisation d'un événement ou d'un projet associatif avec une équipe de 3 personnes",
    "Prise de parole": "3 vidéos de 3 minutes te présentant et présentant un projet, avec auto-évaluation",
    "Gestion du stress": "un plan de gestion de charge (priorités, pauses, escalade) testé pendant 3 semaines",
    "Sens du détail": "une grille de relecture utilisée pour corriger un livrable réel, avec les erreurs trouvées",
    "Négociation": "une simulation d'offre et de négociation salariale écrite, avec arguments et concessions",
    "Relation client": "un parcours client cartographié avec points de friction et 3 améliorations proposées",
}


def project_idea(skill: str) -> str:
    if skill in PROJECT_IDEAS:
        return PROJECT_IDEAS[skill]
    # Repli générique
    return (f"un mini-projet concret de 2 à 3 semaines mettant en œuvre « {skill} », "
            "publié sur GitHub ou dans un portfolio avec une fiche de synthèse de 5 lignes")
