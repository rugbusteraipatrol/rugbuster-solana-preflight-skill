"""Code-level enforcement for actions protected by RugBuster preflight."""

from functools import wraps

try:
    from .preflight_scan import run_preflight
except ImportError:  # Support direct imports when skill/scripts is on sys.path.
    from preflight_scan import run_preflight


class RugBusterBlocked(Exception):
    """Raised when a guarded action is blocked by RugBuster Shield."""

    def __init__(self, verdict_result: dict):
        self.verdict_result = verdict_result
        super().__init__(
            f"Blocked by RugBuster Shield: verdict={verdict_result.get('verdict')} "
            f"reason={verdict_result.get('reason')}"
        )


def run_protected(mint: str, action_fn, *args, confirmed: bool = False, **kwargs):
    """
    Run action_fn(*args, **kwargs) ONLY if the preflight verdict allows it.

    ALLOW proceeds immediately. WARN requires the caller to pass exactly
    confirmed=True. BLOCK, UNAVAILABLE, and unknown verdicts fail closed.
    """
    verdict_result = run_preflight(mint)
    verdict = verdict_result.get("verdict")

    if verdict == "ALLOW":
        return action_fn(*args, **kwargs)
    if verdict == "WARN" and confirmed is True:
        return action_fn(*args, **kwargs)

    raise RugBusterBlocked(verdict_result)


def guarded(get_mint):
    """Decorate an action and enforce RugBuster preflight before invocation."""

    def decorator(action_fn):
        @wraps(action_fn)
        def protected_action(*args, **kwargs):
            confirmed = kwargs.pop("confirmed", False)
            mint = get_mint(*args, **kwargs)
            return run_protected(
                mint,
                action_fn,
                *args,
                confirmed=confirmed,
                **kwargs,
            )

        return protected_action

    return decorator
