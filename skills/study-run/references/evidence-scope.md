# study-run — evidence scope and the resolver chain

Loaded at Step 1. Under D1 every `protocol.evidence-scope` entry is
`{remote: <URL>, ref: HEAD-at-run}`; the URL is the identity. Evidence is read
from a pinned git tree, never from a live directory. D2's `blind-scope` and D3's
`evidence-scope-rule` resolve through the same chain — see §D2 and §D3 below.

## Resolver chain (per entry, first rung that holds)

1. The research-docs checkout resolved in Step 1, when `git remote get-url origin` equals the entry's URL.
2. `$DX_ARCH_META_ROOT/repos/*` then `$DX_META_ROOT/repos/*`, the first whose `origin` equals the URL.
3. The clone root `~/.claude/skills/study-run/clones/<sha1 of URL>/`: `git clone --quiet <url>` when absent; on every use
   `git fetch --quiet origin && git reset --quiet --hard origin/HEAD`.
4. Refuse: "evidence-scope entry unresolvable: <url>".

A rung 1/2 tree is used only when all three hold: `git status --porcelain` is
empty; its path is not under `~/.claude`; `git merge-base --is-ancestor HEAD
<remote-head>` where `<remote-head>` is `git ls-remote <url> HEAD`. Otherwise
fall to rung 3. Record `{remote, path, sha, rung}` per entry; `sha` is the
tree's HEAD after the rung's steps.

## The clone root

Gitignored (`clones/`), excluded from deploy sync and ensured in
`.claude-deploy.toml`, plus an explicit `protect_extra` entry — one guard more
than `cache/`, which relies on the deployer's built-in protect denylist as its
second. A clone
is disposable: it is reset to the remote head on every use, so nothing in it
is ever ground truth the remote does not vouch for.

## `~/.claude` is never a scope path

The block's `role: harness-runtime` entry is the `claude-config` URL, pinned
like any other remote. Tracked content is reproducible at its SHA; deployed
skill directories are decided in their source repositories when the census
names them; unsourced content (`projects/`, `telemetry/`, `cache/`) is
unreachable and an item that needs it lands UNRESOLVED.

## Excluded remotes

`evidence-scope-excluded` carries `{remote, reason: remote-inaccessible,
items-citing}` only. Re-attempt `git ls-remote <url>` for each at Step 1 and
Step 8; one that answers is recorded as a deviation.

## Residuals, named

- **Confined by brief, not by jail.** A spawn with ordinary tools can read
  anything on the runner's machine. What bounds it is the gate: a `quote`
  must grep in a pinned tree. Laundering (reading elsewhere, then finding a
  matching quote in scope) is not detected; it sits with RFC-0018's
  labeler-honesty assumptions.
- **`ref: HEAD-at-run` leaves sibling content unfrozen** between design and
  run. Compensating control: the run record's `{remote, path, sha, rung}` set
  plus tamper condition (d) — an already-run document refuses re-execution.

## D2 — `blind-scope`, and what it must not reach

D2 has no `evidence-scope`. `protocol.blind-scope` names what the **skill under
test** may read, and its entries are `{remote, ref, path}` — ref a pinned sha
rather than `HEAD-at-run`, because the corpus is frozen at `corpus-ref.sha`.

The invariant is inverted. D1's scope is derived and **maximal**; D2's is
**exclusive**: the skill under test must not be able to reach the answer key.

**Repository granularity is not enough, so the resolver chain above is not used
for `blind-scope`.** Rungs 1 to 3 all hand back a git tree WITH HISTORY — an
in-checkout tree, a sibling checkout, or a clone that is fetched and reset. The
commit that planted the defects *is* the answer key, so `git log -p` over the
corpus recovers the placement without the publication remote ever being touched.
Sibling paths in the same repository leak as well: this suite's own D2 fixture
states the per-class counts verbatim.

`blind-scope` is therefore materialized differently: `git archive` at
`corpus-ref.sha`, scoped to the entry's `path`, unpacked into a directory with no
`.git`. `recheck.py manifest` checks all three legs together — publication remote
absent, every entry path-scoped and ref-pinned, and no export directory carrying
`.git` or `.gitmodules` — and refuses rather than reporting. Its flags are
required, so an omitted one cannot read as a pass.

The residual adjudication reads that same export, plus the one candidate manifest
row its pack carries. It never resolves the manifest itself.

## D3 — `evidence-scope-rule`, resolved per enrolled item

D3 has no census at freeze time, so it cannot pin a scope list.
`protocol.evidence-scope-rule` is a verbatim rule, applied when each artifact
enrols; the `{remote, path, sha, rung}` set it resolves to is recorded in that
artifact's enrolment-ledger row rather than in the frozen block. Step 3a
validates the ledger, not a scope hash.

The key is present when and only when `outcome.adjudicated` is true. A D3 study
whose outcomes are read mechanically resolves nothing through this chain; it
reads `outcome.source` and gates the citation at the enrolled artifact's merge
SHA.
