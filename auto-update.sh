#!/usr/bin/env bash
# Auto-update the Nightly Stretching Routine app when the GitHub repo changes.
# Run from cron every few minutes (see README). Does nothing when up to date.
set -u
cd "$(dirname "$0")"

git fetch --quiet origin main || exit 0
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') update found, rebuilding..."
  if git pull --ff-only --quiet origin main && docker compose up -d --build; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') update done"
  else
    echo "$(date '+%Y-%m-%d %H:%M:%S') update FAILED — check docker / git state"
    exit 1
  fi
fi
