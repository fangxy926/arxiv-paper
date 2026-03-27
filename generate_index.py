#!/usr/bin/env python3
"""
Generate index page for browsing historical reports
Academic professional design
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from utils import load_json

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
                        metadata = load_json(metadata_file, {})

                    # Get date range from metadata
                    date_range = metadata.get('date_range', {})

                    # Use full directory name (including suffix) for path
                    full_dir_name = day_dir.name

                    reports.append({
                        'date': date_str,
                        'date_obj': date_obj,
                        'path': f'report.html?date={date_str}',  # Use shared template with date parameter
                        'data_path': f'{year}/{month}/{full_dir_name}/papers_data.json',  # Keep data path for reference
                        'year': year,
                        'month': month,
                        'day': day,
                        'paper_count': metadata.get('paper_count', 0),
                        'topics': metadata.get('topics', []),
                        'date_range': date_range
                    })

    return sorted(reports, key=lambda x: x['date_obj'], reverse=True)

def build_calendar_data(reports):
    """
    将报告列表转换为按年月分组的字典
    返回: {year: {month: {day: {'count': int, 'path': str, 'is_latest': bool}}}}
    """
    calendar_data = {}
    if not reports:
        return calendar_data

    # 找到最新报告
    latest_report = reports[0]  # reports 已按日期倒序排列

    for report in reports:
        year = report['year']
        month = report['month']
        day = report['day']

        if year not in calendar_data:
            calendar_data[year] = {}
        if month not in calendar_data[year]:
            calendar_data[year][month] = {}

        is_latest = report['date'] == latest_report['date']

        calendar_data[year][month][day] = {
            'count': report['paper_count'],
            'path': report['path'],
            'is_latest': is_latest
        }

    return calendar_data

def generate_calendar_html(calendar_data, year, month, prev_month_url=None, next_month_url=None):
    """
    生成指定年月的日历HTML

    Args:
        calendar_data: {year: {month: {day: {'count': int, 'path': str, 'is_latest': bool}}}}
        year: 年份 (int or str)
        month: 月份 (int or str)
        prev_month_url: 上一个月链接 (可选)
        next_month_url: 下一个月链接 (可选)

    Returns:
        str: 日历HTML字符串
    """
    year_str = str(year)
    month_str = str(month).zfill(2)
    month_int = int(month)
    year_int = int(year)

    # 计算月份第一天是星期几 (0=周日)
    first_day = datetime(year_int, month_int, 1)
    first_weekday = first_day.weekday()  # Monday=0, Sunday=6
    # 转换为 0=周日 格式
    first_weekday = (first_weekday + 1) % 7

    # 计算月份总天数
    if month_int == 12:
        next_month = datetime(year_int + 1, 1, 1)
    else:
        next_month = datetime(year_int, month_int + 1, 1)
    days_in_month = (next_month - first_day).days

    # 月份名称
    month_names = ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    month_name = month_names[month_int - 1]

    # 获取当前月份的数据
    month_data = calendar_data.get(year_str, {}).get(month_str, {})

    # 生成星期标题
    weekdays = ['日', '一', '二', '三', '四', '五', '六']
    weekdays_html = ''.join([f'<div class="calendar-weekday">{wd}</div>' for wd in weekdays])

    # 生成前导空白格子
    days_html = ''
    for _ in range(first_weekday):
        days_html += '<div class="calendar-day empty"></div>'

    # 遍历每一天
    for day in range(1, days_in_month + 1):
        day_str = str(day).zfill(2)

        if day_str in month_data and month_data[day_str]['count'] > 0:
            # 有报告的日期（count > 0）
            day_data = month_data[day_str]
            count = day_data['count']
            path = day_data['path']
            is_latest = day_data.get('is_latest', False)

            if is_latest:
                # 最新报告日期
                day_class = 'calendar-day has-report latest'
                badge_html = '<span class="day-latest-badge">最新</span>'
            else:
                day_class = 'calendar-day has-report'
                badge_html = ''

            days_html += f'''<a href="{path}" class="{day_class}">
                <span class="day-number">{day}</span>
                <span class="day-count">{count} 篇</span>
                {badge_html}
            </a>'''
        else:
            # 无报告日期（包括 count == 0 或不在 month_data 中）
            days_html += f'''<div class="calendar-day no-report">
                <span class="day-number">{day}</span>
                <span class="day-count">无报告</span>
            </div>'''

    # 导航按钮
    prev_btn = f'<a href="{prev_month_url}" class="calendar-nav-btn">←</a>' if prev_month_url else '<span class="calendar-nav-btn disabled">←</span>'
    next_btn = f'<a href="{next_month_url}" class="calendar-nav-btn">→</a>' if next_month_url else '<span class="calendar-nav-btn disabled">→</span>'

    # 图例
    legend_html = '''
    <div class="calendar-legend">
        <div class="legend-item">
            <span class="legend-color latest"></span>
            <span>最新报告</span>
        </div>
        <div class="legend-item">
            <span class="legend-color has-report"></span>
            <span>有报告</span>
        </div>
        <div class="legend-item">
            <span class="legend-color no-report"></span>
            <span>无报告</span>
        </div>
    </div>
    '''

    # 组装完整HTML
    html = f'''<div class="calendar-container">
    <div class="calendar-header">
        {prev_btn}
        <span class="calendar-title">{year_int}年 {month_name}</span>
        {next_btn}
    </div>
    <div class="calendar-grid">
        <div class="calendar-weekdays">
            {weekdays_html}
        </div>
        <div class="calendar-days">
            {days_html}
        </div>
    </div>
    {legend_html}
</div>'''

    return html

def generate_index(reports, docs_dir='docs', current_year=None, current_month=None):
    """Generate index HTML page with calendar view"""

    # Build calendar data
    calendar_data = build_calendar_data(reports)

    # Determine which month to display (default to latest report's month or current month)
    if reports:
        latest_report = reports[0]
        default_year = int(latest_report['year'])
        default_month = int(latest_report['month'])
    else:
        now = datetime.now()
        default_year = now.year
        default_month = now.month

    # Use provided values or defaults
    display_year = current_year if current_year is not None else default_year
    display_month = current_month if current_month is not None else default_month

    # Calculate previous/next month URLs
    def get_month_url(year, month, offset):
        """Get URL for month offset (prev/next)"""
        from datetime import timedelta
        target_date = datetime(year, month, 15) + timedelta(days=offset * 30)
        # Adjust to first day of target month
        target_year = target_date.year
        target_month = target_date.month
        return f"?year={target_year}&month={target_month}"

    # Check if we have reports for prev/next month
    prev_month_url = get_month_url(display_year, display_month, -1) if calendar_data else None
    next_month_url = get_month_url(display_year, display_month, 1) if calendar_data else None

    # Generate calendar HTML
    calendar_html = generate_calendar_html(
        calendar_data, display_year, display_month,
        prev_month_url=prev_month_url,
        next_month_url=next_month_url
    )

    # Generate latest report preview (keep this logic)
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

        /* Calendar Container */
        .calendar-container {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}

        /* Calendar Header */
        .calendar-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--color-border-light);
        }}

        .calendar-title {{
            font-family: var(--font-serif);
            font-size: 24px;
            font-weight: 700;
            color: var(--color-text);
        }}

        .calendar-nav-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border: 1px solid var(--color-border);
            border-radius: 8px;
            background: var(--color-surface);
            color: var(--color-text);
            font-size: 18px;
            text-decoration: none;
            transition: all 0.15s;
            cursor: pointer;
        }}

        .calendar-nav-btn:hover {{
            background: var(--color-bg);
            border-color: var(--color-text-muted);
        }}

        .calendar-nav-btn.disabled {{
            opacity: 0.4;
            cursor: not-allowed;
            pointer-events: none;
        }}

        /* Calendar Grid */
        .calendar-grid {{
            display: flex;
            flex-direction: column;
        }}

        /* Weekdays Row */
        .calendar-weekdays {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-bottom: 8px;
        }}

        .calendar-weekday {{
            text-align: center;
            font-size: 13px;
            font-weight: 600;
            color: var(--color-text-muted);
            padding: 8px;
        }}

        /* Days Grid */
        .calendar-days {{
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }}

        .calendar-day {{
            aspect-ratio: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            border: 1px solid var(--color-border);
            background: var(--color-surface);
            text-decoration: none;
            color: inherit;
            transition: all 0.15s;
            min-height: 80px;
        }}

        .calendar-day.empty {{
            border: none;
            background: transparent;
            pointer-events: none;
        }}

        .calendar-day.no-report {{
            background: linear-gradient(145deg, #f8fafc, #e2e8f0);
            border-color: #cbd5e1;
            color: #94a3b8;
            cursor: default;
        }}

        .calendar-day.no-report .day-count {{
            font-size: 11px;
            opacity: 0.7;
        }}

        .calendar-day.has-report {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-color: transparent;
            color: white;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25);
        }}

        .calendar-day.has-report:hover {{
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35);
        }}

        .calendar-day.latest {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.35);
            position: relative;
            overflow: hidden;
        }}

        .calendar-day.latest::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, transparent 50%);
            pointer-events: none;
        }}

        .calendar-day.latest:hover {{
            background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.45);
        }}

        .day-number {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .day-count {{
            font-size: 12px;
            opacity: 0.9;
        }}

        .day-latest-badge {{
            font-size: 10px;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 4px;
        }}

        /* Calendar Legend */
        .calendar-legend {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid var(--color-border-light);
            justify-content: center;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--color-text-secondary);
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid var(--color-border);
        }}

        .legend-color.latest {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            border-color: transparent;
        }}

        .legend-color.has-report {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-color: transparent;
        }}

        .legend-color.no-report {{
            background: linear-gradient(145deg, #f8fafc, #e2e8f0);
            border-color: #cbd5e1;
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
        @media (max-width: 768px) {{
            .header-content {{ padding: 24px 20px 20px; }}
            .header-title {{ font-size: 24px; }}
            .main {{ padding: 16px 16px 32px; }}
            .latest-report {{ padding: 20px; }}
            .calendar-container {{ padding: 16px; }}
            .calendar-title {{ font-size: 20px; }}
            .calendar-day {{ min-height: 60px; }}
            .day-number {{ font-size: 14px; }}
            .day-count {{ font-size: 10px; }}
            .calendar-legend {{ flex-direction: column; gap: 10px; align-items: center; }}
        }}

        @media (max-width: 480px) {{
            .calendar-day {{ min-height: 50px; }}
            .day-number {{ font-size: 12px; }}
            .day-count {{ display: none; }}
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

        {'<h2 style="font-family: var(--font-serif); font-size: 20px; font-weight: 700; margin-bottom: 16px;">历史归档</h2>' if reports else ''}
        {calendar_html}
    </main>

    <footer class="footer">
        <p class="footer-text">生成于 {datetime.now().strftime('%Y-%m-%d')} · 数据来源：arXiv.org</p>
    </footer>
</body>
</html>
'''

    return html

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate index page for historical reports')
    parser.add_argument('--year', type=int, help='Specify year (YYYY)')
    parser.add_argument('--month', type=int, help='Specify month (MM)')

    args = parser.parse_args()

    print("Generating index page for historical reports...")

    reports = scan_reports('docs')
    print(f"Found {len(reports)} historical reports")

    html = generate_index(
        reports,
        'docs',
        current_year=args.year,
        current_month=args.month
    )

    # Ensure docs directory exists
    os.makedirs('docs', exist_ok=True)

    # Write index.html
    index_path = os.path.join('docs', 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Index page generated: {index_path}")
    if args.year and args.month:
        print(f"Calendar view: {args.year}年{args.month}月")

if __name__ == '__main__':
    main()
