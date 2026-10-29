import json
from typing import Annotated
from pydantic import BaseModel, BeforeValidator


def _s(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, (dict, list)):
        return json.dumps(v)
    return str(v)


def _ls(v):
    if v is None or v is False or v is True:
        return []
    if not isinstance(v, list):
        v = [v]
    return [_s(x) for x in v]


def _dec(v):
    v = _s(v).strip().lower().replace(" ", "_").replace("-", "_")
    return v if v in ("approve", "request_changes", "block") else "request_changes"


def _risk(v):
    try:
        return max(0, min(100, int(float(v))))
    except Exception:
        return 50


def _conf(v):
    try:
        f = float(v)
        if f > 1:
            f = f / 100
        return max(0.0, min(1.0, f))
    except Exception:
        return 0.5


def _find(v):
    if v is None or isinstance(v, bool):
        return []
    if isinstance(v, (str, dict)):
        v = [v]
    out = []
    for x in v:
        if isinstance(x, dict):
            out.append({k: x[k] for k in ("severity", "file", "line", "issue", "why_it_matters", "suggested_fix") if k in x})
        else:
            out.append({"issue": _s(x)})
    return out


S = Annotated[str, BeforeValidator(_s)]


class Finding(BaseModel):
    severity: S = "medium"
    file: S = ""
    line: S = ""
    issue: S = ""
    why_it_matters: S = ""
    suggested_fix: S = ""


class Report(BaseModel):
    decision: Annotated[str, BeforeValidator(_dec)] = "request_changes"
    risk_score: Annotated[int, BeforeValidator(_risk)] = 50
    summary: S = ""
    findings: Annotated[list[Finding], BeforeValidator(_find)] = []
    missing_tests: Annotated[list[str], BeforeValidator(_ls)] = []
    security_issues: Annotated[list[str], BeforeValidator(_ls)] = []
    suggested_patch: S = ""
    confidence: Annotated[float, BeforeValidator(_conf)] = 0.5
