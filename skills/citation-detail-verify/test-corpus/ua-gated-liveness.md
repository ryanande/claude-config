---
title: Fixture — ua-gated-liveness
date: 2026-06-02
fixture: citation-detail-verify
expected_check_name: url-liveness
expected_status: pass
sources:
  - {id: A1, title: "ISO/IEC/IEEE 42010:2022 - Software, systems and enterprise — Architecture description", url: "https://www.iso.org/standard/74393.html", tier: 1}
  - {id: A2, title: "A Genuinely Unreachable Paper", url: "https://example.com/papers/no-route-anywhere.pdf", tier: 1}
---

# Fixture — ua-gated-liveness

This decision artifact cites [A1], an `iso.org` standards catalog page. A bare fetcher with no browser `User-Agent` (Claude's default WebFetch) receives HTTP `403` from this host — a bot-block, NOT a dead link. The page is live and returns HTTP `200` to a browser `User-Agent`.

Running `/citation-detail-verify --artifact <this-file>` MUST apply the `references/cache-contract.md` §Liveness fetch fallback ladder: the first-attempt `403` is a ladder TRIGGER, so the skill retries with a browser `User-Agent`, obtains the `200` body, and emits `check-name: url-liveness`, `status: pass`, `citation-id: [A1]`. This is the `liveness-ladder-recovery` case: a first-attempt `403`/`429`/empty-body MUST NOT be emitted as a standalone `fail` or `unverifiable` verdict.

By contrast, [A2] is genuinely unreachable: it fails the default fetch, fails the browser-`User-Agent` retry, and has no alternate authoritative route (no DOI, no bibliographic API record, no listing host). Only after the ladder is EXHAUSTED does [A2] terminate at `status: unverifiable`, with `check-detail` naming the routes attempted. The exhausted-ladder terminal is the only legitimate path to `unverifiable` for a fetch-reachability check.

The contrast is the point of this fixture: [A1] `liveness-ladder-recovery` → pass; [A2] exhausted ladder → unverifiable. A skill that emits `unverifiable` (or `fail`) for [A1] on the first-attempt `403` — without climbing the ladder — exhibits the first-attempt-misclassification pathology this fixture guards against. (The `absent`-primitive row over this fixture asserts that pathology's compound literal never appears here; keep the fixture free of that token.)
