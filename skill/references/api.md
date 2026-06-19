# RugBuster API Reference

## Endpoint

```
GET https://rugbuster-api-production.up.railway.app/score?token=<MINT_ADDRESS>&chain=solana
```

(Base URL is read from `RUGBUSTER_API_BASE` env var if set, defaulting to
the URL above. See `skill/scripts/preflight_scan.py`.)

## Response shape (current /score endpoint)

```json
{
  "token": "string",
  "network": "solana",
  "rug_score": 0-100,
  "rugcheck_score": 0-100,
  "verdict_label": "string",
  "flags": ["string", "..."]
}
```

## Mapping to preflight verdict

The /score endpoint does not itself return ALLOW/WARN/BLOCK — this skill
maps it client-side:

- `rug_score <= 15` and no critical flags -> `ALLOW`
- `rug_score 16-49`, or non-critical flag present -> `WARN`
- `rug_score >= 50`, or any critical flag -> `BLOCK`
- Non-200 response, timeout, or unparseable JSON -> `UNAVAILABLE`

Critical flags (any one forces BLOCK regardless of score):
- both mint authority and freeze authority active with no LP lock evidence
- known rug-pattern wallet clustering
- deployer wallet flagged in prior rug events

This mapping lives in `preflight_scan.py` so it can be updated without
changing the API contract. If RugBuster ships a native `/v1/preflight`
endpoint that returns the verdict directly, update `PREFLIGHT_NATIVE_PATH`
in the script and this skill will prefer it automatically.

## Timeouts

Default timeout: 8 seconds. On timeout, return `UNAVAILABLE` — do not retry
silently more than once.
