# markdown_utils.py
import os
from urllib.parse import urlparse
from datetime import datetime
from config import EXCLUDED_PATTERNS


def generate_markdown_for_page(index, d):
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


def generate_full_markdown_report(data, url, depth, filename, output_dir):
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

    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filepath
