"""Write an HTML report for one evaluation run."""
import html
from pathlib import Path


def write_report(prompt_name, results, path):
    average = sum(r["final_score"] for r in results) / len(results)
    rows = ""
    for i, r in enumerate(results, 1):
        case = r["case"]
        rows += (
            f"<h3>Case {i} ({html.escape(case['format'])}): {r['final_score']:.1f}/10</h3>"
            f"<p><b>Task:</b> {html.escape(case['task'])}</p>"
            f"<p><b>Model score:</b> {r['model_score']}/10 &nbsp; "
            f"<b>Syntax score:</b> {r['syntax_score']}/10 "
            f"{html.escape(r.get('syntax_detail', ''))}</p>"
            f"<p><b>Grader:</b> {html.escape(str(r['reasoning']))}</p>"
            f"<p><b>Weaknesses:</b> {html.escape('; '.join(map(str, r['weaknesses'])))}</p>"
            f"<pre style='white-space:pre-wrap;background:#f4f4f4;padding:8px'>{html.escape(r['output'])}</pre><hr>"
        )
    page = (
        "<html><head><meta charset='utf-8'></head>"
        "<body style='font-family:sans-serif;max-width:800px;margin:auto'>"
        f"<h1>Prompt {html.escape(prompt_name)}: average {average:.1f} / 10</h1>{rows}</body></html>"
    )
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
