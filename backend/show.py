import json, sys
d = json.load(open(f"reports/{sys.argv[1]}.json")); r = d["report"]
print("RESULT:", r["decision"], "| risk", r["risk_score"], "| conf", r["confidence"], "| findings", len(r["findings"]), "|", d["runtime_s"], "s")
print("summary:", r["summary"][:250])
for f in r["findings"][:3]: print("  finding:", f["severity"], f["file"], f["issue"][:110])
for m in r["missing_tests"][:3]: print("  missing test:", m[:110])
