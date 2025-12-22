CONTRACT NAME:
Curriculum Understanding – v1

STATUS:
LOCKED

VERSION:
curriculum_v1

APPLIES TO:
POST /curriculum/parse

PURPOSE:
Convert raw curriculum text into structured, teacher-editable learning objectives that can be reliably reused for test generation and AI-assisted grading.

This contract defines WHAT the AI must produce.
It does not define HOW the AI is prompted or implemented.

----------------------------------------------------------------
INPUT (FROZEN)
----------------------------------------------------------------
{
  "subject": "string",
  "grade": "string",
  "curriculum": "string"
}

Rules:
- Curriculum text may be unstructured and copied from documents or PDFs
- No preprocessing or chunking is assumed at this stage
- Input format is frozen for Phase 1 and Phase 2

----------------------------------------------------------------
OUTPUT SCHEMA (JSON ONLY – LOCKED)
----------------------------------------------------------------
{
  "summary": "string",
  "topics": [
    {
      "name": "string"
    }
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

Schema Rules:
- JSON only
- No markdown
- No additional fields
- All fields are required
- Field names are stable and must not change silently

----------------------------------------------------------------
CONTENT CONSTRAINTS (HARD RULES)
----------------------------------------------------------------

Learning Objectives:
- Must start with an action verb (e.g. Understand, Explain, Apply, Compare, Produce)
- Must be observable or assessable
- One sentence per objective
- Target count: 5–8 objectives
- Written in teacher-familiar language
- Avoid vague phrasing such as:
  - “learn about”
  - “get better at”
  - “be familiar with”

Skill Type:
- One of: reading, writing, listening, speaking, grammar
- AI suggests skill type
- Teacher may edit skill type

Assessment Weight:
- One of: low, medium, high
- Represents relative importance for assessment
- AI suggests weight
- Teacher may edit weight

Topics:
- Nouns only
- 1–3 words per topic
- High-level only
- No verbs
- No explanations or descriptions

Summary:
- Maximum 4–5 sentences
- Plain teacher language
- No curriculum codes
- No standards references
- No pedagogy theory jargon

Notes for Teacher:
- Framed as suggestions, not instructions
- Non-authoritative tone
- May include teaching focus hints or cautions

----------------------------------------------------------------
QUALITY BAR (“GOOD ENOUGH” – PHASE 1)
----------------------------------------------------------------

A curriculum analysis is acceptable if:
- Output validates against the schema
- 5–8 learning objectives are produced
- Objectives are mostly usable without rewrite
- A teacher would keep most objectives and edit wording only
- Objectives can clearly drive:
  - Test question generation (Phase 2)
  - Skill-based assessment and grading (Phase 3)

Explicitly accepted:
- Minor wording imperfections
- Conservative difficulty assessment
- Teacher edits as part of normal workflow

Explicitly rejected:
- Vague or non-assessable objectives
- Overly verbose explanations
- Authoritative or final-sounding AI language

----------------------------------------------------------------
KNOWN FAILURE MODES (DETECTED, MVP HANDLING)
----------------------------------------------------------------

Failure Types:
1. Invalid JSON
2. Schema violation (missing or extra fields)
3. Low-quality objectives (not verb-led or not assessable)
4. Insufficient curriculum input (too short or unclear)

MVP Handling Strategy:
- Backend validation fails → return HTTP 400
- Teacher-facing message:
  “AI could not confidently analyse this curriculum. Please review or retry.”
- No auto-retry logic
- No prompt chaining
- No silent fallback behavior

----------------------------------------------------------------
TRUST & OWNERSHIP GUARDRAILS (GLOBAL)
----------------------------------------------------------------

- All AI-generated outputs must be labeled:
  “AI draft – teacher review required”
- Teachers can edit all AI-generated text
- AI never makes final pedagogical decisions
- This contract is versioned and locked as curriculum_v1

----------------------------------------------------------------
CHANGE POLICY
----------------------------------------------------------------

- This contract must not be modified silently
- Any changes require a new version (e.g. curriculum_v2)
- Version changes must be deliberate and documented

END OF CONTRACT
