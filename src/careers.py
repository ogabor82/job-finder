# src/careers.py
from __future__ import annotations

from typing import Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


CAREER_KEYWORDS = ["career", "job", "join", "work with", "hiring"]
BAD_HINTS = ["contact", "about", "privacy", "terms", "press", "blog"]


def looks_like_careers(text: str, href: str) -> bool:
    t = (text or "").lower().strip()
    h = (href or "").lower().strip()

    # reject anchors like "#contact"
    if h.startswith("#"):
        return False

    # reject obvious non-careers pages
    if any(b in t or b in h for b in BAD_HINTS):
        return False

    # accept careers-ish
    return any(k in t or k in h for k in CAREER_KEYWORDS)


def find_careers_url(homepage: str, *, timeout: int = 10) -> Optional[str]:
    """
    Fetch homepage HTML and try to find a careers/jobs link.
    Returns absolute URL (without trailing slash) or None.
    """
    try:
        resp = requests.get(
            homepage, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.find_all("a", href=True):
            text = a.get_text() or ""
            href = a["href"] or ""

            if looks_like_careers(text, href):
                url = urljoin(homepage, href)
                return url.rstrip("/")

    except Exception:
        return None

    return None


def extract_careers_text(
    careers_url: str, *, timeout: int = 10, max_lines: int = 200
) -> str:
    resp = requests.get(
        careers_url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # remove junk
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # basic cleanup
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if len(l) > 30]

    return "\n".join(lines[:max_lines])


JOB_HINTS = [
    "engineer",
    "developer",
    "scientist",
    "researcher",
    "intern",
    "backend",
    "full stack",
    "full-stack",
    "machine learning",
    "ml",
    "ai",
    "python",
    "django",
    "flask",
]


def extract_jobish_lines(
    text: str, *, window: int = 4, max_out_lines: int = 200
) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    keep = set()

    for i, line in enumerate(lines):
        low = line.lower()
        if any(h in low for h in JOB_HINTS):
            for j in range(max(0, i - window), min(len(lines), i + window + 1)):
                keep.add(j)

    out = [lines[i] for i in sorted(keep)]
    out = out[:max_out_lines]
    return "\n".join(out)
