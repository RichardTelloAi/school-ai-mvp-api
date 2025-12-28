from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Curriculum(Base):
    __tablename__ = "curricula"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False)
    grade = Column(String(50), nullable=False)
    curriculum = Column(String(100), nullable=False)

    summary = Column(Text, nullable=True)
    difficulty_assessment = Column(String(50), nullable=True)
    notes_for_teacher = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
