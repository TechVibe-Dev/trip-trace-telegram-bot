#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

log() {
    echo "[start.sh] $1"
}

create_venv_if_missing() {
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating virtual environment in $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    else
        log "Virtual environment already exists, skipping creation"
    fi
}

install_dependencies() {
    log "Installing dependencies from requirements.txt"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet -r requirements.txt
}

run_bot() {
    log "Starting bot.py"
    "$VENV_DIR/bin/python" bot.py
}

main() {
    create_venv_if_missing
    install_dependencies
    run_bot
}

main
