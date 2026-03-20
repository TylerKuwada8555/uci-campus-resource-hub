from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RawResource:
    category: str
    name: str
    location: str
    contact_info: str
    description: str
    target_audience: str
    source_url: str


@dataclass(slots=True)
class ResourceCandidate:
    category: str
    name: str
    location: str
    contact_info: str
    description: str
    target_audience: str
    source_url: str
    quality_flags: tuple[str, ...]
    page_type: str
    audience_signals: tuple[str, ...]
    quality_score: int = 0
