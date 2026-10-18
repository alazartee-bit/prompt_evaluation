"""Small helpers for talking to Claude and cleaning up its replies."""
import json
import re

from anthropic import Anthropic

from config import MODEL, require_api_key

_client = None


def get_client():
    """Create the API client once, the first time it is needed."""
    global _client
    if _client is None:
        require_api_key()
        _client = Anthropic()
    return _client


def chat(prompt, system=None, max_tokens=2000):
    """Send one user message and return Claude's reply as plain text."""
    params = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        params["system"] = system
    message = get_client().messages.create(**params)
    return "".join(block.text for block in message.content if block.type == "text")


def extract_json(text):
    """Pull JSON out of a reply, even if Claude wraps it in a code fence or adds words."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    starts = [i for i in (text.find("["), text.find("{")) if i != -1]
    if not starts:
        raise ValueError("No JSON found in this reply:\n" + text)
    start = min(starts)
    end = max(text.rfind("]"), text.rfind("}"))
    return json.loads(text[start : end + 1])


def extract_code(text, language):
    """Return the first code block for `language`; fall back to any block, then the raw text."""
    match = re.search(rf"```{re.escape(language)}[ \t]*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if not match:
        match = re.search(r"```[\w+-]*[ \t]*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()
