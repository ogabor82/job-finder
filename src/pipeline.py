# src/pipeline.py
from __future__ import annotations

from typing import List, Dict, Any

from src.discovery import discover_company_seeds
from src.careers import find_careers_url


def run_job_finder(
    query: str, *, limit_companies: int = 10, max_llm: int = 5
) -> List[Dict[str, Any]]:
    """
    End-to-end pipeline (to be filled step-by-step):

    Tavily -> seed companies -> find careers -> extract job-ish text -> LLM analyze -> flatten rows
    """
    seeds = discover_company_seeds(query, max_results=limit_companies)

    out = []
    for s in seeds:
        careers_url = find_careers_url(s.homepage)
        out.append(
            {
                "title": s.title,
                "source_url": s.source_url,
                "homepage": s.homepage,
                "careers_url": careers_url,
            }
        )

    return out
