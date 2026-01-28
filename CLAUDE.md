# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an arXiv Research Report Generator. It searches for recent papers on arXiv, extracts insights using LLM, categorizes them by topic, and generates a styled HTML report.

## Development Commands

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run the complete pipeline
.venv/Scripts/python.exe main.py

# Run individual steps
.venv/Scripts/python.exe search_arxiv_medical.py      # Step 1: Search arXiv
.venv/Scripts/python.exe extract_paper_insights.py    # Step 2: Extract insights with LLM
.venv/Scripts/python.exe categorize_papers.py         # Step 3: Categorize papers
.venv/Scripts/python.exe generate_html_report.py      # Step 4: Generate HTML report
```

## Architecture

### Pipeline Workflow

The project follows a 4-step pipeline defined in `main.py`:

1. **search_arxiv_medical.py**: Searches arXiv using LLM-generated search terms based on configured topics. Applies keyword filtering and LLM relevance filtering. Outputs `relative_papers.json`.
2. **extract_paper_insights.py**: Enriches papers with LLM-extracted keywords, Chinese summaries, and translated abstracts. Updates `relative_papers.json` in-place.
3. **categorize_papers.py**: Groups papers by their assigned topics. Outputs `categorized_papers.json`.
4. **generate_html_report.py**: Generates a styled HTML report (`medical_ai_report.html`) with filtering and collapsible abstracts.

### Key Files

- **llm.py**: OpenAI-compatible LLM client initialization from environment variables.
- **prompts.py**: LLM prompt templates (in Chinese) for search term generation, relevance filtering, and insight extraction.
- **category_paper.py**: Alternative categorization script that uses configured TOPICS from environment.

### Configuration

Configuration is loaded from `.env` file:

- `OPENAI_API_BASE`, `OPENAI_API_KEY`, `OPENAI_MODEL`: LLM API configuration
- `TOPICS`: Comma-separated topics for categorization (e.g., "医疗大模型,医疗数据集,医疗智能体")
- `ARXIV_DAYS_BACK`: Days to look back for papers (default: 7)
- `ARXIV_MAX_RESULTS`: Max results per search term (default: 50)
- `FILTER_KEYWORDS`: Comma-separated keywords for initial paper filtering

### Data Flow

```
search_arxiv_medical.py → relative_papers.json
                              ↓
                   extract_paper_insights.py
                              ↓
                     categorize_papers.py → categorized_papers.json
                              ↓
                     generate_html_report.py → medical_ai_report.html
```

### Output Files

- `relative_papers.json`: Raw search results with paper metadata and LLM insights
- `categorized_papers.json`: Papers grouped by topic
- `medical_ai_report.html`: Final styled HTML report
- `search_terms_cache.json`: Cache for LLM-generated search terms
