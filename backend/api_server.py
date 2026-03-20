
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Copy Steps 2-9 above into this file, or:
# from resume_engine import analyze   (if you saved notebook as .py)

app = FastAPI(title="Resume Analyzer API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    resume_text: str
    jd_text: str

@app.post("/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    return analyze(req.resume_text, req.jd_text)

@app.get("/health")
def health():
    return {"status": "ok"}
