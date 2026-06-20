# RugBuster Solana API

## Endpoint

```http
GET https://rugbuster-solana-api-production.up.railway.app/score?address=<MINT>
```

The service is Solana-only. Do not send a `chain` parameter. Set
`RUGBUSTER_API_BASE` only when testing a compatible deployment.

## Response sources

The API checks sources in this order:

1. `postgres_cache`: collector-enriched `solana_scans` result.
2. `live_cache`: a live RugCheck baseline cached for less than one hour.
3. `live_rugcheck`: a new rate-limited RugCheck baseline.

Collector results can contain richer historical and behavioral evidence than a
single live report. Do not present the two sources as equivalent.

## Verified collector response

This response was verified for USDC on 2026-06-20:

```json
{
  "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "chain": "solana",
  "label": "GOOD",
  "ok": true,
  "risk_flags": [],
  "risk_score": 5,
  "rugcheck_score": 1,
  "scanned_at": "2026-05-29T12:16:42.937869+00:00",
  "source": "postgres_cache",
  "token_name": "Unknown ()",
  "token_symbol": null
}
```

Verdict mapping:

- `DANGER` or risk >= 70: `BLOCK`.
- `WARN` or risk 35-69: `WARN`.
- `GOOD` and risk < 35: `ALLOW`.

## Live-scan failure

If the collector and live cache miss and RugCheck returns an error, timeout,
rate limit, or malformed response, the API responds with HTTP 200 and a safe
unknown result:

```json
{
  "address": "<MINT>",
  "chain": "solana",
  "ok": true,
  "label": "UNKNOWN",
  "note": "No verified score is available. Treat this token as unverified.",
  "risk_score": null,
  "risk_flags": ["not_in_intelligence_db"],
  "scanned_at": null,
  "source": "live_scan_unavailable"
}
```

The preflight client maps this API-level `UNKNOWN` to `WARN`, never `ALLOW`.
Shield therefore requires explicit `confirmed=True` before invoking an action.

## Other errors

- Invalid or EVM address: HTTP 400 with `invalid solana mint address`.
- Other non-200 responses, an unreachable API, malformed JSON, and `ok: false`
  responses map to `UNAVAILABLE`.
- Shield always refuses `BLOCK` and `UNAVAILABLE`.

The preflight HTTP client timeout is eight seconds. The API's internal live
RugCheck request timeout is six seconds.
