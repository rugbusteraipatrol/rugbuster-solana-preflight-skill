"""Tests for the code-level RugBuster Shield enforcement wrapper."""

import os
import sys
from unittest.mock import Mock

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))

import shield


def verdict(name):
    return {"verdict": name, "reason": f"test_{name.lower()}"}


def test_run_protected_allow_calls_action_and_returns_value(monkeypatch):
    action = Mock(return_value="signature")
    monkeypatch.setattr(shield, "run_preflight", lambda _mint: verdict("ALLOW"))

    result = shield.run_protected("MINT", action, 7, memo="safe")

    assert result == "signature"
    action.assert_called_once_with(7, memo="safe")


def test_run_protected_warn_without_confirmation_never_calls_action(monkeypatch):
    action = Mock()
    monkeypatch.setattr(shield, "run_preflight", lambda _mint: verdict("WARN"))

    with pytest.raises(shield.RugBusterBlocked) as raised:
        shield.run_protected("MINT", action)

    action.assert_not_called()
    assert raised.value.verdict_result["verdict"] == "WARN"


def test_run_protected_warn_with_explicit_confirmation_calls_action(monkeypatch):
    action = Mock(return_value="confirmed")
    monkeypatch.setattr(shield, "run_preflight", lambda _mint: verdict("WARN"))

    assert shield.run_protected("MINT", action, confirmed=True) == "confirmed"
    action.assert_called_once_with()


@pytest.mark.parametrize("blocked_verdict", ["BLOCK", "UNAVAILABLE"])
def test_run_protected_hard_failure_never_calls_action_even_if_confirmed(
    monkeypatch, blocked_verdict
):
    action = Mock()
    monkeypatch.setattr(
        shield, "run_preflight", lambda _mint: verdict(blocked_verdict)
    )

    with pytest.raises(shield.RugBusterBlocked):
        shield.run_protected("MINT", action, confirmed=True)

    action.assert_not_called()


def test_run_protected_unknown_verdict_fails_closed(monkeypatch):
    action = Mock()
    monkeypatch.setattr(shield, "run_preflight", lambda _mint: verdict("MYSTERY"))

    with pytest.raises(shield.RugBusterBlocked):
        shield.run_protected("MINT", action, confirmed=True)

    action.assert_not_called()


@pytest.mark.parametrize(
    ("preflight_verdict", "confirmed", "should_call"),
    [
        ("ALLOW", False, True),
        ("WARN", False, False),
        ("WARN", True, True),
        ("BLOCK", False, False),
        ("BLOCK", True, False),
        ("UNAVAILABLE", False, False),
        ("UNAVAILABLE", True, False),
    ],
)
def test_guarded_matches_run_protected_semantics(
    monkeypatch, preflight_verdict, confirmed, should_call
):
    action = Mock(return_value="done")

    @shield.guarded(get_mint=lambda mint, amount: mint)
    def swap(mint, amount):
        return action(mint, amount)

    monkeypatch.setattr(
        shield, "run_preflight", lambda _mint: verdict(preflight_verdict)
    )

    if should_call:
        assert swap("MINT", 1.5, confirmed=confirmed) == "done"
        action.assert_called_once_with("MINT", 1.5)
    else:
        with pytest.raises(shield.RugBusterBlocked):
            swap("MINT", 1.5, confirmed=confirmed)
        action.assert_not_called()


def test_verdict_check_completes_before_action_side_effect(monkeypatch):
    events = []
    action = Mock(side_effect=lambda: events.append("action"))

    def blocked_preflight(_mint):
        events.append("preflight")
        return verdict("BLOCK")

    monkeypatch.setattr(shield, "run_preflight", blocked_preflight)

    with pytest.raises(shield.RugBusterBlocked):
        shield.run_protected("MINT", action)

    assert events == ["preflight"]
    action.assert_not_called()
