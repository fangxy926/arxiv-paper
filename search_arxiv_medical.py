#!/usr/bin/env python3
"""
Search for recent medical AI papers on arXiv
Only focuses on: medical LLMs, medical datasets, medical AI agents
"""
import arxiv
from datetime import datetime, timedelta, timezone
import json
import os
from llm import get_llm_client
from prompts import TOPIC_RELATED_PROMPT

# Configuration from environment variables
DAYS_BACK = int(os.getenv('ARXIV_DAYS_BACK', 7))  # Default: last 7 days
MAX_RESULTS_PER_TERM = int(os.getenv('ARXIV_MAX_RESULTS', 50))

# Filter keywords from environment variables (comma-separated)
FILTER_KEYWORDS_RAW = os.getenv('FILTER_KEYWORDS', '')
FILTER_KEYWORDS = FILTER_KEYWORDS_RAW.split(',') if FILTER_KEYWORDS_RAW else []

# Calculate date range dynamically
now = datetime.now(timezone.utc)
end_date = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)
start_date = end_date - timedelta(days=DAYS_BACK - 1)
start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)

# Core search terms for medical AI
search_terms = [
    # Medical LLM / Dataset / Agent (7 key terms)
    'medical "large language model"',
    'clinical "language model"',
    '"medical dataset"',
    '"medical benchmark"',
    '"medical agent"',
    'clinical reasoning model',
    '"medical reasoning"',
]

all_results = []

client = arxiv.Client()
llm_client = get_llm_client()


def keywords_filter(title: str, summary: str) -> bool:
    """关键词初筛：检查是否包含任一配置关键词
    如果关键词列表为空，跳过初筛直接返回True
    """
    if not FILTER_KEYWORDS:
        return True
    text = (title + ' ' + summary).lower()
    return any(kw in text for kw in FILTER_KEYWORDS)


def llm_filter(client, title, abstract, max_retries=2):
    """
    LLM筛选：判断论文是否与TOPIC相关
    返回: yes=相关, no=不相关
    """
    if not client:
        return True  # 没有LLM时不过滤

    prompt = TOPIC_RELATED_PROMPT.format(title=title, abstract=abstract)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.1,
                max_tokens=8192
            )

            if not response.choices:
                raise ValueError("Empty response choices")

            content = response.choices[0].message.content.strip().lower()
            return content.startswith('yes')

        except Exception as e:
            if attempt < max_retries - 1:
                continue
            print(f"[WARN] LLM filter failed: {e}")
            return True  # 出错时保留

    return True


for term in search_terms:
    print(f"Searching for: {term}")

    # Combine search term with medical keyword filter
    search_query = f'{term}'

    search = arxiv.Search(
        query=search_query,
        max_results=MAX_RESULTS_PER_TERM,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    try:
        for result in client.results(search):
            published = result.published
            category = result.primary_category

            # Filter by date range
            if not (start_date <= published <= end_date):
                continue

            # 关键词初筛
            if not keywords_filter(result.title, result.summary):
                continue

            # LLM二次筛选：判断是否与医疗大模型/数据集/智能体相关
            if not llm_filter(llm_client, result.title, result.summary):
                continue

            paper_info = {
                "title": result.title,
                "authors": [str(a) for a in result.authors],
                "published": published.strftime("%Y-%m-%d"),
                "summary": result.summary[:500],
                "pdf_url": result.pdf_url,
                "primary_category": category
            }

            # Extract arxiv ID from entry_id
            arxiv_id = result.entry_id.split("/")[-1] if "/" in result.entry_id else result.entry_id
            paper_info["arxiv_id"] = arxiv_id

            if arxiv_id not in [r["arxiv_id"] for r in all_results]:
                all_results.append(paper_info)
                print(f"  Found: {arxiv_id} - {paper_info['title'][:60]}...")

    except Exception as e:
        print(f"  Error searching {term}: {e}")

# Sort by date (most recent first)
all_results.sort(key=lambda x: x["published"], reverse=True)

# Save results
output_file = "relative_papers.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"Total unique papers found: {len(all_results)}")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Results saved to: {output_file}")
