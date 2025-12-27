# Test Generation Contract – v1

STATUS: LOCKED – Phase 2 Core  
Changes require an explicit version bump (v2, v3, …).

This document defines the authoritative output contract for the
`/test/generate` endpoint.

---

## 1. Purpose

The purpose of `/test/generate` is to generate a teacher-editable assessment
(test) based on selected learning objectives.

The generated test must:
- Align pedagogically with the provided learning objectives
- Match the specified subject and grade level
- Be suitable for review and editing by a human teacher
- Conform strictly to the schema defined below

---

## 2. Input Assumptions (Context Only)

The AI will receive:
- Subject
- Grade
- One or more learning objectives (each with a unique ID)

The AI MUST NOT invent learning objectives or IDs.

---

## 3. Output Rules (Strict)

- Output MUST be valid JSON
- Output MUST match this contract exactly
- No markdown
- No explanations
- No commentary outside JSON
- No additional fields beyond those defined here

If a requirement cannot be fulfilled, the AI must still return valid JSON
and make a best pedagogical attempt within constraints.

---

## 4. Top-Level Schema

```json
{
  "test_title": "string",
  "questions": [ Question ],
  "grading_guidelines": "string"
}
