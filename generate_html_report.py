#!/usr/bin/env python3
"""
Generate shared HTML report template that loads papers_data.json dynamically.
This template is shared across all reports, with date specified via URL parameter.
Usage: report.html?date=2026-03-27
"""
import os
import sys
import hashlib
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getenv('OUTPUT_DIR', 'docs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

TOPICS_RAW = os.getenv('TOPICS', '')
TOPICS = [t.strip() for t in TOPICS_RAW.split(',') if t.strip()]

TOPIC_COLORS = {
    '医疗大模型': '#1e40af',
    '医疗数据集': '#047857',
    '医疗智能体': '#7c3aed',
    '医学影像AI': '#0369a1',
    '临床决策支持': '#be123c',
}

def get_topic_color(topic):
    if topic in TOPIC_COLORS:
        return TOPIC_COLORS[topic]
    hash_val = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16)
    colors = ['#1e40af', '#047857', '#7c3aed', '#0369a1', '#be123c', '#b45309', '#4338ca']
    return colors[hash_val % len(colors)]

# Build topic colors JS
js_colors = 'const TOPIC_COLORS = {};\n'
js_colors += ''.join(f"TOPIC_COLORS['{topic}'] = '{get_topic_color(topic)}';\n" for topic in TOPICS)

# CSS styles
css = """
:root { --bg: #fafafa; --surface: #fff; --border: #e5e7eb; --text: #111827; --muted: #6b7280; --accent: #1e40af; --accent-light: #dbeafe; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
.header { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 24px; }
.header-top { max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.header-logo { width: 48px; height: 48px; background: var(--accent); color: white; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold; font-size: 20px; }
.header-title { font-size: 24px; font-weight: 700; }
.header-subtitle { font-size: 14px; color: var(--muted); }
.header-total { font-size: 32px; font-weight: 700; color: var(--accent); }
.main { max-width: 1400px; margin: 0 auto; padding: 20px 24px; }
.loading { text-align: center; padding: 100px; }
.error { display: none; text-align: center; padding: 100px; color: #dc2626; }
.stats-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 20px; }
.stats-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-item { display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.stat-item:hover { background: #f3f4f6; }
.stat-item.active { background: var(--accent-light); }
.stat-dot { width: 10px; height: 10px; border-radius: 50%; }
.papers-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
@media (max-width: 767px) { .papers-grid { grid-template-columns: 1fr; } }
.paper-card { background: var(--surface); border: 1px solid var(--border); border-left-width: 3px; border-radius: 0 6px 6px 0; padding: 16px; }
.paper-title { font-size: 17px; font-weight: 600; margin-bottom: 8px; }
.paper-title a { color: inherit; text-decoration: none; }
.paper-title a:hover { color: var(--accent); text-decoration: underline; }
.paper-meta { font-size: 13px; color: var(--muted); margin-bottom: 8px; }
.paper-summary { font-size: 15px; color: #4b5563; margin-bottom: 12px; }
.keyword { display: inline-block; font-size: 11px; color: var(--accent); background: var(--accent-light); padding: 2px 8px; border-radius: 3px; margin-right: 4px; }
.btn { display: inline-block; padding: 6px 12px; font-size: 13px; border-radius: 4px; text-decoration: none; margin-right: 8px; }
.btn-primary { background: var(--accent); color: white; }
.btn-secondary { background: white; border: 1px solid var(--border); color: var(--text); }
.hidden { display: none !important; }
.section-header { border-left: 4px solid var(--accent); padding: 12px; margin-bottom: 12px; background: #fff; border: 1px solid var(--border); border-radius: 0 8px 8px 0; display: flex; align-items: center; gap: 10px; }
.section-title { font-weight: 700; font-size: 18px; }
.section-count { margin-left: auto; color: var(--muted); }
.back-link { display: inline-flex; align-items: center; gap: 6px; color: var(--accent); text-decoration: none; font-size: 14px; margin-bottom: 16px; }
.back-link:hover { text-decoration: underline; }
.report-date { font-size: 14px; color: var(--muted); margin-top: 4px; }
"""

# JavaScript - now with URL parameter support
js = """
let data = null, filter = 'all';

function getReportDate() {
    const params = new URLSearchParams(window.location.search);
    return params.get('date');
}

function getDataPath() {
    const date = getReportDate();
    if (!date) return './papers_data.json';
    // Date format: 2026-03-27 -> 2026/03/27/papers_data.json
    const parts = date.split('-');
    if (parts.length !== 3) return './papers_data.json';
    return parts.join('/') + '/papers_data.json';
}

async function loadData() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const content = document.getElementById('content');
    const dateDisplay = document.getElementById('report-date');

    loading.style.display = 'block';
    error.style.display = 'none';
    content.style.display = 'none';

    const reportDate = getReportDate();
    if (reportDate && dateDisplay) {
        dateDisplay.textContent = '报告日期: ' + reportDate;
    }

    try {
        const dataPath = getDataPath();
        const r = await fetch(dataPath);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        data = await r.json();
        render();
        loading.style.display = 'none';
        content.style.display = 'block';
    } catch(e) {
        console.error('Load error:', e);
        loading.style.display = 'none';
        error.style.display = 'block';
        error.textContent = '加载失败: ' + e.message;
    }
}

function formatAuthors(authors) {
    if (!authors || authors.length === 0) return '<span class="author">未知作者</span>';
    const list = authors.slice(0, 6).map(a => {
        let n = typeof a === 'object' ? a.name : String(a);
        const p = n.split(' ');
        if (p.length > 1) n = p[p.length-1] + ' ' + p.slice(0,-1).map(x=>x[0]).join('');
        return '<span class="author">' + n + '</span>';
    });
    if (authors.length > 6) list.push('<span class="author">等</span>');
    return list.join(', ');
}

function formatKeywords(kw) {
    if (!kw) return '';
    const arr = typeof kw === 'string' ? kw.split(',').map(x=>x.trim()).filter(x=>x) : kw;
    return arr.slice(0,8).map(k => '<span class="keyword">' + k + '</span>').join('');
}

function generateCard(p, topic) {
    const id = p.arxiv_id || '';
    const c = TOPIC_COLORS[topic] || '#1e40af';
    return '<article class="paper-card" data-cat="' + topic + '" style="border-left-color:' + c + '"><div class="paper-header"><div class="paper-category" style="color:' + c + '">' + topic + ' · ' + (p.category || p.primary_category || 'cs.AI') + '</div><h3 class="paper-title"><a href="https://arxiv.org/abs/' + id + '" target="_blank">' + (p.title || '无标题') + '</a></h3></div><div class="paper-meta">📅 ' + (p.published || '未知日期') + ' | 🏷️ arXiv:' + id + '</div><div class="paper-body"><p class="paper-summary">' + (p.llm_summary || '') + '</p></div><div class="paper-footer"><div class="paper-authors">' + formatAuthors(p.authors) + '</div><div class="paper-keywords">' + formatKeywords(p.llm_keywords) + '</div></div><div class="paper-actions"><a href="' + (p.pdf_url || 'https://arxiv.org/pdf/' + id) + '" class="btn btn-primary" target="_blank">📄 PDF</a><a href="https://arxiv.org/abs/' + id + '" class="btn btn-secondary" target="_blank">🔗 arXiv</a></div></article>';
}

function renderStats() {
    const el = document.getElementById('stats-grid');
    let html = "<div class='stat-item active' data-filter='all'><span class='stat-dot' style='background:var(--accent)'></span><span>全部</span><span>" + (data.total_count || 0) + "</span></div>";
    (data.topics || []).forEach(t => {
        const n = (data.papers_by_topic[t] || []).length;
        const c = TOPIC_COLORS[t] || '#1e40af';
        html += '<div class="stat-item" data-filter="' + t + '"><span class="stat-dot" style="background:' + c + '"></span><span>' + t + '</span><span>' + n + '</span></div>';
    });
    el.innerHTML = html;
    // Bind click events
    el.querySelectorAll('.stat-item').forEach(item => {
        item.addEventListener('click', function() {
            setFilter(this.dataset.filter);
        });
    });
}

function renderSections() {
    const el = document.getElementById('sections');
    let html = '';
    (data.topics || []).forEach(t => {
        const papers = data.papers_by_topic[t] || [];
        if (papers.length === 0) return;
        const c = TOPIC_COLORS[t] || '#1e40af';
        html += "<section data-topic='" + t + "'><div class='section-header' style='border-left-color:" + c + "'><span style='color:" + c + "'>◆</span><span class='section-title'>" + t + "</span><span class='section-count'>" + papers.length + " 篇论文</span></div><div>" + papers.map(p => generateCard(p, t)).join('') + "</div></section>";
    });
    el.innerHTML = html;
}

function render() {
    document.getElementById('header-total').textContent = data.total_count || 0;
    const dr = data.date_range || {};
    document.getElementById('header-range').textContent = dr.start_date ? dr.start_date + ' - ' + dr.end_date : '';
    renderStats();
    renderSections();
}

function setFilter(f) {
    filter = f;
    document.querySelectorAll('.stat-item').forEach(el => el.classList.toggle('active', el.dataset.filter === f));
    document.querySelectorAll('.paper-card').forEach(el => el.classList.toggle('hidden', f !== 'all' && el.dataset.cat !== f));
    document.querySelectorAll('section').forEach(el => {
        const visible = el.querySelectorAll('.paper-card:not(.hidden)').length;
        el.classList.toggle('hidden', f !== 'all' && visible === 0);
    });
}

loadData();
"""

# Build HTML with back link
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>医疗AI学术进展</title>
<style>{css}</style>
</head>
<body>
<header class="header">
  <div class="header-top">
    <div style="display:flex;align-items:center;gap:16px">
      <div class="header-logo">arXiv</div>
      <div>
        <div class="header-title">医疗AI学术进展周报</div>
        <div class="header-subtitle">自动文献综述与前沿追踪</div>
        <div class="report-date" id="report-date"></div>
      </div>
    </div>
    <div style="text-align:right">
      <div id="header-range" style="font-size:13px;color:var(--muted)"></div>
      <div class="header-total" id="header-total">-</div>
      <div style="font-size:12px;color:var(--muted)">论文</div>
    </div>
  </div>
</header>
<main class="main">
  <a href="index.html" class="back-link">← 返回归档页</a>
  <div class="loading" id="loading">加载中...</div>
  <div class="error" id="error"></div>
  <div id="content" style="display:none">
    <div class="stats-panel">
      <div style="font-size:12px;font-weight:600;color:var(--muted);margin-bottom:12px">按研究领域筛选</div>
      <div class="stats-grid" id="stats-grid"></div>
    </div>
    <div id="sections"></div>
  </div>
</main>
<script>
{js_colors}
{js}
</script>
</body>
</html>"""

output = os.path.join(OUTPUT_DIR, 'report.html')
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)
print('Generated:', output)
print('Usage: report.html?date=YYYY-MM-DD')
