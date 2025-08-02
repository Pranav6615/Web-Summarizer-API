# app/utils.py

import re
import os
from datetime import datetime
from urllib.parse import urlparse

from config import OUTPUT_DIR, EXCLUDED_PATTERNS

# Helper functions for markdown processing
def split_pages(md_text):
    """Splits content by page using "## Page N:" headers."""
    pattern = r"(## Page \d+: .+?)(?=\n## Page \d+:|\Z)"
    return re.findall(pattern, md_text, flags=re.DOTALL)

def extract_title_and_body(page_block):
    """Extracts "Page N: Title" and page body from a markdown block."""
    header_match = re.match(r"## (Page \d+: .+?)\n", page_block)
    title = header_match.group(1).strip() if header_match else "Untitled"
    body = page_block[len(header_match.group(0)):] if header_match else page_block
    return title, body

def generate_markdown_for_page(index, d):
    """Generates a markdown block for a single scraped page."""
    lines = []
    lines.append(f"## Page {index+1}: {d['title']}")
    lines.append(f"**URL**: <{d['url']}>")
    lines.append(f"**Title**: {d['title']}")
    lines.append(f"**Description**: {d['description']}\n")
    lines.append(f"### Main Headings\n#### H1: {d['h1']}")
    if d['h2_headings']:
        lines.append("#### H2:")
        lines += [f"- {h2}" for h2 in d['h2_headings']]
    if d['h3_headings']:
        lines.append("#### H3:")
        lines += [f"- {h3}" for h3 in d['h3_headings']]
    lines.append(f"\n### Content Preview\n" + "\n".join([f"> {line}" for line in d['content_preview'].split('\n') if line.strip()]))
    return "\n".join(lines)

def generate_full_markdown_report(data, url, depth, filename):
    """Generates and saves a comprehensive markdown report of all scraped pages."""
    domain = urlparse(url).netloc
    lines = [
        f"# {domain} - Website Content Analysis",
        f"\n## Crawl Metadata",
        f"- **Source URL**: {url}",
        f"- **Crawl Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Total Pages Crawled**: {len(data)}",
        f"- **Crawl Depth**: {depth}",
        f"- **Excluded Patterns**: {', '.join([p.pattern for p in EXCLUDED_PATTERNS])}\n",
        "---\n"
    ]
    for i, d in enumerate(data):
        lines.append(generate_markdown_for_page(i, d))
        lines.append("\n---\n")

    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filepath