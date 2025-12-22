import configparser
import json
import re
import shutil
import subprocess
from typing import Any

import calmerge.config as cfg


def log(msg):
    print(f"[calmerge] {msg}")


def main():
    log("Doing initial setup")
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    cal_dir = cfg.DATA_DIR / "pimsync-caldav"
    out_cal_dir = cal_dir / cfg.OUTPUT_CALENDAR.id
    vd_cfg_file = cfg.DATA_DIR / "pimsync-config"
    vd_status_file = cfg.DATA_DIR / "pimsync-status"
    with open(vd_cfg_file, "w") as f:
        f.write(f"""
status_path {vd_status_file}

storage local_ro {{
  type vdir/icalendar
  path {cal_dir}
  read_only
}}

storage local {{
  type vdir/icalendar
  path {cal_dir}
}}

storage caldav_ro {{
  type caldav
  url {cfg.CALDAV.url}
  username {cfg.CALDAV.username}
  password {cfg.CALDAV.password}
  read_only
}}

storage caldav {{
  type caldav
  url {cfg.CALDAV.url}
  username {cfg.CALDAV.username}
  password {cfg.CALDAV.password}
}}

pair download {{
  storage_a caldav_ro
  storage_b local
  {"\n  ".join(f"collection {c.id}" for c in cfg.INPUT_CALENDARS)}
  conflict_resolution keep a
}}

pair upload {{
  storage_a local_ro
  storage_b caldav
  collection {cfg.OUTPUT_CALENDAR.id}
  conflict_resolution keep a
}}
        """.strip() + "\n")
    cal_dir.mkdir(exist_ok=True)
    run_vd = lambda *args: subprocess.run(
        ["pimsync", "-c", str(vd_cfg_file), *args], check=True
    )
    log("Running pimsync download")
    run_vd("sync", "download")
    log("Merging calendar collections")
    try:
        shutil.rmtree(out_cal_dir)
    except FileNotFoundError:
        pass
    out_cal_dir.mkdir()
    for coll in cfg.INPUT_CALENDARS:
        for ics_file in (cal_dir / coll.id).iterdir():
            event_id = coll.id + "_" + ics_file.stem
            with open(ics_file) as f1:
                with open(out_cal_dir / (event_id + ".ics"), "w") as f2:
                    for line in f1:
                        if line.startswith("UID:"):
                            f2.write("UID:" + event_id + "\n")
                        else:
                            f2.write(line)
    log("Running pimsync upload")
    run_vd("sync", "upload")
