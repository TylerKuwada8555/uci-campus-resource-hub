from __future__ import annotations

from typing import Any

from crawler.config import CrawlConfig
from crawler.models import ResourceCandidate


OUTPUT_KEYS = (
    "category",
    "name",
    "location",
    "contact_info",
    "description",
    "target_audience",
    "source_url",
)

REQUIRED_KEYS = ("category", "name", "location", "contact_info", "source_url")


def to_output_record(resource: ResourceCandidate) -> dict[str, str]:
    """Map a raw resource candidate into the persisted JSON schema."""
    return {
        "category": resource.category.strip(),
        "name": resource.name.strip(),
        "location": resource.location.strip(),
        "contact_info": resource.contact_info.strip(),
        "description": resource.description.strip(),
        "target_audience": resource.target_audience.strip(),
        "source_url": resource.source_url.strip(),
    }


def to_internal_record(resource: ResourceCandidate, config: CrawlConfig) -> dict[str, Any] | None:
    record = to_output_record(resource)
    category = record["category"].strip().lower().replace(" ", "_")
    if category == "accommodations":
        category = "accessibility"
    if category not in config.allowed_output_categories:
        return None
    record["category"] = category
    record["_quality_flags"] = list(resource.quality_flags)
    record["_page_type"] = resource.page_type
    record["_audience_signals"] = list(resource.audience_signals)
    record["_quality_score"] = resource.quality_score
    return record


def has_required_fields(record: dict[str, Any]) -> bool:
    return all(str(record.get(key, "")).strip() for key in REQUIRED_KEYS)
