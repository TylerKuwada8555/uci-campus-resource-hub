import unittest

from crawler.config import CrawlConfig
from crawler.mapper import has_required_fields, to_internal_record, to_output_record
from crawler.models import ResourceCandidate


class MapperTests(unittest.TestCase):
    def test_to_output_record_uses_expected_keys(self) -> None:
        resource = ResourceCandidate(
            category="health",
            name="Student Health Center",
            location="501 Student Health, Irvine, CA 92697-5200",
            contact_info="Phone: (949) 824-5301",
            description="Medical services for students.",
            target_audience="UCI students",
            source_url="https://studenthealth.uci.edu/",
            quality_flags=(),
            page_type="resource",
            audience_signals=("students",),
            quality_score=0,
        )

        record = to_output_record(resource)
        self.assertEqual(
            tuple(record.keys()),
            (
                "category",
                "name",
                "location",
                "contact_info",
                "description",
                "target_audience",
                "source_url",
            ),
        )
        self.assertTrue(has_required_fields(record))

    def test_to_internal_record_enforces_accessibility_schema(self) -> None:
        config = CrawlConfig()
        resource = ResourceCandidate(
            category="accommodations",
            name="DSC",
            location="234 Pereira Drive, Irvine, CA 92697-5250",
            contact_info="Email: dsc@uci.edu",
            description="Accessibility services.",
            target_audience="UCI students",
            source_url="https://dsc.uci.edu/",
            quality_flags=(),
            page_type="resource",
            audience_signals=("students",),
            quality_score=0,
        )
        internal = to_internal_record(resource, config)
        self.assertIsNotNone(internal)
        assert internal is not None
        self.assertEqual(internal["category"], "accessibility")

    def test_to_internal_record_keeps_recreation_category(self) -> None:
        config = CrawlConfig()
        resource = ResourceCandidate(
            category="recreation",
            name="UCI Campus Recreation - ARC Hours",
            location="680 California Ave, Irvine, CA 92697",
            contact_info="Email: camprec@uci.edu",
            description="Current ARC hours and facility schedule.",
            target_audience="UCI students",
            source_url="https://campusrec.uci.edu/arc/hours.html",
            quality_flags=(),
            page_type="resource",
            audience_signals=("students",),
            quality_score=0,
        )
        internal = to_internal_record(resource, config)
        self.assertIsNotNone(internal)
        assert internal is not None
        self.assertEqual(internal["category"], "recreation")


if __name__ == "__main__":
    unittest.main()
