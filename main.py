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
        "subject": data.subject,
        "grade": data.grade,
        "summary": f"Curriculum received: {data.curriculum}"
    }
