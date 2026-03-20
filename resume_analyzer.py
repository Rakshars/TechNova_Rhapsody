"""
Resume Analyzer — Full Backend
================================
Original rule-based engine (Steps 1-10) is fully preserved.
LLM layer sits on top and upgrades skill extraction + reasoning.
FastAPI exposes everything as clean REST endpoints for the frontend.

Install:
    pip install pandas beautifulsoup4 lxml kagglehub
    pip install sentence-transformers                  # Tier 1 (semantic)
    pip install requests                               # Tier 2 (Ollama local)
    pip install huggingface_hub                        # Tier 3 (HF cloud)
    pip install fastapi uvicorn python-multipart       # API server

Run:
    python resume_analyzer.py          # test mode (prints sample result)
    uvicorn resume_analyzer:app --reload --port 8000   # API server mode
"""

import os
import re
import json
import logging
import requests
import pandas as pd
from collections import Counter
from bs4 import BeautifulSoup

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — DATASET LOADING
# ══════════════════════════════════════════════════════════════════════════

import kagglehub

path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
csv_path = os.path.join(path, "Resume", "Resume.csv")
resume_df = pd.read_csv(csv_path)

log.info(f"Dataset loaded — {resume_df.shape[0]} resumes, columns: {resume_df.columns.tolist()}")
log.info(f"Categories: {resume_df['Category'].unique().tolist()}")


# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — TEXT CLEANING
# ══════════════════════════════════════════════════════════════════════════

def clean_text(raw: str) -> str:
    """Strip HTML tags and collapse whitespace to plain text."""
    if not isinstance(raw, str):
        return ""
    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


resume_df["clean_resume"] = resume_df["Resume_str"].apply(clean_text)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — SKILL DATABASE (mined from dataset + curated)
# ══════════════════════════════════════════════════════════════════════════

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "have", "has",
    "been", "will", "was", "are", "were", "not", "but", "all", "any",
    "can", "work", "also", "use", "used", "using", "more", "other",
    "include", "including", "experience", "skills", "ability", "strong",
    "knowledge", "team", "years", "year", "month", "months", "good",
    "well", "within", "across", "our", "your", "their", "such", "both",
    "each", "into", "over", "than", "then", "they", "what", "when",
    "where", "which", "while", "who", "its", "out", "new", "may",
    "must", "per", "etc", "via", "key", "able", "many", "high",
    "level", "related", "basis", "help", "make", "need", "role", "time"
}


def mine_frequent_terms(series: pd.Series, top_n: int = 300) -> list:
    """Return the top-N most frequent meaningful words across all resumes."""
    counter = Counter()
    for text in series.dropna():
        tokens = re.findall(r"[a-zA-Z][a-zA-Z+#.]{2,}", text.lower())
        filtered = [t for t in tokens if t not in STOPWORDS]
        counter.update(filtered)
    return [word for word, _ in counter.most_common(top_n)]


mined_terms = mine_frequent_terms(resume_df["clean_resume"])
log.info(f"Top 30 mined terms: {mined_terms[:30]}")

# Curated skill list — derived from mined_terms + domain expertise
SKILLS_BY_DOMAIN = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "r",
        "scala", "golang", "ruby", "swift", "kotlin", "php", "bash", "matlab"
    ],
    "data_and_ml": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "data analysis", "data science", "data engineering", "statistics",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
        "keras", "xgboost", "opencv", "feature engineering",
        "model deployment", "mlops"
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "oracle", "elasticsearch", "sqlite", "nosql", "firebase"
    ],
    "cloud_and_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "jenkins", "ci/cd", "git", "linux", "ansible", "cloud computing"
    ],
    "web_and_api": [
        "react", "angular", "vue", "node.js", "django", "flask",
        "fastapi", "rest api", "graphql", "html", "css", "spring boot"
    ],
    "hr_and_business": [
        "recruitment", "talent acquisition", "onboarding", "payroll",
        "performance management", "employee relations", "hris", "workday",
        "sap hr", "successfactors", "compensation", "benefits administration",
        "labour law", "compliance", "training and development",
        "organizational development", "change management", "workforce planning"
    ],
    "soft_and_tools": [
        "communication", "leadership", "project management", "agile",
        "scrum", "jira", "excel", "powerpoint", "tableau", "power bi",
        "stakeholder management", "problem solving", "critical thinking"
    ],
    "finance_and_accounting": [
        "financial analysis", "accounting", "auditing", "budgeting",
        "forecasting", "tally", "sap fi", "quickbooks", "taxation",
        "risk management"
    ]
}

COMMON_SKILLS = [
    skill
    for domain_skills in SKILLS_BY_DOMAIN.values()
    for skill in domain_skills
]

log.info(f"Total skills in database: {len(COMMON_SKILLS)}")


# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — RULE-BASED SKILL EXTRACTION (original)
# ══════════════════════════════════════════════════════════════════════════

SYNONYMS = {
    "ml":                          "machine learning",
    "dl":                          "deep learning",
    "ai":                          "machine learning",
    "natural language processing": "nlp",
    "nodejs":                      "node.js",
    "node js":                     "node.js",
    "reactjs":                     "react",
    "react js":                    "react",
    "vuejs":                       "vue",
    "postgres":                    "postgresql",
    "scikit learn":                "scikit-learn",
    "sklearn":                     "scikit-learn",
    "power-bi":                    "power bi",
    "ms excel":                    "excel",
    "microsoft excel":             "excel",
    "ms powerpoint":               "powerpoint",
    "talent management":           "talent acquisition",
    "hiring":                      "recruitment",
    "sourcing":                    "talent acquisition",
}


def normalise(text: str) -> str:
    text = text.lower().strip()
    return SYNONYMS.get(text, text)


def extract_skills(text: str) -> list:
    """
    Rule-based: match text against COMMON_SKILLS using regex.
    Multi-word skills checked first to prevent partial matches.
    Used as fallback when LLM is unavailable.
    """
    normalised = normalise(text)
    sorted_skills = sorted(COMMON_SKILLS, key=lambda s: len(s.split()), reverse=True)

    found = []
    for skill in sorted_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, normalised, re.IGNORECASE):
            found.append(skill)

    return list(dict.fromkeys(found))


# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — SKILL GAP ANALYSIS (original)
# ══════════════════════════════════════════════════════════════════════════

def find_missing(user_skills: list, required_skills: list) -> list:
    """Return skills required by the JD that the candidate doesn't have."""
    user_set = {s.lower() for s in user_skills}
    return [skill for skill in required_skills if skill.lower() not in user_set]


# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — SKILL DEPENDENCY GRAPH (original)
# ══════════════════════════════════════════════════════════════════════════

SKILL_GRAPH = {
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
    # Frontend
    "react":                    ["javascript", "html", "css"],
    "angular":                  ["typescript", "html", "css"],
    "vue":                      ["javascript", "html", "css"],
    "typescript":               ["javascript"],
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
    # Finance
    "financial analysis":       ["excel", "accounting"],
    "forecasting":              ["financial analysis", "statistics"],
    "auditing":                 ["accounting", "compliance"],
    "risk management":          ["financial analysis", "compliance"],
    "sap fi":                   ["accounting"],
    # BI / Analytics
    "tableau":                  ["excel", "sql"],
    "power bi":                 ["excel", "sql"],
    "elasticsearch":            ["sql", "linux"],
    "postgresql":               ["sql"],
    "mongodb":                  ["sql"],
}


# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — ADAPTIVE LEARNING PATH (original)
# ══════════════════════════════════════════════════════════════════════════

def _collect_prereqs(skill: str, known: set, path: list, visited: set) -> None:
    """Depth-first post-order: prerequisites come before the skill itself."""
    if skill in visited:
        return
    visited.add(skill)
    for prereq in SKILL_GRAPH.get(skill, []):
        if prereq.lower() not in known:
            _collect_prereqs(prereq, known, path, visited)
    if skill.lower() not in known and skill not in path:
        path.append(skill)


def generate_learning_path(user_skills: list, missing_skills: list) -> list:
    """
    Ordered learning path — prerequisites injected automatically,
    already-known skills skipped.
    """
    known = {s.lower() for s in user_skills}
    learning_path = []
    visited = set()
    for skill in missing_skills:
        _collect_prereqs(skill, known, learning_path, visited)
    return learning_path


# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — RULE-BASED REASONING ENGINE (original)
# ══════════════════════════════════════════════════════════════════════════

def generate_reasoning(user_skills: list, required_skills: list, missing_skills: list) -> list:
    """
    One explanation per required skill.
    Missing skills get a prereq hint if the candidate already knows related skills.
    """
    reasons = []
    user_set = {s.lower() for s in user_skills}

    for skill in required_skills:
        if skill.lower() in user_set:
            reasons.append({
                "skill": skill.title(),
                "status": "matched",
                "reason": "Found in resume and required by the job description."
            })
        else:
            prereqs = SKILL_GRAPH.get(skill.lower(), [])
            known_prereqs = [p for p in prereqs if p.lower() in user_set]
            hint = (
                f" You already know {', '.join(known_prereqs)} — "
                "prerequisite(s) covered, should be quick to learn."
                if known_prereqs else ""
            )
            reasons.append({
                "skill": skill.title(),
                "status": "missing",
                "reason": f"Required in job description but not found in resume.{hint}"
            })

    return reasons


# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — LLM UPGRADE LAYER
# Each function here is a drop-in upgrade for the corresponding rule-based one.
# They all fall back to rule-based if the LLM call fails.
# ══════════════════════════════════════════════════════════════════════════

# ── Tier 1: Sentence Transformers (runs fully offline, no API key needed) ──

_semantic_model = None  # loaded lazily on first use

def _load_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            log.info("Loading sentence-transformers model (first run may take ~30s)...")
            _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("Semantic model ready.")
        except ImportError:
            log.warning("sentence-transformers not installed. Run: pip install sentence-transformers")
    return _semantic_model


def extract_skills_semantic(text: str, threshold: float = 0.42) -> list:
    """
    Upgrade over regex: uses cosine similarity between sentence embeddings
    and skill embeddings. Catches synonyms, paraphrases, and context clues
    that regex misses entirely.

    Falls back to rule-based extract_skills() if model unavailable.
    """
    model = _load_semantic_model()
    if model is None:
        log.warning("Falling back to rule-based skill extraction.")
        return extract_skills(text)

    try:
        from sentence_transformers import util

        # Split into sentences for finer-grained matching
        sentences = [s.strip() for s in re.split(r"[.;\n]", text) if len(s.strip()) > 10]
        if not sentences:
            return extract_skills(text)

        text_embeddings  = model.encode(sentences, convert_to_tensor=True)
        skill_embeddings = model.encode(COMMON_SKILLS, convert_to_tensor=True)

        found = []
        for i, skill in enumerate(COMMON_SKILLS):
            scores = util.cos_sim(skill_embeddings[i], text_embeddings)
            if scores.max().item() >= threshold:
                found.append(skill)

        # Merge with regex results — semantic can miss exact keyword matches
        regex_found = extract_skills(text)
        merged = list(dict.fromkeys(found + regex_found))
        return merged

    except Exception as e:
        log.warning(f"Semantic extraction failed ({e}), falling back to regex.")
        return extract_skills(text)


# ── Tier 2: Ollama (local LLM — llama3 / mistral, no internet needed) ─────

OLLAMA_URL    = "http://localhost:11434/api/generate"
OLLAMA_MODEL  = "llama3"   # change to "mistral" or "gemma2" if preferred


def _call_ollama(prompt: str, timeout: int = 60) -> str:
    """Raw call to local Ollama server. Returns response text."""
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=timeout
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


def extract_skills_ollama(text: str) -> list:
    """
    Ask local LLM to extract skills. Much smarter than regex —
    understands context, infers implicit skills, handles typos.
    Falls back to semantic → regex on failure.
    """
    prompt = f"""Extract all professional and technical skills from the text below.
Return ONLY a valid JSON array of skill name strings. No explanation, no markdown.
Example output: ["Python", "SQL", "Recruitment", "Excel"]

Text:
{text[:3000]}

JSON array:"""

    try:
        raw = _call_ollama(prompt)
        # Find the JSON array in the response
        start, end = raw.find("["), raw.rfind("]") + 1
        if start == -1:
            raise ValueError("No JSON array in response")
        skills = json.loads(raw[start:end])
        return [s.lower().strip() for s in skills if isinstance(s, str)]
    except Exception as e:
        log.warning(f"Ollama skill extraction failed ({e}), falling back to semantic.")
        return extract_skills_semantic(text)


def generate_reasoning_ollama(
    user_skills: list,
    required_skills: list,
    missing_skills: list
) -> list:
    """
    Ask local LLM to write personalised, intelligent gap explanations.
    Much richer than the rule-based hints.
    Falls back to rule-based reasoning on failure.
    """
    prompt = f"""You are a professional career coach reviewing a candidate's skill gap.

Candidate's skills: {json.dumps(user_skills)}
Required skills for the job: {json.dumps(required_skills)}
Missing skills: {json.dumps(missing_skills)}

For each required skill, write a short one-sentence explanation (max 20 words).
Be specific, encouraging, and practical.

Return ONLY a valid JSON array of objects. No markdown, no explanation.
Each object must have exactly these keys: "skill", "status", "reason"
"status" must be either "matched" or "missing"

Example:
[
  {{"skill": "Python", "status": "matched", "reason": "Solid foundation that directly meets the job requirement."}},
  {{"skill": "Docker", "status": "missing", "reason": "You know Linux already, so Docker should take about a week to learn."}}
]

JSON array:"""

    try:
        raw = _call_ollama(prompt, timeout=90)
        start, end = raw.find("["), raw.rfind("]") + 1
        if start == -1:
            raise ValueError("No JSON array in response")
        result = json.loads(raw[start:end])
        # Validate structure before returning
        for item in result:
            assert "skill" in item and "status" in item and "reason" in item
        return result
    except Exception as e:
        log.warning(f"Ollama reasoning failed ({e}), falling back to rule-based.")
        return generate_reasoning(user_skills, required_skills, missing_skills)


def generate_learning_path_ollama(user_skills: list, missing_skills: list) -> list:
    """
    Ask local LLM to build a smarter, personalised learning path.
    Considers the candidate's existing background when ordering steps.
    Falls back to graph-based path on failure.
    """
    prompt = f"""You are a learning path designer for professionals.

Candidate already knows: {json.dumps(user_skills)}
Skills the candidate needs to learn: {json.dumps(missing_skills)}

Create an ordered learning path from basic to advanced.
- Start with prerequisites the candidate is missing
- Consider what they already know
- Keep it practical and ordered

Return ONLY a valid JSON array of skill name strings in learning order.
No explanation, no markdown.

JSON array:"""

    try:
        raw = _call_ollama(prompt, timeout=60)
        start, end = raw.find("["), raw.rfind("]") + 1
        if start == -1:
            raise ValueError("No JSON array in response")
        path = json.loads(raw[start:end])
        return [s.strip() for s in path if isinstance(s, str)]
    except Exception as e:
        log.warning(f"Ollama learning path failed ({e}), falling back to graph-based.")
        return generate_learning_path(user_skills, missing_skills)


# ── Tier 3: HuggingFace Inference API (cloud-hosted, no GPU needed) ────────

HF_TOKEN = os.environ.get("HF_TOKEN", "")   # set via: export HF_TOKEN=hf_xxx
HF_MODEL  = "HuggingFaceH4/zephyr-7b-beta"  # or "mistralai/Mixtral-8x7B-Instruct-v0.1"


def extract_skills_huggingface(text: str) -> list:
    """
    Use HuggingFace Inference API for skill extraction.
    Requires HF_TOKEN env variable. Falls back to semantic on failure.
    """
    if not HF_TOKEN:
        log.warning("HF_TOKEN not set. Falling back to semantic extraction.")
        return extract_skills_semantic(text)

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=HF_TOKEN)

        prompt = f"""<|system|>
You are a resume parser. Extract all professional skills as a JSON array. Return only the array, nothing else.
<|user|>
{text[:2000]}
<|assistant|>"""

        output = client.text_generation(
            prompt,
            model=HF_MODEL,
            max_new_tokens=300,
            temperature=0.1
        )
        start, end = output.find("["), output.rfind("]") + 1
        if start == -1:
            raise ValueError("No JSON array in response")
        skills = json.loads(output[start:end])
        return [s.lower().strip() for s in skills if isinstance(s, str)]

    except Exception as e:
        log.warning(f"HuggingFace extraction failed ({e}), falling back to semantic.")
        return extract_skills_semantic(text)


# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 — SMART ANALYZE FUNCTIONS
# Two versions: original (fast, no dependencies) and LLM-upgraded (smarter)
# ══════════════════════════════════════════════════════════════════════════

def analyze(resume_text: str, jd_text: str) -> dict:
    """
    Original rule-based pipeline.
    Fast, no external dependencies, always works.
    """
    clean_resume = clean_text(resume_text)
    clean_jd     = clean_text(jd_text)

    user_skills     = extract_skills(clean_resume)
    required_skills = extract_skills(clean_jd)
    missing_skills  = find_missing(user_skills, required_skills)
    learning_path   = generate_learning_path(user_skills, missing_skills)
    reasoning       = generate_reasoning(user_skills, required_skills, missing_skills)

    return {
        "mode":            "rule_based",
        "user_skills":     [s.title() for s in user_skills],
        "required_skills": [s.title() for s in required_skills],
        "missing_skills":  [s.title() for s in missing_skills],
        "learning_path":   [s.title() for s in learning_path],
        "reasoning":       reasoning,
    }


def analyze_with_llm(
    resume_text: str,
    jd_text: str,
    mode: str = "semantic"
) -> dict:
    """
    LLM-upgraded pipeline. Same structure as analyze() but smarter.

    mode options:
        "semantic"      — sentence-transformers (offline, recommended default)
        "ollama"        — local LLM via Ollama (best quality, needs Ollama running)
        "huggingface"   — HuggingFace Inference API (cloud, needs HF_TOKEN)

    All modes fall back to the rule-based engine if something fails,
    so this function will always return a valid result.
    """
    clean_resume = clean_text(resume_text)
    clean_jd     = clean_text(jd_text)

    log.info(f"Running analyze_with_llm in mode: {mode}")

    # ── Skill extraction (upgraded) ────────────────────────────────────
    if mode == "ollama":
        user_skills     = extract_skills_ollama(clean_resume)
        required_skills = extract_skills_ollama(clean_jd)
    elif mode == "huggingface":
        user_skills     = extract_skills_huggingface(clean_resume)
        required_skills = extract_skills_huggingface(clean_jd)
    else:  # default: semantic
        user_skills     = extract_skills_semantic(clean_resume)
        required_skills = extract_skills_semantic(clean_jd)

    # ── Gap analysis (same logic, inputs are smarter now) ──────────────
    missing_skills = find_missing(user_skills, required_skills)

    # ── Learning path + reasoning (upgraded for Ollama) ────────────────
    if mode == "ollama":
        learning_path = generate_learning_path_ollama(user_skills, missing_skills)
        reasoning     = generate_reasoning_ollama(user_skills, required_skills, missing_skills)
    else:
        # For semantic/HF: skill extraction is smarter, reasoning stays rule-based
        # (rule-based reasoning works well when skills are correctly identified)
        learning_path = generate_learning_path(user_skills, missing_skills)
        reasoning     = generate_reasoning(user_skills, required_skills, missing_skills)

    return {
        "mode":            mode,
        "user_skills":     [s.title() for s in user_skills],
        "required_skills": [s.title() for s in required_skills],
        "missing_skills":  [s.title() for s in missing_skills],
        "learning_path":   [s.title() for s in learning_path],
        "reasoning":       reasoning,
    }


# ══════════════════════════════════════════════════════════════════════════
# SECTION 11 — FASTAPI SERVER (frontend connects here)
# ══════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(
    title="Resume Analyzer API",
    description="AI-powered resume skill gap analysis. Supports rule-based and LLM modes.",
    version="2.0"
)

# Allow all origins during dev — tighten this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Raw resume text (HTML or plain)")
    jd_text:     str = Field(..., description="Job description text")
    mode:        Literal["rule_based", "semantic", "ollama", "huggingface"] = Field(
        default="semantic",
        description=(
            "rule_based  — fast regex, no dependencies\n"
            "semantic    — sentence-transformers offline (recommended)\n"
            "ollama      — local LLM via Ollama (best quality)\n"
            "huggingface — cloud LLM via HuggingFace API"
        )
    )


class ReasoningItem(BaseModel):
    skill:  str
    status: str
    reason: str


class AnalyzeResponse(BaseModel):
    mode:            str
    user_skills:     list
    required_skills: list
    missing_skills:  list
    learning_path:   list
    reasoning:       list


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(req: AnalyzeRequest):
    """
    Main endpoint. Frontend sends resume + JD, gets back skill analysis.

    Example request body:
    {
        "resume_text": "...",
        "jd_text": "...",
        "mode": "semantic"
    }
    """
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text is empty")
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="jd_text is empty")

    try:
        if req.mode == "rule_based":
            result = analyze(req.resume_text, req.jd_text)
        else:
            result = analyze_with_llm(req.resume_text, req.jd_text, mode=req.mode)
        return result
    except Exception as e:
        log.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Quick health check — useful for frontend to verify server is up."""
    return {"status": "ok", "version": "2.0"}


@app.get("/modes")
def list_modes():
    """
    Tell the frontend which LLM modes are available on this server.
    Frontend can use this to show/hide mode options dynamically.
    """
    semantic_available = True
    try:
        from sentence_transformers import SentenceTransformer  # noqa
    except ImportError:
        semantic_available = False

    ollama_available = False
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        ollama_available = r.status_code == 200
    except Exception:
        pass

    hf_available = bool(HF_TOKEN)

    return {
        "rule_based":   True,
        "semantic":     semantic_available,
        "ollama":       ollama_available,
        "huggingface":  hf_available,
    }


@app.get("/dataset/stats")
def dataset_stats():
    """Return basic stats about the loaded dataset — useful for dashboard."""
    return {
        "total_resumes": len(resume_df),
        "categories":    resume_df["Category"].value_counts().to_dict(),
        "total_skills":  len(COMMON_SKILLS),
    }


# ══════════════════════════════════════════════════════════════════════════
# SECTION 12 — TEST (run directly: python resume_analyzer.py)
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    hr_rows = resume_df[resume_df["Category"] == "HR"]
    sample_resume_raw = (
        hr_rows["Resume_str"].iloc[0]
        if not hr_rows.empty
        else resume_df["Resume_str"].iloc[0]
    )

    sample_jd = """
    We are looking for an HR Business Partner with strong experience in
    talent acquisition, onboarding, performance management, and HRIS systems
    such as Workday. The ideal candidate should have excellent communication
    skills, knowledge of labour law, payroll, and compensation. Experience
    with training and development and change management is a plus.
    Proficiency in Excel and PowerPoint required.
    """

    print("\n" + "="*60)
    print("TEST 1 — Rule-based (original engine)")
    print("="*60)
    result = analyze(sample_resume_raw, sample_jd)
    print(json.dumps(result, indent=2))

    print("\n" + "="*60)
    print("TEST 2 — Semantic (sentence-transformers)")
    print("="*60)
    result_llm = analyze_with_llm(sample_resume_raw, sample_jd, mode="semantic")
    print(json.dumps(result_llm, indent=2))