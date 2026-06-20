"""
Live demo: RugBuster Shield in action.

Run with: python demo/shield_demo.py
"""

import os
import sys


sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"),
)

from shield import RugBusterBlocked, guarded


# Placeholder swap function - represents a real Jupiter/swap call.
# It must NEVER print "EXECUTING SWAP" unless Shield actually let it through.
@guarded(get_mint=lambda mint, amount: mint)
def jupiter_swap(mint, amount):
    print(f"   >>> EXECUTING SWAP: {amount} SOL -> {mint}")
    return "swap_tx_signature_placeholder"


def try_swap(label, mint, amount=1.0):
    print(f"\n--- Attempting swap: {label} ---")
    print(f"Mint: {mint}")
    try:
        result = jupiter_swap(mint, amount)
        print(f"RESULT: swap executed successfully -> {result}")
    except RugBusterBlocked as error:
        print(f"RESULT: BLOCKED - {error}")


if __name__ == "__main__":
    print("=" * 60)
    print("RugBuster Shield - Live Demo")
    print("=" * 60)

    try_swap(
        "Known GOOD token (USDC)",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    )
    try_swap(
        "Known DANGER token (real flagged rug)",
        "4RA7u9YP5ShPHBCURXq9w4BU5fPyJfnoZQxr64iFpump",
    )
