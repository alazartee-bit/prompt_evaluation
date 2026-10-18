"""Two graders: Claude judges quality, plain code checks that the answer is valid."""
import ast
import json
import re

from claude_helpers import chat, extract_code, extract_json


# ---------- Code-based grading: no API call, always the same answer ----------

def validate_json(text):
    try:
        json.loads(text)
        return True, ""
    except ValueError as e:
        return False, f"Invalid JSON: {e}"


def validate_python(text):
    try:
        ast.parse(text)
        return True, ""
    except SyntaxError as e:
        return False, f"Invalid Python: {e}"


def validate_regex(text):
    try:
        re.compile(text)
        return True, ""
    except re.error as e:
        return False, f"Invalid regex: {e}"


VALIDATORS = {"json": validate_json, "python": validate_python, "regex": validate_regex}


def grade_syntax(output, fmt):
    """Return a score of 10 if the code block is valid for its format, otherwise 0."""
    code = extract_code(output, fmt)
    if not code:
        return {"syntax_score": 0, "syntax_detail": "No code found in the answer"}
    ok, detail = VALIDATORS[fmt](code)
    return {"syntax_score": 10 if ok else 0, "syntax_detail": detail}


# ---------- Model-based grading: Claude reads the answer and scores it ----------

def grade_with_model(case, output):
    criteria = "\n".join(f"- {c}" for c in case["criteria"])
    prompt = f"""You are grading an answer written by an AI assistant.

The user asked for ({case["format"]}):
<task>
{case["task"]}
</task>

The answer to grade:
<answer>
{output}
</answer>

A good answer meets these criteria:
{criteria}

Be strict. Return only a JSON object with these keys:
- "strengths": a list of short strings
- "weaknesses": a list of short strings
- "reasoning": one or two sentences
- "score": an integer from 1 to 10"""
    verdict = extract_json(chat(prompt))
    return {
        "model_score": max(1, min(10, int(verdict["score"]))),
        "strengths": verdict.get("strengths", []),
        "weaknesses": verdict.get("weaknesses", []),
        "reasoning": verdict.get("reasoning", ""),
    }


def grade_case(case, output):
    """Combine both graders: the final score is the average of the two."""
    result = {}
    result.update(grade_with_model(case, output))
    result.update(grade_syntax(output, case["format"]))
    result["final_score"] = (result["model_score"] + result["syntax_score"]) / 2
    return result
