from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = BASE_DIR / "output" / "uci_resources.json"

ALLOWED_OUTPUT_CATEGORIES = (
    "basic_needs",
    "health",
    "academic",
    "career",
    "financial",
    "housing",
    "accessibility",
    "recreation",
)


DEFAULT_ALLOWED_DOMAINS = (
    "basicneeds.uci.edu",
    "counseling.uci.edu",
    "studenthealth.uci.edu",
    "career.uci.edu",
    "ofas.uci.edu",
    "aid.ofas.uci.edu",
    "dsc.uci.edu",
    "larc.uci.edu",
    "writingcenter.uci.edu",
    "housing.uci.edu",
    "campusrec.uci.edu",
    "www.campusrec.uci.edu",
    "ics.uci.edu",
    "tutoring.ics.uci.edu",
    "oai.ics.uci.edu",
    "undergraduate.eng.uci.edu",
    "advise.education.uci.edu",
    "undergraduate.bio.uci.edu",
    "hq.humanities.uci.edu",
    "honors.uci.edu",
    "pharmsci.uci.edu",
    "nursing.uci.edu",
    "merage.uci.edu",
    "law.uci.edu",
    "www.law.uci.edu",
    "www.arts.uci.edu",
    "studentwellness.uci.edu",
    "care.uci.edu",
    "ssihi.uci.edu",
)


DEFAULT_SEED_URLS = (
    "https://basicneeds.uci.edu/",
    "https://basicneeds.uci.edu/fresh-pantry/",
    "https://basicneeds.uci.edu/calfresh-application-process/",
    "https://counseling.uci.edu/contact-us/emergency-assistance/",
    "https://counseling.uci.edu/services/referral-and-resource-support/",
    "https://studenthealth.uci.edu/",
    "https://dsc.uci.edu/contact/",
    "https://career.uci.edu/about/contact-us/",
    "https://www.ofas.uci.edu/contact-us/index.php",
    "https://writingcenter.uci.edu/about/",
    "https://larc.uci.edu/",
    "https://housing.uci.edu/",
    "https://campusrec.uci.edu/",
    "https://campusrec.uci.edu/membership/index.html",
    "https://campusrec.uci.edu/groupx/index.html",
    "https://campusrec.uci.edu/arc/hours.html",
    "https://campusrec.uci.edu/training/index.html",
    "https://campusrec.uci.edu/app.html",
    "https://ics.uci.edu/academics/undergrad/contact/",
    "https://undergraduate.eng.uci.edu/contact-us/",
    "https://advise.education.uci.edu/contact-us.html",
    "https://undergraduate.bio.uci.edu/contact-us/",
    "https://hq.humanities.uci.edu/undergrad/about/acad_advising.php",
    "https://honors.uci.edu/chchat/",
    "https://pharmsci.uci.edu/for-current-students/",
    "https://nursing.uci.edu/",
    "https://merage.uci.edu/programs/undergraduate/contact-us.html",
    "https://law.uci.edu/admission/tuition-aid/",
    "https://www.arts.uci.edu/student-affairs-advising",
)


CATEGORY_KEYWORDS = {
    "basic_needs": ("basic needs", "pantry", "calfresh", "food", "emergency meal"),
    "health": ("health", "counseling", "wellness", "medical", "crisis", "mental health"),
    "accessibility": (
        "disability",
        "accommodation",
        "accessibility",
        "assistive technology",
        "testing",
        "dsc",
        "dhh",
        "alternate instructional materials",
    ),
    "career": ("career", "internship", "job", "employment", "resume"),
    "financial": ("financial aid", "scholarship", "loan", "tuition", "grant"),
    "academic": ("academic", "advising", "writing center", "tutoring", "larc", "honors"),
    "housing": ("housing", "off-campus housing", "residential", "roommate", "dorm", "residence", "apartment", "student housing", "sponsored housing"),
    "recreation": ("recreation", "fitness", "gym", "sports", "campus rec"),
}


COUNSELING_DIRECT_HEALTH_TERMS = (
    "therapy",
    "screening",
    "appointment",
    "crisis",
    "referral",
    "counseling",
    "emergency assistance",
    "walk-in clinics",
)

COUNSELING_PROGRAM_TERMS = (
    "mentor",
    "mentoring",
    "educator",
    "coach",
    "peer program",
    "leadership",
)

COUNSELING_EDITORIAL_TERMS = (
    "mind your zot",
    "feeling sick and have an appointment",
    "resources",
    "resources for students",
    "local hospitals",
    "forms and documents",
)


DOMAIN_NAME_HINTS = {
    "basicneeds.uci.edu": "UCI Basic Needs Center",
    "counseling.uci.edu": "UCI Counseling Center",
    "studenthealth.uci.edu": "UCI Student Health Center",
    "dsc.uci.edu": "UCI Disability Services Center",
    "career.uci.edu": "UCI Division of Career Pathways",
    "ofas.uci.edu": "UCI Office of Financial Aid and Scholarships",
    "www.ofas.uci.edu": "UCI Office of Financial Aid and Scholarships",
    "writingcenter.uci.edu": "UCI Writing Center",
    "larc.uci.edu": "UCI Learning & Academic Resource Center",
    "housing.uci.edu": "UCI Student Housing",
    "campusrec.uci.edu": "UCI Campus Recreation",
    "www.campusrec.uci.edu": "UCI Campus Recreation",
    "ics.uci.edu": "UCI Donald Bren School of Information and Computer Sciences",
    "undergraduate.eng.uci.edu": "UCI Samueli School of Engineering",
    "advise.education.uci.edu": "UCI School of Education",
    "undergraduate.bio.uci.edu": "UCI Charlie Dunlop School of Biological Sciences",
    "hq.humanities.uci.edu": "UCI School of Humanities",
    "honors.uci.edu": "UCI Campuswide Honors Collegium",
    "pharmsci.uci.edu": "UCI School of Pharmacy & Pharmaceutical Sciences",
    "nursing.uci.edu": "UCI Sue & Bill Gross School of Nursing",
    "merage.uci.edu": "UCI Paul Merage School of Business",
    "law.uci.edu": "UCI School of Law",
    "www.arts.uci.edu": "UCI Claire Trevor School of the Arts",
}


DISCOVERY_KEYWORDS = tuple(
    keyword
    for keywords in CATEGORY_KEYWORDS.values()
    for keyword in keywords
) + (
    "student",
    "students",
    "support",
    "resource",
    "resources",
    "contact",
    "services",
)


DISCOVERY_ALLOW_TERMS = (
    "advis",
    "service",
    "support",
    "resource",
    "appointment",
    "clinic",
    "care",
    "pantry",
    "calfresh",
    "financial-aid",
    "financial",
    "accessibility",
    "accommodation",
    "disability",
    "assistive",
    "dsc",
    "dhh",
    "register",
    "testing",
    "housing",
    "off-campus-housing",
    "apartment",
    "roommate",
    "residence",
    "walk-in",
    "tutoring",
    "writing",
    "career",
    "health",
    "wellness",
    "aid",
    "student",
    "basic-needs",
    "recreation",
    "membership",
    "groupx",
    "training",
    "arc",
    "pool",
    "fitness",
    "app",
)


DISCOVERY_DENY_TERMS = (
    "news",
    "announcement",
    "closed",
    "holiday",
    "staff",
    "team",
    "calendar",
    "event",
    "special-event",
    "special-events",
    "feedback",
    "complaint",
    "policy",
    "report",
    "training",
    "parents",
    "faculty-staff",
    "faculty",
    "employee",
    "employees",
    "meet-our-staff",
    "faq",
    "mission",
    "values",
    "social-media",
    "vendor",
    "board",
    "give",
    "permits",
    "contactlist",
    "mind-your-zot",
    "local-hospitals",
)


RESOURCE_ALLOW_TERMS = (
    "advising",
    "appointment",
    "services",
    "support",
    "resources-for-students",
    "resource support",
    "clinic",
    "care",
    "pantry",
    "calfresh",
    "financial aid",
    "financial-aid",
    "accessibility",
    "accommodation",
    "disability",
    "assistive technology",
    "assistive",
    "dsc",
    "dhh",
    "register",
    "testing",
    "housing",
    "off-campus housing",
    "student housing",
    "sponsored housing",
    "apartment",
    "roommate",
    "walk-in",
    "tutoring",
    "writing",
    "career",
    "student health",
    "counseling",
    "therapy",
    "pharmacy",
    "nutrition",
    "immunization",
    "primary care",
    "disability",
    "basic needs",
    "recreation",
    "membership",
    "groupx",
    "training",
    "arc",
    "pool",
    "fitness",
    "app",
)


RESOURCE_DENY_TERMS = (
    "announcement",
    "news",
    "closed",
    "holiday",
    "staff",
    "team",
    "calendar",
    "event",
    "special events",
    "feedback",
    "complaint",
    "policy",
    "rights",
    "responsibilities",
    "report",
    "nondiscrimination",
    "faculty",
    "staff only",
    "employee",
    "employees",
    "parents",
    "faq",
    "mission",
    "values",
    "social media",
    "vendor",
    "board",
    "donate",
    "give",
    "permits",
)


GENERIC_TITLES = (
    "about",
    "about us",
    "contact",
    "contact us",
    "welcome",
    "welcome!",
    "for current students",
    "hours of operation",
    "events calendar",
    "meet our staff",
)


SKIP_FILE_SUFFIXES = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
    ".mp4",
    ".mov",
)


@dataclass(slots=True)
class CrawlConfig:
    """Configuration object used throughout the crawler pipeline."""

    seed_urls: list[str] = field(default_factory=lambda: list(DEFAULT_SEED_URLS))
    allowed_domains: tuple[str, ...] = DEFAULT_ALLOWED_DOMAINS
    allowed_output_categories: tuple[str, ...] = ALLOWED_OUTPUT_CATEGORIES
    category_keywords: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {key: tuple(value) for key, value in CATEGORY_KEYWORDS.items()}
    )
    domain_name_hints: dict[str, str] = field(default_factory=lambda: dict(DOMAIN_NAME_HINTS))
    discovery_keywords: tuple[str, ...] = DISCOVERY_KEYWORDS
    discovery_allow_terms: tuple[str, ...] = DISCOVERY_ALLOW_TERMS
    discovery_deny_terms: tuple[str, ...] = DISCOVERY_DENY_TERMS
    resource_allow_terms: tuple[str, ...] = RESOURCE_ALLOW_TERMS
    resource_deny_terms: tuple[str, ...] = RESOURCE_DENY_TERMS
    generic_titles: tuple[str, ...] = GENERIC_TITLES
    counseling_direct_health_terms: tuple[str, ...] = COUNSELING_DIRECT_HEALTH_TERMS
    counseling_program_terms: tuple[str, ...] = COUNSELING_PROGRAM_TERMS
    counseling_editorial_terms: tuple[str, ...] = COUNSELING_EDITORIAL_TERMS
    skip_file_suffixes: tuple[str, ...] = SKIP_FILE_SUFFIXES
    domain_page_limits: dict[str, int] = field(
        default_factory=lambda: {
            "basicneeds.uci.edu": 10,
            "studenthealth.uci.edu": 10,
            "dsc.uci.edu": 8,
            "counseling.uci.edu": 8,
            "career.uci.edu": 6,
        }
    )
    output_path: Path = DEFAULT_OUTPUT_PATH
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    timeout_seconds: int = 20
    max_pages: int = 75
    max_depth: int = 2
