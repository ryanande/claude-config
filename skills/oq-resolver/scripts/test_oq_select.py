#!/usr/bin/env python3
"""Self-contained tests for oq_select (no pytest dep — run: python3 test_oq_select.py).

Exercises the PURE core only (parse_frontmatter / validate_oq_id / tractability /
select). The git boundary (main/_build_rows) is not tested here.
"""
import sys

from oq_select import parse_frontmatter, validate_oq_id, tractability, classify, select

_fails = []


def check(name, cond):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}")
        _fails.append(name)


# --- frontmatter parse, incl. the nested build: block (read-only; selector must
#     not choke on it) ---------------------------------------------------------
OQ0038 = """---
id: OQ-0038
title: How does a read-repair freshness fence stay effective?
status: open
date: 2026-06-17
author: wyatt.rupp
unblock-by:
  - action taxonomy — which actions are destructive-enough to gate vs warn
  - warn-fatigue prototype — evidence on whether a warn-only signal changes behavior
tags: [exocortex, consistency, seam-fences, worker]
promoted-to: null
build:
  render: never
  list: never
---

# body
"""

fm = parse_frontmatter(OQ0038)
check("parse status=open", fm["status"] == "open")
check("parse date", fm["date"] == "2026-06-17")
check("parse unblock-by 2 items", len(fm["unblock_by"]) == 2)
check("parse tags list", "seam-fences" in fm["tags"])
check("nested build does not leak into unblock_by",
      all("render" not in u for u in fm["unblock_by"]))

# --- --oq regex validation ---------------------------------------------------
check("validate 0037", validate_oq_id("0037") == "0037")
check("validate OQ-0037", validate_oq_id("OQ-0037") == "0037")
check("reject 37", validate_oq_id("37") is None)
check("reject injection", validate_oq_id("0037; rm -rf /") is None)
check("reject path", validate_oq_id("../secrets") is None)

# --- tractability heuristic: flag our-own-data, NOT design/mechanism ----------
UB_0023 = ["90 days of per-skill commit cadence post-v1.0.0 cut; max/min churn ratio threshold"]
UB_0024 = ["first MAJOR release cycle in dx-aicentral that exercises the stub-forwarder pattern"]
UB_0037 = ["warrant decision — preventative guard worth it; static lint vs a shared safe git-show helper"]
UB_0038 = ["action taxonomy — destructive-enough to gate vs warn",
           "warn-fatigue prototype — whether a warn-only signal changes behavior"]

check("0023 flagged needs-our-own-data", tractability(UB_0023) == "needs-our-own-data")
check("0024 flagged needs-our-own-data", tractability(UB_0024) == "needs-our-own-data")
check("0037 NOT flagged (design/mechanism)", tractability(UB_0037) == "ok")
check("0038 NOT flagged (warn-fatigue has external lit)", tractability(UB_0038) == "ok")

# --- classify + select -------------------------------------------------------
rows = [
    {"id": "0037", "status": "open", "date": "2026-06-17", "tags": [], "unblock_by": UB_0037},
    {"id": "0038", "status": "open", "date": "2026-06-10", "tags": [], "unblock_by": UB_0038},
    {"id": "0023", "status": "open", "date": "2026-05-30", "tags": [], "unblock_by": UB_0023},
    {"id": "0011", "status": "resolved", "date": "2026-05-30", "tags": [], "unblock_by": ["x"]},
    {"id": "0099", "status": "open", "date": "2026-05-01", "tags": [], "unblock_by": []},
]

ok23, _ = classify(rows[2])
check("0023 not selectable (needs-our-own-data)", not ok23)
okR, _ = classify(rows[3])
check("resolved excluded by allowlist", not okR)
okE, _ = classify(rows[4])
check("empty unblock-by excluded", not okE)
ok37, _ = classify(rows[0])
check("0037 selectable", ok37)

dec = select(rows)
check("auto-pick action resolve", dec["action"] == "resolve")
check("auto-pick oldest selectable = 0038 (2026-06-10 < 2026-06-17; 0023/0099 filtered)",
      dec["oq_id"] == "0038")
check("filtered surfaces 0023 + 0099 (open but skipped), not 0011 (resolved noise)",
      {f["id"] for f in dec["filtered"]} == {"0023", "0099"})

pin = select(rows, oq="0037")
check("--oq 0037 pins", pin["action"] == "resolve" and pin["oq_id"] == "0037")
pin_bad = select(rows, oq="0011")
check("--oq on resolved → none", pin_bad["action"] == "none")
pin_missing = select(rows, oq="1234")
check("--oq missing → none", pin_missing["action"] == "none")

# --- measuring OQs are excluded from selection, but stay visible ------------

_MEASURING_ROW = {"id": "0050", "status": "open", "date": "2026-07-13",
                  "tags": [], "unblock_by": ["needs a number"],
                  "measuring": "EVAL-0001"}
_PLAIN_ROW = {"id": "0051", "status": "open", "date": "2026-07-20",
              "tags": [], "unblock_by": ["needs a number"], "measuring": None}

ok, reason = classify(_MEASURING_ROW)
check("measuring OQ is not selectable", ok is False)
check("measuring reason names the eval", "EVAL-0001" in reason)

ok2, _ = classify(_PLAIN_ROW)
check("non-measuring open OQ still selectable", ok2 is True)

out = select([_MEASURING_ROW, _PLAIN_ROW])
check("select skips the measuring OQ", out["oq_id"] == "0051")
check("measuring OQ stays visible in filtered[]",
      any(f["id"] == "0050" for f in out["filtered"]))

# a null/absent measuring: must not exclude
_NULL_ROW = dict(_PLAIN_ROW, id="0052", measuring=None)
check("measuring=None does not exclude", classify(_NULL_ROW)[0] is True)
_ABSENT = {k: v for k, v in _PLAIN_ROW.items() if k != "measuring"}
_ABSENT["id"] = "0053"
check("absent measuring key does not exclude", classify(_ABSENT)[0] is True)

print()
if _fails:
    print(f"FAILED ({len(_fails)}): {_fails}")
    sys.exit(1)
print("all oq_select tests passed")
