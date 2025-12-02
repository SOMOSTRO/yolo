#!/usr/bin/env bash

set -e

ok()   { echo -e "[\e[32mOK\e[0m]  $1"; }
info() { echo -e "[\e[34mINFO\e[0m] $1"; }
fail() { echo -e "[\e[31mFAIL\e[0m] $1"; exit 1; }

# updater/ → yolo/ → repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YOLO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$YOLO_ROOT" || exit 1

info "Checking YOLO installation..."

if [ ! -d ".git" ]; then
  fail "YOLO is not installed via git, update cannot continue."
fi

info "Fetching latest changes..."
git fetch origin

info "Pulling updates..."
git pull origin main

ok "YOLO update completed"