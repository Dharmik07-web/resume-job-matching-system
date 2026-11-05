# SkillSync AI - Production AI Resume Screening & Job Matching System

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.x-emerald.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20TF--IDF-orange.svg)](https://scikit-learn.org/)
[![PDF Parsing](https://img.shields.io/badge/Parser-pypdf%20%2F%20PyPDF2-red.svg)](https://pypdf.readthedocs.io/)
[![Author](https://img.shields.io/badge/Developed%20By-DHARMIK%20MTH-purple.svg)](#developed-by)

A modern, production-ready AI Resume Screening and Job Matching platform that automates candidate screening, skill extraction, ATS score evaluation, and job role classification using Machine Learning and NLP.

> **Designed and Developed by DHARMIK MTH**

---

## 🌟 Key Features

1. **Resume Upload & Multi-Page PDF Parsing**:
   - Clean, drag-and-drop web interface for PDF resumes (and direct text input).
   - High-throughput text extraction powered by `pypdf` and `PyPDF2` with layout preservation and Unicode normalization.

2. **Skill & Experience NLP Extraction**:
   - Boundary-safe keyword extraction matching against an extensive catalog of 300+ technical and soft skills.
   - Automatic extraction of candidate metadata: Name, Email, Phone, LinkedIn, GitHub, and Education degrees.
   - Heuristic and regex extraction for total years of professional experience.

3. **Job Description Comparison & Scoring**:
   - Instant TF-IDF Vectorizer with unigrams and bigrams (`(1, 2)`) removing English stop words.
   - Cosine Similarity computation between candidate resume and target Job Description.
   - Calibrated Composite ATS Match Score combining TF-IDF semantic alignment (50%) and direct skill requirement coverage (50%).

4. **Actionable Gap Analysis & Suggestions**:
   - Pinpoints missing critical technical and domain requirements.
   - Provides prioritized recommendations (High / Medium / Low Impact) to optimize resume readability, incorporate measurable metrics, and strengthen action verbs.

5. **Machine Learning Job Category Classification**:
   - Supervised Scikit-learn Classifier trained on Kaggle's `UpdatedResumeDataSet.csv` across 25 job domains.
   - Delivers **98.96% test accuracy**.
   - Outputs top predicted job profile, confidence percentage, and alternative matching profiles.

6. **Responsive Glassmorphism UI**:
   - Modern dark-mode interface built with Tailwind CSS, custom glass panels, and Bootstrap Icons.
   - Animated SVG circular gauge for ATS fit score.
   - One-click sample loaders (Senior Data Scientist, Full Stack Python Dev, DevOps Engineer).
   - Export analysis as JSON or formatted printable report.

---

## 📂 Project Structure

```text
resume/
├── app.py                     # Flask application backend & routing
├── model.py                   # TF-IDF cosine similarity & ML classifier inference
├── train_model.py             # Model training pipeline on UpdatedResumeDataSet.csv
├── nlp_utils.py               # PDF parser, skill dictionary & gap analysis engine
├── dataset/
│   └── UpdatedResumeDataSet.csv   # Kaggle dataset (962 resumes, 25 categories)
├── models/
│   ├── resume_classifier.pkl  # Serialized Logistic Regression model
│   ├── tfidf_vectorizer.pkl   # Serialized TF-IDF feature extractor
│   └── label_encoder.pkl      # Serialized label encoder for 25 categories
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphism, gauges & responsive layout
│   ├── js/
│   │   └── main.js            # Dropzone, preset loaders, copy & JSON export
│   ├── uploads/               # Secure uploaded resume storage
│   └── sample_resumes/        # Pre-generated sample PDF resumes
├── templates/
│   ├── index.html             # Landing page with drag-and-drop & preset toolbar
│   └── results.html           # Interactive results dashboard & ATS scorecard
├── requirements.txt           # Python dependency requirements
└── README.md                  # Comprehensive documentation & credits
```

---

## 🚀 Quick Start & Installation

### 1. Clone or Open the Repository
```bash
cd d:\Projects\newwww\resume
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Train or Re-Train the ML Classifier
The trained model artifacts are already included in the `models/` directory. To retrain at any time:
```bash
python train_model.py
```
*Output:*
```text
============================================================
AI Resume Screening & Job Matching System
Model Training Pipeline - Developed by DHARMIK MTH
============================================================
Total resumes: 962 across 25 categories
Test Accuracy: 98.96%
Artifacts saved to: models/
```

### 5. Launch the Web Application
```bash
python app.py
```
The application will launch locally at:
👉 **http://127.0.0.1:5000**

---

## 🧪 Testing the Application

### Method A: Instant 1-Click Demos
1. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
2. Click any of the instant demo buttons at the top:
   - ⚡ **Senior Data Scientist**
   - ⚡ **Python Full Stack**
   - ⚡ **DevOps & Cloud**
3. Click **"Run AI Screening & Matching"** to see instant real-time results.

### Method B: Upload Real Sample PDFs
Sample PDF resumes are included in `static/sample_resumes/`:
- `static/sample_resumes/sample_data_scientist.pdf`
- `static/sample_resumes/sample_python_developer.pdf`

Drag and drop either file into the upload zone, paste your target job description, and run analysis.

---

## 🔌 Headless JSON API

The application exposes a REST API endpoint for integration into external ATS software:

### `POST /api/analyze`
**Request Body:**
```json
{
  "resume_text": "Experienced Python Developer with 5 years experience in FastAPI, Docker, and PostgreSQL...",
  "job_description": "Looking for a Python Developer proficient in Python, Docker, Kubernetes, and AWS..."
}
```

**Response:**
```json
{
  "success": true,
  "credits": "Developed by DHARMIK MTH",
  "candidate": {
    "name": "Candidate",
    "email": "alex.dev@example.com",
    "phone": "+1 (555) 234-5678",
    "education": ["Bachelor of Science"]
  },
  "experience": {
    "resume": {"years": 5.0, "formatted": "5 Years", "is_detected": true},
    "job_description": {"years": 3.0, "formatted": "3 Years", "is_detected": true}
  },
  "scoring": {
    "overall_score": 85.5,
    "tfidf_score": 78.2,
    "skill_score": 92.8,
    "rating": "Excellent Fit",
    "summary_message": "Outstanding alignment with the job description."
  },
  "predicted_category": {
    "top_category": "Python Developer",
    "confidence": 94.2,
    "alternatives": [
      {"category": "DevOps Engineer", "confidence": 3.5}
    ]
  },
  "gap_analysis": {
    "matched_skills": ["Docker", "FastAPI", "PostgreSQL", "Python"],
    "missing_skills": ["AWS", "Kubernetes"],
    "skill_coverage_percent": 66.7,
    "suggestions": [...]
  }
}
```

---

## 📊 25 Supported Job Categories

The classifier recognizes 25 diverse professional domains:
- Advocate
- Arts
- Automation Testing
- Blockchain
- Business Analyst
- Civil Engineer
- Data Science
- Database
- DevOps Engineer
- DotNet Developer
- ETL Developer
- Electrical Engineering
- HR
- Hadoop
- Health and fitness
- Java Developer
- Mechanical Engineer
- Network Security Engineer
- Operations Manager
- PMO
- Python Developer
- SAP Developer
- Sales
- Testing
- Web Designing

---

## 👨‍💻 Developed By

**DHARMIK MTH**  
- **System**: SkillSync AI - AI Resume Screening & Job Matching Platform  
- **Tech Stack**: Python 3.13, Flask, Scikit-learn, TF-IDF, PyPDF2/pypdf, Pandas, NumPy, Tailwind CSS  
- **Version**: 2.0.0 Pro  
- **License**: MIT License  

---
*Crafted with precision & passion by DHARMIK MTH.*
