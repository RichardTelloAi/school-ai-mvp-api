import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

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
# Embedded prompt (Azure-safe)
# --------------------------------------------------

CURRICULUM_V1_PROMPT = """
You are an expert curriculum analyst assisting a school teacher.

Your task is to analyse the provided curriculum text and return a structured draft that the teacher can review and edit.

IMPORTANT:
- Output VALID JSON ONLY
- Follow the schema exactly
- No explanations or markdown

Subject: {subject}
Grade: {grade}

Curriculum text:
{curriculum}

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

# --------------------------------------------------
# Endpoints
# --------------------------------------------------

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/curriculum/parse", response_model=CurriculumAIResponse)
def parse_curriculum(data: CurriculumRequest):
    # 1️⃣ Read env vars SAFELY
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not all([endpoint, api_key, api_version, deployment]):
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI is not fully configured"
        )

    # 2️⃣ Import OpenAI lazily (Swagger-safe)
    try:
        from openai import AzureOpenAI
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI SDK import failed: {str(e)}"
        )

    # 3️⃣ Create client lazily
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize OpenAI client: {str(e)}"
        )

    # 4️⃣ Build prompt
    prompt = CURRICULUM_V1_PROMPT.format(
        subject=data.subject,
        grade=data.grade,
        curriculum=data.curriculum
    )

    # 5️⃣ Call Azure OpenAI
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a strict JSON API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        ai_content = response.choices[0].message.content
        return CurriculumAIResponse.model_validate_json(ai_content)

    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="AI response did not match expected schema"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI request failed: {str(e)}"
        )
