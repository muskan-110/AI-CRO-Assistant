"""
ad_analyzer.py
--------------
Analyzes an ad creative (image or URL) using OpenRouter
and returns structured information about the ad's intent.
"""

import os
from openai import OpenAI
from app.utils.prompts import ad_analysis_prompt
from app.utils.clean_text import extract_json, sanitize_ad_input

# Free model that supports vision (images)
VISION_MODEL = "openrouter/auto"

# Free model for text-only (faster, more quota)
TEXT_MODEL = "openrouter/auto"


def _get_client():
    return OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )


def analyze_ad(ad_creative: str) -> dict:
    """
    Takes ad_creative which is either:
      - A base64 encoded image string (starts with "data:image/...")
      - A plain URL string (starts with "http...")

    Returns a dict like:
    {
        "headline": "...",
        "cta": "...",
        "theme": "...",
        "audience": "...",
        "tone": "...",
        "pain_point": "...",
        "value_prop": "..."
    }
    """
    ad_creative = sanitize_ad_input(ad_creative)

    if not ad_creative:
        return _fallback("Empty ad creative received.")

    is_image = ad_creative.startswith("data:image")

    try:
        if is_image:
            return _analyze_image(ad_creative)
        else:
            return _analyze_url_or_text(ad_creative)
    except Exception as e:
        print(f"[ad_analyzer] Error: {e}")
        return _fallback(str(e))


def _analyze_image(base64_string: str) -> dict:
    """Sends a base64 image to OpenRouter vision model."""
    client = _get_client()
    prompt = ad_analysis_prompt(is_image=True)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": base64_string}},
                ],
            }
        ],
        max_tokens=1000,
    )

    raw_text = response.choices[0].message.content
    return extract_json(raw_text)


def _analyze_url_or_text(text: str) -> dict:
    """Sends a URL or text description to OpenRouter text model."""
    client = _get_client()
    prompt = ad_analysis_prompt(is_image=False)
    full_prompt = f"{prompt}\n\nAd creative input: {text}"

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=1000,
    )

    raw_text = response.choices[0].message.content
    return extract_json(raw_text)


def _fallback(reason: str) -> dict:
    print(f"[ad_analyzer] Using fallback because: {reason}")
    return {
        "headline": "Discover something new",
        "cta": "Get Started",
        "theme": "General",
        "audience": "General audience",
        "tone": "friendly",
        "pain_point": "Not detected",
        "value_prop": "Not detected",
    }