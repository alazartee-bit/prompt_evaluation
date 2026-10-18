"""Tests that run without an API key. Run them with:  python -m pytest -q"""
import graders
from claude_helpers import extract_code, extract_json


def test_validators_accept_valid_code():
    assert graders.validate_json('{"a": 1}')[0]
    assert graders.validate_python("def f():\n    return 1")[0]
    assert graders.validate_regex(r"^\d{4}$")[0]


def test_validators_reject_invalid_code():
    assert not graders.validate_json("{'a': 1}")[0]
    assert not graders.validate_python("def f(:")[0]
    assert not graders.validate_regex("(unclosed")[0]


def test_extract_code_prefers_the_right_language():
    reply = "Intro\n```python\nprint('x')\n```\nand\n```json\n{\"a\": 1}\n```"
    assert extract_code(reply, "json") == '{"a": 1}'
    assert extract_code(reply, "python") == "print('x')"


def test_extract_code_falls_back_to_raw_text():
    assert extract_code("^abc$", "regex") == "^abc$"


def test_extract_json_handles_fences_and_extra_words():
    assert extract_json('Sure!\n```json\n[{"a": 1}]\n```') == [{"a": 1}]


def test_grade_syntax_scores_ten_or_zero():
    good = graders.grade_syntax("```regex\n^a+$\n```", "regex")
    bad = graders.grade_syntax("```regex\n(oops\n```", "regex")
    assert good["syntax_score"] == 10
    assert bad["syntax_score"] == 0


def test_grade_case_averages_model_and_syntax(monkeypatch):
    monkeypatch.setattr(
        graders, "grade_with_model",
        lambda case, output: {"model_score": 8, "strengths": [], "weaknesses": [], "reasoning": "ok"},
    )
    case = {"task": "t", "format": "json", "criteria": ["c"]}
    result = graders.grade_case(case, '```json\n{"a": 1}\n```')
    assert result["final_score"] == 9.0
