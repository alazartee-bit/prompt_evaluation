# Claude prompt evaluation pipeline

A small, readable pipeline for answering one question: **is prompt B actually better than prompt A?**

It asks Claude to write test cases, runs each prompt on every case, grades every answer two ways, and compares the scores. It follows the prompt-evaluation lessons of Anthropic's course [Building with the Claude API](https://academy.claude.com/courses/building-with-the-claude-api).

## How it works

1. **Generate a dataset.** Claude writes test cases for AWS-related code in three formats: Python, JSON and regex. Each case has a task, a format and 2 criteria.
2. **Run the prompts.** Every prompt in `prompts.py` is run on every case.
3. **Grade each answer twice.**
   - *Model grading:* Claude reads the answer and scores it from 1 to 10 against the criteria.
   - *Code grading:* plain Python checks that the answer is valid (Python parses, JSON loads, regex compiles) and scores 10 or 0.
4. **Combine.** The final score for a case is the average of the two. Per-prompt averages are printed and each prompt gets an HTML report.

## Files

| File | Purpose |
|---|---|
| `config.py` | Model name, concurrency and API key check |
| `claude_helpers.py` | `chat()` plus functions that pull JSON and code out of replies |
| `prompts.py` | The prompt versions under test (add yours here) |
| `generate_dataset.py` | Creates `datasets/aws_tasks.json` |
| `graders.py` | Model grader and code graders |
| `report.py` | Writes the HTML reports |
| `run_eval.py` | Runs everything and prints the comparison |
| `test_graders.py` | Tests that run without an API key |

## Setup

```
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your API key after `ANTHROPIC_API_KEY=`. The `.env` file is ignored by Git.

## Run

```
python generate_dataset.py --n 6
python run_eval.py --prompts v1 v2
python -m pytest -q
```

HTML reports are written to the `reports` folder. Each run calls the API, so it costs a small amount.

## Results

6 test cases (2 Python, 2 JSON, 2 regex), graded with claude-sonnet-5-5.

| prompt | final | model | syntax |
|---|---|---|---|
| v1 | 9.3 | 8.7 | 10.0 |
| v2 | 9.5 | 9.0 | 10.0 |

Both prompts produced valid code every time. v2 scored slightly higher with the model grader, but with 6 cases a gap this small is within noise. A larger, harder dataset is the next step.

## Limits

- Graded by Claude, so scores carry that model's own biases. The code check is the objective part.
- Small datasets (6 cases by default) give noisy averages. Use more cases before trusting a small difference.
- The code check proves an answer is valid, not that it is correct.
