"""Référentiel de compétences, qualités, langues et niveaux de formation.

Chaque compétence possède des alias (pour la détection dans un CV ou une
offre), une catégorie et des compétences liées utilisées par le moteur de
matching pour accorder des crédits partiels.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Catégories et niveaux
# --------------------------------------------------------------------------- #

SKILL_CATEGORIES = [
    "Programmation",
    "Data & IA",
    "Design & UX",
    "Marketing & Croissance",
    "Gestion & Produit",
    "Outils & Cloud",
    "Soft skills",
]

SKILL_LEVELS = {
    1: "Notions",
    2: "Débutant",
    3: "Intermédiaire",
    4: "Avancé",
    5: "Expert",
}

COVERAGE_LABELS = {
    "acquise": "Compétence acquise",
    "presque": "Presque acquise",
    "partielle": "Partiellement couverte",
    "manquante": "À acquérir",
}

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2", "Natif"]

CEFR_VALUE = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
    "Natif": 7,
}

EDUCATION_LEVELS = [
    "Bac",
    "Bac+2 (BTS / BUT2)",
    "Bac+3 (Licence / BUT3)",
    "Bac+4 (Master 1)",
    "Bac+5 (Master 2 / Ingénieur)",
    "Doctorat",
]

EDUCATION_VALUE = {
    "Bac": 1,
    "Bac+2 (BTS / BUT2)": 2,
    "Bac+3 (Licence / BUT3)": 3,
    "Bac+4 (Master 1)": 4,
    "Bac+5 (Master 2 / Ingénieur)": 5,
    "Doctorat": 6,
}

STUDY_FIELDS = [
    "Informatique & Développement",
    "Data & Intelligence artificielle",
    "Design & UX",
    "Marketing & Communication",
    "Gestion, Finance & Commerce",
    "Ingénierie & Sciences",
    "Sciences humaines & Social",
    "Droit & Administration",
    "Santé & Biologie",
    "Autre",
]

CONTRACT_TYPES = ["Stage", "Alternance", "CDI junior", "CDD / Freelance", "Peu importe"]

TARGET_DOMAINS = [
    "Data & IA",
    "Développement logiciel",
    "Design & UX",
    "Marketing & Communication",
    "Produit & Gestion de projet",
    "Finance & Conseil",
    "Cybersécurité & Cloud",
    "Ressources humaines",
    "Autre",
]


# --------------------------------------------------------------------------- #
# Référentiel de compétences
# --------------------------------------------------------------------------- #
# aliases : minuscules, sans accent (la normalisation est faite par le moteur)
# related : compétence proche -> crédit partiel (0 à 1)

SKILLS: dict[str, dict] = {
    # ----------------------------- Programmation --------------------------- #
    "Python": {
        "category": "Programmation",
        "aliases": ["python", "py", "python3"],
        "related": {"R": 0.35, "Scripting": 0.45, "Pandas": 0.5, "Django": 0.45, "Flask": 0.45},
    },
    "JavaScript": {
        "category": "Programmation",
        "aliases": ["javascript", "js", "es6", "ecmascript"],
        "related": {"TypeScript": 0.5, "React": 0.5, "Node.js": 0.45, "HTML/CSS": 0.3},
    },
    "TypeScript": {
        "category": "Programmation",
        "aliases": ["typescript", "ts"],
        "related": {"JavaScript": 0.6, "React": 0.4},
    },
    "Java": {
        "category": "Programmation",
        "aliases": ["java", "spring boot", "spring"],
        "related": {"C#": 0.35, "Programmation orientée objet": 0.5},
    },
    "C#": {"category": "Programmation", "aliases": ["c#", "csharp", ".net", "dotnet"], "related": {"Java": 0.35}},
    "C++": {"category": "Programmation", "aliases": ["c++", "cpp"], "related": {"C": 0.5, "Algorithmique": 0.4}},
    "PHP": {"category": "Programmation", "aliases": ["php", "laravel", "symfony"], "related": {"JavaScript": 0.25}},
    "Go": {"category": "Programmation", "aliases": ["golang", "go lang"], "related": {"Python": 0.3}},
    "R": {"category": "Programmation", "aliases": ["r", "rstudio", "tidyverse"], "related": {"Python": 0.35, "Statistiques": 0.5}},
    "SQL": {
        "category": "Programmation",
        "aliases": ["sql", "mysql", "postgresql", "postgres", "requetes sql", "bases de donnees", "base de donnees"],
        "related": {"Power BI": 0.25, "Analyse de données": 0.4, "ETL": 0.4},
    },
    "HTML/CSS": {
        "category": "Programmation",
        "aliases": ["html", "css", "html5", "css3", "sass", "scss", "tailwind"],
        "related": {"JavaScript": 0.3, "UI Design": 0.35, "Accessibilité": 0.4},
    },
    "React": {
        "category": "Programmation",
        "aliases": ["react", "react.js", "reactjs", "next.js", "nextjs"],
        "related": {"JavaScript": 0.6, "TypeScript": 0.45, "HTML/CSS": 0.3, "UI Design": 0.25},
    },
    "Node.js": {
        "category": "Programmation",
        "aliases": ["node", "node.js", "nodejs", "express", "nestjs"],
        "related": {"JavaScript": 0.6, "API REST": 0.5},
    },
    "Django": {"category": "Programmation", "aliases": ["django"], "related": {"Python": 0.6, "API REST": 0.5}},
    "Flask": {"category": "Programmation", "aliases": ["flask", "fastapi"], "related": {"Python": 0.6, "API REST": 0.5}},
    "API REST": {
        "category": "Programmation",
        "aliases": ["api", "api rest", "rest", "graphql", "web service", "web services"],
        "related": {"Node.js": 0.4, "Python": 0.35, "Django": 0.45},
    },
    "Git": {
        "category": "Programmation",
        "aliases": ["git", "github", "gitlab", "versioning", "gestion de versions"],
        "related": {},
    },
    "Tests unitaires": {
        "category": "Programmation",
        "aliases": ["tests unitaires", "test unitaire", "unit test", "pytest", "jest", "tdd"],
        "related": {"Python": 0.3, "JavaScript": 0.3, "Qualité de code": 0.5},
    },
    "Algorithmique": {
        "category": "Programmation",
        "aliases": ["algorithmique", "algorithmes", "structures de donnees"],
        "related": {"Python": 0.4, "C++": 0.35},
    },
    "Programmation orientée objet": {
        "category": "Programmation",
        "aliases": ["poo", "programmation orientee objet", "objet"],
        "related": {"Java": 0.5, "C#": 0.5, "Python": 0.4},
    },
    "Scripting": {
        "category": "Programmation",
        "aliases": ["scripting", "bash", "shell", "powershell", "script"],
        "related": {"Linux": 0.5, "Python": 0.5},
    },
    # ------------------------------ Data & IA ------------------------------ #
    "Excel": {
        "category": "Data & IA",
        "aliases": ["excel", "tableur", "vlookup", "recherchev", "tcd", "tableau croise dynamique"],
        "related": {"Power Query": 0.5, "VBA": 0.5, "Analyse de données": 0.35},
    },
    "Power Query": {
        "category": "Data & IA",
        "aliases": ["power query", "powerquery"],
        "related": {"Excel": 0.5, "Power BI": 0.5},
    },
    "VBA": {"category": "Data & IA", "aliases": ["vba", "macros excel"], "related": {"Excel": 0.6}},
    "Analyse de données": {
        "category": "Data & IA",
        "aliases": ["analyse de donnees", "analyse de donnee", "analyse data", "data analysis", "analyse exploratoire", "eda"],
        "related": {"Statistiques": 0.5, "SQL": 0.4, "Pandas": 0.45, "Data visualisation": 0.4},
    },
    "Statistiques": {
        "category": "Data & IA",
        "aliases": ["statistiques", "statistique", "stats", "probabilites", "tests statistiques", "regression"],
        "related": {"R": 0.4, "Python": 0.3, "Machine Learning": 0.45},
    },
    "Data visualisation": {
        "category": "Data & IA",
        "aliases": ["data visualisation", "dataviz", "visualisation de donnees", "visualisation", "dataviz"],
        "related": {"Power BI": 0.5, "Tableau": 0.5, "Excel": 0.35},
    },
    "Power BI": {
        "category": "Data & IA",
        "aliases": ["power bi", "powerbi", "dax"],
        "related": {"Data visualisation": 0.6, "Excel": 0.4, "SQL": 0.35},
    },
    "Tableau": {
        "category": "Data & IA",
        "aliases": ["tableau", "tableau software", "tableau desktop"],
        "related": {"Data visualisation": 0.6, "Power BI": 0.45},
    },
    "Looker Studio": {
        "category": "Data & IA",
        "aliases": ["looker", "looker studio", "data studio", "google data studio"],
        "related": {"Data visualisation": 0.5, "Analytics": 0.4},
    },
    "Pandas": {
        "category": "Data & IA",
        "aliases": ["pandas", "dataframe"],
        "related": {"Python": 0.6, "NumPy": 0.5, "Analyse de données": 0.5},
    },
    "NumPy": {"category": "Data & IA", "aliases": ["numpy", "scipy"], "related": {"Python": 0.6, "Pandas": 0.5}},
    "Scikit-learn": {
        "category": "Data & IA",
        "aliases": ["scikit-learn", "sklearn", "scikit learn"],
        "related": {"Machine Learning": 0.6, "Python": 0.5, "Pandas": 0.4},
    },
    "Machine Learning": {
        "category": "Data & IA",
        "aliases": ["machine learning", "ml", "apprentissage automatique", "modelisation predictive", "modeles predictifs"],
        "related": {"Statistiques": 0.5, "Python": 0.4, "Deep Learning": 0.5},
    },
    "Deep Learning": {
        "category": "Data & IA",
        "aliases": ["deep learning", "reseaux de neurones", "neural networks", "cnn", "rnn"],
        "related": {"Machine Learning": 0.6, "PyTorch": 0.5, "TensorFlow": 0.5},
    },
    "NLP": {
        "category": "Data & IA",
        "aliases": ["nlp", "traitement du langage naturel", "traitement automatique du langage", "tal"],
        "related": {"Machine Learning": 0.5, "Deep Learning": 0.5, "LLM": 0.55},
    },
    "LLM": {
        "category": "Data & IA",
        "aliases": ["llm", "large language model", "modeles de langage", "gpt", "transformers", "hugging face", "fine-tuning"],
        "related": {"NLP": 0.6, "Deep Learning": 0.5, "Prompt Engineering": 0.5},
    },
    "Prompt Engineering": {
        "category": "Data & IA",
        "aliases": ["prompt engineering", "prompt", "ingenierie de prompt"],
        "related": {"LLM": 0.6},
    },
    "PyTorch": {"category": "Data & IA", "aliases": ["pytorch", "torch"], "related": {"Deep Learning": 0.6, "Python": 0.5}},
    "TensorFlow": {"category": "Data & IA", "aliases": ["tensorflow", "keras"], "related": {"Deep Learning": 0.6, "Python": 0.5}},
    "ETL": {
        "category": "Data & IA",
        "aliases": ["etl", "elt", "data pipeline", "pipeline de donnees", "airflow", "dbt", "data engineering"],
        "related": {"SQL": 0.5, "Python": 0.4, "Big Data": 0.4},
    },
    "Big Data": {
        "category": "Data & IA",
        "aliases": ["big data", "spark", "hadoop", "databricks", "hive"],
        "related": {"ETL": 0.5, "SQL": 0.35, "Python": 0.3},
    },
    "MLOps": {
        "category": "Data & IA",
        "aliases": ["mlops", "ml ops", "deploiement de modeles", "model serving"],
        "related": {"Machine Learning": 0.45, "Docker": 0.5, "CI/CD": 0.4},
    },
    "A/B testing": {
        "category": "Data & IA",
        "aliases": ["a/b testing", "ab testing", "test a/b", "experimentation"],
        "related": {"Statistiques": 0.5, "Analytics": 0.5},
    },
    "Séries temporelles": {
        "category": "Data & IA",
        "aliases": ["series temporelles", "time series", "prevision"],
        "related": {"Statistiques": 0.5, "Machine Learning": 0.4},
    },
    # ----------------------------- Design & UX ----------------------------- #
    "Figma": {
        "category": "Design & UX",
        "aliases": ["figma", "maquette", "maquettes", "mockup"],
        "related": {"UI Design": 0.5, "Prototypage": 0.5, "Design System": 0.4},
    },
    "UX Research": {
        "category": "Design & UX",
        "aliases": ["ux research", "recherche utilisateur", "entretiens utilisateurs", "tests utilisateurs", "personas", "user research"],
        "related": {"UI Design": 0.4, "Product Discovery": 0.5, "Accessibilité": 0.35},
    },
    "UI Design": {
        "category": "Design & UX",
        "aliases": ["ui design", "interface utilisateur", "ui", "design d'interface"],
        "related": {"Figma": 0.5, "Design System": 0.45, "Accessibilité": 0.4},
    },
    "Prototypage": {
        "category": "Design & UX",
        "aliases": ["prototypage", "prototype", "wireframe", "wireframes", "maquette interactive"],
        "related": {"Figma": 0.6, "UI Design": 0.5},
    },
    "Design System": {
        "category": "Design & UX",
        "aliases": ["design system", "design systems", "composants ui", "charte graphique"],
        "related": {"Figma": 0.5, "UI Design": 0.5, "Accessibilité": 0.4},
    },
    "Accessibilité": {
        "category": "Design & UX",
        "aliases": ["accessibilite", "a11y", "rgaa", "wai", "inclusion"],
        "related": {"HTML/CSS": 0.45, "UI Design": 0.4},
    },
    "Adobe Photoshop": {
        "category": "Design & UX",
        "aliases": ["photoshop", "adobe photoshop", "retouche"],
        "related": {"Adobe Illustrator": 0.4, "Canva": 0.3},
    },
    "Adobe Illustrator": {
        "category": "Design & UX",
        "aliases": ["illustrator", "adobe illustrator", "vectoriel"],
        "related": {"Adobe Photoshop": 0.4, "Figma": 0.35},
    },
    "Motion Design": {
        "category": "Design & UX",
        "aliases": ["motion design", "after effects", "animation graphique"],
        "related": {"Adobe Photoshop": 0.35, "Montage vidéo": 0.5},
    },
    "Montage vidéo": {
        "category": "Design & UX",
        "aliases": ["montage video", "premiere pro", "capcut", "final cut", "video"],
        "related": {"Motion Design": 0.5},
    },
    "Canva": {"category": "Design & UX", "aliases": ["canva"], "related": {"Adobe Photoshop": 0.3, "UI Design": 0.25}},
    "Design Thinking": {
        "category": "Design & UX",
        "aliases": ["design thinking", "ateliers d'ideation", "ideation"],
        "related": {"UX Research": 0.5, "Product Discovery": 0.5},
    },
    # ------------------------ Marketing & Croissance ------------------------ #
    "SEO": {
        "category": "Marketing & Croissance",
        "aliases": ["seo", "referencement naturel", "referencement", "mots-cles", "search engine optimization"],
        "related": {"Content Marketing": 0.5, "Analytics": 0.4},
    },
    "SEA": {
        "category": "Marketing & Croissance",
        "aliases": ["sea", "referencement payant", "paid search", "sem"],
        "related": {"Google Ads": 0.6, "SEO": 0.35},
    },
    "Google Ads": {
        "category": "Marketing & Croissance",
        "aliases": ["google ads", "adwords", "google adwords"],
        "related": {"SEA": 0.6, "Analytics": 0.4},
    },
    "Meta Ads": {
        "category": "Marketing & Croissance",
        "aliases": ["meta ads", "facebook ads", "instagram ads", "social ads"],
        "related": {"Réseaux sociaux": 0.5, "Google Ads": 0.35},
    },
    "Analytics": {
        "category": "Marketing & Croissance",
        "aliases": ["analytics", "google analytics", "ga4", "matomo", "mesure d'audience", "kpi"],
        "related": {"Analyse de données": 0.5, "A/B testing": 0.4, "Looker Studio": 0.4},
    },
    "Content Marketing": {
        "category": "Marketing & Croissance",
        "aliases": ["content marketing", "marketing de contenu", "strategie de contenu", "contenu", "blogs", "articles"],
        "related": {"Copywriting": 0.55, "SEO": 0.5},
    },
    "Copywriting": {
        "category": "Marketing & Croissance",
        "aliases": ["copywriting", "redaction", "redaction web", "ecriture", "storytelling"],
        "related": {"Content Marketing": 0.55, "Réseaux sociaux": 0.3},
    },
    "Réseaux sociaux": {
        "category": "Marketing & Croissance",
        "aliases": ["reseaux sociaux", "social media", "community management", "instagram", "linkedin", "tiktok"],
        "related": {"Content Marketing": 0.45, "Copywriting": 0.3, "Meta Ads": 0.4},
    },
    "Email marketing": {
        "category": "Marketing & Croissance",
        "aliases": ["email marketing", "e-mailing", "newsletter", "mailchimp", "brevo", "hubspot"],
        "related": {"CRM": 0.4, "Copywriting": 0.4, "Marketing Automation": 0.5},
    },
    "Marketing Automation": {
        "category": "Marketing & Croissance",
        "aliases": ["marketing automation", "automatisation marketing", "workflow marketing"],
        "related": {"Email marketing": 0.5, "CRM": 0.45},
    },
    "CRM": {
        "category": "Marketing & Croissance",
        "aliases": ["crm", "salesforce", "hubspot crm", "pipedrive"],
        "related": {"Salesforce": 0.6, "Relation client": 0.4},
    },
    "Salesforce": {"category": "Marketing & Croissance", "aliases": ["salesforce"], "related": {"CRM": 0.6}},
    "Growth": {
        "category": "Marketing & Croissance",
        "aliases": ["growth", "growth hacking", "acquisition", "funnel", "tunnel de conversion"],
        "related": {"Analytics": 0.5, "A/B testing": 0.5, "SEO": 0.35},
    },
    "Branding": {
        "category": "Marketing & Croissance",
        "aliases": ["branding", "marque", "identite de marque", "positionnement"],
        "related": {"Copywriting": 0.35, "UI Design": 0.3},
    },
    # ------------------------- Gestion & Produit ---------------------------- #
    "Gestion de projet": {
        "category": "Gestion & Produit",
        "aliases": ["gestion de projet", "project management", "chef de projet", "pilotage de projet", "pmo"],
        "related": {"Agile/Scrum": 0.5, "Organisation": 0.5, "Jira": 0.35, "Reporting": 0.4},
    },
    "Agile/Scrum": {
        "category": "Gestion & Produit",
        "aliases": ["agile", "scrum", "kanban", "sprint", "safe", "methode agile"],
        "related": {"Gestion de projet": 0.5, "Jira": 0.5, "Product Discovery": 0.4},
    },
    "Product Discovery": {
        "category": "Gestion & Produit",
        "aliases": ["product discovery", "discovery", "product management", "product owner", "product manager", "user stories"],
        "related": {"UX Research": 0.5, "Roadmap": 0.5, "Agile/Scrum": 0.4},
    },
    "Roadmap": {
        "category": "Gestion & Produit",
        "aliases": ["roadmap", "priorisation", "backlog", "vision produit"],
        "related": {"Product Discovery": 0.5, "Gestion de projet": 0.4},
    },
    "Jira": {"category": "Gestion & Produit", "aliases": ["jira", "confluence"], "related": {"Agile/Scrum": 0.5, "Gestion de projet": 0.35}},
    "Notion": {"category": "Gestion & Produit", "aliases": ["notion"], "related": {"Gestion de projet": 0.35, "Organisation": 0.35}},
    "Trello": {"category": "Gestion & Produit", "aliases": ["trello", "asana", "monday.com"], "related": {"Gestion de projet": 0.4, "Agile/Scrum": 0.4}},
    "Reporting": {
        "category": "Gestion & Produit",
        "aliases": ["reporting", "tableaux de bord", "tableau de bord", "dashboard", "kpi"],
        "related": {"Data visualisation": 0.5, "Excel": 0.4, "Power BI": 0.5},
    },
    "Analyse financière": {
        "category": "Gestion & Produit",
        "aliases": ["analyse financiere", "finance", "modelisation financiere", "valuation", "business plan", "controle de gestion"],
        "related": {"Comptabilité": 0.5, "Excel": 0.5},
    },
    "Comptabilité": {
        "category": "Gestion & Produit",
        "aliases": ["comptabilite", "ecritures comptables", "bilan", "compte de resultat", "pcg"],
        "related": {"Analyse financière": 0.5, "Excel": 0.4},
    },
    "Contrôle de gestion": {
        "category": "Gestion & Produit",
        "aliases": ["controle de gestion", "budget", "previsionnel", "reporting financier"],
        "related": {"Analyse de données": 0.4, "Excel": 0.5, "Analyse financière": 0.5},
    },
    "Négociation": {
        "category": "Gestion & Produit",
        "aliases": ["negociation", "negocier", "closing", "vente"],
        "related": {"Communication": 0.5, "Relation client": 0.5},
    },
    "Relation client": {
        "category": "Gestion & Produit",
        "aliases": ["relation client", "service client", "satisfaction client", "customer success"],
        "related": {"Communication": 0.5, "CRM": 0.4, "Empathie": 0.4},
    },
    "Management": {
        "category": "Gestion & Produit",
        "aliases": ["management", "encadrement", "gestion d'equipe", "manager"],
        "related": {"Leadership": 0.6, "Communication": 0.5, "Gestion de projet": 0.4},
    },
    # ---------------------------- Outils & Cloud ---------------------------- #
    "Linux": {
        "category": "Outils & Cloud",
        "aliases": ["linux", "ubuntu", "debian", "unix", "centos", "red hat"],
        "related": {"Scripting": 0.5, "Réseaux": 0.4, "Administration système": 0.6},
    },
    "Docker": {
        "category": "Outils & Cloud",
        "aliases": ["docker", "conteneur", "conteneurs", "container", "dockerfile", "docker compose"],
        "related": {"Kubernetes": 0.5, "CI/CD": 0.5, "Linux": 0.4},
    },
    "Kubernetes": {
        "category": "Outils & Cloud",
        "aliases": ["kubernetes", "k8s", "helm"],
        "related": {"Docker": 0.6, "CI/CD": 0.4, "Cloud": 0.4},
    },
    "CI/CD": {
        "category": "Outils & Cloud",
        "aliases": ["ci/cd", "ci cd", "integration continue", "deploiement continu", "jenkins", "gitlab ci", "github actions"],
        "related": {"Git": 0.45, "Docker": 0.45, "Automatisation": 0.5},
    },
    "Cloud": {
        "category": "Outils & Cloud",
        "aliases": ["cloud", "aws", "azure", "gcp", "google cloud", "cloud computing", "s3", "ec2"],
        "related": {"Linux": 0.4, "Docker": 0.4, "Terraform": 0.4},
    },
    "AWS": {"category": "Outils & Cloud", "aliases": ["aws", "amazon web services"], "related": {"Cloud": 0.7, "Terraform": 0.4}},
    "Azure": {"category": "Outils & Cloud", "aliases": ["azure", "microsoft azure"], "related": {"Cloud": 0.7}},
    "GCP": {"category": "Outils & Cloud", "aliases": ["gcp", "google cloud platform", "google cloud"], "related": {"Cloud": 0.7, "Big Data": 0.4}},
    "Terraform": {
        "category": "Outils & Cloud",
        "aliases": ["terraform", "infrastructure as code", "iac"],
        "related": {"Cloud": 0.5, "CI/CD": 0.4},
    },
    "Monitoring": {
        "category": "Outils & Cloud",
        "aliases": ["monitoring", "supervision", "grafana", "prometheus", "datadog", "observabilite"],
        "related": {"Linux": 0.4, "Cloud": 0.4, "Administration système": 0.5},
    },
    "Réseaux": {
        "category": "Outils & Cloud",
        "aliases": ["reseaux", "reseau", "tcp/ip", "dns", "vpn", "routeur", "switch", "cisco"],
        "related": {"Cybersécurité": 0.5, "Linux": 0.4, "Administration système": 0.5},
    },
    "Cybersécurité": {
        "category": "Outils & Cloud",
        "aliases": ["cybersecurite", "securite informatique", "securite", "pentest", "soc", "ctf", "vulnerabilites"],
        "related": {"Réseaux": 0.5, "Linux": 0.45, "SIEM": 0.5, "RGPD": 0.35},
    },
    "SIEM": {
        "category": "Outils & Cloud",
        "aliases": ["siem", "splunk", "elastic", "qradar", "sentinel", "analyse de logs"],
        "related": {"Cybersécurité": 0.55, "Linux": 0.35, "Scripting": 0.35},
    },
    "Administration système": {
        "category": "Outils & Cloud",
        "aliases": ["administration systeme", "sysadmin", "systeme", "active directory", "virtualisation", "vmware"],
        "related": {"Linux": 0.6, "Réseaux": 0.5, "Monitoring": 0.5},
    },
    "RGPD": {
        "category": "Outils & Cloud",
        "aliases": ["rgpd", "gdpr", "protection des donnees", "donnees personnelles"],
        "related": {"Cybersécurité": 0.35, "Droit & Administration": 0.4},
    },
    # ----------------------------- Soft skills ------------------------------ #
    "Communication": {
        "category": "Soft skills",
        "aliases": ["communication", "communiquer", "presentation", "presenter", "vulgarisation", "oral", "ecrit professionnel"],
        "related": {"Prise de parole": 0.6, "Relation client": 0.4, "Travail en équipe": 0.4},
    },
    "Travail en équipe": {
        "category": "Soft skills",
        "aliases": ["travail en equipe", "equipe", "teamwork", "collaboration", "collectif", "entraide"],
        "related": {"Communication": 0.5, "Empathie": 0.4, "Leadership": 0.35},
    },
    "Autonomie": {
        "category": "Soft skills",
        "aliases": ["autonomie", "autonome", "initiative", "proactif", "proactivite", "debrouillard"],
        "related": {"Organisation": 0.45, "Adaptabilité": 0.4},
    },
    "Rigueur": {
        "category": "Soft skills",
        "aliases": ["rigueur", "rigoureux", "rigoureuse", "precision", "serieux", "fiabilite", "methodique"],
        "related": {"Sens du détail": 0.6, "Organisation": 0.5, "Esprit d'analyse": 0.4},
    },
    "Curiosité": {
        "category": "Soft skills",
        "aliases": ["curiosite", "curieux", "curieuse", "veille", "apprentissage continu", "envie d'apprendre"],
        "related": {"Adaptabilité": 0.4, "Créativité": 0.35},
    },
    "Créativité": {
        "category": "Soft skills",
        "aliases": ["creativite", "creatif", "creative", "innovation", "idees", "imagination"],
        "related": {"Design Thinking": 0.45, "Curiosité": 0.35},
    },
    "Esprit d'analyse": {
        "category": "Soft skills",
        "aliases": ["esprit d'analyse", "analytique", "analyse", "esprit critique", "resolution de problemes", "probleme"],
        "related": {"Statistiques": 0.4, "Esprit critique": 0.5, "Rigueur": 0.4},
    },
    "Esprit critique": {
        "category": "Soft skills",
        "aliases": ["esprit critique", "critique", "recul", "objectivite", "hypotheses"],
        "related": {"Esprit d'analyse": 0.6, "Curiosité": 0.4},
    },
    "Organisation": {
        "category": "Soft skills",
        "aliases": ["organisation", "organise", "organisee", "planification", "gestion du temps", "priorisation", "gestion des priorites"],
        "related": {"Gestion de projet": 0.5, "Rigueur": 0.45, "Gestion du stress": 0.35},
    },
    "Adaptabilité": {
        "category": "Soft skills",
        "aliases": ["adaptabilite", "adaptable", "flexibilite", "flexible", "polyvalent", "polyvalence", "changement"],
        "related": {"Autonomie": 0.4, "Curiosité": 0.4},
    },
    "Leadership": {
        "category": "Soft skills",
        "aliases": ["leadership", "leader", "encadrement", "motivation d'equipe", "responsable d'equipe"],
        "related": {"Management": 0.6, "Communication": 0.45, "Travail en équipe": 0.4},
    },
    "Empathie": {
        "category": "Soft skills",
        "aliases": ["empathie", "ecoute", "ecoute active", "bienveillance", "comprehension des besoins"],
        "related": {"Communication": 0.5, "UX Research": 0.4},
    },
    "Persévérance": {
        "category": "Soft skills",
        "aliases": ["perseverance", "perseverant", "tenacite", "resilience", "courage"],
        "related": {"Autonomie": 0.4, "Gestion du stress": 0.4},
    },
    "Prise de parole": {
        "category": "Soft skills",
        "aliases": ["prise de parole", "pitch", "presentation orale", "conference", "animation de reunion"],
        "related": {"Communication": 0.6, "Leadership": 0.4},
    },
    "Gestion du stress": {
        "category": "Soft skills",
        "aliases": ["gestion du stress", "sous pression", "calme", "gestion des urgences", "equilibre"],
        "related": {"Organisation": 0.4, "Persévérance": 0.4},
    },
    "Sens du détail": {
        "category": "Soft skills",
        "aliases": ["sens du detail", "attention aux details", "minutie", "soin", "precision", "relecture"],
        "related": {"Rigueur": 0.6, "Qualité de code": 0.4},
    },
    "Proactivité": {
        "category": "Soft skills",
        "aliases": ["proactivite", "proactif", "force de proposition", "initiatives"],
        "related": {"Autonomie": 0.6, "Curiosité": 0.4},
    },
    "Qualité de code": {
        "category": "Soft skills",
        "aliases": ["qualite de code", "code propre", "clean code", "revue de code", "bonnes pratiques"],
        "related": {"Tests unitaires": 0.5, "Rigueur": 0.4, "Git": 0.3},
    },
    "Droit & Administration": {
        "category": "Gestion & Produit",
        "aliases": ["droit", "juridique", "contrats", "administration", "marches publics"],
        "related": {"RGPD": 0.4, "Comptabilité": 0.2},
    },
    "Vente": {
        "category": "Gestion & Produit",
        "aliases": ["vente", "prospection", "business development", "commercial"],
        "related": {"Négociation": 0.6, "Relation client": 0.5},
    },
}

SKILL_NAMES = list(SKILLS.keys())

SOFT_SKILLS = [name for name, meta in SKILLS.items() if meta["category"] == "Soft skills"]

HARD_SKILLS = [name for name in SKILLS if name not in SOFT_SKILLS]


# --------------------------------------------------------------------------- #
# Alias -> compétence canonique
# --------------------------------------------------------------------------- #

def _build_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for name, meta in SKILLS.items():
        index[name.lower()] = name
        for alias in meta.get("aliases", []):
            index[alias.lower()] = name
    return index


ALIAS_INDEX = _build_alias_index()


# --------------------------------------------------------------------------- #
# Formation
# --------------------------------------------------------------------------- #

EDUCATION_FIELD_KEYWORDS = {
    "Informatique & Développement": ["informatique", "developpement", "genie logiciel", "web", "programmation", "si"],
    "Data & Intelligence artificielle": ["data", "donnees", "intelligence artificielle", "ia", "machine learning", "statistiques", "maths appliquees"],
    "Design & UX": ["design", "ux", "ui", "graphisme", "arts appliques"],
    "Marketing & Communication": ["marketing", "communication", "commerce", "publicite", "journalisme"],
    "Gestion, Finance & Commerce": ["gestion", "finance", "comptabilite", "commerce", "management", "economie", "gestion de projet"],
    "Ingénierie & Sciences": ["ingenieur", "ingenierie", "mecanique", "electrique", "physique", "chimie", "sciences"],
    "Sciences humaines & Social": ["psychologie", "sociologie", "sciences humaines", "histoire", "geographie"],
    "Droit & Administration": ["droit", "juridique", "administration", "politique"],
    "Santé & Biologie": ["sante", "biologie", "medecine", "pharmacie", "soins"],
}

FIELD_ADJACENCY = {
    "Informatique & Développement": {"Data & Intelligence artificielle": 0.8, "Ingénierie & Sciences": 0.55},
    "Data & Intelligence artificielle": {"Informatique & Développement": 0.8, "Ingénierie & Sciences": 0.6, "Gestion, Finance & Commerce": 0.4},
    "Design & UX": {"Marketing & Communication": 0.55, "Informatique & Développement": 0.4},
    "Marketing & Communication": {"Gestion, Finance & Commerce": 0.6, "Design & UX": 0.55},
    "Gestion, Finance & Commerce": {"Marketing & Communication": 0.6, "Droit & Administration": 0.4},
    "Ingénierie & Sciences": {"Informatique & Développement": 0.55, "Data & Intelligence artificielle": 0.6},
    "Sciences humaines & Social": {"Marketing & Communication": 0.4},
    "Droit & Administration": {"Gestion, Finance & Commerce": 0.5},
    "Santé & Biologie": {"Ingénierie & Sciences": 0.4},
}


def field_relevance(profile_field: str, required_fields: list[str]) -> float:
    """Retourne la pertinence (0 à 1) entre un parcours et les filières attendues."""
    if not required_fields:
        return 0.85
    if not profile_field:
        return 0.6
    if profile_field in required_fields:
        return 1.0
    for required in required_fields:
        if FIELD_ADJACENCY.get(profile_field, {}).get(required, 0) > 0:
            return FIELD_ADJACENCY[profile_field][required]
        if FIELD_ADJACENCY.get(required, {}).get(profile_field, 0) > 0:
            return FIELD_ADJACENCY[required][profile_field]
    return 0.35
