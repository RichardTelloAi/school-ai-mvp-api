import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from openai import AzureOpenAI

# --------------------------------------------------
# App
# --------------------------------------------------

app = FastAPI()

# --------------------------------------------------
# Models
# --------------------------------------------------

class CurriculumRequest(BaseModel):
    subject: str
    grade: str
    curriculum: str


class CurriculumAIResponse(BaseModel):
    summary: str
    topics: List[dict]
    learning_objectives: List[dict]
    difficulty_assessment: str
    notes_for_teacher: str

# --------------------------------------------------
# Prompt loading (fail fast)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompts" / "curriculum_v1.md"

if not PROMPT_PATH.exists():
    raise RuntimeError("Prompt file prompts/curriculum_v1.md not found")

PROMPT_TEMPLATE = PROMPT_PATH.read_text()

# --------------------------------------------------
# Azure OpenAI client
# --------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

if not os.getenv("AZURE_OPENAI_DEPLOYMENT"):
    raise RuntimeError("AZURE_OPENAI_DEPLOYMENT is not set")

# --------------------------------------------------
# Endpoints
# --------------------------------------------------

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/curriculum/parse", response_model=CurriculumAIResponse)
def parse_curriculum(data: CurriculumRequest):
    prompt = PROMPT_TEMPLATE.format(
        subject=data.subject,
        grade=data.grade,
        curriculum=data.curriculum
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        ai_content = response.choices[0].message.content

        # Validate strictly against the locked contract
        return CurriculumAIResponse.model_validate_json(ai_content)

    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="AI response did not match curriculum_v1 schema"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )
