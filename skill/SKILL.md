# RugBuster Solana Preflight Skill

Pre-transaction risk gate for Solana tokens. Call this skill **before** any
swap, buy, or signature involving an unfamiliar SPL token. It returns a
hard verdict — ALLOW, WARN, or BLOCK — so an agent never signs blind.

## When to use this skill

- Before executing a swap (Jupiter, Raydium, Orca, etc.)
- Before approving a token transfer to/from an unknown mint
- Before recommending a token to a user
- Any time an agent is about to sign a transaction involving a token it
  hasn't already vetted in this session

## What it does NOT do

- Does not execute trades or sign transactions
- Does not give investment advice
- Does not guarantee a token is safe — ALLOW means "no hard rug signals
  detected," not "guaranteed legitimate"

## How to use

Run the preflight script with the token mint address:

```bash
python skill/scripts/preflight_scan.py <TOKEN_MINT_ADDRESS>
```

Returns JSON:

```json
{
  "verdict": "ALLOW | WARN | BLOCK | UNAVAILABLE",
  "risk_score": 0-100,
  "rugcheck_score": 0-100,
  "flags": ["mint_authority_active", "freeze_authority_active", "..."],
  "reason": "short human-readable summary"
}
```

## Verdict logic

| Verdict | Meaning | Agent behavior |
|---|---|---|
| `ALLOW` | risk_score below threshold, no critical flags | Proceed, but still surface flags to the user |
| `WARN` | risk_score in middle band, or non-critical flags present | Surface flags explicitly, ask user to confirm before proceeding |
| `BLOCK` | risk_score above threshold, or critical flag (e.g. mint+freeze both active with no LP lock) | Do not proceed without explicit, informed user override |
| `UNAVAILABLE` | API unreachable, timed out, or returned malformed data | **Treat as BLOCK.** Never silently proceed when the engine can't be reached. |

This skill never returns a false ALLOW. If the underlying engine cannot be
reached, the verdict is `UNAVAILABLE` and must be handled identically to
`BLOCK` by the calling agent.

## Enforcement layer

Use the code-level Shield for integrations that execute swaps or signatures.
Read `skill/SHIELD.md`, then route the action through `run_protected` or the
`guarded` decorator. Unlike the advisory `preflight-guardian` agent pattern,
Shield checks the verdict in code and does not invoke the wrapped function on
`BLOCK` or `UNAVAILABLE`. A `WARN` requires explicit `confirmed=True`.

Once adopted, Shield fully enforces the guarded call. It cannot prevent an
integration from bypassing the wrapper and calling separate swap logic
directly, so recommend Shield at every money-moving integration boundary.

## Reference

See `skill/references/api.md` for the full API contract and field
definitions. Load it only when you need raw field-level detail — the table
above is enough for normal use.
