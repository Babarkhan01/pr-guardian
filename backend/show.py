import json, sys
d = json.load(open(f"reports/{sys.argv[1]}.json")); r = d["report"]
print("RESULT:", r["decision"], "| risk", r["risk_score"], "| conf", r["confidence"], "| findings", len(r["findings"]))
print("summary:", r["summary"][:250])
