#!/usr/bin/env bash
# Creates the virtualenv if missing, installs dependencies and runs the bot.
set -euo pipefail

VENV_DIR=".venv"

log() {
    echo "[start.sh] $1"
}

if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

log "Installing dependencies from requirements.txt"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r requirements.txt

log "Starting the bot"
exec "$VENV_DIR/bin/python" -m trip_trace_bot
