"""Ask Claude to write test cases, then save them as JSON.

Usage:  python generate_dataset.py --n 6 --out datasets/aws_tasks.json
"""
import argparse
import json
from pathlib import Path

from claude_helpers import chat, extract_json

FORMATS = ("python", "json", "regex")


def build_prompt(n, topic):
    return f"""Generate {n} test cases for evaluating a prompt that helps users write {topic}-related code in one of three formats: python (a single short function), json (a single configuration object) or regex (a single regular expression).

Spread the formats evenly. Keep every task small and self-contained.

Each test case is an object with exactly these keys:
- "task": a short description of what the user wants
- "format": one of "python", "json" or "regex"
- "criteria": a list of 2 short statements describing what a correct answer must do

Return only a JSON array of {n} objects, with no other text."""


def is_valid_case(case):
    return (
        isinstance(case, dict)
        and isinstance(case.get("task"), str)
        and case.get("format") in FORMATS
        and isinstance(case.get("criteria"), list)
        and all(isinstance(c, str) for c in case["criteria"])
    )


def generate_dataset(n=6, topic="AWS", out="datasets/aws_tasks.json"):
    cases = [c for c in extract_json(chat(build_prompt(n, topic), max_tokens=3000)) if is_valid_case(c)]
    if not cases:
        raise ValueError("Claude returned no usable test cases. Run the script again.")
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    return cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=6, help="how many test cases")
    parser.add_argument("--topic", default="AWS", help="what the code is about")
    parser.add_argument("--out", default="datasets/aws_tasks.json", help="where to save the file")
    args = parser.parse_args()
    saved = generate_dataset(args.n, args.topic, args.out)
    print(f"Saved {len(saved)} test cases to {args.out}")
