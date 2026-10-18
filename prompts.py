"""The prompts under test. Add a new version here, then evaluate it against the old ones.

Each template can use {task} and {format}; run_eval.py fills them in.
"""

PROMPTS = {
    # Version 1: the plain baseline.
    "v1": "Please solve the following task:\n\n{task}",
    # Version 2: clear structure, a fixed output format and one example.
    "v2": """You are a careful AWS engineer. Solve the task below.

<task>
{task}
</task>

<output_format>
Answer with one fenced code block labelled {format}, followed by at most two sentences explaining the key choice.
- python: one short, complete function with a docstring
- json: one valid JSON object with no comments
- regex: only the bare regular expression, with no quotes, delimiters or surrounding code
</output_format>

<example>
Task: Write a regular expression that matches a four-digit year.
```regex
^\\d{4}$
```
It matches exactly four digits from the start to the end of the string.
</example>""",
}
