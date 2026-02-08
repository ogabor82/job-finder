# src/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


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
