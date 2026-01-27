#!/usr/bin/env python3
"""
Categorize medical AI papers based on topics field from search_arxiv_medical.py
Reads relative_papers.json and outputs categorized_papers.json
"""
import json


def categorize_papers(input_file: str = 'relative_papers.json', output_file: str = 'categorized_papers.json') -> dict:
    """
    Categorize papers based on their topics field.
    Output keys directly correspond to the topics found in the input data.

    Args:
        input_file: Path to input JSON file (default: relative_papers.json)
        output_file: Path to output JSON file (default: categorized_papers.json)

    Returns:
        Dictionary with categorized papers and date range
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)

    papers = input_data.get('papers', [])
    date_range = input_data.get('date_range', {})

    # Dynamic categories based on actual topics
    categorized = {}
    paper_tracker = {}  # topic -> set of arxiv_ids

    for p in papers:
        topics_raw = p.get('topics', [])
        # Handle both list and comma-separated string formats
        if isinstance(topics_raw, str):
            topics = [t.strip() for t in topics_raw.split(',')]
        elif isinstance(topics_raw, list):
            topics = topics_raw
        else:
            topics = []

        if not topics:
            topics = ['Other']

        # Add paper to each topic category
        for topic in topics:
            topic = topic.strip()
            if not topic:
                continue
            if topic not in categorized:
                categorized[topic] = []
                paper_tracker[topic] = set()
            if p['arxiv_id'] not in paper_tracker[topic]:
                paper_tracker[topic].add(p['arxiv_id'])
                categorized[topic].append(p)

    # Build output - keys are the actual topic names
    output_data = dict(categorized)
    output_data['date_range'] = date_range

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"Categorization complete:")
    for topic, topic_papers in categorized.items():
        print(f"  {topic}: {len(topic_papers)} papers")
    print(f"Results saved to: {output_file}")

    return output_data


if __name__ == '__main__':
    categorize_papers()
