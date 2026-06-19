# RugBuster Solana API

## Endpoint

```http
GET https://rugbuster-solana-api-production.up.railway.app/score?address=<MINT>
```

The service is Solana-only; do not send a `chain` parameter. Override the base
URL with `RUGBUSTER_API_BASE` only when testing a compatible deployment.

## Cache hit

```json
{
  "ok": true,
  "address": "...",
  "chain": "solana",
  "risk_score": 5,
  "label": "GOOD",
  "rugcheck_score": 1,
  "risk_flags": [],
  "source": "postgres_cache",
  "scanned_at": "2026-05-29T12:16:42.937869+00:00",
  "token_name": "USD Coin",
  "token_symbol": "USDC"
}
```

Verdict mapping:

- `DANGER` or risk >= 70: `BLOCK`
- `WARN` or risk 35-69: `WARN`
- `GOOD` and risk < 35: `ALLOW`

## Cache miss

```json
{
  "ok": true,
  "label": "UNKNOWN",
  "risk_score": null,
  "risk_flags": ["not_in_intelligence_db"],
  "source": "cache_miss"
}
```

A cache miss always maps to `WARN`. It never maps to `ALLOW`.

## Errors

- Invalid or EVM address: HTTP 400 with `invalid solana mint address`.
- Other non-200 responses, timeouts, malformed JSON, and `ok: false` database
  errors map to `UNAVAILABLE`.
- Calling agents must treat `UNAVAILABLE` as `BLOCK`.

The client timeout is eight seconds. Live scanning for unseen mints is planned
for Phase 2.
