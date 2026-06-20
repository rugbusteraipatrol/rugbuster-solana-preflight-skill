---
name: rugbuster-solana-preflight
description: Check Solana token risk before swaps, buys, transfers, or signatures, and optionally enforce the verdict with a code-level Shield wrapper. Use for unfamiliar SPL mints or any integration that must gate a money-moving action on ALLOW, WARN, BLOCK, or UNAVAILABLE.
---

# RugBuster Solana Preflight

Run a pre-transaction risk check before acting on an unfamiliar Solana mint.
Return one of four verdicts: `ALLOW`, `WARN`, `BLOCK`, or `UNAVAILABLE`.

## Scope

- Do not provide investment advice or guarantee that an `ALLOW` token is safe.
- Do not include a trade or signing implementation in this package.
- Allow Shield to invoke only the action function supplied by the adopter and
  only after the required verdict check.

## Run preflight

```bash
python skill/scripts/preflight_scan.py <TOKEN_MINT_ADDRESS>
```

Expect this JSON shape:

```json
{
  "verdict": "ALLOW | WARN | BLOCK | UNAVAILABLE",
  "risk_score": 0,
  "rugcheck_score": null,
  "flags": [],
  "reason": "short human-readable summary"
}
```

`risk_score` is a normalized 0-100 value or `null`. `rugcheck_score` is the raw
provider score and is not limited to 0-100.

## Apply verdicts

| Verdict | Exact client behavior |
|---|---|
| `ALLOW` | Permit the caller to proceed. Do not describe this as a safety guarantee. |
| `WARN` | Require explicit user confirmation before proceeding. |
| `BLOCK` | Do not proceed. Shield never accepts confirmation for this verdict. |
| `UNAVAILABLE` | Do not proceed. The API was unreachable or returned an unusable response. |

The client maps API/network failure and malformed responses to `UNAVAILABLE`,
never `ALLOW`. An API-level `UNKNOWN` score maps to `WARN`.

## Enforcement layer

For integrations that execute swaps or signatures, read [`SHIELD.md`](SHIELD.md)
and route the action through `run_protected` or `guarded`. The advisory
`preflight-guardian` pattern depends on an agent following instructions;
Shield enforces the decision in code and does not invoke the wrapped function
on `BLOCK` or `UNAVAILABLE`. A `WARN` requires exact `confirmed=True`.

Once adopted, Shield fully enforces the guarded call. It cannot prevent an
integration from bypassing the wrapper and calling separate swap logic
directly, so place Shield at every money-moving integration boundary.

## Load API details only when needed

Read [`references/api.md`](references/api.md) for the endpoint, source values,
and error contract.
