import datetime
from meetdown_config import MeetDownConfig
class MeetDownUtils:
    
    def __init__(self, config=None):
        self.config = MeetDownConfig.default_config() if config is None else config

    def now():
        now = datetime.datetime.now()
        return now.strftime("%m-%d-%Y-%I-%M-%p")
