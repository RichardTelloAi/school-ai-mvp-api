# models.py
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ==================================================
# Curriculum (Identity)
# ==================================================
class Curriculum(Base):
    __tablename__ = "curricula"

    id = Column(Integer, primary_key=True)
    subject = Column(String(100), nullable=False)
    grade = Column(String(20), nullable=False)
    curriculum_system = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    versions = relationship(
        "CurriculumVersion",
        back_populates="curriculum",
        cascade="all, delete-orphan",
        order_by="CurriculumVersion.version_number",
    )


# ==================================================
# Curriculum Version (Interpretation Layer)
# ==================================================
class CurriculumVersion(Base):
    __tablename__ = "curriculum_versions"

    id = Column(Integer, primary_key=True)

    curriculum_id = Column(
        Integer,
        ForeignKey("curricula.id", ondelete="CASCADE"),
        nullable=False,
    )

    version_number = Column(Integer, nullable=False)

    created_by = Column(
        Enum("ai", "teacher", name="created_by_enum"),
        nullable=False,
    )

    source = Column(
        Enum("parse", "edit", "regenerate", name="version_source_enum"),
        nullable=False,
    )

    summary = Column(Text, nullable=False)
    difficulty_assessment = Column(String(50), nullable=True)
    notes_for_teacher = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    curriculum = relationship("Curriculum", back_populates="versions")

    learning_objectives = relationship(
        "LearningObjective",
        back_populates="curriculum_version",
        cascade="all, delete-orphan",
    )


# ==================================================
# Learning Objective (Assessment Backbone)
# ==================================================
class LearningObjective(Base):
    __tablename__ = "learning_objectives"

    id = Column(Integer, primary_key=True)

    curriculum_version_id = Column(
        Integer,
        ForeignKey("curriculum_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    code = Column(String(20), nullable=False)  # e.g. LO1, LO2
    objective_text = Column(Text, nullable=False)

    skill_type = Column(
        Enum(
            "reading",
            "writing",
            "listening",
            "speaking",
            "grammar",
            "vocabulary",
            "math",
            name="skill_type_enum",
        ),
        nullable=False,
    )

    assessment_weight = Column(
        Enum("low", "medium", "high", name="assessment_weight_enum"),
        nullable=False,
    )

    # Relationships
    curriculum_version = relationship(
        "CurriculumVersion",
        back_populates="learning_objectives",
    )
