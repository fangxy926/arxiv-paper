#!/usr/bin/env python3
"""
Main script to generate medical AI research report
Run: python main.py

Supports GitHub Pages deployment with dated directories:
- Reports are saved to docs/YYYY/MM/DD/index.html
- Index page is updated at docs/index.html
"""
import subprocess
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_step(name, script, env_vars=None):
    print(f"\n{'='*50}")
    print(f"Step: {name}")
    print(f"{'='*50}")
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    result = subprocess.run([sys.executable, script], capture_output=False, env=env)
    if result.returncode != 0:
        print(f"Error in {name}")
        return False
    return True

def main():
    print("Medical AI Research Report Generator")
    print("=" * 50)

    # Check if running in GitHub Actions (deploy mode)
    is_deploy = os.getenv('DEPLOY_MODE', 'false').lower() == 'true'

    # Allow ARXIV_DAYS_BACK to be overridden by env variable, default to 7
    days_back = int(os.getenv('ARXIV_DAYS_BACK', '7'))

    # Calculate date range based on days_back
    today = datetime.now()
    # Get the most recent days_back days (including today)
    start_date = today - timedelta(days=days_back - 1)
    end_date = today

    # Use today's date for directory structure (report generation date)
    year = today.strftime('%Y')
    month = today.strftime('%m')
    day = today.strftime('%d')

    # Set output directory (always use dated directory under docs/)
    output_dir = os.path.join('docs', year, month, day)
    os.makedirs(output_dir, exist_ok=True)

    # Set date range for arXiv search
    os.environ['FORCE_DATE_START'] = start_date.strftime('%Y-%m-%d')
    os.environ['FORCE_DATE_END'] = end_date.strftime('%Y-%m-%d')

    print(f"Generating report for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({days_back} days)")
    print(f"Output directory: {output_dir}")

    # Pass OUTPUT_DIR to all steps
    env = {'OUTPUT_DIR': output_dir}

    # Step 1: Search arXiv for medical papers
    if not run_step("Search arXiv for medical papers", "search_arxiv_medical.py", env):
        return

    # Step 2: Extract keywords and Chinese summary using LLM
    if not run_step("Extract paper insights with LLM", "extract_paper_insights.py", env):
        return

    # Step 3: Categorize papers
    if not run_step("Categorize papers", "categorize_papers.py", env):
        return

    # Step 4: Generate HTML report
    if not run_step("Generate HTML report", "generate_html_report.py", env):
        return

    # Step 5: Clean up temporary JSON files
    print(f"\n{'='*50}")
    print("Step: Cleanup temporary files")
    print(f"{'='*50}")
    json_files = ['relative_papers.json', 'categorized_papers.json']
    for json_file in json_files:
        file_path = os.path.join(output_dir, json_file)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed: {file_path}")
    print("Cleanup complete")

    # Step 6: Generate index page (deploy mode only)
    if is_deploy:
        if not run_step("Generate index page", "generate_index.py"):
            return

    print("\n" + "=" * 50)
    print("All steps completed successfully!")
    print(f"Output: {output_dir}/index.html")
    if is_deploy:
        print("Index: docs/index.html")
    print("=" * 50)

if __name__ == "__main__":
    main()
