# src/pipeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class CompanySeed:
    title: str
    source_url: str
    homepage: str


@dataclass
class CompanyRun:
    seed: CompanySeed
    careers_url: Optional[str] = None
    jobish_text: Optional[str] = None
    llm: Optional[Dict[str, Any]] = None


def run_job_finder(
    query: str, *, limit_companies: int = 10, max_llm: int = 5
) -> List[Dict[str, Any]]:
    """
    End-to-end pipeline (to be filled step-by-step):

    Tavily -> seed companies -> find careers -> extract job-ish text -> LLM analyze -> flatten rows
    """
    # TODO: implement step-by-step
    rows: List[Dict[str, Any]] = []
    return rows
