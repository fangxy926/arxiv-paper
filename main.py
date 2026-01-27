#!/usr/bin/env python3
"""
Main script to generate medical AI research report
Run: python main.py
"""
import subprocess
import sys

def run_step(name, script):
    print(f"\n{'='*50}")
    print(f"Step: {name}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"Error in {name}")
        return False
    return True

def main():
    print("Medical AI Research Report Generator")
    print("=" * 50)

    # Step 1: Search arXiv for medical papers
    if not run_step("Search arXiv for medical papers", "search_arxiv_medical.py"):
        return

    # Step 2: Extract keywords and Chinese summary using LLM
    if not run_step("Extract paper insights with LLM", "extract_paper_insights.py"):
        return

    # Step 3: Categorize papers
    if not run_step("Categorize papers", "categorize_papers.py"):
        return

    # Step 4: Generate HTML report
    if not run_step("Generate HTML report", "generate_html_report.py"):
        return

    print("\n" + "=" * 50)
    print("All steps completed successfully!")
    print("Output: medical_ai_report.html")
    print("=" * 50)

if __name__ == "__main__":
    main()
