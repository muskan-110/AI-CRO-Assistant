import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.scraper.page_scraper import scrape_page as _scrape_page
from app.services.ai.ad_analyzer import analyze_ad
from app.services.ai.personalization import personalize_page

router = APIRouter()
_executor = ThreadPoolExecutor()


class AnalyzeAdRequest(BaseModel):
    adCreative: str

class ScrapeRequest(BaseModel):
    url: str

class GenerateRequest(BaseModel):
    adCreative: dict
    landingUrl: str
    pageData: dict = {}


@router.get("/")
def root():
    return {"message": "Backend running 🚀"}


@router.post("/analyze-ad")
async def analyze_ad_route(data: AnalyzeAdRequest):
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, analyze_ad, data.adCreative)
    except Exception as e:
        _check_balance_error(e)
        raise HTTPException(status_code=500, detail=f"Ad analysis failed: {str(e)}")
    return result


@router.post("/scrape")
async def scrape_page_route(data: ScrapeRequest):
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _scrape_page, data.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    if not result.get("success"):
        status_map = {
            "proxy_blocked": 502, "connection_failed": 502,
            "timeout": 504, "bad_status": 502, "unknown": 500,
        }
        error_type = result.get("error_type", "unknown")
        raise HTTPException(
            status_code=status_map.get(error_type, 502),
            detail=result.get("error_message", "Scraping failed.")
        )
    return result


@router.post("/generate")
async def generate(data: GenerateRequest):
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _executor, personalize_page, data.adCreative, data.pageData, data.landingUrl
        )
    except Exception as e:
        _check_balance_error(e)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    return result


def _check_balance_error(e: Exception):
    """Raise a clear 402 error if the issue is OpenRouter balance."""
    err = str(e).lower()
    if any(word in err for word in ["402", "balance", "payment", "credits", "billing", "insufficient"]):
        raise HTTPException(
            status_code=402,
            detail="OpenRouter balance is negative or exhausted. Top up at https://openrouter.ai/credits"
        )