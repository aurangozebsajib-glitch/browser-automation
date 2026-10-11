
from pydantic import BaseModel
from typing import Optional, List

class PromptSave(BaseModel):
    prompt_type: str = "idea"
    content: str

class SettingsUpdate(BaseModel):
    timezone: Optional[str] = None
    daily_time: Optional[str] = None
    schedule_enabled: Optional[bool] = None
    missed_run_policy: Optional[str] = None
    provider: Optional[str] = None
    target_duration: Optional[int] = None
    aspect_ratio: Optional[str] = None
    language: Optional[str] = None
    video_type: Optional[str] = None
    camoufox: Optional[dict] = None

class RunRequest(BaseModel):
    prompt: Optional[str] = None
    use_saved: bool = True
    dry_run: bool = False
