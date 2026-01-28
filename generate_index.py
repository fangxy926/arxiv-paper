#!/usr/bin/env python3
"""
Generate index page for browsing historical reports
Creates a landing page with links to all dated reports
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def scan_reports(docs_dir='docs'):
    """Scan docs directory for all dated reports"""
    reports = []
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        return reports

    # Scan year/month/day directory structure
    for year_dir in sorted(docs_path.iterdir(), reverse=True):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        year = year_dir.name

        for month_dir in sorted(year_dir.iterdir(), reverse=True):
            if not month_dir.is_dir() or not month_dir.name.isdigit():
                continue
            month = month_dir.name

            for day_dir in sorted(month_dir.iterdir(), reverse=True):
                if not day_dir.is_dir() or not day_dir.name.isdigit():
                    continue
                day = day_dir.name

                report_file = day_dir / 'index.html'
                if report_file.exists():
                    date_str = f"{year}-{month}-{day}"
                    date_obj = datetime(int(year), int(month), int(day))

                    # Try to load metadata from categorized_papers.json if exists
                    metadata = {}
                    metadata_file = day_dir / 'metadata.json'
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except:
                            pass

                    reports.append({
                        'date': date_str,
                        'date_obj': date_obj,
                        'path': f'{year}/{month}/{day}/',
                        'year': year,
                        'month': month,
                        'day': day,
                        'paper_count': metadata.get('paper_count', 0),
                        'topics': metadata.get('topics', [])
                    })

    return sorted(reports, key=lambda x: x['date_obj'], reverse=True)

def generate_index(reports, docs_dir='docs'):
    """Generate index HTML page"""

    # Group reports by year
    reports_by_year = {}
    for report in reports:
        year = report['year']
        if year not in reports_by_year:
            reports_by_year[year] = []
        reports_by_year[year].append(report)

    # Generate report cards HTML
    reports_html = ''
    for year in sorted(reports_by_year.keys(), reverse=True):
        reports_html += f'<div class="year-section">\n'
        reports_html += f'  <h2 class="year-title">{year}年</h2>\n'
        reports_html += f'  <div class="reports-grid">\n'

        for report in reports_by_year[year]:
            date_display = report['date_obj'].strftime('%m月%d日')
            weekday = report['date_obj'].strftime('%A')
            weekday_cn = {'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
                         'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'}.get(weekday, weekday)

            paper_count = report['paper_count']
            count_badge = f'<span class="paper-count">{paper_count} 篇论文</span>' if paper_count else ''

            reports_html += f'''    <a href="{report['path']}" class="report-card">
      <div class="report-date">
        <span class="date-day">{report['day']}</span>
        <span class="date-month">{int(report['month'])}月</span>
      </div>
      <div class="report-info">
        <div class="report-title">{date_display} {weekday_cn}周报</div>
        <div class="report-meta">
          {count_badge}
          <span class="date-range">{report['date']} 至 {(report['date_obj'] + timedelta(days=6)).strftime('%Y-%m-%d')}</span>
        </div>
      </div>
      <div class="report-arrow">→</div>
    </a>
'''

        reports_html += '  </div>\n</div>\n'

    # Generate latest report preview
    latest_report = reports[0] if reports else None
    latest_html = ''
    if latest_report:
        latest_html = f'''
        <div class="latest-report">
            <div class="latest-badge">最新报告</div>
            <h3>{latest_report['date_obj'].strftime('%Y年%m月%d日')}周报</h3>
            <p>包含 {latest_report['paper_count']} 篇精选论文</p>
            <a href="{latest_report['path']}" class="btn-primary">查看最新报告 →</a>
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv 学术进展周报 - 历史存档</title>
    <style>
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
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
            background: var(--bg-primary);
            background-image:
                radial-gradient(ellipse at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 90% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        header {{
            text-align: center;
            padding: 60px 20px;
            margin-bottom: 40px;
        }}

        header h1 {{
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #22d3ee 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}

        header p {{
            color: var(--text-secondary);
            font-size: 1.2em;
        }}

        .latest-report {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
        }}

        .latest-report::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-cyan));
        }}

        .latest-badge {{
            display: inline-block;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-bottom: 20px;
        }}

        .latest-report h3 {{
            font-size: 1.8em;
            margin-bottom: 10px;
        }}

        .latest-report p {{
            color: var(--text-secondary);
            margin-bottom: 25px;
        }}

        .btn-primary {{
            display: inline-block;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            padding: 14px 32px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }}

        .year-section {{
            margin-bottom: 40px;
        }}

        .year-title {{
            font-size: 1.5em;
            color: var(--text-secondary);
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid var(--accent-primary);
        }}

        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}

        .report-card {{
            display: flex;
            align-items: center;
            gap: 15px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.3s;
        }}

        .report-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .report-date {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 10px;
            padding: 10px 15px;
            min-width: 60px;
        }}

        .date-day {{
            font-size: 1.5em;
            font-weight: 700;
        }}

        .date-month {{
            font-size: 0.8em;
            opacity: 0.9;
        }}

        .report-info {{
            flex: 1;
        }}

        .report-title {{
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .report-meta {{
            display: flex;
            gap: 10px;
            font-size: 0.85em;
            color: var(--text-muted);
        }}

        .paper-count {{
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            padding: 2px 8px;
            border-radius: 10px;
        }}

        .report-arrow {{
            font-size: 1.5em;
            color: var(--text-muted);
            transition: transform 0.3s;
        }}

        .report-card:hover .report-arrow {{
            transform: translateX(5px);
            color: var(--accent-primary);
        }}

        footer {{
            text-align: center;
            padding: 40px;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            margin-top: 40px;
        }}

        .empty-state {{
            text-align: center;
            padding: 80px 20px;
            color: var(--text-muted);
        }}

        .empty-state h2 {{
            color: var(--text-secondary);
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>arXiv 学术进展周报</h1>
            <p>每周自动整理医疗AI领域最新研究进展</p>
        </header>

        {latest_html if latest_report else '<div class="empty-state"><h2>暂无报告</h2><p>报告将在每周一自动生成</p></div>'}

        {reports_html if reports else ''}

        <footer>
            <p>自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据来源：arXiv.org</p>
        </footer>
    </div>
</body>
</html>
'''

    return html

def main():
    print("Generating index page for historical reports...")

    reports = scan_reports('docs')
    print(f"Found {len(reports)} historical reports")

    html = generate_index(reports, 'docs')

    # Ensure docs directory exists
    os.makedirs('docs', exist_ok=True)

    # Write index.html
    index_path = os.path.join('docs', 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Index page generated: {index_path}")

if __name__ == '__main__':
    main()
