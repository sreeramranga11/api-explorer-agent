import os
from typing import Any


def _safe_section(text: str, fallback: str = "Possible: Not clearly documented in crawled pages.") -> str:
    return text.strip() if text and text.strip() else fallback


def _build_rule_based_markdown(extracted_data: dict[str, Any]) -> str:
    endpoints = extracted_data.get("endpoints", [])
    json_examples = extracted_data.get("json_examples", [])
    topics = [item["topic"] for item in extracted_data.get("topics", [])]

    lines: list[str] = [
        "# API Integration Guide",
        "",
        "## Overview",
        "Guide synthesized from crawled API documentation pages.",
        "",
        "## Base URLs",
        "Possible: Base URLs were not explicitly detected in the crawled pages.",
        "",
        "## Authentication",
        _safe_section(
            "Authentication-related content detected in docs."
            if "authentication" in topics or "authorization" in topics or "bearer" in topics
            else ""
        ),
        "",
        "## Rate Limits",
        _safe_section("Rate limit references were found." if "rate limit" in topics else ""),
        "",
        "## Core Resources",
    ]

    resource_names = sorted({endpoint["path"].strip("/").split("/")[0] for endpoint in endpoints if endpoint.get("path")})
    if resource_names:
        lines.extend([f"- {name.title()}" for name in resource_names if name])
    else:
        lines.append("- Possible: Resources not clearly identified.")

    lines.extend(["", "## Endpoints", ""])
    if endpoints:
        for endpoint in endpoints[:30]:
            lines.extend(
                [
                    f"### {endpoint['method']} {endpoint['path']}",
                    f"Description: Extracted from {endpoint['source']}",
                    "",
                    "Parameters:",
                    "- Possible: Parameter details not fully extracted.",
                    "",
                    "Example response:",
                    "```json",
                    (json_examples[0]["snippet"] if json_examples else '{"possible": true}'),
                    "```",
                    "",
                ]
            )
    else:
        lines.append("Possible: No explicit endpoint signatures were detected.")

    lines.extend(
        [
            "## Pagination",
            _safe_section("Pagination references were found." if "pagination" in topics or "cursor" in topics else ""),
            "",
            "## Webhooks",
            _safe_section("Webhook references were found." if "webhook" in topics else ""),
            "",
            "## Error Handling",
            "Possible: Error model not clearly documented in crawled snippets.",
            "",
            "## Example Integration Flow",
            "1. Configure credentials and authentication.",
            "2. Call read/list endpoints for core resources.",
            "3. Create/update data via write endpoints.",
            "4. Handle pagination, retries, and error responses.",
            "5. Subscribe to webhook events if available.",
            "",
            "## Gotchas",
            "- Possible: Confirm required headers and versioning strategy.",
            "- Possible: Confirm default pagination limits and rate-limit backoff behavior.",
            "",
            "## Sources",
        ]
    )

    lines.extend([f"- {source}" for source in extracted_data.get("sources", [])])
    return "\n".join(lines)


def build_markdown_guide(docs_url: str, pages: list[dict[str, str]], extracted_data: dict[str, Any]) -> str:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return _build_rule_based_markdown(extracted_data)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=openai_api_key)
        page_chunks = []
        for page in pages[:15]:
            page_chunks.append(f"URL: {page['page_url']}\nCONTENT:\n{page['page_text'][:5000]}")

        prompt = f"""
You are an API documentation analyst.

Your task:
Convert the following documentation pages into a structured API integration guide.

Rules:
- Only include confirmed information.
- If uncertain, label as \"Possible\".
- Include endpoint examples if available.
- Extract webhook events if present.

Return output in Markdown using this format:
# API Integration Guide
## Overview
## Base URLs
## Authentication
## Rate Limits
## Core Resources
## Endpoints
## Pagination
## Webhooks
## Error Handling
## Example Integration Flow
## Gotchas
## Sources

Documentation URL: {docs_url}

Crawled content:
{'\n\n'.join(page_chunks)}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.2,
        )
        return response.output_text
    except Exception:
        return _build_rule_based_markdown(extracted_data)
