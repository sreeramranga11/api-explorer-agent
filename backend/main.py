from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from crawler.doc_crawler import crawl_documentation
from crawler.extractor import extract_api_content
from summarizer.guide_builder import build_markdown_guide


class GenerateRequest(BaseModel):
    docs_url: HttpUrl


class GenerateResponse(BaseModel):
    status: str
    markdown: str
    sources: list[str]


app = FastAPI(title="API Explorer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        pages = crawl_documentation(str(request.docs_url), max_pages=50)
        if not pages:
            raise HTTPException(status_code=400, detail="No pages could be crawled from the provided URL.")

        extracted = extract_api_content(pages)
        markdown = build_markdown_guide(
            docs_url=str(request.docs_url),
            pages=pages,
            extracted_data=extracted,
        )

        return GenerateResponse(
            status="complete",
            markdown=markdown,
            sources=[page["page_url"] for page in pages],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc
