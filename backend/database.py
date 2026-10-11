
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
from datetime import datetime
ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "database.sqlite"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    id = Column(Integer, primary_key=True)
    prompt_type = Column(String) # idea, script, image, narration, etc
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=False)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, unique=True)
    prompt_version_id = Column(Integer)
    prompt_snapshot = Column(Text)
    status = Column(String) # pending, running, completed, failed
    stage = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    raw_response = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True)
    idea_id = Column(String, unique=True) # IDE001
    job_id = Column(Integer)
    title = Column(String)
    description = Column(Text)
    raw = Column(Text)
    is_selected = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    task_id = Column(String, unique=True)
    project_id = Column(String, default="PROJ001")
    episode_id = Column(String)
    scene_id = Column(String)
    type = Column(String) # idea, script, image, video, audio, edit
    status = Column(String) # pending, running, waiting_input, needs_review, completed, failed, skipped
    payload = Column(JSON)
    result_path = Column(String)
    retries = Column(Integer, default=0)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
