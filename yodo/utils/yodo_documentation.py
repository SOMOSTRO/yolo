import shutil
from yodo.utils.colors import *
from yodo.utils.terminal_utils import print_crossline, center_title

# ---------------------------------------


ATTRS_HELP_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Arguments Usage Guide{CLR_RESET}', '–')}
  
  {CLR_BRIGHT_CYAN}Syntax:   {CLR_CYAN}<choice> <argument>=<value>
  {CLR_BRIGHT_CYAN}Example:  {CLR_CYAN}high quality=4K format=mkv{CLR_RESET}
    
  {CLR_BRIGHT_GREEN}Available Arguments:{CLR_RESET}
    • {CLR_BRIGHT_GREEN}quality{CLR_RESET}:
        Controls audio/video quality.
        Example:
          low quality=144p
        
    • {CLR_BRIGHT_GREEN}format{CLR_RESET}:
        Output file format.
        Examples:
          medium format=mkv
          audio format=mp3
        
    • {CLR_BRIGHT_GREEN}metadata{CLR_RESET}:
        Embed media metadata into the file.
        Example:
          high metadata=true
        
    • {CLR_BRIGHT_GREEN}thumbnail{CLR_RESET}:
        Embed thumbnail into the file.
        Example:
          audio thumbnail=true
        
    • {CLR_BRIGHT_GREEN}subtitles{CLR_RESET}:
        Download and embed subtitles (video only).
        Example:
          high subtitles=true
  
  {CLR_BOLD}To learn more about a specific argument:{CLR_RESET}
      {CLR_CYAN}<choice> <argument>=help{CLR_RESET}
  Examples:
      {CLR_CYAN}high quality=help
      audio format=help{CLR_RESET}
      
  {CLR_WARNING}Notes:{CLR_RESET}
    - Arguments are optional.
    - If an argument is not specified, defaults are used.
    - {CLR_GREEN}subtitles{CLR_RESET} argument is only available for video options.
{CLR_RESET}{print_crossline('-')}"""


# ---------------------------------------


AUDIO_QUALITY_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Audio Quality Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   quality=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  quality=high
{CLR_RESET}
• {CLR_BRIGHT_GREEN}high{CLR_RESET} (default)  
  Best available audio (highest bitrate).  
  {CLR_DIM}(yt-dlp: "bestaudio"){CLR_RESET}

• {CLR_BRIGHT_GREEN}medium{CLR_RESET}  
  Best audio up to 128 kbps,  
  falls back to best available if not found.  
  {CLR_DIM}(yt-dlp: "bestaudio[abr<=128]/bestaudio"){CLR_RESET}

• {CLR_BRIGHT_GREEN}low{CLR_RESET}  
  Best audio up to 64 kbps,  
  falls back to worst available if not found.  
  {CLR_DIM}(yt-dlp: "bestaudio[abr<=64]/worstaudio"){CLR_RESET}

• {CLR_BRIGHT_GREEN}quality=<number>{CLR_RESET}  
  Target average bitrate (kbps).  
  Example: {CLR_GREEN}quality=96{CLR_RESET}
{print_crossline('-')}"""


# ---------------------------------------


VIDEO_QUALITY_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Video Quality Options{CLR_RESET}', '–')}

{CLR_ITALIC}{CLR_GREEN}Defines the preferred video resolution for downloads. You can specify quality using pixel values (e.g., 720p or 4K).{CLR_RESET}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   quality=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  quality=720p
{CLR_RESET}
• {CLR_BRIGHT_GREEN}Standard Resolutions:{CLR_RESET}
  Available values: {CLR_CYAN}144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p{CLR_RESET}
  {CLR_DIM}Example:
    quality=1080p
    yt-dlp: "bestvideo[height<=1080]/[choice-default-value]"{CLR_RESET}

• {CLR_BRIGHT_GREEN}High-end Resolutions:{CLR_RESET}
  Available values: {CLR_CYAN}2K, 4K, 8K{CLR_RESET}
  {CLR_DIM}Example:
    quality=4K
    yt-dlp: "bestvideo[width<=3840]/[choice-default-value]"{CLR_RESET}

{CLR_WARNING}Notes:{CLR_RESET}
- If no quality is specified, The program will use the default setting for the selected mode (low, medium, or high).
- Invalid or unsupported values will fall back to the default.
- Audio quality cannot be customized, it's determined automatically.
- Higher resolutions may not be available for all videos.
{print_crossline('-')}"""


# ---------------------------------------


AVAILABLE_AUDIO_FORMATS_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Audio Format Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   format=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  format=opus
{CLR_RESET}
• {CLR_BRIGHT_GREEN}best{CLR_RESET}   : Keep original (default, uses best available format)
• {CLR_BRIGHT_GREEN}mp3{CLR_RESET}    : Universal, lossy
• {CLR_BRIGHT_GREEN}m4a{CLR_RESET}    : AAC, Apple-friendly
• {CLR_BRIGHT_GREEN}opus{CLR_RESET}   : Modern, efficient (recommended)
• {CLR_BRIGHT_GREEN}flac{CLR_RESET}   : Lossless, large files
• {CLR_BRIGHT_GREEN}wav{CLR_RESET}    : Uncompressed, very large
• {CLR_BRIGHT_GREEN}vorbis{CLR_RESET} : OGG container, open-source
{print_crossline('-')}"""


# ---------------------------------------


AVAILABLE_VIDEO_FORMATS_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Video Format Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   format=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  format=mp4
{CLR_RESET}
• {CLR_BRIGHT_GREEN}best{CLR_RESET} : Keep original (uses best available format).
• {CLR_BRIGHT_GREEN}mp4{CLR_RESET}  : ({CLR_GREEN}Default{CLR_RESET}) Universal format. Works on phones, PCs, TVs, editors. (May trigger fast remux from webm/mkv → mp4).
• {CLR_BRIGHT_GREEN}mkv{CLR_RESET}  : Flexible container. Supports subtitles, multiple tracks. (Some mobile/TV players don’t support mkv).
• {CLR_BRIGHT_GREEN}webm{CLR_RESET} : YouTube’s native format. Efficient for browsers, but less supported in offline editors/players.

{CLR_WARNING}Notes:{CLR_RESET}
- By default, the output format is set to {CLR_GREEN}mp4{CLR_RESET}, ensuring reliable performance and compatibility with a wide range of modern devices.
- Choosing {CLR_GREEN}best{CLR_RESET} lets yt-dlp decide the format (usually webm for YouTube).
- Remuxing (container change without re-encoding) is fast and keeps quality (example: mp4 to mkv).
- If compatibility is your priority, choose {CLR_GREEN}mp4{CLR_RESET}.
{print_crossline('-')}"""


# ---------------------------------------


THUMB_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Thumbnail Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   thumbnail=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  thumbnail=false
{CLR_RESET}
• {CLR_BRIGHT_GREEN}True{CLR_RESET}  : Enable thumbnail embedding (default). The thumbnail will be downloaded and embedded into the video/audio file. Default extension: jpg
• {CLR_BRIGHT_GREEN}False{CLR_RESET} : Disable thumbnail embedding completely."""

# —————————————————

AUDIO_THUMB_DESCRIPTION = f"""
{THUMB_DESCRIPTION}

{CLR_BOLD}Allowed image extensions for thumbnails:{CLR_RESET}
• {CLR_BRIGHT_GREEN}jpg{CLR_RESET}  : Most widely supported for embedding across formats and players.
• {CLR_BRIGHT_GREEN}png{CLR_RESET}  : Supported, but may result in larger file sizes.
• {CLR_BRIGHT_GREEN}webp{CLR_RESET} : Modern format, smaller size, but often converted internally to jpg/png for embedding (depends on audio format & player).

{CLR_WARNING}Notes on compatibility:{CLR_RESET}
- Some audio formats (e.g., {CLR_YELLOW}opus/vorbis/wav{CLR_RESET}) do not officially support embedded thumbnails. yt-dlp/ffmpeg may still embed them, but many players will ignore or fail to display the artwork.  
- {CLR_GREEN}mp3, m4a, flac{CLR_RESET} generally support thumbnail embedding well.  
- If maximum compatibility is needed, use {CLR_GREEN}jpg{CLR_RESET} image format for thumbnail.
- Supported filetypes for thumbnail embedding are: {CLR_GREEN}mp3, opus, m4a.{CLR_RESET}
{print_crossline('-')}"""

# —————————————————

VIDEO_THUMB_DESCRIPTION = f"""
{THUMB_DESCRIPTION}
{CLR_BOLD}Allowed image extensions for thumbnails:{CLR_RESET}  

• {CLR_BRIGHT_GREEN}jpg{CLR_RESET}  : Most widely supported (default).  
• {CLR_BRIGHT_GREEN}png{CLR_RESET}  : Supported, but increases file size.  
• {CLR_BRIGHT_GREEN}webp{CLR_RESET} : Downloaded from sites like YouTube; often converted internally to jpg for embedding.  

{CLR_WARNING}Notes on compatibility:{CLR_RESET}  
- Thumbnail embedding is supported in common video containers like {CLR_GREEN}mp4, mkv, webm{CLR_RESET}.  
- Some players (especially mobile/older ones) may not display embedded thumbnails, even if successfully added.  
- If maximum compatibility is needed, use {CLR_GREEN}jpg{CLR_RESET}.  
- Supported filetypes for thumbnail embedding are: {CLR_GREEN}mp4, mkv, webm{CLR_RESET}.  
{print_crossline('-')}"""


# ---------------------------------------


METADATA_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Metadata Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   metadata=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  metadata=true
{CLR_RESET}
• {CLR_BRIGHT_GREEN}True{CLR_RESET}  : Embed metadata (title, artist, albums, etc). Enabled by default for supported formats.
• {CLR_BRIGHT_GREEN}False{CLR_RESET} : Do not embed metadata."""

# —————————————————

AUDIO_METADATA_DESCRIPTION = f"""
{METADATA_DESCRIPTION}

{CLR_BOLD}Notes on compatibility:{CLR_RESET}
- Most formats like {CLR_GREEN}mp3, m4a, flac{CLR_RESET} fully support metadata embedding.
- Some formats such as {CLR_YELLOW}aac, wav{CLR_RESET} have limited or no reliable metadata support. Metadata may fail to embed or may be ignored by players.
- For maximum compatibility across players, use {CLR_GREEN}mp3{CLR_RESET} or {CLR_GREEN}m4a{CLR_RESET}.

{CLR_WARNING}Warning:{CLR_RESET} Enabling metadata for unsupported formats will not stop the download, but the tags may be missing in the final file.
{print_crossline('-')}"""

# —————————————————

VIDEO_METADATA_DESCRIPTION = f"""
{METADATA_DESCRIPTION}

{CLR_BOLD}Notes on compatibility:{CLR_RESET}
- Most video formats like {CLR_GREEN}mp4, mkv{CLR_RESET} support metadata embedding (title, artist, date, description, etc).  
- Some formats such as {CLR_YELLOW}webm{CLR_RESET} have partial or inconsistent support. Metadata may embed but may not be recognized by all players.  
- For maximum compatibility across players, use {CLR_GREEN}mp4{CLR_RESET} or {CLR_GREEN}mkv{CLR_RESET}.  

{CLR_WARNING}Warning:{CLR_RESET} Embedding metadata in formats with poor support will not stop the download, but tags may not appear or may be ignored by players.  
{print_crossline('-')}"""


# ---------------------------------------


SUBTITLES_DESCRIPTION = f"""{CLR_RESET}{center_title(f'{CLR_BOLD}Subtitles Options{CLR_RESET}', '–')}

  {CLR_BRIGHT_CYAN}Syntax:{CLR_CYAN}   subtitles=[value]
  {CLR_BRIGHT_CYAN}Example:{CLR_CYAN}  subtitles=ml
{CLR_RESET}
• {CLR_BRIGHT_GREEN}True{CLR_RESET}  : Enable subtitle embedding.  
    Default language: {CLR_GREEN}all{CLR_RESET} (downloads all available subtitles)
    Format used: {CLR_GREEN}srt{CLR_RESET} for {CLR_GREEN}MKV{CLR_RESET} files,  
    and {CLR_GREEN}ttxt{CLR_RESET} (mov_text) for {CLR_GREEN}MP4{CLR_RESET} files.  
    Subtitles will be automatically embedded into the final video.
• {CLR_BRIGHT_GREEN}False{CLR_RESET} : {CLR_BOLD}(Default){CLR_RESET} Disable subtitles embedding completely.

{CLR_BOLD}Allowed language codes:{CLR_RESET}
  English   : en
  Hindi     : hi
  Tamil     : ta
  Malayalam : ml
  Spanish   : es

{CLR_YELLOW}You can search online for additional supported language codes provided by the site (e.g., YouTube).{CLR_RESET}

{CLR_BOLD}Notes:{CLR_RESET}
- {CLR_GREEN}MKV{CLR_RESET} format supports subtitles very well (recommended for multi-language or styled subtitles).  
- {CLR_GREEN}MP4{CLR_RESET} uses internal {CLR_GREEN}mov_text (ttxt){CLR_RESET} subtitles; some players (especially on Android) may not display them.  
- {CLR_GREEN}WebM{CLR_RESET} and other lightweight formats typically do {CLR_YELLOW}not support subtitle embedding{CLR_RESET}.  
- When subtitles are enabled, they are automatically fetched from the source if available for the selected language.

{CLR_WARNING}Warning:{CLR_RESET}
Enabling subtitles for unsupported formats (like WebM) may cause errors or result in external subtitle files instead of embedding.
{print_crossline('-')}"""
