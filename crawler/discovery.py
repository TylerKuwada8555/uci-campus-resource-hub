from __future__ import annotations

from collections import Counter
from urllib.parse import urldefrag, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from crawler.config import CrawlConfig


def canonicalize_url(url: str) -> str:
    """Drop fragments and normalize scheme/host so dedupe is stable."""
    cleaned_url, _ = urldefrag(url.strip())
    parsed = urlparse(cleaned_url)
    netloc = parsed.netloc.lower()
    if netloc == "www.campusrec.uci.edu":
        netloc = "campusrec.uci.edu"
    normalized = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower())
    normalized = normalized._replace(netloc=netloc)
    return urlunparse(normalized)


def is_allowed_url(url: str, config: CrawlConfig) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    return any(parsed.netloc == domain or parsed.netloc.endswith(f".{domain}") for domain in config.allowed_domains)


def looks_relevant(url: str, anchor_text: str, config: CrawlConfig) -> bool:
    haystack = f"{url} {anchor_text}".lower()
    return any(keyword in haystack for keyword in config.discovery_keywords)


def has_discovery_deny_term(url: str, anchor_text: str, config: CrawlConfig) -> bool:
    haystack = f"{url} {anchor_text}".lower()
    return any(term in haystack for term in config.discovery_deny_terms)


def has_discovery_allow_term(url: str, anchor_text: str, config: CrawlConfig) -> bool:
    haystack = f"{url} {anchor_text}".lower()
    return any(term in haystack for term in config.discovery_allow_terms)


def should_visit(url: str, anchor_text: str, config: CrawlConfig) -> bool:
    canonical = canonicalize_url(url)
    if not is_allowed_url(canonical, config):
        return False
    if any(canonical.lower().endswith(suffix) for suffix in config.skip_file_suffixes):
        return False
    if has_discovery_deny_term(canonical, anchor_text, config):
        return False
    path = urlparse(canonical).path.lower()
    if any(term in path for term in ("vendor", "board", "social-media", "give", "permits", "contactlist", "faq", "mission", "values", "mind-your-zot", "local-hospitals")):
        return False
    if has_discovery_allow_term(canonical, anchor_text, config):
        return True
    return looks_relevant(canonical, anchor_text, config)


def extract_links(soup: BeautifulSoup, base_url: str, config: CrawlConfig) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        label = anchor.get_text(" ", strip=True)
        if not should_visit(href, label, config):
            continue

        canonical = canonicalize_url(href)
        if canonical in seen:
            continue
        seen.add(canonical)
        links.append(canonical)

    return links


def prioritize_links(
    urls: list[str],
    domain_counts: Counter[str],
    preferred_domains: set[str] | None = None,
) -> list[str]:
    """Spread crawl budget across domains instead of diving deeply into one site first."""
    preferred_domains = preferred_domains or set()
    preferred_terms = (
        "advis",
        "service",
        "support",
        "clinic",
        "pantry",
        "calfresh",
        "financial-aid",
        "disability",
        "accessibility",
        "testing",
        "housing",
        "recreation",
        "membership",
        "groupx",
        "training",
        "arc",
        "pool",
        "fitness",
        "app",
    )
    return sorted(
        urls,
        key=lambda url: (
            0 if urlparse(url).netloc in preferred_domains else 1,
            0 if any(term in url.lower() for term in preferred_terms) else 1,
            domain_counts[urlparse(url).netloc],
            urlparse(url).netloc,
            url,
        ),
    )
