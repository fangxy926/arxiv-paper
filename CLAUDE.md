# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated arXiv academic progress weekly report generator focused on medical AI. It searches arXiv for papers, uses LLM for intelligent filtering and information extraction, generates HTML reports, and deploys to GitHub Pages via GitHub Actions.

## Common Commands

### Running the Application

```bash
# Run the complete workflow (search → extract → categorize → generate report)
.venv/Scripts/python.exe main.py

# Run individual steps
.venv/Scripts/python.exe search_arxiv_medical.py      # Step 1: Search arXiv
.venv/Scripts/python.exe extract_paper_insights.py   # Step 2: Extract paper insights with LLM
.venv/Scripts/python.exe categorize_papers.py        # Step 3: Categorize papers by topic
.venv/Scripts/python.exe generate_html_report.py     # Step 4: Generate HTML report
.venv/Scripts/python.exe generate_index.py           # Generate history index page
```

### Dependency Management

```bash
# Sync dependencies (uses uv)
uv sync

# Install dependencies manually
pip install arxiv openai python-dotenv httpx
```

## Architecture

### Data Flow Pipeline

```
search_arxiv_medical.py
       ↓
relative_papers.json  (papers + date range metadata)
       ↓
extract_paper_insights.py  (adds Chinese abstract, keywords, summary)
       ↓
categorize_papers.py
       ↓
categorized_papers.json  (papers grouped by topic)
       ↓
generate_html_report.py + generate_index.py
       ↓
docs/YYYY/MM/DD/index.html + docs/index.html
```

### Key Design Patterns

**Dual Filtering Mechanism**: Papers go through keyword-based pre-filtering (`FILTER_KEYWORDS` env var), then LLM-based relevance filtering (`TOPIC_RELATED_PROMPT` in prompts.py).

**Dynamic Search Terms**: `search_arxiv_medical.py` uses LLM to generate search terms based on configured topics (cached in `search_terms_cache.json`).

**Date Directory Structure**: Reports are saved to `docs/YYYY/MM/DD/index.html` for historical archiving. Each report includes a `metadata.json` for index generation.

**Environment-Driven Configuration**: All behavior is controlled via environment variables (see `.env.example`). Key variables:
- `TOPICS`: Comma-separated list of research topics (e.g., "医疗大模型,医疗数据集")
- `FILTER_KEYWORDS`: Comma-separated keywords for pre-filtering
- `ARXIV_DAYS_BACK`: Number of days to search back (default: 7)
- `OUTPUT_DIR`: Target directory for generated files

### Module Responsibilities

- `main.py`: Orchestrates the full pipeline, calculates date ranges, manages output directories
- `search_arxiv_medical.py`: Searches arXiv API, applies dual filtering, outputs `relative_papers.json`
- `extract_paper_insights.py`: Uses LLM to extract keywords, Chinese summary, and translated abstract
- `categorize_papers.py`: Groups papers by topic, outputs `categorized_papers.json` and `metadata.json`
- `generate_html_report.py`: Creates dark-themed, responsive HTML report with collapsible abstracts
- `generate_index.py`: Scans all date directories to build historical index page
- `llm.py`: LLM client initialization (OpenAI-compatible API)
- `prompts.py`: LLM prompt templates for topic filtering, search term generation, and insight extraction

### GitHub Actions Integration

The workflow in `.github/workflows/weekly-report.yml`:
1. Runs every Monday at 00:00 UTC (08:00 Beijing Time)
2. Sets `DEPLOY_MODE=true` which triggers index generation in `main.py`
3. Deploys `docs/` directory to GitHub Pages

When `DEPLOY_MODE=true`, `main.py` generates the index page after creating the report. In local development, only the dated report is generated.
