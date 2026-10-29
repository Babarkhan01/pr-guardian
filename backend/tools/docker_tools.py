import os, shutil, subprocess, uuid
from backend.tools.security_tools import mask

IMAGE = "python:3.11-slim"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK = os.path.join(ROOT, ".work")  # inside $HOME so Colima can mount it


def _docker(args, timeout):
    return subprocess.run(["docker", "run", "--rm", "--memory", "512m", "--cpus", "1", *args],
                          capture_output=True, text=True, timeout=timeout)


def run_tests_in(repo: str, timeout: int = 120) -> dict:
    mount = ["-v", f"{repo}:/repo", "-w", "/repo"]
    req = "-r requirements.txt" if os.path.exists(os.path.join(repo, "requirements.txt")) else ""
    try:
        # step 1: install dependencies (network ON)
        inst = _docker(mount + [IMAGE, "sh", "-c", f"pip install -q --target /repo/.deps pytest {req}"], 180)
        if inst.returncode != 0:
            return {"status": "install_failed", "exit_code": inst.returncode,
                    "output": mask((inst.stdout + inst.stderr)[-1500:])}
        # step 2: run tests (network OFF)
        r = _docker(["--network", "none", "-e", "PYTHONPATH=/repo/.deps:/repo", *mount, IMAGE,
                     "python", "-m", "pytest", "-q", "--tb=short", "-x", "-p", "no:cacheprovider"], timeout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "exit_code": -1, "output": "Test run timed out"}
    status = {0: "passed", 1: "failed", 5: "no_tests_found"}.get(r.returncode, "error")
    return {"status": status, "exit_code": r.returncode, "output": mask((r.stdout + r.stderr)[-3000:])}


def run_tests(clone_url: str, head_ref: str, timeout: int = 120) -> dict:
    os.makedirs(WORK, exist_ok=True)
    work = os.path.join(WORK, uuid.uuid4().hex[:8])
    try:
        c = subprocess.run(["git", "clone", "--depth", "1", "--branch", head_ref, clone_url, work],
                           capture_output=True, text=True, timeout=90)
        if c.returncode != 0:
            return {"status": "clone_failed", "exit_code": -1, "output": c.stderr[-1500:]}
        return run_tests_in(work, timeout)
    finally:
        shutil.rmtree(work, ignore_errors=True)
