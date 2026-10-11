
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import init_db, SessionLocal, PromptVersion, Job, Idea, Task
from .models import PromptSave, SettingsUpdate, RunRequest
from .config import load_settings, save_settings, ROOT
from .scheduler import start_scheduler, update_schedule
from .workflow import run_idea_generation
from datetime import datetime
import os

app = FastAPI(title="Autonomous AI Video Production Studio")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

init_db()
try:
    start_scheduler()
except Exception as e:
    print("Scheduler start failed", e)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

@app.get("/api/settings")
def get_settings():
    return load_settings()

@app.post("/api/settings")
def update_settings(upd: SettingsUpdate):
    cur = load_settings()
    data = upd.dict(exclude_unset=True)
    if "camoufox" in data and data["camoufox"]:
        cur["camoufox"] = {**cur.get("camoufox",{}), **data.pop("camoufox")}
    for k,v in data.items():
        cur[k]=v
    save_settings(cur)
    if "daily_time" in data or "schedule_enabled" in data:
        update_schedule(cur.get("daily_time","09:00"), cur.get("schedule_enabled", False))
    return cur

@app.get("/api/prompts")
def list_prompts(prompt_type: str = "idea", db: Session = Depends(get_db)):
    rows = db.query(PromptVersion).filter_by(prompt_type=prompt_type).order_by(PromptVersion.id.desc()).limit(20).all()
    return [{"id": r.id, "content": r.content, "is_current": r.is_current, "created_at": r.created_at} for r in rows]

@app.get("/api/prompts/current")
def current_prompt(prompt_type: str = "idea", db: Session = Depends(get_db)):
    r = db.query(PromptVersion).filter_by(prompt_type=prompt_type, is_current=True).order_by(PromptVersion.id.desc()).first()
    if not r:
        return {"content": "", "is_current": False}
    return {"id": r.id, "content": r.content, "is_current": True, "created_at": r.created_at}

@app.post("/api/prompts/save")
def save_prompt(payload: PromptSave, db: Session = Depends(get_db)):
    # mark old as not current
    db.query(PromptVersion).filter_by(prompt_type=payload.prompt_type, is_current=True).update({"is_current": False})
    pv = PromptVersion(prompt_type=payload.prompt_type, content=payload.content, is_current=True)
    db.add(pv); db.commit(); db.refresh(pv)
    return {"id": pv.id, "is_current": True, "saved": True}

@app.post("/api/run/test_prompt")
def test_prompt(req: RunRequest, db: Session = Depends(get_db)):
    cur = db.query(PromptVersion).filter_by(prompt_type="idea", is_current=True).first()
    prompt = req.prompt or (cur.content if cur else "")
    if not prompt:
        raise HTTPException(400, "No prompt")
    # snapshot but not save as current unless requested
    pv_id = cur.id if cur else 0
    result = run_idea_generation(prompt, pv_id, trigger="test", dry_run=False if not req.dry_run else True)
    return result

@app.post("/api/run/now")
def run_now(req: RunRequest, db: Session = Depends(get_db)):
    cur = db.query(PromptVersion).filter_by(prompt_type="idea", is_current=True).first()
    if req.use_saved:
        if not cur:
            raise HTTPException(400, "No saved prompt")
        prompt = cur.content
        pv_id = cur.id
    else:
        if not req.prompt:
            raise HTTPException(400, "Prompt required")
        prompt = req.prompt
        pv_id = cur.id if cur else 0
    return run_idea_generation(prompt, pv_id, trigger="manual", dry_run=req.dry_run)

@app.get("/api/jobs")
def jobs(db: Session = Depends(get_db)):
    rows = db.query(Job).order_by(Job.id.desc()).limit(50).all()
    return [{"run_id": r.run_id, "status": r.status, "stage": r.stage, "start_time": r.start_time, "end_time": r.end_time, "error": r.error} for r in rows]

@app.get("/api/ideas/history")
def ideas(db: Session = Depends(get_db)):
    rows = db.query(Idea).order_by(Idea.id.desc()).limit(100).all()
    return [{"idea_id": r.idea_id, "title": r.title, "description": r.description, "is_selected": r.is_selected, "is_duplicate": r.is_duplicate, "created_at": r.created_at, "job_id": r.job_id} for r in rows]

@app.get("/api/tasks")
def tasks(db: Session = Depends(get_db)):
    rows = db.query(Task).order_by(Task.id.desc()).limit(100).all()
    return [{"task_id": r.task_id, "type": r.type, "status": r.status, "episode_id": r.episode_id, "payload": r.payload, "error": r.error} for r in rows]

@app.get("/api/camoufox/test")
def test_camoufox():
    from adapters.camoufox_adapter import CamoufoxAdapter
    from .config import load_settings
    s = load_settings()
    ad = CamoufoxAdapter(s.get("camoufox",{}), provider=s.get("provider","generic"))
    return ad.test_connectivity()

# Serve frontend
frontend_dir = ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
