import configparser
import json
import re
import shutil
import subprocess
from typing import Any

import calmerge.config as cfg


def log(msg):
    print(f"[calmerge] {msg}")


def format_vd_cfg(o: dict) -> dict:
    def recurse(o: Any) -> dict | str:
        if isinstance(o, dict):
            return {k: recurse(v) for k, v in o.items()}
        return json.dumps(o)

    return {k: recurse(v) for k, v in o.items()}


def main():
    log("Doing initial setup")
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    cal_dir = cfg.DATA_DIR / "vdirsyncer-caldav"
    out_cal_dir = cal_dir / cfg.OUTPUT_CALENDAR.id
    vd_cfg_file = cfg.DATA_DIR / "vdirsyncer-config"
    vd_status_file = cfg.DATA_DIR / "vdirsyncer-status"
    vd_cfg = configparser.ConfigParser()
    vd_cfg.update(
        format_vd_cfg(
            {
                "general": {
                    "status_path": str(vd_status_file),
                },
                "storage local_ro": {
                    "type": "filesystem",
                    "path": str(cal_dir),
                    "fileext": ".ics",
                    "read_only": True,
                },
                "storage local": {
                    "type": "filesystem",
                    "path": str(cal_dir),
                    "fileext": ".ics",
                },
                "storage caldav_ro": {
                    "type": "caldav",
                    "url": cfg.CALDAV.url,
                    "username": cfg.CALDAV.username,
                    "password": cfg.CALDAV.password,
                    "read_only": True,
                },
                "storage caldav": {
                    "type": "caldav",
                    "url": cfg.CALDAV.url,
                    "username": cfg.CALDAV.username,
                    "password": cfg.CALDAV.password,
                },
                "pair download": {
                    "a": "caldav_ro",
                    "b": "local",
                    "collections": [c.id for c in cfg.INPUT_CALENDARS],
                    "conflict_resolution": "a wins",
                },
                "pair upload": {
                    "a": "local_ro",
                    "b": "caldav",
                    "collections": [cfg.OUTPUT_CALENDAR.id],
                    "conflict_resolution": "a wins",
                },
            }
        )
    )
    with open(vd_cfg_file, "w") as f:
        vd_cfg.write(f)
    run_vd = lambda *args: subprocess.run(
        ["vdirsyncer", f"--config={str(vd_cfg_file)}", *args], check=True
    )
    log("Running vdirsyncer download")
    run_vd("discover", "download")
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
    log("Running vdirsyncer upload")
    run_vd("discover", "upload")
    run_vd("sync", "upload")
