"""
Tests for preflight_scan.py.

Run with: python -m pytest tests/test_preflight_scan.py -v

These tests use monkeypatched _fetch_json so no network calls are made.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))

import preflight_scan as ps


def test_allow_on_low_score(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: {"rug_score": 5, "rugcheck_score": 95, "flags": [], "verdict_label": "clean"},
    )
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "ALLOW"


def test_warn_on_mid_score(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: {"rug_score": 30, "rugcheck_score": 60, "flags": ["mutable_metadata"], "verdict_label": "caution"},
    )
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "WARN"


def test_block_on_high_score(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: {"rug_score": 80, "rugcheck_score": 10, "flags": [], "verdict_label": "high risk"},
    )
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "BLOCK"


def test_block_on_critical_flag_even_with_low_score(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: {
            "rug_score": 5,
            "rugcheck_score": 90,
            "flags": ["deployer_flagged_prior_rug"],
            "verdict_label": "clean-looking but flagged deployer",
        },
    )
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "BLOCK"


def test_unavailable_on_network_failure(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(ps, "_fetch_json", lambda url: None)
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "UNAVAILABLE"


def test_unavailable_never_silently_becomes_allow(monkeypatch):
    """Critical security property: API down must never map to ALLOW."""
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(ps, "_fetch_json", lambda url: None)
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] != "ALLOW"
    assert result["verdict"] == "UNAVAILABLE"


def test_malformed_response_is_unavailable(monkeypatch):
    monkeypatch.setattr(ps, "_try_native_preflight", lambda token: None)
    monkeypatch.setattr(
        ps,
        "_fetch_json",
        lambda url: {"flags": []},  # missing rug_score entirely
    )
    result = ps.run_preflight("FAKE_MINT")
    assert result["verdict"] == "UNAVAILABLE"


def test_missing_argument_returns_unavailable_exit_code(capsys):
    old_argv = sys.argv
    sys.argv = ["preflight_scan.py"]
    try:
        code = ps.main()
    finally:
        sys.argv = old_argv
    assert code == 3
