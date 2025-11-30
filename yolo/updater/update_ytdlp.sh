#!/usr/bin/env bash

# Colors
CLR_BLUE='\033[94m'
CLR_RED='\033[91m'
CLR_GREEN='\033[92m'
CLR_YELLOW='\033[93m'
CLR_RESET='\033[0m'

# Python detection 
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo -e "${CLR_RED}Python not found. Cannot update yt-dlp.${CLR_RESET}"
    exit 1
fi

# Argument handling 
MODE="$1"   # "nightly" or empty

# Current version 
if command -v yt-dlp >/dev/null 2>&1; then
    CURRENT_VERSION="$(yt-dlp --version)"
else
    CURRENT_VERSION="not installed"
fi

echo -e "${CLR_BLUE}Updating yt-dlp...${CLR_RESET}"
echo -e "${CLR_YELLOW}Current version: ${CURRENT_VERSION}${CLR_RESET}\n"

# Update logic 
if [ "$MODE" = "nightly" ]; then
    echo -e "${CLR_BLUE}Installing yt-dlp nightly build...${CLR_RESET}\n"
    INSTALL_CMD="$PY -m pip install -U --force-reinstall \
https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/latest/download/yt-dlp.tar.gz"
else
    echo -e "${CLR_BLUE}Installing latest stable yt-dlp...${CLR_RESET}\n"
    INSTALL_CMD="$PY -m pip install -U yt-dlp"
fi

# Execute update 
if eval "$INSTALL_CMD"; then
    NEW_VERSION="$(yt-dlp --version 2>/dev/null)"
    echo -e "\n${CLR_GREEN}yt-dlp updated successfully!${CLR_RESET}"
    echo -e "${CLR_GREEN}New version: ${NEW_VERSION}${CLR_RESET}"
else
    echo -e "\n${CLR_RED}yt-dlp update failed.${CLR_RESET}"
    exit 1
fi