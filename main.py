import os
from typing import List, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

app = FastAPI()

# ==================================================
# Phase 1 – Curriculum Models
# ==================================================

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


# ==================================================
# Phase 2 – Test Generation Models
# ==================================================

class LearningObjective(BaseModel):
    id: str
    objective: str
    skill_type: Literal["reading", "writing", "listening", "speaking", "grammar"]


class TestGenerateRequest(BaseModel):
    subject: str
    grade: str
    purpose: Literal["diagnostic", "practice", "exam"]
    duration_minutes: int
    difficulty_mix: str
    learning_objectives: List[LearningObjective]


class TestV1Response(BaseModel):
    test_metadata: dict
    coverage_summary: dict
    questions: List[dict]


# ==================================================
# Embedded Prompts (Azure-safe)
# ==================================================

CURRICULUM_V1_PROMPT = """
You are an expert curriculum analyst assisting a school teacher.

Your task is to analyse the provided curriculum text and return a structured draft that the teacher can review and edit.

IMPORTANT:
- Output VALID JSON ONLY
- Follow the schema exactly
- No explanations or markdown

Subject: <<SUBJECT>>
Grade: <<GRADE>>

Curriculum text:
<<CURRICULUM>>

Output schema:
{
  "summary": "string",
  "topics": [{ "name": "string" }],
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

Return JSON only.
"""


TEST_V1_PROMPT = """
You are an expert teacher and assessment designer.

Your task is to generate a draft test aligned to the provided learning objectives.
This is an AI draft that will be reviewed and edited by a teacher.

CRITICAL RULES:
- Output VALID JSON ONLY
- Follow the OUTPUT SCHEMA EXACTLY
- Do NOT include explanations or markdown
- Each question must link to ONE learning objective
- Each question must test ONE skill

Subject: {subject}
Grade: {grade}
Purpose: {purpose}
Difficulty mix: {difficulty_mix}
Estimated duration: {duration_minutes} minutes

Learning objectives:
{learning_objectives_json}

OUTPUT SCHEMA:
{
  "test_metadata": {
    "title": "string",
    "subject": "string",
    "grade": "string",
    "purpose": "diagnostic | practice | exam",
    "estimated_duration_minutes": 30,
    "ai_draft": true
  },
  "coverage_summary": {
    "total_questions": 10,
    "skills_covered": ["reading"],
    "objectives_covered": ["obj_1"]
  },
  "questions": []
}

Return JSON only.
"""


# ==================================================
# Utility – Azure OpenAI Client (Lazy)
# ==================================================

def get_openai_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([endpoint, api_key, api_version, deployment]):
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI is not fully configured"
        )

    try:
        from openai import AzureOpenAI
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI SDK import failed: {str(e)}"
        )

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        return client, deployment
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize OpenAI client: {str(e)}"
        )


# ==================================================
# Endpoints
# ==================================================

@app.get("/")
def health():
    return {"status": "ok"}


# ---------- Phase 1 ----------
@app.post("/curriculum/parse", response_model=CurriculumAIResponse)
def parse_curriculum(data: CurriculumRequest):
    client, deployment = get_openai_client()

   prompt = (
    CURRICULUM_V1_PROMPT
    .replace("<<SUBJECT>>", data.subject)
    .replace("<<GRADE>>", data.grade)
    .replace("<<CURRICULUM>>", data.curriculum)
)

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a strict JSON API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return CurriculumAIResponse.model_validate_json(
            response.choices[0].message.content
        )

    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="AI response did not match curriculum_v1 schema"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI request failed: {str(e)}"
        )


# ---------- Phase 2 ----------
@app.post("/test/generate", response_model=TestV1Response)
def generate_test(data: TestGenerateRequest):
    client, deployment = get_openai_client()

    learning_objectives_json = [
        {
            "id": lo.id,
            "objective": lo.objective,
            "skill_type": lo.skill_type
        }
        for lo in data.learning_objectives
    ]

    prompt = TEST_V1_PROMPT.format(
        subject=data.subject,
        grade=data.grade,
        purpose=data.purpose,
        difficulty_mix=data.difficulty_mix,
        duration_minutes=data.duration_minutes,
        learning_objectives_json=learning_objectives_json
    )

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a strict JSON API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return TestV1Response.model_validate_json(
            response.choices[0].message.content
        )

    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="AI response did not match test_v1 schema"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI request failed: {str(e)}"
        )
