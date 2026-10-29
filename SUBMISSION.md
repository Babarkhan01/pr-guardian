# Hackathon submission — Nebius x NVIDIA Global AI Hackathon

**Track:** Coding and Agentic Engineering
**Deadline:** October 30, 2026, 10:00 AM PDT

**Demo video:** https://www.youtube.com/watch?v=m6RuuVhl0Qk (public, 2:11, no music)

---

## Tagline

An agentic first-pass PR reviewer where deterministic tools produce the evidence, NVIDIA Nemotron explains it, and the model can never overrule the evidence.

## Description (paste into the Devpost "About the project" field)

Pull requests pile up, and the first-pass checks are repetitive: do the tests pass, did someone commit a secret, did they test the new logic? PR Guardian is an AI agent that does that first pass, so a human reviewer can focus on design and make the final call. It never merges anything.

For a public GitHub PR URL, the agent:

1. Fetches the PR metadata and unified diff from the GitHub API.
2. Scans added lines for hardcoded secrets, SQL injection patterns, `eval`/`exec`, unsafe `pickle`, `shell=True`, and dependency changes.
3. Clones the PR branch and runs the project's pytest suite in a Docker container with memory and CPU limits, a timeout, and the network disabled during the run.
4. Masks secrets, then sends the diff, the test output, and the scanner findings to NVIDIA Nemotron (`nvidia/nemotron-3-super-120b-a12b`) through Nebius Token Factory, which returns a structured JSON review.
5. Validates that report, then applies deterministic guardrails: a critical scanner finding forces `block`, failing tests prevent `approve`, and source changes without test changes prevent `approve`.
6. Returns a decision, a risk score, findings with file and line, missing tests, a suggested patch, and a full timestamped agent trace.

The three demo PRs cover a clean change (approve), new logic with no tests (request changes), and a hardcoded key plus SQL injection (block). All three match the expected verdict, but they are seeded scenarios built to exercise the pipeline, not an accuracy benchmark.

**Where Nebius and NVIDIA fit.** Inference runs entirely on Nebius Token Factory's OpenAI-compatible endpoint with NVIDIA Nemotron-3-Super; Nemotron-3-Nano also works by changing one environment variable. Token Factory removed the need to provision GPUs or host a model server, and JSON mode gave a reliably parseable report. A full review — fetch, scan, Docker tests, model call — finishes in about 13-14 seconds.

**Why the design matters.** It would be easy to let a model approve PRs. PR Guardian deliberately splits the work: tools that can be checked produce the evidence, the model explains and prioritizes it, and either can override the model. Secrets are masked before anything leaves the machine, tests run with no network, and the agent has no write access to the target repository.

**Limitations, stated plainly.** Test execution supports Python projects that use pytest. Dependencies are installed with the network on before the network-off test run, so only review repositories you trust. The scanner is rule-based and will produce false positives and misses. Only the first 40,000 characters of a diff are reviewed.

## Links

- Code: https://github.com/Babarkhan01/pr-guardian
- Interactive replay of the three real runs: https://babarkhan01.github.io/pr-guardian/
- Demo video: https://www.youtube.com/watch?v=m6RuuVhl0Qk

## Built with

Python, FastAPI, Pydantic, Docker, Nebius Token Factory, NVIDIA Nemotron-3-Super-120B-A12B, GitHub REST API.

---

## Feedback on Nebius Token Factory and NVIDIA tools

*For the Devpost feedback field and the "Most Valuable Feedback" award. Edit the two bracketed spots to match what you actually hit during the build.*

> Token Factory was the easiest part of this build. The endpoint is OpenAI-compatible, so the official `openai` SDK worked unchanged — base URL and key, nothing else — and `response_format: json_object` returned valid JSON on every call, which is usually where structured-output agents break. Nemotron-3-Super followed a long, adversarial system prompt (PR text explicitly marked as untrusted data) and still respected the schema, and the Super/Nano split let me use the big model for the reasoning call while keeping the cheap model available for faster iterations.
>
> Two things would have saved time. First, model discovery: finding the exact model IDs available on my account, their context limits, and which ones support JSON mode took [how long / a few tries], and a per-model capability table in the docs would have removed that guesswork. Second, diff-sized inputs: a 40,000-character diff is already near the practical limit for a single useful call, and there is no obvious guidance on chunking a large diff without losing cross-file context — a recommended pattern for map-then-reduce reviews of big PRs would help anyone building a coding agent.
>
> Smaller notes: an explicit statement of rate limits per tier, and streaming support through the OpenAI-compatible path, would both help agents that want to show partial progress instead of a 14-second spinner. Overall, the platform did the boring parts (serving, scaling, auth) well enough that I never thought about them.

---

## YouTube upload

- URL: https://www.youtube.com/watch?v=m6RuuVhl0Qk
- Visibility: **Public** (the rules require publicly visible)
- Category: Science & Technology
- Music: none — no Content ID risk
- Thumbnail suggestion: the BLOCK decision card, or the end card

**Title**

    PR Guardian — an agentic PR reviewer with evidence (Nebius Token Factory + NVIDIA Nemotron)

**Description**

    PR Guardian is an agentic first-pass reviewer for GitHub pull requests: it fetches the diff,
    scans for secrets and injection patterns, runs the repo's tests in a network-off Docker
    sandbox, and asks NVIDIA Nemotron on Nebius Token Factory for an evidence-based review.
    Deterministic guardrails can override the model. It never merges — humans decide.

    Built for the Nebius x NVIDIA Global AI Hackathon, Coding and Agentic Engineering track.

    Code: https://github.com/Babarkhan01/pr-guardian
    Interactive replay of the three real runs: https://babarkhan01.github.io/pr-guardian/

    Chapters
    0:00 The problem
    0:20 How the pipeline works / clean PR
    0:42 New logic with no tests
    1:17 Secret and SQL injection
    1:34 Design, limits, and what this is not

    The footage shows the project's UI replaying saved outputs from real runs. Live reviews run
    the full pipeline locally (Docker plus a Nebius key); setup is in the README.

**Tags**

    AI agent, code review, pull request, NVIDIA Nemotron, Nebius Token Factory, LLM, FastAPI, Docker, hackathon, agentic AI

---

## Devpost checklist

| Field | Status |
|---|---|
| Track | Coding and Agentic Engineering |
| Code repository URL | ready |
| Demo / test-build URL | ready (replay page) |
| Text description | ready above |
| Demo video URL | https://www.youtube.com/watch?v=m6RuuVhl0Qk |
| Feedback on Nebius / NVIDIA tools | drafted above |
| Explanation of pre-hackathon work | not needed — repository created during the submission period |
| Built-with tags | ready above |
