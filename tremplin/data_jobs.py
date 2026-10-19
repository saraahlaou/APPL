"""Catalogue d'offres de stage, d'alternance et de premier emploi.

Pensé pour les étudiants au Maroc : 14 offres de sociétés marocaines
(Casablanca, Rabat, Tanger, Fès…) et 4 ouvertures à l'international
(Paris, Montréal, Dubaï, Berlin) pour ceux qui visent l'étranger.

Chaque offre décrit les compétences (avec niveau attendu et poids), les
qualités, les langues, les certifications appréciées et le niveau de
formation attendu. Le moteur de matching consomme directement ces données.
"""

from __future__ import annotations


def req(skill: str, level: int, weight: int, nature: str = "important") -> dict:
    """Définit une compétence requise.

    nature :
      - "indispensable" : poids fort dans le score ;
      - "important"     : poids moyen ;
      - "atout"         : bonus.
    """
    return {"skill": skill, "level": level, "weight": weight, "nature": nature}


def quality(name: str, weight: int = 3) -> dict:
    return {"skill": name, "weight": weight}


def lang(name: str, min_level: str, weight: int = 3) -> dict:
    return {"name": name, "min": min_level, "weight": weight}


JOBS: list[dict] = [
    # ------------------------------------------------------------------ 1
    {
        "id": "data-analyst-stage",
        "title": "Data Analyst — Stage 6 mois",
        "company": "Attijariwafa Bank",
        "company_type": "Banque · leader au Maroc · 20 000+ collaborateurs",
        "domain": "Data & IA",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Casablanca — Casanearshore",
        "remote": "Sur site · télétravail ponctuel",
        "salary": "5 000 MAD / mois",
        "summary": "Attijariwafa Bank renforce ses équipes Data : tu aides à transformer les données de l'activité commerciale en décisions concrètes.",
        "description": (
            "Tu rejoins une cellule Data de 6 personnes au sein de la direction "
            "marketing. Tu produis des analyses qui servent réellement aux équipes : "
            "suivi des campagnes, comportement des clients, performance des agences."
        ),
        "missions": [
            "Écrire des requêtes SQL pour extraire et croiser les données clients.",
            "Automatiser les reportings mensuels (acquisition, activation, rétention).",
            "Construire 2 à 3 tableaux de bord Power BI suivis par les équipes.",
            "Présenter tes analyses en réunion et formuler des recommandations.",
        ],
        "required_skills": [
            req("SQL", 4, 3, "indispensable"),
            req("Python", 3, 2, "important"),
            req("Excel", 4, 2, "important"),
            req("Data visualisation", 3, 2, "important"),
            req("Statistiques", 3, 2, "important"),
            req("Power BI", 3, 2, "important"),
            req("Analyse de données", 3, 2, "important"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Esprit d'analyse", 3), quality("Communication", 2), quality("Curiosité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Google Data Analytics Professional Certificate", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Data & Intelligence artificielle", "Informatique & Développement", "Gestion, Finance & Commerce", "Ingénierie & Sciences"]},
        "nice_to_have": ["ETL", "A/B testing", "Reporting", "Power Query"],
        "keywords": ["data analyst", "business intelligence", "kpi", "dashboard", "tableau de bord", "segmentation"],
        "accent": "#17795E",
    },
    # ------------------------------------------------------------------ 2
    {
        "id": "data-scientist-stage",
        "title": "Data Scientist Junior — Stage 6 mois",
        "company": "OCP Group",
        "company_type": "Leader mondial des phosphates · 20 000+ collaborateurs",
        "domain": "Data & IA",
        "contract": "Stage",
        "duration": "6 mois · démarrage février 2027",
        "location": "Casablanca / Khouribga (navette)",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "6 000 MAD / mois",
        "summary": "OCP modernise ses sites industriels : tu construis des modèles prédictifs qui anticipent les pannes et optimisent la production.",
        "description": (
            "Au sein de l'équipe Data Science industrielle, tu travailles sur des "
            "données de capteurs et de maintenance. Tes modèles alimentent les "
            "outils de pilotage des usines de Jorf Lasfar et Khouribga."
        ),
        "missions": [
            "Explorer et nettoyer des données industrielles volumineuses (Pandas).",
            "Entraîner et évaluer des modèles de maintenance prédictive.",
            "Documenter tes choix de modélisation et tes résultats.",
            "Restituer tes travaux aux équipes métier et aux ingénieurs.",
        ],
        "required_skills": [
            req("Python", 4, 3, "indispensable"),
            req("Machine Learning", 3, 3, "indispensable"),
            req("Statistiques", 4, 2, "important"),
            req("SQL", 3, 2, "important"),
            req("Pandas", 3, 2, "important"),
            req("Scikit-learn", 3, 2, "atout"),
            req("Data visualisation", 3, 1, "atout"),
        ],
        "qualities": [quality("Esprit d'analyse", 3), quality("Rigueur", 3), quality("Autonomie", 2), quality("Curiosité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Microsoft Certified: Power BI Data Analyst (PL-300)", "importance": "atout"}],
        "education": {"min_level": "Bac+5 (Master 2 / Ingénieur)", "fields": ["Data & Intelligence artificielle", "Ingénierie & Sciences", "Informatique & Développement"]},
        "nice_to_have": ["Deep Learning", "Séries temporelles", "MLOps", "Cloud"],
        "keywords": ["machine learning", "data science", "modèle", "prévision", "python", "industrie"],
        "accent": "#2E7D9A",
    },
    # ------------------------------------------------------------------ 3
    {
        "id": "ia-nlp-stage",
        "title": "Stage IA — Chatbot & NLP",
        "company": "Inwi",
        "company_type": "Opérateur télécom · 1 500+ collaborateurs",
        "domain": "Data & IA",
        "contract": "Stage",
        "duration": "5 à 6 mois · démarrage janvier 2027",
        "location": "Rabat — Hay Riad",
        "remote": "Sur site · 1 jour flexible",
        "salary": "5 000 MAD / mois",
        "summary": "Inwi améliore son service client : tu participes à la création d'un assistant intelligent capable de comprendre le français et la darija.",
        "description": (
            "Tu rejoins l'équipe Innovation & Data. Tu travailles sur le "
            "traitement automatique des réclamations clients : classification des "
            "demandes, réponses suggérées et suivi de la qualité des échanges."
        ),
        "missions": [
            "Collecter et annoter des conversations clients (français / arabe).",
            "Entraîner et évaluer des modèles de classification de texte.",
            "Prototyper des réponses assistées par IA pour le support.",
            "Mesurer la qualité des prédictions et proposer des améliorations.",
        ],
        "required_skills": [
            req("Python", 4, 3, "indispensable"),
            req("NLP", 3, 2, "important"),
            req("Machine Learning", 3, 2, "important"),
            req("Pandas", 3, 2, "important"),
            req("LLM", 2, 2, "atout"),
            req("SQL", 2, 1, "atout"),
        ],
        "qualities": [quality("Curiosité", 3), quality("Esprit d'analyse", 2), quality("Autonomie", 2), quality("Créativité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Data & Intelligence artificielle", "Informatique & Développement", "Ingénierie & Sciences"]},
        "nice_to_have": ["LLM", "Prompt Engineering", "MLOps", "Docker"],
        "keywords": ["nlp", "chatbot", "darija", "intelligence artificielle", "traitement du langage", "support client"],
        "accent": "#8A5CC6",
    },
    # ------------------------------------------------------------------ 4
    {
        "id": "frontend-alternance",
        "title": "Développeur·se Front-End React — Alternance",
        "company": "Sopra HR Software",
        "company_type": "Éditeur de logiciels RH · Fès Shore",
        "domain": "Développement logiciel",
        "contract": "Alternance",
        "duration": "12 à 24 mois · démarrage septembre 2026",
        "location": "Fès — Fès Shore",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "4 000 MAD / mois",
        "summary": "Sopra HR développe des solutions de paie et de gestion des talents utilisées dans 20 pays. Tu participes à la refonte de leur interface.",
        "description": (
            "Au sein d'une équipe produit de 8 personnes, tu développes des "
            "composants React accessibles et performants. Tu travailles avec les "
            "designers et le back-end pour livrer des fonctionnalités de bout en bout."
        ),
        "missions": [
            "Développer des composants React / TypeScript réutilisables.",
            "Intégrer les maquettes Figma avec une attention forte au détail.",
            "Écrire des tests et participer aux revues de code.",
            "Contribuer au design system et à la documentation technique.",
        ],
        "required_skills": [
            req("JavaScript", 4, 3, "indispensable"),
            req("React", 4, 3, "indispensable"),
            req("HTML/CSS", 4, 2, "important"),
            req("Git", 3, 2, "important"),
            req("API REST", 3, 2, "important"),
            req("TypeScript", 3, 2, "atout"),
            req("Figma", 2, 1, "atout"),
        ],
        "qualities": [quality("Autonomie", 3), quality("Curiosité", 3), quality("Travail en équipe", 2), quality("Sens du détail", 3)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Informatique & Développement", "Data & Intelligence artificielle", "Design & UX"]},
        "nice_to_have": ["TypeScript", "Tests unitaires", "Accessibilité", "Design System"],
        "keywords": ["frontend", "react", "typescript", "design system", "web", "alternance"],
        "accent": "#6C8EF5",
    },
    # ------------------------------------------------------------------ 5
    {
        "id": "backend-stage",
        "title": "Développeur·se Back-End Java — Stage 6 mois",
        "company": "HPS",
        "company_type": "Fintech paiement · leader mondial · Casablanca",
        "domain": "Développement logiciel",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Casablanca — Sidi Maârouf",
        "remote": "Sur site",
        "salary": "5 500 MAD / mois",
        "summary": "HPS équipe les banques de 90 pays en solutions de paiement. Tu rejoins une équipe qui développe les services transactionnels.",
        "description": (
            "Tu intègres une équipe agile de 7 développeurs. Tu participes à la "
            "conception et au développement de services Java qui traitent des "
            "millions de transactions, avec des exigences fortes de fiabilité."
        ),
        "missions": [
            "Développer des services Java exposant des API REST documentées.",
            "Écrire des tests unitaires et participer aux revues de code.",
            "Corriger des anomalies remontées par les équipes support.",
            "Documenter les évolutions techniques et les déploiements.",
        ],
        "required_skills": [
            req("Java", 4, 3, "indispensable"),
            req("Programmation orientée objet", 4, 2, "important"),
            req("API REST", 3, 2, "important"),
            req("SQL", 3, 2, "important"),
            req("Git", 3, 2, "important"),
            req("Linux", 2, 1, "atout"),
            req("Docker", 2, 1, "atout"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Esprit d'analyse", 2), quality("Travail en équipe", 3), quality("Autonomie", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Informatique & Développement", "Ingénierie & Sciences"]},
        "nice_to_have": ["Docker", "Tests unitaires", "CI/CD", "Qualité de code"],
        "keywords": ["java", "backend", "api", "paiement", "fintech", "microservices"],
        "accent": "#0E7C86",
    },
    # ------------------------------------------------------------------ 6
    {
        "id": "cybersecurite-stage",
        "title": "Analyste Cybersécurité — Stage 6 mois",
        "company": "Bank of Africa (BMCE)",
        "company_type": "Banque panafricaine · Casablanca",
        "domain": "Cybersécurité & Cloud",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Casablanca — Boulevard Zerktouni",
        "remote": "Sur site · télétravail exceptionnel",
        "salary": "5 000 MAD / mois",
        "summary": "Bank of Africa renforce son SOC : tu participes à la surveillance et à la protection des systèmes bancaires contre les cyberattaques.",
        "description": (
            "Tu rejoins l'équipe Sécurité des Systèmes d'Information (10 personnes). "
            "Tu découvres le quotidien d'un SOC bancaire : analyse des alertes, "
            "sensibilisation des équipes et application des exigences réglementaires."
        ),
        "missions": [
            "Surveiller les alertes de sécurité et qualifier les incidents.",
            "Analyser les journaux systèmes et réseaux (SIEM).",
            "Contribuer aux campagnes de sensibilisation internes.",
            "Vérifier la conformité des traitements avec la loi 09-08 (RGPD local).",
        ],
        "required_skills": [
            req("Cybersécurité", 3, 3, "indispensable"),
            req("Réseaux", 3, 2, "important"),
            req("Linux", 3, 2, "important"),
            req("SIEM", 2, 2, "important"),
            req("Monitoring", 2, 1, "atout"),
            req("RGPD", 3, 1, "atout"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Esprit d'analyse", 3), quality("Esprit critique", 2), quality("Organisation", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "CompTIA Security+", "importance": "atout"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Informatique & Développement", "Ingénierie & Sciences", "Data & Intelligence artificielle"]},
        "nice_to_have": ["SIEM", "Cloud", "Monitoring", "RGPD"],
        "keywords": ["cybersécurité", "soc", "siem", "sécurité informatique", "banque", "alertes"],
        "accent": "#C2543A",
    },
    # ------------------------------------------------------------------ 7
    {
        "id": "devops-alternance",
        "title": "Ingénieur·e DevOps / Cloud — Alternance",
        "company": "Capgemini Maroc",
        "company_type": "ESN internationale · 1 800+ collaborateurs au Maroc",
        "domain": "Cybersécurité & Cloud",
        "contract": "Alternance",
        "duration": "12 à 24 mois · démarrage septembre 2026",
        "location": "Casablanca — Casanearshore",
        "remote": "Hybride · 3 jours de télétravail",
        "salary": "4 500 MAD / mois",
        "summary": "Capgemini accompagne les grandes entreprises dans leur migration cloud. Tu apprends à automatiser le déploiement des applications.",
        "description": (
            "Tu rejoins une équipe Cloud & DevOps qui sert des clients bancaires "
            "et télécom. Tu construis des chaînes d'intégration continue et tu "
            "automatises les environnements de test et de production."
        ),
        "missions": [
            "Écrire des scripts d'automatisation (bash, Python).",
            "Construire et maintenir des pipelines CI/CD.",
            "Conteneuriser des applications avec Docker.",
            "Participer au suivi des environnements cloud et à leur bon fonctionnement.",
        ],
        "required_skills": [
            req("Docker", 3, 3, "indispensable"),
            req("CI/CD", 3, 3, "indispensable"),
            req("Linux", 3, 2, "important"),
            req("Cloud", 3, 2, "important"),
            req("Git", 3, 2, "important"),
            req("Scripting", 3, 2, "important"),
            req("Kubernetes", 2, 2, "atout"),
            req("Terraform", 2, 1, "atout"),
        ],
        "qualities": [quality("Autonomie", 3), quality("Rigueur", 2), quality("Curiosité", 3), quality("Adaptabilité", 2)],
        "languages": [lang("Français", "C1", 2), lang("Anglais", "B2", 3)],
        "certifications": [{"name": "AWS Certified Cloud Practitioner", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Informatique & Développement", "Ingénierie & Sciences", "Data & Intelligence artificielle"]},
        "nice_to_have": ["AWS", "Azure", "Terraform", "Monitoring"],
        "keywords": ["devops", "cloud", "ci/cd", "docker", "kubernetes", "automatisation"],
        "accent": "#354576",
    },
    # ------------------------------------------------------------------ 8
    {
        "id": "ux-designer-stage",
        "title": "UX/UI Designer — Stage 6 mois",
        "company": "Chari",
        "company_type": "Startup e-commerce B2B · Casablanca",
        "domain": "Design & UX",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Casablanca — Sidi Maârouf",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "4 500 MAD / mois",
        "summary": "Chari digitalise le commerce de proximité au Maroc. Tu conçois des expériences simples pour des milliers de commerçants.",
        "description": (
            "Tu travailles avec le Product Manager et les développeurs sur "
            "l'application mobile et le back-office. Tu mènes des recherches "
            "utilisateurs auprès des commerçants et tu prototypes les évolutions."
        ),
        "missions": [
            "Mener des entretiens et des tests utilisateurs auprès des commerçants.",
            "Concevoir des maquettes et prototypes sur Figma.",
            "Faire vivre le design system de l'application.",
            "Travailler la lisibilité en français et en arabe (RTL).",
        ],
        "required_skills": [
            req("Figma", 4, 3, "indispensable"),
            req("UX Research", 3, 2, "important"),
            req("UI Design", 3, 2, "important"),
            req("Prototypage", 3, 2, "important"),
            req("Accessibilité", 2, 1, "atout"),
            req("Design System", 2, 1, "atout"),
        ],
        "qualities": [quality("Créativité", 3), quality("Empathie", 3), quality("Sens du détail", 3), quality("Communication", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Google UX Design Professional Certificate", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Design & UX", "Informatique & Développement", "Marketing & Communication"]},
        "nice_to_have": ["Design System", "Accessibilité", "A/B testing", "Motion Design"],
        "keywords": ["ux", "ui", "figma", "design", "e-commerce", "mobile", "recherche utilisateur"],
        "accent": "#A03621",
    },
    # ------------------------------------------------------------------ 9
    {
        "id": "growth-marketing-stage",
        "title": "Growth Marketing — Stage 6 mois",
        "company": "Glovo Maroc",
        "company_type": "Plateforme de livraison · Casablanca",
        "domain": "Marketing & Communication",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Casablanca — Marina",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "4 500 MAD / mois",
        "summary": "Glovo accélère ses lancements de villes au Maroc et dans la région. Tu optimises les campagnes d'acquisition pour faire grandir la base clients.",
        "description": (
            "Tu rejoins l'équipe Growth Maghreb. Tu analyses la performance des "
            "campagnes payantes, tu testes de nouveaux canaux et tu conduis des "
            "expérimentations avec les équipes produit et CRM."
        ),
        "missions": [
            "Piloter les campagnes Google Ads et Meta Ads (budgets, créas, ciblages).",
            "Analyser les entonnoirs d'acquisition et proposer des optimisations.",
            "Conduire des tests A/B sur les parcours de commande.",
            "Construire les reportings hebdomadaires de croissance.",
        ],
        "required_skills": [
            req("SEO", 3, 2, "important"),
            req("SEA", 3, 2, "important"),
            req("Google Ads", 3, 2, "important"),
            req("Meta Ads", 3, 2, "important"),
            req("Analytics", 3, 2, "important"),
            req("Growth", 3, 2, "atout"),
            req("Content Marketing", 2, 1, "atout"),
        ],
        "qualities": [quality("Proactivité", 3), quality("Créativité", 2), quality("Esprit d'analyse", 2), quality("Adaptabilité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Google Analytics Certification (GA4)", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Marketing & Communication", "Gestion, Finance & Commerce", "Data & Intelligence artificielle"]},
        "nice_to_have": ["Marketing Automation", "CRM", "Email marketing", "Copywriting"],
        "keywords": ["growth", "marketing digital", "acquisition", "crm", "performance", "seo"],
        "accent": "#D98324",
    },
    # ------------------------------------------------------------------ 10
    {
        "id": "communication-alternance",
        "title": "Chargé·e de Communication — Alternance",
        "company": "Centrale Danone",
        "company_type": "Agroalimentaire · marque historique au Maroc",
        "domain": "Marketing & Communication",
        "contract": "Alternance",
        "duration": "12 mois · démarrage septembre 2026",
        "location": "Casablanca — Aïn Sebaâ",
        "remote": "Sur site",
        "salary": "4 000 MAD / mois",
        "summary": "Centrale Danone cherche un profil créatif pour animer ses réseaux sociaux et raconter ses marques auprès du public marocain.",
        "description": (
            "Tu rejoins l'équipe communication de 5 personnes. Tu participes aux "
            "campagnes de marque, au contenu digital et aux relations avec les "
            "agences, en travaillant en français et en arabe/darija."
        ),
        "missions": [
            "Créer et planifier des contenus pour Instagram, Facebook et TikTok.",
            "Rédiger des textes en français et en darija adaptés à chaque audience.",
            "Coordonner la production avec les agences et les équipes produit.",
            "Suivre les performances des publications et proposer des ajustements.",
        ],
        "required_skills": [
            req("Content Marketing", 3, 2, "important"),
            req("Copywriting", 3, 2, "important"),
            req("Réseaux sociaux", 3, 2, "important"),
            req("Canva", 2, 1, "atout"),
            req("Montage vidéo", 2, 1, "atout"),
            req("Branding", 2, 1, "atout"),
        ],
        "qualities": [quality("Créativité", 3), quality("Communication", 3), quality("Organisation", 2), quality("Sens du détail", 2)],
        "languages": [lang("Français", "C1", 3), lang("Arabe", "C1", 2), lang("Anglais", "B1", 1)],
        "certifications": [{"name": "HubSpot Content Marketing Certification", "importance": "atout"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Marketing & Communication", "Sciences humaines & Social", "Design & UX"]},
        "nice_to_have": ["SEO", "Email marketing", "Adobe Photoshop", "Branding"],
        "keywords": ["communication", "réseaux sociaux", "contenu", "marque", "digital", "darija"],
        "accent": "#57408F",
    },
    # ------------------------------------------------------------------ 11
    {
        "id": "business-analyst-cdi",
        "title": "Business Analyst Junior — CDI",
        "company": "CIH Bank",
        "company_type": "Banque à forte culture digitale · Casablanca",
        "domain": "Finance & Conseil",
        "contract": "CDI junior",
        "duration": "CDI · démarrage dès que possible",
        "location": "Casablanca — CFC",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "12 000 – 15 000 MAD / mois",
        "summary": "CIH Bank digitalise ses parcours clients (crédit, mobile banking). Tu fais le lien entre les besoins métier et les équipes techniques.",
        "description": (
            "Au sein de la direction Innovation, tu recueilles les besoins des "
            "métiers, tu formalises les exigences et tu accompagnes les équipes "
            "techniques jusqu'à la mise en production des évolutions."
        ),
        "missions": [
            "Recueillir et formaliser les besoins métier (user stories, critères d'acceptation).",
            "Analyser les données d'usage et construire les reportings de suivi.",
            "Animer les réunions de priorisation avec les développeurs.",
            "Valider les livraisons et mesurer l'impact des évolutions.",
        ],
        "required_skills": [
            req("SQL", 3, 3, "indispensable"),
            req("Excel", 4, 2, "important"),
            req("Analyse de données", 3, 2, "important"),
            req("Reporting", 3, 2, "important"),
            req("Power BI", 3, 2, "important"),
            req("Gestion de projet", 3, 2, "atout"),
            req("ETL", 2, 1, "atout"),
        ],
        "qualities": [quality("Esprit d'analyse", 3), quality("Communication", 3), quality("Rigueur", 3), quality("Organisation", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Professional Scrum Master I (PSM I)", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Gestion, Finance & Commerce", "Data & Intelligence artificielle", "Informatique & Développement"]},
        "nice_to_have": ["Agile/Scrum", "Jira", "Power Query", "ETL"],
        "keywords": ["business analyst", "besoins", "cahier des charges", "reporting", "banque", "kpi"],
        "accent": "#0E5B45",
    },
    # ------------------------------------------------------------------ 12
    {
        "id": "controle-gestion-alternance",
        "title": "Contrôle de Gestion — Alternance",
        "company": "Marjane Holding",
        "company_type": "Leader de la grande distribution au Maroc",
        "domain": "Finance & Conseil",
        "contract": "Alternance",
        "duration": "12 à 24 mois · démarrage septembre 2026",
        "location": "Casablanca — Aïn Sebaâ",
        "remote": "Sur site",
        "salary": "4 000 MAD / mois",
        "summary": "Marjane pilote plus de 40 hypermarchés : tu participes au suivi budgétaire et à l'analyse des performances des magasins.",
        "description": (
            "Tu rejoins la direction financière. Tu produis des tableaux de bord "
            "pour les responsables de magasins et tu analyses les écarts entre "
            "le budget et les réalisations."
        ),
        "missions": [
            "Construire et mettre à jour les tableaux de bord de gestion (Excel, Power BI).",
            "Analyser les écarts budget / réalisé et rédiger les commentaires.",
            "Automatiser les clôtures mensuelles avec Power Query.",
            "Participer aux réunions de pilotage avec les directeurs de magasin.",
        ],
        "required_skills": [
            req("Excel", 4, 3, "indispensable"),
            req("Contrôle de gestion", 3, 2, "important"),
            req("Comptabilité", 3, 2, "important"),
            req("Analyse financière", 3, 2, "important"),
            req("Reporting", 3, 2, "important"),
            req("Power Query", 2, 1, "atout"),
            req("VBA", 2, 1, "atout"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Organisation", 3), quality("Esprit d'analyse", 2), quality("Esprit critique", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 1)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Gestion, Finance & Commerce", "Data & Intelligence artificielle"]},
        "nice_to_have": ["Power BI", "VBA", "Analyse financière", "SQL"],
        "keywords": ["contrôle de gestion", "budget", "reporting", "retail", "finance", "tableaux de bord"],
        "accent": "#4A5A16",
    },
    # ------------------------------------------------------------------ 13
    {
        "id": "chef-projet-digital-stage",
        "title": "Assistant·e Chef de Projet Digital — Stage 6 mois",
        "company": "Maroc Telecom (IAM)",
        "company_type": "Opérateur télécom historique · Rabat",
        "domain": "Produit & Gestion de projet",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Rabat — Hay Riad",
        "remote": "Hybride · 1 jour de télétravail",
        "salary": "5 500 MAD / mois",
        "summary": "Maroc Telecom refond ses services digitaux (app, espace client). Tu assistes le chef de projet dans la coordination des équipes.",
        "description": (
            "Tu suis les projets de la direction digitale : planning, suivi des "
            "risques, animation des points d'avancement et communication auprès "
            "des parties prenantes internes."
        ),
        "missions": [
            "Mettre à jour les plannings et les tableaux de suivi de projet.",
            "Préparer et animer les points d'avancement avec les équipes.",
            "Documenter les besoins et les décisions dans les outils de gestion.",
            "Suivre les indicateurs des projets digitaux et alerter sur les risques.",
        ],
        "required_skills": [
            req("Gestion de projet", 3, 3, "indispensable"),
            req("Agile/Scrum", 3, 2, "important"),
            req("Roadmap", 2, 2, "important"),
            req("Jira", 2, 1, "atout"),
            req("Notion", 2, 1, "atout"),
            req("Analyse de données", 2, 1, "atout"),
        ],
        "qualities": [quality("Organisation", 3), quality("Communication", 3), quality("Prise de parole", 2), quality("Leadership", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Google Project Management Professional Certificate", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Gestion, Finance & Commerce", "Informatique & Développement", "Marketing & Communication"]},
        "nice_to_have": ["Product Discovery", "Figma", "SQL", "Trello"],
        "keywords": ["chef de projet", "digital", "coordination", "agile", "roadmap", "télécom"],
        "accent": "#2E7D9A",
    },
    # ------------------------------------------------------------------ 14
    {
        "id": "rh-stage",
        "title": "Chargé·e de Recrutement & Talents — Stage 6 mois",
        "company": "Renault Group Maroc",
        "company_type": "Industrie automobile · usine de Tanger Med",
        "domain": "Ressources humaines",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Tanger — Tanger Med",
        "remote": "Sur site",
        "salary": "4 000 MAD / mois",
        "summary": "Renault recrute chaque année des centaines de collaborateurs à Tanger. Tu participes au sourcing et à l'accueil des nouveaux talents.",
        "description": (
            "Au sein de l'équipe RH, tu prends en charge une partie du processus "
            "de recrutement : publication des offres, présélection, entretiens "
            "téléphoniques et suivi de l'intégration des nouveaux arrivants."
        ),
        "missions": [
            "Publier les offres et sourcer des profils (LinkedIn, écoles, forums).",
            "Réaliser les présélections téléphoniques et planifier les entretiens.",
            "Mettre à jour les tableaux de suivi des recrutements.",
            "Contribuer au parcours d'intégration des nouveaux collaborateurs.",
        ],
        "required_skills": [
            req("Excel", 3, 3, "indispensable"),
            req("Reporting", 3, 2, "important"),
            req("Réseaux sociaux", 2, 2, "important"),
            req("Négociation", 2, 1, "atout"),
            req("CRM", 2, 1, "atout"),
        ],
        "qualities": [quality("Empathie", 3), quality("Organisation", 3), quality("Communication", 3), quality("Adaptabilité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Arabe", "C1", 2), lang("Anglais", "B2", 1)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Sciences humaines & Social", "Droit & Administration", "Gestion, Finance & Commerce"]},
        "nice_to_have": ["Branding", "Email marketing", "Canva", "Prise de parole"],
        "keywords": ["ressources humaines", "recrutement", "talents", "sourcing", "stage", "tanger"],
        "accent": "#C2543A",
    },
    # ============================================================ INTERNATIONAL
    # ------------------------------------------------------------------ 15
    {
        "id": "data-analyst-stage-paris",
        "title": "Data Analyst — Stage 6 mois (France)",
        "company": "Société Générale",
        "company_type": "Banque internationale · Paris La Défense",
        "domain": "Data & IA",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Paris La Défense, France",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "1 300 € / mois",
        "summary": "Dans le cadre d'une mobilité en France, la Société Générale propose un stage Data Analyst dans ses équipes de pilotage de la relation client.",
        "description": (
            "Tu rejoins une équipe internationale qui suit la performance des "
            "parcours clients. Tu produis des analyses en anglais et en français "
            "pour les équipes produit et direction."
        ),
        "missions": [
            "Écrire des requêtes SQL sur des entrepôts de données volumineux.",
            "Produire des tableaux de bord Power BI pour le suivi des parcours clients.",
            "Analyser la satisfaction et l'attrition avec des méthodes statistiques.",
            "Présenter tes résultats en anglais aux équipes internationales.",
        ],
        "required_skills": [
            req("SQL", 4, 3, "indispensable"),
            req("Python", 3, 2, "important"),
            req("Power BI", 3, 2, "important"),
            req("Statistiques", 3, 2, "important"),
            req("Data visualisation", 3, 2, "important"),
            req("Analyse de données", 3, 2, "important"),
            req("ETL", 2, 1, "atout"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Esprit d'analyse", 3), quality("Communication", 2), quality("Curiosité", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [{"name": "Google Data Analytics Professional Certificate", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Data & Intelligence artificielle", "Informatique & Développement", "Gestion, Finance & Commerce", "Ingénierie & Sciences"]},
        "nice_to_have": ["ETL", "A/B testing", "Power Query", "Reporting"],
        "keywords": ["data analyst", "banque", "paris", "stage international", "kpi", "dashboard"],
        "accent": "#B3450E",
    },
    # ------------------------------------------------------------------ 16
    {
        "id": "fullstack-alternance-montreal",
        "title": "Développeur·se Full-Stack — Alternance (Canada)",
        "company": "CGI",
        "company_type": "ESN internationale · Montréal",
        "domain": "Développement logiciel",
        "contract": "Alternance",
        "duration": "12 à 24 mois · démarrage septembre 2026",
        "location": "Montréal, Canada",
        "remote": "Hybride · 3 jours de télétravail",
        "salary": "2 300 CAD / mois",
        "summary": "CGI accompagne les entreprises canadiennes dans leur transformation digitale. Tu développes des applications web pour des clients variés.",
        "description": (
            "Tu intègres une équipe de développement à Montréal. Dans un "
            "environnement francophone et anglophone, tu construis des "
            "applications web de bout en bout avec les meilleures pratiques."
        ),
        "missions": [
            "Développer des interfaces web en React et des services Node.js.",
            "Concevoir et consommer des API REST documentées.",
            "Écrire des tests et participer aux revues de code de l'équipe.",
            "Collaborer avec les équipes canadiennes en anglais et en français.",
        ],
        "required_skills": [
            req("JavaScript", 4, 3, "indispensable"),
            req("Node.js", 3, 2, "important"),
            req("React", 3, 2, "important"),
            req("API REST", 3, 2, "important"),
            req("SQL", 3, 2, "important"),
            req("Git", 3, 2, "important"),
            req("Docker", 2, 1, "atout"),
            req("TypeScript", 2, 1, "atout"),
        ],
        "qualities": [quality("Autonomie", 3), quality("Travail en équipe", 3), quality("Adaptabilité", 2), quality("Qualité de code", 2)],
        "languages": [lang("Français", "C1", 3), lang("Anglais", "B2", 2)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Informatique & Développement", "Data & Intelligence artificielle", "Ingénierie & Sciences"]},
        "nice_to_have": ["TypeScript", "Docker", "CI/CD", "Tests unitaires"],
        "keywords": ["fullstack", "node.js", "react", "montréal", "alternance", "web", "canada"],
        "accent": "#D98324",
    },
    # ------------------------------------------------------------------ 17
    {
        "id": "cybersecurite-cdi-dubai",
        "title": "Cybersecurity Analyst Junior — CDI (Émirats)",
        "company": "Careem",
        "company_type": "Super-app du Moyen-Orient · Dubaï",
        "domain": "Cybersécurité & Cloud",
        "contract": "CDI junior",
        "duration": "CDI · démarrage dès que possible",
        "location": "Dubaï, Émirats arabes unis",
        "remote": "Sur site · 1 jour de télétravail",
        "salary": "14 000 AED / mois",
        "summary": "Careem protège les données de millions d'utilisateurs au Moyen-Orient. Tu rejoins une équipe sécurité multiculturelle basée à Dubaï.",
        "description": (
            "Au sein de l'équipe sécurité, tu participes à la surveillance des "
            "infrastructures cloud, à la réponse aux incidents et à la mise en "
            "œuvre des bonnes pratiques de sécurité."
        ),
        "missions": [
            "Surveiller les alertes et participer à la réponse aux incidents.",
            "Analyser les journaux systèmes avec les outils SIEM.",
            "Durcir les configurations des environnements cloud.",
            "Documenter les procédures de sécurité et former les équipes.",
        ],
        "required_skills": [
            req("Cybersécurité", 4, 3, "indispensable"),
            req("SIEM", 3, 2, "important"),
            req("Monitoring", 3, 2, "important"),
            req("Linux", 3, 2, "important"),
            req("Cloud", 3, 2, "important"),
            req("Réseaux", 3, 2, "important"),
            req("RGPD", 2, 1, "atout"),
        ],
        "qualities": [quality("Rigueur", 3), quality("Esprit d'analyse", 3), quality("Gestion du stress", 2), quality("Autonomie", 2)],
        "languages": [lang("Anglais", "C1", 3)],
        "certifications": [{"name": "CompTIA Security+", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+4 (Master 1)", "fields": ["Informatique & Développement", "Ingénierie & Sciences", "Data & Intelligence artificielle"]},
        "nice_to_have": ["AWS", "Terraform", "SIEM", "Cloud"],
        "keywords": ["cybersecurity", "soc", "dubai", "cloud", "monitoring", "siem", "international"],
        "accent": "#0E7C86",
    },
    # ------------------------------------------------------------------ 18
    {
        "id": "ux-designer-stage-berlin",
        "title": "UX/UI Designer — Stage 6 mois (Allemagne)",
        "company": "Zalando",
        "company_type": "E-commerce mode · Berlin",
        "domain": "Design & UX",
        "contract": "Stage",
        "duration": "6 mois · démarrage janvier 2027",
        "location": "Berlin, Allemagne",
        "remote": "Hybride · 2 jours de télétravail",
        "salary": "1 100 € / mois",
        "summary": "Zalando repense l'expérience d'achat mode en Europe. Tu travailles en anglais avec des designers de toute l'Europe.",
        "description": (
            "Tu rejoins une équipe design internationale. Tu mènes des "
            "recherches utilisateurs, tu prototypes des parcours d'achat et tu "
            "fais vivre le design system de la plateforme."
        ),
        "missions": [
            "Mener des entretiens utilisateurs et des tests de maquettes.",
            "Concevoir des prototypes Figma pour les parcours d'achat.",
            "Contribuer au design system et à sa documentation.",
            "Présenter tes travaux en anglais lors des revues design.",
        ],
        "required_skills": [
            req("Figma", 4, 3, "indispensable"),
            req("UX Research", 3, 2, "important"),
            req("Prototypage", 3, 2, "important"),
            req("UI Design", 3, 2, "important"),
            req("Design System", 2, 2, "atout"),
            req("Accessibilité", 2, 1, "atout"),
        ],
        "qualities": [quality("Créativité", 3), quality("Sens du détail", 3), quality("Empathie", 3), quality("Esprit critique", 2)],
        "languages": [lang("Anglais", "C1", 3)],
        "certifications": [{"name": "Google UX Design Professional Certificate", "importance": "souhaitee"}],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": ["Design & UX", "Informatique & Développement", "Marketing & Communication"]},
        "nice_to_have": ["Design System", "Accessibilité", "Motion Design", "A/B testing"],
        "keywords": ["ux", "ui", "design", "berlin", "stage international", "e-commerce", "figma"],
        "accent": "#4B5D9E",
    },
]


JOBS_BY_ID = {job["id"]: job for job in JOBS}


def get_job(job_id: str) -> dict | None:
    return JOBS_BY_ID.get(job_id)


def job_search_text(job: dict) -> str:
    """Texte complet d'une offre, utilisé pour la recherche et la détection."""
    parts = [
        job.get("title", ""),
        job.get("company", ""),
        job.get("location", ""),
        job.get("summary", ""),
        job.get("description", ""),
        " ".join(job.get("missions", [])),
        " ".join(job.get("keywords", [])),
        " ".join(r["skill"] for r in job.get("required_skills", [])),
        " ".join(job.get("nice_to_have", [])),
    ]
    return " \n ".join(parts)


def empty_custom_job() -> dict:
    return {
        "id": "custom",
        "title": "",
        "company": "",
        "company_type": "Offre ajoutée manuellement",
        "domain": "Autre",
        "contract": "Stage",
        "duration": "",
        "location": "",
        "remote": "",
        "salary": "",
        "summary": "",
        "description": "",
        "missions": [],
        "required_skills": [],
        "qualities": [],
        "languages": [lang("Français", "C1", 2), lang("Anglais", "B2", 2)],
        "certifications": [],
        "education": {"min_level": "Bac+3 (Licence / BUT3)", "fields": []},
        "nice_to_have": [],
        "keywords": [],
        "accent": "#7A7F7B",
        "is_custom": True,
        "raw_text": "",
    }
