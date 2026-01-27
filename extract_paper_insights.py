#!/usr/bin/env python3
"""
Extract keywords, Chinese summary, and translated abstract from paper using LLM.
Updates relative_papers.json in-place.
"""
import arxiv
import json
import os
from llm import get_llm_client
from prompts import EXTRACT_PAPER_INSIGHTS

INPUT_FILE = 'relative_papers.json'


def extract_insights(client, title, abstract, max_retries=2):
    """Extract keywords, Chinese summary, and translated abstract using LLM"""
    if not client:
        return None, None, None

    prompt = EXTRACT_PAPER_INSIGHTS.format(title=title, abstract=abstract)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=8192
            )

            if not response.choices:
                raise ValueError("Empty response choices")

            content = response.choices[0].message.content
            data = json.loads(content)
            return (
                data.get('keywords'),
                data.get('summary'),
                data.get('abstract_cn')
            )

        except Exception as e:
            if attempt < max_retries - 1:
                continue
            print(f"[WARN] LLM extraction failed: {e}")
            return None, None, None

    return None, None, None


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    client = arxiv.Client()
    llm_client = get_llm_client()

    print(f"Processing {len(papers)} papers...")

    updated_count = 0

    for i, p in enumerate(papers):
        arxiv_id = p['arxiv_id'].split('v')[0]

        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(client.results(search))

            # Extract keywords, summary, and translated abstract
            llm_keywords, llm_summary, abstract_cn = extract_insights(
                llm_client, result.title, result.summary
            )

            # Update paper in-place
            p['abstract'] = result.summary
            p['llm_keywords'] = llm_keywords
            p['llm_summary'] = llm_summary
            p['abstract_cn'] = abstract_cn

            updated_count += 1
            print(f"[OK] ({i+1}/{len(papers)}) {arxiv_id}")

        except Exception as e:
            print(f"[ERR] {arxiv_id}: {e}")

    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    print(f"\n=== Summary ===")
    print(f"Updated: {updated_count}/{len(papers)} papers")


if __name__ == '__main__':
    main()
