"""Local smoke test for the dictionary explorer (TestClient, no port)."""
from __future__ import annotations

import sys
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def check(path: str, expect: list[str], status: int = 200) -> bool:
    r = client.get(path)
    ok = r.status_code == status
    body = r.text if r.status_code == 200 else ""
    missing = [e for e in expect if e not in body]
    mark = "OK " if (ok and not missing) else "FAIL"
    print(f"[{mark}] {path} -> {r.status_code} (want {status})"
          + (f"  missing={missing}" if missing else ""))
    return ok and not missing


results = []
# core
results.append(check("/", ["FreeNIC"]))
results.append(check("/dictionary", ["Variable dictionary", "FR Y-9C", "Call Report",
                                     "UBPR", "FDIC", "Historical", "schedules"]))
# 3 random schedule pages (one Call, two Y-9C incl an income schedule)
results.append(check("/dictionary/schedule/call_RC", ["Balance Sheet", "Line items",
                                                      "Download", "RCFD2170", "sched_call_rc"]))
results.append(check("/dictionary/schedule/y9c_HC-R", ["Regulatory Capital",
                                                       "risk-weighted", "Line items"]))
results.append(check("/dictionary/schedule/y9c_HI", ["Income", "Line items", "Pitfalls"]))
# 2 variable pages (a line-item code + a UBPR code)
results.append(check("/dictionary/variable/BHCK2170", ["BHCK2170", "Attributes",
                                                       "Where it is exposed"]))
results.append(check("/dictionary/variable/UBPRE013", ["UBPRE013", "UBPR concept",
                                                       "Derivation"]))
# sources
results.append(check("/sources", ["Data sources", "FFIEC", "Coverage", "Use for"]))
# 404 cleanliness
results.append(check("/dictionary/variable/NOTACODE", [], status=404))
results.append(check("/dictionary/schedule/call_ZZZ", [], status=404))

print()
if all(results):
    print("ALL SMOKE CHECKS PASSED")
    sys.exit(0)
print("SOME SMOKE CHECKS FAILED")
sys.exit(1)
