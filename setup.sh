#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "VAIB Warm Outreach Starter, setup"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.10+ first."
  exit 1
fi

if ! python3 -c "import typer" >/dev/null 2>&1; then
  echo "Installing typer..."
  python3 -m pip install --user --quiet typer
fi

python3 -m outreach.db
echo "SQLite DB ready at ./outreach.db"
echo ""
echo "Done. Open this folder in Claude Code:"
echo "  cd $(pwd) && claude"
echo ""
echo "First time: type /activate (one-time onboarding, about 10 min)"
echo "Then daily: type /outreach"
