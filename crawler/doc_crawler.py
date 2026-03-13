from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def _is_doc_like(url: str) -> bool:
    path = urlparse(url).path.lower()
    keywords = ["docs", "api", "reference", "developer", "webhook", "authentication"]
    return any(keyword in path for keyword in keywords)


def _normalize_url(base: str, href: str) -> str | None:
    if not href:
        return None
    if href.startswith("mailto:") or href.startswith("javascript:"):
        return None
    full = urljoin(base, href)
    clean, _ = urldefrag(full)
    parsed = urlparse(clean)
    if parsed.scheme not in {"http", "https"}:
        return None
    return clean


def crawl_documentation(start_url: str, max_pages: int = 50, timeout: int = 15) -> list[dict[str, str]]:
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc

    visited = set()
    queue = deque([start_url])
    pages: list[dict[str, str]] = []

    session = requests.Session()
    session.headers.update({"User-Agent": "api-explorer-mvp/0.1"})

    while queue and len(pages) < max_pages:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        try:
            response = session.get(current, timeout=timeout)
            if response.status_code >= 400:
                continue
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue
        except requests.RequestException:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        text = "\n".join(soup.stripped_strings)

        if current == start_url or _is_doc_like(current) or any(k in text.lower() for k in ["endpoint", "authentication", "api"]):
            pages.append({"page_url": current, "page_text": text})

        for anchor in soup.find_all("a", href=True):
            link = _normalize_url(current, anchor["href"])
            if not link:
                continue
            parsed_link = urlparse(link)
            if parsed_link.netloc != base_domain:
                continue
            if link not in visited:
                queue.append(link)

    return pages
