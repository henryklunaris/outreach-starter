#!/usr/bin/env bash
# SessionStart hook: prints a daily accountability nudge into the Claude Code context.
# Reads .claude/state/user-profile.json (from /activate) and outreach.db for today's count.
# Never blocks. Fails open with a minimal message if anything is missing.
# Requires: python3 + jq in PATH. (jq is widely installed on macOS/Linux.)

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROFILE="$ROOT/.claude/state/user-profile.json"

# Read stdin so we don't back-pressure Claude Code. We don't actually use the event.
cat > /dev/null 2>&1 || true

# First-time branch: if the user profile doesn't exist, show onboarding instead of
# the daily accountability nudge. This prevents a fresh-clone student from seeing
# a confusing "0 / 100 sent today, hey friend" message before they even know what
# this repo does.
if [ ! -f "$PROFILE" ]; then
  read -r -d '' MSG <<'EOF' || true
Welcome to the VAIB Warm Outreach Starter.

Looks like this is your first time here, welcome!

Type /activate to get started!

After that, /outreach is your daily workflow. And /coach is always there if you get stuck or have a question.
EOF
  export MSG
  python3 -c 'import os, json; print(json.dumps({"continue": True, "systemMessage": os.environ.get("MSG", "")}))'
  exit 0
fi

# First name (fallback to "friend")
FIRST_NAME="friend"
if [ -f "$PROFILE" ] && command -v jq >/dev/null 2>&1; then
  NAME=$(jq -r '.user.first_name // empty' "$PROFILE" 2>/dev/null || true)
  if [ -n "$NAME" ] && [ "$NAME" != "null" ]; then FIRST_NAME="$NAME"; fi
fi

# Mindset completion check. If the profile exists but /mindset hasn't been run yet,
# surface a nudge instead of the full accountability board. The daily nudge leans
# on the student's own mindset words, so without them it's not doing its job.
MINDSET_DONE=""
if command -v jq >/dev/null 2>&1; then
  MINDSET_DONE=$(jq -r '.mindset.completed_at // empty' "$PROFILE" 2>/dev/null || true)
fi
if [ -z "$MINDSET_DONE" ] || [ "$MINDSET_DONE" = "null" ]; then
  read -r -d '' MSG <<EOF || true
Hey ${FIRST_NAME}, one step to finish onboarding.

You've got the voice profile saved, but the mindset lock-in hasn't been done yet. That's the back-and-forth where you say the 3 mindset shifts in your own words. It's the thing that makes the daily nudges actually land on you, because they'll echo your voice back, not mine.

Type /mindset whenever you're ready, takes about 10 minutes. Then /outreach for daily work.
EOF
  export MSG
  python3 -c 'import os, json; print(json.dumps({"continue": True, "systemMessage": os.environ.get("MSG", "")}))'
  exit 0
fi

# Today's counts (fallback to zero)
COUNTS_JSON="$(cd "$ROOT" && python3 -m outreach.cli count-today --json 2>/dev/null || echo '{"sent_today":0,"target":100,"added_today":0}')"
SENT=$(echo "$COUNTS_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('sent_today',0))" 2>/dev/null || echo 0)
TARGET=$(echo "$COUNTS_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('target',100))" 2>/dev/null || echo 100)

# Top 3 due follow-ups
DUE_JSON="$(cd "$ROOT" && python3 -m outreach.cli due-json 2>/dev/null || echo '{"due":[],"silent":[]}')"
DUE_LINES=$(echo "$DUE_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    items = (d.get('due') or []) + (d.get('silent') or [])
    names = []
    for i in items[:3]:
        n = i.get('name') or '?'
        names.append('  - ' + n)
    print('\n'.join(names) if names else '  (no one due, go message 3 new people)')
except Exception:
    print('  (tracker not initialized yet, run ./setup.sh if needed)')
")

# Mindset and Carnegie rotation by weekday
DAY=$(date +%u)  # 1-7
MINDSET_IDX=$(( (DAY - 1) % 3 ))
CARNEGIE_IDX=$(( (DAY - 1) % 6 ))

MINDSET_DEFAULTS=(
  "targets = anyone who knows your name, not just business owners"
  "you're not selling anything in msg one, the goal is referrals later"
  "actually pressing send is the hardest part, everything else is an excuse"
)

# Try to pull the user's own words if profile has mindset
MINDSET_KEYS=("targets" "selling" "hardest")
MINDSET_LINE="${MINDSET_DEFAULTS[$MINDSET_IDX]}"
if [ -f "$PROFILE" ] && command -v jq >/dev/null 2>&1; then
  K="${MINDSET_KEYS[$MINDSET_IDX]}"
  USER_LINE=$(jq -r --arg k "$K" '.mindset[$k] // empty' "$PROFILE" 2>/dev/null || true)
  if [ -n "$USER_LINE" ] && [ "$USER_LINE" != "null" ]; then
    MINDSET_LINE="$USER_LINE (your words)"
  fi
fi

CARNEGIE_LINES=(
  "make them feel important, sincerely, notice something real"
  "become genuinely interested in them, ask because you want to know"
  "listen, let them talk about themselves, ask a follow-up"
  "talk in terms of their interests, not yours"
  "honest, sincere appreciation, never flattery"
  "avoid criticism, judgment, and advice early on"
)
CARNEGIE_LINE="${CARNEGIE_LINES[$CARNEGIE_IDX]}"

# Realistic daily ceiling from availability. If the user set one in /activate,
# surface it alongside the Golden 100 so they see their actual ramp, not just
# the aspirational number.
REALISTIC_LINE=""
if command -v jq >/dev/null 2>&1; then
  MINS=$(jq -r '.availability.daily_minutes // empty' "$PROFILE" 2>/dev/null || true)
  if [ -n "$MINS" ] && [ "$MINS" != "null" ] && [ "$MINS" -gt 0 ] 2>/dev/null; then
    LOW=$(( MINS ))
    HIGH=$(( MINS * 3 / 2 ))
    REALISTIC_LINE="Realistic for your ~${MINS} min window today: ${LOW}-${HIGH} messages. Golden 100 is where you land once discovery calls are booking."
  fi
fi

# Build the system message
read -r -d '' MSG <<EOF || true

Hey ${FIRST_NAME}, daily warm-outreach check-in

Today: ${SENT} / ${TARGET} sent (first 10 are warm-up, then the Golden 100 until discovery calls land)
${REALISTIC_LINE}

Top 3 due:
${DUE_LINES}

Mindset for today: 
${MINDSET_LINE}

Nudge: ${CARNEGIE_LINE}

When stuck, type /coach and ask. when drafting, /outreach.
EOF

# Emit the hook JSON. continue=true so Claude proceeds normally.
export MSG
python3 -c 'import os, json; print(json.dumps({"continue": True, "systemMessage": os.environ.get("MSG", "")}))'
