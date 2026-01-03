"""
Magenta Tarife Scraper
FastAPI backend for cross-operator tariff comparison.
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

app = FastAPI(title="Magenta", version="1.0.0")

# Store last scrape results in memory
all_provider_data = {
    "vodafone": [],
    "turkcell": [],
    "turkcell_mevcut": []
}
last_scrape = {
    "timestamp": None,
    "status": "idle",
    "message": "",
    "current_provider": None
}

async def run_scraping_task(provider: str):
    """Background task to run the scraper."""
    global last_scrape, all_provider_data
    try:
        last_scrape["status"] = "running"
        last_scrape["message"] = f"{provider} scraper başlatıldı..."
        last_scrape["current_provider"] = provider
        
        scraper = TarifeScraper()
        tariffs = []
        
        url = ""
        provider_key = provider.lower()
        if provider_key == "vodafone":
            url = "https://www.vodafone.com.tr/numara-tasima-yeni-hat/tarifeler?homeheader=post-vodafoneluol"
            tariffs = await scraper.scrape_vodafone(url)
        elif provider_key == "turkcell":
            url = "https://www.turkcell.com.tr/trc/turkcellli-olmak/paket-secimi"
            tariffs = await scraper.scrape_turkcell(url)
        elif provider_key == "turkcell_mevcut":
            url = "https://www.turkcell.com.tr/paket-ve-tarifeler/4-5-g-hizinda?paymentType=faturali-hat"
            tariffs = await scraper.scrape_turkcell_mevcut(url)
        
        # Save to Excel
        if tariffs:
            all_provider_data[provider_key] = tariffs
            output_path = scraper.config.get('output_file', 'tarifeler.xlsx')
            # Consolidate all for excel? For now just the current one as before.
            # Actually, let's just save current.
            scraper.save_to_excel(tariffs, output_path)
        
        last_scrape["timestamp"] = datetime.now().isoformat()
        last_scrape["status"] = "completed"
        last_scrape["message"] = f"{len(tariffs)} {provider} tarifesi başarıyla çekildi."
        
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
async def start_scrape(background_tasks: BackgroundTasks, provider: str = "vodafone"):
    """Start the scraper in the background."""
    global last_scrape
    if last_scrape["status"] == "running":
        return {"success": False, "message": "Scraper zaten çalışıyor."}
    
    last_scrape["status"] = "running"
    last_scrape["message"] = f"{provider} işlemi başlatılıyor..."
    background_tasks.add_task(run_scraping_task, provider)
    
    return {"success": True, "message": f"{provider} scraping işlemi başlatıldı."}

@app.get("/api/tariffs")
async def get_tariffs():
    """Get the last scraped tariffs and current status."""
    return {
        "providers": all_provider_data,
        "timestamp": last_scrape["timestamp"],
        "status": last_scrape["status"],
        "message": last_scrape["message"],
        "current_provider": last_scrape["current_provider"]
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
