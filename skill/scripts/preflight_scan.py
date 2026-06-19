#!/usr/bin/env python3
"""RugBuster Solana preflight scanner.

Usage: python preflight_scan.py <TOKEN_MINT_ADDRESS>

Exits 0 on ALLOW, 1 on WARN, 2 on BLOCK, and 3 on UNAVAILABLE.
Always prints a JSON verdict to stdout. Engine failure is never ALLOW.
"""

import json
import os
import sys
import urllib.error
import urllib.request


API_BASE = os.environ.get(
    "RUGBUSTER_API_BASE",
    "https://rugbuster-solana-api-production.up.railway.app",
).rstrip("/")
SCORE_PATH = "/score"
TIMEOUT_SECONDS = 8


def _unavailable(reason: str) -> dict:
    return {
        "verdict": "UNAVAILABLE",
        "risk_score": None,
        "rugcheck_score": None,
        "flags": [],
        "reason": reason,
    }


def _fetch_json(url: str) -> tuple[int | None, dict | None]:
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            body = None
        return error.code, body
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None, None


def _map_score_to_verdict(data: dict) -> dict:
    if data.get("ok") is not True:
        return _unavailable(data.get("error") or "RugBuster API returned an invalid response")

    label = str(data.get("label") or "").upper()
    source = data.get("source")
    flags = data.get("risk_flags")
    if not isinstance(flags, list):
        flags = []

    if label == "UNKNOWN" or source == "cache_miss":
        return {
            "verdict": "WARN",
            "risk_score": None,
            "rugcheck_score": data.get("rugcheck_score"),
            "flags": flags or ["not_in_intelligence_db"],
            "reason": "token not yet in intelligence DB - unverified, proceed with caution",
        }

    try:
        risk_score = float(data["risk_score"])
    except (KeyError, TypeError, ValueError):
        return _unavailable("malformed risk_score in /score response")

    if label == "DANGER" or risk_score >= 70:
        verdict = "BLOCK"
    elif label == "WARN" or 35 <= risk_score < 70:
        verdict = "WARN"
    elif label == "GOOD" and risk_score < 35:
        verdict = "ALLOW"
    else:
        return _unavailable("unrecognized label in /score response")

    return {
        "verdict": verdict,
        "risk_score": risk_score,
        "rugcheck_score": data.get("rugcheck_score"),
        "flags": flags,
        "reason": f"RugBuster label: {label}",
    }


def run_preflight(mint: str) -> dict:
    url = f"{API_BASE}{SCORE_PATH}?address={mint}"
    status, data = _fetch_json(url)

    if status == 400:
        reason = data.get("error") if isinstance(data, dict) else None
        return _unavailable(reason or "invalid solana mint address")
    if status != 200 or not isinstance(data, dict):
        return _unavailable("RugBuster API unreachable or returned non-200/invalid JSON")

    return _map_score_to_verdict(data)


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps(_unavailable("missing token mint address argument")))
        return 3

    mint = sys.argv[1].strip()
    if not mint:
        print(json.dumps(_unavailable("empty token mint address")))
        return 3

    result = run_preflight(mint)
    print(json.dumps(result, indent=2))
    return {"ALLOW": 0, "WARN": 1, "BLOCK": 2, "UNAVAILABLE": 3}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
