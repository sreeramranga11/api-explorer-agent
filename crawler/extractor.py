import re
from collections import defaultdict

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
KEYWORDS = [
    "endpoint",
    "webhook",
    "rate limit",
    "authentication",
    "authorization",
    "bearer",
    "cursor",
    "pagination",
]


ENDPOINT_PATTERN = re.compile(r"\b(GET|POST|PUT|DELETE|PATCH)\s+(/[\w\-./{}:?=&]+)")
JSON_PATTERN = re.compile(r"\{[\s\S]{20,4000}?\}")


def extract_api_content(pages: list[dict[str, str]]) -> dict:
    extracted: dict = defaultdict(list)
    extracted["sources"] = []

    for page in pages:
        url = page["page_url"]
        text = page["page_text"]
        lower = text.lower()
        extracted["sources"].append(url)

        for match in ENDPOINT_PATTERN.finditer(text):
            extracted["endpoints"].append(
                {
                    "method": match.group(1),
                    "path": match.group(2),
                    "source": url,
                }
            )

        for keyword in KEYWORDS:
            if keyword in lower:
                extracted["topics"].append({"topic": keyword, "source": url})

        for method in HTTP_METHODS:
            if method.lower() in lower:
                extracted["methods_seen"].append(method)

        for snippet in JSON_PATTERN.findall(text):
            if any(marker in snippet.lower() for marker in ["id", "status", "error", "data", "event"]):
                extracted["json_examples"].append({"snippet": snippet[:1200], "source": url})

    extracted["endpoints"] = _unique_dicts(extracted["endpoints"], keys=["method", "path"])
    extracted["topics"] = _unique_dicts(extracted["topics"], keys=["topic", "source"])
    extracted["methods_seen"] = sorted(set(extracted["methods_seen"]))
    extracted["json_examples"] = _unique_dicts(extracted["json_examples"], keys=["snippet"])
    extracted["sources"] = sorted(set(extracted["sources"]))

    return extracted


def _unique_dicts(items: list[dict], keys: list[str]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        marker = tuple(item.get(k) for k in keys)
        if marker in seen:
            continue
        seen.add(marker)
        unique.append(item)
    return unique
