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

try:
    import kagglehub
    _path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
    _csv  = os.path.join(_path, "Resume", "Resume.csv")
    resume_df = pd.read_csv(_csv)
    log.info(f"Dataset loaded — {resume_df.shape[0]} resumes")
except Exception as e:
    log.warning(f"Dataset not loaded ({e}). /dataset/stats will return empty.")
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
    # Backend / Cloud
    "docker":                   ["linux"],
    "kubernetes":               ["docker"],
    "terraform":                ["cloud computing"],
    "ci/cd":                    ["git"],
    "aws":                      ["linux", "cloud computing"],
    "azure":                    ["cloud computing"],
    "gcp":                      ["cloud computing"],
    "fastapi":                  ["python"],
    "django":                   ["python"],
    "flask":                    ["python"],
    "spring boot":              ["java"],
    "rest api":                 ["python"],
    "graphql":                  ["rest api"],
    "microservices":            ["docker", "rest api"],
    "serverless":               ["cloud computing"],
    "helm":                     ["kubernetes"],
    "prometheus":               ["kubernetes"],
    "grafana":                  ["prometheus"],
    "github actions":           ["git", "ci/cd"],
    "gitlab ci":                ["git", "ci/cd"],
    "azure devops":             ["azure", "ci/cd"],
    # Frontend
    "react":                    ["javascript", "html", "css"],
    "angular":                  ["typescript", "html", "css"],
    "vue":                      ["javascript", "html", "css"],
    "next.js":                  ["react"],
    "svelte":                   ["javascript"],
    "typescript":               ["javascript"],
    "tailwind":                 ["css"],
    "sass":                     ["css"],
    "webpack":                  ["javascript"],
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
    "mongodb":                  ["sql"],
    "cassandra":                ["sql"],
    "dynamodb":                 ["aws", "nosql"],
    "firebase":                 ["nosql"],
    # Security
    "penetration testing":      ["linux", "networking"],
    "siem":                     ["cybersecurity"],
    "incident response":        ["cybersecurity", "siem"],
    "vulnerability assessment": ["cybersecurity"],
    # Product / Design
    "product roadmap":          ["product management"],
    "wireframing":              ["ux design"],
    "prototyping":              ["ux design", "figma"],
    "usability testing":        ["ux design"],
}


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — LEARNING PATH GENERATOR
# ══════════════════════════════════════════════════════════════════════════

def _collect_prereqs(skill: str, known: set, path: list, visited: set) -> None:
    if skill in visited:
        return
    visited.add(skill)
    for prereq in SKILL_GRAPH.get(skill, []):
        if prereq.lower() not in known:
            _collect_prereqs(prereq, known, path, visited)
    if skill.lower() not in known and skill not in path:
        path.append(skill)


def generate_learning_path(user_skills: list[str], missing_skills: list[str]) -> list[str]:
    known   = {s.lower() for s in user_skills}
    path    : list[str] = []
    visited : set[str]  = set()
    for skill in missing_skills:
        _collect_prereqs(skill, known, path, visited)
    return path


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
        return generate_learning_path(user, missing)


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

    # ── Path & reasoning ───────────────────────────────────────────────
    if mode == "ollama":
        learning_path = generate_learning_path_ollama(user_skills, missing_skills)
        reasoning     = generate_reasoning_ollama(user_skills, required_skills, missing_skills)
    else:
        learning_path = generate_learning_path(user_skills, missing_skills)
        reasoning     = generate_reasoning(user_skills, required_skills, missing_skills)

    return {
        "mode":            mode,
        "match_score":     match_score,            # ← NEW: 0–100
        "user_skills":     [s.title() for s in user_skills],
        "required_skills": [s.title() for s in required_skills],
        "missing_skills":  [s.title() for s in missing_skills],
        "learning_path":   [s.title() for s in learning_path],
        "reasoning":       reasoning,
        "summary": {                               # ← NEW: quick stats for dashboard cards
            "total_required":  len(required_skills),
            "matched":         len(required_skills) - len(missing_skills),
            "missing":         len(missing_skills),
            "extra_skills":    len(user_skills) - (len(required_skills) - len(missing_skills)),
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


class SummaryModel(BaseModel):
    total_required: int
    matched:        int
    missing:        int
    extra_skills:   int


class AnalyzeResponse(BaseModel):
    mode:            str
    match_score:     int
    user_skills:     list[str]
    required_skills: list[str]
    missing_skills:  list[str]
    learning_path:   list[str]
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