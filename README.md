# Calendar Merge

Take a set of CalDAV calendars and merge all their events into a
single CalDAV calendar. Uses vdirsyncer. Run it as a cron job.

## Usage

Clone the repo and create `.env` file in it:

```
CALDAV_URL=
CALDAV_USERNAME=
CALDAV_PASSWORD=

INPUT_CALENDARS=
OUTPUT_CALENDAR=
```

The input calendars envvar is a comma-separated list of CalDAV
collection IDs, the output calendar is a single ID. Warning, the
output calendar will be **fully overwritten** with the merged
calendars.

Calendar IDs can each be prefixed with a comment string and a colon,
to help keep them straight.

Install dependencies with [Poetry](https://python-poetry.org/) or
equivalent following the versions in `pyproject.toml`, `poetry.lock`.
Execute

```
poetry run python -m calmerge
```

on a cron job with the desired frequency.

### Multiple sync jobs

You might want to create multiple merged calendars from separate sets
of input calendars. In that case, you can use the multiple profiles
feature. Restructure your `.env` file like this:

```
PROFILES=abc,xyz

INPUT_CALENDARS_ABC=
OUTPUT_CALENDAR_ABC=

INPUT_CALENDARS_XYZ=
OUTPUT_CALENDAR_XYZ=
```

Where each comma-delimited profile name is converted to uppercase and
suffixed on the end of the other environment variables. Each job is
executed in turn, in the order specified.
