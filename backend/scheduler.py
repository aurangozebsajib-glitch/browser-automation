
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz, uuid
from .config import load_settings
from .database import SessionLocal, Job, PromptVersion
from .workflow import run_idea_generation

scheduler = BackgroundScheduler()
started = False

def job_wrapper():
    print("[Scheduler] Daily trigger firing")
    db = SessionLocal()
    try:
        # get current idea prompt
        pv = db.query(PromptVersion).filter_by(prompt_type="idea", is_current=True).order_by(PromptVersion.id.desc()).first()
        if not pv:
            print("[Scheduler] No saved idea prompt")
            return
        run_idea_generation(pv.content, pv.id, trigger="schedule")
    finally:
        db.close()

def start_scheduler():
    global started
    if started:
        return
    settings = load_settings()
    tz = pytz.timezone(settings.get("timezone","Asia/Dhaka"))
    time_str = settings.get("daily_time","09:00")
    hour, minute = map(int, time_str.split(":"))
    scheduler.configure(timezone=tz)
    scheduler.add_job(job_wrapper, CronTrigger(hour=hour, minute=minute), id="daily_idea", replace_existing=True)
    scheduler.start()
    started = True
    print(f"[Scheduler] Started daily at {time_str} {tz}")

    # missed run policy
    if settings.get("missed_run_policy")=="run_on_startup" and settings.get("schedule_enabled"):
        # check last job
        db = SessionLocal()
        last = db.query(Job).order_by(Job.id.desc()).first()
        db.close()
        # naive: if no job today, run once
        # we let job_wrapper decide, but we trigger once
        # Commented to avoid double run on every restart; uncomment if you want immediate run
        pass

def update_schedule(new_time, enabled):
    settings = load_settings()
    tz = pytz.timezone(settings.get("timezone","Asia/Dhaka"))
    if enabled:
        hour, minute = map(int, new_time.split(":"))
        scheduler.add_job(job_wrapper, CronTrigger(hour=hour, minute=minute), id="daily_idea", replace_existing=True)
    else:
        try:
            scheduler.remove_job("daily_idea")
        except:
            pass
