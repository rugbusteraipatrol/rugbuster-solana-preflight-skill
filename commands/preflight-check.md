# /preflight-check

Run a RugBuster preflight scan on a Solana token mint address and report
the verdict.

## Usage

```
/preflight-check <TOKEN_MINT_ADDRESS>
```

## Behavior

Invokes `skill/scripts/preflight_scan.py` with the given address and
prints a human-readable summary:

- Verdict (ALLOW / WARN / BLOCK / UNAVAILABLE)
- Risk score and RugCheck score
- Any flags raised
- One-line recommendation

If the result is `UNAVAILABLE`, state clearly that the safety engine could
not be reached and that this should be treated as a block, not skipped.
