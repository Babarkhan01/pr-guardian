# PR Guardian

PR Guardian is an agentic first-pass code reviewer for GitHub pull requests. It fetches the PR diff, runs the repository's tests in an isolated Docker sandbox, scans the diff for security risks, and asks NVIDIA Nemotron (served by Nebius Token Factory) to produce an evidence-based review report. It never merges code. A human makes the final decision.

Built for the Nebius x NVIDIA Global AI Hackathon, Coding and Agentic Engineering track.

[![PR Guardian demo video](https://img.youtube.com/vi/m6RuuVhl0Qk/maxresdefault.jpg)](https://www.youtube.com/watch?v=m6RuuVhl0Qk)

[Watch the 2-minute demo](https://www.youtube.com/watch?v=m6RuuVhl0Qk) — the problem, the pipeline, three real reviews, and the design limits. No music; the steps are also captioned on screen, so it works muted.

Replay demo (saved outputs of the three real runs): https://babarkhan01.github.io/pr-guardian/

The replay page is static: it serves the saved JSON reports in `docs/reports/`. To run the full pipeline (GitHub API, Docker sandbox, Token Factory inference) use the local instructions below.

## What it does

1. Fetches PR metadata and the unified diff from the GitHub API.
2. Scans added lines for hardcoded secrets, SQL injection patterns, eval/exec, unsafe pickle, shell=True, and dependency changes.
3. Clones the PR branch and runs pytest in a Docker container (memory and CPU limited, network disabled during the test run).
4. Sends the masked diff, test output and scanner findings to Nemotron through the Nebius Token Factory API.
5. Validates the model's JSON report, then applies deterministic guardrails: a critical scanner finding forces `block`, failing tests prevent `approve`, and source changes without test changes prevent `approve`.
6. Returns a decision (approve, request_changes, block), a risk score, findings, missing tests, and a full agent trace.

## Architecture

    GitHub PR URL
        -> fetch PR + diff (GitHub API)
        -> security scan (regex rules, secret masking)
        -> Docker sandbox (pytest, network off)
        -> Nemotron review (Nebius Token Factory)
        -> guardrails (scanner and test evidence can override the model)
        -> report + agent trace (FastAPI + web UI)

## Tech stack

- Python, FastAPI, Pydantic
- Docker (Colima on macOS) for the test sandbox
- Nebius Token Factory (OpenAI-compatible API)
- NVIDIA Nemotron-3-Super-120B-A12B (Nemotron-3-Nano-30B-A3B also tested)

## How NVIDIA Nemotron and Nebius Token Factory are used

**Model.** `nvidia/nemotron-3-super-120b-a12b` through Token Factory's OpenAI-compatible endpoint (`NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/`). The model is selected with `NEMOTRON_MAIN_MODEL`, so Nano can be swapped in for cheaper runs without code changes.

**What the model receives.** The masked unified diff (first 40,000 characters), the pytest output from the Docker sandbox, the deterministic scanner findings, and the PR title and description. Secrets are redacted before this payload is built, and the PR text is wrapped as untrusted data in the system prompt.

**What it returns.** A single JSON object (`response_format: json_object`, temperature 0.2): decision, risk score, findings with file and line, why each issue matters, a suggested fix, missing tests, security issues, an optional patch, and a confidence value. The schema is validated before anything reaches the UI.

**Where Token Factory accelerated the work.** One key and one OpenAI-compatible endpoint replaced GPU provisioning, model serving, and an inference server. `response_format: json_object` removed the usual prompt-engineering fight for parseable output, and the same SDK call works for both Super and Nano. A full review — fetch, scan, Docker tests, model call — completes in about 13-14 seconds end to end, so the whole loop stayed inside one demo.

**Who decides.** Deterministic tools produce the evidence; the model explains and prioritizes it. A critical scanner finding forces `block` and failing tests block `approve` regardless of what the model says, so the model cannot wave through a secret or a failing suite.

## Run it locally

    git clone https://github.com/Babarkhan01/pr-guardian.git
    cd pr-guardian
    python3.11 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env    # add your Nebius and GitHub keys
    docker info             # Docker (or Colima) must be running
    uvicorn backend.main:app --port 8000

Open http://127.0.0.1:8000 and paste a public GitHub PR URL, or click one of the three demo PRs.

Command line: `python -m backend.agent.orchestrator <PR_URL>` writes a JSON report to `reports/`.

## Demo scenarios

| Repo | Scenario | Expected | Actual | Risk | Confidence | Time |
|---|---|---|---|---|---|---|
| pg-demo-clean | Small change with tests updated | approve | approve (match) | 5 | 0.98 | 9.6s |
| pg-demo-missing-test | New logic, no tests | request_changes | request_changes (match) | 45 | 0.9 | 12.6s |
| pg-demo-security-risk | Hardcoded key and SQL injection | block | block (match) | 85 | 0.95 | 13.4s |

These are three seeded scenarios built to exercise the pipeline. They show that the pipeline works end to end, not a general accuracy rate.

## Safety design

- Never merges or modifies the target repository.
- Tests run in Docker with memory and CPU limits, a timeout, and the network disabled.
- Secrets are masked before any text is sent to the model.
- PR text and code are treated as untrusted data in the system prompt.
- Scanner and test results can override the model's decision.
- Suggested patches require human approval.

## Limitations

- Test execution supports Python projects that use pytest.
- Dependencies are installed with the network enabled before the network-off test run, so only run PR Guardian on repositories you trust.
- The scanner is rule-based and will produce false positives and misses.
- Only the first 40,000 characters of a diff are reviewed.

## Hackathon compliance

- Inference runs on Nebius Token Factory at runtime (`backend/services/nebius_client.py`, `backend/agent/orchestrator.py`).
- Uses NVIDIA Nemotron open models (Nemotron-3-Super, with Nemotron-3-Nano tested).
- Open-source repository with an MIT license.
- Built for the Coding and Agentic Engineering track of the Nebius x NVIDIA Global AI Hackathon.
- This repository was created during the submission period: the agent, the FastAPI UI, the replay page, the three demo repositories, and the demo video were all produced as part of the submission.

## Judge quick path

1. Watch the demo video, or open the replay demo above (no setup, no keys) to see the three saved runs.
2. Or run it locally with your own keys and Docker, then paste any public Python PR URL.
3. Command line for a single review: `python -m backend.agent.orchestrator <PR_URL>`.

## License

MIT
