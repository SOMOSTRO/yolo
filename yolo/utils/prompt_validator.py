# prompt_toolkit modules
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style

# video attributes or arguments
_video_quality_attrs = ['quality=144p', 'quality=240p', 'quality=360p', 'quality=480p', 'quality=720p', 'quality=1080p', 'quality=2K', 'quality=4K', 'quality=8K']
_video_format_attrs = ['format=best', 'format=mp4', 'format=mkv', 'format=webm']
_video_subtitles_attrs = ['subtitles=true', 'subtitles=false', 'subtitles=all', 'subtitles=en', 'subtitles=hi', 'subtitles=ml']

# audio attributes or arguments
_audio_quality_attrs = ['quality=high', 'quality=medium', 'quality=low']
_audio_format_attrs = ['format=best', 'format=opus', 'format=mp3', 'format=aac', 'format=flac', 'format=wav', 'format=vorbis']

# general video and audio attrs
_metadata_attrs = ['metadata=true', 'metadata=false']
_thumbnail_attrs = ['thumbnail=true', 'thumbnail=false', 'thumbnail=jpg', 'thumbnail=png', 'thumbnail=webp']

# placeholders that displayed on input screen
placeholder_words = {
  # choices
  "options": ['low', 'medium', 'high', 'audio', 'cancel'],
  # video attributes or arguments
  "video": [
    *_video_quality_attrs,
    *_video_format_attrs,
    *_metadata_attrs,
    *_thumbnail_attrs,
    *_video_subtitles_attrs
    ],
  # audio attributes or arguments
  "audio": [
    *_audio_quality_attrs,
    *_audio_format_attrs,
    *_metadata_attrs,
    *_thumbnail_attrs
    ]
}

class CustomCompleter(Completer):
  def get_completions(self, document, complete_event):
    text = document.text_before_cursor.lstrip()
    parts = text.split()

    # Case 1: nothing typed yet
    if len(parts) == 0:
      for w in placeholder_words["options"]:
        yield Completion(w, start_position=0)

    # Case 2: user is still typing the first word (the option)
    elif len(parts) == 1 and not text.endswith(" "):
      for w in placeholder_words["options"]:
        if w.startswith(parts[0].lower()):
          yield Completion(w, start_position=-len(parts[0]))

    elif parts[0].lower().strip() in placeholder_words["options"]:
      option = parts[0].lower().strip()
      option = "audio" if option == "audio" else "video"

  
      # Case 3: user typed an option + space + [starts typeing attributes] → start suggesting attributes
      if len(parts) >= 2 and not text.endswith(" "):
        current_attr = parts[-1].lower()
        for a in placeholder_words[option]:
          if a.startswith(current_attr):
            yield Completion(a, start_position=-len(current_attr))

  
# coustom styles
style = Style.from_dict({
  'prompt': 'ansicyan bold',
  '': 'ansicyan'
})

# validator to check user input as user types
class OptionsValidator(Validator):
  def emptyInputError(self, text):
    raise ValidationError(
        message = "Please choose either option from (low, medium, high, audio). Enter 'cancel' to cancel the operation.",
        cursor_position = len(text)+1
      )
  def invalidChoiceError(self, text):
    raise ValidationError(
        message = "invalid choice, enter 'cancel' to cancel the operation.",
        cursor_position = len(text)+1 # highlights whole word, set cursor position to the end
      )
  def validate(self, document):
    text = document.text.lower().strip()
    choice = text.split(" ", 1)[0]
    if not text:
      self.emptyInputError(text)
    elif not choice in placeholder_words["options"]:
      self.invalidChoiceError(text)
      
# prompt method
def prompt_screen():
  return prompt(
    [("class:prompt", "Enter your choice: ")],
    completer = CustomCompleter(),
    validator = OptionsValidator(),
    validate_while_typing = False,
    style = style
  ).strip().lower()
