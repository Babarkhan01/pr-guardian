import re

PATTERNS = {
    "hardcoded_secret": (r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[=:]\s*['\"][A-Za-z0-9_\-/+=]{12,}['\"]", "critical"),
    "sk_style_key": (r"\bsk[-_](live|test)?[-_]?[A-Za-z0-9]{16,}", "critical"),
    "aws_key": (r"\bAKIA[0-9A-Z]{16}\b", "critical"),
    "private_key": (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "critical"),
    "eval_exec": (r"\b(eval|exec)\s*\(", "high"),
    "unsafe_pickle": (r"\bpickle\.loads?\(", "high"),
    "shell_true": (r"shell\s*=\s*True", "high"),
    "sql_fstring": (r"(?i)(execute|query)\s*\(\s*f['\"].*(select|insert|update|delete)", "critical"),
    "sql_concat": (r"(?i)(select|insert|update|delete)\b.*['\"]\s*\+\s*\w+", "high"),
}

def mask(text: str) -> str:
    for pat, _ in PATTERNS.values():
        text = re.sub(pat, "[REDACTED]", text)
    return text

def scan_diff(diff: str) -> dict:
    findings, files, cur = [], [], None
    dep_changes, test_files, src_files = [], [], []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
            files.append(cur)
            low = cur.lower()
            if "test" in low:
                test_files.append(cur)
            elif low.endswith(".py"):
                src_files.append(cur)
            continue
        if line.startswith("+") and not line.startswith("+++"):
            body = line[1:]
            if cur and "requirements" in cur.lower():
                dep_changes.append(f"{cur}: {body.strip()}")
            for name, (pat, sev) in PATTERNS.items():
                if re.search(pat, body):
                    findings.append({"rule": name, "severity": sev, "file": cur,
                                     "evidence": mask(body.strip())[:120]})
    return {"findings": findings, "dependency_changes": dep_changes,
            "changed_files": files,
            "source_changed_without_tests": bool(src_files) and not test_files,
            "has_critical": any(f["severity"] == "critical" for f in findings)}
