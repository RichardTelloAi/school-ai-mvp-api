from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CurriculumRequest(BaseModel):
    subject: str
    grade: str
    curriculum: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/curriculum/parse")
def parse_curriculum(data: CurriculumRequest):
    return {
        "summary": "stub",
        "topics": [],
        "learning_objectives": [],
        "difficulty_assessment": "appropriate",
        "notes_for_teacher": "stub"
    }
