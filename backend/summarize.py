import os, sys, json
from backend.services.nebius_client import client
from backend.tools.github_tools import fetch_pr

SYSTEM = """You are PR Guardian, a senior software engineer reviewing a pull request.
Be conservative and evidence-based. Never claim something is wrong without evidence in the diff.
Return valid JSON only."""

PROMPT = """Analyze this pull request.

TITLE: {title}
DESCRIPTION: {body}

DIFF:
{diff}

Return JSON with keys: purpose, affected_files (list), tests_that_should_exist (list),
risks (list of {{severity, issue, why_it_matters}}), safe_to_merge (true/false), reasoning."""

if __name__ == "__main__":
    pr = fetch_pr(sys.argv[1])
    print(f"Fetched: {pr['title']} ({pr['changed_files']} files, truncated={pr['diff_truncated']})")
    r = client.chat.completions.create(
        model=os.getenv("NEMOTRON_MAIN_MODEL"),
        temperature=0.2,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": PROMPT.format(**pr)}],
        response_format={"type": "json_object"},
    )
    print(json.dumps(json.loads(r.choices[0].message.content), indent=2))
