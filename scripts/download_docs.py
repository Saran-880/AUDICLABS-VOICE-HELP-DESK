
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://docs.audiclabs.com"
START_URL = f"{BASE_URL}/docs/quickstart"

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "data" / "docs"
MANIFEST_PATH = DOCS_DIR / "manifest.json"

DOCS_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "AudicLabsDocumentationResearch/1.0"
})

visited = set()
documents = []


def clean_filename(text):
    text = re.sub(r"[^\w-]+", "_", text.lower()).strip("_")
    return text[:100] or "documentation"


def extract_page(url):
    response = session.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(" ", strip=True) if title_tag else url

    # Prefer the main documentation content over navigation.
    main = soup.find("main") or soup.find("article") or soup.body

    if main is None:
        return title, "", []

    # Remove navigation and other unrelated page elements.
    for element in main.select(
        "nav, header, footer, script, style, "
        "button, [aria-hidden='true']"
    ):
        element.decompose()

    content = main.get_text("\n", strip=True)
    links = []

    for anchor in main.find_all("a", href=True):
        absolute_url = urljoin(url, anchor["href"])
        parsed = urlparse(absolute_url)

        if (
            parsed.scheme in ("http", "https")
            and parsed.netloc == urlparse(BASE_URL).netloc
            and parsed.path.startswith("/docs/")
        ):
            links.append(absolute_url.split("#")[0])

    return title, content, links


def crawl(url, max_pages=100):
    url = url.split("#")[0]

    if url in visited or len(visited) >= max_pages:
        return

    visited.add(url)

    try:
        title, content, links = extract_page(url)

        if len(content.strip()) >= 100:
            filename = clean_filename(urlparse(url).path) + ".md"
            output_path = DOCS_DIR / filename

            output_path.write_text(
                f"# {title}\n\n"
                f"Source URL: {url}\n\n"
                f"{content}\n",
                encoding="utf-8",
            )

            documents.append({
                "filename": filename,
                "title": title,
                "url": url,
            })

            print(f"Saved: {title} | {url}")
        else:
            print(f"Skipped page with little content: {url}")

        # Follow links discovered within the documentation.
        for link in links:
            if link not in visited and len(visited) < max_pages:
                time.sleep(0.2)
                crawl(link, max_pages)

    except requests.RequestException as exc:
        print(f"Could not retrieve {url}: {exc}")


if __name__ == "__main__":
    crawl(START_URL)

    MANIFEST_PATH.write_text(
        json.dumps(documents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nFinished. Pages visited: {len(visited)}")
    print(f"Pages saved: {len(documents)}")
    print(f"Documentation folder: {DOCS_DIR}")
    print(f"Manifest: {MANIFEST_PATH}")
