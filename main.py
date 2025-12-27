import os
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
# Prompt template (embedded – Azure App Service safe)
# --------------------------------------------------

CURRICULUM_V1_PROMPT = """
You are an expert curriculum analyst assisting a school teacher.

Your task is to analyse the provided curriculum text and return a structured draft that the teacher can review and edit.

IMPORTANT:
- You must follow the output schema exactly
- You must respect all content constraints
- Your response must be valid JSON only
- Do not include explanations, markdown, or additional text

--------------------------------------------------
CONTEXT
--------------------------------------------------
Subject: {subject}
Grade: {grade}

--------------------------------------------------
CURRICULUM TEXT
--------------------------------------------------
{curriculum}

--------------------------------------------------
OUTPUT SCHEMA (JSON ONLY)
--------------------------------------------------
{
  "summary": "string",
  "topics": [
    { "name": "string" }
  ],
  "learning_objectives": [
    {
      "id": "string",
      "objective": "string",
      "skill_type": "reading | writing | listening | speaking | grammar",
      "assessment_weight": "low | medium | high"
    }
  ],
  "difficulty_assessment": "too_easy | appropriate | too_hard",
  "notes_for_teacher": "string"
}

Return valid JSON only.
"""

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
    prompt = CURRICULUM_V1_PROMPT.format(
        subject=data.subject,
        grade=data.grade,
        curriculum=data.curriculum
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict JSON API. Output JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        ai_content = response.choices[0].message.content

        # Strict validation against Phase 1 contract
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
