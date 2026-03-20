from __future__ import annotations

import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from crawler.config import CrawlConfig


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class FetchResult:
    url: str
    html: str
    soup: BeautifulSoup
    status_code: int


class PageFetcher:
    """HTTP client wrapper so crawl behavior stays easy to swap or mock later."""

    def __init__(self, config: CrawlConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": config.user_agent})

    def fetch(self, url: str) -> FetchResult | None:
        try:
            response = self._session.get(url, timeout=self._config.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            LOGGER.warning("Failed to fetch %s: %s", url, exc)
            return None

        content_type = response.headers.get("Content-Type", "").lower()
        if "html" not in content_type:
            LOGGER.info("Skipping non-HTML content at %s (%s)", url, content_type or "unknown")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        return FetchResult(
            url=response.url,
            html=response.text,
            soup=soup,
            status_code=response.status_code,
        )
