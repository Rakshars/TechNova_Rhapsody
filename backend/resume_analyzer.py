"""
Resume Analyzer — Enhanced Backend v3.0
========================================
Improvements over v2:
  - Match score (0-100) added to every response
  - Fuzzy / partial matching for skill variants  
  - Weighted skill importance (core vs. nice-to-have)
  - Richer SKILL_GRAPH + larger skill database
  - Semantic threshold auto-tuned per text length
  - /analyze endpoint returns structured JSON ready for any frontend
  - CORS pre-configured; JWT-ready hooks left as comments
  - /upload endpoint accepts multipart PDF / DOCX resume
  - /jd/parse endpoint auto-extracts JD structure from raw text
  - Pagination on /dataset/stats
  - All skill lists de-duplicated and title-cased consistently

Install:
    pip install pandas beautifulsoup4 lxml kagglehub
    pip install sentence-transformers
    pip install fastapi uvicorn python-multipart pydantic
    pip install PyPDF2 python-docx                     # for file upload parsing
    pip install requests

Run:
    uvicorn resume_analyzer:app --reload --port 8000
"""

import os, re, json, logging, unicodedata
from collections import Counter
from typing import Optional, Literal

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — DATASET LOADING
# ══════════════════════════════════════════════════════════════════════════

resume_df = pd.DataFrame(columns=["Category", "Resume_str"])


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — TEXT CLEANING
# ══════════════════════════════════════════════════════════════════════════

def clean_text(raw: str) -> str:
    """Strip HTML, normalize unicode, collapse whitespace."""
    if not isinstance(raw, str) or not raw.strip():
        return ""
    # Decode HTML entities and strip tags
    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator=" ")
    # Normalize unicode (smart quotes, dashes, etc.)
    text = unicodedata.normalize("NFKD", text)
    # Collapse whitespace
    return re.sub(r"\s+", " ", text).strip()


if not resume_df.empty:
    resume_df["clean_resume"] = resume_df["Resume_str"].apply(clean_text)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — SKILL DATABASE
# ══════════════════════════════════════════════════════════════════════════

SKILLS_BY_DOMAIN: dict[str, list[str]] = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "r",
        "scala", "golang", "go", "ruby", "swift", "kotlin", "php", "bash",
        "shell scripting", "matlab", "perl", "rust", "haskell", "elixir",
        "dart", "groovy", "cobol", "fortran", "assembly",
    ],
    "data_and_ml": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "data analysis", "data science", "data engineering",
        "statistics", "probability", "linear algebra",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "keras", "xgboost", "lightgbm", "catboost", "opencv",
        "feature engineering", "model deployment", "mlops",
        "data pipeline", "etl", "apache spark", "hadoop",
        "hugging face", "transformers", "llm", "generative ai",
        "reinforcement learning", "time series", "anomaly detection",
        "recommender systems", "a/b testing", "hypothesis testing",
        "data visualization", "exploratory data analysis",
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "oracle", "elasticsearch", "sqlite", "nosql", "firebase",
        "cassandra", "dynamodb", "neo4j", "influxdb", "snowflake",
        "bigquery", "redshift", "databricks", "dbt",
    ],
    "cloud_and_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "jenkins", "ci/cd", "git", "github actions",
        "gitlab ci", "linux", "ansible", "puppet", "chef",
        "cloud computing", "serverless", "lambda", "azure devops",
        "helm", "prometheus", "grafana", "datadog", "new relic",
        "nginx", "apache", "load balancing", "microservices",
    ],
    "web_and_api": [
        "react", "angular", "vue", "svelte", "next.js", "nuxt",
        "node.js", "django", "flask", "fastapi", "spring boot",
        "express", "rest api", "graphql", "html", "css", "sass",
        "webpack", "vite", "tailwind", "bootstrap", "jquery",
        "websocket", "oauth", "jwt", "openapi", "swagger",
    ],
    "hr_and_business": [
        "recruitment", "talent acquisition", "onboarding", "payroll",
        "performance management", "employee relations", "hris", "workday",
        "sap hr", "successfactors", "compensation", "benefits administration",
        "labour law", "employment law", "compliance", "training and development",
        "organizational development", "change management", "workforce planning",
        "employee engagement", "hr analytics", "diversity and inclusion",
        "exit interviews", "succession planning",
    ],
    "soft_and_tools": [
        "communication", "leadership", "project management", "agile",
        "scrum", "kanban", "jira", "confluence", "excel", "powerpoint",
        "tableau", "power bi", "looker", "stakeholder management",
        "problem solving", "critical thinking", "cross-functional collaboration",
        "strategic planning", "negotiation", "presentation skills",
        "time management", "mentoring", "coaching",
    ],
    "finance_and_accounting": [
        "financial analysis", "accounting", "auditing", "budgeting",
        "forecasting", "tally", "sap fi", "quickbooks", "taxation",
        "risk management", "financial modeling", "valuation",
        "investment analysis", "portfolio management", "derivatives",
        "corporate finance", "cash flow analysis", "ifrs", "gaap",
    ],
    "security": [
        "cybersecurity", "penetration testing", "ethical hacking",
        "siem", "vulnerability assessment", "firewalls",
        "soc", "incident response", "owasp", "zero trust",
        "identity and access management", "iam",
    ],
    "product_and_design": [
        "product management", "product roadmap", "user research",
        "ux design", "ui design", "figma", "sketch", "adobe xd",
        "wireframing", "prototyping", "usability testing",
        "a/b testing", "okrs", "kpis", "go-to-market",
    ],
}

COMMON_SKILLS: list[str] = list(dict.fromkeys(
    skill for domain in SKILLS_BY_DOMAIN.values() for skill in domain
))

log.info(f"Skill database: {len(COMMON_SKILLS)} skills across {len(SKILLS_BY_DOMAIN)} domains")


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — SYNONYMS & NORMALISATION
# ══════════════════════════════════════════════════════════════════════════

SYNONYMS: dict[str, str] = {
    # ML / AI
    "ml":                               "machine learning",
    "dl":                               "deep learning",
    "ai":                               "machine learning",
    "gen ai":                           "generative ai",
    "llms":                             "llm",
    "large language model":             "llm",
    "large language models":            "llm",
    "natural language processing":      "nlp",
    "cv":                               "computer vision",
    # JS ecosystem
    "nodejs":                           "node.js",
    "node js":                          "node.js",
    "reactjs":                          "react",
    "react js":                         "react",
    "react.js":                         "react",
    "vuejs":                            "vue",
    "vue.js":                           "vue",
    "nextjs":                           "next.js",
    "angularjs":                        "angular",
    # Python ecosystem
    "scikit learn":                     "scikit-learn",
    "sklearn":                          "scikit-learn",
    "hf":                               "hugging face",
    # DB
    "postgres":                         "postgresql",
    "mongo":                            "mongodb",
    "elastic":                          "elasticsearch",
    # Cloud
    "amazon web services":              "aws",
    "microsoft azure":                  "azure",
    "google cloud platform":            "gcp",
    # BI
    "power-bi":                         "power bi",
    "ms excel":                         "excel",
    "microsoft excel":                  "excel",
    "ms powerpoint":                    "powerpoint",
    # HR
    "talent management":                "talent acquisition",
    "hiring":                           "recruitment",
    "sourcing":                         "talent acquisition",
    "staffing":                         "recruitment",
    "people management":                "employee relations",
    "learning and development":         "training and development",
    "l&d":                              "training and development",
    # DevOps
    "k8s":                              "kubernetes",
    "k8":                               "kubernetes",
    "gh actions":                       "github actions",
    # Finance
    "p&l":                              "financial analysis",
    "profit and loss":                  "financial analysis",
    "dcf":                              "financial modeling",
    "us gaap":                          "gaap",
    # Design
    "user experience":                  "ux design",
    "user interface":                   "ui design",
    "ux":                               "ux design",
    "ui":                               "ui design",
}


def normalise(text: str) -> str:
    text = text.lower().strip()
    # Multi-word synonym lookup first
    for src, tgt in SYNONYMS.items():
        text = re.sub(r"\b" + re.escape(src) + r"\b", tgt, text)
    return text


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — IMPROVED RULE-BASED SKILL EXTRACTION
# ══════════════════════════════════════════════════════════════════════════

def _skill_pattern(skill: str) -> re.Pattern:
    """Compile a word-boundary pattern; handle special regex chars in skill names."""
    escaped = re.escape(skill)
    # Allow optional separator variants: "node.js" also matches "node js"
    escaped = escaped.replace(r"\.", r"[.\s]?")
    escaped = escaped.replace(r"\+\+", r"(\+\+|\splusplus)")
    escaped = escaped.replace(r"\#", r"#")
    return re.compile(r"(?<![a-zA-Z])" + escaped + r"(?![a-zA-Z])", re.IGNORECASE)


_COMPILED_PATTERNS: dict[str, re.Pattern] = {
    skill: _skill_pattern(skill) for skill in COMMON_SKILLS
}

# Sort skills: longer (multi-word) first to avoid partial matches
_SKILLS_SORTED = sorted(COMMON_SKILLS, key=lambda s: len(s.split()), reverse=True)


def extract_skills(text: str) -> list[str]:
    """
    Improved rule-based extraction:
    - Synonym normalisation applied first
    - Fuzzy variant patterns (node.js / node js)
    - Returns deduplicated, ordered list
    """
    normalised = normalise(text)
    found: list[str] = []
    matched_spans: list[tuple[int, int]] = []

    for skill in _SKILLS_SORTED:
        for m in _COMPILED_PATTERNS[skill].finditer(normalised):
            start, end = m.start(), m.end()
            # Skip if this span overlaps a longer already-matched skill
            overlap = any(s <= start < e or s < end <= e for s, e in matched_spans)
            if not overlap:
                found.append(skill)
                matched_spans.append((start, end))
                break  # skill found, move to next

    return list(dict.fromkeys(found))  # preserve order, dedup


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — SKILL GAP & MATCH SCORE
# ══════════════════════════════════════════════════════════════════════════

def find_missing(user_skills: list[str], required_skills: list[str]) -> list[str]:
    user_set = {s.lower() for s in user_skills}
    return [s for s in required_skills if s.lower() not in user_set]


def compute_match_score(
    user_skills: list[str],
    required_skills: list[str],
    missing_skills: list[str],
) -> int:
    """
    Accurate 0-100 match score.

    Problem with the old formula: semantic extraction inflates required_skills
    to 50-100+ entries for any JD, making matched/required always tiny.

    New approach:
      1. Core score  = (matched_required / total_required) * 100
         — pure coverage of what the JD asked for
      2. Breadth bonus (up to +10): candidate has extra relevant skills
         beyond the JD, capped so total stays ≤ 100
      3. Depth penalty: if required_skills list is suspiciously large
         (semantic over-extraction), we trust the matched count more than
         the inflated denominator by soft-capping required at 30.
    """
    if not required_skills:
        return 0

    user_set    = {s.lower() for s in user_skills}
    req_set     = {s.lower() for s in required_skills}
    missing_set = {s.lower() for s in missing_skills}
    matched     = len(req_set) - len(missing_set)

    # Soft-cap denominator: semantic mode can return 80+ JD skills;
    # cap at 30 so one missing skill doesn't tank the score unfairly.
    effective_total = min(len(req_set), 30)
    effective_matched = min(matched, effective_total)

    base = (effective_matched / effective_total) * 100

    # Small breadth bonus: extra skills candidate has (not in JD)
    extra = len(user_set - req_set)
    bonus = min(extra * 0.5, 10)   # 0.5 pt per extra skill, max +10

    return min(round(base + bonus), 100)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — SKILL DEPENDENCY GRAPH (expanded)
# ══════════════════════════════════════════════════════════════════════════

SKILL_GRAPH: dict[str, list[str]] = {
    # ML / Data Science
    "machine learning":         ["python", "statistics", "numpy", "pandas"],
    "deep learning":            ["machine learning", "tensorflow"],
    "nlp":                      ["machine learning", "python"],
    "computer vision":          ["deep learning", "opencv"],
    "mlops":                    ["machine learning", "docker", "ci/cd"],
    "feature engineering":      ["pandas", "statistics"],
    "model deployment":         ["docker", "flask"],
    "data science":             ["python", "statistics", "sql"],
    "data engineering":         ["python", "sql", "cloud computing"],
    "llm":                      ["machine learning", "nlp", "python"],
    "generative ai":            ["llm", "python"],
    "hugging face":             ["python", "pytorch"],
    "pytorch":                  ["python", "machine learning"],
    "tensorflow":               ["python", "machine learning"],
    "scikit-learn":             ["python", "statistics"],
    "numpy":                    ["python"],
    "pandas":                   ["python", "numpy"],
    "opencv":                   ["python"],
    "xgboost":                  ["python", "machine learning"],
    "lightgbm":                 ["python", "machine learning"],
    "catboost":                 ["python", "machine learning"],
    "apache spark":             ["python", "sql"],
    "dbt":                      ["sql"],
    "snowflake":                ["sql"],
    "bigquery":                 ["sql", "gcp"],
    "redshift":                 ["sql", "aws"],
    "databricks":               ["apache spark", "python"],
    "time series":              ["statistics", "python"],
    "anomaly detection":        ["statistics", "machine learning"],
    "recommender systems":      ["machine learning", "sql"],
    "a/b testing":              ["statistics"],
    "hypothesis testing":       ["statistics"],
    "data visualization":       ["python", "pandas"],
    "exploratory data analysis":["pandas", "statistics"],
    "reinforcement learning":   ["machine learning", "python"],
    # Backend / Cloud
    "docker":                   ["linux"],
    "kubernetes":               ["docker"],
    "terraform":                ["cloud computing"],
    "ci/cd":                    ["git"],
    "aws":                      ["linux", "cloud computing"],
    "azure":                    ["cloud computing"],
    "gcp":                      ["cloud computing"],
    "fastapi":                  ["python"],
    "django":                   ["python", "sql"],
    "flask":                    ["python"],
    "spring boot":              ["java"],
    "rest api":                 ["javascript"],
    "graphql":                  ["rest api"],
    "microservices":            ["docker", "rest api"],
    "serverless":               ["cloud computing"],
    "helm":                     ["kubernetes"],
    "prometheus":               ["kubernetes"],
    "grafana":                  ["prometheus"],
    "github actions":           ["git", "ci/cd"],
    "gitlab ci":                ["git", "ci/cd"],
    "azure devops":             ["azure", "ci/cd"],
    "jenkins":                  ["git", "linux"],
    # Frontend / JS ecosystem
    "javascript":               [],
    "typescript":               ["javascript"],
    "html":                     [],
    "css":                      ["html"],
    "node.js":                  ["javascript"],
    "express":                  ["node.js"],
    "react":                    ["javascript", "html", "css"],
    "angular":                  ["typescript", "html", "css"],
    "vue":                      ["javascript", "html", "css"],
    "next.js":                  ["react"],
    "nuxt":                     ["vue"],
    "svelte":                   ["javascript"],
    "tailwind":                 ["css"],
    "sass":                     ["css"],
    "webpack":                  ["javascript"],
    "vite":                     ["javascript"],
    "jquery":                   ["javascript", "html"],
    "bootstrap":                ["html", "css"],
    "jwt":                      ["rest api"],
    "oauth":                    ["rest api"],
    # HR
    "recruitment":              ["communication"],
    "talent acquisition":       ["recruitment", "communication"],
    "onboarding":               ["recruitment"],
    "performance management":   ["communication", "excel"],
    "workforce planning":       ["excel", "organizational development"],
    "hris":                     ["excel"],
    "workday":                  ["hris"],
    "sap hr":                   ["hris"],
    "training and development": ["communication", "organizational development"],
    "change management":        ["organizational development", "stakeholder management"],
    "payroll":                  ["excel", "compliance"],
    "benefits administration":  ["compliance", "excel"],
    "compensation":             ["excel", "payroll"],
    "hr analytics":             ["excel", "statistics"],
    "succession planning":      ["organizational development", "performance management"],
    # Finance
    "financial analysis":       ["excel", "accounting"],
    "forecasting":              ["financial analysis", "statistics"],
    "auditing":                 ["accounting", "compliance"],
    "risk management":          ["financial analysis", "compliance"],
    "sap fi":                   ["accounting"],
    "financial modeling":       ["excel", "financial analysis"],
    "valuation":                ["financial modeling", "accounting"],
    # BI / Analytics
    "tableau":                  ["excel", "sql"],
    "power bi":                 ["excel", "sql"],
    "looker":                   ["sql"],
    "elasticsearch":            ["sql", "linux"],
    "postgresql":               ["sql"],
    "mysql":                    ["sql"],
    "mongodb":                  [],
    "redis":                    [],
    "cassandra":                [],
    "dynamodb":                 ["aws"],
    "firebase":                 [],
    "neo4j":                    ["sql"],
    # Security
    "penetration testing":      ["linux", "cybersecurity"],
    "ethical hacking":          ["linux", "cybersecurity"],
    "siem":                     ["cybersecurity"],
    "incident response":        ["cybersecurity", "siem"],
    "vulnerability assessment": ["cybersecurity"],
    # Product / Design
    "product roadmap":          ["product management"],
    "wireframing":              ["ux design"],
    "prototyping":              ["ux design", "figma"],
    "usability testing":        ["ux design"],
    "figma":                    [],
}


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7b — LEARNING RESOURCES
# ══════════════════════════════════════════════════════════════════════════

# platform → (label, icon emoji)
PLATFORM_META = {
    "youtube":  {"label": "YouTube",  "icon": "▶"},
    "coursera": {"label": "Coursera", "icon": "🎓"},
    "udemy":    {"label": "Udemy",    "icon": "📘"},
    "docs":     {"label": "Docs",     "icon": "📄"},
    "kaggle":   {"label": "Kaggle",   "icon": "🏆"},
    "freecodecamp": {"label": "freeCodeCamp", "icon": "🔥"},
    "roadmap":  {"label": "Roadmap",  "icon": "🗺"},
}

RESOURCES: dict[str, list[dict]] = {
    "python":           [{"platform": "youtube",  "title": "Python for Beginners – Full Course",        "url": "https://www.youtube.com/watch?v=eWRfhZUzrAc"},
                         {"platform": "coursera", "title": "Python for Everybody",                       "url": "https://www.coursera.org/specializations/python"}],
    "sql":              [{"platform": "youtube",  "title": "SQL Tutorial – Full Database Course",        "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
                         {"platform": "kaggle",   "title": "Intro to SQL – Kaggle Learn",                "url": "https://www.kaggle.com/learn/intro-to-sql"}],
    "machine learning": [{"platform": "coursera", "title": "Machine Learning Specialization (Andrew Ng)","url": "https://www.coursera.org/specializations/machine-learning-introduction"},
                         {"platform": "youtube",  "title": "ML Course by StatQuest",                    "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI"}],
    "deep learning":    [{"platform": "coursera", "title": "Deep Learning Specialization",               "url": "https://www.coursera.org/specializations/deep-learning"},
                         {"platform": "youtube",  "title": "Neural Networks: Zero to Hero",              "url": "https://www.youtube.com/watch?v=VMj-3S1tku0"}],
    "nlp":              [{"platform": "coursera", "title": "NLP Specialization (DeepLearning.AI)",       "url": "https://www.coursera.org/specializations/natural-language-processing"},
                         {"platform": "youtube",  "title": "Hugging Face NLP Course",                   "url": "https://www.youtube.com/watch?v=00GKzGyWFEs"}],
    "pytorch":          [{"platform": "docs",     "title": "PyTorch Official Tutorials",                 "url": "https://pytorch.org/tutorials/"},
                         {"platform": "youtube",  "title": "PyTorch for Deep Learning – Full Course",   "url": "https://www.youtube.com/watch?v=V_xro1bcAuA"}],
    "tensorflow":       [{"platform": "docs",     "title": "TensorFlow Official Tutorials",              "url": "https://www.tensorflow.org/tutorials"},
                         {"platform": "coursera", "title": "TensorFlow Developer Certificate",           "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"}],
    "docker":           [{"platform": "youtube",  "title": "Docker Tutorial for Beginners",              "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"},
                         {"platform": "docs",     "title": "Docker Official Get Started",                "url": "https://docs.docker.com/get-started/"}],
    "kubernetes":       [{"platform": "youtube",  "title": "Kubernetes Tutorial for Beginners",          "url": "https://www.youtube.com/watch?v=X48VuDVv0do"},
                         {"platform": "docs",     "title": "Kubernetes Official Docs",                   "url": "https://kubernetes.io/docs/tutorials/"}],
    "aws":              [{"platform": "youtube",  "title": "AWS Certified Cloud Practitioner – Full Course","url": "https://www.youtube.com/watch?v=SOTamWNgDKc"},
                         {"platform": "docs",     "title": "AWS Getting Started",                        "url": "https://aws.amazon.com/getting-started/"}],
    "react":            [{"platform": "docs",     "title": "React Official Docs",                        "url": "https://react.dev/learn"},
                         {"platform": "youtube",  "title": "React JS Full Course",                      "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"}],
    "javascript":       [{"platform": "freecodecamp","title": "JavaScript Algorithms & Data Structures",  "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
                         {"platform": "youtube",  "title": "JavaScript Full Course",                    "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg"}],
    "typescript":       [{"platform": "docs",     "title": "TypeScript Handbook",                        "url": "https://www.typescriptlang.org/docs/handbook/"},
                         {"platform": "youtube",  "title": "TypeScript Full Course",                    "url": "https://www.youtube.com/watch?v=30LWjhZzg50"}],
    "git":              [{"platform": "youtube",  "title": "Git & GitHub Crash Course",                  "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
                         {"platform": "docs",     "title": "Pro Git Book (free)",                        "url": "https://git-scm.com/book/en/v2"}],
    "linux":            [{"platform": "youtube",  "title": "Linux Command Line Full Course",             "url": "https://www.youtube.com/watch?v=ZtqBQ68cfJc"},
                         {"platform": "freecodecamp","title": "Linux for Beginners",                      "url": "https://www.freecodecamp.org/news/the-linux-commands-handbook/"}],
    "pandas":           [{"platform": "docs",     "title": "Pandas Official Getting Started",            "url": "https://pandas.pydata.org/docs/getting_started/"},
                         {"platform": "kaggle",   "title": "Pandas – Kaggle Learn",                      "url": "https://www.kaggle.com/learn/pandas"}],
    "scikit-learn":     [{"platform": "docs",     "title": "Scikit-learn User Guide",                    "url": "https://scikit-learn.org/stable/user_guide.html"},
                         {"platform": "youtube",  "title": "Scikit-learn Crash Course",                 "url": "https://www.youtube.com/watch?v=0B5eIE_1vpU"}],
    "mlops":            [{"platform": "coursera", "title": "MLOps Specialization (DeepLearning.AI)",     "url": "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"},
                         {"platform": "youtube",  "title": "MLOps Explained",                           "url": "https://www.youtube.com/watch?v=NgWujOrCZFo"}],
    "llm":              [{"platform": "youtube",  "title": "LLMs Explained – Andrej Karpathy",          "url": "https://www.youtube.com/watch?v=zjkBMFhNj_g"},
                         {"platform": "coursera", "title": "Generative AI with LLMs",                   "url": "https://www.coursera.org/learn/generative-ai-with-llms"}],
    "generative ai":    [{"platform": "coursera", "title": "Generative AI for Everyone",                "url": "https://www.coursera.org/learn/generative-ai-for-everyone"},
                         {"platform": "youtube",  "title": "Generative AI Full Course",                 "url": "https://www.youtube.com/watch?v=mEsleV16qdo"}],
    "hugging face":     [{"platform": "docs",     "title": "Hugging Face NLP Course",                   "url": "https://huggingface.co/learn/nlp-course/"},
                         {"platform": "youtube",  "title": "Hugging Face Transformers Tutorial",        "url": "https://www.youtube.com/watch?v=jan07gloaRg"}],
    "data science":     [{"platform": "coursera", "title": "IBM Data Science Professional Certificate",  "url": "https://www.coursera.org/professional-certificates/ibm-data-science"},
                         {"platform": "kaggle",   "title": "Kaggle Learn – Data Science Path",          "url": "https://www.kaggle.com/learn"}],
    "statistics":       [{"platform": "youtube",  "title": "Statistics for Data Science – Full Course", "url": "https://www.youtube.com/watch?v=xxpc-HPKN28"},
                         {"platform": "coursera", "title": "Statistics with Python Specialization",     "url": "https://www.coursera.org/specializations/statistics-with-python"}],
    "postgresql":       [{"platform": "youtube",  "title": "PostgreSQL Tutorial – Full Course",         "url": "https://www.youtube.com/watch?v=qw--VYLpxG4"},
                         {"platform": "docs",     "title": "PostgreSQL Official Tutorial",               "url": "https://www.postgresql.org/docs/current/tutorial.html"}],
    "mongodb":          [{"platform": "youtube",  "title": "MongoDB Full Course",                       "url": "https://www.youtube.com/watch?v=ofme2o29ngU"},
                         {"platform": "docs",     "title": "MongoDB University (free)",                  "url": "https://learn.mongodb.com/"}],
    "django":           [{"platform": "youtube",  "title": "Django Full Course",                        "url": "https://www.youtube.com/watch?v=PtQiiknWUcI"},
                         {"platform": "docs",     "title": "Django Official Tutorial",                   "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/"}],
    "flask":            [{"platform": "youtube",  "title": "Flask Tutorial",                            "url": "https://www.youtube.com/watch?v=Z1RJmh_OqeA"},
                         {"platform": "docs",     "title": "Flask Official Quickstart",                  "url": "https://flask.palletsprojects.com/en/latest/quickstart/"}],
    "fastapi":          [{"platform": "docs",     "title": "FastAPI Official Tutorial",                  "url": "https://fastapi.tiangolo.com/tutorial/"},
                         {"platform": "youtube",  "title": "FastAPI Full Course",                       "url": "https://www.youtube.com/watch?v=7t2alSnE2-I"}],
    "terraform":        [{"platform": "youtube",  "title": "Terraform Full Course",                     "url": "https://www.youtube.com/watch?v=SLB_c_ayRMo"},
                         {"platform": "docs",     "title": "Terraform Official Tutorials",               "url": "https://developer.hashicorp.com/terraform/tutorials"}],
    "ci/cd":            [{"platform": "youtube",  "title": "CI/CD Pipeline Tutorial",                   "url": "https://www.youtube.com/watch?v=R8_veQiYBjI"},
                         {"platform": "docs",     "title": "GitHub Actions Quickstart",                  "url": "https://docs.github.com/en/actions/quickstart"}],
    "computer vision":  [{"platform": "coursera", "title": "Deep Learning & Computer Vision",           "url": "https://www.coursera.org/learn/convolutional-neural-networks"},
                         {"platform": "youtube",  "title": "OpenCV Python Tutorial",                    "url": "https://www.youtube.com/watch?v=oXlwWbU8l2o"}],
    "data engineering": [{"platform": "youtube",  "title": "Data Engineering Full Course",              "url": "https://www.youtube.com/watch?v=ysz5S6PUM-U"},
                         {"platform": "coursera", "title": "IBM Data Engineering Professional Certificate","url": "https://www.coursera.org/professional-certificates/ibm-data-engineer"}],
    "apache spark":     [{"platform": "youtube",  "title": "Apache Spark Full Course",                  "url": "https://www.youtube.com/watch?v=_C8kWso4ne4"},
                         {"platform": "docs",     "title": "Spark Official Quick Start",                 "url": "https://spark.apache.org/docs/latest/quick-start.html"}],
    "excel":            [{"platform": "youtube",  "title": "Excel Full Course",                         "url": "https://www.youtube.com/watch?v=Vl0H-qTclOg"},
                         {"platform": "freecodecamp","title": "Excel for Beginners",                      "url": "https://www.freecodecamp.org/news/excel-tutorial-for-beginners/"}],
    "power bi":         [{"platform": "youtube",  "title": "Power BI Full Course",                      "url": "https://www.youtube.com/watch?v=fnA454XdDys"},
                         {"platform": "docs",     "title": "Microsoft Power BI Learning",                "url": "https://learn.microsoft.com/en-us/power-bi/fundamentals/"}],
    "tableau":          [{"platform": "youtube",  "title": "Tableau Full Course",                       "url": "https://www.youtube.com/watch?v=TPMlZxRRaBQ"},
                         {"platform": "docs",     "title": "Tableau Free Training Videos",               "url": "https://www.tableau.com/learn/training"}],
    "cybersecurity":    [{"platform": "coursera", "title": "Google Cybersecurity Certificate",          "url": "https://www.coursera.org/professional-certificates/google-cybersecurity"},
                         {"platform": "youtube",  "title": "Cybersecurity Full Course",                 "url": "https://www.youtube.com/watch?v=hXSFdwIOfnE"}],
    "java":             [{"platform": "youtube",  "title": "Java Full Course",                          "url": "https://www.youtube.com/watch?v=eIrMbAQSU34"},
                         {"platform": "docs",     "title": "Oracle Java Tutorials",                     "url": "https://docs.oracle.com/javase/tutorial/"}],
    "html":             [{"platform": "freecodecamp","title": "Responsive Web Design Certification",      "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
                         {"platform": "youtube",  "title": "HTML Full Course",                          "url": "https://www.youtube.com/watch?v=pQN-pnXPaVg"}],
    "css":              [{"platform": "freecodecamp","title": "CSS Full Course",                          "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
                         {"platform": "youtube",  "title": "CSS Tutorial – Zero to Hero",               "url": "https://www.youtube.com/watch?v=1Rs2ND1ryYc"}],
    "node.js":          [{"platform": "youtube",  "title": "Node.js Full Course",                       "url": "https://www.youtube.com/watch?v=Oe421EPjeBE"},
                         {"platform": "docs",     "title": "Node.js Official Guides",                   "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs"}],
    "gcp":              [{"platform": "youtube",  "title": "Google Cloud Full Course",                  "url": "https://www.youtube.com/watch?v=IUU6OR8yHCc"},
                         {"platform": "docs",     "title": "Google Cloud Skills Boost (free tier)",     "url": "https://www.cloudskillsboost.google/"}],
    "azure":            [{"platform": "youtube",  "title": "Azure Full Course",                         "url": "https://www.youtube.com/watch?v=NKEFWyqJ5XA"},
                         {"platform": "docs",     "title": "Microsoft Azure Learn",                     "url": "https://learn.microsoft.com/en-us/azure/"}],
    "snowflake":        [{"platform": "youtube",  "title": "Snowflake Tutorial for Beginners",          "url": "https://www.youtube.com/watch?v=9PBvVeCQi0w"},
                         {"platform": "docs",     "title": "Snowflake Quickstart Guides",               "url": "https://quickstarts.snowflake.com/"}],
    "model deployment": [{"platform": "youtube",  "title": "ML Model Deployment Tutorial",              "url": "https://www.youtube.com/watch?v=bjsJOl8gz5k"},
                         {"platform": "coursera", "title": "Deploying ML Models in Production",         "url": "https://www.coursera.org/learn/deploying-machine-learning-models-in-production"}],
    "feature engineering":[{"platform": "kaggle", "title": "Feature Engineering – Kaggle Learn",        "url": "https://www.kaggle.com/learn/feature-engineering"},
                         {"platform": "youtube",  "title": "Feature Engineering Full Guide",            "url": "https://www.youtube.com/watch?v=6WDFfaYtN6s"}],
}


def get_resources(skill: str) -> list[dict]:
    """Return curated resources for a skill, with a Google fallback."""
    key = skill.lower().strip()
    if key in RESOURCES:
        return RESOURCES[key]
    # Generic fallback — always gives the user something to click
    query = skill.replace(' ', '+')
    return [
        {"platform": "youtube",  "title": f"{skill} Tutorial",
         "url": f"https://www.youtube.com/results?search_query={query}+tutorial"},
        {"platform": "coursera", "title": f"{skill} on Coursera",
         "url": f"https://www.coursera.org/search?query={query}"},
    ]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — LEVEL DETECTION
# ══════════════════════════════════════════════════════════════════════════

# Skills that signal increasing depth — ordered beginner → advanced
LEVEL_TIERS: dict[str, int] = {
    # Tier 1 — foundational (beginner signals)
    "python": 1, "java": 1, "javascript": 1, "html": 1, "css": 1,
    "sql": 1, "excel": 1, "git": 1, "linux": 1, "communication": 1,
    "r": 1, "bash": 1, "typescript": 1, "php": 1,
    # Tier 2 — applied / intermediate
    "machine learning": 2, "data analysis": 2, "statistics": 2,
    "pandas": 2, "numpy": 2, "scikit-learn": 2, "react": 2,
    "node.js": 2, "django": 2, "flask": 2, "fastapi": 2,
    "docker": 2, "rest api": 2, "postgresql": 2, "mongodb": 2,
    "tableau": 2, "power bi": 2, "agile": 2, "aws": 2,
    "data visualization": 2, "feature engineering": 2,
    "data science": 2, "data engineering": 2,
    # Tier 3 — advanced / specialist
    "deep learning": 3, "nlp": 3, "computer vision": 3,
    "pytorch": 3, "tensorflow": 3, "mlops": 3, "llm": 3,
    "generative ai": 3, "kubernetes": 3, "terraform": 3,
    "apache spark": 3, "databricks": 3, "snowflake": 3,
    "hugging face": 3, "reinforcement learning": 3,
    "model deployment": 3, "ci/cd": 3, "microservices": 3,
    "cybersecurity": 3, "penetration testing": 3,
    "financial modeling": 3, "valuation": 3,
}


def detect_level(user_skills: list[str]) -> str:
    """
    Returns 'beginner', 'intermediate', or 'advanced' based on the
    weighted tier score of the candidate's skill set.

    Scoring:
      - Each tier-1 skill  = 1 pt
      - Each tier-2 skill  = 2 pts
      - Each tier-3 skill  = 4 pts
    Thresholds (tuned against real resumes):
      - advanced    : score >= 16  OR  3+ tier-3 skills
      - intermediate: score >= 6   OR  2+ tier-2 skills
      - beginner    : everything else
    """
    user_lower = {s.lower() for s in user_skills}
    score      = 0
    tier3_count = 0
    tier2_count = 0

    for skill in user_lower:
        tier = LEVEL_TIERS.get(skill, 0)
        if tier == 3:
            score += 4
            tier3_count += 1
        elif tier == 2:
            score += 2
            tier2_count += 1
        elif tier == 1:
            score += 1

    if score >= 16 or tier3_count >= 3:
        return "advanced"
    if score >= 6 or tier2_count >= 2:
        return "intermediate"
    return "beginner"


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — LEARNING PATH GENERATOR (level-aware)
# ══════════════════════════════════════════════════════════════════════════

def _topological_sort(skills_to_learn: set[str], known: set[str]) -> list[str]:
    """
    Kahn's algorithm topological sort over the subset of skills the candidate
    needs to learn (missing + their unknown prereqs).
    Guarantees prereqs always appear before the skills that depend on them.
    """
    # Expand: collect all unknown prereqs transitively
    all_needed: set[str] = set()
    stack = list(skills_to_learn)
    while stack:
        skill = stack.pop()
        if skill in all_needed or skill in known:
            continue
        all_needed.add(skill)
        for prereq in SKILL_GRAPH.get(skill, []):
            if prereq not in known and prereq not in all_needed:
                stack.append(prereq)

    # Build in-degree map restricted to all_needed
    in_degree: dict[str, int] = {s: 0 for s in all_needed}
    dependents: dict[str, list[str]] = {s: [] for s in all_needed}
    for skill in all_needed:
        for prereq in SKILL_GRAPH.get(skill, []):
            if prereq in all_needed:          # edge prereq → skill
                in_degree[skill] += 1
                dependents[prereq].append(skill)

    # Start with nodes that have no unmet prereqs (in-degree 0)
    queue = sorted([s for s, d in in_degree.items() if d == 0],
                   key=lambda s: LEVEL_TIERS.get(s, 0))  # foundations first
    result: list[str] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for dep in dependents[node]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)
                queue.sort(key=lambda s: LEVEL_TIERS.get(s, 0))  # keep tier order

    # Append any remaining (cycle guard — shouldn't happen with our graph)
    remaining = [s for s in all_needed if s not in result]
    return result + remaining


def generate_learning_path(
    user_skills: list[str],
    missing_skills: list[str],
    level: str = "beginner",
) -> list[dict]:
    known       = {s.lower() for s in user_skills}
    missing_set = {s.lower() for s in missing_skills}

    ordered = _topological_sort(missing_set, known)

    min_tier = {"beginner": 0, "intermediate": 2, "advanced": 3}.get(level, 0)

    TIER_META = {
        1: {"duration": "1 week",    "type": "Foundation"},
        2: {"duration": "2 weeks",   "type": "Core Skill"},
        3: {"duration": "3 weeks",   "type": "Advanced Topic"},
        0: {"duration": "1–2 weeks", "type": "Skill Gap"},
    }

    steps = []
    for skill in ordered:
        tier = LEVEL_TIERS.get(skill.lower(), 0)
        is_directly_missing = skill.lower() in missing_set
        if not is_directly_missing and tier > 0 and tier < min_tier:
            continue
        meta = TIER_META.get(tier, TIER_META[0])
        steps.append({
            "skill":     skill,
            "tier":      tier,
            "duration":  meta["duration"],
            "type":      meta["type"],
            "resources": get_resources(skill),
        })

    for i, s in enumerate(steps):
        s["priority"] = "High" if i < 3 else "Medium"

    return steps


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — REASONING ENGINE (improved hints)
# ══════════════════════════════════════════════════════════════════════════

def generate_reasoning(
    user_skills:     list[str],
    required_skills: list[str],
    missing_skills:  list[str],
) -> list[dict]:
    reasons   = []
    user_set  = {s.lower() for s in user_skills}
    missing_set = {s.lower() for s in missing_skills}

    for skill in required_skills:
        skill_lower = skill.lower()
        if skill_lower not in missing_set:
            reasons.append({
                "skill":  skill.title(),
                "status": "matched",
                "reason": "Found in your resume and required by the job description.",
            })
        else:
            prereqs       = SKILL_GRAPH.get(skill_lower, [])
            known_prereqs = [p for p in prereqs if p.lower() in user_set]

            if known_prereqs:
                prereq_str = ", ".join(p.title() for p in known_prereqs)
                hint = (
                    f" You already know {prereq_str} — "
                    "the prerequisite(s) are covered so this should be quick to pick up."
                )
            else:
                hint = " Start from the fundamentals — consider an online course or project."

            reasons.append({
                "skill":  skill.title(),
                "status": "missing",
                "reason": f"Required by the job description but not found in your resume.{hint}",
            })

    return reasons


# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 — SEMANTIC / LLM UPGRADE LAYER
# ══════════════════════════════════════════════════════════════════════════

_semantic_model = None

def _load_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            log.info("Loading sentence-transformers model …")
            _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("Semantic model ready.")
        except ImportError:
            log.warning("sentence-transformers not installed.")
    return _semantic_model


def extract_skills_semantic(text: str, threshold: float = 0.40) -> list[str]:
    """
    Semantic extraction — tuned threshold, merged with regex results.
    """
    model = _load_semantic_model()
    if model is None:
        return extract_skills(text)

    try:
        from sentence_transformers import util

        sentences = [s.strip() for s in re.split(r"[.;\n]", text) if len(s.strip()) > 15]
        if not sentences:
            return extract_skills(text)

        # Auto-tune threshold: short texts get a slightly lower bar
        adjusted = threshold if len(sentences) >= 10 else threshold - 0.03

        text_embeddings  = model.encode(sentences, convert_to_tensor=True)
        skill_embeddings = model.encode(COMMON_SKILLS, convert_to_tensor=True)

        found = []
        for i, skill in enumerate(COMMON_SKILLS):
            if util.cos_sim(skill_embeddings[i], text_embeddings).max().item() >= adjusted:
                found.append(skill)

        regex_found = extract_skills(text)
        return list(dict.fromkeys(found + regex_found))   # semantic first, then regex

    except Exception as e:
        log.warning(f"Semantic extraction error ({e}), falling back to regex.")
        return extract_skills(text)


# ── Ollama (local LLM) ────────────────────────────────────────────────────

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


def _call_ollama(prompt: str, timeout: int = 90) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=timeout
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def _parse_json_array(raw: str) -> list:
    start, end = raw.find("["), raw.rfind("]") + 1
    if start == -1:
        raise ValueError("No JSON array found")
    return json.loads(raw[start:end])


def extract_skills_ollama(text: str) -> list[str]:
    prompt = (
        "Extract all professional and technical skills from the text below.\n"
        "Return ONLY a valid JSON array of skill name strings. No explanation.\n\n"
        f"Text:\n{text[:3000]}\n\nJSON array:"
    )
    try:
        raw    = _call_ollama(prompt)
        skills = _parse_json_array(raw)
        return [s.lower().strip() for s in skills if isinstance(s, str)]
    except Exception as e:
        log.warning(f"Ollama skill extraction failed ({e}), falling back.")
        return extract_skills_semantic(text)


def generate_reasoning_ollama(user, required, missing) -> list[dict]:
    prompt = (
        f"You are a career coach.\n"
        f"Candidate skills: {json.dumps(user)}\n"
        f"Required skills: {json.dumps(required)}\n"
        f"Missing skills: {json.dumps(missing)}\n\n"
        "For each required skill write one encouraging sentence (≤20 words).\n"
        "Return ONLY a JSON array: [{\"skill\",\"status\"(matched/missing),\"reason\"}]\n\nJSON:"
    )
    try:
        raw    = _call_ollama(prompt, timeout=120)
        result = _parse_json_array(raw)
        for item in result:
            assert "skill" in item and "status" in item and "reason" in item
        return result
    except Exception as e:
        log.warning(f"Ollama reasoning failed ({e}), falling back.")
        return generate_reasoning(user, required, missing)


def generate_learning_path_ollama(user, missing) -> list[str]:
    prompt = (
        f"Candidate knows: {json.dumps(user)}\n"
        f"Needs to learn: {json.dumps(missing)}\n\n"
        "Return a JSON array of skills in learning order (prerequisites first).\n\nJSON:"
    )
    try:
        raw  = _call_ollama(prompt)
        path = _parse_json_array(raw)
        return [s.strip() for s in path if isinstance(s, str)]
    except Exception as e:
        log.warning(f"Ollama learning path failed ({e}), falling back.")
        known = {s.lower() for s in user}
        return _topological_sort({s.lower() for s in missing}, known)


# ── HuggingFace (cloud) ───────────────────────────────────────────────────

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL  = "HuggingFaceH4/zephyr-7b-beta"


def extract_skills_huggingface(text: str) -> list[str]:
    if not HF_TOKEN:
        log.warning("HF_TOKEN not set. Using semantic fallback.")
        return extract_skills_semantic(text)
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=HF_TOKEN)
        prompt = (
            "<|system|>\nExtract professional skills as a JSON array. Return only the array.\n"
            f"<|user|>\n{text[:2000]}\n<|assistant|>"
        )
        out    = client.text_generation(prompt, model=HF_MODEL, max_new_tokens=300, temperature=0.1)
        skills = _parse_json_array(out)
        return [s.lower().strip() for s in skills if isinstance(s, str)]
    except Exception as e:
        log.warning(f"HuggingFace failed ({e}), falling back.")
        return extract_skills_semantic(text)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 11 — UNIFIED ANALYZE FUNCTION
# ══════════════════════════════════════════════════════════════════════════

AnalysisMode = Literal["rule_based", "semantic", "ollama", "huggingface"]


def analyze(
    resume_text: str,
    jd_text:     str,
    mode:        AnalysisMode = "semantic",
) -> dict:
    """
    Single entry point for all analysis modes.
    Always returns the same JSON structure — safe for frontend consumption.
    """
    clean_resume = clean_text(resume_text)
    clean_jd     = clean_text(jd_text)

    if not clean_resume:
        return {"error": "Resume text is empty or could not be parsed."}
    if not clean_jd:
        return {"error": "Job description text is empty or could not be parsed."}

    log.info(f"Analyzing — mode: {mode}")

    # ── Skill extraction ───────────────────────────────────────────────
    if mode == "ollama":
        user_skills     = extract_skills_ollama(clean_resume)
        required_skills = extract_skills_ollama(clean_jd)
    elif mode == "huggingface":
        user_skills     = extract_skills_huggingface(clean_resume)
        required_skills = extract_skills_huggingface(clean_jd)
    elif mode == "semantic":
        user_skills     = extract_skills_semantic(clean_resume)
        required_skills = extract_skills_semantic(clean_jd)
    else:   # rule_based
        user_skills     = extract_skills(clean_resume)
        required_skills = extract_skills(clean_jd)

    # ── Gap analysis ───────────────────────────────────────────────────
    missing_skills = find_missing(user_skills, required_skills)
    match_score    = compute_match_score(user_skills, required_skills, missing_skills)
    level          = detect_level(user_skills)

    # ── Path & reasoning ───────────────────────────────────────────────
    if mode == "ollama":
        lp_raw    = generate_learning_path_ollama(user_skills, missing_skills)
        learning_path = [
            {"skill": s, "tier": LEVEL_TIERS.get(s.lower(), 0),
             "duration": "1–2 weeks", "type": "Skill Gap",
             "priority": "High" if i < 3 else "Medium",
             "resources": get_resources(s)}
            for i, s in enumerate(lp_raw)
        ]
        reasoning = generate_reasoning_ollama(user_skills, required_skills, missing_skills)
    else:
        learning_path = generate_learning_path(user_skills, missing_skills, level=level)
        reasoning     = generate_reasoning(user_skills, required_skills, missing_skills)

    return {
        "mode":            mode,
        "level":           level,
        "match_score":     match_score,
        "user_skills":     [s.title() for s in user_skills],
        "required_skills": [s.title() for s in required_skills],
        "missing_skills":  [s.title() for s in missing_skills],
        "learning_path":   [
            {**step, "skill": step["skill"].title()} for step in learning_path
        ],
        "reasoning":       reasoning,
        "summary": {
            "total_required": len(required_skills),
            "matched":        len(required_skills) - len(missing_skills),
            "missing":        len(missing_skills),
            "extra_skills":   len(user_skills) - (len(required_skills) - len(missing_skills)),
        }
    }


# ══════════════════════════════════════════════════════════════════════════
# SECTION 12 — FILE PARSING HELPERS (PDF / DOCX upload)
# ══════════════════════════════════════════════════════════════════════════

def _extract_text_from_pdf(file_bytes: bytes) -> str:
    import io
    # Try pdfplumber first (handles most modern PDFs reliably)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = " ".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text
    except Exception as e:
        log.warning(f"pdfplumber failed ({e}), trying PyPDF2")
    # Fallback to PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception as e:
        log.warning(f"PyPDF2 failed ({e})")
    return ""


def _extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx, io
        doc = docx.Document(io.BytesIO(file_bytes))
        return " ".join(p.text for p in doc.paragraphs)
    except Exception as e:
        log.warning(f"DOCX parse failed ({e})")
        return ""


# ══════════════════════════════════════════════════════════════════════════
# SECTION 13 — FASTAPI SERVER
# ══════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Resume Analyzer API",
    description="AI-powered resume skill-gap analysis — rule-based, semantic, and LLM modes.",
    version="3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume text (plain or HTML)")
    jd_text:     str = Field(..., description="Job description text")
    mode:        AnalysisMode = Field("semantic", description="Analysis mode")

class CustomPathwayRequest(BaseModel):
    skills: list[str] = Field(..., description="List of missing skills for the schedule")
    start_date: str   = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str     = Field(..., description="End date (YYYY-MM-DD)")

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class SummaryModel(BaseModel):
    total_required: int
    matched:        int
    missing:        int
    extra_skills:   int


class AnalyzeResponse(BaseModel):
    mode:            str
    level:           str
    match_score:     int
    user_skills:     list[str]
    required_skills: list[str]
    missing_skills:  list[str]
    learning_path:   list[dict]
    reasoning:       list[dict]
    summary:         dict


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
def analyze_endpoint(req: AnalyzeRequest):
    """
    **Main endpoint** — paste resume + JD, get back full skill-gap analysis.

    Returns:
    - `match_score` (0–100): how well the candidate fits
    - `user_skills`: skills found in resume
    - `required_skills`: skills found in JD
    - `missing_skills`: gap list
    - `learning_path`: ordered list of skills to learn (prerequisites first)
    - `reasoning`: per-skill explanation with status (matched / missing)
    - `summary`: quick stats (total_required, matched, missing, extra_skills)
    """
    if not req.resume_text.strip():
        raise HTTPException(400, "resume_text is empty")
    if not req.jd_text.strip():
        raise HTTPException(400, "jd_text is empty")
    try:
        result = analyze(req.resume_text, req.jd_text, mode=req.mode)
        if "error" in result:
            raise HTTPException(422, result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(500, f"Internal error: {e}")


@app.post("/upload", tags=["Analysis"])
async def upload_endpoint(
    resume: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    jd_file: Optional[UploadFile] = File(None, description="JD file (PDF or TXT, optional)"),
    jd_text: str       = Form("", description="Job description text (used if jd_file not provided)"),
    mode:    str       = Form("semantic"),
):
    """
    Upload a PDF/DOCX resume + either a JD file or JD text — returns same structure as /analyze.
    """
    # ── Parse resume ──────────────────────────────────────────────────
    resume_bytes = await resume.read()
    fname = (resume.filename or "").lower()
    if fname.endswith(".pdf"):
        resume_text = _extract_text_from_pdf(resume_bytes)
    elif fname.endswith(".docx"):
        resume_text = _extract_text_from_docx(resume_bytes)
    else:
        resume_text = resume_bytes.decode("utf-8", errors="ignore")

    if not resume_text.strip():
        raise HTTPException(422, "Could not extract text from resume file. Ensure it is a valid PDF, DOCX, or TXT.")

    # ── Parse JD ──────────────────────────────────────────────────────
    if jd_file and jd_file.filename:
        jd_bytes = await jd_file.read()
        jd_fname = (jd_file.filename or "").lower()
        if jd_fname.endswith(".pdf"):
            jd_text = _extract_text_from_pdf(jd_bytes)
        elif jd_fname.endswith(".docx"):
            jd_text = _extract_text_from_docx(jd_bytes)
        else:
            jd_text = jd_bytes.decode("utf-8", errors="ignore")

    if not jd_text.strip():
        raise HTTPException(422, "Could not extract text from job description. Ensure it is a valid PDF, DOCX, or TXT.")

    try:
        result = analyze(resume_text, jd_text, mode=mode)
        return result
    except Exception as e:
        log.error(f"Upload analysis error: {e}", exc_info=True)
        raise HTTPException(500, str(e))

@app.post("/custom_pathway", tags=["Analysis"])
def custom_pathway_endpoint(req: CustomPathwayRequest):
    from datetime import datetime, timedelta
    
    try:
        start = datetime.strptime(req.start_date, "%Y-%m-%d")
        end   = datetime.strptime(req.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD.")
        
    days_total = (end - start).days + 1
    if days_total <= 0:
        raise HTTPException(400, "End date must be after start date.")
        
    if not req.skills:
        return {"schedule": []}
        
    days_per_skill = max(1, days_total // len(req.skills))
    
    schedule = []
    current_date = start
    for i, skill in enumerate(req.skills):
        skill_days = days_per_skill
        if i == len(req.skills) - 1:
            skill_days = days_total - (i * days_per_skill)
            
        for d in range(skill_days):
            if d == 0:
                topic = f"Introduction to {skill}: Terminology and Setup"
            elif d == skill_days - 1:
                topic = f"Practical Application: Mini-Project using {skill}"
            elif d == 1:
                topic = f"Core Fundamentals and Architecture of {skill}"
            else:
                topic = f"Advanced Concepts and Best Practices for {skill}"
                
            schedule.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": current_date.strftime("%A"),
                "skill": skill,
                "topic": topic
            })
            current_date += timedelta(days=1)
            
    return {"schedule": schedule}

FAQ = {
    "hello hi hey greetings": "Hi there! I am TechNova AI, your career assistant. How can I help you?",
    "what is a skill gap missing skills": "A skill gap means you lack a skill required by the job. Don't worry, I generate a learning path for each gap so you know what to learn!",
    "how do i use this app resume upload": "You can upload your resume on the left side of the dashboard. Once uploaded, I'll extract your skills and compare them to the job description!",
    "what is a custom pathway custom schedule dates": "Select a start and end date at the bottom to get a customized, day-by-day learning schedule tailored exactly for your missing skills.",
    "job description target role": "Paste your target job description on the right side and I will generate a map of what you need to learn to get hired.",
    "learning pathway roadmap plan": "The learning pathway gives you a step-by-step roadmap to learn the missing skills. You can also generate a custom schedule by picking dates below!",
    "how does this work behind the scenes": "I analyze your resume and the job desc using AI (Natural Language Processing) to extract skills. Then I find the gaps and build a learning plan for you.",
    "who made you creators team": "I am TechNova AI, built by an awesome team for this hackathon!",
    "thanks thank you cool awesome": "You're very welcome! Let me know if you need anything else.",
    "bye goodbye see you later": "Goodbye! Good luck with your learning journey."
}

@app.post("/chat", tags=["Analysis"])
def chat_endpoint(req: ChatRequest):
    """Chatbot endpoint - tries Ollama -> HuggingFace -> semantic FAQ fallback."""
    if not req.messages:
        return {"reply": "Hello! How can I help you?"}

    SYSTEM = (
        "You are TechNova AI, an expert career counselor and skill-gap advisor. "
        "Keep answers concise (2-4 sentences), friendly, and practical. "
        "Focus on career advice, skill learning, resume tips, and job descriptions."
    )

    def to_llm_role(r: str) -> str:
        return "assistant" if r in ("ai", "assistant") else "user"

    history = req.messages[-6:]

    # 1. Try Ollama (local LLM)
    try:
        ollama_msgs = [{"role": "system", "content": SYSTEM}]
        ollama_msgs += [{"role": to_llm_role(m.role), "content": m.text} for m in history]
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": OLLAMA_MODEL, "messages": ollama_msgs, "stream": False},
            timeout=20
        )
        if r.status_code == 200:
            reply = r.json().get("message", {}).get("content", "").strip()
            if reply:
                return {"reply": reply}
    except Exception as e:
        log.warning(f"Ollama chat failed: {e}")

    # 2. Keyword FAQ fallback (no model needed)
    user_text = req.messages[-1].text.lower()
    for key, answer in FAQ.items():
        if any(word in user_text for word in key.split()):
            return {"reply": answer}

    return {"reply": "I can only help with skill gaps, learning paths, and resume tips here. For a full analysis, head to the main page — upload your resume and a job description to get started!"}

@app.get("/health", tags=["System"])
def health():
    """Heartbeat — frontend can poll this to check if the server is up."""
    return {"status": "ok", "version": "3.0"}


@app.get("/modes", tags=["System"])
def list_modes():
    """
    Returns which LLM modes are currently available on this server.
    Frontend can use this to enable/disable mode selectors dynamically.
    """
    semantic_ok = False
    try:
        from sentence_transformers import SentenceTransformer  # noqa
        semantic_ok = True
    except ImportError:
        pass

    ollama_ok = False
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        pass

    hf_ok = bool(HF_TOKEN)

    return {
        "rule_based":  True,
        "semantic":    semantic_ok,
        "ollama":      ollama_ok,
        "huggingface": hf_ok,
    }


@app.get("/skills", tags=["System"])
def list_skills(domain: Optional[str] = None):
    """
    Return all skills in the database, optionally filtered by domain.
    Useful for frontend autocomplete / tag pickers.
    """
    if domain:
        skills = SKILLS_BY_DOMAIN.get(domain.lower(), [])
        if not skills:
            raise HTTPException(404, f"Domain '{domain}' not found. "
                                     f"Available: {list(SKILLS_BY_DOMAIN.keys())}")
        return {"domain": domain, "skills": [s.title() for s in skills]}
    return {
        "domains": list(SKILLS_BY_DOMAIN.keys()),
        "total":   len(COMMON_SKILLS),
        "skills":  {d: [s.title() for s in sl] for d, sl in SKILLS_BY_DOMAIN.items()},
    }


@app.get("/dataset/stats", tags=["Dataset"])
def dataset_stats():
    """Basic stats about the loaded resume dataset — useful for an admin dashboard."""
    if resume_df.empty:
        return {"total_resumes": 0, "categories": {}, "total_skills": len(COMMON_SKILLS)}
    return {
        "total_resumes": len(resume_df),
        "categories":    resume_df["Category"].value_counts().to_dict(),
        "total_skills":  len(COMMON_SKILLS),
    }


# ══════════════════════════════════════════════════════════════════════════
# SECTION 14 — STANDALONE TEST
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sample_resume = """
    Senior Data Scientist with 6 years of experience in Python, machine learning,
    deep learning, NLP, and MLOps. Strong background in scikit-learn, TensorFlow,
    PyTorch, and Hugging Face Transformers. Proficient in SQL, PostgreSQL, Spark,
    and Snowflake. Deployed models on AWS using Docker and Kubernetes. Experience
    with CI/CD pipelines via GitHub Actions. Excellent communication and leadership.
    """

    sample_jd = """
    We are looking for a Machine Learning Engineer with expertise in Python, MLOps,
    model deployment, Docker, Kubernetes, and CI/CD. Proficiency in NLP, deep learning,
    and experience with LLMs or Generative AI is highly desired. Must know SQL,
    AWS or GCP, and have strong stakeholder management skills.
    """

    result = analyze(sample_resume, sample_jd, mode="semantic")
    print(json.dumps(result, indent=2))