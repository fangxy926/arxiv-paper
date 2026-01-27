#!/usr/bin/env python3
"""
Categorize papers based on LLM-assigned topics
Simplified version - just reads topics from papers and organizes them
"""
import json
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read topics from environment variable
TOPICS_RAW = os.getenv('TOPICS', '')
TOPICS = [t.strip() for t in TOPICS_RAW.split(',') if t.strip()]

with open('relative_papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

papers = data.get('papers', [])
date_range = data.get('date_range', {})

# Organize papers by topic
categorized = {topic: [] for topic in TOPICS}

for paper in papers:
    paper_topics = paper.get('topics', [])
    if not paper_topics:
        # Fallback: if no topics assigned, try to infer from keywords
        title_summary = (paper.get('title', '') + ' ' + paper.get('summary', '')).lower()
        for topic in TOPICS:
            if topic.lower() in title_summary:
                paper_topics.append(topic)

    # Assign paper to all matching topics
    for topic in paper_topics:
        # Normalize topic name (handle slight variations)
        for t in TOPICS:
            if t in topic or topic in t:
                if paper not in categorized[t]:
                    categorized[t].append(paper)
                break

# Save categorized papers
output_data = {
    **categorized,
    'date_range': date_range,
    'all_topics': TOPICS
}

with open('categorized_papers.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"=== Papers Categorized by Topic ===")
for topic, topic_papers in categorized.items():
    print(f"  {topic}: {len(topic_papers)} papers")
print(f"\nTotal: {sum(len(p) for p in categorized.values())} paper-topic pairs")
print(f"Output saved to: categorized_papers.json")
