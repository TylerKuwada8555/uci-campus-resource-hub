import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re
import time

# ──────────────────────────────────────────────
# SEED URLs — one per category/department
# The crawler stays within each seed's domain
# ──────────────────────────────────────────────
SEEDS = [
    ("basic_needs",     "https://basicneeds.uci.edu"),
    ("health",          "https://counseling.uci.edu"),
    ("health",          "https://studenthealth.uci.edu"),
    ("accommodations",  "https://dsc.uci.edu"),
    ("career",          "https://career.uci.edu"),
    ("financial",       "https://www.ofas.uci.edu"),
    ("academic",        "https://larc.uci.edu"),
    ("academic",        "https://writingcenter.uci.edu"),
    ("academic",        "https://honors.uci.edu"),
    ("academic",        "https://ic.uci.edu"),          # International Center
    ("academic",        "https://uu.uci.edu"),           # Undeclared advising
    ("housing",         "https://housing.uci.edu"),
    ("recreation",      "https://www.campusrec.uci.edu"),
    ("academic",        "https://www.lib.uci.edu"),
    ("financial",       "https://emergency.uci.edu"),   # Emergency funds
]

MAX_PAGES_PER_SEED = 8   # how many pages to visit per seed domain
REQUEST_DELAY      = 1.0  # seconds between requests (be polite)
HEADERS = {
    "User-Agent": "UCI-Campus-Resource-Crawler/1.0 (student project)"
}

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def same_domain(url, base):
    return urlparse(url).netloc == urlparse(base).netloc


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
            return r.text
    except Exception as e:
        print(f"  [skip] {url} — {e}")
    return None


def extract_emails(text):
    return re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)


def extract_phones(text):
    return re.findall(r"\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}", text)


def extract_contact_info(soup, raw_text):
    phones = extract_phones(raw_text)
    emails = extract_emails(raw_text)
    parts = []
    if phones:
        parts.append("Phone: " + phones[0])
    if emails:
        # filter out noreply / generic webmaster emails
        real = [e for e in emails if "noreply" not in e and "webmaster" not in e]
        if real:
            parts.append("Email: " + real[0])
    return " | ".join(parts) if parts else "See source URL for contact info"


def extract_location(raw_text):
    # Look for Irvine, CA address patterns
    match = re.search(
        r"\d+[\w\s,\.]+(?:Dr|Drive|Ave|Avenue|Rd|Road|Blvd|Boulevard|St|Street|Way|Ln|Lane)[,\s]+(?:Suite\s*\w+[,\s]+)?Irvine[\s,]+CA[\s,]+9\d{4}",
        raw_text, re.IGNORECASE
    )
    if match:
        return match.group(0).strip()
    # fallback: just mention Irvine
    if "irvine" in raw_text.lower():
        return "UCI Campus, Irvine, CA 92697"
    return "UCI Campus, Irvine, CA"


def extract_description(soup):
    # Try meta description first
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content", "").strip():
        desc = meta["content"].strip()
        if len(desc) > 30:
            return desc[:300]

    # Try first substantial paragraph
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 60:
            return text[:300]

    return "UCI campus resource and service."


def extract_name(soup, url):
    # Try h1 first
    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(" ", strip=True)
        if 5 < len(name) < 100:
            return name

    # Try title tag
    title = soup.find("title")
    if title:
        name = title.get_text(" ", strip=True)
        # Strip site suffix like " | UCI" or " - University of California"
        name = re.split(r"\s*[\|\-–]\s*(?:UCI|University)", name)[0].strip()
        if 5 < len(name) < 100:
            return name

    # Fallback: use domain
    return urlparse(url).netloc.replace("www.", "").replace(".uci.edu", "").replace("-", " ").title()


def infer_target_audience(text, category):
    text_lower = text.lower()
    if "graduate" in text_lower and "undergraduate" in text_lower:
        return "UCI students (undergraduate and graduate)"
    if "graduate" in text_lower:
        return "UCI graduate students"
    if "undergraduate" in text_lower or "undergrad" in text_lower:
        return "UCI undergraduate students"
    if category == "health":
        return "UCI students (undergraduate and graduate)"
    return "UCI students (undergraduate and graduate)"


def page_is_useful(soup):
    """Skip pages that are mostly navigation, login walls, or too thin."""
    text = soup.get_text(" ", strip=True)
    if len(text) < 200:
        return False
    # skip 404 / error pages
    title = soup.find("title")
    if title and re.search(r"404|not found|error|login|sign.in", title.get_text(), re.IGNORECASE):
        return False
    return True


def scrape_page(url, category):
    html = fetch(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    if not page_is_useful(soup):
        return None

    raw_text = soup.get_text(" ", strip=True)

    name        = extract_name(soup, url)
    description = extract_description(soup)
    location    = extract_location(raw_text)
    contact     = extract_contact_info(soup, raw_text)
    audience    = infer_target_audience(raw_text, category)

    return {
        "category":        category,
        "name":            name,
        "location":        location,
        "contact_info":    contact,
        "description":     description,
        "target_audience": audience,
        "source_url":      url
    }


def get_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # skip anchors, javascript, mailto, tel
        if href.startswith(("#", "javascript", "mailto", "tel")):
            continue
        full = urljoin(base_url, href)
        # only keep same-domain http/https links
        if full.startswith("http") and same_domain(full, base_url):
            # strip query strings and fragments to avoid duplicates
            parsed = urlparse(full)
            clean = parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip("/")
            links.add(clean)
    return links


# ──────────────────────────────────────────────
# Main crawl loop
# ──────────────────────────────────────────────

def crawl():
    all_resources = []
    seen_urls = set()
    seen_names = set()

    for category, seed in SEEDS:
        print(f"\n── Crawling [{category}] {seed}")
        queue   = [seed]
        visited = set()
        count   = 0

        while queue and count < MAX_PAGES_PER_SEED:
            url = queue.pop(0)
            if url in visited or url in seen_urls:
                continue
            visited.add(url)
            seen_urls.add(url)

            print(f"  fetching: {url}")
            html = fetch(url)
            if not html:
                time.sleep(REQUEST_DELAY)
                continue

            # Extract resource from this page
            soup = BeautifulSoup(html, "html.parser")
            if page_is_useful(soup):
                raw_text    = soup.get_text(" ", strip=True)
                name        = extract_name(soup, url)
                description = extract_description(soup)
                location    = extract_location(raw_text)
                contact     = extract_contact_info(soup, raw_text)
                audience    = infer_target_audience(raw_text, category)

                # Deduplicate by name
                if name not in seen_names:
                    seen_names.add(name)
                    all_resources.append({
                        "category":        category,
                        "name":            name,
                        "location":        location,
                        "contact_info":    contact,
                        "description":     description,
                        "target_audience": audience,
                        "source_url":      url
                    })
                    count += 1
                    print(f"  ✓ added: {name}")

            # Discover more links within this domain
            new_links = get_links(html, seed)
            for link in new_links:
                if link not in visited and link not in seen_urls:
                    queue.append(link)

            time.sleep(REQUEST_DELAY)

    return all_resources


if __name__ == "__main__":
    print("Starting UCI Campus Resource Crawler...")
    resources = crawl()

    output_path = "new_resources.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Scraped {len(resources)} resources → {output_path}")
    print("Review the file and merge into uci_resources.json when ready.")