import unittest

from bs4 import BeautifulSoup

from crawler.config import CrawlConfig
from crawler.extractors import build_resource_candidate, parse_json_ld


def build_candidate(url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    return build_resource_candidate(url, soup, CrawlConfig())


class ExtractorQualityTests(unittest.TestCase):
    def test_basic_needs_application_process_uses_canonical_title_and_clean_location(self) -> None:
        candidate = build_candidate(
            "https://basicneeds.uci.edu/calfresh-application-process/",
            """
            <html>
              <head>
                <title>Application Process | UCI Basic Needs Center</title>
                <meta name="description" content="CalFresh helps UCI students access food benefits and step-by-step application support.">
              </head>
              <body>
                <main>
                  <h1>Application Process</h1>
                  <p>CalFresh helps UCI students access food benefits and step-by-step application support from the Basic Needs Center.</p>
                  <div>10 October March 5th September 5th</div>
                  <div>800 W Peltason Dr</div>
                  <div>Irvine, CA 92617</div>
                  <div>Email: basicneeds@uci.edu</div>
                  <div>Phone: 949-824-0607</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.name, "UCI Basic Needs Center - CalFresh Application Process")
        self.assertEqual(candidate.location, "800 W Peltason Dr Irvine, CA 92617")

    def test_dsc_contact_page_uses_general_contact_title(self) -> None:
        candidate = build_candidate(
            "https://dsc.uci.edu/contact/",
            """
            <html>
              <body>
                <main>
                  <h1>Office Hours</h1>
                  <p>Contact the Disability Services Center for accommodations support and general questions from enrolled students.</p>
                  <div class="contact-card">
                    <p>Phone: 949-824-7494</p>
                    <p>Email: dsc@uci.edu</p>
                  </div>
                  <div>234 Pereira Drive</div>
                  <div>Irvine, CA 92697-5250</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.name, "UCI Disability Services Center - General Contact")
        self.assertEqual(candidate.contact_info, "Phone: (949) 824-7494 | Email: dsc@uci.edu")

    def test_dsc_policy_jsonld_page_is_excluded(self) -> None:
        soup = BeautifulSoup(
            """
            <html>
              <body>
                <script type="application/ld+json">
                  {
                    "@type": "Organization",
                    "name": "Disability Services Center (DSC)",
                    "telephone": "949-824-7494",
                    "email": "dsc@uci.edu",
                    "description": "Support for students."
                  }
                </script>
              </body>
            </html>
            """,
            "html.parser",
        )
        resources = parse_json_ld(soup, "https://dsc.uci.edu/dsc-policies/", CrawlConfig())
        self.assertEqual(resources, [])

    def test_student_health_after_hours_uses_canonical_title(self) -> None:
        candidate = build_candidate(
            "https://studenthealth.uci.edu/after-hours-urgent-care/",
            """
            <html>
              <head>
                <meta name="description" content="After-hours urgent care helps UCI students get follow-up support when the Student Health Center is closed.">
              </head>
              <body>
                <main>
                  <h1>After-Hours &amp;</h1>
                  <p>After-hours urgent care helps UCI students get follow-up support when the Student Health Center is closed.</p>
                  <div class="contact-card">
                    <a href="tel:9498245301">(949) 824-5301</a>
                    <a href="tel:8664402752">(866) 440-2752</a>
                    <a href="mailto:shc-medical-records@uci.edu">shc-medical-records@uci.edu</a>
                  </div>
                  <div>501 Student Health</div>
                  <div>Irvine, CA 92697-5200</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.name, "UCI Student Health Center - After-Hours Urgent Care")
        self.assertIn("(949) 824-5301", candidate.contact_info)
        self.assertIn("(866) 440-2752", candidate.contact_info)

    def test_student_health_immunizations_filters_external_emails(self) -> None:
        candidate = build_candidate(
            "https://studenthealth.uci.edu/immunizations/",
            """
            <html>
              <head>
                <meta name="description" content="Immunization services help UCI students complete required vaccine and TB clearance steps.">
              </head>
              <body>
                <main>
                  <h1>Immunizations</h1>
                  <p>Immunization services help UCI students complete required vaccine and TB clearance steps.</p>
                  <div class="contact-card">
                    <p>Email: SHC-immunization@uci.edu</p>
                    <p>Email: ImmTrac2@dshs.texas.gov</p>
                    <p>Email: NYCvaxrecord@health.nyc.gov</p>
                    <p>Phone: 949-824-5301</p>
                  </div>
                  <div>501 Student Health</div>
                  <div>Irvine, CA 92697-5200</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertIn("shc-immunization@uci.edu", candidate.contact_info)
        self.assertNotIn("ImmTrac2@dshs.texas.gov", candidate.contact_info)
        self.assertNotIn("NYCvaxrecord@health.nyc.gov", candidate.contact_info)

    def test_career_article_page_is_excluded(self) -> None:
        candidate = build_candidate(
            "https://career.uci.edu/job-search-strategies/",
            """
            <html>
              <body>
                <main>
                  <h1>You may also be interested in...</h1>
                  <p>The job search is a process. First, you have to discover what career options might interest you.</p>
                  <div>100 Student Services 1</div>
                  <div>Irvine, CA 92697-2075</div>
                  <div>Email: career@uci.edu</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNone(candidate)

    def test_nursing_homepage_is_excluded(self) -> None:
        candidate = build_candidate(
            "https://nursing.uci.edu/",
            """
            <html>
              <body>
                <main>
                  <h1>Explore Your Path</h1>
                  <p>At the Sue &amp; Bill Gross School of Nursing, we are dedicated to preparing the next generation of nurses.</p>
                  <div>854 Health Sciences Road</div>
                  <div>Irvine, CA 92697-3959</div>
                  <div>Phone: 949-824-1514</div>
                </main>
              </body>
            </html>
            """,
        )
        self.assertIsNone(candidate)


if __name__ == "__main__":
    unittest.main()
