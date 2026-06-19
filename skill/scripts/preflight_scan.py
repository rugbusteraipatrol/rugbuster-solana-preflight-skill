#!/usr/bin/env python3
"""
RugBuster Solana Preflight Scanner.

Usage:
    python preflight_scan.py <TOKEN_MINT_ADDRESS>

Exits 0 on ALLOW, 1 on WARN, 2 on BLOCK, 3 on UNAVAILABLE.
Always prints a JSON verdict to stdout.

Security principle: this script NEVER returns ALLOW when the underlying
engine is unreachable or returns malformed data. Unavailable == BLOCK.
"""

import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = os.environ.get(
    "RUGBUSTER_API_BASE",
    "https://rugbuster-api-production.up.railway.app",
)
PREFLIGHT_NATIVE_PATH = "/v1/preflight"  # used automatically if it ever responds
SCORE_PATH = "/score"
TIMEOUT_SECONDS = 8

CRITICAL_FLAGS = {
    "mint_and_freeze_active_no_lp",
    "deployer_flagged_prior_rug",
    "wallet_clustering_rug_pattern",
}


def _unavailable(reason: str) -> dict:
    return {
        "verdict": "UNAVAILABLE",
        "risk_score": None,
        "rugcheck_score": None,
        "flags": [],
        "reason": reason,
    }


def _fetch_json(url: str):
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            if resp.status != 200:
                return None
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def _try_native_preflight(token: str):
    url = f"{API_BASE}{PREFLIGHT_NATIVE_PATH}?token={token}&chain=solana"
    data = _fetch_json(url)
    if not data or "verdict" not in data:
        return None
    if data["verdict"] not in {"ALLOW", "WARN", "BLOCK"}:
        return None
    return data


def _map_score_to_verdict(data: dict) -> dict:
    try:
        rug_score = float(data.get("rug_score"))
    except (TypeError, ValueError):
        return _unavailable("malformed rug_score in /score response")

    flags = data.get("flags") or []
    has_critical = any(f in CRITICAL_FLAGS for f in flags)

    if has_critical or rug_score >= 50:
        verdict = "BLOCK"
    elif rug_score >= 16:
        verdict = "WARN"
    else:
        verdict = "ALLOW"

    return {
        "verdict": verdict,
        "risk_score": rug_score,
        "rugcheck_score": data.get("rugcheck_score"),
        "flags": flags,
        "reason": data.get("verdict_label", "scored via /score endpoint"),
    }


def run_preflight(token: str) -> dict:
    native = _try_native_preflight(token)
    if native is not None:
        return native

    url = f"{API_BASE}{SCORE_PATH}?token={token}&chain=solana"
    data = _fetch_json(url)
    if data is None:
        return _unavailable("rugbuster API unreachable or returned non-200/invalid JSON")

    return _map_score_to_verdict(data)


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps(_unavailable("missing token mint address argument")))
        return 3

    token = sys.argv[1].strip()
    if not token:
        print(json.dumps(_unavailable("empty token mint address")))
        return 3

    result = run_preflight(token)
    print(json.dumps(result, indent=2))

    return {"ALLOW": 0, "WARN": 1, "BLOCK": 2, "UNAVAILABLE": 3}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
