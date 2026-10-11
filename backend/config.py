
import json, os
from pathlib import Path
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / "settings.json"
DEFAULT_SETTINGS = {
    "timezone": "Asia/Dhaka",
    "daily_time": "09:00",
    "schedule_enabled": False,
    "missed_run_policy": "run_on_startup", # skip | run_on_startup
    "camoufox": {
        "executable_path": "",
        "profile_dir": "",
        "connect_url": None,
        "headless": False,
        "timeout_ms": 120000
    },
    "provider": "generic",
    "target_duration": 60,
    "aspect_ratio": "9:16",
    "language": "bn",
    "video_type": "manga"
}
def load_settings():
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    try:
        return {**DEFAULT_SETTINGS, **json.loads(SETTINGS_FILE.read_text())}
    except:
        return DEFAULT_SETTINGS

def save_settings(s):
    SETTINGS_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False))

def get_project_root():
    return ROOT / "projects"
