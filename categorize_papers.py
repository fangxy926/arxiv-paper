#!/usr/bin/env python3
"""
Categorize medical AI papers into LLM, Agent, and Dataset categories
"""
import json

with open('relative_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

# Classify papers
llm_papers = []
agent_papers = []
dataset_papers = []

for p in papers:
    title = p['title'].lower()
    abstract = p['abstract'].lower()
    combined = title + ' ' + abstract

    is_llm = any(kw in combined for kw in [
        'language model', 'llm', 'gpt', 'foundation model',
        'embedding model', 'vlm', 'vision language', 'multimodal'
    ])

    is_agent = any(kw in combined for kw in [
        'agent', 'tool-enhanced', 'conversational agent',
        'guardrail', 'autonom', 'multi-hop'
    ])

    is_dataset = any(kw in combined for kw in [
        'dataset', 'benchmark', 'corpus', 'data collection'
    ])

    if is_agent and 'agent' in combined:
        agent_papers.append(p)
    elif is_dataset and ('dataset' in p['title'].lower() or 'benchmark' in p['title'].lower()):
        dataset_papers.append(p)
    elif is_llm:
        llm_papers.append(p)
    elif is_agent:
        agent_papers.append(p)
    elif is_dataset:
        dataset_papers.append(p)

print(f'LLM: {len(llm_papers)}, Agent: {len(agent_papers)}, Dataset: {len(dataset_papers)}')

# Save categorized results
with open('categorized_papers.json', 'w', encoding='utf-8') as f:
    json.dump({
        'llm_papers': llm_papers,
        'agent_papers': agent_papers,
        'dataset_papers': dataset_papers
    }, f, ensure_ascii=False, indent=2)

print("Categorized papers saved to categorized_papers.json")
