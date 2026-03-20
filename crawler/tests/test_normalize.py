import unittest

from crawler.config import CrawlConfig
from crawler.normalize import dedupe_records, normalize_record


class NormalizeTests(unittest.TestCase):
    def test_normalize_record_rejects_missing_required_fields(self) -> None:
        config = CrawlConfig()
        record = {
            "category": "health",
            "name": "Student Health Center",
            "location": "",
            "contact_info": "Phone: (949) 824-5301",
            "description": "",
            "target_audience": "",
            "source_url": "https://studenthealth.uci.edu/",
        }
        self.assertIsNone(normalize_record(record, config))

    def test_normalize_record_keeps_compatibility_fields(self) -> None:
        config = CrawlConfig()
        record = {
            "category": "financial aid",
            "name": "Office of Financial Aid",
            "location": "102 Aldrich Hall, Irvine, CA 92697",
            "contact_info": "Phone: (949) 824-8262",
            "description": "",
            "target_audience": "",
            "source_url": "https://www.ofas.uci.edu/contact-us/index.php",
        }
        normalized = normalize_record(record, config)
        self.assertIsNotNone(normalized)
        assert normalized is not None
        self.assertEqual(normalized["category"], "financial")
        self.assertEqual(normalized["description"], "")
        self.assertEqual(normalized["target_audience"], "")

    def test_normalize_category_repairs_accommodations_to_accessibility(self) -> None:
        config = CrawlConfig()
        record = {
            "category": "accommodations",
            "name": "Disability Services Center",
            "location": "234 Pereira Drive, Irvine, CA 92697-5250",
            "contact_info": "Email: dsc@uci.edu",
            "description": "Accessibility support for students.",
            "target_audience": "UCI students",
            "source_url": "https://dsc.uci.edu/",
        }
        normalized = normalize_record(record, config)
        self.assertIsNotNone(normalized)
        assert normalized is not None
        self.assertEqual(normalized["category"], "accessibility")

    def test_dedupe_prefers_richer_record(self) -> None:
        records = [
            {
                "category": "academic",
                "name": "LARC",
                "location": "3500 Anteater Learning Pavilion, Irvine, CA 92697-3850",
                "contact_info": "Phone: (949) 824-6451",
                "description": "",
                "target_audience": "",
                "source_url": "https://larc.uci.edu/",
            },
            {
                "category": "academic",
                "name": "LARC",
                "location": "3500 Anteater Learning Pavilion, Irvine, CA 92697-3850",
                "contact_info": "Phone: (949) 824-6451 | Email: larc@uci.edu",
                "description": "Academic support center.",
                "target_audience": "UCI students",
                "source_url": "https://larc.uci.edu/",
            },
        ]

        deduped = dedupe_records(records)
        self.assertEqual(len(deduped), 1)
        self.assertIn("Email", deduped[0]["contact_info"])
        self.assertEqual(deduped[0]["description"], "Academic support center.")

    def test_normalize_record_rejects_editorial_counseling_titles(self) -> None:
        config = CrawlConfig()
        record = {
            "category": "health",
            "name": "UCI Counseling Center - Mind Your Zot!",
            "location": "203 Student Services 1, Irvine, CA 92697-2200",
            "contact_info": "Phone: (949) 824-6457",
            "description": "As the quarter draws to a close, and the academic pressure gets turned up...",
            "target_audience": "UCI students",
            "source_url": "https://counseling.uci.edu/managing-perfectionism/",
        }
        self.assertIsNone(normalize_record(record, config))


if __name__ == "__main__":
    unittest.main()
