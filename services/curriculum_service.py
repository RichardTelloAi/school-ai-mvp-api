from sqlalchemy.orm import Session
from repositories.curriculum_repository import CurriculumRepository


class CurriculumService:

    @staticmethod
    def save_curriculum(db: Session, curriculum_data: dict):
        return CurriculumRepository.create(db, curriculum_data)

    @staticmethod
    def list_curricula(db: Session):
        return CurriculumRepository.get_all(db)

    @staticmethod
    def get_curriculum(db: Session, curriculum_id: int):
        return CurriculumRepository.get_by_id(db, curriculum_id)
