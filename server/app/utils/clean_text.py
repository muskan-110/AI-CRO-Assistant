import re
import json


def extract_json(raw_text: str) -> dict:
    """
    Extracts JSON from AI response, handling:
    - Markdown code fences
    - Text before/after JSON
    - Unterminated strings caused by unescaped quotes in HTML
    """
    text = raw_text.strip()

    # Remove markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Find where JSON starts
    first_brace = text.find("{")
    if first_brace == -1:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    text = text[first_brace:]

    # Strategy 1: Try parsing as-is first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: The personalizedHtml field often contains unescaped quotes/newlines.
    # Extract it separately using regex, then parse the rest normally.
    try:
        return _extract_with_html_regex(text)
    except Exception:
        pass

    # Strategy 3: Try to fix common issues and parse again
    try:
        fixed = _fix_common_json_issues(text)
        return json.loads(fixed)
    except Exception:
        pass

    raise ValueError(f"Could not parse JSON from response: {text[:300]}")


def _extract_with_html_regex(text: str) -> dict:
    """
    Pulls out personalizedHtml using regex (finds the full HTML block),
    then parses the remaining fields normally.
    """
    # Match personalizedHtml value — captures everything between the first
    # occurrence of "personalizedHtml": " and the closing </html> tag
    html_pattern = re.search(
        r'"personalizedHtml"\s*:\s*"(.*?</html>)\s*"',
        text,
        re.DOTALL
    )

    if not html_pattern:
        # Try without closing html tag
        html_pattern = re.search(
            r'"personalizedHtml"\s*:\s*"(<!DOCTYPE.*?)"(?:\s*,|\s*})',
            text,
            re.DOTALL
        )

    if html_pattern:
        html_content = html_pattern.group(1)
        # Unescape any escaped quotes inside the HTML
        html_content = html_content.replace('\\"', '"').replace('\\n', '\n')

        # Extract changes array
        changes = []
        changes_pattern = re.search(
            r'"changes"\s*:\s*\[(.*?)\]',
            text,
            re.DOTALL
        )
        if changes_pattern:
            changes_raw = changes_pattern.group(1)
            changes = re.findall(r'"([^"]*)"', changes_raw)

        # Extract score
        score = 80
        score_pattern = re.search(r'"score"\s*:\s*(\d+)', text)
        if score_pattern:
            score = int(score_pattern.group(1))

        return {
            "personalizedHtml": html_content,
            "changes": changes if changes else ["Page personalized to match ad messaging"],
            "score": score
        }

    raise ValueError("Could not find personalizedHtml in response")


def _fix_common_json_issues(text: str) -> str:
    """
    Attempts to fix common JSON issues from AI responses.
    """
    # Replace actual newlines inside string values with \n
    # This is a simple heuristic — find content between quotes and escape it
    text = re.sub(r'(?<!\\)\n', '\\n', text)
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)
    return text


def truncate_html(html: str, max_chars: int = 6000) -> str:
    """
    Truncates HTML to max_chars at a clean tag boundary.
    """
    if len(html) <= max_chars:
        return html

    truncated = html[:max_chars]
    last_tag_end = truncated.rfind(">")
    if last_tag_end != -1:
        truncated = truncated[:last_tag_end + 1]

    return truncated + "\n<!-- truncated -->"


def clean_html_string(html: str) -> str:
    """
    Strips markdown fences from an HTML string returned by AI.
    """
    html = html.strip()
    html = re.sub(r"^```(?:html)?\s*", "", html)
    html = re.sub(r"\s*```$", "", html)
    return html.strip()


def sanitize_ad_input(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", "")
    return text.strip()