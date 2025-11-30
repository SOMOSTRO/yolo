# prompt_toolkit modules
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style


placeholder_words = {
  "options": ['low', 'medium', 'high', 'audio', 'cancel'],
  
  "video": [
    'quality=360p', 'quality=720p', 'quality=1080p', 'quality=4K', 'quality=8K',
    'format=best', 'format=mp4', 'format=mkv', 'format=webm',
    'metadata=true', 'metadata=false',
    'thumbnail=true', 'thumbnail=false', 'thumbnail=jpg', 'thumbnail=png', 'thumbnail=webp',
    'subtitles=true', 'subtitles=false', 'subtitles=all', 'subtitles=en', 'subtitles=hi', 'subtitles=ml'
    ],
  
  "audio": [
    'quality=high', 'quality=medium', 'quality=low',
    'format=best', 'format=opus', 'format=mp3', 'format=aac',
    'metadata=true', 'metadata=false',
    'thumbnail=true', 'thumbnail=false', 'thumbnail=jpg', 'thumbnail=png', 'thumbnail=webp'
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