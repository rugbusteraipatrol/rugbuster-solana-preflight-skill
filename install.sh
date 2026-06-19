#!/usr/bin/env bash
set -euo pipefail

echo "Installing RugBuster Solana Preflight Skill..."

TARGET_DIR="${1:-.}"

mkdir -p "$TARGET_DIR/.claude/skills/rugbuster-preflight"
cp -r skill/* "$TARGET_DIR/.claude/skills/rugbuster-preflight/"

mkdir -p "$TARGET_DIR/.claude/agents"
cp agents/preflight-guardian.md "$TARGET_DIR/.claude/agents/"

mkdir -p "$TARGET_DIR/.claude/commands"
cp commands/preflight-check.md "$TARGET_DIR/.claude/commands/"

echo "Done. Restart Claude Code to pick up the new skill."
echo "Optional: set RUGBUSTER_API_BASE env var to override the default API URL."
