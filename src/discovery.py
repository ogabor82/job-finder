import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from tavily import TavilyClient
from typing import List

from src.models import CompanySeed


BLOCKED_DOMAINS = [
    "linkedin.com",
    "indeed.com",
    "ziprecruiter.com",
    "randstad",
    "crossover.com",
    "amazon.jobs",
    "youtube.com",
    "wikipedia.org",
    "substack.com",
    "medium.com",
    "workatastartup.com",
    "startup.google.com",
    "bus.umich.edu",
    "ycombinator.com",
    "crunchbase.com",
    "topstartups.io",
    "fortune.com",
    "informationweek.com",
    "neweconomies.co",
    "economictimes.indiatimes.com",
    "siliconangle.com",
    "calcalistech.com",
    "thequantuminsider.com",
]

BLOCKED_PATH_HINTS = [
    "/blog/",
    "/news/",
    "/article",
    "/posts/",
    "/journal/",
    "/alumni/",
    "/stories/",
    "/directory",
    "/job-board",
]


def _is_noise_url(url: str) -> bool:
    u = url.lower()
    p = urlparse(u)
    domain = p.netloc
    path = p.path
    if any(d in domain for d in BLOCKED_DOMAINS):
        return True
    if any(h in path for h in BLOCKED_PATH_HINTS):
        return True
    return False


def _root_homepage(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def discover_company_seeds(query: str, *, max_results: int = 20) -> List[CompanySeed]:
    load_dotenv()
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing TAVILY_API_KEY in environment (.env).")

    client = TavilyClient(api_key=api_key)
    resp = client.search(query=query, search_depth="advanced", max_results=max_results)

    seen = set()
    seeds: List[CompanySeed] = []

    for r in resp.get("results", []):
        url = r.get("url", "")
        title = r.get("title", "")
        if not url or _is_noise_url(url):
            continue

        hp = _root_homepage(url)
        if hp in seen:
            continue
        seen.add(hp)

        seeds.append(CompanySeed(title=title, source_url=url, homepage=hp))

    return seeds
