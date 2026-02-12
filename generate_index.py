#!/usr/bin/env python3
"""
Generate index page for browsing historical reports
Academic professional design
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
                if not day_dir.is_dir():
                    continue
                # Handle day directories with optional suffix (e.g., "28", "28-1", "28-2")
                day_name = day_dir.name
                day_base = day_name.split('-')[0]  # Get base day number
                if not day_base.isdigit():
                    continue
                day = day_base

                report_file = day_dir / 'index.html'
                if report_file.exists():
                    date_str = f"{year}-{month}-{day}"
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                    except ValueError:
                        continue

                    # Try to load metadata from categorized_papers.json if exists
                    metadata = {}
                    metadata_file = day_dir / 'metadata.json'
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except:
                            pass

                    # Get date range from metadata
                    date_range = metadata.get('date_range', {})

                    # Use full directory name (including suffix) for path
                    full_dir_name = day_dir.name

                    reports.append({
                        'date': date_str,
                        'date_obj': date_obj,
                        'path': f'{year}/{month}/{full_dir_name}/index.html',
                        'year': year,
                        'month': month,
                        'day': day,
                        'paper_count': metadata.get('paper_count', 0),
                        'topics': metadata.get('topics', []),
                        'date_range': date_range
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
        reports_html += f'  <div class="year-header">\n'
        reports_html += f'    <span class="year-label">{year}</span>\n'
        reports_html += f'    <span class="year-count">{len(reports_by_year[year])} 期</span>\n'
        reports_html += f'  </div>\n'
        reports_html += f'  <div class="reports-list">\n'

        for report in reports_by_year[year]:
            date_display = report['date_obj'].strftime('%b %d')
            weekday = report['date_obj'].strftime('%A')
            weekday_cn = {'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
                         'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'}.get(weekday, weekday)

            paper_count = report['paper_count']
            count_badge = f'<span class="count-badge">{paper_count} 篇论文</span>' if paper_count else ''

            # Get actual date range from metadata
            date_range = report.get('date_range', {})
            if date_range.get('start_date') and date_range.get('end_date'):
                date_range_text = f"{date_range['start_date']} — {date_range['end_date']}"
            else:
                date_range_text = f"{report['date']} — {(report['date_obj'] + timedelta(days=6)).strftime('%Y-%m-%d')}"

            reports_html += f'''    <a href="{report['path']}" class="report-item">
      <div class="report-date">
        <span class="date-day">{report['day']}</span>
        <span class="date-month">{report['date_obj'].strftime('%b')}</span>
      </div>
      <div class="report-info">
        <div class="report-title">{date_display} · {weekday_cn}</div>
        <div class="report-range">{date_range_text}</div>
      </div>
      <div class="report-meta">
        {count_badge}
        <span class="arrow">→</span>
      </div>
    </a>
'''

        reports_html += '  </div>\n</div>\n'

    # Generate latest report preview
    latest_report = reports[0] if reports else None
    latest_html = ''
    if latest_report:
        date_range_text = ''
        if latest_report.get('date_range', {}).get('start_date'):
            dr = latest_report['date_range']
            date_range_text = f"{dr['start_date']} — {dr['end_date']}"

        latest_html = f'''
        <div class="latest-report">
            <div class="latest-header">
                <span class="latest-badge">最新</span>
                <span class="latest-date">{latest_report['date_obj'].strftime('%Y年%m月%d日')}</span>
            </div>
            <h2 class="latest-title">学术进展周报</h2>
            <p class="latest-desc">{latest_report['paper_count']} 篇精选论文 · {date_range_text}</p>
            <a href="{latest_report['path']}" class="btn-primary">查看报告 →</a>
        </div>
        '''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医疗AI学术进展 | arXiv 周报归档</title>
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
        }}

        .header-content {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 32px 24px 24px;
            text-align: center;
        }}

        .header-logo {{
            width: 48px;
            height: 48px;
            background: var(--color-accent);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 700;
            margin: 0 auto 16px;
        }}

        .header-title {{
            font-family: var(--font-serif);
            font-size: 30px;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
        }}

        .header-subtitle {{
            font-size: 16px;
            color: var(--color-text-muted);
        }}

        /* Main */
        .main {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px 24px 40px;
        }}

        /* Latest Report */
        .latest-report {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 32px;
            position: relative;
        }}

        .latest-report::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--color-accent);
            border-radius: 8px 8px 0 0;
        }}

        .latest-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .latest-badge {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-accent);
            background: var(--color-accent-light);
            padding: 4px 10px;
            border-radius: 4px;
        }}

        .latest-date {{
            font-size: 13px;
            color: var(--color-text-muted);
        }}

        .latest-title {{
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .latest-desc {{
            font-size: 16px;
            color: var(--color-text-secondary);
            margin-bottom: 24px;
        }}

        .btn-primary {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--color-accent);
            color: white;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            border-radius: 6px;
            transition: background 0.15s;
        }}

        .btn-primary:hover {{
            background: #1e3a8a;
        }}

        /* Archive */
        .archive-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--color-border);
        }}

        .archive-title {{
            font-family: var(--font-serif);
            font-size: 20px;
            font-weight: 700;
        }}

        .archive-count {{
            font-size: 13px;
            color: var(--color-text-muted);
        }}

        /* Year Section */
        .year-section {{
            margin-bottom: 24px;
        }}

        .year-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}

        .year-label {{
            font-family: var(--font-serif);
            font-size: 18px;
            font-weight: 700;
        }}

        .year-count {{
            font-size: 12px;
            color: var(--color-text-muted);
            font-weight: 500;
        }}

        /* Reports List */
        .reports-list {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .report-item {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 6px;
            padding: 16px 20px;
            text-decoration: none;
            color: inherit;
            transition: all 0.15s;
        }}

        .report-item:hover {{
            border-color: #d1d5db;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}

        .report-date {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 56px;
            padding: 8px;
            background: var(--color-bg);
            border-radius: 4px;
            border: 1px solid var(--color-border-light);
        }}

        .date-day {{
            font-family: var(--font-serif);
            font-size: 20px;
            font-weight: 700;
            color: var(--color-text);
            line-height: 1;
        }}

        .date-month {{
            font-size: 11px;
            font-weight: 600;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 2px;
        }}

        .report-info {{
            flex: 1;
        }}

        .report-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--color-text);
            margin-bottom: 4px;
        }}

        .report-range {{
            font-size: 12px;
            color: var(--color-text-muted);
        }}

        .report-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .count-badge {{
            font-size: 12px;
            font-weight: 500;
            color: var(--color-accent);
            background: var(--color-accent-light);
            padding: 4px 10px;
            border-radius: 12px;
        }}

        .arrow {{
            font-size: 18px;
            color: var(--color-text-muted);
            transition: transform 0.15s;
        }}

        .report-item:hover .arrow {{
            transform: translateX(4px);
            color: var(--color-accent);
        }}

        /* Footer */
        .footer {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px 24px;
            border-top: 1px solid var(--color-border);
            text-align: center;
        }}

        .footer-text {{
            font-size: 12px;
            color: var(--color-text-muted);
        }}

        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 80px 40px;
            color: var(--color-text-muted);
        }}

        .empty-state h2 {{
            font-family: var(--font-serif);
            font-size: 20px;
            color: var(--color-text-secondary);
            margin-bottom: 8px;
        }}

        /* Responsive */
        @media (max-width: 640px) {{
            .header-content {{ padding: 32px 20px; }}
            .header-title {{ font-size: 28px; }}
            .main {{ padding: 24px 20px; }}
            .latest-report {{ padding: 24px; }}
            .report-item {{ padding: 14px 16px; }}
            .report-date {{ min-width: 48px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="header-logo">arXiv</div>
            <h1 class="header-title">医疗AI学术进展归档</h1>
            <p class="header-subtitle">自动整理医疗人工智能领域最新研究进展</p>
        </div>
    </header>

    <main class="main">
        {latest_html if latest_report else '<div class="empty-state"><h2>暂无报告</h2><p>报告将自动生成</p></div>'}

        {'<div class="archive-header"><h2 class="archive-title">历史归档</h2><span class="archive-count">共 ' + str(len(reports)) + ' 期</span></div>' if reports else ''}
        {reports_html if reports else ''}
    </main>

    <footer class="footer">
        <p class="footer-text">生成于 {datetime.now().strftime('%Y-%m-%d')} · 数据来源：arXiv.org</p>
    </footer>
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
