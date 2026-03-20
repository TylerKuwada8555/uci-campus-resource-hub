from __future__ import annotations

import re

from crawler.config import CrawlConfig
from crawler.mapper import OUTPUT_KEYS, has_required_fields


WHITESPACE_RE = re.compile(r"\s+")
ELLIPSIS_RE = re.compile(r"(?:\[\u2026\]|\.\.\.)")
PHONE_RE = re.compile(r"\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
GENERIC_NAME_RE = re.compile(
    r"\b(?:about(?: us)?|contact(?: us)?|welcome!?|home|logo|for current students|hours of operation|events calendar|meet our staff|meet the staff|what is(?: the)?|mind your zot|resources(?: for students)?|what services are right for me)\b",
    re.IGNORECASE,
)
FRAGMENT_NAME_RE = re.compile(
    r"(?:for students|office hours|popular methods|process overview|requirements|you may also be interested in(?:\.\.\.)?|top requests:?|step \d+:|we encourage all students)",
    re.IGNORECASE,
)
BOILERPLATE_RE = re.compile(
    r"(for life threatening emergencies|for crisis care needs 24/7|privacy & legal notice|read more|university of california, irvine)",
    re.IGNORECASE,
)
BAD_DESCRIPTION_RE = re.compile(
    r"(holiday break|located across ring road|medical record processing time|monday, tuesday, thursday, and friday|business hours|i am a proud uci alumna|phone\s*:|fax\s*:)",
    re.IGNORECASE,
)
ADMIN_RE = re.compile(
    r"\b(?:staff|calendar|feedback|complaint|policy|rights|responsibilities|report|nondiscrimination|faculty|employee|employees|parents|closed|holiday)\b",
    re.IGNORECASE,
)
MALFORMED_CONTACT_RE = re.compile(r"(?: (?<!\()\b\d{3}\)\s*\d{3}-\d{4}\b | \(\d{3}\)\d{3}-\d{4} | dsctesing@uci\.edu )", re.IGNORECASE | re.VERBOSE)
EXTERNAL_EMAIL_RE = re.compile(r"@(?!(?:[\w.-]+\.)?uci\.edu\b)[\w.-]+", re.IGNORECASE)


def clean_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value or "").strip()


def normalize_category(value: str, config: CrawlConfig) -> str:
    cleaned = clean_text(value).lower().replace(" ", "_")
    if cleaned == "accommodations":
        cleaned = "accessibility"
    if cleaned in config.allowed_output_categories:
        return cleaned

    for category, keywords in config.category_keywords.items():
        if cleaned == category:
            return category
        if any(cleaned == keyword.replace(" ", "_") for keyword in keywords):
            return category

    return ""


def normalize_name(value: str) -> str:
    cleaned = clean_text(value)
    cleaned = re.sub(r"\s+-\s+(?:About(?: Us)?|Contact(?: Us)?|Welcome!?|For Current Students)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(?:About(?: Us)?|Contact(?: Us)?|Welcome!?|For Current Students)\s+-\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^What is the\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" -")


def normalize_description(value: str) -> str:
    cleaned = clean_text(value)
    cleaned = ELLIPSIS_RE.sub("", cleaned)
    if BOILERPLATE_RE.search(cleaned) or BAD_DESCRIPTION_RE.search(cleaned):
        return ""
    if len(cleaned) > 280:
        cleaned = cleaned[:280].rsplit(" ", 1)[0].rstrip(" .,;:") + "."
    return cleaned


def contact_looks_noisy(value: str) -> bool:
    emails = EMAIL_RE.findall(value)
    phones = PHONE_RE.findall(value)
    return (
        MALFORMED_CONTACT_RE.search(value) is not None
        or EXTERNAL_EMAIL_RE.search(value) is not None
        or len(emails) > 4
        or len(phones) > 4
    )


def quality_score(record: dict[str, str]) -> int:
    score = 0
    name = record["name"]
    description = record["description"]
    audience = record["target_audience"]
    contact_info = record["contact_info"]
    page_type = record.get("_page_type", "")
    flags = set(record.get("_quality_flags", []))

    if name and not GENERIC_NAME_RE.search(name) and len(name) <= 90:
        score += 4
    if description and not BOILERPLATE_RE.search(description) and 40 <= len(description) <= 260:
        score += 3
    if audience:
        score += 2
    if record["category"] in name.lower() or any(token in name.lower() for token in ("advis", "pantry", "health", "counsel", "financial", "housing", "accessibility", "disability")):
        score += 1
    if GENERIC_NAME_RE.search(name):
        score -= 5
    if FRAGMENT_NAME_RE.search(name):
        score -= 6
    if len(name) > 120:
        score -= 5
    if BOILERPLATE_RE.search(description):
        score -= 5
    if BAD_DESCRIPTION_RE.search(description):
        score -= 6
    if ADMIN_RE.search(name) or page_type in {"policy", "feedback", "event", "staff", "announcement"}:
        score -= 6
    if any(term in description.lower() for term in ("holiday break", "register for spring programs", "learn more", "scroll to the bottom", "redirect")):
        score -= 4
    if "non_student_audience" in flags:
        score -= 8
    if contact_looks_noisy(contact_info):
        score -= 8
    return score


def normalize_record(record: dict[str, str], config: CrawlConfig) -> dict[str, str] | None:
    normalized = {key: clean_text(record.get(key, "")) for key in OUTPUT_KEYS}
    normalized["_quality_flags"] = list(record.get("_quality_flags", []))
    normalized["_page_type"] = str(record.get("_page_type", "")).strip()
    normalized["_audience_signals"] = list(record.get("_audience_signals", []))
    normalized["category"] = normalize_category(normalized["category"], config)
    normalized["name"] = normalize_name(normalized["name"])
    normalized["description"] = normalize_description(normalized["description"])

    if not normalized["category"]:
        return None
    if normalized["category"] not in config.allowed_output_categories:
        return None
    if not has_required_fields(normalized):
        return None
    if GENERIC_NAME_RE.search(normalized["name"]) or FRAGMENT_NAME_RE.search(normalized["name"]):
        return None
    if contact_looks_noisy(normalized["contact_info"]):
        return None

    normalized["_quality_score"] = quality_score(normalized)
    if normalized["_quality_score"] < 0:
        return None
    return normalized


def merge_contact_info(primary: str, secondary: str) -> str:
    values = [item.strip() for item in (primary + " | " + secondary).split("|") if item.strip()]
    seen: list[str] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return " | ".join(seen)


def dedupe_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Merge duplicate discoveries while keeping the higher-quality version."""
    deduped: list[dict[str, str]] = []
    index_by_key: dict[tuple[str, str], int] = {}

    for record in records:
        service_identity = normalize_name(record["name"]).lower()
        if service_identity.startswith("uci "):
            service_identity = service_identity[4:]
        key = (record["category"], service_identity)
        if key not in index_by_key:
            index_by_key[key] = len(deduped)
            deduped.append(record)
            continue

        existing = deduped[index_by_key[key]]
        if record.get("_quality_score", 0) > existing.get("_quality_score", 0):
            winner, loser = record, existing
        else:
            winner, loser = existing, record

        winner["contact_info"] = merge_contact_info(winner["contact_info"], loser["contact_info"])
        if not winner["description"] and loser["description"]:
            winner["description"] = loser["description"]
        if not winner["target_audience"] and loser["target_audience"]:
            winner["target_audience"] = loser["target_audience"]
        deduped[index_by_key[key]] = winner

    cleaned = [{key: value for key, value in item.items() if not key.startswith("_")} for item in deduped]
    cleaned.sort(key=lambda item: (item["category"], item["name"].lower(), item["source_url"].lower()))
    return cleaned
