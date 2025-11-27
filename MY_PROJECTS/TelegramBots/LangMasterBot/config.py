import os
from typing import Optional

class Config:
    BOT_TOKEN: str
    GITHUB_TOKEN: Optional[str]
    GITHUB_REPO:Optional[str]
    GITHUB_BRANCH:Optional[str]

    def __init__(self):
        self.BOT_TOKEN = os.getenv('8311185221:AAGgB0brk1SGmhyCVDIoPlKYn6Wce96FV_M','')
        if not self.BOT_TOKEN:
            raise RuntimeError('BOT_TOKENI topilmadi u talab qilinadi!')
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # optional
        self.GITHUB_REPO = os.getenv("GITHUB_REPO")    # optional (format: "owner/repo")
        self.GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

config = Config()