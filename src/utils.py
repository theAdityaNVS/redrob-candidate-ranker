"""Data loading and preprocessing for the candidate ranking engine."""
import json
from pathlib import Path
from typing import Iterator, Dict, Any, Optional
from datetime import date, datetime


def load_candidates(path: str) -> Iterator[Dict[str, Any]]:
    """Stream candidates from a JSONL file one at a time."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def days_since(date_str: str, ref_date: date) -> int:
    """Return days since date_str (ISO format) from ref_date."""
    if not date_str:
        return 9999
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (ref_date - d).days
    except (ValueError, TypeError):
        return 9999


def parse_date(date_str: str) -> Optional[date]:
    """Parse ISO date string, return None on failure."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
