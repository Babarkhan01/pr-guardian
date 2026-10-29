from pydantic import BaseModel

class Finding(BaseModel):
    severity: str = "medium"
    file: str = ""
    line: str = ""
    issue: str = ""
    why_it_matters: str = ""
    suggested_fix: str = ""

class Report(BaseModel):
    decision: str = "request_changes"
    risk_score: int = 50
    summary: str = ""
    findings: list[Finding] = []
    missing_tests: list[str] = []
    security_issues: list[str] = []
    suggested_patch: str = ""
    confidence: float = 0.5
