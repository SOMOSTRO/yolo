import argparse

def parse_cli_args(version):
  parser = argparse.ArgumentParser(
    prog="yodo",
    description="YODO — Universal Media Downloader",
    add_help=True,
    formatter_class=argparse.RawTextHelpFormatter
  )

  # Core flags
  parser.add_argument(
    "-d", "--debug",
    action="store_true",
    help="Enable debug mode (shows internal details)"
  )

  parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable verbose output"
  )

  parser.add_argument(
    "--download-dir",
    metavar="PATH",
    help="Set custom download directory"
  )

  # Version
  parser.add_argument(
    "--version",
    action="version",
    version=f"YODO version {version}"
  )

  return parser.parse_args()