#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
YOLO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$YOLO_ROOT" || exit 1

echo "🔍 Checking YOLO installation..."

if [ ! -d ".git" ]; then
  echo "❌ YOLO is not installed via git"
  echo "❌ Update cannot continue"
  exit 1
fi

echo "📡 Fetching latest changes..."
git fetch origin

echo "⬇️ Pulling updates..."
git pull origin main

echo "✅ YOLO update completed"