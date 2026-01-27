#!/usr/bin/env python3
"""
Generate HTML report from categorized papers
Dynamically generates columns based on TOPIC from environment
"""
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read topics from environment variable
TOPICS_RAW = os.getenv('TOPICS', '')
TOPICS = [t.strip() for t in TOPICS_RAW.split(',') if t.strip()]

# Default colors for topics
DEFAULT_COLORS = ['#667eea', '#11998e', '#fc4a1a', '#4facfe', '#a18cd1', '#ff6b6b', '#ee5a24', '#0ba360']

def get_topic_config(topic):
    """Generate config for a topic based on its name - fully dynamic"""
    import hashlib

    # Generate consistent values from topic name
    hash_val = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16)

    # Select color based on hash
    color_idx = hash_val % len(DEFAULT_COLORS)
    color = DEFAULT_COLORS[color_idx]

    # Select icon from a diverse set based on hash
    ICONS = ['🤖', '📊', '🛡️', '📈', '🔬', '💊', '🧬', '🧪', '🏥', '🔍', '📱', '💻', '🎯', '📋', '📑']
    icon_idx = hash_val % len(ICONS)
    icon = ICONS[icon_idx]

    return {
        'icon': icon,
        'color': color,
        'gradient': f'linear-gradient(135deg, {color} 0%, {DEFAULT_COLORS[(color_idx+1)%len(DEFAULT_COLORS)]} 100%)',
        'label': topic  # 使用主题名称作为显示标签
    }

def format_authors(authors):
    """Format authors list"""
    if not authors:
        return '<span class="author-tag">Unknown</span>'
    author_list = []
    for author in authors[:5]:
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
    if isinstance(keywords, str):
        keyword_list = [kw.strip() for kw in keywords.split(',')]
    else:
        keyword_list = keywords
    return ''.join([f'<span class="keyword-tag">{kw}</span>' for kw in keyword_list[:10]])

# Read categorized papers
with open('categorized_papers.json', 'r', encoding='utf-8') as f:
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
    date_range_text = f"检索时间范围: {date_range['start_date']} 至 {date_range['end_date']}"

# Generate filter buttons HTML
filter_buttons_html = '<button class="filter-btn active" data-filter="all">全部论文</button>\n'
for topic in TOPICS:
    config = get_topic_config(topic)
    filter_buttons_html += f'            <button class="filter-btn" data-filter="{topic}">{config["icon"]} {config["label"]}</button>\n'

# Generate stats HTML
stats_html = f'''
                <div class="stat-box">
                    <div class="stat-number">{total_papers}</div>
                    <div class="stat-label">论文总数</div>
                </div>
'''
for topic in TOPICS:
    config = get_topic_config(topic)
    count = len(topic_papers[topic])
    stats_html += f'''
                <div class="stat-box">
                    <div class="stat-number">{count}</div>
                    <div class="stat-label">{config["label"]}</div>
                </div>
'''

# Generate CSS for topics
topic_css = ''
topic_style = ''
for i, topic in enumerate(TOPICS):
    config = get_topic_config(topic)
    topic_lower = topic.replace(' ', '_').lower()
    topic_css += f'''
        .filter-btn[data-filter="{topic}"] {{
            background: {config["gradient"]};
            color: white;
        }}

        .section-title.{topic_lower} {{
            background: linear-gradient(135deg, {config["color"]}22 0%, {config["color"]}44 100%);
            border-left: 4px solid {config["color"]};
        }}

        .card[data-category="{topic}"] {{
            border-top: 3px solid {config["color"]};
        }}

        .card[data-category="{topic}"] .card-header {{
            background: linear-gradient(135deg, {config["color"]}1a 0%, {config["color"]}33 100%);
        }}
'''

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv 学术进展报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.6);
            --border-color: rgba(148, 163, 184, 0.15);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.3);
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
            background: var(--bg-primary);
            background-image:
                radial-gradient(ellipse at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 90% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(6, 182, 212, 0.05) 0%, transparent 70%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        /* Header Styles */
        header {{
            text-align: center;
            padding: 50px 30px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-radius: 24px;
            margin-bottom: 35px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }}

        header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-cyan));
        }}

        header h1 {{
            font-size: 2.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #22d3ee 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            letter-spacing: -0.02em;
        }}

        header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1em;
            margin-bottom: 15px;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 12px;
        }}

        header .subtitle span {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}

        header .date-range {{
            color: var(--text-muted);
            font-size: 0.9em;
            padding: 10px 20px;
            background: rgba(148, 163, 184, 0.1);
            border-radius: 20px;
            display: inline-block;
            border: 1px solid var(--border-color);
        }}

        /* Stats Styles */
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 35px;
            flex-wrap: wrap;
        }}

        .stat-box {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 25px 35px;
            border: 1px solid var(--border-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            min-width: 120px;
            position: relative;
            overflow: hidden;
        }}

        .stat-box::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .stat-box:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-glow);
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .stat-box:hover::after {{
            opacity: 1;
        }}

        .stat-number {{
            font-size: 2.8em;
            font-weight: 700;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 8px;
            font-weight: 500;
        }}

        /* Filter Bar */
        .filter-bar {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 35px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 12px 24px;
            border: 1px solid var(--border-color);
            border-radius: 25px;
            font-size: 0.95em;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
            background: var(--bg-card);
            color: var(--text-secondary);
            backdrop-filter: blur(10px);
        }}

        .filter-btn:hover {{
            border-color: rgba(99, 102, 241, 0.4);
            color: var(--text-primary);
            transform: translateY(-2px);
        }}

        .filter-btn.active {{
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }}

{topic_css}
        /* Section Title */
        .section-title {{
            font-size: 1.3em;
            margin: 30px 0 20px;
            padding: 14px 22px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            font-weight: 600;
        }}

        /* Papers Grid */
        .papers-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            margin-bottom: 35px;
            align-items: start;
        }}

        @media (max-width: 1100px) {{
            .papers-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Card Styles */
        .card {{
            background: var(--bg-card);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
        }}

        .card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(99, 102, 241, 0.25);
        }}

        .card-header {{
            padding: 18px 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-title {{
            font-size: 1.15em;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.5;
            flex: 1;
        }}

        .card-badge {{
            background: rgba(99, 102, 241, 0.15);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            color: #818cf8;
            white-space: nowrap;
            font-weight: 500;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }}

        .meta-grid {{
            display: flex;
            gap: 20px;
            padding: 12px 20px;
            background: rgba(15, 23, 42, 0.5);
            font-size: 0.85em;
            border-bottom: 1px solid var(--border-color);
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            color: var(--text-muted);
        }}

        .card-body {{
            padding: 18px 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        /* Summary Section */
        .summary {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
            border-left: 3px solid var(--accent-primary);
            padding: 14px 16px;
            border-radius: 0 10px 10px 0;
        }}

        .summary-label {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8em;
            color: #818cf8;
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .summary-text {{
            color: var(--text-primary);
            font-size: 0.95em;
            line-height: 1.7;
        }}

        /* Abstract Collapsible */
        .abstract-section {{
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            background: rgba(15, 23, 42, 0.4);
        }}

        .abstract-toggle {{
            width: 100%;
            padding: 12px 16px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.9em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s;
        }}

        .abstract-toggle:hover {{
            background: rgba(99, 102, 241, 0.05);
            color: var(--text-primary);
        }}

        .abstract-toggle .toggle-icon {{
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .abstract-toggle.expanded .toggle-icon {{
            transform: rotate(180deg);
        }}

        .abstract-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .abstract-content.expanded {{
            max-height: 2000px;
        }}

        .abstract-inner {{
            padding: 0 16px 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .abstract-item {{
            color: var(--text-secondary);
            font-size: 0.88em;
            line-height: 1.7;
            padding: 12px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 8px;
            border-left: 2px solid var(--accent-cyan);
        }}

        .abstract-item.original {{
            border-left-color: var(--accent-emerald);
        }}

        .abstract-label {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75em;
            color: var(--accent-cyan);
            margin-bottom: 6px;
            font-weight: 600;
        }}

        .abstract-item.original .abstract-label {{
            color: var(--accent-emerald);
        }}

        /* Authors & Keywords */
        .info-section {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .info-block {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .info-block label {{
            font-size: 0.75em;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .tag-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .author-tag {{
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-secondary);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8em;
            border: 1px solid var(--border-color);
            transition: all 0.2s;
        }}

        .author-tag:hover {{
            background: rgba(148, 163, 184, 0.2);
            color: var(--text-primary);
        }}

        .keyword-tag {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
            color: #a5b4fc;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            border: 1px solid rgba(99, 102, 241, 0.25);
            transition: all 0.2s;
        }}

        .keyword-tag:hover {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.25));
            transform: translateY(-1px);
        }}

        /* Card Footer */
        .card-footer {{
            padding: 14px 20px;
            background: rgba(15, 23, 42, 0.5);
            display: flex;
            gap: 10px;
            border-top: 1px solid var(--border-color);
        }}

        .btn {{
            flex: 1;
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-size: 0.9em;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }}

        .btn-secondary {{
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}

        .btn-secondary:hover {{
            background: rgba(148, 163, 184, 0.2);
            color: var(--text-primary);
            border-color: rgba(148, 163, 184, 0.3);
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            font-size: 0.9em;
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }}

        footer p {{
            margin: 6px 0;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2em;
            }}

            .stats {{
                gap: 12px;
            }}

            .stat-box {{
                padding: 18px 25px;
                min-width: 100px;
            }}

            .stat-number {{
                font-size: 2.2em;
            }}

            .filter-bar {{
                gap: 8px;
            }}

            .filter-btn {{
                padding: 10px 18px;
                font-size: 0.9em;
            }}

            .card-title {{
                font-size: 1em;
            }}
        }}

        .hidden {{
            display: none !important;
        }}

        /* Smooth scroll */
        html {{
            scroll-behavior: smooth;
        }}

        /* Selection */
        ::selection {{
            background: rgba(99, 102, 241, 0.3);
            color: var(--text-primary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>arXiv 学术进展报告</h1>
            <p class="subtitle">{''.join([f'<span>{get_topic_config(t)["icon"]} {get_topic_config(t)["label"]}</span>' for t in TOPICS])}</p>
            <p class="date-range">{date_range_text}</p>
            <div class="stats">
{stats_html}
            </div>
        </header>

        <div class="filter-bar">
{filter_buttons_html}
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
    summary = paper.get('llm_summary', '')

    # Build abstract section with collapsible content
    abstract_html = ''
    has_abstract = bool(abstract_cn or abstract)

    if has_abstract:
        abstract_items = ''
        if abstract_cn:
            abstract_items += f'''<div class="abstract-item"><span class="abstract-label">📄 中文摘要</span>{abstract_cn}</div>'''
        if abstract:
            abstract_items += f'''<div class="abstract-item original"><span class="abstract-label">📄 原文摘要</span>{abstract}</div>'''

        abstract_html = f'''
            <div class="abstract-section">
                <button class="abstract-toggle" onclick="toggleAbstract(this)">
                    <span>📄 查看摘要详情</span>
                    <span class="toggle-icon">▼</span>
                </button>
                <div class="abstract-content">
                    <div class="abstract-inner">
                        {abstract_items}
                    </div>
                </div>
            </div>
        '''

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
                <div class="info-section">
                    <div class="info-block">
                        <label>作者</label>
                        <div class="tag-list">
                            {format_authors(authors)}
                        </div>
                    </div>
                    <div class="info-block">
                        <label>关键词</label>
                        <div class="tag-list">
                            {format_keywords(keywords)}
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <a href="{pdf_url}" target="_blank" class="btn btn-primary">📄 PDF</a>
                <a href="https://arxiv.org/abs/{arxiv_id}" target="_blank" class="btn btn-secondary">📖 arXiv</a>
            </div>
        </div>
'''

# Generate sections for each topic
for topic in TOPICS:
    config = get_topic_config(topic)
    topic_lower = topic.replace(' ', '_').lower()
    papers = topic_papers.get(topic, [])
    html_content += f'''
        <h2 class="section-title {topic_lower}">{config['icon']} {config['label']} - {len(papers)}篇</h2>
        <div class="papers-grid">
'''
    for paper in papers:
        html_content += generate_card(paper, topic)
    html_content += '''
        </div>
'''

# Generate filter JavaScript with abstract toggle
filter_js = '''
        // Filter functionality
        const topicFilters = ['all', ''' + ', '.join([f"'{t}'" for t in TOPICS]) + '''];

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

        // Abstract toggle functionality
        function toggleAbstract(btn) {
            const content = btn.nextElementSibling;
            const isExpanded = content.classList.contains('expanded');

            if (isExpanded) {
                content.classList.remove('expanded');
                btn.classList.remove('expanded');
                btn.querySelector('span:first-child').textContent = '📄 查看摘要详情';
            } else {
                content.classList.add('expanded');
                btn.classList.add('expanded');
                btn.querySelector('span:first-child').textContent = '📄 收起摘要详情';
            }
        }
'''

html_content += f'''
        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Data source: arXiv {date_range.get('start_date', '') + ' - ' + date_range.get('end_date', '') if date_range else 'recent papers'}</p>
        </footer>
    </div>

    <script>
{filter_js}
    </script>
</body>
</html>
'''

with open('medical_ai_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'HTML report generated: medical_ai_report.html')
print(f'Total paper-topic pairs: {total_papers}')
for topic in TOPICS:
    print(f"  - {topic}: {len(topic_papers[topic])} papers")
