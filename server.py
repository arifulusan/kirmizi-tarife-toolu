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

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Import scraper
from scraper import TarifeScraper

app = FastAPI(title="Kırmızı Tarife Tool'u", version="1.0.0")

# Store last scrape results in memory
last_scrape = {
    "tariffs": [],
    "timestamp": None,
    "status": "idle",
    "message": ""
}

async def run_scraping_task():
    """Background task to run the scraper."""
    global last_scrape
    try:
        last_scrape["status"] = "running"
        last_scrape["message"] = "Scraper başlatıldı..."
        
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
        last_scrape["tariffs"] = tariffs
        last_scrape["timestamp"] = datetime.now().isoformat()
        last_scrape["status"] = "completed"
        last_scrape["message"] = f"{len(tariffs)} tarife başarıyla çekildi."
        
    except Exception as e:
        last_scrape["status"] = "error"
        last_scrape["message"] = f"Hata: {str(e)}"
        print(f"Scrape Error: {e}")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/api/scrape")
async def start_scrape(background_tasks: BackgroundTasks):
    """Start the scraper in the background."""
    global last_scrape
    if last_scrape["status"] == "running":
        return {"success": True, "message": "Scraper zaten çalışıyor."}
    
    last_scrape["status"] = "running"
    last_scrape["message"] = "İşlem başlatılıyor..."
    background_tasks.add_task(run_scraping_task)
    
    return {"success": True, "message": "Scraping işlemi başlatıldı."}

@app.get("/api/tariffs")
async def get_tariffs():
    """Get the last scraped tariffs and current status."""
    return {
        "tariffs": last_scrape["tariffs"],
        "timestamp": last_scrape["timestamp"],
        "status": last_scrape["status"],
        "message": last_scrape["message"]
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
