# RugBuster Solana Preflight Skill

A pre-transaction risk gate for Solana agents and integrations. It converts
RugBuster API results into `ALLOW`, `WARN`, `BLOCK`, or `UNAVAILABLE` before a
caller decides whether to swap, buy, transfer, or sign.

The production intelligence database contained 21,382 collector records for
21,382 distinct mint addresses when verified on 2026-06-20.

## The problem

An agent can construct a transaction for an unfamiliar mint without first
checking token risk. This skill provides a reusable preflight check and an
optional code-level enforcement wrapper for that integration boundary.

## Preflight check

`preflight_scan.py` calls the production Solana API and maps its response:

- `GOOD` with risk below 35 becomes `ALLOW`.
- `WARN` or risk from 35 through 69 becomes `WARN`.
- `DANGER` or risk 70 and above becomes `BLOCK`.
- An unreachable API, invalid response, or malformed score becomes
  `UNAVAILABLE`.

Run it directly:

```bash
python skill/scripts/preflight_scan.py <TOKEN_MINT_ADDRESS>
```

Collector-backed results may include accumulated creator history, launch
sniping, funding, and wallet-clustering evidence. If a mint is absent from the
collector table, the API uses a rate-limited live RugCheck baseline and caches
it for one hour. That one-shot baseline is intentionally less rich. If the
upstream live scan cannot produce a score, the API returns `UNKNOWN`, which the
preflight client maps to `WARN`, never `ALLOW`.

## Shield enforcement layer

For code that executes swaps or signatures, use `run_protected` or the
`guarded` decorator from `skill/scripts/shield.py`. See
[`skill/SHIELD.md`](skill/SHIELD.md) for the integration pattern.

Once an integration routes its swap/sign call through `rugbuster_shield`, that
call cannot execute on a failing verdict: the action function is never invoked.
It does not prevent an integration from bypassing the wrapper entirely by
calling its own swap logic directly instead of adopting the pattern. No library
can force adoption.

Shield permits `ALLOW`, requires explicit `confirmed=True` for `WARN`, and
always refuses `BLOCK`, `UNAVAILABLE`, or an unrecognized verdict.

## Live demo

The demo uses the real production API with a known collector-backed GOOD mint
and a known collector-backed DANGER mint. It contains no trade implementation;
the swap function only prints when Shield invokes it.

```bash
python demo/shield_demo.py
```

The GOOD example prints `EXECUTING SWAP`. The DANGER example prints only the
blocked result, proving that the placeholder action was not called.

## Install

Run these commands in macOS/Linux Bash or Windows Git Bash:

```bash
git clone https://github.com/rugbusteraipatrol/rugbuster-solana-preflight-skill.git
cd rugbuster-solana-preflight-skill
bash install.sh /path/to/your-project
```

The command was verified from a clean clone on 2026-06-20. It installs the
skill contents under `.claude/skills/rugbuster-preflight/`, plus the agent and
command files. For manual installation, copy the **contents** of `skill/` into
that destination rather than nesting the `skill` directory itself.

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

The test suite is offline and mocks API responses. The separate live demo is
the end-to-end production check.

## API dependency

Production API: `https://rugbuster-solana-api-production.up.railway.app`

Source: [rugbusteraipatrol/rugbuster-solana-api](https://github.com/rugbusteraipatrol/rugbuster-solana-api)

See [`skill/references/api.md`](skill/references/api.md) for the response
contract. Set `RUGBUSTER_API_BASE` only to use a compatible deployment.

## License

MIT. See [`LICENSE`](LICENSE).
