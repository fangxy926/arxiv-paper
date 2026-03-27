#!/usr/bin/env python3
"""
Categorize medical AI papers based on topics field from search_arxiv_medical.py
Reads relative_papers.json and outputs categorized_papers.json
"""
import json
import os
from datetime import datetime
from utils import load_json, save_json


def categorize_papers(input_file: str = 'relative_papers.json', output_file: str = 'papers_data.json') -> dict:
    """
    Categorize papers based on their topics field.
    Output structured data for client-side rendering.

    Args:
        input_file: Path to input JSON file (default: relative_papers.json)
        output_file: Path to output JSON file (default: papers_data.json)

    Returns:
        Dictionary with categorized papers and date range
    """
    input_data = load_json(input_file, {})

    papers = input_data.get('papers', [])
    date_range = input_data.get('date_range', {})

    # Dynamic categories based on actual topics
    papers_by_topic = {}
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
            if topic not in papers_by_topic:
                papers_by_topic[topic] = []
                paper_tracker[topic] = set()
            if p['arxiv_id'] not in paper_tracker[topic]:
                paper_tracker[topic].add(p['arxiv_id'])
                papers_by_topic[topic].append(p)

    # Build output with new structure for client-side rendering
    topics = list(papers_by_topic.keys())
    output_data = {
        'date_range': date_range,
        'topics': topics,
        'papers_by_topic': papers_by_topic,
        'total_count': len(papers),
        'generated_at': datetime.now().isoformat()
    }

    # Save results
    save_json(output_file, output_data)

    # Save metadata for index page (if in output dir mode)
    output_dir = os.getenv('OUTPUT_DIR', '.')
    if output_dir != '.' and os.path.exists(output_dir):
        metadata = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'paper_count': len(papers),
            'topics': topics,
            'date_range': date_range
        }
        metadata_file = os.path.join(output_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Metadata saved to: {metadata_file}")

    # Print summary
    print(f"Categorization complete:")
    for topic, topic_papers in papers_by_topic.items():
        print(f"  {topic}: {len(topic_papers)} papers")
    print(f"Results saved to: {output_file}")

    return output_data


if __name__ == '__main__':
    output_dir = os.getenv('OUTPUT_DIR', '.')
    os.makedirs(output_dir, exist_ok=True)
    input_file = os.path.join(output_dir, 'relative_papers.json')
    output_file = os.path.join(output_dir, 'papers_data.json')
    categorize_papers(input_file, output_file)
