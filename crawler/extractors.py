from __future__ import annotations

import json
import re
from collections import Counter
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from crawler.config import CrawlConfig
from crawler.models import RawResource, ResourceCandidate


EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?1[-.\s]*)?(?:\(?\d{3}\)?[-.\s]*)\d{3}[-.\s]*\d{4}")
ADDRESS_SUFFIX_PATTERN = (
    r"(?:Dr|Drive|Rd|Road|St|Street|Ave|Avenue|Blvd|Boulevard|Way|Ln|Lane|Ct|Court|Hall|Library|Pavilion|Building|Center|Health|Services(?:\s+\d+)?)"
)
ADDRESS_RE = re.compile(
    rf"\b\d{{2,5}}\s+(?:[A-Za-z0-9#.\-'\u2019]+\s+){{0,10}}{ADDRESS_SUFFIX_PATTERN}\.?(?:,\s*|\s+)Irvine,\s*CA\s+\d{{5}}(?:[-\u2010-\u2015]\d{{4}})?\b",
    re.IGNORECASE,
)
STREET_LINE_RE = re.compile(
    rf"^\d{{2,5}}\s+(?:[A-Za-z0-9#.\-'\u2019]+\s+){{0,10}}{ADDRESS_SUFFIX_PATTERN}\.?\s*$",
    re.IGNORECASE,
)
CITY_STATE_RE = re.compile(r"^Irvine,\s*CA\s+\d{5}(?:[-\u2010-\u2015]\d{4})?$", re.IGNORECASE)
FULL_ADDRESS_LINE_RE = re.compile(r"^\d{2,5}.{0,80}Irvine,\s*CA\s+\d{5}(?:[-\u2010-\u2015]\d{4})?$", re.IGNORECASE)
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")
URL_SLUG_SPLIT_RE = re.compile(r"[-_/]+")
UPPERCASE_PLACEHOLDER_RE = re.compile(r"^[A-Z\s&]{6,}$")
MULTI_SEPARATOR_RE = re.compile(r"\s+(?:\||[-:])\s+")
BOILERPLATE_DESCRIPTION_PATTERNS = (
    "for life threatening emergencies",
    "for crisis care needs 24/7",
    "privacy & legal notice",
    "read more",
    "university of california, irvine",
    "call uci counseling center at",
    "a valid parking permit is required",
    "this page showcases",
    "this page is being developed",
)
BAD_DESCRIPTION_PATTERNS = (
    "located across ring road",
    "holiday break",
    "the end is in sight",
    "medical record processing time",
    "we highly encourage all students",
    "i am a proud uci alumna",
    "business hours",
    "phone :",
    "fax :",
)
GENERIC_NAME_PATTERNS = (
    "about",
    "about us",
    "contact",
    "contact us",
    "home",
    "logo",
    "welcome",
    "welcome!",
    "what is",
    "for current students",
    "hours of operation",
    "events calendar",
    "meet our staff",
    "meet the staff",
    "what can we help you with today",
    "are you an undergraduate or graduate student",
    "click to read",
    "our mission is",
    "step 1",
    "email",
    "resources",
    "resources for students",
)
FRAGMENT_TITLE_PATTERNS = (
    "application process",
    "for students",
    "office hours",
    "popular methods",
    "process overview",
    "requirements",
    "you may also be interested in",
    "top requests",
)
RESOURCE_PAGE_HINTS = (
    "advising",
    "appointment",
    "services",
    "support",
    "resource",
    "clinic",
    "care",
    "pantry",
    "calfresh",
    "financial aid",
    "accommodation",
    "testing",
    "housing",
    "walk-in",
    "tutoring",
    "writing",
    "career",
    "therapy",
    "health",
    "student",
    "basic needs",
    "pharmacy",
)
EXCLUDED_URL_TERMS = (
    "/pantry-anniversary/",
    "/pantry-community-guidelines/",
    "/employment/",
    "/field-study/",
    "/job-search-strategies/",
    "/chatgpt-ai-and-the-job-search/",
    "/undergraduate/apply-for-grad-school/pre-law/",
    "/undergraduate/apply-for-grad-school/applying-preparing/",
    "/undergraduate/apply-for-grad-school/selecting-schools-programs/",
    "/how-can-we-help/",
    "/patient-forms/",
    "/fees-for-common-services/",
    "/new-prospective-students/",
    "/dsc-policies/",
)
EXCLUDED_TITLE_TERMS = (
    "our history",
    "employment opportunities",
    "pantry community guidelines",
    "10 tips",
    "launch scholarship",
    "sample prompts",
    "peer programs",
    "you may also be interested in",
    "top requests",
    "patient forms",
    "fees for common services",
    "awards & honors",
    "what’s the difference",
    "what's the difference",
    "explore your path",
)
TITLE_OVERRIDES: dict[str, dict[str, str]] = {
    "basicneeds.uci.edu": {
        "/calfresh-application-process/": "CalFresh Application Process",
        "/contact-us/": "General Contact",
        "/new-students/": "Basic Needs Assessment",
        "/basicneeds-assessment/": "Basic Needs Assessment",
    },
    "dsc.uci.edu": {
        "/contact/": "General Contact",
        "/dhh/": "Deaf and Hard of Hearing Services",
        "/at/": "Assistive Technology",
        "/aims/": "Alternative Media and Format Conversion",
        "/accessible-furniture/": "Accessible Furniture Accommodations",
        "/testing/": "Testing Accommodations",
    },
    "studenthealth.uci.edu": {
        "/after-hours-urgent-care/": "After-Hours Urgent Care",
        "/lab/": "Laboratory Services",
        "/gynecology/": "Gynecology",
        "/primary-care/": "Primary Care",
        "/psychiatry-mental-health/": "Psychiatry and Mental Health",
        "/specialty-care/": "Specialty Care",
    },
    "career.uci.edu": {
        "/": "Division of Career Pathways",
        "/undergraduate/apply-for-grad-school/pre-health/": "Pre-Health Advising",
        "/about/contact-us/": "General Contact",
    },
    "ics.uci.edu": {
        "/academics/undergrad/contact/": "Academic Advising",
    },
    "tutoring.ics.uci.edu": {
        "/": "ICS Tutoring",
        "/contact-us/": "ICS Tutoring",
    },
    "oai.ics.uci.edu": {
        "/oai-tutoring/": "OAI Tutoring",
    },
    "advise.education.uci.edu": {
        "/contact-us.html": "Academic Advising",
    },
    "undergraduate.eng.uci.edu": {
        "/advising/walk-in-advising/": "Academic Advising",
        "/contact-us/": "Academic Advising",
    },
    "undergraduate.bio.uci.edu": {
        "/contact-us/": "Academic Advising",
    },
    "hq.humanities.uci.edu": {
        "/undergrad/about/chat.php": "Academic Advising Chat",
        "/undergrad/about/acad_advising.php": "Academic Advising",
    },
    "merage.uci.edu": {
        "/programs/undergraduate/contact-us.html": "Academic Advising",
    },
    "law.uci.edu": {
        "/admission/tuition-aid/": "Financial Aid",
    },
    "campusrec.uci.edu": {
        "/": "Campus Recreation",
        "/membership/index.html": "ARC Membership",
        "/groupx/index.html": "Group X Classes",
        "/arc/hours.html": "Anteater Recreation Center",
        "/app.html": "Campus Recreation App",
    },
    "aid.ofas.uci.edu": {
        "/portal/financialaid_appointments/": "Financial Aid Appointments",
    },
    "ofas.uci.edu": {
        "/index.php": "Office of Financial Aid and Scholarships",
    },
    "writingcenter.uci.edu": {
        "/": "UCI Writing Center",
    },
    "housing.uci.edu": {
        "/": "General Contact",
    },
}
LOCATION_OVERRIDES: dict[str, dict[str, str]] = {
    "campusrec.uci.edu": {
        "/": "680 California Ave Irvine, CA 92697",
    },
    "undergraduate.eng.uci.edu": {
        "/contact-us/": "415 E Peltason Dr #286 Irvine, CA 92697-2750",
    },
    "undergraduate.bio.uci.edu": {
        "/contact-us/": "1011 Biological Sciences III, Irvine, CA 92697-1460",
    },
    "hq.humanities.uci.edu": {
        "/undergrad/about/acad_advising.php": "143 Humanities Instructional Building (HIB) Irvine, CA 92697-3380",
    },
    "law.uci.edu": {
        "/admission/tuition-aid/": "401 E. Peltason Dr Irvine, CA 92697-8000",
    },
    "www.law.uci.edu": {
        "/admission/tuition-aid/": "401 E. Peltason Dr Irvine, CA 92697-8000",
    },
}
CATEGORY_OVERRIDES: dict[tuple[str, str], str] = {
    ("career.uci.edu", "/undergraduate/apply-for-grad-school/pre-health/"): "career",
    ("nursing.uci.edu", "/"): "academic",
    ("law.uci.edu", "/admission/tuition-aid/"): "financial",
    ("housing.uci.edu", "/"): "housing",
    ("campusrec.uci.edu", "/"): "recreation",
    ("campusrec.uci.edu", "/membership/index.html"): "recreation",
    ("campusrec.uci.edu", "/groupx/index.html"): "recreation",
    ("campusrec.uci.edu", "/arc/hours.html"): "recreation",
    ("campusrec.uci.edu", "/app.html"): "recreation",
}
ACADEMIC_HINT_DOMAINS = {
    "ics.uci.edu",
    "undergraduate.eng.uci.edu",
    "advise.education.uci.edu",
    "undergraduate.bio.uci.edu",
    "hq.humanities.uci.edu",
    "honors.uci.edu",
    "pharmsci.uci.edu",
    "nursing.uci.edu",
    "merage.uci.edu",
    "www.arts.uci.edu",
}


def page_text(soup: BeautifulSoup) -> str:
    return soup.get_text(" ", strip=True)


def meta_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    return tag.get("content", "").strip() if tag else ""


def extract_name(soup: BeautifulSoup) -> str:
    for selector in ("h1", "meta[property='og:title']", "title"):
        if selector.startswith("meta"):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                return tag["content"].strip()
            continue

        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(" ", strip=True)
            if text:
                return text
    return ""


def clean_title(value: str) -> str:
    text = " ".join(value.split())
    text = re.sub(r"\s+[|\-:]\s+.*$", "", text).strip()
    return text


def normalize_name_token(value: str) -> str:
    return clean_title(value).lower().strip(" -:!?.")


def canonical_path(url: str) -> str:
    path = urlparse(url).path or "/"
    lowered = path.lower()
    if lowered != "/" and "." not in lowered.rsplit("/", 1)[-1] and not lowered.endswith("/"):
        lowered += "/"
    return lowered


def lookup_title_override(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return TITLE_OVERRIDES.get(domain, {}).get(canonical_path(url), "")


def lookup_category_override(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return CATEGORY_OVERRIDES.get((domain, canonical_path(url)), "")


def lookup_location_override(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    return LOCATION_OVERRIDES.get(domain, {}).get(canonical_path(url), "")


def is_explicitly_excluded(url: str, title: str, description: str) -> bool:
    lowered_url = url.lower()
    lowered_title = title.lower()
    lowered_description = description.lower()
    if any(term in lowered_url for term in EXCLUDED_URL_TERMS):
        return True
    if any(term in lowered_title for term in EXCLUDED_TITLE_TERMS):
        return True
    if "prospective student" in lowered_title or "prospective student" in lowered_description:
        return True
    return False


def format_phone(digits: str) -> str:
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def normalize_phone(value: str) -> tuple[str, str] | None:
    digits = re.sub(r"\D", "", value)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return digits, format_phone(digits)


def select_contact_emails(emails: list[str]) -> list[str]:
    normalized = []
    seen: set[str] = set()
    for email in emails:
        cleaned = email.strip(" .;,").lower()
        if re.search(r"@(?:[\w.-]+\.)?uci\.edu$", cleaned) is None:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)
    return normalized[:4]


def select_contact_phones(phones: list[tuple[str, str]]) -> list[str]:
    if not phones:
        return []

    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for digits, formatted in phones:
        if digits in seen:
            continue
        seen.add(digits)
        unique.append((digits, formatted))

    local = [formatted for digits, formatted in unique if digits.startswith(("949", "714"))]
    toll_free = [formatted for digits, formatted in unique if digits.startswith(("800", "844", "855", "866", "877", "888"))]
    if local:
        selected = local[:3]
        if toll_free:
            selected.append(toll_free[0])
        return selected
    return [formatted for _, formatted in unique[:4]]


def contact_blocks(root: Tag) -> list[str]:
    selectors = (
        "address",
        "a[href^='mailto:']",
        "a[href^='tel:']",
        "[class*='contact']",
        "[id*='contact']",
        "footer",
    )
    values: list[str] = []
    seen: set[str] = set()
    for selector in selectors:
        for node in root.select(selector):
            if not isinstance(node, Tag):
                continue
            text = clean_text_block(node.get_text("\n", strip=True))
            if not text:
                continue
            if not (EMAIL_RE.search(text) or PHONE_RE.search(text)):
                continue
            if text not in seen:
                seen.add(text)
                values.append(text)

    if values:
        return values

    for line in root.get_text("\n", strip=True).splitlines():
        cleaned = clean_text_block(line)
        if not cleaned:
            continue
        if "fax" in cleaned.lower() and "phone" not in cleaned.lower() and "call" not in cleaned.lower():
            continue
        if EMAIL_RE.search(cleaned) or PHONE_RE.search(cleaned):
            values.append(cleaned)
    return values


def format_contact_info(phones: list[tuple[str, str]], emails: list[str]) -> str:
    selected_phones = select_contact_phones(phones)
    selected_emails = select_contact_emails(emails)

    parts: list[str] = []
    if selected_phones:
        parts.append("Phone: " + " | ".join(selected_phones))
    if selected_emails:
        parts.append("Email: " + " | ".join(selected_emails))
    return " | ".join(parts)


def contains_phrase(haystack: str, phrase: str) -> bool:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
    return pattern.search(haystack) is not None


def extract_main_content(soup: BeautifulSoup) -> Tag:
    """Prefer the primary content region so extraction avoids nav, footer, and banners."""
    selectors = (
        "main",
        "article",
        "[role='main']",
        ".entry-content",
        ".site-main",
        ".content-area",
        ".main-content",
        "#content",
        "#main",
    )
    for selector in selectors:
        node = soup.select_one(selector)
        if isinstance(node, Tag):
            for bad_selector in ("nav", "footer", "header", ".breadcrumb", ".breadcrumbs", ".alert", ".notice", ".sidebar", ".widget", ".site-footer", ".site-header"):
                for child in node.select(bad_selector):
                    child.decompose()
            return node
    return soup.body if isinstance(soup.body, Tag) else soup


def extract_breadcrumbs(soup: BeautifulSoup) -> str:
    selectors = (
        "nav[aria-label*='breadcrumb']",
        ".breadcrumb",
        ".breadcrumbs",
        "[class*='breadcrumb']",
    )
    for selector in selectors:
        node = soup.select_one(selector)
        if isinstance(node, Tag):
            text = clean_text_block(node.get_text(" ", strip=True))
            if text:
                return text
    return ""


def clean_text_block(value: str) -> str:
    return " ".join(value.split()).strip()


def extract_heading_candidates(node: Tag) -> list[str]:
    headings: list[str] = []
    for selector in ("h1", "h2", "h3"):
        for tag in node.select(selector):
            text = clean_title(tag.get_text(" ", strip=True))
            if text and text not in headings:
                headings.append(text)
    return headings


def extract_site_name(url: str, soup: BeautifulSoup, config: CrawlConfig) -> str:
    parsed = urlparse(url)
    for host, label in config.domain_name_hints.items():
        if parsed.netloc == host or parsed.netloc.endswith(f".{host}"):
            return label

    for selector in ("meta[property='og:site_name']", "meta[name='application-name']"):
        tag = soup.select_one(selector)
        if tag and tag.get("content"):
            return clean_title(tag["content"])

    logo = soup.find("img", alt=True)
    if logo:
        alt = clean_title(logo.get("alt", ""))
        if alt and len(alt) > 6:
            return alt
    return ""


def title_looks_generic(title: str, config: CrawlConfig) -> bool:
    normalized = normalize_name_token(title)
    return (
        normalized in config.generic_titles
        or normalized in GENERIC_NAME_PATTERNS
        or normalized.startswith("what is ")
        or normalized.endswith(" logo")
    )


def title_looks_fragmentary(title: str) -> bool:
    lowered = clean_title(title).lower().strip()
    return (
        lowered.endswith("&")
        or lowered.endswith(":")
        or any(pattern == lowered for pattern in FRAGMENT_TITLE_PATTERNS)
        or lowered.startswith("step ")
        or lowered.startswith("we encourage all students")
    )


def title_looks_noisy(title: str) -> bool:
    cleaned = clean_title(title)
    if not cleaned:
        return True
    if len(cleaned) > 120:
        return True
    if title_looks_fragmentary(cleaned):
        return True
    if UPPERCASE_PLACEHOLDER_RE.match(cleaned):
        return True
    if any(token in cleaned.lower() for token in ("will be closed", "holiday", "normal hours of operation")):
        return True
    if any(token in cleaned.lower() for token in ("click to read", "what can we help you with today", "are you an undergraduate or graduate student", "our mission is", " logo")):
        return True
    return False


def extract_slug_phrase(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    if not slug:
        return ""
    words = [word for word in URL_SLUG_SPLIT_RE.split(slug) if word]
    if not words:
        return ""
    return clean_title(" ".join(word.capitalize() if word.isalpha() else word for word in words))


def choose_best_heading(headings: list[str], config: CrawlConfig) -> str:
    for heading in headings:
        if not title_looks_noisy(heading) and not title_looks_generic(heading, config):
            return heading
    return headings[0] if headings else ""


def build_resource_name(url: str, soup: BeautifulSoup, main_content: Tag, config: CrawlConfig) -> str:
    title = clean_title(extract_name(main_content) or extract_name(soup))
    site_name = clean_title(extract_site_name(url, soup, config))
    breadcrumbs = clean_title(extract_breadcrumbs(soup))
    heading_candidates = extract_heading_candidates(main_content)
    best_heading = choose_best_heading(heading_candidates, config)
    slug_phrase = extract_slug_phrase(url)
    override_title = lookup_title_override(url)

    if override_title:
        title = override_title
    elif not title or title_looks_noisy(title):
        title = best_heading or slug_phrase

    if title_looks_generic(title, config) or title_looks_fragmentary(title):
        for candidate in (best_heading, slug_phrase, breadcrumbs):
            if candidate and not title_looks_generic(candidate, config) and not title_looks_noisy(candidate):
                title = candidate
                break

    normalized_title = normalize_name_token(title)
    if normalized_title.startswith("about the") and site_name:
        title = site_name
    elif normalized_title.startswith("what is the") and site_name and site_name.lower() in normalized_title:
        title = site_name
    elif normalized_title.startswith("welcome") and slug_phrase:
        title = slug_phrase
    elif normalized_title in {"resources", "resources for students", "forms and documents"} and site_name:
        title = f"{site_name} - {title}"

    title = clean_title(title)
    lowered_title = title.lower()
    lowered_site = site_name.lower()

    if not title:
        return site_name
    if not site_name:
        return title
    if lowered_title == lowered_site or lowered_title in lowered_site:
        return site_name

    generic_titles = {
        "about",
        "contact",
        "contact us",
        "walk-in advising",
        "emergency assistance",
        "referral and resource support",
        "undergraduate academic advising",
        "about the writing center",
        "welcome to the",
    }
    if lowered_title in generic_titles or len(title.split()) <= 3:
        return f"{site_name} - {title}"

    if "uci" not in lowered_title and lowered_site not in lowered_title:
        return f"{site_name} - {title}"
    return title


def looks_like_boilerplate_description(text: str) -> bool:
    lowered = text.lower()
    if len(text) < 40:
        return True
    if any(pattern in lowered for pattern in BOILERPLATE_DESCRIPTION_PATTERNS):
        return True
    if any(pattern in lowered for pattern in BAD_DESCRIPTION_PATTERNS):
        return True
    if "©" in text or "[…]" in text or "..." in text:
        return True
    return False


def trim_description(text: str, max_length: int = 280) -> str:
    cleaned = clean_text_block(text)
    if len(cleaned) <= max_length:
        return cleaned

    sentences = SENTENCE_END_RE.split(cleaned)
    pieces: list[str] = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        proposed = total + len(sentence) + (1 if pieces else 0)
        if proposed > max_length and pieces:
            break
        pieces.append(sentence)
        total = proposed
        if total >= max_length:
            break
    return " ".join(pieces).strip() if pieces else cleaned[:max_length].rstrip() + "..."


def description_score(text: str) -> int:
    cleaned = clean_text_block(text)
    lowered = cleaned.lower()
    score = 0
    if not cleaned:
        return -10
    if 40 <= len(cleaned) <= 280:
        score += 2
    if any(term in lowered for term in RESOURCE_PAGE_HINTS):
        score += 2
    if any(term in lowered for term in ("students", "services", "support", "provides", "offers", "appointments", "advising", "assistance")):
        score += 2
    if looks_like_boilerplate_description(cleaned):
        score -= 8
    if re.match(r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered):
        score -= 6
    if lowered.startswith("i am ") or lowered.startswith("located across ring road"):
        score -= 6
    if cleaned.count(":") > 3:
        score -= 3
    return score


def extract_description(soup: BeautifulSoup, main_content: Tag) -> str:
    candidates: list[str] = []
    description = meta_description(soup)
    if description:
        candidates.append(description)

    for paragraph in main_content.find_all("p")[:8]:
        text = clean_text_block(paragraph.get_text(" ", strip=True))
        if not text:
            continue
        if any(term in text.lower() for term in ("privacy laws", "for all inquiries containing phi", "button is for", "click", "scroll to the bottom")):
            continue
        candidates.append(text)

    if not candidates:
        return ""

    best = max(candidates, key=description_score)
    if description_score(best) <= 0:
        return ""
    return trim_description(best)


def extract_location(url: str, main_content: Tag, soup: BeautifulSoup, text: str, full_text: str) -> str:
    # Many UCI sites place the street address and city/state/ZIP on separate lines in the footer.
    scoped_text = main_content.get_text("\n", strip=True)
    lines = [line.strip() for line in scoped_text.splitlines() if line.strip()]
    for line in lines:
        if FULL_ADDRESS_LINE_RE.match(line) and len(line) <= 90:
            return " ".join(line.split())
    for index, line in enumerate(lines[:-1]):
        next_line = lines[index + 1]
        if STREET_LINE_RE.match(line) and CITY_STATE_RE.match(next_line):
            return f"{line} {next_line}"

        combined = f"{line} {next_line}"
        match = ADDRESS_RE.search(combined)
        if match:
            return " ".join(match.group(0).split())

    match = ADDRESS_RE.search(text)
    if match:
        return " ".join(match.group(0).split())

    match = ADDRESS_RE.search(full_text)
    if match:
        return " ".join(match.group(0).split())
    return lookup_location_override(url)


def extract_contact_info(main_content: Tag, soup: BeautifulSoup) -> str:
    emails: list[str] = []
    phones: list[tuple[str, str]] = []

    blocks = contact_blocks(main_content)
    if not blocks:
        blocks = contact_blocks(soup)

    for block in blocks:
        emails.extend(EMAIL_RE.findall(block))
        for match in PHONE_RE.findall(block):
            normalized = normalize_phone(match)
            if normalized is not None:
                phones.append(normalized)

    return format_contact_info(phones, emails)


def infer_target_audience(text: str) -> str:
    lowered = text.lower()
    if "faculty and staff" in lowered or "employees" in lowered:
        return ""
    if "graduate" in lowered and "undergraduate" in lowered:
        return "UCI undergraduate and graduate students"
    if "graduate" in lowered:
        return "UCI graduate students"
    if "undergraduate" in lowered:
        return "UCI undergraduate students"
    if "students" in lowered or "student" in lowered:
        return "UCI students"
    return ""


def infer_category(
    url: str,
    title: str,
    description: str,
    breadcrumbs: str,
    text: str,
    config: CrawlConfig,
) -> str:
    lowered_url = url.lower()
    path = urlparse(url).path.lower()
    path_segments = [segment for segment in URL_SLUG_SPLIT_RE.split(path) if segment]
    lowered_title = title.lower()
    lowered_breadcrumbs = breadcrumbs.lower()
    lowered_description = description.lower()
    lowered_text = text.lower()
    override = lookup_category_override(url)
    if override:
        return override
    if urlparse(url).netloc.lower() in ACADEMIC_HINT_DOMAINS and any(
        term in lowered_url or term in lowered_title or term in lowered_breadcrumbs
        for term in ("advis", "current students", "student affairs", "chat", "honors", "contact")
    ):
        return "academic"

    if any(
        term in lowered_url or term in lowered_title or term in lowered_breadcrumbs
        for term in ("housing", "off-campus-housing", "student housing", "sponsored housing", "residence", "apartment", "roommate")
    ):
        return "housing"
    if any(
        term in lowered_url or term in lowered_title or term in lowered_breadcrumbs
        for term in ("dsc", "accessibility", "disability", "accommodation", "assistive", "dhh", "testing")
    ):
        return "accessibility"
    recreation_text_terms = ("campus recreation", "campus rec", "group x", "fitness", "arc membership")
    if (
        "campusrec.uci.edu" in lowered_url
        or "www.campusrec.uci.edu" in lowered_url
        or any(term in lowered_title or term in lowered_breadcrumbs for term in recreation_text_terms)
    ):
        return "recreation"

    scores: dict[str, int] = Counter()
    weighted_sources = (
        (lowered_url, 4),
        (lowered_title, 4),
        (lowered_breadcrumbs, 3),
        (lowered_description, 3),
        (lowered_text[:1500], 1),
    )

    for category, keywords in config.category_keywords.items():
        for source, weight in weighted_sources:
            scores[category] += sum(weight for keyword in keywords if keyword in source)

    if any(term in lowered_url or term in lowered_title for term in ("feedback", "calendar", "staff", "report", "policy", "insurance", "mission", "values")):
        scores["health"] = max(0, scores["health"] - 3)

    if not scores or max(scores.values(), default=0) <= 0:
        return "academic"
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0][0]


def classify_counseling_page(
    url: str,
    title: str,
    description: str,
    text: str,
    config: CrawlConfig,
) -> tuple[str, str]:
    haystack = " ".join([url, title, description, text[:1200]]).lower()

    if any(term in haystack for term in config.counseling_editorial_terms):
        return "exclude", "editorial"
    if any(term in haystack for term in config.counseling_direct_health_terms):
        return "health", "direct_health"
    if any(term in haystack for term in config.counseling_program_terms):
        if any(term in haystack for term in ("academic success", "study", "workshop", "skill building")):
            return "academic", "program_academic"
        return "career", "program_career"
    return "exclude", "navigation"


def evaluate_resource_worthiness(
    url: str,
    title: str,
    description: str,
    text: str,
    breadcrumbs: str,
    audience: str,
    config: CrawlConfig,
) -> tuple[bool, tuple[str, ...], str]:
    classification_haystack = " ".join([url, title]).lower()
    allow_haystack = " ".join([classification_haystack, breadcrumbs, text[:1500]]).lower()
    flags: list[str] = []

    if not audience and any(term in allow_haystack for term in ("faculty and staff", "employees only", "staff only", "for parents", "vendor", "employer advisory board")):
        flags.append("non_student_audience")

    if any(contains_phrase(classification_haystack, term) for term in config.resource_deny_terms):
        flags.append("deny_term")

    if title_looks_generic(title, config):
        flags.append("generic_title")

    if title_looks_noisy(title):
        flags.append("noisy_title")

    if title_looks_fragmentary(title):
        flags.append("fragment_title")

    if is_explicitly_excluded(url, title, description):
        flags.append("explicit_exclusion")

    page_type = "resource"
    if any(contains_phrase(classification_haystack, term) for term in ("staff", "team", "vendor", "board")):
        page_type = "staff"
    elif any(contains_phrase(classification_haystack, term) for term in ("calendar", "event", "special events")):
        page_type = "event"
    elif any(contains_phrase(classification_haystack, term) for term in ("policy", "rights", "responsibilities", "nondiscrimination", "report")):
        page_type = "policy"
    elif any(contains_phrase(classification_haystack, term) for term in ("feedback", "complaint")):
        page_type = "feedback"
    elif any(contains_phrase(classification_haystack, term) for term in ("announcement", "closed", "holiday", "news", "mission", "values", "faq", "social media", "give")):
        page_type = "announcement"

    allow_match = any(term in allow_haystack for term in config.resource_allow_terms) or bool(audience)
    if not allow_match:
        flags.append("missing_allow_signal")

    strong_reject = page_type in {"announcement", "event", "feedback", "policy", "staff"}
    keep = (
        allow_match
        and "non_student_audience" not in flags
        and "explicit_exclusion" not in flags
        and "generic_title" not in flags
        and "fragment_title" not in flags
        and not strong_reject
        and "noisy_title" not in flags
    )
    return keep, tuple(flags), page_type


def parse_json_ld(soup: BeautifulSoup, source_url: str, config: CrawlConfig) -> list[RawResource]:
    """JSON-LD gives us a clean fallback when pages publish organization metadata."""
    resources: list[RawResource] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        content = (script.string or "").strip()
        if not content:
            continue
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            continue

        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") not in {"Organization", "CollegeOrUniversity", "MedicalOrganization"}:
                continue

            name = str(item.get("name", "")).strip()
            if not name:
                continue

            if is_explicitly_excluded(source_url, name, str(item.get("description", "")).strip()):
                continue

            address = item.get("address", {})
            location = ""
            if isinstance(address, dict):
                location = ", ".join(
                    str(address.get(key, "")).strip()
                    for key in ("streetAddress", "addressLocality", "addressRegion", "postalCode")
                    if str(address.get(key, "")).strip()
                )

            description = str(item.get("description", "")).strip()
            audience = "UCI students" if "student" in description.lower() else ""
            phones: list[tuple[str, str]] = []
            emails: list[str] = []
            if item.get("telephone"):
                normalized = normalize_phone(str(item["telephone"]).strip())
                if normalized is not None:
                    phones.append(normalized)
            if item.get("email"):
                emails.append(str(item["email"]).strip())
            category = infer_category(source_url, name, description, "", description, config)
            resources.append(
                RawResource(
                    category=category,
                    name=name,
                    location=location,
                    contact_info=format_contact_info(phones, emails),
                    description=description,
                    target_audience=audience,
                    source_url=source_url,
                )
            )
    return resources


def build_resource_candidate(url: str, soup: BeautifulSoup, config: CrawlConfig) -> ResourceCandidate | None:
    main_content = extract_main_content(soup)
    text = clean_text_block(main_content.get_text(" ", strip=True))
    full_text = clean_text_block(soup.get_text(" ", strip=True))
    breadcrumbs = extract_breadcrumbs(soup)
    title = build_resource_name(url, soup, main_content, config)
    description = extract_description(soup, main_content)
    if is_explicitly_excluded(url, title, description):
        return None
    location = extract_location(url, main_content, soup, text, full_text)
    contact_info = extract_contact_info(main_content, soup)
    audience = infer_target_audience(text)
    keep, flags, page_type = evaluate_resource_worthiness(url, title, description, text, breadcrumbs, audience, config)
    category = infer_category(url, title, description, breadcrumbs, text, config)

    if "counseling.uci.edu" in urlparse(url).netloc:
        counseling_category, counseling_page_type = classify_counseling_page(url, title, description, text, config)
        if counseling_category == "exclude":
            return None
        category = counseling_category
        page_type = counseling_page_type

    if not all([title, location, contact_info]):
        return None
    if not keep:
        return None

    audience_signals = tuple(
        signal
        for signal in ("students", "undergraduate", "graduate")
        if signal in text.lower()
    )

    return ResourceCandidate(
        category=category,
        name=title,
        location=location,
        contact_info=contact_info,
        description=description,
        target_audience=audience,
        source_url=url,
        quality_flags=flags,
        page_type=page_type,
        audience_signals=audience_signals,
        quality_score=0,
    )


def extract_resources(url: str, soup: BeautifulSoup, config: CrawlConfig) -> list[ResourceCandidate]:
    """Extract resource candidates from one page.

    v1 keeps extraction conservative: one page-level resource plus any structured JSON-LD fallback.
    """

    resources: list[ResourceCandidate] = []
    for resource in parse_json_ld(soup, url, config):
        resources.append(
            ResourceCandidate(
                category=resource.category,
                name=resource.name,
                location=resource.location,
                contact_info=resource.contact_info,
                description=resource.description,
                target_audience=resource.target_audience,
                source_url=resource.source_url,
                quality_flags=(),
                page_type="structured_data",
                audience_signals=("students",) if resource.target_audience else (),
                quality_score=0,
            )
        )

    page_resource = build_resource_candidate(url, soup, config)
    if page_resource is not None:
        resources.append(page_resource)

    # Keep order stable while removing duplicates caused by JSON-LD + page-level extraction.
    deduped: list[ResourceCandidate] = []
    seen: set[tuple[str, str]] = set()
    for resource in resources:
        key = (resource.name.lower(), resource.source_url.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(resource)
    return deduped
