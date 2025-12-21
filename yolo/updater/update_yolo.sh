#!/usr/bin/env bash

set -e

ok()   { echo -e "[\e[32mOK\e[0m]  $1"; }
info() { echo -e "[\e[34mINFO\e[0m] $1"; }
warn() { echo -e "[\e[33mWARN\e[0m] $1"; }
fail() { echo -e "[\e[31mFAIL\e[0m] $1"; exit 1; }

# updater/ → yolo/ → repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YOLO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$YOLO_ROOT" || exit 1

info "Checking YOLO installation..."

if [ ! -d ".git" ]; then
  fail "YOLO is not installed via git, update cannot continue."
  exit 1
fi

info "Checking for local modifications..."
# check if working tree is dirty
if [ -n "$(git status --porcelain)" ]; then
  echo ""
  warn "You have modified YOLO source files locally."
  warn "If you continue, all your local changes will be PERMANENTLY LOST."
  echo ""
  printf "Do you want to continue updating? (y/n): "
  read choice
  
  if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
    fail "Update aborted by user."
    exit 1
  fi
  
  # Backup local changes
  backup="$HOME/yolo_local_changes_$(date +%Y%m%d_%H%M%S).patch"
  info "Backing up user changes to '$backup'"
  git diff > "$backup"
else
  ok "Working tree is clean."
fi

echo ""

info "Fetching latest changes..."
git fetch origin # download latest changes

info "Forcing updates..."
git reset --hard origin/main # overwrite all local changes
git clean -fd # deletes untracked files&folders

ok "YOLO update completed"
