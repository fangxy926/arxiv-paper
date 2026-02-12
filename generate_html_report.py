#!/usr/bin/env python3
"""
Generate HTML report from categorized papers
Academic professional design inspired by arXiv, Nature, and PubMed
"""
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get output directory from command line argument or environment
OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getenv('OUTPUT_DIR', '.')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read topics from environment variable
TOPICS_RAW = os.getenv('TOPICS', '')
TOPICS = [t.strip() for t in TOPICS_RAW.split(',') if t.strip()]

# Academic color palette - muted, professional
TOPIC_COLORS = {
    '医疗大模型': '#1e40af',
    '医疗数据集': '#047857',
    '医疗智能体': '#7c3aed',
    '医学影像AI': '#0369a1',
    '临床决策支持': '#be123c',
}

def get_topic_color(topic):
    """Get color for topic - use predefined or generate consistent color"""
    import hashlib
    if topic in TOPIC_COLORS:
        return TOPIC_COLORS[topic]
    # Generate consistent color from topic name
    hash_val = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16)
    colors = ['#1e40af', '#047857', '#7c3aed', '#0369a1', '#be123c', '#b45309', '#4338ca']
    return colors[hash_val % len(colors)]

def format_authors(authors):
    """Format authors list in academic style"""
    if not authors:
        return '<span class="author">未知作者</span>'
    author_list = []
    for author in authors[:6]:
        if isinstance(author, dict):
            name = author.get('name', '未知作者')
        else:
            name = str(author)
        # 格式化为 "Lastname FM" 学术格式
        parts = name.split()
        if len(parts) > 1:
            formatted = parts[-1] + ' ' + ''.join(p[0] for p in parts[:-1])
        else:
            formatted = name
        author_list.append(f'<span class="author">{formatted}</span>')
    if len(authors) > 6:
        author_list.append(f'<span class="author">等</span>')
    return ', '.join(author_list)

def format_keywords(keywords):
    """Format keywords list"""
    if not keywords:
        return ''
    if isinstance(keywords, str):
        keyword_list = [kw.strip() for kw in keywords.split(',')]
    else:
        keyword_list = keywords
    return ''.join([f'<span class="keyword">{kw}</span>' for kw in keyword_list[:8]])

# Read categorized papers from OUTPUT_DIR
data_file = os.path.join(OUTPUT_DIR, 'categorized_papers.json')
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get papers for each topic
topic_papers = {}
for topic in TOPICS:
    topic_papers[topic] = data.get(topic, [])

date_range = data.get('date_range', {})

# Calculate totals
total_papers = sum(len(p) for p in topic_papers.values())

# Format date range display
date_range_text = ""
if date_range.get('start_date') and date_range.get('end_date'):
    date_range_text = f"{date_range['start_date']} — {date_range['end_date']}"

# Generate stats HTML
stats_html = ''
for topic in TOPICS:
    color = get_topic_color(topic)
    count = len(topic_papers[topic])
    stats_html += f'''
                <div class="stat-item" data-filter="{topic}">
                    <span class="stat-dot" style="background: {color};"></span>
                    <span class="stat-name">{topic}</span>
                    <span class="stat-count">{count}</span>
                </div>
'''

# Generate topic-specific CSS
topic_css = ''
for topic in TOPICS:
    color = get_topic_color(topic)
    topic_lower = topic.replace(' ', '_').lower()
    topic_css += f'''
        .section-header.{topic_lower} {{ border-left-color: {color}; }}
        .section-header.{topic_lower} .section-icon {{ color: {color}; }}
        .paper-card[data-category="{topic}"] {{ border-left-color: {color}; }}
        .paper-card[data-category="{topic}"] .paper-category {{ color: {color}; }}
        .stat-item[data-filter="{topic}"].active .stat-dot {{ box-shadow: 0 0 0 3px {color}30; }}
'''

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医疗AI学术进展 | {date_range.get('start_date', '')}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --color-bg: #fafafa;
            --color-surface: #ffffff;
            --color-border: #e5e7eb;
            --color-border-light: #f3f4f6;
            --color-text: #111827;
            --color-text-secondary: #4b5563;
            --color-text-muted: #6b7280;
            --color-accent: #1e40af;
            --color-accent-light: #dbeafe;
            --font-serif: 'Crimson Pro', Georgia, 'Times New Roman', serif;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: var(--font-sans);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            font-size: 17px;
        }}

        /* Header */
        .header {{
            background: var(--color-surface);
            border-bottom: 1px solid var(--color-border);
            padding: 0;
        }}

        .header-top {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
        }}

        .header-brand {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .header-logo {{
            width: 48px;
            height: 48px;
            background: var(--color-accent);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 700;
        }}

        .header-title-group {{}}

        .header-title {{
            font-family: var(--font-serif);
            font-size: 26px;
            font-weight: 700;
            color: var(--color-text);
            letter-spacing: -0.02em;
        }}

        .header-subtitle {{
            font-size: 14px;
            color: var(--color-text-muted);
            margin-top: 4px;
        }}

        .header-meta {{
            text-align: right;
        }}

        .header-date {{
            font-size: 14px;
            font-weight: 600;
            color: var(--color-text-secondary);
            font-family: var(--font-serif);
            font-style: italic;
        }}

        .header-range {{
            font-size: 13px;
            color: var(--color-text-muted);
            margin-top: 4px;
        }}

        .header-total {{
            font-size: 32px;
            font-weight: 700;
            color: var(--color-accent);
            margin-top: 8px;
        }}

        .header-total-label {{
            font-size: 12px;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* Navigation Bar */
        .nav-bar {{
            background: var(--color-surface);
            border-bottom: 1px solid var(--color-border);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            gap: 4px;
            overflow-x: auto;
        }}

        .nav-item {{
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 500;
            color: var(--color-text-secondary);
            cursor: pointer;
            border: none;
            background: none;
            border-bottom: 2px solid transparent;
            white-space: nowrap;
            transition: all 0.15s;
        }}

        .nav-item:hover {{
            color: var(--color-text);
            background: var(--color-border-light);
        }}

        .nav-item.active {{
            color: var(--color-accent);
            border-bottom-color: var(--color-accent);
            font-weight: 600;
        }}

        /* Main Content */
        .main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 24px 40px;
        }}

        /* Stats Panel */
        .stats-panel {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 20px;
        }}

        .stats-title {{
            font-size: 12px;
            font-weight: 600;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }}

        .stats-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px 24px;
        }}

        .stat-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.15s;
        }}

        .stat-item:hover {{
            background: var(--color-border-light);
        }}

        .stat-item.active {{
            background: var(--color-accent-light);
        }}

        .stat-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        .stat-name {{
            font-size: 13px;
            color: var(--color-text-secondary);
        }}

        .stat-item.active .stat-name {{
            color: var(--color-accent);
            font-weight: 600;
        }}

        .stat-count {{
            font-size: 13px;
            font-weight: 600;
            color: var(--color-text);
            background: var(--color-border-light);
            padding: 2px 8px;
            border-radius: 12px;
            min-width: 24px;
            text-align: center;
        }}

        .stat-item.active .stat-count {{
            background: var(--color-accent);
            color: white;
        }}

        /* Section */
        .section {{
            margin-bottom: 24px;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-left-width: 4px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 12px;
        }}

        .section-icon {{
            font-size: 18px;
        }}

        .section-title {{
            font-family: var(--font-serif);
            font-size: 18px;
            font-weight: 700;
        }}

        .section-count {{
            margin-left: auto;
            font-size: 13px;
            color: var(--color-text-muted);
            font-weight: 500;
        }}

        /* Papers Grid */
        .papers-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}

        @media (max-width: 1100px) {{
            .papers-grid {{ grid-template-columns: 1fr; }}
        }}

        /* Paper Card */
        .paper-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-left-width: 3px;
            border-radius: 0 6px 6px 0;
            overflow: hidden;
            transition: box-shadow 0.15s, border-color 0.15s;
        }}

        .paper-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-color: #d1d5db;
        }}

        .paper-header {{
            padding: 14px 16px 10px;
            border-bottom: 1px solid var(--color-border-light);
        }}

        .paper-category {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}

        .paper-title {{
            font-family: var(--font-serif);
            font-size: 17px;
            font-weight: 600;
            line-height: 1.4;
            color: var(--color-text);
        }}

        .paper-title a {{
            color: inherit;
            text-decoration: none;
        }}

        .paper-title a:hover {{
            color: var(--color-accent);
            text-decoration: underline;
        }}

        .paper-meta {{
            display: flex;
            gap: 12px;
            padding: 8px 16px;
            font-size: 12px;
            color: var(--color-text-muted);
            border-bottom: 1px solid var(--color-border-light);
            background: #fafafa;
        }}

        .paper-meta-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .paper-body {{
            padding: 12px 16px;
        }}

        .paper-summary {{
            font-size: 16px;
            line-height: 1.7;
            color: var(--color-text-secondary);
            margin-bottom: 12px;
        }}

        .paper-summary::before {{
            content: '';
            display: inline-block;
            width: 3px;
            height: 14px;
            background: var(--color-accent);
            margin-right: 8px;
            vertical-align: middle;
        }}

        /* Abstract */
        .abstract-section {{
            margin-top: 12px;
        }}

        .abstract-toggle {{
            width: 100%;
            padding: 8px 0;
            background: none;
            border: none;
            font-size: 12px;
            font-weight: 500;
            color: var(--color-accent);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: color 0.15s;
        }}

        .abstract-toggle:hover {{
            color: #1e3a8a;
        }}

        .abstract-toggle-icon {{
            transition: transform 0.2s;
        }}

        .abstract-toggle.expanded .abstract-toggle-icon {{
            transform: rotate(180deg);
        }}

        .abstract-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}

        .abstract-content.expanded {{
            max-height: 2000px;
        }}

        .abstract-inner {{
            padding: 12px 0 4px;
            border-top: 1px dashed var(--color-border);
            margin-top: 8px;
        }}

        .abstract-block {{
            margin-bottom: 12px;
        }}

        .abstract-label {{
            font-size: 11px;
            font-weight: 600;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 6px;
        }}

        .abstract-text {{
            font-size: 15px;
            line-height: 1.7;
            color: var(--color-text-secondary);
        }}

        /* Authors & Keywords */
        .paper-footer {{
            padding: 10px 16px;
            background: #fafafa;
            border-top: 1px solid var(--color-border-light);
        }}

        .paper-authors {{
            font-size: 14px;
            color: var(--color-text-secondary);
            margin-bottom: 10px;
            line-height: 1.5;
        }}

        .author {{
            font-weight: 500;
        }}

        .paper-keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .keyword {{
            font-size: 11px;
            color: var(--color-accent);
            background: var(--color-accent-light);
            padding: 3px 10px;
            border-radius: 3px;
            font-weight: 500;
        }}

        /* Paper Actions */
        .paper-actions {{
            display: flex;
            gap: 8px;
            padding: 10px 16px;
            border-top: 1px solid var(--color-border-light);
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.15s;
            cursor: pointer;
            border: none;
        }}

        .btn-primary {{
            background: var(--color-accent);
            color: white;
        }}

        .btn-primary:hover {{
            background: #1e3a8a;
        }}

        .btn-secondary {{
            background: white;
            color: var(--color-text-secondary);
            border: 1px solid var(--color-border);
        }}

        .btn-secondary:hover {{
            background: var(--color-border-light);
            color: var(--color-text);
        }}

        /* Footer */
        .footer {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 24px;
            border-top: 1px solid var(--color-border);
            text-align: center;
        }}

        .footer-text {{
            font-size: 12px;
            color: var(--color-text-muted);
        }}

        /* Hidden state */
        .hidden {{ display: none !important; }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header-top {{
                flex-direction: column;
                padding: 20px;
                gap: 20px;
            }}
            .header-meta {{ text-align: left; }}
            .nav-content {{ padding: 0 20px; }}
            .main {{ padding: 20px; }}
            .papers-grid {{ grid-template-columns: 1fr; }}
        }}

{topic_css}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-top">
            <div class="header-brand">
                <div class="header-logo">arXiv</div>
                <div class="header-title-group">
                    <h1 class="header-title">医疗AI学术进展周报</h1>
                    <p class="header-subtitle">自动文献综述与前沿追踪</p>
                </div>
            </div>
            <div class="header-meta">
                <div class="header-date">{datetime.now().strftime('%B %d, %Y')}</div>
                <div class="header-range">{date_range_text}</div>
                <div class="header-total">{total_papers}</div>
                <div class="header-total-label">论文</div>
            </div>
        </div>
    </header>

    <main class="main">
        <div class="stats-panel">
            <div class="stats-title">按研究领域筛选</div>
            <div class="stats-grid">
'''

# Add stats items
html_content += f'''                <div class="stat-item active" data-filter="all">
                    <span class="stat-dot" style="background: var(--color-accent);"></span>
                    <span class="stat-name">全部主题</span>
                    <span class="stat-count">{total_papers}</span>
                </div>
'''

for topic in TOPICS:
    color = get_topic_color(topic)
    count = len(topic_papers[topic])
    html_content += f'''                <div class="stat-item" data-filter="{topic}">
                    <span class="stat-dot" style="background: {color};"></span>
                    <span class="stat-name">{topic}</span>
                    <span class="stat-count">{count}</span>
                </div>
'''

html_content += '''            </div>
        </div>
'''

def generate_card(paper, category):
    arxiv_id = paper.get('arxiv_id', '')
    title = paper.get('title', 'No title')
    published = paper.get('published', '未知日期')
    category_tag = paper.get('category', 'cs.AI')
    abstract = paper.get('abstract', 'No abstract available')
    abstract_cn = paper.get('abstract_cn', '')
    authors = paper.get('authors', [])
    keywords = paper.get('llm_keywords', '')
    pdf_url = paper.get('pdf_url', f'https://arxiv.org/pdf/{arxiv_id}')
    summary = paper.get('llm_summary', '')

    # Build abstract section
    abstract_html = ''
    has_abstract = bool(abstract_cn or abstract)

    if has_abstract:
        abstract_items = ''
        if abstract_cn:
            abstract_items += f'''<div class="abstract-block">
                            <div class="abstract-label">中文摘要</div>
                            <div class="abstract-text">{abstract_cn}</div>
                        </div>'''
        if abstract:
            abstract_items += f'''<div class="abstract-block">
                            <div class="abstract-label">英文摘要</div>
                            <div class="abstract-text">{abstract}</div>
                        </div>'''

        abstract_html = f'''
                <div class="abstract-section">
                    <button class="abstract-toggle" onclick="toggleAbstract(this)">
                        <span>查看摘要</span>
                        <span class="abstract-toggle-icon">▼</span>
                    </button>
                    <div class="abstract-content">
                        <div class="abstract-inner">
                            {abstract_items}
                        </div>
                    </div>
                </div>
        '''

    return f'''
        <article class="paper-card" data-category="{category}">
            <div class="paper-header">
                <div class="paper-category">{category} · {category_tag}</div>
                <h3 class="paper-title"><a href="https://arxiv.org/abs/{arxiv_id}" target="_blank">{title}</a></h3>
            </div>
            <div class="paper-meta">
                <span class="paper-meta-item">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    {published}
                </span>
                <span class="paper-meta-item">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                    arXiv:{arxiv_id}
                </span>
            </div>
            <div class="paper-body">
                <p class="paper-summary">{summary}</p>
                {abstract_html}
            </div>
            <div class="paper-footer">
                <div class="paper-authors">{format_authors(authors)}</div>
                <div class="paper-keywords">{format_keywords(keywords)}</div>
            </div>
            <div class="paper-actions">
                <a href="{pdf_url}" target="_blank" class="btn btn-primary">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    PDF
                </a>
                <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank" class="btn btn-secondary">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    arXiv
                </a>
            </div>
        </article>
'''

# Generate sections for each topic
for topic in TOPICS:
    color = get_topic_color(topic)
    topic_lower = topic.replace(' ', '_').lower()
    papers = topic_papers.get(topic, [])
    html_content += f'''
        <section class="section">
            <div class="section-header {topic_lower}">
                <span class="section-icon" style="color: {color};">◆</span>
                <h2 class="section-title">{topic}</h2>
                <span class="section-count">{len(papers)} 篇论文</span>
            </div>
            <div class="papers-grid">
'''
    for paper in papers:
        html_content += generate_card(paper, topic)
    html_content += '''            </div>
        </section>
'''

# JavaScript for filtering and abstract toggle
html_content += '''    </main>

    <footer class="footer">
        <p class="footer-text">生成于 ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + ''' · 数据来源：arXiv.org</p>
    </footer>

    <script>
        // Filter functionality
        const statItems = document.querySelectorAll('.stat-item');
        const sections = document.querySelectorAll('.section');

        function filterPapers(filter) {
            // Update stat items
            statItems.forEach(item => {
                item.classList.toggle('active', item.dataset.filter === filter);
            });

            // Filter cards
            document.querySelectorAll('.paper-card').forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });

            // Show/hide sections
            sections.forEach(section => {
                const visibleCards = section.querySelectorAll('.paper-card:not(.hidden)');
                if (filter === 'all' || visibleCards.length > 0) {
                    section.classList.remove('hidden');
                } else {
                    section.classList.add('hidden');
                }
            });
        }

        statItems.forEach(item => {
            item.addEventListener('click', () => filterPapers(item.dataset.filter));
        });

        // Abstract toggle
        function toggleAbstract(btn) {
            const content = btn.nextElementSibling;
            const isExpanded = content.classList.contains('expanded');
            const textSpan = btn.querySelector('span:first-child');

            if (isExpanded) {
                content.classList.remove('expanded');
                btn.classList.remove('expanded');
                textSpan.textContent = '查看摘要';
            } else {
                content.classList.add('expanded');
                btn.classList.add('expanded');
                textSpan.textContent = '收起摘要';
            }
        }
    </script>
</body>
</html>
'''

output_path = os.path.join(OUTPUT_DIR, 'index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'HTML report generated: {output_path}')
print(f'Total paper-topic pairs: {total_papers}')
for topic in TOPICS:
    print(f"  - {topic}: {len(topic_papers[topic])} papers")
