# RugBuster Shield

RugBuster Shield is a code-level guard for a Solana swap, sign, transfer, or
other action function. It completes preflight before invoking the action.

Once an integration routes its swap/sign call through `rugbuster_shield`, that
call cannot execute on a failing verdict: the action function is never invoked.
It does not prevent an integration from bypassing the wrapper entirely by
calling its own swap logic directly instead of adopting the pattern. No library
can force adoption.

## Example

```python
from skill.scripts.shield import guarded, RugBusterBlocked


@guarded(get_mint=lambda mint, amount_sol: mint)
def jupiter_swap(mint, amount_sol):
    # Placeholder: a real integration would call Jupiter's swap API here.
    return f"swapped {amount_sol} SOL for {mint}"


try:
    result = jupiter_swap("SomeMintAddress...", 1.0)
except RugBusterBlocked as error:
    print(f"Swap refused: {error}")
```

`ALLOW` invokes the wrapped action. `WARN` remains blocked unless the caller
passes `confirmed=True` explicitly, modeling that the user acknowledged the
risk. `BLOCK` and `UNAVAILABLE` never invoke it, even with confirmation.

```python
jupiter_swap("SomeMintAddress...", 1.0, confirmed=True)
```
