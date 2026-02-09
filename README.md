# YODO  
### Simple & Beginner-Friendly Media Downloader

## Introduction

`YODO` is a simple and beginner-friendly command-line media downloader built on top of `yt-dlp`.

Its main goal is to make downloading videos and audio easy and understandable, especially for users who are new to the terminal. Instead of using long and complex yt-dlp commands, YODO provides interactive prompts and clear output while handling common tasks automatically.

YODO is designed for Termux and Linux systems, focusing on simplicity, reliability, and easy updates.

---

## Features

- **Video Downloading**  
  Download videos in various resolutions and formats with interactive quality selection.

- **Audio Downloading**  
  Extract audio only (MP3, M4A, etc.) with proper metadata support.

- **Beginner Friendly**  
  No need to memorize yt-dlp commands — YODO guides you step by step.

- **Colored Terminal Output**  
  Clear, readable, and visually distinct messages for better understanding.

- **Customizable Downloads**  
  Quality selection (low / medium / high / custom), Format selection (video/audio) and Codec-aware handling

- **Thumbnail & Metadata Embedding**  
  Automatically embeds thumbnails and metadata when supported by the output format.

- **Subtitle Embedding**  
  Download and embed subtitles (when available), container-aware (MP4 / MKV).

- **yt-dlp Extractor Challenge Handling**  
  Uses Deno + EJS integration to help handle yt-dlp extractor challenges more reliably.

- **Easy Updates**  
  Update YODO via built-in updater and update yt-dlp separately when needed

---

## Notice

YODO is currently **tested and developed primarily for the Termux environment**.

- Full compatibility is **not guaranteed on all Linux distributions**
- **Windows is not supported** at this time
- Some features may behave differently outside Termux due to system-level dependencies

*Support for additional platforms may be added in future releases as development continues.*

---

## Installation (Termux)

YODO is designed to work best in the **Termux** environment on Android.

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

This step is **required** so YODO and yt-dlp can save downloaded files.

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

### 4. Install YODO

After setting up Termux (or if you are on a supported Linux system), install YODO using Git.

```bash
git clone https://github.com/somostro/yodo.git
cd yodo
bash install.sh
```

**What this does**:
* Clones the YODO repository
* Installs required system dependencies (like ffmpeg)
* Installs required Python packages
* Sets up yt-dlp
* Configures the environment for running YODO easily

*Follow any on-screen messages during installation.
Once completed, YODO will be ready to use.*

---

## Usage

### Quick Start

```bash
yodo
```

Or from the project directory:

```bash
./run.sh
```

*YODO will launch in interactive mode.*

---

## Interactive Mode (Default)

This is the **recommended and simplest way** to use YODO.

### Basic usage

1. Start YODO
2. Paste a media URL and press Enter
3. Choose quality and format when prompted
4. Download starts automatically

You can type `cancel` at any time to exit the program.

---

### Special Command: `update`

You can use the `update` keyword **instead of entering a URL**.

**Usage:**

```bash
update [yodo] [yt-dlp] [nightly]
```

**Examples:**

- `update`  
  → Update both YODO and yt-dlp (stable)

- `update yodo`  
  → Update only YODO

- `update yt-dlp`  
  → Update only yt-dlp (stable)

- `update yt-dlp nightly`  
  → Install yt-dlp nightly build

---

## CLI Mode (Command-Line Arguments)

YODO supports optional CLI arguments for advanced usage.

### Usage

```bash
yodo [-h] [-d] [-v] [--download-dir PATH] [--version]
```

### Available options

- `-h, --help`  
→ Show help message and exit

- `-d, --debug`  
→ Enable debug mode (shows internal details)

- `-v, --verbose`  
→ Enable verbose output

- `--download-dir PATH`  
→ Set a custom download directory

- `--version`  
→ Show program version and exit

- `-U, --update`  
→ Update YODO and yt-dlp (stable), then exit

**Note:**  

- Debug mode automatically enables verbose output.
- CLI arguments customize YODO behavior but do not replace the interactive download flow.

---

## Environment Variables

YODO supports inline environment variables.

### Supported variables

- `DOWNLOAD_DIR`  
Set the base download directory

### Default download directories

- **Android (Termux)**  
→ "*/storage/emulated/0/YODO/*"

- **Linux**  
→ "*$HOME/YODO/*"

### Directory structure

**All downloads are organized automatically:**  

> YODO/  
├── audio/  
└── video/  

**Examples:**  
- "/storage/emulated/0/YODO/audio/..."
- "/storage/emulated/0/YODO/video/..."

**Priority order:**  
- *CLI arguments > Environment variables > Defaults*

---

## Download Directory Resolution

YODO safely resolves the download directory based on platform:

- **Android (Termux)**  
  - Relative paths → /storage/emulated/0/<path>

- **Linux**  
  - Relative paths → $HOME/<path>

### Important behavior

- Invalid or restricted paths are rejected with a clear warning

- The YODO project directory itself cannot be used as a download location

- This prevents:
  - Accidental data loss during updates
  - Permission issues
  - Broken installations

---

## Examples

### Start YODO (interactive mode)

```bash
yodo
```

### Use custom download directory (CLI)

```bash
yodo --download-dir Download
```

### Use environment variable

```bash
DOWNLOAD_DIR="YouTube_Downloads" yodo
```

### Enable debug mode

```bash
yodo -d
```

---

## Configuration & Behavior Notes

### 1. Why is the project directory protected?

*YODO updates itself using a forced Git reset. Any files inside the project directory may be **deleted during updates.***

**To protect user data:**

- Downloads are **never allowed** inside the YODO project folder

### 2. Why Windows is not supported?

**YODO is developed and tested primarily for:**  

- Termux (Android)
- Linux

*As a developer, Windows access for development and testing is limited, and most users run YODO in Termux or Linux environments.*  

Windows support may be added in future releases.

### 3. Why are relative paths redirected?

**This ensures:**  

- Safe storage access on Android
- Predictable behavior across platforms
- No accidental writes to restricted locations

---

## Troubleshooting

### 1. Storage permission issues (Termux)

**Run:**  

```bash
termux-setup-storage
```

Restart Termux afterward.

### 2. YouTube throttling or temporary bans

**If downloads fail or slow down:**  

- Use a trusted VPN
- Wait before retrying
- Avoid excessive repeated requests

### 3. yt-dlp extractor errors

**These are usually site-specific issues. Try:**  

- Updating yt-dlp (`update yt-dlp`)
- Waiting for upstream fixes

---

## FAQ

### 1. Where are my downloads saved?

By default, downloads are saved in the **YODO directory** based on your platform:

- **Android (Termux)**  
  `/storage/emulated/0/YODO/`

- **Linux**  
  `$HOME/YODO/`

Inside this directory, YODO automatically organizes files:

- **Audio files** → `.../audio/`
- **Video files** → `.../video/`

**Example paths:**

- "/storage/emulated/0/YODO/audio/Song.opus"
- "/storage/emulated/0/YODO/video/Video.mp4"

*If you provide a custom download directory (via CLI or environment variable), the same `audio/` and `video/` structure will be created inside that directory.*

### 2. Can I pass cookies to yt-dlp?

No. Cookie support is intentionally skipped due to limitations in Android (Termux).

### 3. Does YODO track or collect data?

No. YODO runs entirely locally.

---

## Notes & Limitations

- Windows is not supported
- Some Linux distributions may behave differently
- YODO does not expose low-level or advanced yt-dlp options
- Cookie-based authentication is not available
- DRM-protected content cannot be downloaded

---

## Final Notes

**YODO focuses on:**  

- Simplicity
- Safety
- Performance
- Beginner accessibility

*Advanced features are exposed without sacrificing clarity.*