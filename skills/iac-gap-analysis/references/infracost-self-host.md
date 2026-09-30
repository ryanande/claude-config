# Self-hosted Infracost Cloud Pricing API (zero resource-metadata egress)

Use this when org policy forbids sending *any* infrastructure metadata to a third-party SaaS. The Infracost **CLI** already parses your `.tf` locally and never transmits code/state/secrets/credentials — but by default its **price lookups** call the hosted Cloud Pricing API. Self-hosting moves that lookup onto your own infra.

**Trust-boundary note (the whole point):** with a self-hosted pricing API, the CLI's pricing queries go to *your* endpoint → **nothing about your resources leaves your network**. The only external traffic is the **inbound download of the public price list** (~3M AWS/Azure/GCP prices) from Infracost's S3 — that's a one-way download of public data, not an upload of your infra. A free Infracost API key is required **once**, only to authorize that download.

## Setup (docker-compose, ~15 min)

```bash
# 1. Clone the self-host repo (official; IBM-Cloud maintains a current mirror)
git clone https://github.com/infracost/cloud-pricing-api && cd cloud-pricing-api

# 2. Get a free key ONCE (only used to download the public price DB)
#    infracost auth login   → or register at infracost.io; copy the key
export INFRACOST_API_KEY=ico-xxxxxxxx

# 3. Stand up Postgres + the API and seed the price DB
docker-compose run init_job          # starts Postgres, downloads the price dump
docker-compose up -d                  # API now serving on http://localhost:4000

# 4. Verify
open http://localhost:4000            # shows price freshness + stats
#    GraphQL playground at http://localhost:4000/graphql
```

Weekly price refresh (cron):
```
0 4 * * SUN  docker-compose run --rm update_job npm run job:update >> /var/log/cron.log 2>&1
```

## Point the CLI at it

```bash
export INFRACOST_PRICING_API_ENDPOINT=http://localhost:4000   # or your internal host
export INFRACOST_API_KEY=self-hosted                          # any non-empty value; self-hosted endpoint doesn't auth
infracost breakdown --path <stack>           # now 100% on-prem, no egress of resource shapes
```

For CI: host the API on an internal VM/cluster, set `INFRACOST_PRICING_API_ENDPOINT` to its internal URL, and inject a dummy `INFRACOST_API_KEY` as a pipeline var.

## When to bother

- **Self-host** if data-classification policy forbids third-party egress of resource metadata (type/region/SKU), or for air-gapped envs.
- **Hosted free key** is fine if policy permits that metadata leaving to a SOC 2 vendor — the CLI still never sends code/state/secrets.
- **Skip** if cost analysis isn't worth either; the gap analysis then leaves Cost as semantic/qualitative and says so under "Coverage & limitations."

Sources: Infracost docs *Self-hosting* (`infracost.io/docs/cloud_pricing_api/self_hosted/`), `github.com/infracost/cloud-pricing-api`. Verify image/repo currency before standing it up.
