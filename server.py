#!/usr/bin/env python3
"""
Tarife Scraper Web Server
FastAPI backend for the Vodafone tariff scraper with web interface.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import scraper
from scraper import TarifeScraper

app = FastAPI(title="Tarife Scraper", version="1.0.0")

# Store last scrape results in memory
last_scrape = {
    "tariffs": [],
    "timestamp": None,
    "status": "idle"
}


class ScrapeResponse(BaseModel):
    success: bool
    message: str
    tariff_count: int
    timestamp: Optional[str]
    tariffs: list


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/scrape")
async def scrape_tariffs():
    """Run the scraper and return results."""
    global last_scrape
    
    try:
        last_scrape["status"] = "running"
        
        scraper = TarifeScraper()
        tariffs = []
        
        for site in scraper.config.get('urls', []):
            url = site.get('url', '')
            if 'vodafone' in url.lower():
                tariffs = await scraper.scrape_vodafone(url)
        
        # Save to Excel
        if tariffs:
            output_path = scraper.config.get('output_file', 'tarifeler.xlsx')
            scraper.save_to_excel(tariffs, output_path)
        
        # Update last scrape
        last_scrape = {
            "tariffs": tariffs,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        return ScrapeResponse(
            success=True,
            message=f"{len(tariffs)} tarife başarıyla çekildi!",
            tariff_count=len(tariffs),
            timestamp=last_scrape["timestamp"],
            tariffs=tariffs
        )
        
    except Exception as e:
        last_scrape["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tariffs")
async def get_tariffs():
    """Get the last scraped tariffs."""
    return {
        "tariffs": last_scrape["tariffs"],
        "timestamp": last_scrape["timestamp"],
        "status": last_scrape["status"]
    }


@app.get("/api/download")
async def download_excel():
    """Download the Excel file."""
    excel_path = Path(__file__).parent / "tarifeler.xlsx"
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel dosyası bulunamadı. Önce scraping yapın.")
    return FileResponse(
        path=excel_path,
        filename="tarifeler.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
