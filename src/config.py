import logging
import logging.config
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

logging.config.fileConfig(
    Path(__file__).parents[1] / "logging.ini", disable_existing_loggers=False
)


class Config:
    INSEE_KEY = os.environ.get("INSEE_KEY")
    INSEE_SECRET = os.environ.get("INSEE_SECRET")
