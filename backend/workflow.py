
import uuid, random, json
from datetime import datetime
from .database import SessionLocal, Job, Idea, Task, PromptVersion
from .parser import parse_ideas, stable_idea_id, is_duplicate
from .config import load_settings
from adapters.camoufox_adapter import CamoufoxAdapter

def run_idea_generation(prompt_text: str, prompt_version_id: int, trigger="manual", dry_run=False):
    db = SessionLocal()
    run_id = f"RUN_{uuid.uuid4().hex[:8].upper()}"
    job = Job(run_id=run_id, prompt_version_id=prompt_version_id, prompt_snapshot=prompt_text,
              status="running", stage="idea_generation", start_time=datetime.utcnow())
    db.add(job); db.commit()
    try:
        settings = load_settings()
        if dry_run:
            raw = f"1. Test idea from dry run: {prompt_text[:100]}\n2. Second idea: demo video about AI"
        else:
            adapter = CamoufoxAdapter(settings.get("camoufox",{}), provider=settings.get("provider","generic"))
            raw = adapter.submit_prompt(prompt_text)
        job.raw_response = raw
        ideas = parse_ideas(raw)
        if not ideas:
            job.status="failed"; job.error="Parsing failed, no ideas"; job.end_time=datetime.utcnow(); db.commit()
            return {"run_id": run_id, "error": "parse failed", "raw": raw}

        # duplicate check
        existing_titles = [r[0] for r in db.query(Idea.title).all()]
        valid = []
        for it in ideas:
            dup = is_duplicate(it["title"], existing_titles)
            iid = stable_idea_id(it["title"]+str(random.random()))
            idea_row = Idea(idea_id=iid, job_id=job.id, title=it["title"], description=it["description"], raw=it["raw"], is_duplicate=dup)
            db.add(idea_row)
            if not dup:
                valid.append(idea_row)
        db.commit()

        if not valid:
            job.status="failed"; job.error="All ideas duplicate/invalid"; job.end_time=datetime.utcnow(); db.commit()
            return {"run_id": run_id, "error": "all duplicates"}

        selected = random.choice(valid)
        selected.is_selected = True
        db.commit()

        # create downstream tasks (stub for production pipeline)
        for stage in ["script","scenes","narration","image_prompts","media_generation","editing","validation"]:
            t = Task(task_id=f"TASK_{uuid.uuid4().hex[:6].upper()}", project_id="PROJ001", episode_id=selected.idea_id, scene_id="", type=stage, status="pending", payload={"idea_id": selected.idea_id, "idea_title": selected.title})
            db.add(t)
        job.status="completed"; job.stage="idea_selected"; job.end_time=datetime.utcnow(); db.commit()
        return {"run_id": run_id, "selected": {"id": selected.idea_id, "title": selected.title}, "count": len(ideas)}
    except Exception as e:
        job.status="failed"; job.error=str(e); job.end_time=datetime.utcnow(); db.commit()
        raise
    finally:
        db.close()
