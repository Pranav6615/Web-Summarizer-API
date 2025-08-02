# app/config.py

import os
import re
from openai import OpenAI
from pydantic import BaseModel

# --- API Keys & Clients ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set.")
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Output Directory ---
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Excluded Patterns for Crawling ---
EXCLUDED_PATTERNS = [
    re.compile(p) for p in [
        r"/login", r"/signup", r"/help", r"/docs", r"/support", r"/blog", r"/community",
        r"/pricing", r"/terms", r"/privacy", r"/cookie-policy", r"/contact", r"/careers",
        r"#", r"\?", r"/events", r"/webinars", r"/resources", r"/case-studies",
        r"/integrations", r"/developers", r"/status", r"/sitemap", r"/feed"
    ]
]

# --- Pydantic Models ---
class ScrapeRequest(BaseModel):
    url: str
    depth: int = 1