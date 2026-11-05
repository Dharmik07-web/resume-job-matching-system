"""
NLP and Text Extraction Utilities for AI Resume Screening & Job Matching System.
Handles PDF text extraction, Candidate Details, Skill & Experience Extraction,
and Actionable Gap Analysis.

Developed by DHARMIK MTH.
"""

import os
import re
from typing import Dict, List, Set, Tuple, Any

# Prefer pypdf, fallback to PyPDF2
try:
    import pypdf
    PDF_READER = "pypdf"
except ImportError:
    try:
        import PyPDF2 as pypdf
        PDF_READER = "PyPDF2"
    except ImportError:
        pypdf = None
        PDF_READER = None

# Comprehensive Skills Dictionary mapped to display names and normalized keys
TECH_SKILLS_CATALOG = {
    # Programming Languages
    "python": "Python",
    "java": "Java",
    "c": "C",
    "c++": "C++",
    "c#": "C#",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "dart": "Dart",
    "r": "R",
    "scala": "Scala",
    "perl": "Perl",
    "shell": "Shell Scripting",
    "bash": "Bash",
    "powershell": "PowerShell",
    "sql": "SQL",
    "nosql": "NoSQL",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sass": "Sass",
    "scss": "SCSS",

    # Web & Frameworks
    "react": "React",
    "reactjs": "React.js",
    "react.js": "React.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "angular": "Angular",
    "angularjs": "AngularJS",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "svelte": "Svelte",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "asp.net": "ASP.NET",
    ".net": ".NET",
    ".net core": ".NET Core",
    "laravel": "Laravel",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    "graphql": "GraphQL",
    "rest api": "RESTful API",
    "rest": "REST API",
    "restful": "RESTful API",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "jquery": "jQuery",
    "webpack": "Webpack",
    "vite": "Vite",

    # AI, Machine Learning, Data Science
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "computer vision": "Computer Vision",
    "opencv": "OpenCV",
    "llm": "Large Language Models (LLM)",
    "large language models": "Large Language Models (LLM)",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "rag": "RAG (Retrieval-Augmented Generation)",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "hugging face": "Hugging Face",
    "transformers": "Transformers",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    "spacy": "spaCy",
    "nltk": "NLTK",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "data analysis": "Data Analysis",
    "data science": "Data Science",
    "data modeling": "Data Modeling",
    "data visualization": "Data Visualization",
    "feature engineering": "Feature Engineering",
    "statistics": "Statistical Analysis",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",

    # Cloud, DevOps & Infrastructure
    "aws": "Amazon Web Services (AWS)",
    "amazon web services": "Amazon Web Services (AWS)",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud": "Google Cloud Platform (GCP)",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "linux": "Linux",
    "unix": "Unix",
    "ubuntu": "Ubuntu",
    "nginx": "Nginx",
    "apache": "Apache",
    "serverless": "Serverless",
    "lambda": "AWS Lambda",
    "cloudformation": "CloudFormation",
    "helm": "Helm",
    "prometheus": "Prometheus",
    "grafana": "Grafana",

    # Databases & Big Data
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "mssql": "MS SQL Server",
    "sql server": "MS SQL Server",
    "oracle": "Oracle Database",
    "cassandra": "Apache Cassandra",
    "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "firebase": "Firebase",
    "firestore": "Firestore",
    "supabase": "Supabase",
    "snowflake": "Snowflake",
    "bigquery": "Google BigQuery",
    "databricks": "Databricks",
    "redshift": "AWS Redshift",
    "hadoop": "Apache Hadoop",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "rabbitmq": "RabbitMQ",
    "etl": "ETL Pipelines",

    # Mobile, Testing & Cybersecurity
    "android": "Android Development",
    "ios": "iOS Development",
    "react native": "React Native",
    "flutter": "Flutter",
    "swiftui": "SwiftUI",
    "selenium": "Selenium",
    "cypress": "Cypress",
    "playwright": "Playwright",
    "pytest": "PyTest",
    "junit": "JUnit",
    "postman": "Postman",
    "swagger": "Swagger / OpenAPI",
    "unit testing": "Unit Testing",
    "integration testing": "Integration Testing",
    "cybersecurity": "Cybersecurity",
    "penetration testing": "Penetration Testing",
    "ethical hacking": "Ethical Hacking",
    "siem": "SIEM",
    "wireshark": "Wireshark",
    "metasploit": "Metasploit",
    "cryptography": "Cryptography",
    "owasp": "OWASP",
    "vulnerability assessment": "Vulnerability Assessment",
    "network security": "Network Security",
    "iam": "Identity and Access Management (IAM)",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "jira": "Jira",
    "agile": "Agile Methodology",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "microservices": "Microservices Architecture",
    "system design": "System Design",
    "oop": "Object-Oriented Programming (OOP)",
    "design patterns": "Design Patterns",
}

SOFT_SKILLS_CATALOG = {
    "communication": "Communication",
    "leadership": "Leadership",
    "teamwork": "Teamwork & Collaboration",
    "collaboration": "Collaboration",
    "problem solving": "Problem Solving",
    "problem-solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "time management": "Time Management",
    "adaptability": "Adaptability",
    "mentorship": "Mentorship",
    "presentation": "Presentation Skills",
    "negotiation": "Negotiation",
    "conflict resolution": "Conflict Resolution",
    "decision making": "Decision Making",
    "analytical thinking": "Analytical Thinking",
    "attention to detail": "Attention to Detail",
    "creative thinking": "Creative Thinking",
    "work ethic": "Strong Work Ethic",
    "project management": "Project Management",
    "stakeholder management": "Stakeholder Management",
}


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extracts raw text and total page count from a PDF file using pypdf/PyPDF2.
    """
    if not pypdf:
        raise ImportError("Neither pypdf nor PyPDF2 is installed in the environment.")

    extracted_text = []
    page_count = 0

    with open(pdf_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        page_count = len(reader.pages)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_text.append(page_text)

    full_text = "\n".join(extracted_text).strip()
    return full_text, page_count


def clean_text(text: str) -> str:
    """Standardizes text by removing non-ASCII and excess whitespace."""
    if not text:
        return ""
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_candidate_info(text: str) -> Dict[str, Any]:
    """
    Extracts candidate metadata including Name heuristic, Email, Phone,
    LinkedIn, GitHub, and Education keywords.
    """
    info = {
        "name": "Candidate",
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "education": [],
    }

    # Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        info["email"] = email_match.group(0)

    # Phone (US & International & Indian format)
    phone_pattern = r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})|(?:\+?91[-.\s]?[6-9]\d{9})"
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        info["phone"] = phone_match.group(0).strip()

    # LinkedIn
    linkedin_match = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9-_]+", text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-_]+", text, re.IGNORECASE)
    if github_match:
        info["github"] = github_match.group(0)

    # Education degrees
    degree_keywords = [
        "Ph.D.", "PhD", "Master of Science", "M.S.", "M.Tech", "M.E.", "MBA",
        "Bachelor of Science", "B.S.", "B.Tech", "B.E.", "BCA", "MCA",
        "Bachelor", "Master", "Diploma", "Associate Degree"
    ]
    detected_degrees = set()
    for degree in degree_keywords:
        pattern = r"\b" + re.escape(degree) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            detected_degrees.add(degree)
    info["education"] = sorted(list(detected_degrees))

    # Name heuristic: inspect first 5 non-empty lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:
        # Filter out email, phone, web urls, or section titles
        if any(keyword in line.lower() for keyword in ["resume", "curriculum", "vitae", "summary", "profile", "contact", "@", "http", "phone"]):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z.'-]+$", w) for w in words):
            info["name"] = " ".join(words)
            break

    return info


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extracts tech and soft skills from input text using boundary-safe regex matching.
    """
    text_lower = text.lower()
    matched_tech = set()
    matched_soft = set()

    # Helper matcher for specialized tokens like c++, c#, .net
    def match_skill(skill_key: str, target_text: str) -> bool:
        if skill_key in ["c++", "c#", ".net", ".net core"]:
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(skill_key)}(?![a-zA-Z0-9])"
        elif skill_key in ["r", "c"]:
            pattern = rf"\b{re.escape(skill_key)}\b"
        elif skill_key in ["ci/cd", "cicd"]:
            pattern = r"\bci\s*\/\s*cd\b|\bcicd\b"
        else:
            pattern = rf"\b{re.escape(skill_key)}\b"
        return bool(re.search(pattern, target_text))

    # Search Tech Catalog
    for skill_key, display_name in TECH_SKILLS_CATALOG.items():
        if match_skill(skill_key, text_lower):
            matched_tech.add(display_name)

    # Search Soft Catalog
    for skill_key, display_name in SOFT_SKILLS_CATALOG.items():
        if match_skill(skill_key, text_lower):
            matched_soft.add(display_name)

    return {
        "tech_skills": sorted(list(matched_tech)),
        "soft_skills": sorted(list(matched_soft)),
        "all_skills": sorted(list(matched_tech.union(matched_soft))),
    }


def extract_years_of_experience(text: str) -> Dict[str, Any]:
    """
    Extracts years of experience using multiple regex patterns and date calculations.
    """
    patterns = [
        # Example: '5+ years of experience', '7.5 years of work experience'
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*(?:relevant\s+|professional\s+|work\s+)?experience",
        # Example: 'Experience: 4 years', 'Total Experience: 6.5 Yrs'
        r"(?:total\s+)?experience[:\s]+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        # Example: 'over 8 years in Software Engineering'
        r"(?:over|around|more than)\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    detected_values = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                val = float(match.group(1))
                if 0.5 <= val <= 40:
                    detected_values.append(val)
            except ValueError:
                continue

    # Date range heuristic (e.g. 2018 - 2024 or 2019 - Present)
    date_range_pattern = r"\b((?:19|20)\d{2})\s*(?:-|–|to)\s*((?:19|20)\d{2}|present|current)\b"
    current_year = 2026
    date_spans = []
    for match in re.finditer(date_range_pattern, text, re.IGNORECASE):
        start_yr = int(match.group(1))
        end_str = match.group(2).lower()
        end_yr = current_year if end_str in ["present", "current"] else int(end_str)
        if end_yr >= start_yr and (end_yr - start_yr) <= 35:
            date_spans.append(end_yr - start_yr)

    if detected_values:
        max_exp = max(detected_values)
    elif date_spans:
        max_exp = max(date_spans)
    else:
        max_exp = 0.0

    return {
        "years": max_exp,
        "formatted": f"{int(max_exp) if max_exp.is_integer() else max_exp} Years" if max_exp > 0 else "Not explicitly stated",
        "is_detected": max_exp > 0
    }


def perform_gap_analysis(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Compares Resume skills against Job Description requirements.
    Identifies matched skills, missing skills, bonus skills, and provides
    actionable improvement recommendations.
    """
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(jd_text)

    resume_all = set(resume_skills["all_skills"])
    jd_all = set(jd_skills["all_skills"])

    matched_skills = sorted(list(resume_all.intersection(jd_all)))
    missing_skills = sorted(list(jd_all - resume_all))
    extra_skills = sorted(list(resume_all - jd_all))

    # Match ratio based on JD required skills
    if len(jd_all) > 0:
        skill_coverage_ratio = len(matched_skills) / len(jd_all)
    else:
        skill_coverage_ratio = 1.0 if len(resume_all) > 0 else 0.5

    # Actionable suggestions generation
    suggestions = []

    # 1. Missing skills suggestions
    if missing_skills:
        top_missing = missing_skills[:5]
        suggestions.append({
            "type": "missing_skills",
            "title": f"Incorporate Key Missing Skills ({len(missing_skills)} identified)",
            "description": f"The Job Description prominently seeks: {', '.join(top_missing)}. If you have practical experience or coursework with any of these, feature them explicitly in your Skills and Projects sections.",
            "impact": "High"
        })

    # 2. Metric & Quantification check
    metrics_pattern = r"\b(?:\d+%\s*(?:increase|decrease|growth|improvement|reduction)?|\$\d+[kKmM]?|\b\d+\s*(?:users|clients|projects|features|microservices|pipelines|endpoints)\b)"
    has_metrics = bool(re.search(metrics_pattern, resume_text, re.IGNORECASE))
    if not has_metrics:
        suggestions.append({
            "type": "quantify_results",
            "title": "Quantify Your Impact with Metrics & Numbers",
            "description": "Recruiters and ATS favor quantifiable achievements. Replace vague statements with concrete numbers (e.g., 'Optimized database queries reducing latency by 35%' or 'Led team delivering feature used by 10k+ daily users').",
            "impact": "High"
        })

    # 3. Action Verbs analysis
    action_verbs = [
        "architected", "spearheaded", "engineered", "implemented", "optimized",
        "designed", "developed", "orchestrated", "automated", "streamlined",
        "refactored", "built", "delivered", "deployed", "scaled"
    ]
    detected_verbs = [v for v in action_verbs if re.search(rf"\b{v}\b", resume_text, re.IGNORECASE)]
    if len(detected_verbs) < 3:
        suggestions.append({
            "type": "action_verbs",
            "title": "Use Strong Technical Action Verbs",
            "description": "Enhance bullet points by leading with decisive verbs such as 'Spearheaded', 'Architected', 'Automated', or 'Orchestrated' rather than passive phrasing like 'Responsible for' or 'Worked on'.",
            "impact": "Medium"
        })

    # 4. Links / Portfolio check
    candidate_info = extract_candidate_info(resume_text)
    if not candidate_info["github"] and not candidate_info["linkedin"]:
        suggestions.append({
            "type": "links",
            "title": "Include Active GitHub & LinkedIn Profiles",
            "description": "Tech recruiters verify practical coding ability. Add clickable links to your LinkedIn and GitHub profiles showing recent commits and repositories.",
            "impact": "Medium"
        })

    # 5. Experience verification
    resume_exp = extract_years_of_experience(resume_text)
    jd_exp = extract_years_of_experience(jd_text)
    if jd_exp["is_detected"] and resume_exp["is_detected"]:
        if resume_exp["years"] < jd_exp["years"]:
            suggestions.append({
                "type": "experience_gap",
                "title": f"Experience Gap: Position asks for ~{jd_exp['years']:.0f} years",
                "description": f"Resume indicates ~{resume_exp['years']:.0f} years. Highlight high-impact freelance projects, open-source contributions, or leadership roles to compensate for seniority requirements.",
                "impact": "Medium"
            })

    # If resume is already exceptional
    if not suggestions:
        suggestions.append({
            "type": "alignment",
            "title": "Excellent Keyword Alignment",
            "description": "Your resume reflects high congruence with the target position. Keep formatting clean, scannable, and tailored for ATS systems.",
            "impact": "Low"
        })

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "jd_skills_count": len(jd_all),
        "resume_skills_count": len(resume_all),
        "skill_coverage_percent": round(skill_coverage_ratio * 100, 1),
        "suggestions": suggestions,
        "resume_details": {
            "tech_skills": resume_skills["tech_skills"],
            "soft_skills": resume_skills["soft_skills"],
        },
        "jd_details": {
            "tech_skills": jd_skills["tech_skills"],
            "soft_skills": jd_skills["soft_skills"],
        }
    }
