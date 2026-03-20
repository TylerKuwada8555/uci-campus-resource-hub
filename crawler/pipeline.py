from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from crawler.config import CrawlConfig
from crawler.discovery import canonicalize_url, extract_links, prioritize_links
from crawler.extractors import extract_resources
from crawler.fetcher import PageFetcher
from crawler.mapper import to_internal_record
from crawler.normalize import dedupe_records, normalize_record


LOGGER = logging.getLogger(__name__)


def load_seed_urls(seed_file: Path | None, config: CrawlConfig) -> list[str]:
    if seed_file is None:
        return [canonicalize_url(url) for url in config.seed_urls]

    urls = [
        canonicalize_url(line.strip())
        for line in seed_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return urls or [canonicalize_url(url) for url in config.seed_urls]


def resolve_domain_page_limit(url: str, config: CrawlConfig) -> int:
    domain = urlparse(url).netloc
    for limited_domain, limit in config.domain_page_limits.items():
        if domain == limited_domain or domain.endswith(f".{limited_domain}"):
            return limit
    return config.max_pages


def pop_next_url(
    queue: list[tuple[str, int]],
    seed_domains: set[str],
    pages_by_domain: Counter[str],
    accepted_by_domain: Counter[str],
) -> tuple[str, int]:
    best_index = min(
        range(len(queue)),
        key=lambda index: (
            0 if queue[index][0] and urlparse(queue[index][0]).netloc in seed_domains and accepted_by_domain[urlparse(queue[index][0]).netloc] == 0 else 1,
            0 if pages_by_domain[urlparse(queue[index][0]).netloc] == 0 else 1,
            pages_by_domain[urlparse(queue[index][0]).netloc],
            queue[index][1],
            urlparse(queue[index][0]).netloc,
            queue[index][0],
        ),
    )
    return queue.pop(best_index)


def run_crawl(config: CrawlConfig, seed_file: Path | None = None) -> list[dict[str, str]]:
    fetcher = PageFetcher(config)
    seed_urls = list(dict.fromkeys(load_seed_urls(seed_file, config)))
    seed_domains = {urlparse(url).netloc for url in seed_urls}
    queue: list[tuple[str, int]] = [(url, 0) for url in seed_urls]
    queued_urls = set(seed_urls)
    visited: set[str] = set()
    collected: list[dict[str, str]] = []
    pages_by_domain: Counter[str] = Counter()
    accepted_by_domain: Counter[str] = Counter()
    stats = {
        "pages_crawled": 0,
        "raw_candidates": 0,
        "rejected_candidates": 0,
        "accepted_candidates": 0,
        "repaired_categories": 0,
        "invalid_categories": 0,
        "counseling_reclassified_career": 0,
        "counseling_reclassified_academic": 0,
        "recreation_candidates": 0,
        "recreation_kept": 0,
    }

    while queue and len(visited) < config.max_pages:
        url, depth = pop_next_url(queue, seed_domains, pages_by_domain, accepted_by_domain)
        queued_urls.discard(url)
        if url in visited:
            continue
        if pages_by_domain[urlparse(url).netloc] >= resolve_domain_page_limit(url, config):
            continue
        visited.add(url)
        pages_by_domain[urlparse(url).netloc] += 1
        stats["pages_crawled"] += 1
        LOGGER.info("Crawling [%s/%s] %s", len(visited), config.max_pages, url)

        result = fetcher.fetch(url)
        if result is None:
            continue

        for raw_resource in extract_resources(result.url, result.soup, config):
            stats["raw_candidates"] += 1
            if raw_resource.category == "recreation":
                stats["recreation_candidates"] += 1
            if "counseling.uci.edu" in raw_resource.source_url and raw_resource.category == "career":
                stats["counseling_reclassified_career"] += 1
            if "counseling.uci.edu" in raw_resource.source_url and raw_resource.category == "academic":
                stats["counseling_reclassified_academic"] += 1
            mapped = to_internal_record(raw_resource, config)
            if mapped is None:
                stats["invalid_categories"] += 1
                continue
            if raw_resource.category == "accommodations" and mapped["category"] == "accessibility":
                stats["repaired_categories"] += 1
            record = normalize_record(mapped, config)
            if record is not None:
                collected.append(record)
                accepted_by_domain[urlparse(record["source_url"]).netloc] += 1
                stats["accepted_candidates"] += 1
                if record["category"] == "recreation":
                    stats["recreation_kept"] += 1
            else:
                stats["rejected_candidates"] += 1

        if depth >= config.max_depth:
            continue

        preferred_domains = {domain for domain in seed_domains if accepted_by_domain[domain] == 0}
        child_urls = prioritize_links(
            extract_links(result.soup, result.url, config),
            Counter(urlparse(item[0]).netloc for item in queue),
            preferred_domains=preferred_domains,
        )
        for child_url in child_urls:
            if child_url in visited or child_url in queued_urls:
                continue
            if pages_by_domain[urlparse(child_url).netloc] >= resolve_domain_page_limit(child_url, config):
                continue
            queue.append((child_url, depth + 1))
            queued_urls.add(child_url)

    final_records = dedupe_records(collected)
    LOGGER.info(
        "Crawl summary: pages=%s raw_candidates=%s accepted=%s rejected=%s repaired_categories=%s invalid_categories=%s counseling_to_career=%s counseling_to_academic=%s recreation_candidates=%s recreation_kept=%s final=%s",
        stats["pages_crawled"],
        stats["raw_candidates"],
        stats["accepted_candidates"],
        stats["rejected_candidates"],
        stats["repaired_categories"],
        stats["invalid_categories"],
        stats["counseling_reclassified_career"],
        stats["counseling_reclassified_academic"],
        stats["recreation_candidates"],
        stats["recreation_kept"],
        len(final_records),
    )
    return final_records


def save_records(records: list[dict[str, str]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path
