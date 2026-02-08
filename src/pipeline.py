# src/pipeline.py
from __future__ import annotations

from typing import List, Dict, Any

from src.discovery import discover_company_seeds
from src.careers import find_careers_url
from src.careers import extract_careers_text, extract_jobish_lines
from src.analysis import analyze_careers_json


def flatten_company_result(company: str, careers_url: str, data: dict) -> list[dict]:
    rows = []
    for r in data.get("roles", []):
        rows.append(
            {
                "company": company,
                "careers_url": careers_url,
                "title": r.get("title"),
                "seniority": r.get("seniority", "unknown"),
                "remote_friendly": r.get("remote_friendly", "unknown"),
                "tech_stack": ", ".join(r.get("tech_stack", [])),
                "summary": r.get("summary", ""),
                "evidence": " | ".join((r.get("evidence") or [])[:2]),
                "title_evidence": r.get("title_evidence", ""),
            }
        )
    if not rows:
        rows.append(
            {
                "company": company,
                "careers_url": careers_url,
                "title": None,
                "seniority": None,
                "remote_friendly": None,
                "tech_stack": "",
                "summary": data.get("overall_summary", ""),
                "evidence": "",
                "title_evidence": "",
            }
        )
    return rows


def run_job_finder(
    query: str, *, limit_companies: int = 10, max_llm: int = 5
) -> List[Dict[str, Any]]:
    """
    End-to-end pipeline (to be filled step-by-step):

    Tavily -> seed companies -> find careers -> extract job-ish text -> LLM analyze -> flatten rows
    """
    seeds = discover_company_seeds(query, max_results=limit_companies * 5)
    seeds = seeds[:limit_companies]

    out = []
    llm_used = 0
    for s in seeds:
        careers_url = find_careers_url(s.homepage)
        if careers_url:
            try:
                text = extract_careers_text(careers_url)
            except Exception:
                text = None
            if text:
                try:
                    jobish = extract_jobish_lines(text)
                except Exception:
                    jobish = None
            else:
                jobish = None
        else:
            text = None
            jobish = None

        if jobish and llm_used < max_llm:
            company_name = s.homepage.replace("https://", "").replace("http://", "")
            try:
                llm_data = analyze_careers_json(company_name, jobish)
                llm_used += 1
            except Exception:
                llm_data = None
        else:
            llm_data = None
        out.append(
            {
                "title": s.title,
                "source_url": s.source_url,
                "homepage": s.homepage,
                "careers_url": careers_url,
                "careers_text": text,
                "jobish_text": jobish,
                "llm": llm_data,
            }
        )

    rows = []
    for item in out:
        if item.get("llm") and item.get("careers_url"):
            company = item["homepage"].replace("https://", "").replace("http://", "")
            rows += flatten_company_result(company, item["careers_url"], item["llm"])

    return rows
