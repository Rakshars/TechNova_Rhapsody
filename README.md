# TechNova Rhapsody — AI Resume & Skill-Gap Analyzer

We built this to solve a problem most of us have faced — you find a great job posting, look at the requirements, and have no idea where you actually stand. So we made something that tells you exactly that. Upload your resume, paste the job description, and it'll show you what you have, what you're missing, and how to get there.

---

## What it does

- Pulls skills out of your resume (PDF, DOCX, or plain text) and the job description
- Compares them and gives you a match score along with your experience level
- Builds a learning roadmap where prerequisites always come before the skills that depend on them
- Lets you pick a start and end date to get a day-by-day custom learning schedule
- Can compare two resumes against the same JD and tell you who's the better fit
- Has a small chatbot for quick questions about the app
- Shows you the reasoning behind every matched or missing skill — not just a list, but why

---

## Project Structure

```
TechNova_Rhapsody/
├── backend/
│   ├── resume_analyzer.py   # FastAPI app — all the analysis logic lives here
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # all the React UI components
│   │   ├── App.jsx          # root component, holds state and API calls
│   │   └── main.jsx
│   ├── vite.config.js       # proxies /api/* → http://127.0.0.1:8000
│   └── package.json
├── docker-compose.yml
└── start.bat                # one-click start on Windows
```

---

## Dependencies

### Backend — Python 3.10+

| Package | What it's used for |
|---|---|
| `fastapi` + `uvicorn` | the REST API server |
| `python-multipart` | handling file uploads |
| `pdfplumber`, `PyPDF2` | extracting text from PDFs |
| `python-docx` | extracting text from DOCX files |
| `beautifulsoup4`, `lxml` | cleaning up HTML and raw text |
| `sentence-transformers` | semantic skill matching using `all-MiniLM-L6-v2` |
| `torch` (CPU) | needed by sentence-transformers |
| `scikit-learn`, `numpy`, `pandas` | scoring and general data utilities |
| `requests` | making HTTP calls to local AI services |
| `kagglehub` | optional — downloads a resume dataset if available |
| `huggingface-hub` | optional — HF inference client |

### Frontend — Node 18+

| Package | What it's used for |
|---|---|
| `react` + `react-dom` | the UI |
| `vite` | dev server and build tool |
| `framer-motion` | animations throughout the app |

---

## How to run it

### Option 1 — Windows one-click

Just double-click or run:

```bat
start.bat
```

This opens the backend at `http://localhost:8000` and the frontend at `http://localhost:5173` in two separate terminal windows. That's it.

---

### Option 2 — Run manually

**Start the backend first:**

```bash
cd backend
pip install -r requirements.txt
uvicorn resume_analyzer:app --reload --port 8000
```

**Then the frontend in a new terminal:**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser once both are running.

---

### Option 3 — Docker

If you'd rather not deal with Python/Node setup:

```bash
docker-compose up --build
```

- Backend will be at `http://localhost:5000`
- Frontend will be at `http://localhost:5173`

---

## How the skill-gap analysis actually works

### Step 1 — Reading the files

We support PDF, DOCX, and plain text for both resumes and job descriptions. PDFs go through `pdfplumber` first and fall back to `PyPDF2` if needed. Any HTML tags or leftover boilerplate get stripped out with BeautifulSoup before we do anything else.

### Step 2 — Finding the skills

We have a hand-curated database of 160+ skills spread across 7 domains — ML/AI, Software Engineering, Cloud/DevOps, Data Engineering, HR, Finance, and Product. Each skill has a precompiled regex pattern that we run against the cleaned text. We also have a synonym map so things like `"k8s"` correctly maps to `"kubernetes"` and `"cv"` maps to `"computer vision"`. If a shorter skill match overlaps with a longer one, we keep the longer one and drop the shorter — so "machine learning" won't also match "learning" separately.

### Step 3 — Figuring out experience level

Before scoring, we scan the resume for seniority signals. Things like explicit years of experience ("5 years of..."), and words like `senior`, `lead`, `principal`, `junior`, `intern`. Based on this we classify the candidate as beginner, intermediate, or advanced. This matters for the learning path — we don't want to tell a senior engineer to go learn what a variable is.

### Step 4 — Scoring the match

```
match_score = (matched skills / required skills) × 100
```

Simple enough. Skills that appear in both the resume and the JD are matched. Skills in the JD that aren't in the resume are flagged as missing. Every single decision gets a plain-English explanation that shows up in the Reasoning panel on the results page — so you're not just staring at a number.

### Step 5 — Building the learning path

This is the part we're most proud of. Missing skills get sorted using Kahn's topological sort over a directed prerequisite graph we built manually. The graph has edges like `numpy → python`, `pandas → numpy`, `pytorch → machine learning`, `express → node.js`, and about 30 more. The sort guarantees that if you need to learn `pandas`, `python` will always show up first in your roadmap — never after.

For beginners, we include all prerequisites automatically. For intermediate and advanced users, we only include skills that are directly missing — we don't pad the list with things they almost certainly already know.

Each step in the path comes with the skill name, its tier (foundational / intermediate / advanced), an estimated time to learn it, the type of resource, and actual links to learning material.

### Step 6 — Comparing two candidates

The `/compare` endpoint runs the full analysis on both resumes independently against the same JD. It then returns each candidate's match score, strengths, skill gaps, and a winner verdict with a short reason — useful if you're a recruiter trying to decide between two people quickly.

---

## API Endpoints

| Method | Path | What it does |
|---|---|---|
| `POST` | `/analyze` | analyze a single resume against a JD |
| `POST` | `/compare` | compare two resumes against the same JD |
| `POST` | `/chat` | chatbot — keyword FAQ with a friendly fallback |
| `GET` | `/health` | check if the server is up |
| `GET` | `/modes` | see which AI modes are currently active |
| `GET` | `/skills` | list all skills, optionally filter by domain |
