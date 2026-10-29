import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from backend.agent.orchestrator import review

app = FastAPI(title="PR Guardian")
HERE = os.path.dirname(__file__)

class Req(BaseModel):
    pr_url: str

@app.get("/", response_class=HTMLResponse)
def home():
    return open(os.path.join(HERE, "static", "index.html")).read()

@app.post("/api/review")
def api_review(req: Req):
    try:
        return review(req.pr_url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Review failed: {e}")
