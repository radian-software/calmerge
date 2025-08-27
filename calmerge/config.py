import dotenv

dotenv.load_dotenv()

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path


@dataclass
class Credentials:
    url: str
    username: str
    password: str


@dataclass
class Calendar:
    id: str
    comment: Optional[str] = None

    @staticmethod
    def from_str(s: str):
        if ":" in s:
            comment, id = s.split(":")
            return Calendar(id=id, comment=comment)
        return Calendar(id=s)


CALDAV = Credentials(
    url=os.environ["CALDAV_URL"],
    username=os.environ["CALDAV_USERNAME"],
    password=os.environ["CALDAV_PASSWORD"],
)

INPUT_CALENDARS = [
    Calendar.from_str(s) for s in os.environ["INPUT_CALENDAR_IDS"].split(",")
]
OUTPUT_CALENDAR = Calendar.from_str(os.environ["OUTPUT_CALENDAR_ID"])

DATA_DIR = Path(__file__).parent.parent / "data"
