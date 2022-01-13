import logging
import logging.config
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

ROOTDIR = Path(__file__).parents[1]

logging.config.fileConfig(ROOTDIR / "logging.ini", disable_existing_loggers=False)


class Config:
    INSEE_KEY = os.environ.get("INSEE_KEY")
    INSEE_SECRET = os.environ.get("INSEE_SECRET")
    RAWDIR = Path(os.environ.get("RAWDIR", ROOTDIR / "data" / "raw"))
    INTDIR = Path(os.environ.get("INTDIR", ROOTDIR / "data" / "interim"))
    DB_URI = os.environ.get("DB_URI", str(ROOTDIR / "data" / "interim" / "db.sqlite"))
