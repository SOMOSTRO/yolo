import subprocess
import sys
import shlex
from yodo.utils.colors import *
from yodo.utils.terminal_utils import center_title, print_crossline
from yodo.utils.version import get_version, get_channel

YODO_SCRIPT = "yodo/updater/update_yodo.sh"
YTDLP_SCRIPT = "yodo/updater/update_ytdlp.sh"

def update(command="update"):
  parts = command.lower().split()
  args = parts[1:]

  # defaults
  update_yodo = False
  update_ytdlp = False
  nightly = False

  # no arguments: update both (stable)
  if not args:
    update_yodo = True
    update_ytdlp = True
  else:
    for arg in args:
      if arg == "yodo":
        update_yodo = True
      elif arg == "yt-dlp":
        update_ytdlp = True
      elif arg == "nightly":
        nightly = True
      else:
        print(f"{CLR_ERROR}Unknown update argument: '{arg}'{CLR_RESET}")
        print("Usage: update [yodo] [yt-dlp] [nightly]")
        return

    # if nothing specified but args exist then invalid
    if not update_yodo and not update_ytdlp:
      print(f"{CLR_ERROR}Nothing to update.{CLR_RESET}")
      print("Usage: update [yodo] [yt-dlp] [nightly]")
      return

  # sanity checks
  if nightly and not update_ytdlp:
    print(f"{CLR_WARNING}Note: 'nightly' applies only to yt-dlp. Ignored for YODO.{CLR_RESET}")

  print(f"\n{CLR_BRIGHT_BLUE}Starting update process...{CLR_RESET}")

  # update YODO
  if update_yodo:
    print(center_title(f"{CLR_BRIGHT_GREEN}YODO{CLR_RESET}"))
    print(f"Current YODO version: {CLR_YELLOW}{get_version()} ({get_channel()}){CLR_RESET}")
    print(f"{CLR_BRIGHT_GREEN}• Updating YODO...{CLR_RESET}")
    
    _run_script(YODO_SCRIPT)
    
    print(f"Updated YODO version: {CLR_GREEN}{get_version()} ({get_channel()}){CLR_RESET}")
    print(print_crossline())
    print()

  # update yt-dlp
  if update_ytdlp:
    print(center_title(f"{CLR_BRIGHT_GREEN}YT-DLP{CLR_RESET}"))
    print(f"{CLR_BRIGHT_GREEN}• Updating yt-dlp ({'nightly' if nightly else 'stable'})...{CLR_RESET}")
    args = ["--nightly"] if nightly else []
    _run_script(YTDLP_SCRIPT, args)
    print(print_crossline())
    print()

  print(f"{CLR_BRIGHT_GREEN}Update process finished.{CLR_RESET}")
  print(f"{CLR_BRIGHT_GREEN}Start {CLR_BOLD}yodo{CLR_RESET_BOLD} again to experience the new version.{CLR_RESET}\n")
  print("Exiting...")
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
