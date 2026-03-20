import json
import re
import unittest
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from crawler.config import CrawlConfig


OUTPUT_PATH = Path("/Users/frank/uci-campus-resource-hub/crawler/output/uci_resources.json")
BAD_TITLE_RE = re.compile(
    r"(?:You may also be interested in|Top Requests:|Requirements$|For Students$|Office Hours$|Popular Methods$|What(?:’|')s the Difference|What is Campuswide Honors|After-Hours &$|Gynecologic &$|Psychiatry &$|Clinical$|Primary$|Specialty$|Step \d+:|We encourage ALL students|Explore Your Path|\bHome$|logo$|Launch Scholarship|Awards & Honors)",
    re.IGNORECASE,
)
BAD_DESCRIPTION_RE = re.compile(
    r"(?:holiday break|located across ring road|medical record processing time|monday, tuesday, thursday, and friday|i am a proud uci alumna|business hours)",
    re.IGNORECASE,
)
MALFORMED_CONTACT_RE = re.compile(
    r"(?:dsctesing@uci\.edu|(?<!\()\b\d{3}\)\s*\d{3}-\d{4}\b|ImmTrac2@|NYCvaxrecord@|@health\.nyc\.gov|@dshs\.texas\.gov)",
    re.IGNORECASE,
)
ALLOWED_MISSING_SEED_DOMAINS = {"merage.uci.edu"}


def canonical_domain(domain: str) -> str:
    if domain.startswith("www."):
        return domain[4:]
    if domain == "aid.ofas.uci.edu":
        return "ofas.uci.edu"
    return domain


class OutputAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = json.loads(OUTPUT_PATH.read_text())

    def test_output_schema_is_still_compatible(self) -> None:
        expected_keys = {
            "category",
            "name",
            "location",
            "contact_info",
            "description",
            "target_audience",
            "source_url",
        }
        for record in self.records:
            self.assertEqual(set(record.keys()), expected_keys)
            for key in ("category", "name", "location", "contact_info", "source_url"):
                self.assertTrue(record[key].strip(), msg=f"missing required {key}: {record}")

    def test_output_has_no_known_bad_title_patterns(self) -> None:
        bad_names = [record["name"] for record in self.records if BAD_TITLE_RE.search(record["name"])]
        self.assertEqual(bad_names, [])

    def test_output_has_no_known_bad_descriptions_or_contacts(self) -> None:
        bad_descriptions = [record["name"] for record in self.records if BAD_DESCRIPTION_RE.search(record["description"])]
        bad_contacts = [record["name"] for record in self.records if MALFORMED_CONTACT_RE.search(record["contact_info"])]
        self.assertEqual(bad_descriptions, [])
        self.assertEqual(bad_contacts, [])

    def test_output_has_real_housing_and_recreation_coverage(self) -> None:
        counts = Counter(record["category"] for record in self.records)
        self.assertGreaterEqual(counts["housing"], 1)
        self.assertGreaterEqual(counts["recreation"], 1)

    def test_output_covers_seed_domains_except_known_external_blocker(self) -> None:
        seed_domains: list[str] = []
        for url in CrawlConfig().seed_urls:
            domain = canonical_domain(urlparse(url).netloc)
            if domain not in seed_domains:
                seed_domains.append(domain)

        output_domains = {canonical_domain(urlparse(record["source_url"]).netloc) for record in self.records}
        missing = [domain for domain in seed_domains if domain not in output_domains]
        self.assertEqual(missing, sorted(ALLOWED_MISSING_SEED_DOMAINS))


if __name__ == "__main__":
    unittest.main()
