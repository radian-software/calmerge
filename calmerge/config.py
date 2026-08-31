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


@dataclass
class Profile:
    name: str
    input_calendars: list[Calendar]
    output_calendar: Calendar

    @property
    def data_dir(self):
        return Path(__file__).parent.parent / "data" / self.name


PROFILES = []
for profile_name in os.environ.get("PROFILES", "").split(","):
    suffix = profile_name and f"_{profile_name.upper()}"
    PROFILES.append(
        Profile(
            name=profile_name,
            input_calendars=[
                Calendar.from_str(s)
                for s in os.environ["INPUT_CALENDAR_IDS" + suffix].split(",")
            ],
            output_calendar=Calendar.from_str(
                os.environ["OUTPUT_CALENDAR_ID" + suffix]
            ),
        )
    )
