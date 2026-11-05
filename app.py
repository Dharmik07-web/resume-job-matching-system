"""
AI Resume Screening & Job Matching System
Flask Backend Application

Developed by DHARMIK MTH.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename

from model import get_classifier, JobMatcher
from nlp_utils import (
    extract_text_from_pdf,
    clean_text,
    extract_candidate_info,
    extract_skills_from_text,
    extract_years_of_experience,
    perform_gap_analysis
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dharmik-mth-ai-resume-screener-secret-2026"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max limit

# Global Brand Credits
APP_META = {
    "title": "SkillSync AI - Resume Screening & Job Matching System",
    "developer": "DHARMIK MTH",
    "version": "2.0.0 Pro",
    "year": "2026"
}


# Pre-configured Sample Resumes and Job Descriptions for 1-Click Demos
SAMPLE_PRESETS = {
    "data_science": {
        "title": "Senior Data Scientist & AI Engineer",
        "jd": """Senior Data Scientist & Machine Learning Engineer
Location: Remote / Hybrid | Experience: 3-5 Years

Job Overview:
We are seeking a seasoned Senior Data Scientist to architect and deploy predictive machine learning models and Generative AI solutions. You will collaborate with cross-functional engineering teams to scale AI systems into production.

Key Responsibilities:
- Design, train, and deploy supervised and unsupervised Machine Learning models using Python, Scikit-Learn, and PyTorch.
- Build NLP pipelines, LLM-based solutions, and RAG architectures for automated document intelligence.
- Analyze large-scale datasets with Pandas, NumPy, and SQL; build actionable dashboards in Tableau or Power BI.
- Containerize and operationalize ML models using Docker, FastAPI, and AWS SageMaker.
- Conduct A/B testing, feature engineering, and statistical modeling to measure model drift and business KPIs.

Requirements & Qualifications:
- Bachelor's or Master's degree in Computer Science, Data Science, or related quantitative discipline.
- 3+ years of hands-on experience in Python, Machine Learning, Deep Learning, and NLP.
- Strong proficiency in SQL, PostgreSQL, Docker, Git, and CI/CD pipelines.
- Excellent communication and problem-solving skills; experience in Agile/Scrum environments.""",
        "resume": """ALEXANDER REED
Email: alex.reed.ai@example.com | Phone: +1 (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alexreed-ai | GitHub: github.com/alexreed-ml

PROFESSIONAL SUMMARY:
Accomplished Data Scientist & Machine Learning Engineer with 4.5 years of experience designing, training, and deploying end-to-end AI applications. Proven track record in NLP, LLMs, computer vision, and high-performance predictive systems, delivering 30%+ efficiency gains in production environments.

CORE SKILLS:
- Programming: Python, SQL, C++, Bash
- ML/AI: Machine Learning, Deep Learning, NLP, Generative AI, RAG, Scikit-Learn, PyTorch, TensorFlow, Pandas, NumPy, spaCy, NLTK
- Cloud & DevOps: AWS, Docker, Kubernetes, FastAPI, Git, CI/CD, Linux
- Databases & BI: PostgreSQL, MongoDB, Redis, Tableau, Power BI
- Methodologies: Agile, Scrum, Statistical Analysis, Feature Engineering

PROFESSIONAL EXPERIENCE:
Lead Machine Learning Engineer | DataCore Analytics | 2022 - Present
- Architected enterprise RAG and NLP search pipelines using Python, PyTorch, and FastAPI, serving 250k+ daily queries and reducing latency by 42%.
- Trained custom Scikit-Learn predictive models achieving 94% classification accuracy; decreased customer churn rate by 18%.
- Containerized model inference microservices with Docker and deployed onto AWS Kubernetes clusters with automated CI/CD.

Data Scientist | CloudWave Solutions | 2020 - 2022
- Developed customer segmentation models and automated ETL data pipelines utilizing Python, Pandas, and PostgreSQL for 15M+ transaction records.
- Spearheaded interactive executive BI dashboards in Tableau, driving strategic decision making across 4 department heads.
- Mentored 3 junior data analysts on Git workflows and statistical hypothesis testing.

EDUCATION:
- Master of Science in Computer Science | Stanford University (2020)
- Bachelor of Science in Data Science | University of California, Berkeley (2018)"""
    },
    "python_dev": {
        "title": "Full Stack Python Developer",
        "jd": """Senior Full Stack Python Developer
Location: New York / Remote | Experience: 4+ Years

We are seeking a talented Senior Python Developer with strong backend and frontend fundamentals. You will lead the development of high-throughput web applications, REST APIs, and microservices.

Core Requirements:
- 4+ years of professional software development experience in Python, Django, or FastAPI.
- Solid experience in Frontend frameworks: React, TypeScript, HTML5, CSS3, and Tailwind CSS.
- Production experience with PostgreSQL, Redis caching, and Docker microservice deployments.
- Expertise in AWS cloud infrastructure, CI/CD pipelines (GitHub Actions), and Git.
- Experience with Unit Testing (PyTest), GraphQL or RESTful APIs, and Agile development.""",
        "resume": """DAVID CHEN
Email: david.chen.dev@example.com | Phone: +1 (555) 876-5432 | Austin, TX
LinkedIn: linkedin.com/in/davidchendev | GitHub: github.com/davidchen-code

PROFESSIONAL SUMMARY:
Senior Full Stack Python Developer with 5 years of experience engineering resilient web applications and microservices. Specialist in Python, FastAPI, Django, React, and cloud-native containerized deployments.

TECHNICAL PROFICIENCIES:
- Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
- Frameworks & Libraries: FastAPI, Django, Flask, React, Redux, Tailwind CSS, Bootstrap
- Cloud & DevOps: AWS, Docker, GitHub Actions, CI/CD, Linux, Nginx
- Databases: PostgreSQL, MySQL, Redis, MongoDB
- Practices: REST API, GraphQL, PyTest, Agile, Scrum, System Design

EXPERIENCE:
Senior Backend Engineer | Vertex Software | 2022 - Present
- Engineered high-throughput RESTful microservices using Python and FastAPI, handling 12k requests per second with 99.99% uptime.
- Built responsive user dashboards in React and TypeScript styled with Tailwind CSS, increasing user engagement by 35%.
- Implemented multi-tier caching with Redis and PostgreSQL query tuning, reducing page load times by 55%.

Software Engineer | NexaTech Systems | 2019 - 2022
- Developed scalable Django web applications and integrated Stripe payment gateways for 50k+ active subscribers.
- Established automated CI/CD deployment pipelines using GitHub Actions and Docker containers deployed to AWS ECS.

EDUCATION:
- Bachelor of Science in Computer Science | University of Texas at Austin (2019)"""
    },
    "devops_engineer": {
        "title": "DevOps & Cloud Engineer",
        "jd": """Senior DevOps & Cloud Platform Engineer
Experience: 3+ Years | Location: Remote

Responsibilities:
- Build and maintain infrastructure as code using Terraform and Ansible across AWS and Kubernetes (EKS).
- Manage robust CI/CD pipelines using Jenkins and GitHub Actions.
- Implement comprehensive monitoring, alerting, and telemetry using Prometheus, Grafana, and ELK stack.
- Automate Linux server provisioning, Docker containerization, and network security hardening.
- Collaborate with engineering teams to optimize cloud costs and enforce zero-trust security policies.""",
        "resume": """SARAH JENKINS
Email: sarah.jenkins.devops@example.com | Phone: +1 (555) 345-9876 | Seattle, WA
LinkedIn: linkedin.com/in/sarahjenkins-devops | GitHub: github.com/sarah-cloud

SUMMARY:
DevOps and Cloud Infrastructure Engineer with 4 years of experience orchestrating AWS cloud architecture, Kubernetes clusters, and automated CI/CD delivery pipelines.

CORE COMPETENCIES:
- Cloud & Infrastructure: AWS, Terraform, Ansible, Docker, Kubernetes, Helm
- CI/CD & Automation: GitHub Actions, Jenkins, Bash, Python, Linux
- Monitoring & Logging: Prometheus, Grafana, Elasticsearch
- Networking & Security: Network Security, IAM, Firewalls, SSL/TLS, Nginx
- Collaboration: Git, Agile, Jira, Scrum

EXPERIENCE:
DevOps Engineer | CloudScale Systems | 2021 - Present
- Automated multi-region AWS cloud infrastructure using Terraform, cutting deployment provisioning time from 4 days to 15 minutes.
- Maintained production Kubernetes (EKS) clusters hosting 60+ microservices, achieving 99.98% service reliability.
- Implemented observability stack using Prometheus and Grafana dashboards with automated Slack alerts.

Cloud Support Specialist | Apex Technologies | 2020 - 2021
- Scripted automated Linux server backups and compliance audits using Python and Bash.
- Standardized Docker images across 8 dev teams, reducing image sizes by 60%.

EDUCATION:
- Bachelor of Science in Information Technology | University of Washington (2020)"""
    }
}


def allowed_file(filename: str) -> bool:
    """Verifies file extension against whitelist."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.context_processor
def inject_app_meta():
    """Injects developer branding and meta into all Jinja templates."""
    return dict(app_meta=APP_META)


@app.route("/", methods=["GET"])
def index():
    """Landing page with clean modern UI, file upload, and sample presets."""
    return render_template("index.html", presets=SAMPLE_PRESETS)


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Core screening endpoint:
    - Parses PDF (or raw text)
    - Performs NLP skill & experience extraction
    - Predicts resume job category via Scikit-learn
    - Computes TF-IDF Cosine Similarity and calibrated match score
    - Performs gap analysis with actionable suggestions
    """
    resume_text = ""
    original_filename = "Pasted Resume Text"
    page_count = 1

    # Check for file upload
    if "resume_file" in request.files:
        file = request.files["resume_file"]
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("Invalid file format. Please upload a PDF or TXT file.", "error")
                return redirect(url_for("index"))

            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(save_path)

            ext = original_filename.rsplit(".", 1)[1].lower()
            if ext == "pdf":
                try:
                    resume_text, page_count = extract_text_from_pdf(save_path)
                except Exception as e:
                    flash(f"Error parsing PDF file: {str(e)}", "error")
                    return redirect(url_for("index"))
            else:
                with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
                    resume_text = f.read()

    # Fallback to direct text area if no file was uploaded
    if not resume_text.strip():
        resume_text = request.form.get("resume_text", "").strip()

    job_description = request.form.get("job_description", "").strip()

    if not resume_text:
        flash("Please upload a resume PDF or paste resume text to analyze.", "error")
        return redirect(url_for("index"))

    if not job_description:
        flash("Please provide a Job Description to compare against.", "error")
        return redirect(url_for("index"))

    # 1. Candidate Info Extraction
    candidate_info = extract_candidate_info(resume_text)

    # 2. Years of Experience Extraction
    resume_experience = extract_years_of_experience(resume_text)
    jd_experience = extract_years_of_experience(job_description)

    # 3. NLP Skill Extraction & Gap Analysis
    gap_analysis = perform_gap_analysis(resume_text, job_description)

    # 4. TF-IDF Cosine Similarity & Composite Match Score
    match_results = JobMatcher.evaluate_match(
        resume_text=resume_text,
        jd_text=job_description,
        skill_coverage_percent=gap_analysis["skill_coverage_percent"]
    )

    # 5. ML Classifier Category Prediction
    classifier = get_classifier()
    category_prediction = classifier.predict_category(resume_text)

    # Compile structured analysis
    analysis_data = {
        "filename": original_filename,
        "page_count": page_count,
        "candidate": candidate_info,
        "resume_experience": resume_experience,
        "jd_experience": jd_experience,
        "gap_analysis": gap_analysis,
        "match": match_results,
        "classification": category_prediction,
        "resume_preview": clean_text(resume_text)[:800] + ("..." if len(resume_text) > 800 else ""),
        "jd_preview": clean_text(job_description)[:800] + ("..." if len(job_description) > 800 else ""),
    }

    return render_template("results.html", data=analysis_data)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Headless JSON API endpoint for programmatic screening."""
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not resume_text or not job_description:
        return jsonify({
            "success": False,
            "error": "Both 'resume_text' and 'job_description' fields are required."
        }), 400

    candidate_info = extract_candidate_info(resume_text)
    resume_experience = extract_years_of_experience(resume_text)
    jd_experience = extract_years_of_experience(job_description)
    gap_analysis = perform_gap_analysis(resume_text, job_description)

    match_results = JobMatcher.evaluate_match(
        resume_text=resume_text,
        jd_text=job_description,
        skill_coverage_percent=gap_analysis["skill_coverage_percent"]
    )

    classifier = get_classifier()
    category_prediction = classifier.predict_category(resume_text)

    return jsonify({
        "success": True,
        "credits": "Developed by DHARMIK MTH",
        "candidate": candidate_info,
        "experience": {
            "resume": resume_experience,
            "job_description": jd_experience
        },
        "scoring": match_results,
        "gap_analysis": gap_analysis,
        "predicted_category": category_prediction
    })


@app.route("/sample/<preset_key>", methods=["GET"])
def get_sample_preset(preset_key):
    """Returns preset JSON for quick UI population."""
    preset = SAMPLE_PRESETS.get(preset_key)
    if not preset:
        return jsonify({"error": "Preset not found"}), 404
    return jsonify(preset)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "app": APP_META["title"],
        "developer": APP_META["developer"],
        "version": APP_META["version"]
    })


if __name__ == "__main__":
    # Pre-warm classifier model on startup
    print(f"Starting {APP_META['title']}...")
    print(f"Credits: Developed by {APP_META['developer']}")
    get_classifier()
    print("AI Model loaded and ready. Starting Flask web server on port 5000...")
    app.run(host="127.0.0.1", port=5000, debug=False)
