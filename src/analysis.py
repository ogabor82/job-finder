# src/analysis.py
from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


def analyze_careers_json(
    company: str, text: str, *, model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    load_dotenv()

    llm = ChatOpenAI(model=model, temperature=0)

    prompt = f"""
You are analyzing startup careers pages for a job discovery tool.

Company: {company}

Rules (very important):
- ONLY extract roles that are explicitly mentioned in the TEXT.
- A role title MUST be copied from a SINGLE line in TEXT that looks like a job title.
- Do NOT invent a title based on tech keywords.
- If you can't find a job-title-like line, do not create a role.
- Return a SINGLE valid JSON object only (no markdown, no code fences).

Return JSON schema:
{{
  "relevant": boolean,
  "roles": [
    {{
      "title": string,
      "title_evidence": string,
      "seniority": "intern" | "junior" | "mid" | "senior" | "unknown",
      "tech_stack": [string],
      "remote_friendly": boolean | "unknown",
      "summary": string,
      "evidence": [string]
    }}
  ],
  "overall_summary": string
}}

TEXT:
{text}
""".strip()

    resp = llm.invoke([HumanMessage(content=prompt)])
    raw = resp.content.strip()

    return json.loads(raw)
