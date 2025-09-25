from __future__ import annotations
import time, hashlib, datetime as dt
from typing import List, Dict, Any
import requests, feedparser
from tenacity import retry, wait_fixed, stop_after_attempt

def _now_utc():
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

def _safe_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()

def _coerce_date(feed_entry):
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(feed_entry, key, None) or (feed_entry.get(key) if hasattr(feed_entry, "get") else None)
        if val:
            return dt.datetime(*val[:6], tzinfo=dt.timezone.utc)
    return _now_utc()

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_rss(url: str, source_name: str, max_items: int) -> List[Dict[str, Any]]:
    feed = feedparser.parse(url, request_headers={"user-agent": "bioinfo-newsbot/1.0"})
    items = []
    for e in feed.entries[:max_items]:
        link = getattr(e, "link", "") or ""
        title = getattr(e, "title", "") or ""
        summary = getattr(e, "summary", "") or ""
        date = _coerce_date(e)
        uid = _safe_hash(f"{source_name}|{title}|{link}")
        items.append({
            "id": uid,
            "title": title.strip(),
            "url": link.strip(),
            "summary_raw": summary,
            "published_at": date.isoformat(),
            "source": source_name,
        })
    return items

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_arxiv(query: str, max_results: int) -> List[Dict[str, Any]]:
    ARXIV_API = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }
    r = requests.get(ARXIV_API, params=params, timeout=30)
    r.raise_for_status()
    feed = feedparser.parse(r.text)

    items = []
    for e in feed.entries:
        link = (getattr(e, "link", "") or "").strip()
        title = (getattr(e, "title", "") or "").strip()
        summary = getattr(e, "summary", "") or ""
        date = _coerce_date(e)
        uid = _safe_hash(f"arxiv|{title}|{link}")
        items.append({
            "id": uid,
            "title": title,
            "url": link,
            "summary_raw": summary,
            "published_at": date.isoformat(),
            "source": "arXiv",
        })
    return items

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_eupmc(query: str, max_results: int) -> List[Dict[str, Any]]:
    params = {
        "query": query,
        "pageSize": max_results,
        "format": "json",
        "sort": "PUB_DATE_D desc",
    }
    r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = []
    for rec in data.get("resultList", {}).get("result", []):
        title = rec.get("title") or ""
        link = f"https://europepmc.org/abstract/{rec.get('source')}/{rec.get('id')}"
        date_str = rec.get("firstPublicationDate") or rec.get("pubYear") or ""
        try:
            date = dt.datetime.fromisoformat(date_str.replace("Z","")).replace(tzinfo=dt.timezone.utc)
        except Exception:
            date = _now_utc()
        uid = _safe_hash(f"eupmc|{title}|{link}")
        items.append({
            "id": uid,
            "title": title.strip(),
            "url": link,
            "summary_raw": rec.get("abstractText",""),
            "published_at": date.isoformat(),
            "source": "Europe PMC",
        })
    return items

def fetch_from_config(src: dict) -> List[Dict[str, Any]]:
    t = src["type"]
    if t == "rss":
        return fetch_rss(src["url"], src["name"], src.get("max_items", 50))
    if t == "api_arxiv":
        return fetch_arxiv(src["query"], src.get("max_results", 50))
    if t == "api_eupmc":
        return fetch_eupmc(src["query"], src.get("max_results", 50))
    return []
