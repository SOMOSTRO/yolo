import subprocess
import sys
import shlex
from yolo.utils.colors import *
from yolo.utils.terminal_utils import print_title, print_crossline
from yolo.utils.version import get_version, get_channel

YOLO_SCRIPT = "yolo/updater/update_yolo.sh"
YTDLP_SCRIPT = "yolo/updater/update_ytdlp.sh"

def update(command: str):
  parts = command.lower().split()
  args = parts[1:]

  # defaults
  update_yolo = False
  update_ytdlp = False
  nightly = False

  # no arguments: update both (stable)
  if not args:
    update_yolo = True
    update_ytdlp = True
  else:
    for arg in args:
      if arg == "yolo":
        update_yolo = True
      elif arg == "yt-dlp":
        update_ytdlp = True
      elif arg == "nightly":
        nightly = True
      else:
        print(f"{CLR_ERROR}Unknown update argument: '{arg}'{CLR_RESET}")
        print("Usage: update [yolo] [yt-dlp] [nightly]")
        return

    # if nothing specified but args exist then invalid
    if not update_yolo and not update_ytdlp:
      print(f"{CLR_ERROR}Nothing to update.{CLR_RESET}")
      print("Usage: update [yolo] [yt-dlp] [nightly]")
      return

  # sanity checks
  if nightly and not update_ytdlp:
    print(f"{CLR_WARNING}Note: 'nightly' applies only to yt-dlp. Ignored for YOLO.{CLR_RESET}")

  print(f"\n{CLR_BRIGHT_BLUE}Starting update process...{CLR_RESET}")

  # update YOLO
  if update_yolo:
    print_title(f"{CLR_BRIGHT_GREEN}YOLO{CLR_RESET}")
    print(f"Current YOLO version: {CLR_YELLOW}{get_version()} ({get_channel()}){CLR_RESET}")
    print(f"{CLR_BRIGHT_GREEN}• Updating YOLO...{CLR_RESET}")
    
    _run_script(YOLO_SCRIPT)
    
    print(f"Updated YOLO version: {CLR_GREEN}{get_version()} ({get_channel()}){CLR_RESET}")
    print(print_crossline("–"))

  # update yt-dlp
  if update_ytdlp:
    print_title(f"{CLR_BRIGHT_GREEN}YT-DLP{CLR_RESET}")
    print(f"{CLR_BRIGHT_GREEN}• Updating yt-dlp ({'nightly' if nightly else 'stable'})...{CLR_RESET}")
    args = ["--nightly"] if nightly else []
    _run_script(YTDLP_SCRIPT, args)
    print(print_crossline("–"))

  print(f"\n{CLR_BRIGHT_GREEN}Update process finished.{CLR_RESET}")
  print("Exiting...")
  print(f"\n({CLR_BRIGHT_GREEN}Type {CLR_BOLD}yolo{CLR_RESET_BOLD} again to enjoy the new version...{CLR_RESET})")
  sys.exit()


def _run_script(script_path, args=None):
  try:
    cmd = ["bash", script_path]
    if args:
      cmd.extend(args)

    subprocess.run(
      cmd,
      check=True
    )
  except FileNotFoundError:
    print(f"{CLR_ERROR}Update script not found: {script_path}{CLR_RESET}")
  except subprocess.CalledProcessError:
    print(f"{CLR_ERROR}Update failed while running {script_path}{CLR_RESET}")