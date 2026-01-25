import os
import sys
import time
# import re
# import shlex
# import importlib
# from threading import Thread

# benchmark for debugging
_perf_startup_time_start = time.perf_counter()

# YODO built-in modules/functions
from yodo.utils.colors import * # import required on top level

# set environment variables
os.environ["YTDLP_REMOTE_COMPONENTS"] = "ejs:github"
os.environ["YTDLP_JS_RUNTIME"] = "deno"


# to go back to previous line, move up 1 line
move_up_1_line = "\x1b[1A"

# Default configuration
DEBUG = False
VERBOSE = False
DOWNLOAD_DIR = None
VERSION = "1.2.1"

# var for tracking loader
is_info_loaded = False

# Global var for final filename
FINAL_FILENAME = None
FINAL_TITLE = None # filename without ext
FINAL_EXT = None


# function to print program banner/logo
def PRINT_LOGO():
  """Print YODO banner"""
  
  _1 = '\033[38;2;255;153;204m'  # Pink
  _2 = '\033[38;2;230;153;230m'  # Soft Violet
  _3 = '\033[38;2;204;153;255m'  # Violet
  _4 = '\033[38;2;153;153;255m'  # Periwinkle
  _5 = '\033[38;2;153;204;255m'  # Sky Blue
  _6 = '\033[38;2;153;220;255m'  # Soft Cyan
  
  print(fr"""{CLR_BOLD}
  {_1}__     __ ____   _____    ____  
  {_2}\ \   / // __ \ |  __ \  / __ \ 
  {_3} \ \_/ /| |  | || |  | || |  | |
  {_4}  \   / | |  | || |  | || |  | |
  {_5}   | |  | |__| || |__| || |__| |
  {_6}   |_|   \____/ |_____/  \____/  {CLR_RESET}Version: {VERSION}
  """)

# print_space
def p_s(count, char = " "):
  """Returns number of spaces (char)."""
  return char * int(count)

# function for convert bytes to human-readable MB/GB string.
def get_size_str(size_bytes):
  """Convert bytes to human-readable MB/GB string."""
  if not size_bytes:
    return "Unknown"
  size_mb = size_bytes / (1024*1024)
  if size_mb < 1024:
    size = f"{size_mb:.2f} MB"
  else:
    size = f"{size_mb/1024:.2f} GB"
  return f"{CLR_LIME}{size}{CLR_RESET}"

# function to convert acodec to ext
def codec_to_ext(acodec):
  """Map yt-dlp audio codecs to common file extensions"""
  mapping = {
    "opus": "opus", # WebM/Opus extracted → .opus
    "vorbis": "ogg", # Legacy format → .ogg
    "mp4a.40.2": "m4a", # AAC inside MP4 → .m4a
    "aac": "m4a", # raw AAC format inside m4a container
    "mp3": "mp3", # Direct MP3
    "flac": "flac", # FLAC
    "alac": "m4a", # ALAC usually in M4A container
    "ac3": "ac3",
    "eac3": "eac3",
    "wav": "wav", # PCM/WAVE
  }
  return mapping.get(acodec, "m4a")  # default safe fallback

# function for displaying loader for fetch media information
def display_fetch_loader():
  """Display a loading indicator while video information is being fetched."""
  
  print(f"{CLR_BRIGHT_BLUE}{CLR_ITALIC}Fetching media information", end='', flush=True)
  dots = 0
  while not is_info_loaded:
    time.sleep(.5)
    print(".", end='', flush=True)
    dots += 1
    if dots >= 3:
      time.sleep(.5)
      print(f"\b\b\b   \b\b\b", end='', flush=True)
      dots = 0
  print(f"{'\b'*dots + ' '*dots + '\b'*dots}{CLR_RESET}", end='\t', flush=True)
  
def sanitize_filename(title, max_bytes=240):
  """
  Sanitize a string for safe use as a filename.

  This function:
  - Normalizes Unicode characters to NFKC form to fix inconsistent encodings.
  - Replaces characters that are unsafe for filenames (e.g., / \\ : * ? " < > | #) with underscores.
  - Collapses multiple spaces into a single space and trims leading/trailing whitespace.
  - Truncates the filename to maximum bytes to avoid filesystem limits (240 is safe for most FS, 255 - some room for extension and other FS specific characters.
  - Applies yt-dlp's internal filename sanitization for additional safety.

  Args:
      title (str): The input string to be converted into a safe filename.
      max_bytes (int, optional): Maximum byte length of the filename. Defaults to 240.

  Returns:
      str: A sanitized, filesystem-safe filename string.
  """
  
  if DEBUG:
    sfn_start = time.perf_counter()
  
  # Normalize unicode
  title = unicodedata.normalize("NFKC", title)
  
  # Replace unsafe filename characters
  unsafe_chars = r'[\/:*?"<>|#]'
  title = re.sub(unsafe_chars, "_", title)
  
  # Collapse multiple spaces into one
  title = re.sub(r'\s+', ' ', title).strip()

  # Enforce max filename byte limit
  # Encode the title to bytes
  encoded_title = title.encode('utf-8')
  
  # Truncate the byte array
  if len(encoded_title) > max_bytes:
    truncated_bytes = encoded_title[:max_bytes]
    
    # Decode truncated bytes (skip any incomplete multi-byte sequence at the end)
    title = truncated_bytes.decode('utf-8', errors='ignore')
    
  # Remove trailing "." (dots), " " (whitespaces) and "_" (underscores)
  title = title.strip("._ ")
  
  # Return placeholder if title is empty
  if not title: return "media"
  
  # Using yt_dlp sanitize_filename function
  title = _ytdlp_sanitize(title)
  
  if DEBUG:
    print(f"{CLR_DIM}[debug] sanitized filename: {title}")
    print(f"[perf] Filename sanitization: {(time.perf_counter()-sfn_start)*1000:.2f} ms{CLR_RESET}")
  
  # return sanitized file name
  return title

def resolve_download_dir(cli_dir = None):
  """
  Resolve and validate the download directory.

  Rules:
  - Absolute paths are respected
  - '~' is expanded
  - Relative paths are redirected to platform-safe base directory
  - Project root is never used for downloads
  """
  
  PROJECT_ROOT = os.path.abspath(".")
  
  def normalize(path):
    return os.path.abspath(os.path.expanduser(path))

  def is_inside_project(path):
    return os.path.commonpath([path, PROJECT_ROOT]) == PROJECT_ROOT

  # Platform detection
  is_termux = (
    os.getenv("PREFIX") is not None or
    os.path.exists("/data/data/com.termux/files/usr")
  )

  safe_base = (
    "/storage/emulated/0" if is_termux else os.path.expanduser("~")
  )

  # CLI argument
  if cli_dir:
    expanded = os.path.expanduser(cli_dir)

    # Absolute path → accept (after validation)
    if os.path.isabs(expanded):
      final = normalize(expanded)
    else:
      # Relative path → redirect to safe base
      final = normalize(os.path.join(safe_base, expanded))

  else:
    # Env var
    env_dir = os.getenv("DOWNLOAD_DIR")
    if env_dir:
      expanded = os.path.expanduser(env_dir)
      if os.path.isabs(expanded):
        final = normalize(expanded)
      else:
        final = normalize(os.path.join(safe_base, expanded))
    else:
      # Default
      final = os.path.join(safe_base, "YODO")

  if DEBUG:
    print(f"{CLR_DIM}[debug] Download directory: '{final}'{CLR_RESET}")
  
  # Final safety check
  if is_inside_project(final):
    print(f"{CLR_ERROR}Runtime Error: Download directory cannot be inside YODO project directory{CLR_RESET}")
  
  # Ensure DOWNLOAD_DIR is valid and accessible
  ensure_dir_exists(final)
    
  return final

def ensure_dir_exists(download_dir):
  "Ensure and make directories exists. Throw and catch errors if download_dir is not accessible or invalid."
  
  def fatal_error(message):
    print(center_title(f"{CLR_ERROR}Exception{CLR_RESET}"))
    print(message)
    print(print_crossline())
    sys.exit(1)
  
  try:
    os.makedirs(download_dir, exist_ok=True)
  
  except PermissionError:
    fatal_error(
      f"{CLR_ERROR}Permission denied while creating download directory: {CLR_RESET}"
      f"'{download_dir}'\n"
      f"Try choosing a directory you have access to."
    )
  
  except FileNotFoundError:
    fatal_error(
      f"{CLR_ERROR}Invalid download path: {CLR_RESET}"
      f"'{download_dir}'\n\n"
      f"The parent directory does not exist.\n"
      f"On Android (Termux), use paths like: "
      f"'/storage/emulated/0/YODO'"
    )
  
  except OSError as e:
    fatal_error(
      f"{CLR_ERROR}Failed to create download directory:{CLR_RESET}\n"
      f"  {download_dir}\n"
      f"Reason: {e.strerror}"
    )

# initialisation function.
def init():
  """
  Initialize application state and start background preloading.

  • Starts a daemon thread to lazily preload required modules
  • Parses command-line arguments
  • Exposes the Thread class globally

  Returns:
      threading.Thread: The background module preloading thread.
  """
  # start = time.perf_counter()
  global Thread
  import importlib
  from threading import Thread
  
  # lazy preloading (background module preloading) logic
  modules_to_preload = (
    "re",
    "shlex",
    "unicodedata",
    "urllib.parse",
    "yt_dlp",
    "yt_dlp.utils",
    "yt_dlp.extractor",
    "yt_dlp.extractor.common",
    "yt_dlp.extractor.youtube",
    "yodo.updater.update_handler",
    "yodo.utils.yodo_documentation",
    "yodo.utils.prompt_validator",
    "yodo.utils.terminal_utils"
  )
  
  def preload_modules():
    for module in modules_to_preload:
      try:
        importlib.import_module(module)
      except Exception as e:
        print(f"{CLR_WARNING}Failed to preload '{module}': {CLR_ERROR}{e}{CLR_RESET}")
  
  # start background preload
  preload_modules_thread = Thread(target=preload_modules, daemon=True)
  preload_modules_thread.start()
  
  # optimization: parse arguments only if user has given atleast one argument
  if len(sys.argv) > 1:
    global DEBUG, VERBOSE, DOWNLOAD_DIR
    
    # Parse command line arguments
    from yodo.cli import parse_cli_args
    
    #_start = time.perf_counter()
    
    args = parse_cli_args(VERSION)
    
    #print(f"{CLR_DIM}[perf] parse cli arguments: {(time.perf_counter()-_start)*1000:.2f} ms{CLR_RESET}")
    
    DEBUG = args.debug
    VERBOSE = args.verbose
    DOWNLOAD_DIR = args.download_dir
    
    # Rule: debug implies verbose
    if DEBUG and not VERBOSE:
      VERBOSE = True
      
    if DEBUG:
      print(f"{CLR_DIM}[info] CLI mode detected{CLR_RESET}")
      
  # print(f"{CLR_DIM}Preload execution time: {(time.perf_counter()-start)*1000:.2f} ms{CLR_RESET}")
      
  return preload_modules_thread

def url_input_handler():
  """
  Prompt the user to enter a media URL and validate before returning
  
  This function repeatedly asks the user for a URL until a valid media URL is provided or the user chooses to exit.
  If the URL fails validation, a descriptive error message is displayed and the user is prompted again.
  The user can exit the program by entering:
      'e', 'q', 'exit', or 'cancel'
  Returns:
    str:
      A validated media URL suitable for use with `yt-dlp`.
  Raises:
    SystemExit:
      If the user chooses to exit the program.
  """
  
  def validate_url(url):
    """Function to check the url is acceptable input for yt-dlp.
    
      Rules:
        • scheme is http or https
        • domain exists (netloc)
        • URL point to a resource (path/query)
      Returns:
        • None if valid
        • error message if invalid
    """
    
    parsed = urlparse(url)
  
    if parsed.scheme not in ("http", "https"):
      return "URL must start with http or https"
  
    if not parsed.netloc:
      return "URL must contain a valid domain"
  
    if not parsed.path.strip("/") and not parsed.query:
      return "URL must point to a specific resource"
    
    # Return None if all checks passed
    return None
    
  # Intro message
  print(f"{CLR_BRIGHT_GREEN}YODO — Universal Media Downloader{CLR_RESET}")
  print(f"{CLR_BRIGHT_GREEN}Github: https://github.com/somostro/yodo{CLR_RESET}\n")
  
  print(f"{CLR_ITALIC}Download videos and audio from supported websites using a simple, interactive interface.\n{CLR_RESET}")
  
  print(f"{CLR_GREEN}How to use:{CLR_RESET}")
  print(f"{CLR_BOLD}  • Paste a media URL and press Enter to choose quality and download{CLR_RESET}")
  print(f"  • Type '{CLR_CYAN}update{CLR_RESET}' to update YODO and yt-dlp to the latest version")
  print(f"  • Type '{CLR_CYAN}cancel{CLR_RESET}' to exit the program at any time\n")
  
  while True:
    user_input = input(f"{CLR_INPUT}=> {CLR_RESET}{CLR_CYAN}").strip()
    print(CLR_RESET)
    
    # import urllib.parse.urlparse function
    try:
      urlparse
    except NameError:
      from urllib.parse import urlparse
      
    # import YODO updater.update_handler
    try:
      update_handler
    except NameError:
      from yodo.updater import update_handler
      
    # update command handler
    if user_input.lower().startswith("update"):
      update_handler.update(user_input)
      continue
    
    if user_input.lower() in ('e', 'q', 'exit', 'cancel' ):
      print("Exiting...")
      sys.exit()
    if not user_input:
      print(f"{CLR_WARNING}URL cannot be empty. Please enter a valid video/audio link{CLR_RESET}\n")
      continue
    if "instagram.com/p" in user_input:
      print(f"{CLR_ERROR}Instagram post cannot be downloaded.{CLR_RESET}\n")
      continue
    if "youtube.com/post" in user_input:
      print(f"{CLR_ERROR}Youtube post or images cannot be downloaded.{CLR_RESET}\n")
      continue
    if "www.instagram.com/reels/audio" in user_input:
      print(f"{CLR_ERROR}Instagram audio files cannot be downloaded.{CLR_RESET}\n")
      continue
    if "/playlist" in user_input:
      print(f"{CLR_ERROR}Downloading playlists is not currently supported, this feature will be added soon.{CLR_RESET}\n")
      continue
    
    # validate URL
    error = validate_url(user_input)
    if error:
      print(f"{CLR_ERROR}Invalid URL, {error}{CLR_RESET}\nPlease enter a valid video/audio link from supported sites ({CLR_GREEN}'YouTube', 'Instagram', 'Reels', 'TikTok', 'SoundCloud' etc{CLR_RESET}).\nType '{CLR_CYAN}cancel{CLR_RESET}' to exit\n")
    else:
      break
      
  return user_input
  
def fetch_details(url, options):
  """
  Fetch media information for a given URL and estimate file sizes.

  Uses yt-dlp to extract format details, duration, and title, then calculates estimated file sizes and format metadata for the available options (low, medium, high, audio).

  Args:
    url (str): Media URL to extract information from.
    options (dict): yt-dlp format selectors for each quality option.

  Returns:
    tuple:
      (options_file_size, options_details) where:
        - options_file_size maps each option to its estimated size
        - options_details contains audio/video format attributes

  Exits:
      Terminates the program on unsupported URLs or extraction errors.
  """
  
  options_file_size = {'low': None, 'medium': None, 'high': None, 'audio': None}
  options_details = {'low': {'video': None, 'audio': None}, 'medium': {'video': None, 'audio': None}, 'high': {'video': None, 'audio': None}, 'audio': {'video': None, 'audio': None}}
  
  global is_info_loaded
  
  # Display media fetch loader
  if not VERBOSE:
    loader_thread = Thread(target=display_fetch_loader, daemon=True)
    loader_thread.start() # start the loader
  # if VERBOSE enabled, display media fetch details (in verbose mode)
  else:
    print(center_title(f"{CLR_BRIGHT_BLUE}Fetch Media Information{CLR_RESET}"))
  
  try:
    # fetch info yt-dlp options
    INFO_YDL_OPTS = {
      "verbose": VERBOSE,
      "quiet": not VERBOSE,
      "skip_download": True,
      "no_warnings": not DEBUG,
      "remote_components": {"ejs:github"},
      "js_runtimes": {
        "deno": {
          "exec": "deno",
          "args": ["run", "--quiet", "--allow-net", "--allow-read"],
        }
      },
      "js_runtime": "deno"
    }
    with YoutubeDL(INFO_YDL_OPTS) as ydl:
      # track loading time of fetching info
      if DEBUG:
        info_load_time = time.perf_counter()
      
      info = ydl.extract_info(url, download=False)
      
      if not VERBOSE:
        is_info_loaded = True
        loader_thread.join() # Wait for loader to finish cleanly
        print(f"{CLR_RESET}{CLR_BRIGHT_BLUE}✓done.{CLR_RESET}") # loading finished
      
      # print crossline if verbose mode enabled
      if VERBOSE:
        print(print_crossline())
      
      if DEBUG:
        # reset color styles for output in debug mode
        print(f"{CLR_DIM}[perf] Fetch metadata: {(time.perf_counter() - info_load_time):.2f} s{CLR_RESET}")
      
      # get video information and print
      formats = info.get("formats", None)
      title = info.get("title", "unknown title")
      duration_seconds = info.get("duration", 0)
      duration_str = time.strftime("%H:%M:%S", time.gmtime(duration_seconds))
      
      C_START = CLR_BRIGHT_GREEN
      C_RESET = CLR_LIME
      print(f"\n{p_s(2)}{C_START}video Title: {C_RESET}{title}\n{p_s(2)}{C_START}Duration: {C_RESET}{duration_str}{CLR_RESET}\n")
      
      # check if the input video url is Invalid(Instagram post) or not
      if duration_str == "00:00:00":
        print(f"{CLR_ERROR}There is no video in this URL, Posts or Images cannot be downloaded.{CLR_RESET}\nExiting...")
        sys.exit(1)
  
      # set the base name of the file
      global FINAL_FILENAME
      FINAL_FILENAME = sanitize_filename(title)
      
      # 'None' for invalid value
      invalid_value = f"{CLR_ERROR}None{CLR_RESET}"
      
      # debugging for loop timing
      if DEBUG:
        for_start = time.perf_counter()
      
      
      for label, fmt in options.items():
        try:
          # Resolve which format yt-dlp would pick
          selector = ydl.build_format_selector(fmt)
          chosen = list(selector(info))
          
          if DEBUG:
            _chosen_formats = [f.get("format_id") for f in chosen]
            if _chosen_formats:
              print(f"{CLR_DIM}[debug] {label} chosen formats:", _chosen_formats, CLR_RESET)
            else:
              print(f"{CLR_DIM}[debug] No valid formats found for option: {label}{CLR_RESET}")
          
          if not chosen:
            options_file_size[label] = f"{CLR_ERROR}Not available{CLR_RESET}"
            continue
  
          total_size = 0
          part_sizes = []
          first_f = chosen[0] # first format for video info reference
          
          # collect necessary details
          # video details
          resolution = f"{first_f.get('width', '?')}x{first_f.get('height', '?')}"
          fps = first_f.get("fps") if first_f.get("fps") and first_f.get("fps") != "None" else invalid_value
          vbr = f"{first_f.get('vbr'):.1f}" if first_f.get("vbr") else invalid_value # video bitrate in kbps
          ext = first_f.get("ext", invalid_value)  # video extension
          
          # audio details
          acodec = first_f.get("acodec", invalid_value)  # audio codec "mp4a.40.2" (AAC), "opus"
          abr = f"{first_f.get('abr'):.1f}" if first_f.get("abr") else invalid_value # audio bitrate in kbps
          channels = first_f.get("audio_channels", invalid_value)  # 1=mono, 2=stereo
          channels_str = "mono" if channels == 1 else "stereo" if channels == 2 else invalid_value
          
          # iterate over the format to calculate file sizes
          for f in chosen:   
            # get file size information
            size = f.get("filesize") or f.get("filesize_approx") or 0 
            total_size += size
            part_sizes.append(get_size_str(size))
          #💥
          # store the details into options_details dict
          # video details
          options_details[label]['video'] = {
            "Resolution": resolution,
            "FPS": fps,
            "video Bitrate": vbr,
            "video Extension": ext
          }
          
          # audio details
          options_details[label]['audio'] = {
            "Audio codec": acodec,
            "Audio Bitrate": abr,
            "Channels": channels_str
          }
          
          # store the file size info into options_file_size dict 
          size_str = get_size_str(total_size) if total_size else "Unknown"
          if not part_sizes:
            options_file_size[label] = None
          elif len(part_sizes) == 1:
            options_file_size[label] = part_sizes[0]
          else:
            options_file_size[label] = f"{size_str} ({' + '.join(part_sizes)})"
        except Exception as e:
          if DEBUG:
            print(f"{CLR_DIM}[debug] Skipping incomplete formats for '{label}'{CLR_RESET}")
          options_file_size[label] = f"{CLR_ERROR}Not available{CLR_RESET}"
      
      # debugging
      if DEBUG:
        print(f"{CLR_DIM}[perf] Format selection loop: {(time.perf_counter()-for_start)*1000:.2f} ms{CLR_RESET}")
      
  except Exception as e:
    error = str(e).lower()
    print("\n", center_title(f"{CLR_ERROR}Exception{CLR_RESET}"), sep='')
    if "unable to download" in error:
      print(f"{CLR_ERROR}Unable to fetch information. Please check your internet connection and try again.{CLR_RESET}")
    elif "unsupported" in error:
      print(f"{CLR_ERROR}Invalid or unsupported URL. Please enter a valid video/audio link from supported sites ('YouTube', 'Instagram', 'Reels', 'TikTok', 'SoundCloud' etc).{CLR_RESET}")
    elif "private" in error:
      print(f"{CLR_ERROR}This video is private or requires login credentials. Please use a different video.{CLR_RESET}")
    elif "geo" in error or "restricted" in error:
      print(f"{CLR_ERROR}This video is not available in your region.{CLR_RESET}")
    elif "extracterror" in error or "forbidden" in error:
      print(f"{CLR_ERROR}Could not extract video information. The site may have changed — try updating yt-dlp.{CLR_RESET}")
    else:
      print(f"{CLR_ERROR}An unexpected error occurred while fetching media information:\n{e}{CLR_RESET}")
    
    print(print_crossline())
    print("Exiting...")
    sys.exit(1)
    
  return options_file_size, options_details

def choice_input_handler(options_file_size, options_details):
  """
  Display available audio/video download options, accept user choice,
    validate optional attributes, and return the selected option with
    its resolved attributes.

    Args:
      options_file_size (dict): Estimated file sizes for each choice (low, medium, high, audio).
      options_details (dict): Format and codec details for available options.

    Returns:
      dict:
        Contains the selected choice and its validated options_attributes configuration.

    Raises:
      SystemExit: If the user cancels the operation.
  """
  
    # *here arguments are referred as attributes.
  
    # choice/options attributes and its values
  options_attributes = {
    "video": {
      "quality": None, # if not specified default value will be used
      "format": "mp4", # default
      "thumbnail": {"enabled": True, "ext": 'jpg'}, # default True, jpg
      "metadata": True, # default True, except for 'webm'
      "subtitles": {
        "enabled": False,
        "lang": 'all',
        "subtitlesformat": 'ttxt'
      }
    },
    "audio": {
      "quality": "bestaudio",
      "format": "best", # default best
      "thumbnail": {"enabled": True, "ext": 'jpg'}, # default True, jpg
      "metadata": True # default True for supported formats
    }
  }
  
  # set filename+prefix+extension of the filename
  # the function dependes on predicted properties
  def set_FINAL_FILENAME(choice, ext=None):
    """
    The function takes FINAL_FILENAME(video title) then append '.{ext}' to the name.
    The function may reset the FINAL_FILENAME Extension if user requested (options_attributes.audio/video.format)
    The function estimates the final file name based on properties such as the video title and the chosen or predicted video/audio extension. So, the FINAL_FILENAME is only an estimate and may not be completely accurate.
    """
    # reset the prefix and the extension of FINAL_FILENAME if given
    def normalise_name(name):
      """function for removing the file extension from the file name"""
      if '.' in name:
        name = name.rsplit('.', 1)[0]
      return name
    
    if choice == "audio":
      if not ext or ext == "best":
        ext = options_details['audio']['audio']['Audio codec']
      ext = codec_to_ext(ext)
    else:
      if not ext:
        ext = "mp4" # default video format
      elif ext == "best":
        ext = options_details[choice]['video']['video Extension']
    
    global FINAL_TITLE
    global FINAL_EXT
    FINAL_EXT = ext
    global FINAL_FILENAME
    FINAL_TITLE = normalise_name(FINAL_FILENAME)
    FINAL_FILENAME = FINAL_TITLE
    FINAL_FILENAME = f"{FINAL_FILENAME}.{ext}"
    if DEBUG:
      print(f"{CLR_DIM}[debug] FINAL_FILENAME: {FINAL_FILENAME}{CLR_RESET}")
  
  
  details = {'low': {'video': "", 'audio': ""}, 'medium': {'video': "", 'audio': ""}, 'high': {'video': "", 'audio': ""}, 'audio': {'video': "", 'audio': ""}}
  
  # shorthand of attr
  attr_shorthand = {
    'Resolution': f"{CLR_ORANGE}res{CLR_RESET}",
    'FPS': f"{CLR_ORANGE}fps{CLR_RESET}",
    'video Bitrate': f"{CLR_ORANGE}vbr{CLR_RESET}",
    'video Extension': f"{CLR_ORANGE}ext{CLR_RESET}",
    'Audio codec': f"{CLR_ORANGE}acodec{CLR_RESET}",
    'Audio Bitrate': f"{CLR_ORANGE}abr{CLR_RESET}",
    'Channels': f"{CLR_ORANGE}channels{CLR_RESET}"
  }
  
  for label in options_details.keys():
    for frmt in options_details[label].keys():
      if options_details[label][frmt]:
        for attr in options_details[label][frmt].keys():
          details[label][frmt] = f"{details[label][frmt]} {attr}: {options_details[label][frmt][attr]},"

  # format details, shorthand for attr
  details_formated = {'low': {'video': "", 'audio': ""}, 'medium': {'video': "", 'audio': ""}, 'high': {'video': "", 'audio': ""}, 'audio': {'video': "", 'audio': ""}}
  
  for label in details.keys():
    for frmt in details[label].keys():
      if details[label][frmt]:
        descr = details[label][frmt]
        # skip the last item
        descr_list = descr.split(",")[0:-1]
        # replace attr name by its shorthand
        descr_list_formated = []
        for i in range(len(descr_list)):
          item_value = descr_list[i]
          item_attr = item_value.split(':', 1)[0].strip()
          descr_list_formated.append(item_value.replace(item_attr, attr_shorthand[item_attr]))
        # format the items by ','
        descr_formated = ",".join(descr_list_formated)
        details_formated[label][frmt] = descr_formated
  
  choice_description = {'low': "", 'medium': "", 'high': "", 'audio': ""}
  for choice in choice_description.keys():
    if choice == 'audio':
      choice_description[choice] = f"""
  • {CLR_INPUT}'{choice}'{CLR_RESET} = {CLR_ITALIC}{CLR_BOLD}high quality audio only{CLR_RESET}  ({CLR_ORANGE}Size: {CLR_RESET}{options_file_size[choice]}){f"""
      {CLR_BRIGHT_GREEN}Details of audio:
        {details_formated[choice]['audio']}{CLR_RESET}""" if details_formated[choice]['audio'] else ''} 
      {move_up_1_line}"""
    else:
      choice_description[choice] = f"""
  • {CLR_INPUT}'{choice}'{CLR_RESET} = {CLR_ITALIC}{CLR_BOLD}{choice} quality audio and video{CLR_RESET}  ({CLR_ORANGE}Size: {CLR_RESET}{options_file_size[choice]}){f"""
      {CLR_BRIGHT_GREEN}Details of video:
        {details_formated[choice]['video']}
      {CLR_BRIGHT_GREEN}Details of audio:
        {details_formated[choice]['audio']}{CLR_RESET}""" if details_formated[choice]['video'] else ''}
      {move_up_1_line}"""
  
  print(f"""{CLR_BRIGHT_GREEN}{CLR_BOLD}choose an option from the list:{CLR_RESET}
  {choice_description['low']}
  {choice_description['medium']}
  {choice_description['high']}
  {choice_description['audio']}
  """)

  
  # Check available choices
  _available_choices = []
  for _choice in ('low', 'medium', 'high', 'audio'):
    if details_formated[_choice]['audio']:
      _available_choices.append(_choice)

  # Guide user to select a available choice and optional arguments/attributes
  print(f"""{CLR_BRIGHT_GREEN}How to choose:{CLR_RESET}
  • Type one option: {CLR_CYAN}{', '.join(_available_choices)}{CLR_RESET}
  • Optionally add arguments using {CLR_CYAN}<key>=<value>{CLR_RESET}
  • Examples:{CLR_CYAN}
      high
      audio quality=low format=mp3
  {CLR_RESET}""")
  
  print(f"Type '{CLR_CYAN}<choice> help{CLR_RESET}' to see available arguments.")
  print(f"Type '{CLR_CYAN}cancel{CLR_RESET}' to cancel.\n")

  
  # function to handle and validate user input and its attribute values
  def opt_attr_handler(user_input):
    """
    Parse and validate user-provided options and their attributes.
    Updates the `options_attributes` dictionary with the parsed values.
    Returns:
      (True, None): if all validations pass
      (False, error_msg): if validation failed or an error occurred
    """
    ALLOWED_AUDIO_ATTRS = ("quality", "format", "thumbnail", "metadata")
    ALLOWED_VIDEO_ATTRS = ("quality", "format", "thumbnail", "metadata", "subtitles")
    
    # helper functions
    def validate_audio_quality(value):
      value = value.strip().lower()
      
      QUALITY_LABELS_MAP = {
        "high": "bestaudio",
        "medium": "bestaudio[abr<=128]/bestaudio",
        "low": "bestaudio[abr<=64]/worstaudio"
      }
      
      if value in QUALITY_LABELS_MAP:
        return QUALITY_LABELS_MAP[value]
      elif value.isdigit():
        return f"bestaudio[abr<={int(value)}]/bestaudio"
      elif value == 'help':
        raise ValueError(AUDIO_QUALITY_DESCRIPTION)
      raise ValueError(f"Invalid value (quality: '{value}').\n{AUDIO_QUALITY_DESCRIPTION}")
    
    def validate_video_quality(value, choice):
      value = value.strip().lower()
      
      QUALITY_FORMAT = {
        "low": 
          {
            "video": "best[height<=360]/best[height<=480]/bestvideo[height<=480]+bestaudio[ext=m4a]/best",
            "audio": "bestaudio[ext=m4a]"
          },
        "medium": 
          {
            "video": "bestvideo[height<=720]+bestaudio[abr<=128]/bestvideo[height<=1080]+bestaudio[abr<=128]",
            "audio": "bestaudio[abr<=128]"
          },
        "high": 
          {
            "video": "bestvideo+bestaudio/best",
            "audio": "bestaudio"
          }
      }
      
      ALLOWED_VPIXEL_QUALITY = {"144", "240", "360", "480", "720", "1080", "1440", "2160"}
      ALLOWED_HPIXEL_QUALITY = {
        "2": "1920",
        "4": "3840",
        "8": "7680"
      }
      
      if value == 'help':
        raise ValueError(VIDEO_QUALITY_DESCRIPTION)
      elif value.endswith('p'):
        value = value[:-1]
        if value in ALLOWED_VPIXEL_QUALITY:
          return f"bestvideo[height<={value}]+{QUALITY_FORMAT[choice]["audio"]}/{QUALITY_FORMAT[choice]["video"]}"
      elif value.endswith('k'):
        value = value[:-1]
        if value in ALLOWED_HPIXEL_QUALITY:
          return f"bestvideo[width<={ALLOWED_HPIXEL_QUALITY[value]}]+{QUALITY_FORMAT[choice]["audio"]}/{QUALITY_FORMAT[choice]["video"]}"
      
      raise ValueError(f"Invalid value (quality: '{value}').\n{VIDEO_QUALITY_DESCRIPTION}")
    
    def validate_audio_format(value, choice):
      value = value.strip().lower()
      ALLOWED_FORMATS = {"best", "aac", "flac", "mp3", "m4a", "opus", "vorbis", "wav"}

      if value in ALLOWED_FORMATS:
        set_FINAL_FILENAME(choice, value)
        # set metadata=false for unsupported formats
        if value in ('wav'):
          options_attributes["audio"]["metadata"] = False
        # set metadata=true for supported formats
        else:
          options_attributes["audio"]["metadata"] = True
        return value
      elif value == 'help':
        raise ValueError(AVAILABLE_AUDIO_FORMATS_DESCRIPTION)
      
      raise ValueError(f"Invalid value (format: '{value}').\n{AVAILABLE_AUDIO_FORMATS_DESCRIPTION}")
    
    def validate_video_format(value, choice):
      value = value.strip().lower()
      ALLOWED_FORMATS = {"best", "mp4", "mkv", "webm"}

      if value in ALLOWED_FORMATS:
        set_FINAL_FILENAME(choice, value)
        # set original format for 'best'
        if value == "best":
          value = options_details[choice]['video']['video Extension']
        
        # disable thumbnail and metadata for unsupported formats (by default)
        if value == "webm":
          options_attributes["video"]["thumbnail"]["enabled"] = False
          options_attributes["video"]["metadata"] = False
        else:
          options_attributes["video"]["thumbnail"]["enabled"] = True
          options_attributes["video"]["metadata"] = True
        # set subtitlesformat='srt' for mkv format
        if value == 'mkv':
          options_attributes["video"]["subtitles"]["subtitlesformat"] = "srt"
        # set subtitlesformat='ttxt' for mp4 format
        elif value == 'mp4':
          options_attributes["video"]["subtitles"]["subtitlesformat"] = "ttxt"
        
        return value
      elif value == 'help':
        raise ValueError(AVAILABLE_VIDEO_FORMATS_DESCRIPTION)
      
      raise ValueError(f"Invalid value (format: '{value}').\n{AVAILABLE_VIDEO_FORMATS_DESCRIPTION}")
      
    def validate_thumbnail(value, choice):
      value = value.strip().lstrip(".").lower()
      
      # logic if the value is boolean
      if value == "true":
        return True, 'jpg'
      if value == "false":
        return False, None
      
      # logic if the value is an extension
      ALLOWED_THUMB_EXT = {"png", "jpg", "webp"}
      ext = value
      if ext not in ALLOWED_THUMB_EXT:
        if value == 'help':
          raise ValueError(AUDIO_THUMB_DESCRIPTION if choice == 'audio' else VIDEO_THUMB_DESCRIPTION)
        raise ValueError(f"Invalid thumbnail image format (extension: '{ext}').\n{AUDIO_THUMB_DESCRIPTION if choice == 'audio' else VIDEO_THUMB_DESCRIPTION}")
      # normalise ext
      if ext == "jpeg": ext = "jpg"
      return True, ext
    
    def validate_metadata(value, choice):
      value = value.strip().lower()
      if value in ('true', '1', 'yes', 'y'):
        return True
      if value in ('false', '0', 'no', 'n'):
        return False
      
      if value == 'help':
        raise ValueError(AUDIO_METADATA_DESCRIPTION if choice == 'audio' else VIDEO_METADATA_DESCRIPTION)
      raise ValueError(f"Invalid value (metadata: '{value}').\n{AUDIO_METADATA_DESCRIPTION if choice == 'audio' else VIDEO_METADATA_DESCRIPTION}")
    
    def validate_subtitles(value):
      value = value.strip().lower()
      # logic if the value is boolean
      if value == "true":
        return True, 'all'
      if value == "false":
        return False, None
    
      # logic if the value is an Extension
      ALLOWED_LANGS = {"all", "en", "hi", "ta", "te", "ml", "es", "fr", "de", "ja", "ko", "ar", "ru", "pt", "zh-Hans", "zh-Hant"}
      lang = value
      if lang in ALLOWED_LANGS:
        return True, lang
      elif value == 'help':
        raise ValueError(SUBTITLES_DESCRIPTION)
      raise ValueError(f"Invalid value(subtitles: '{lang}').\n{SUBTITLES_DESCRIPTION}")
    
    # By default set audio format as best
    options_attributes["audio"]["format"] = codec_to_ext(options_details[user_input.split(" ", 1)[0]]['audio']['Audio codec'])
    
    # set metadata=false for unsupported audio formats (default)
    if FINAL_EXT in ('wav'):
      options_attributes["audio"]["metadata"] = False
    
    # set thumbnail=false for unsupported formats (default)
    if FINAL_EXT in ('webm'):
      options_attributes["video"]["thumbnail"]["enabled"] = False
    # set metadata=false for unsupported formats (default)
    if FINAL_EXT in ('webm'):
      options_attributes["video"]["metadata"] = False
    # set subtitlesformat='ttxt' for mp4 format
    if FINAL_EXT == 'mp4':
      options_attributes["video"]["subtitles"]["subtitlesformat"] = "ttxt"
    
    # list of attributes given by user
    user_input_list = user_input.split(" ", 1)
    
    # if no attributes provided return the function
    if len(user_input_list) == 1:
      return True, None
    
    choice = user_input_list[0]
    attributes = user_input_list[1]
    
    # split the attributes
    attrs_list = shlex.split(attributes) # respect quotes

    if choice == 'audio':
      for attr in attrs_list:
        # split key and its value
        key, sep, value = attr.partition("=")
        key = key.strip().lower()
        value = value.strip().lower()
        
        # Display documentation of availabile attributes 
        if key == 'help':
          return False, ATTRS_HELP_DESCRIPTION
        # check if the key is valid
        elif key not in ALLOWED_AUDIO_ATTRS:
          return False, f"Unknown argument '{attr}'.\n{ATTRS_HELP_DESCRIPTION}"
        
        if sep:
          if attr.startswith('quality'):
            try:
              audio_quality = validate_audio_quality(value)
              options_attributes["audio"]["quality"] = audio_quality
            except ValueError as e:
              return False, e
          elif attr.startswith('format'):
            try:
              audio_format = validate_audio_format(value, choice)
              options_attributes["audio"]["format"] = audio_format
            except ValueError as e:
              return False, e
          elif attr.startswith('thumbnail'):
            try:
              is_enabled, ext = validate_thumbnail(value, choice)
              options_attributes["audio"]["thumbnail"] = {"enabled": is_enabled, "ext": ext}
            except ValueError as e:
              return False, e
          elif attr.startswith('metadata'):
            try:
              is_enabled = validate_metadata(value, choice)
            except ValueError as e:
              return False, e
            
            if is_enabled:
              if FINAL_EXT in ('aac', 'wav'):
                print(f"{CLR_WARNING}\nWarning: The audio format '{FINAL_EXT}' has limited or no metadata support.\nEnabling metadata for unsupported formats will not stop the download, but the tags may be missing in the final file. {CLR_RESET}")
              options_attributes["audio"]["metadata"] = True
            else:
              options_attributes["audio"]["metadata"] = False
    
    else:
      for attr in attrs_list:
        # split key and its value
        key, sep, value = attr.partition("=")
        key = key.strip().lower()
        value = value.strip().lower()
        
        if key == 'help':
          return False, ATTRS_HELP_DESCRIPTION
        # check if the key is valid
        if key not in ALLOWED_VIDEO_ATTRS:
          return False, f"Unknown argument '{attr}'.\n {ATTRS_HELP_DESCRIPTION}"
        
        if sep:
          if attr.startswith('quality'):
            try:
              video_quality = validate_video_quality(value, choice)
              options_attributes["video"]["quality"] = video_quality
            except ValueError as e:
              return False, e
          elif attr.startswith('format'):
            try:
              video_format = validate_video_format(value, choice)
              options_attributes["video"]["format"] = video_format
            except ValueError as e:
              return False, e
          elif attr.startswith('thumbnail'):
            try:
              is_enabled, ext = validate_thumbnail(value, choice)
              options_attributes["video"]["thumbnail"] = {"enabled": is_enabled, "ext": ext}
            except ValueError as e:
              return False, e
          elif attr.startswith('metadata'):
            try:
              is_enabled = validate_metadata(value, choice)
              options_attributes["video"]["metadata"] = is_enabled
            except ValueError as e:
              return False, e
          elif attr.startswith('subtitles'):
            try:
              is_enabled, lang = validate_subtitles(value)
              options_attributes["video"]["subtitles"]["enabled"] = is_enabled
              options_attributes["video"]["subtitles"]["lang"] = lang
            except ValueError as e:
              return False, e
      
      # warn user about unsupported attributes
      if options_attributes["video"]["thumbnail"]["enabled"]:
        if FINAL_EXT == "webm":
          return False, f"{CLR_ERROR}\nError: The video format '{FINAL_EXT}' does not support thumbnail embedding.\nPlease choose another supported format (mp4, mkv) or disable thumbnail (thumbnail=false){CLR_RESET}"
      if options_attributes["video"]["metadata"]:
        if FINAL_EXT in ("webm"):
          return False, f"{CLR_WARNING}\nWarning: The video format '{FINAL_EXT}' has limited metadata support, and some players may ignore it.\n Use mp4 or mkv for better support or disable metadata (metadata=false){CLR_RESET}"
      if FINAL_EXT == 'webm' and options_details[choice]['video']['video Extension'] == 'mp4':
        return False, "WebM remux is not supported for this video (codec mismatch). Please choose mp4/mkv instead."
      if FINAL_EXT == 'mp4' and options_attributes["video"]["subtitles"]["enabled"]:
        print(f"{CLR_WARNING}Warning: Subtitles may not appear in some players for MP4 files. For better compatibility, use MKV format.{CLR_RESET}")
        
    # return the function if all validations pass
    return True, None


  
  while True:
    user_input = prompt_screen()
    
    if not user_input:
      print(f"""{CLR_WARNING}
    choice cannot be empty!
    Please choose either option from low|medium|high|audio
    {CLR_ITALIC}Enter 'cancel' to cancel the operation{CLR_RESET}
      """)
      continue
    
    if user_input == 'cancel':
      print("\nExiting...")
      sys.exit()
    
    choice = user_input.split(" ", 1)[0]
    set_FINAL_FILENAME(choice)
    
    # if choice is available
    if options_file_size[choice] != f"{CLR_ERROR}Not available{CLR_RESET}":
      # receive confirmation message
      ok, error_msg = opt_attr_handler(user_input)
      
      if DEBUG:
        print(f"{CLR_DIM}[debug] options_attributes:", options_attributes, CLR_RESET)
      
      # print error message
      if not ok:
        print(f"\n{CLR_ERROR}{error_msg}{CLR_RESET}\n")
        continue
      
      # stop prompting and continue further actions
      else:
        break
    # if choice is not available
    else:
      print(
        f"{CLR_WARNING}",
        f"The choice '{choice}' is not available for this media.",
        f"{CLR_RESET}",
        sep='\n'
      )
      continue
    
    print(f"""{CLR_ERROR}
    Invalid choice!
    Please choose either option from low|medium|high|audio
    {CLR_ITALIC}Enter 'cancel' to cancel the operation{CLR_RESET}
      """)
  
  # display processed arguments/attributes details
  print()
  def print_attr_details(opt):
    # audio quality attr info
    if opt == "audio":
      print(f"{p_s(2)}{CLR_ORANGE}Quality: {CLR_RESET}{options_attributes[opt]['quality']}")
    # video quality attr info
    else:
      print(f"{p_s(2)}{CLR_ORANGE}Quality: {CLR_RESET}{choice if options_attributes[opt]['quality'] == None else 'custom ('+options_attributes[opt]['quality']+')'}")
    
    # format attr info
    print(f"{p_s(2)}{CLR_ORANGE}Format: {CLR_RESET}{options_attributes[opt]['format']}")
    
    # thumbnail attr info
    print(f"{p_s(2)}{CLR_ORANGE}Thumbnail: {CLR_RESET}{'Enabled' if options_attributes[opt]['thumbnail']['enabled'] else 'Disabled'}{(', '+CLR_ORANGE+'Extension: '+CLR_RESET+options_attributes[opt]['thumbnail']['ext']) if options_attributes[opt]['thumbnail']['enabled'] else ''}")
    
    # metadata attr info
    print(f"{p_s(2)}{CLR_ORANGE}Metadata: {CLR_RESET}{'Enabled' if options_attributes[opt]['metadata'] else 'Disabled'}")
  
  # print overview of audio attrs
  if choice == "audio":
    print(f"{CLR_BRIGHT_GREEN}Audio Arguments Overview:{CLR_RESET}")
    print_attr_details("audio")
  
  #print overview of video attrs
  else:
    print(f"{CLR_BRIGHT_GREEN}Video Arguments Overview:{CLR_RESET}")
    print_attr_details("video")
    # subtitles attr info
    print(f"{p_s(2)}{CLR_ORANGE}Subtitles: {CLR_RESET}{'Enabled' if options_attributes['video']['subtitles']['enabled'] else 'Disabled'}{(', '+CLR_ORANGE+'Subtitles format: '+CLR_RESET+options_attributes['video']['subtitles']['subtitlesformat']) if options_attributes['video']['subtitles']['enabled'] else ''}")
  
  return {"choice": choice, "options_attributes": options_attributes}

# main function
def download_media(url):
  """
  Download media (video or audio) from a given URL using yt-dlp.

  This function fetches available media formats, displays size and quality options to the user, and allows customization of download attributes such as quality, format, thumbnails, metadata, and subtitles. Based on the user’s selection, it configures yt-dlp options and media is downloaded accordingly.
  
  The base download directory is resolved dynamically using the following priority order:
    1. Command-line argument (--download-dir)
    2. Environment variable (DOWNLOAD_DIR)
    3. Platform-specific default:
       - Termux (Android): /storage/emulated/0/YODO
       - Linux: ~/YODO

    Downloaded files are organized into separate subdirectories for video and audio under the resolved base directory.

  Args:
    url (str): Media URL to download from.
  Exits:
    Terminates the program if the user cancels the operation or if a critical download or postprocessing error occurs.
  """
  
  download_dir = resolve_download_dir(DOWNLOAD_DIR)
    
  
  # Categories
  options = {
    # try 360p, else 480p (muxed). then fallback to < 480p merged video+audio
    "low": "best[height<=360]/best[height<=480]/bestvideo[height<=480]+bestaudio[ext=m4a]",
    # try 720p, else 1080p. merged video+audio
    "medium": "bestvideo[height<=720]+bestaudio[abr<=128]/bestvideo[height<=1080]+bestaudio[abr<=128]",
    # high = best available
    "high": "bestvideo+bestaudio/best",
    # audio only
    "audio": "bestaudio"
  }
  
  
  options_file_size, options_details = fetch_details(url, options)
  
  result = choice_input_handler(options_file_size, options_details)
  choice = result["choice"]
  options_attributes = result["options_attributes"]
  
  # yt-dlp options (simple, universal)
  audio_opts = {}
  video_opts = {}
  
  # configuration for audio
  if choice == "audio":
    # audio quality format selection
    audio_quality = options_attributes["audio"]["quality"]
    # set audio_quality to global options dict
    options["audio"] = audio_quality
    
    # FFmpegExtractAudio key
    key_extract_audio = [{
      "key": "FFmpegExtractAudio",
      "preferredcodec": options_attributes["audio"]["format"],
      "preferredquality": "0"
    }]
    # thumbnail converter key
    key_thumbnail_converter = []
    # thumbnail embedding key
    key_thumbnail = []
    # metadata key
    key_metadata = []
    
    # download thumbnail
    write_thumbnail = {}
    # download metadata 
    add_metadata = {}
    
    if options_attributes["audio"]["thumbnail"]["enabled"]:
      key_thumbnail_converter = [{
        "key": "FFmpegThumbnailsConvertor",
        "format": options_attributes["audio"]["thumbnail"]["ext"]
      }]
      key_thumbnail = [{
        "key": "EmbedThumbnail"
      }]
      write_thumbnail = {
        "writethumbnail": True # actually download the thumbnail
      }
    
    if options_attributes["audio"]["metadata"]:
      key_metadata = [{
        "key": "FFmpegMetadata"
      }]
      add_metadata = {
        "addmetadata": True # enable metadata extraction
      }
    
    # audio postprocessors(converter) and downloader options 
    audio_postprocessors_opts = [
        *key_extract_audio,
        *key_thumbnail_converter,
        *key_metadata, # Force embedding metadata first
        *key_thumbnail
      ]
    
    # audio downloader(write thumbnail, add metadata) options
    audio_downloader_opts = {
      **add_metadata, # Force embedding metadata first
      **write_thumbnail
    }
    
    # general audio options
    audio_opts = {
      "extractaudio": True,
      "audioformat": "best",
      "postprocessors": [
        *audio_postprocessors_opts
      ],
      **audio_downloader_opts
    }
   
  # configuration for video
  else:
    # set custom quality/format for video
    if options_attributes["video"]["quality"]:
      options[choice] = options_attributes["video"]["quality"]
      if DEBUG:
        print(f"{CLR_DIM}Quality format: { options_attributes["video"]["quality"]}{CLR_RESET}")
    
    # FFmpegVideoRemuxer key
    key_remux_video = [{
      "key": "FFmpegVideoRemuxer",
      "preferedformat": options_attributes["video"]["format"]
    }]
    # thumbnail converter key
    key_thumbnail_converter = []
    # thumbnail embedding key
    key_thumbnail = []
    # metadata key
    key_metadata = []

    # download thumbnail
    write_thumbnail = {}
    # download metadata 
    add_metadata = {}
    # download subtitles
    subtitles_opts = {}
  
    if options_attributes["video"]["thumbnail"]["enabled"]:
      key_thumbnail_converter = [{
        "key": "FFmpegThumbnailsConvertor",
        "format": options_attributes["video"]["thumbnail"]["ext"]
      }]
      key_thumbnail = [{
        "key": "EmbedThumbnail"
      }]
      write_thumbnail = {
        "writethumbnail": True # actually download the thumbnail
      }
    
    if options_attributes["video"]["metadata"]:
      key_metadata = [{
        "key": "FFmpegMetadata"
      }]
      add_metadata = {
        "addmetadata": True # enable metadata extraction
      }
      
    if options_attributes["video"]["subtitles"]["enabled"]:
      subtitles_opts = {
        "writesubtitles": True,
        "subtitleslangs": [options_attributes["video"]["subtitles"]["lang"]],   # or ["all"]
        "subtitlesformat": options_attributes["video"]["subtitles"]["subtitlesformat"],
        "embedsubtitles": True
      }
  
    # audio postprocessors(converter) and downloader options 
    video_postprocessors_opts = [
        *key_remux_video,
        *key_thumbnail_converter,
        *key_thumbnail,
        *key_metadata
      ]
    
    # audio downloader(write thumbnail, add metadata) options
    video_downloader_opts = {
      **write_thumbnail,
      **add_metadata,
      **subtitles_opts
    }
    
    # general video options
    video_opts = {
      "postprocessors": [
        *video_postprocessors_opts
      ],
      **video_downloader_opts
    }

  # setting download directory/path
  if choice == "audio":
    download_dir = os.path.join(download_dir, "audio")
    ensure_dir_exists(download_dir)
  else:
    download_dir = os.path.join(download_dir, "video")
    ensure_dir_exists(download_dir)
  
  # general yt-dlp opts
  global FINAL_TITLE
  YDL_OPTS = {
    "format": options[choice],
    "outtmpl": os.path.join(download_dir, f"{FINAL_TITLE}.%(ext)s"),  # Download path
    "noplaylist": True,  # Download only single item, not whole playlist
    "overwrites": False,
    "concurrent_fragment_downloads": 3, # number of fragments of a video that are downloaded simultaneously
    "update_time": False, # video download date = file creation date
    "sleep_interval": 1,
    "max_sleep_interval": 5,
    "remote_components": {"ejs:github"},
    "js_runtimes": {
        "deno": {
          "exec": "deno",
          "args": ["run", "--quiet", "--allow-net", "--allow-read"],
        }
      },
    "js_runtime": "ejs",
    "verbose": VERBOSE,
    # "extractor_args": {
    #   "youtube": {
    #     "player_client": ["ios", "web", "tv_embedded"],
    #   }
    # },
    **audio_opts,
    **video_opts
  }

  try:
    # Download media
    print(center_title(f"{CLR_BRIGHT_GREEN}Download Media{CLR_RESET}"))
    with YoutubeDL(YDL_OPTS) as ydl:
      # download and get info
      info = False
      try:
        info = ydl.extract_info(url, download = True)
      except Exception as e:
        error = str(e).lower()
        if "error 403: forbidden" in error:
          print(f"{CLR_ERROR}Download blocked by YouTube (Error 403: Forbidden){CLR_RESET}")
          print(f"{CLR_WARNING}This is a known issue caused by YouTube's recent security changes (SABR streaming.{CLR_RESET}")
          print(f"{CLR_GREEN}Possible temporary fixes:{CLR_RESET}")
          print(f"  • Try switching to a different network — Switch Wi-Fi to Mobile Data.")
          print(f"  • Use a trusted VPN connection to bypass region-specific restrictions.")
          print(f"  • Update yt-dlp to the latest version when an official fix is released.\n")
          print("Exiting...")
          sys.exit(1)
        elif "requested format is not available" in error:
          if choice == 'audio':
            video_format_msg = "Audio-only format"
          else:
            video_format_msg = f"The video format '{choice}'"
          print(f"\n{CLR_ERROR}{video_format_msg} not available for this video.{CLR_RESET}")
          print("Exiting...")
          sys.exit(1)
        elif "unable to download" in error:
          print(f"{CLR_ERROR}Unable to download the file. Please check your internet connection and try again.{CLR_RESET}")
        elif "connection broken" in error:
          print(f"{CLR_ERROR}The download connection was interrupted unexpectedly. This usually happens if the server closed the connection or your internet connection was unstable. Please check your network and try again.{CLR_RESET}")
        elif "postprocessing" in error:
          print(f"{CLR_ERROR}Postprocessing Error: A problem occurred during final postprocessing stage.{CLR_RESET}")
          if choice == "audio":
            print(f"{CLR_WARNING}Warning: Failed to embed thumbnail or metadata to the audio file. Continuing with plain file.{CLR_RESET}")
          else:
            print(f"{CLR_WARNING}Warning: Video re-muxing or metadata processing failed. Continuing with original file{CLR_RESET}")
        elif "permission denied" in error:
          print(f"{CLR_ERROR}No permission to write the file. Try running with correct permissions or change the output folder.{CLR_RESET}")
        elif "disk full" in error:
          print(f"{CLR_ERROR}Not enough disk space. Please free up space and try again.{CLR_RESET}")
          
        else:
          print(f"{CLR_ERROR}Error while downloading the file:\n {e}{CLR_RESET}")
      
      print(print_crossline())
      
      # get the final filename(after extraction/conversion)
      if info:
        final_filename = info["requested_downloads"][0]["filepath"]
      else:
        # fallback to dynamically set final_filename if info not available
        global FINAL_FILENAME
        final_filename = f"{download_dir}/{FINAL_FILENAME}"
      
      # Display downloaded file information
      def get_file_location(filename):
        "Extracts and returns the file location from a full file path."
        return filename.rsplit("/",1)[0] + "/"
      
      def format_filename(filename):
        """Extracts and returns the file name from a full file path."""
        return filename.rsplit('/', 1)[1]
      
      def get_file_size(filename):
        "Calculate and returns the file size of the downloaded file."
        file_size = os.path.getsize(filename)
        return f"{file_size / (1024*1024):.2f} MB"
        
      if VERBOSE:
        print(f"{CLR_DIM}[info] Full path: {final_filename}{CLR_RESET}")
        
      print(
        f"{CLR_BRIGHT_GREEN}Downloaded successfully{CLR_RESET}\n"
        # Location
        f"  {CLR_GREEN}Location: {CLR_LIME}{get_file_location(final_filename)}\n"
        # Filename
        f"  {CLR_GREEN}File: {CLR_LIME}{format_filename(final_filename)}\n"
        # File size
        f"  {CLR_GREEN}Size: {CLR_LIME}{get_file_size(final_filename)}{CLR_RESET}"
      )
  except Exception as e:
    print(center_title(f"{CLR_ERROR}Exception{CLR_RESET}"))
    error = str(e).lower()
    if "no such file" in error:
      print(f"{CLR_ERROR}Failed to download the file or couldn't find the downloaded file in the system storage.\nFinal file is expected at location: '{final_filename}'{CLR_RESET}")
    elif "key" in error:
      print(f"{CLR_ERROR}An internal error occurred in yt-dlp. Failed to clean up or finalize yt-dlp processes.\nThis is likely due to a failure during file conversion or metadata/thumbnail extraction, which prevented yt-dlp from completing its final steps.{CLR_RESET}")
    else:
      print(f"{CLR_ERROR}Error: {e}{CLR_RESET}")
    print("Exiting...")
    sys.exit(1)

if __name__ == "__main__":
  # initialisation function call
  preload_modules_thread = init()
  
  PRINT_LOGO()
  
  # calculate startup time
  print(f"{CLR_DIM}[perf] Startup time: {(time.perf_counter()-_perf_startup_time_start)*1000:.2f} ms{CLR_RESET}")
  
  # user input handler
  url = url_input_handler()
  
  # wait for preload_modules_thread to finish
  preload_modules_thread.join()
  
  # general modules
  import re
  import shlex
  import unicodedata
  from urllib.parse import urlparse
  
  # ytd-dlp imports
  from yt_dlp import YoutubeDL
  from yt_dlp.utils import sanitize_filename as _ytdlp_sanitize
  
  # YODO built-in modules/functions
  from yodo.utils.yodo_documentation import *
  from yodo.utils.prompt_validator import prompt_screen
  from yodo.utils.terminal_utils import print_crossline, center_title
  
  # calling main download function
  download_media(url)
  