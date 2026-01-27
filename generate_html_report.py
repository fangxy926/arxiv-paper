#!/usr/bin/env python3
"""
Generate HTML report from categorized papers
"""
import json
from datetime import datetime

def card_color(category):
    colors = {
        'llm': '#667eea',
        'agent': '#11998e',
        'dataset': '#fc4a1a'
    }
    return colors.get(category, '#667eea')

def format_authors(authors):
    """Format authors list"""
    if not authors:
        return '<span class="author-tag">Unknown</span>'
    author_list = []
    for author in authors[:5]:  # Max 5 authors
        if isinstance(author, dict):
            name = author.get('name', 'Unknown')
        else:
            name = str(author)
        author_list.append(name)
    if len(authors) > 5:
        author_list.append(f'... +{len(authors)-5} more')
    return ''.join([f'<span class="author-tag">{a}</span>' for a in author_list])

def format_keywords(keywords):
    """Format keywords list"""
    if not keywords:
        return ''
    # Handle both list and comma-separated string
    if isinstance(keywords, str):
        keyword_list = [kw.strip() for kw in keywords.split(',')]
    else:
        keyword_list = keywords
    return ''.join([f'<span class="keyword-tag">{kw}</span>' for kw in keyword_list])

with open('categorized_papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

llm_papers = data.get('llm_papers', [])
agent_papers = data.get('agent_papers', [])
dataset_papers = data.get('dataset_papers', [])

total_papers = len(llm_papers) + len(agent_papers) + len(dataset_papers)

html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv 医疗领域 AI 学术进展报告 (2025.12-2026.01)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            --orange-gradient: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
            --blue-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --purple-gradient: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
            --red-gradient: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            --green-gradient: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1800px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }

        header p {
            color: #a0aec0;
            font-size: 1.2em;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 40px;
            flex-wrap: wrap;
        }

        .stat-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-box:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-label {
            color: #a0aec0;
            font-size: 0.9em;
            margin-top: 5px;
        }

        .filter-bar {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .filter-btn.active {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .filter-btn[data-filter="all"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .filter-btn[data-filter="llm"] {
            background: var(--primary-gradient);
            color: white;
        }

        .filter-btn[data-filter="agent"] {
            background: var(--secondary-gradient);
            color: white;
        }

        .filter-btn[data-filter="dataset"] {
            background: var(--orange-gradient);
            color: white;
        }

        .section-title {
            font-size: 1.4em;
            margin: 30px 0 15px;
            padding: 15px 20px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .section-title.llm {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            border-left: 4px solid #667eea;
        }

        .section-title.agent {
            background: linear-gradient(135deg, rgba(17, 153, 142, 0.2) 0%, rgba(56, 239, 125, 0.2) 100%);
            border-left: 4px solid #11998e;
        }

        .section-title.dataset {
            background: linear-gradient(135deg, rgba(252, 74, 26, 0.2) 0%, rgba(247, 183, 51, 0.2) 100%);
            border-left: 4px solid #fc4a1a;
        }

        .papers-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        @media (max-width: 1200px) {
            .papers-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .papers-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            height: auto;
            max-height: 900px;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .card[data-category="llm"] {
            border-top: 3px solid #667eea;
        }

        .card[data-category="agent"] {
            border-top: 3px solid #11998e;
        }

        .card[data-category="dataset"] {
            border-top: 3px solid #fc4a1a;
        }

        .card-header {
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
        }

        .card[data-category="llm"] .card-header {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        }

        .card[data-category="agent"] .card-header {
            background: linear-gradient(135deg, rgba(17, 153, 142, 0.1) 0%, rgba(56, 239, 125, 0.1) 100%);
        }

        .card[data-category="dataset"] .card-header {
            background: linear-gradient(135deg, rgba(252, 74, 26, 0.1) 0%, rgba(247, 183, 51, 0.1) 100%);
        }

        .card-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #fff;
            line-height: 1.4;
        }

        .card-badge {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75em;
            color: #a0aec0;
            white-space: nowrap;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            padding: 10px 15px;
            background: rgba(0, 0, 0, 0.15);
            font-size: 0.8em;
        }

        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #a0aec0;
        }

        .meta-icon {
            width: 16px;
            height: 16px;
            opacity: 0.7;
        }

        .card-body {
            padding: 15px;
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .abstract {
            color: #cbd5e0;
            font-size: 0.85em;
            line-height: 1.6;
            background: rgba(255, 255, 255, 0.03);
            padding: 10px;
            border-radius: 8px;
            margin-top: 8px;
            border-left: 3px solid #4facfe;
            flex: 1;
            overflow-y: auto;
        }

        .abstract.original {
            border-left-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }

        .abstract-label {
            display: block;
            font-size: 0.75em;
            color: #4facfe;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .abstract.original .abstract-label {
            color: #667eea;
        }

        /* Scrollbar styling */
        .abstract::-webkit-scrollbar {
            width: 6px;
        }

        .abstract::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 3px;
        }

        .abstract::-webkit-scrollbar-thumb {
            background: rgba(102, 126, 234, 0.5);
            border-radius: 3px;
        }

        .abstract::-webkit-scrollbar-thumb:hover {
            background: rgba(102, 126, 234, 0.7);
        }

        .summary {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            border-left: 3px solid #667eea;
            padding: 12px;
            margin-top: 10px;
            border-radius: 0 8px 8px 0;
        }

        .summary-label {
            display: block;
            font-size: 0.8em;
            color: #a3bffa;
            margin-bottom: 6px;
            font-weight: 600;
        }

        .summary-text {
            color: #e2e8f0;
            font-size: 0.9em;
            line-height: 1.6;
        }

        .keywords-section {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .keywords-section label {
            font-size: 0.75em;
            color: #718096;
            display: block;
            margin-bottom: 6px;
        }

        .keyword-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .keyword-tag {
            background: rgba(102, 126, 234, 0.2);
            color: #a3bffa;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75em;
        }

        .authors-section {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .authors-section label {
            font-size: 0.75em;
            color: #718096;
            display: block;
            margin-bottom: 6px;
        }

        .author-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .author-tag {
            background: rgba(255, 255, 255, 0.08);
            color: #e2e8f0;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75em;
        }

        .card-footer {
            padding: 10px 15px;
            background: rgba(0, 0, 0, 0.15);
            display: flex;
            gap: 8px;
            margin-top: auto;
        }

        .btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 8px;
            font-size: 0.85em;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #a0aec0;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        footer {
            text-align: center;
            padding: 40px;
            color: #718096;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }

            .stats {
                gap: 15px;
            }

            .stat-box {
                padding: 15px 25px;
            }

            .filter-bar {
                gap: 10px;
            }

            .filter-btn {
                padding: 10px 20px;
                font-size: 0.9em;
            }
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>arXiv 医疗领域 AI 学术进展报告</h1>
            <p class="subtitle">Large Language Models, Agents, and Datasets (2025.12 - 2026.01)</p>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">''' + str(total_papers) + '''</div>
                    <div class="stat-label">论文总数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">''' + str(len(llm_papers)) + '''</div>
                    <div class="stat-label">大语言模型</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">''' + str(len(agent_papers)) + '''</div>
                    <div class="stat-label">智能体系统</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">''' + str(len(dataset_papers)) + '''</div>
                    <div class="stat-label">数据集/基准</div>
                </div>
            </div>
        </header>

        <div class="filter-bar">
            <button class="filter-btn active" data-filter="all">全部论文</button>
            <button class="filter-btn" data-filter="llm">大语言模型</button>
            <button class="filter-btn" data-filter="agent">智能体系统</button>
            <button class="filter-btn" data-filter="dataset">数据集/基准</button>
        </div>
'''

def generate_card(paper, category):
    arxiv_id = paper.get('arxiv_id', '')
    title = paper.get('title', 'No title')
    published = paper.get('published', 'Unknown')
    category_tag = paper.get('category', 'cs.AI')
    abstract = paper.get('abstract', 'No abstract available')
    abstract_cn = paper.get('abstract_cn', '')
    authors = paper.get('authors', [])
    keywords = paper.get('llm_keywords', '')
    pdf_url = paper.get('pdf_url', f'https://arxiv.org/pdf/{arxiv_id}')

    # Use LLM-generated summary if available, otherwise generate fallback
    summary = paper.get('llm_summary', '')

    # Build abstract section with translation
    abstract_html = ''
    if abstract_cn:
        abstract_html = f'''<p class="abstract"><span class="abstract-label">📄 中文摘要</span>{abstract_cn}</p>'''
    if abstract:
        abstract_html += f'''<p class="abstract original"><span class="abstract-label">📄 原文摘要</span>{abstract}</p>'''

    return f'''
        <div class="card" data-category="{category}">
            <div class="card-header">
                <span class="card-title">{title}</span>
                <span class="card-badge">{category_tag}</span>
            </div>
            <div class="meta-grid">
                <div class="meta-item">
                    <span>📅 {published}</span>
                </div>
                <div class="meta-item">
                    <span>🆔 {arxiv_id}</span>
                </div>
            </div>
            <div class="card-body">
                <div class="summary">
                    <div class="summary-label">📋 研究总结</div>
                    <div class="summary-text">{summary}</div>
                </div>
                {abstract_html}
                <div class="authors-section">
                    <label>作者</label>
                    <div class="author-list">
                        {format_authors(authors)}
                    </div>
                </div>
                <div class="keywords-section">
                    <label>关键词</label>
                    <div class="keyword-list">
                        {format_keywords(keywords)}
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <a href="{pdf_url}" target="_blank" class="btn btn-primary">📄 PDF</a>
                <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank" class="btn btn-secondary">📖 arXiv</a>
            </div>
        </div>
'''

# Add LLM section
html_content += '''
        <h2 class="section-title llm">🤖 医疗大语言模型 (LLM) - ''' + str(len(llm_papers)) + '''篇</h2>
        <div class="papers-grid">
'''
for paper in llm_papers:
    html_content += generate_card(paper, 'llm')

# Add Agent section
html_content += '''
        </div>
        <h2 class="section-title agent">🛡️ 医疗智能体 (Agent) - ''' + str(len(agent_papers)) + '''篇</h2>
        <div class="papers-grid">
'''
for paper in agent_papers:
    html_content += generate_card(paper, 'agent')

# Add Dataset section
html_content += '''
        </div>
        <h2 class="section-title dataset">📁 医疗数据集与基准 (Dataset) - ''' + str(len(dataset_papers)) + '''篇</h2>
        <div class="papers-grid">
'''
for paper in dataset_papers:
    html_content += generate_card(paper, 'dataset')

html_content += '''
        </div>

        <footer>
            <p>Generated on ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            <p>Data source: arXiv (2025.12 - 2026.01)</p>
        </footer>
    </div>

    <script>
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const filter = btn.dataset.filter;
                document.querySelectorAll('.card').forEach(card => {
                    if (filter === 'all' || card.dataset.category === filter) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            });
        });
    </script>
</body>
</html>
'''

with open('medical_ai_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'HTML report generated: medical_ai_report.html')
print(f'Total papers: {total_papers}')
print(f'  - LLM: {len(llm_papers)}')
print(f'  - Agent: {len(agent_papers)}')
print(f'  - Dataset: {len(dataset_papers)}')
