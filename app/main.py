from fastapi import FastAPI, HTTPException
from .models import ScrapeRequest
from .scraper import start_scraping_session
from .logger import logger

app = FastAPI()

@app.post("/scrape_jobs")
def scrape_jobs(request: ScrapeRequest):
    try:
        logger.info(f"📡 Received scraping request for URL: {request.url}")
        start_scraping_session(request.url)
        return {"status": "success", "message": "Scraping completed successfully."}
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail=str(e))