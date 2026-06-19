"""Safety and contract tests for the Solana preflight scanner."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))

import preflight_scan as ps


def api_result(label="GOOD", risk_score=5, **overrides):
    result = {
        "ok": True,
        "address": "FAKE_MINT",
        "chain": "solana",
        "label": label,
        "risk_score": risk_score,
        "rugcheck_score": 1,
        "risk_flags": [],
        "source": "postgres_cache",
    }
    result.update(overrides)
    return result


def test_good_low_score_is_allow(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, api_result()))
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "ALLOW"


def test_danger_label_is_block(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, api_result("DANGER", 55)))
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "BLOCK"


def test_high_score_is_block_even_with_good_label(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, api_result("GOOD", 85)))
    assert ps.run_preflight("FAKE_MINT")["verdict"] == "BLOCK"


def test_warn_label_is_warn(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, api_result("WARN", 20)))
    assert ps.run_preflight("FAKE_MINT")["verdict"] == "WARN"


def test_cache_miss_is_warn_never_allow(monkeypatch):
    miss = api_result(
        "UNKNOWN",
        None,
        source="cache_miss",
        risk_flags=["not_in_intelligence_db"],
        rugcheck_score=None,
    )
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, miss))
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "WARN"
    assert result["verdict"] != "ALLOW"
    assert "unverified" in result["reason"]


def test_http_400_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: (400, {"ok": False, "error": "invalid solana mint address"}),
    )
    result = ps.run_preflight("0xBAD")
    assert result["verdict"] == "UNAVAILABLE"
    assert result["reason"] == "invalid solana mint address"


def test_api_down_is_unavailable_never_allow(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (None, None))
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "UNAVAILABLE"
    assert result["verdict"] != "ALLOW"


def test_malformed_json_shape_is_unavailable(monkeypatch):
    monkeypatch.setattr(ps, "_fetch_json", lambda url: (200, {"ok": True}))
    assert ps.run_preflight("FAKE_MINT")["verdict"] == "UNAVAILABLE"


def test_db_error_is_unavailable(monkeypatch):
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: (503, {"ok": False, "error": "database unavailable", "source": "db_error"}),
    )
    assert ps.run_preflight("FAKE_MINT")["verdict"] == "UNAVAILABLE"


def test_uses_new_address_endpoint(monkeypatch):
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return 200, api_result()

    monkeypatch.setattr(ps, "_fetch_json", fake_fetch)
    ps.run_preflight("FAKE_MINT")
    assert seen["url"] == (
        "https://rugbuster-solana-api-production.up.railway.app/score"
        "?address=FAKE_MINT"
    )


def test_missing_argument_returns_unavailable_exit_code(capsys):
    old_argv = sys.argv
    sys.argv = ["preflight_scan.py"]
    try:
        code = ps.main()
    finally:
        sys.argv = old_argv
    assert code == 3
