import os, time
import datetime
import shutil
from meetdown_config import MeetDownConfig
class MeetDownUtils:
    
    def __init__(self, config=None):
        self.config = MeetDownConfig.default_config() if config is None else config

    def now(self):
        now = datetime.datetime.now()
        return now.strftime("%m-%d-%Y-%I-%M-%p")
    
    def get_terminal_width(self):
        terminal_width, _ = shutil.get_terminal_size()
        return terminal_width
    
    def clear_screen(self):
      if os.name == 'posix':
          os.system('clear')
      elif os.name == 'nt':
          os.system('cls')

    def timeout(self, delay):
        time.sleep(delay)
        return