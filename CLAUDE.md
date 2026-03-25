# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an automated arXiv academic progress daily report generator focused on medical AI. It searches arXiv for papers, uses LLM for intelligent filtering and information extraction, generates HTML reports, and deploys to GitHub Pages via GitHub Actions.

## Project Structure

```
.
├── main.py                     # Pipeline orchestrator
├── search_arxiv_medical.py     # Step 1: arXiv search & dual filtering
├── extract_paper_insights.py   # Step 2: LLM insight extraction
├── categorize_papers.py        # Step 3: Topic categorization
├── generate_html_report.py     # Step 4: HTML report generation
├── generate_index.py           # Step 5: Historical index generation
├── llm.py                      # LLM client wrapper
├── prompts.py                  # LLM prompt templates
├── pyproject.toml              # Python project config (uv)
├── uv.lock                     # Dependency lock file
├── .env.example                # Environment template
├── search_terms_cache.json     # Search terms cache (auto-generated)
├── relative_papers.json        # Intermediate: filtered papers
├── categorized_papers.json     # Intermediate: grouped papers
└── docs/                       # Output directory for GitHub Pages
    ├── index.html              # Historical index page
    ├── .nojekyll               # Disable Jekyll processing
    └── YYYY/MM/DD/
        ├── index.html          # Daily report
        └── metadata.json       # Report metadata
```

## Common Commands

### Running the Application

```bash
# Run the complete pipeline (uses OUTPUT_DIR from env or defaults to docs/YYYY/MM/DD/)
uv run main.py

# Or with explicit Python path
.venv/Scripts/python.exe main.py

# Run individual steps (useful for debugging)
.venv/Scripts/python.exe search_arxiv_medical.py      # Step 1: Search arXiv
.venv/Scripts/python.exe extract_paper_insights.py   # Step 2: Extract paper insights with LLM
.venv/Scripts/python.exe categorize_papers.py        # Step 3: Categorize papers by topic
.venv/Scripts/python.exe generate_html_report.py     # Step 4: Generate HTML report
.venv/Scripts/python.exe generate_index.py           # Step 5: Generate history index page
```

### Dependency Management

```bash
# Sync dependencies (uses uv)
uv sync

# Install dependencies manually
pip install arxiv openai python-dotenv httpx

# Lock dependencies
uv lock
```

## Architecture

### Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                         Data Pipeline                            │
└─────────────────────────────────────────────────────────────────┘

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

### Dual Filtering Mechanism

Papers go through two-stage filtering in `search_arxiv_medical.py`:

1. **Keyword Pre-filtering** (`FILTER_KEYWORDS`): Fast regex-based matching against paper title/abstract
2. **LLM Relevance Filtering** (`TOPIC_RELATED_PROMPT` in prompts.py): Semantic judgment of relevance to configured topics

### Dynamic Search Terms

`search_arxiv_medical.py` uses LLM to generate context-aware search terms based on configured topics. Results are cached in `search_terms_cache.json` (keyed by hash of `TOPICS` env var) to avoid regenerating on every run.

### Prompt Templates (prompts.py)

| Prompt | Purpose | Used In |
|--------|---------|---------|
| `GENERATE_SEARCH_TERMS_PROMPT` | Generate arXiv search terms from topics | search_arxiv_medical.py |
| `TOPIC_RELATED_PROMPT` | Judge paper relevance to topics | search_arxiv_medical.py |
| `EXTRACT_PAPER_INSIGHTS` | Extract keywords, summary, Chinese abstract | extract_paper_insights.py |

All prompts expect JSON responses without markdown formatting.

### Data File Formats

**relative_papers.json**
```json
{
  "papers": [
    {
      "entry_id": "arxiv:2401.12345",
      "title": "Paper Title",
      "authors": ["Author Name"],
      "abstract": "English abstract...",
      "published": "2024-01-15",
      "primary_category": "cs.AI",
      "pdf_url": "https://arxiv.org/pdf/2401.12345",
      "topics": ["医疗大模型", "医疗数据集"]
    }
  ],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-07"
  }
}
```

**categorized_papers.json**
```json
{
  "医疗大模型": [
    {
      "entry_id": "...",
      "title": "...",
      "llm_keywords": "关键词1, 关键词2",
      "llm_summary": "中文总结（100字以内）",
      "abstract_cn": "中文摘要翻译"
    }
  ]
}
```

**metadata.json** (per report)
```json
{
  "date": "2026-01-28",
  "year": "2026",
  "month": "01",
  "day": "28",
  "paper_count": 15,
  "topics": ["医疗大模型", "医疗数据集", "医疗智能体"]
}
```

### Module Responsibilities

| Module | Responsibility | Input | Output |
|--------|---------------|-------|--------|
| `main.py` | Pipeline orchestration, date calculation, directory management | Environment variables | Coordinated execution |
| `search_arxiv_medical.py` | arXiv API search, dual filtering, search term generation | arXiv API | `relative_papers.json` |
| `extract_paper_insights.py` | LLM-based insight extraction | `relative_papers.json` | Enriched papers |
| `categorize_papers.py` | Topic grouping | Enriched papers | `categorized_papers.json`, `metadata.json` |
| `generate_html_report.py` | HTML report generation | `categorized_papers.json` | `docs/YYYY/MM/DD/index.html` |
| `generate_index.py` | Historical index generation | All `metadata.json` files | `docs/index.html` |
| `llm.py` | LLM client initialization | Env vars | OpenAI-compatible client |
| `prompts.py` | Prompt templates | - | Formatted prompts |

### Module Dependencies

```
main.py
├── search_arxiv_medical.py
│   ├── llm.py
│   └── prompts.py (GENERATE_SEARCH_TERMS_PROMPT, TOPIC_RELATED_PROMPT)
├── extract_paper_insights.py
│   ├── llm.py
│   └── prompts.py (EXTRACT_PAPER_INSIGHTS)
├── categorize_papers.py
├── generate_html_report.py
└── generate_index.py
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | LLM API key | `sk-...` |
| `TOPICS` | Research topics (comma-separated) | `医疗大模型,医疗数据集,医疗智能体` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_BASE` | LLM API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | LLM model name | `gpt-4o-mini` |
| `FILTER_KEYWORDS` | Pre-filter keywords (comma-separated) | Large medical AI keyword list |
| `ARXIV_DAYS_BACK` | Days to search back | `7` |
| `ARXIV_MAX_RESULTS` | Max results per search term | `50` |
| `OUTPUT_DIR` | Output directory | `docs/YYYY/MM/DD` (auto-generated) |
| `FORCE_DATE_START` | Force specific start date | - |
| `FORCE_DATE_END` | Force specific end date | - |

### Variable Usage by Module

```
search_arxiv_medical.py:
  - ARXIV_DAYS_BACK, ARXIV_MAX_RESULTS
  - FILTER_KEYWORDS, TOPICS
  - FORCE_DATE_START, FORCE_DATE_END
  - OUTPUT_DIR

extract_paper_insights.py:
  - OUTPUT_DIR

categorize_papers.py:
  - OUTPUT_DIR

generate_html_report.py:
  - OUTPUT_DIR

llm.py:
  - OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_MODEL
```

## GitHub Actions Integration

**Workflow**: `.github/workflows/weekly-report.yml`

**Schedule**: Every day at 22:00 UTC (06:00 Beijing Time)

**Steps**:
1. Checkout repository
2. Install uv
3. Sync dependencies (`uv sync`)
4. Run pipeline with `DEPLOY_MODE=true`
5. Deploy `docs/` to GitHub Pages

**Required Secrets/Variables** (configured in Environment "Default"):
- `OPENAI_API_KEY` (Secret)
- `OPENAI_API_BASE` (Variable)
- `OPENAI_MODEL` (Variable)
- `TOPICS` (Variable)
- `FILTER_KEYWORDS` (Variable)
- `ARXIV_DAYS_BACK` (Variable)
- `ARXIV_MAX_RESULTS` (Variable)

## Date Calculation Logic

In `main.py`:
- `ARXIV_DAYS_BACK=7` (default): Searches papers from 7 days ago to yesterday
- Report directory: `docs/YYYY/MM/DD/` using today's date
- If directory exists with `index.html`, appends `-1`, `-2`, etc.

## Troubleshooting

### No papers found
- Check `FILTER_KEYWORDS` - may be too restrictive
- Verify `ARXIV_DAYS_BACK` is appropriate
- Check arXiv API connectivity

### LLM API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check `OPENAI_API_BASE` URL format (should end with `/v1`)
- Ensure model name is correct for your provider

### Missing intermediate files
- Each step depends on previous step's output
- Run steps sequentially or use `main.py` for full pipeline
- Check `OUTPUT_DIR` is consistent across runs

## Development Guidelines

### Adding a New Processing Step

1. Create new module following the naming pattern: `{action}_papers.py`
2. Read from previous step's output JSON
3. Write to new intermediate JSON file
4. Update `main.py` to include the new step
5. Update this documentation

### Modifying Prompts

All LLM prompts are in `prompts.py`. Prompts should return valid JSON without markdown formatting.

### Adding Environment Variables

1. Add to `.env.example` with documentation
2. Read in appropriate module using `os.getenv()`
3. Document in this file's Environment Variables section
4. Update GitHub Actions workflow if needed

### Styling Changes

HTML reports use a dark theme with CSS variables:
- `generate_html_report.py` - Report page styles
- `generate_index.py` - Index page styles

Key CSS variables:
```css
--bg-primary: #0f172a
--bg-secondary: #1e293b
--accent-primary: #6366f1
--accent-secondary: #8b5cf6
```
