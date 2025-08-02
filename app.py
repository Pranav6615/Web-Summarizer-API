# main.py

import asyncio
import sys
import os
import uuid
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

# Set Proactor for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from config import ScrapeRequest, OUTPUT_DIR
from scraper import scrape_website
from summarizer import summarize_page
from utils import generate_markdown_for_page, generate_full_markdown_report

app = FastAPI()

@app.post("/scrape")
async def run_scraper(req: ScrapeRequest):
    """
    API endpoint to start the web scraping and summarization process.
    """
    try:
        data = await scrape_website(req.url, req.depth)
        if not data:
            raise ValueError("No content scraped. Check URL or JS restrictions.")

        # Generate markdown for each page and summarize
        final_output_lines = [f"# {req.url} - Website Summaries\n"]
        for i, page_data in enumerate(data):
            page_markdown_content = generate_markdown_for_page(i, page_data)
            print(f"🔎 Summarizing: Page {i+1}: {page_data['title']}")
            summary = await summarize_page(page_markdown_content)
            final_output_lines.append(f"## Page {i+1}: {page_data['title']}\n\n**Summary:**\n{summary}\n\n---")

        summary_filename = f"summary_{uuid.uuid4().hex}.md"
        summary_filepath = os.path.join(OUTPUT_DIR, summary_filename)
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(final_output_lines))
        print(f"\n✅ Summaries saved to: {summary_filepath}")

        # This generates a full report file, but the primary output is the summary
        # report for the user.
        full_report_filename = f"report_{uuid.uuid4().hex}.md"
        generate_full_markdown_report(data, req.url, req.depth, full_report_filename)

        return JSONResponse({
            "message": "✅ Crawling + Summaries Complete",
            "download_url": f"/download/{os.path.basename(summary_filepath)}"
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    API endpoint to download a generated file.
    """
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="text/markdown", filename=filename)

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this file from the project root using `python -m uvicorn main:app --reload`
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)