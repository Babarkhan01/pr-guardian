import os, re, requests
from dotenv import load_dotenv

load_dotenv()
MAX_DIFF_CHARS = 40_000


def fetch_pr(url: str) -> dict:
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url.strip())
    if not m:
        raise ValueError("Use a URL like https://github.com/owner/repo/pull/123")
    owner, repo, num = m.groups()
    base = f"https://api.github.com/repos/{owner}/{repo}/pulls/{num}"
    auth = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}

    r = requests.get(base, headers={**auth, "Accept": "application/vnd.github+json"}, timeout=30)
    r.raise_for_status()
    meta = r.json()

    d = requests.get(base, headers={**auth, "Accept": "application/vnd.github.v3.diff"}, timeout=30)
    d.raise_for_status()
    diff = d.text

    return {
        "owner": owner, "repo": repo, "number": int(num),
        "title": meta["title"], "body": meta.get("body") or "",
        "clone_url": meta["head"]["repo"]["clone_url"],
        "head_sha": meta["head"]["sha"], "head_ref": meta["head"]["ref"],
        "changed_files": meta["changed_files"],
        "diff": diff[:MAX_DIFF_CHARS],
        "diff_truncated": len(diff) > MAX_DIFF_CHARS,
    }
