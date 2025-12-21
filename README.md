# YOLO  
### Simple & Beginner-Friendly Media Downloader

## Introduction

`YOLO` is a simple and beginner-friendly command-line media downloader built on top of `yt-dlp`.

Its main goal is to make downloading videos and audio easy and understandable, especially for users who are new to the terminal. Instead of using long and complex yt-dlp commands, YOLO provides interactive prompts and clear output while handling common tasks automatically.

YOLO is designed for Termux and Linux systems, focusing on simplicity, reliability, and easy updates.

---

## Features

- *Video Downloading*
: Download videos in various resolutions and formats with interactive quality selection.

- *Audio Downloading*
: Extract audio only (MP3, M4A, etc.) with proper metadata support.

- *Beginner Friendly*
: No need to memorize yt-dlp commands — YOLO guides you step by step.

- *Colored Terminal Output*
: Clear, readable, and visually distinct messages for better understanding.

- *Customizable Downloads*
: Quality selection (low / medium / high / custom), Format selection (video/audio) and Codec-aware handling


- *Thumbnail & Metadata Embedding*
: Automatically embeds thumbnails and metadata when supported by the output format.

- *Subtitle Embedding*
: Download and embed subtitles (when available), container-aware (MP4 / MKV).

- *yt-dlp Extractor Challenge Handling*
: Uses Deno + EJS integration to help handle yt-dlp extractor challenges more reliably.

- *Easy Updates*
: Update YOLO via built-in updater and update yt-dlp separately when needed

---

## Notice

YOLO is currently **tested and developed primarily for the Termux environment**.

- Full compatibility is **not guaranteed on all Linux distributions**
- **Windows is not supported** at this time
- Some features may behave differently outside Termux due to system-level dependencies

*Support for additional platforms may be added in future releases as development continues.*

---

## Installation (Termux)

YOLO is designed to work best in the **Termux** environment on Android.

### 1. Install Termux

You must install Termux before proceeding.

Available sources:

- **GitHub (recommended)**:
  [https://github.com/termux/termux-app/releases](https://github.com/termux/termux-app/releases)

- **F-Droid (recommended)**:
  [https://f-droid.org/packages/com.termux/](https://f-droid.org/packages/com.termux/)

- **Play Store (not recommended)**:
  [Termux App](https://play.google.com/store/apps/details?id=com.termux)
  *The Play Store version is outdated and may cause issues.*

---

### 2. Grant Storage Permission (Important)

After installing Termux, open it and run:

```bash
termux-setup-storage
```

This step is **required** so YOLO and yt-dlp can save downloaded files.

*Accept the permission prompt when it appears.*

---

### 3. Install Git

```
# Termux
pkg update && pkg upgrade -y
pkg install -y git

# Ubuntu / Debian
sudo apt update
sudo apt install git

# Arch Linux
sudo pacman -S git
```

---

### 4. Install YOLO

After setting up Termux (or if you are on a supported Linux system), install YOLO using Git.

```bash
git clone https://github.com/somostro/yolo.git
cd yolo
bash install.sh
```

**What this does**:
* Clones the YOLO repository
* Installs required system dependencies (like ffmpeg)
* Installs required Python packages
* Sets up yt-dlp
* Configures the environment for running YOLO easily

*Follow any on-screen messages during installation.
Once completed, YOLO will be ready to use.*

---

## Usage

After installation, you can start YOLO by typing:

```bash
yolo
```

*YOLO will launch in interactive mode.*

**Basic usage**:
* Paste a video or audio URL and press Enter
* Choose the quality and format when prompted
* The download will start automatically

**Update**:
- To update YOLO and yt-dlp to the latest version:
- start YOLO, type:
  `update`

Type `cancel` to exit the program at any time
