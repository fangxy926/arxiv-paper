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
from prompts import TOPIC_RELATED_PROMPT, GENERATE_SEARCH_TERMS_PROMPT

# Configuration from environment variables
DAYS_BACK = int(os.getenv('ARXIV_DAYS_BACK', 7))  # Default: last 7 days
MAX_RESULTS_PER_TERM = int(os.getenv('ARXIV_MAX_RESULTS', 50))

# Filter keywords from environment variables (comma-separated)
FILTER_KEYWORDS_RAW = os.getenv('FILTER_KEYWORDS', '')
FILTER_KEYWORDS = FILTER_KEYWORDS_RAW.split(',') if FILTER_KEYWORDS_RAW else []

GIVEN_TOPICS = os.getenv('TOPICS')

# Cache file for generated search terms
SEARCH_TERMS_CACHE_FILE = "search_terms_cache.json"


def generate_search_terms(client, topics, max_retries=2):
    """使用 LLM 根据给定主题生成 arXiv 搜索词
    返回: list of search terms
    """
    if not client:
        raise ValueError("LLM client is required to generate search terms")

    # 尝试从缓存读取
    cache_data = load_search_terms_cache()
    if cache_data and cache_data.get("topics") == topics:
        print(f"[INFO] Using cached search terms for topics: {topics}")
        return cache_data.get("terms", [])

    prompt = GENERATE_SEARCH_TERMS_PROMPT.format(topics=topics)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=2048
            )

            if not response.choices:
                raise ValueError("Empty response choices")

            content = response.choices[0].message.content.strip()

            # 清理可能的markdown包装
            content_clean = content
            if content.startswith('```json'):
                content_clean = content[7:]
            if content.startswith('```'):
                content_clean = content[3:]
            if content_clean.endswith('```'):
                content_clean = content_clean[:-3]
            content_clean = content_clean.strip()

            result = json.loads(content_clean)
            terms = result.get('search_terms', [])

            if terms and len(terms) >= 1:
                # 保存到缓存
                save_search_terms_cache(topics, terms)
                print(f"[INFO] Generated {len(terms)} search terms for topics: {topics}")
                return terms

        except json.JSONDecodeError as e:
            print(f"[WARN] Failed to parse LLM response: {e}")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            print(f"[WARN] Failed to generate search terms: {e}")
            if attempt < max_retries - 1:
                continue

    raise ValueError("Failed to generate search terms from LLM")


def load_search_terms_cache():
    """从缓存文件加载搜索词"""
    if not os.path.exists(SEARCH_TERMS_CACHE_FILE):
        return None
    try:
        with open(SEARCH_TERMS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load search terms cache: {e}")
        return None


def save_search_terms_cache(topics, terms):
    """保存搜索词到缓存文件"""
    cache_data = {
        "topics": topics,
        "terms": terms,
        "generated_at": datetime.now().isoformat()
    }
    try:
        with open(SEARCH_TERMS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Failed to save search terms cache: {e}")
    

# Calculate date range dynamically
now = datetime.now(timezone.utc)
end_date = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)
start_date = end_date - timedelta(days=DAYS_BACK - 1)
start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)

all_results = []

client = arxiv.Client()
llm_client = get_llm_client()

# 动态生成搜索词
print(f"[INFO] Topics: {GIVEN_TOPICS}")
search_terms = generate_search_terms(llm_client, GIVEN_TOPICS, max_retries=2)
print(f"[INFO] Search terms: {search_terms}")


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
    LLM筛选：判断论文是否与TOPIC相关，并返回具体所属的主题
    返回: (related: bool, topics: list)
    """
    if not client:
        return True, []  # 没有LLM时不过滤

    prompt = TOPIC_RELATED_PROMPT.format(title=title, abstract=abstract, topics=GIVEN_TOPICS)

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

            content = response.choices[0].message.content.strip()

            # 尝试解析JSON
            import json
            try:
                # 清理可能的markdown包装
                content_clean = content
                if content.startswith('```json'):
                    content_clean = content[7:]
                if content.endswith('```'):
                    content_clean = content[:-3]
                content_clean = content_clean.strip()

                result = json.loads(content_clean)
                related = result.get('related', False)
                topics = result.get('topics', [])
                return related, topics
            except json.JSONDecodeError as e:
                print(f"[WARN] Failed to parse LLM response: {e}, content: {content[:100]}")
                # 回退到简单判断
                return content.lower().startswith('yes'), []

        except Exception as e:
            if attempt < max_retries - 1:
                continue
            print(f"[WARN] LLM filter failed: {e}")
            return True, []  # 出错时保留

    return True, []


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
            related, topics = llm_filter(llm_client, result.title, result.summary)
            if not related:
                continue

            paper_info = {
                "title": result.title,
                "authors": [str(a) for a in result.authors],
                "published": published.strftime("%Y-%m-%d"),
                "summary": result.summary[:500],
                "pdf_url": result.pdf_url,
                "primary_category": category,
                "topics": topics  # LLM返回的所属主题列表
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

# Save results with date range metadata
output_file = "relative_papers.json"
output_data = {
    "papers": all_results,
    "date_range": {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
}
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"Total unique papers found: {len(all_results)}")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Results saved to: {output_file}")
