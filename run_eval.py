"""Run one or more prompts against a dataset, grade every answer and compare the results.

Usage:  python run_eval.py --dataset datasets/aws_tasks.json --prompts v1 v2
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from claude_helpers import chat
from config import MAX_WORKERS
from graders import grade_case
from prompts import PROMPTS
from report import write_report


def run_one(prompt_name, case):
    """Run the prompt on one test case and grade the answer. A failure scores 0 instead of crashing."""
    try:
        prompt = PROMPTS[prompt_name].replace("{task}", case["task"]).replace("{format}", case["format"])
        output = chat(prompt)
        return {"case": case, "output": output, **grade_case(case, output)}
    except Exception as e:  # keep going, and record why this case failed
        return {
            "case": case, "output": "", "final_score": 0, "model_score": 0,
            "syntax_score": 0, "syntax_detail": "", "strengths": [], "weaknesses": [],
            "reasoning": f"This case failed to run: {e}",
        }


def evaluate(prompt_name, cases):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(lambda c: run_one(prompt_name, c), cases))
    return results


def average(results, key):
    return sum(r[key] for r in results) / len(results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="datasets/aws_tasks.json")
    parser.add_argument("--prompts", nargs="+", default=["v1", "v2"], choices=sorted(PROMPTS))
    args = parser.parse_args()

    cases = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    print(f"Running {len(cases)} test cases for prompts: {', '.join(args.prompts)}\n")

    summary = []
    for name in args.prompts:
        results = evaluate(name, cases)
        report_path = f"reports/report_{name}.html"
        write_report(name, results, report_path)
        summary.append((name, average(results, "final_score"), average(results, "model_score"),
                        average(results, "syntax_score")))
        failed = [r for r in results if r["reasoning"].startswith("This case failed")]
        if failed:
            print(f"  {name}: {len(failed)} case(s) failed to run, first error: {failed[0]['reasoning']}")

    print(f"{'prompt':<8}{'final':>8}{'model':>8}{'syntax':>8}")
    for name, final, model, syntax in summary:
        print(f"{name:<8}{final:>8.1f}{model:>8.1f}{syntax:>8.1f}")
    print("\nHTML reports are in the reports folder.")


if __name__ == "__main__":
    main()
