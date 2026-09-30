# Evidence base — what a finding can be grounded in

Every check in this skill should trace to a source, so a finding is *defensible*, not opinion. Two tiers, in the spirit of `survey-author`'s source-tier rubric but adapted for a gap analysis: **Tier 1 is the normative authority a finding is failed against; Tier 2 is the empirical evidence for why the check matters.** A finding's optional `source` field (see `gap-matrix.md`) cites one or both.

> **Citation discipline (survey-author-style).** Every Tier-2 entry below was verified (title, authors, venue, year) before being added. Do **not** add a new academic citation from memory — confirm it via the venue/DOI first, exactly as `survey-author` classifies a Tier-1 source. A wrong citation is worse than none.

---

## Tier 1 — Normative authority (a finding can be *failed against* these)

These are standards/frameworks with enumerable controls. Cite the specific control id where possible (e.g. `CIS-Azure-3.1`), so the reader can look it up.

| Source | What it governs | Citable as |
|--------|-----------------|-----------|
| **Azure Well-Architected Framework** (Microsoft) | The 5 pillars — Reliability, Security, Cost, Operational Excellence, Performance. The org's stated bar (principle #3). | `WAF-<pillar>` (e.g. `WAF-Reliability`) |
| **CIS Microsoft Azure Foundations Benchmark** | Prescriptive, control-numbered security baseline for Azure. The compliance backbone of the `security` dimension. | `CIS-Azure-<section.control>` (e.g. `CIS-Azure-3.1`) |
| **ISO/IEC 27001 (Annex A)** | ISMS control families — access control, cryptography, ops security. | `ISO27001-A.<control>` |
| **SOC 2 (AICPA Trust Services Criteria)** | Security/Availability/Confidentiality criteria for service orgs. | `SOC2-<TSC>` (e.g. `SOC2-CC6.1`) |
| **NIST SP 800-53** *(optional, for federal/regulated stacks)* | Control catalog; useful when a Tier-1 stack carries regulated data. | `NIST-800-53-<control>` |

Tier-1 sources set the **pass/fail bar**. The intent-weighting (`scoring.md`) decides how hard that bar bites per criticality tier.

---

## Tier 2 — Empirical evidence (why the check matters)

Peer-reviewed / arXiv studies on IaC quality and security. Cite these where a check maps to a documented smell/defect, so "this is a problem" is backed by measurement, not assertion. All verified June 2026.

| Tag | Citation | What it establishes | Grounds these checks |
|-----|----------|---------------------|----------------------|
| `Rahman2019-SS` | Rahman, Parnin & Williams, **"The Seven Sins: Security Smells in Infrastructure as Code Scripts"**, *ICSE 2019*. DOI [10.1109/ICSE.2019.00033](https://dl.acm.org/doi/10.1109/ICSE.2019.00033). | Qualitative analysis of 1,726 scripts → 7 recurring security smells; SLIC tool found 21,201 occurrences across 15,232 scripts incl. 1,326 hard-coded passwords. | Hard-coded secrets; empty/weak passwords; hardcoded IPs; suspicious comments; use of HTTP-without-TLS (security dimension). |
| `RahmanWilliams2019-DEF` | Rahman & Williams, **"Source Code Properties of Defective Infrastructure as Code Scripts"**, *Information and Software Technology, 2019*. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0950584919300965) · [arXiv 1810.09605](https://arxiv.org/abs/1810.09605). | Lines-of-code and hard-coded strings as configuration values correlate with defective IaC scripts. | Large/monolithic stacks; hardcoded config values that belong in variables (structural dimension). |
| `Guerriero2019-IND` | Guerriero, Garriga, Tamburri & Palomba, **"Adoption, Support, and Challenges of Infrastructure-as-Code: Insights from Industry"**, *ICSME 2019*, pp. 580–589. [PDF](https://fpalomba.github.io/pdf/Conferencs/C42.pdf). | 44-company interview study: testing/maintainability are the top IaC pain points; no single full-fledged tooling solution. | Modularization/DRY, testing-gap, and maintainability findings (structural / operations dimensions). |
| `Saavedra2022-GLITCH` | Saavedra & Ferreira, **"GLITCH: Automated Polyglot Security Smell Detection in Infrastructure as Code"**, *ASE 2022*. DOI [10.1145/3551349.3556945](https://dl.acm.org/doi/10.1145/3551349.3556945). | Technology-agnostic intermediate representation lets the same security-smell catalog apply across Terraform/Ansible/Chef/Puppet — validates a *cross-tool* smell taxonomy. | Justifies the "beyond regex" semantic smell checks being provider-agnostic (security / structural). |
| `Opdebeeck2022-VAR` | Opdebeeck, Zerouali & De Roover, **"Smelly Variables in Ansible Infrastructure Code: Detection, Prevalence, and Lifetime"**, *MSR 2022*. [ResearchGate](https://www.researchgate.net/publication/364396390). | Variable/precedence smells are prevalent and long-lived in IaC; control/data-flow context matters for true-positive detection. | Dead/unused variables, magic strings, and the "beyond regex — read meaning" discipline (structural dimension). |

---

## Source-tagging convention

The canonical finding shape (`gap-matrix.md`) carries an optional `source` array. Populate it with the most specific applicable tags:

```
"source": ["CIS-Azure-3.1", "Rahman2019-SS"]   // normative bar + empirical why
```

- A **security/compliance** finding should carry at least one **Tier-1** tag (the control it fails).
- A **structural / smell** finding should carry the **Tier-2** study that documents the smell.
- A finding may carry both; it may carry neither only if it's a pure PrePass-principle/Four-Planes alignment finding (cite the principle # instead).

## Why this strengthens the analysis

- **Defensibility** — "public access on a Tier-1 Cosmos account" lands harder as `CIS-Azure-<n>` than as a reviewer's opinion.
- **Confidence signaling (CI-4)** — a finding backed by a Tier-1 control + Tier-2 study + tool corroboration is higher-confidence than a semantic-only read; reflect that when scoring.
- **Refresh** — re-verify Tier-1 control numbers against the current CIS Azure Benchmark and Azure WAF service guides (`microsoft_docs_search`) when versions move; re-confirm Tier-2 citations before adding new ones.
