from shutil import get_terminal_size

# Getting informations about CLI
# Get terminal size
terminal_size = get_terminal_size()

# Width
terminal_width = terminal_size.columns

def get_terminal_width():
  return terminal_size.columns
  
def print_crossline(char='—'):
  return char * terminal_width