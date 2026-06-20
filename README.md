# RugBuster Solana Preflight Skill

A pre-transaction safety gate for Solana AI agents. Before any swap, buy,
or signature involving an unfamiliar SPL token, this skill returns a hard
**ALLOW / WARN / BLOCK** verdict backed by RugBuster's Solana intelligence
database of 20k+ scanned tokens and weighted scoring, so an agent never signs
blind.

## The problem

AI coding/trading agents increasingly construct and sign Solana
transactions autonomously. None of the standard Solana AI Kit skills
include a fraud/rug-detection gate — agents can build and submit a swap
for a brand-new, unvetted token with zero risk checks. This skill closes
that gap.

## What it does

- Calls the dedicated Solana API, served from its low-latency score cache
- Maps the response to a strict verdict: `ALLOW`, `WARN`, `BLOCK`, or
  `UNAVAILABLE`
- **Never returns a false ALLOW.** If the engine can't be reached, the
  verdict is `UNAVAILABLE`, which the calling agent must treat as a block.
- Returns explicit `UNKNOWN`/`WARN` for cache misses; unseen tokens never pass
  as safe. Live on-demand scanning for unseen mints is planned for Phase 2.
- Surfaces RugCheck score, mint/freeze authority status, and CIA Engine
  flags (funding origin, wallet clustering, deployer history) in plain
  language

## Install

```bash
git clone https://github.com/rugbusteraipatrol/rugbuster-solana-preflight-skill.git
cd rugbuster-solana-preflight-skill
bash install.sh /path/to/your-project
```

Or drop the `skill/` folder directly into an existing Solana AI Kit
install under `.claude/skills/rugbuster-preflight/`.

## Usage

```
/preflight-check <TOKEN_MINT_ADDRESS>
```

or directly:

```bash
python skill/scripts/preflight_scan.py <TOKEN_MINT_ADDRESS>
```

### Enforced Shield

For code that executes swaps or signatures, use `run_protected` or the
`guarded` decorator from `skill/scripts/shield.py`. See
[`skill/SHIELD.md`](skill/SHIELD.md) for the integration pattern.

Once an integration routes its swap/sign call through `rugbuster_shield`, that
call cannot execute on a failing verdict: the action function is never invoked.
It does not prevent an integration from bypassing the wrapper entirely by
calling its own swap logic directly instead of adopting the pattern. No library
can force adoption.

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

All tests run offline against mocked responses — no live API calls are
made during CI.

## API

Backed by `https://rugbuster-solana-api-production.up.railway.app`. See
`skill/references/api.md` for the full contract. Override with the
`RUGBUSTER_API_BASE` environment variable if self-hosting against a
different RugBuster deployment.

## License

MIT
