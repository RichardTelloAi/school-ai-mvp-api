from sqlalchemy.orm import Session
from models import Curriculum


class CurriculumRepository:

    @staticmethod
    def create(db: Session, data: dict) -> Curriculum:
        curriculum = Curriculum(**data)
        db.add(curriculum)
        db.commit()
        db.refresh(curriculum)
        return curriculum

    @staticmethod
    def get_all(db: Session):
        return db.query(Curriculum).order_by(Curriculum.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, curriculum_id: int):
        return db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
