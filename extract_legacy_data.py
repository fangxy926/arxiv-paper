#!/usr/bin/env python3
"""
Extract paper data from old index.html files and create papers_data.json
for backward compatibility with the new shared template.
"""
import json
import re
import os
from pathlib import Path
from datetime import datetime

def extract_papers_from_html(html_content):
    """Extract paper data from old index.html format."""
    papers = []
    papers_by_topic = {}

    # Find all paper cards - old format uses <article class="paper-card">
    # Pattern to match from <article to </article>
    card_pattern = r'<article class="paper-card"[^>]*>(.*?)</article>'
    cards = re.findall(card_pattern, html_content, re.DOTALL)

    for card in cards:
        paper = {}

        # Extract category from data-category attribute or paper-category div
        cat_match = re.search(r'data-category="([^"]+)"', card)
        if cat_match:
            category = cat_match.group(1)
        else:
            # Try to extract from paper-category div
            cat_div_match = re.search(r'<div class="paper-category">([^·]+)', card)
            category = cat_div_match.group(1).strip() if cat_div_match else 'Other'

        # Extract arxiv_id and title
        title_match = re.search(r'<h3 class="paper-title">.*?<a href="https://arxiv\.org/abs/([^"]+)"[^>]*>(.*?)</a>', card, re.DOTALL)
        if title_match:
            paper['arxiv_id'] = title_match.group(1).strip()
            # Remove HTML tags from title
            title = re.sub(r'<[^>]+>', '', title_match.group(2))
            paper['title'] = title.strip()

        # Extract published date - look for date pattern after SVG
        date_match = re.search(r'<svg[^>]*>.*?Calendar.*?</svg>\s*([\d]{4}-[\d]{2}-[\d]{2})', card, re.DOTALL)
        if not date_match:
            # Alternative: look for date in meta
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})</span>', card)
        if date_match:
            paper['published'] = date_match.group(1).strip()

        # Extract category info
        cat_text_match = re.search(r'<div class="paper-category">([^<]+)</div>', card)
        if cat_text_match:
            cat_parts = cat_text_match.group(1).split('·')
            if len(cat_parts) > 1:
                paper['primary_category'] = cat_parts[1].strip()
            else:
                paper['primary_category'] = 'cs.AI'

        # Extract summary
        summary_match = re.search(r'<p class="paper-summary">(.*?)</p>', card, re.DOTALL)
        if summary_match:
            summary = re.sub(r'<[^>]+>', '', summary_match.group(1))
            paper['llm_summary'] = summary.strip()

        # Extract keywords from paper-footer
        keywords_match = re.search(r'<div class="paper-footer">.*?<div class="paper-keywords">(.*?)</div>', card, re.DOTALL)
        if keywords_match:
            keywords_html = keywords_match.group(1)
            keyword_list = re.findall(r'<span class="keyword[^"]*">([^<]+)</span>', keywords_html)
            if keyword_list:
                paper['llm_keywords'] = ', '.join(k.strip() for k in keyword_list)

        # Extract authors
        authors_match = re.search(r'<div class="paper-authors">(.*?)</div>', card, re.DOTALL)
        if authors_match:
            authors_html = authors_match.group(1)
            author_names = re.findall(r'<span class="author[^"]*">([^<]+)</span>', authors_html)
            if author_names:
                # Filter out '等' and create author objects
                paper['authors'] = [{'name': name.strip()} for name in author_names if name.strip() not in ['等', '']]

        # Extract PDF URL
        pdf_match = re.search(r'href="(https://arxiv\.org/pdf/[^"]+)"', card)
        if pdf_match:
            paper['pdf_url'] = pdf_match.group(1)

        if paper.get('arxiv_id'):
            papers.append(paper)
            if category not in papers_by_topic:
                papers_by_topic[category] = []
            papers_by_topic[category].append(paper)

    return papers, papers_by_topic


def create_papers_data_for_date(date_dir):
    """Create papers_data.json for a specific date directory."""
    date_path = Path(date_dir)
    index_file = date_path / 'index.html'
    output_file = date_path / 'papers_data.json'
    metadata_file = date_path / 'metadata.json'

    if not index_file.exists():
        print(f"Skipping {date_dir}: no index.html")
        return False

    if output_file.exists():
        print(f"Skipping {date_dir}: papers_data.json already exists")
        return False

    # Read HTML
    with open(index_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract papers
    papers, papers_by_topic = extract_papers_from_html(html)

    if not papers:
        print(f"Warning: {date_dir} - no papers extracted from HTML")
        return False

    # Load metadata for date range
    date_range = {"start_date": "", "end_date": ""}
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            date_range = metadata.get('date_range', date_range)
    else:
        # Try to extract from HTML
        range_match = re.search(r'<div class="header-range">([^<]+)</div>', html)
        if range_match:
            range_text = range_match.group(1).strip()
            # Format: "2026-03-23 — 2026-03-23"
            parts = range_text.split('—')
            if len(parts) == 2:
                date_range = {
                    "start_date": parts[0].strip(),
                    "end_date": parts[1].strip()
                }

    # Build output
    topics = list(papers_by_topic.keys())
    output_data = {
        'date_range': date_range,
        'topics': topics,
        'papers_by_topic': papers_by_topic,
        'total_count': len(papers),
        'generated_at': datetime.now().isoformat(),
        'source': 'extracted_from_legacy_html'
    }

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Created {output_file}: {len(papers)} papers, {len(topics)} topics")
    return True


def main():
    docs_dir = Path('docs')

    # Find all date directories
    date_dirs = []
    for year_dir in docs_dir.glob('2*'):  # Year directories like 2026
        if year_dir.is_dir():
            for month_dir in year_dir.glob('*'):
                if month_dir.is_dir():
                    for day_dir in month_dir.glob('*'):
                        if day_dir.is_dir():
                            date_dirs.append(day_dir)

    print(f"Found {len(date_dirs)} date directories")
    print()

    success_count = 0
    for date_dir in sorted(date_dirs):
        if create_papers_data_for_date(date_dir):
            success_count += 1

    print()
    print(f"Done! Created papers_data.json for {success_count} legacy reports.")


if __name__ == '__main__':
    main()
