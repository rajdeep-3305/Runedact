from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)



class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(String(64), index=True)
    code = Column(Text, nullable=False)
    status = Column(String(32), default="pending")
    execution_time_ms = Column(Float, default=0.0)
    memory_used_kb = Column(Float, default=0.0)
    test_results = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    dialogues = relationship("MentorDialogue", back_populates="submission", cascade="all, delete-orphan")

class MentorDialogue(Base):
    __tablename__ = "mentor_dialogues"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)
    role = Column(String(16))
    hint_level = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    leaked_solution = Column(Boolean, default=False)
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)

    submission = relationship("Submission", back_populates="dialogues")

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    benchmark_name = Column(String(64))
    total_samples = Column(Integer)
    quality_score = Column(Float)
    leak_rate_percentage = Column(Float)
    avg_latency_ms = Column(Float)
    report_json = Column(Text)
    created_at = Column(DateTime, default=utcnow)
