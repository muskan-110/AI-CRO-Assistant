import os
import json
import re
from openai import OpenAI
from app.utils.clean_text import clean_html_string

TEXT_MODEL = "openrouter/auto"


def _get_client():
    return OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )


def personalize_page(ad_analysis: dict, page_content: dict, landing_url: str) -> dict:
    try:
        # FIX #1 — pass landing_url through to _call_openrouter and _build_prompt
        return _call_openrouter(ad_analysis, page_content, landing_url)
    except Exception as e:
        print(f"[personalization] Error: {e}")
        return _fallback(ad_analysis, page_content)


def _build_prompt(ad_analysis: dict, page_content: dict, landing_url: str) -> str:
    colors = page_content.get("brand_colors", {})
    bg = colors.get("bg_color", "#1a1a2e")
    text = colors.get("text_color", "#ffffff")
    btn = colors.get("btn_color", "#ffffff")
    btn_text = colors.get("btn_text_color", "#111111")

    domain = ""
    try:
        from urllib.parse import urlparse
        domain = urlparse(landing_url).netloc.replace("www.", "")
    except Exception:
        domain = landing_url

    return f"""You are a CRO expert. Write a compact hero banner HTML snippet to inject into an existing webpage.

AD INFO:
- Headline: {ad_analysis.get('headline', '')}
- CTA: {ad_analysis.get('cta', '')}
- Audience: {ad_analysis.get('audience', '')}
- Tone: {ad_analysis.get('tone', '')}
- Pain Point: {ad_analysis.get('pain_point', '')}
- Value Prop: {ad_analysis.get('value_prop', '')}
- Theme: {ad_analysis.get('theme', '')}

ORIGINAL PAGE:
- Domain: {domain}
- Title: {page_content.get('title', '')}
- Topic/Headline: {page_content.get('headline', '')}
- Original CTA: {page_content.get('cta', '')}

BRAND COLORS (use these exactly — do not invent colors):
- Background: {bg}
- Text: {text}
- Button background: {btn}
- Button text: {btn_text}

STRICT RULES:
1. Output ONLY a single <div> snippet — NOT a full HTML page
2. Use ONLY the brand colors provided above — no white backgrounds, no light cards
3. The headline must relate to BOTH the ad topic AND the page topic ({domain})
4. Keep it compact — max 250px height, centered text
5. One headline (max 12 words), one subline (max 20 words), one CTA button
6. Use only inline CSS — no classes, no external styles
7. The outer <div> MUST start with: style="width:100%;box-sizing:border-box;background:{bg};color:{text};
8. NO position:absolute, NO floating cards, NO white/light backgrounds

ANTI-HALLUCINATION:
- If page is about trading/investing → hero must mention trading or investing
- If page is about SaaS → hero must mention the SaaS product category
- The hero must make sense on {domain} specifically

Return ONLY this JSON — no markdown, no explanation:
{{"heroHtml":"YOUR_DIV_HERE","newTitle":"NEW TITLE MAX 6 WORDS","changes":["change 1","change 2","change 3"],"score":85}}

Escape all double quotes inside HTML as \\" and newlines as \\n."""


def _call_openrouter(ad_analysis: dict, page_content: dict, landing_url: str) -> dict:
    client = _get_client()
    # FIX #1 — pass landing_url to _build_prompt
    prompt = _build_prompt(ad_analysis, page_content, landing_url)

    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    hero_html, new_title, changes, score = _parse_response(raw, ad_analysis)

    if not _is_relevant(hero_html, ad_analysis, page_content):
        print("[personalization] Relevance check failed — using fallback hero")
        hero_html = _make_hero(ad_analysis, page_content)

    personalized_html = _inject_into_page(
        page_content.get("html", ""),
        hero_html,
        new_title,
        page_content.get("injection_point", "body"),
    )

    return {"personalizedHtml": personalized_html, "changes": changes, "score": score}


def _parse_response(raw: str, ad_analysis: dict) -> tuple:
    # Strategy 1: direct JSON parse
    try:
        data = json.loads(raw)
        # FIX #2 — hero was referenced before assignment in the original code
        # now correctly extracted from data first, then sanitized
        hero = data.get("heroHtml", "")
        hero = re.sub(r'position\s*:\s*absolute', 'position:relative', hero, flags=re.IGNORECASE)
        if hero:
            return (
                hero,
                data.get("newTitle", ""),
                data.get("changes", []),
                int(data.get("score", 80)),
            )
    except Exception:
        pass

    # Strategy 2: regex extract div block
    div_match = re.search(r'(<div[\s\S]*?</div>)', raw, re.DOTALL)
    hero = div_match.group(1).replace('\\"', '"').replace('\\n', '\n') if div_match else ""

    title_m = re.search(r'"newTitle"\s*:\s*"([^"]*)"', raw)
    new_title = title_m.group(1) if title_m else ad_analysis.get("headline", "")

    changes_m = re.search(r'"changes"\s*:\s*\[(.*?)\]', raw, re.DOTALL)
    changes = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', changes_m.group(1)) if changes_m else [
        "Hero section injected matching brand colors",
        f"Headline updated to match ad: \"{ad_analysis.get('headline', '')}\"",
        f"CTA updated to \"{ad_analysis.get('cta', '')}\"",
    ]

    score_m = re.search(r'"score"\s*:\s*(\d+)', raw)
    score = int(score_m.group(1)) if score_m else 80

    return hero, new_title, changes, score


def _is_relevant(hero_html: str, ad_analysis: dict, page_content: dict) -> bool:
    page_topic = (
        page_content.get("title", "") + " " +
        page_content.get("headline", "")
    ).lower()

    ad_topic = (
        ad_analysis.get("theme", "") + " " +
        ad_analysis.get("headline", "") + " " +
        ad_analysis.get("value_prop", "")
    ).lower()

    hero_lower = hero_html.lower()

    page_words = set(w for w in re.findall(r'\b\w{4,}\b', page_topic)
                     if w not in {"this", "that", "with", "from", "have", "been"})
    page_match = any(w in hero_lower for w in page_words)

    ad_words = set(w for w in re.findall(r'\b\w{4,}\b', ad_topic)
                   if w not in {"this", "that", "with", "from", "have", "been"})
    ad_match = any(w in hero_lower for w in ad_words)

    return page_match and ad_match


def _inject_into_page(original_html: str, hero_html: str, new_title: str, injection_point: str) -> str:
    if not original_html:
        return f"<!DOCTYPE html><html><head><meta charset='UTF-8'/><title>{new_title}</title></head><body>{hero_html}</body></html>"

    result = original_html

    if new_title:
        result = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>',
                        result, flags=re.DOTALL | re.IGNORECASE)

    marker_style = (
        "background:#c8f04a;color:#000;text-align:center;"
        "padding:4px;font-size:11px;font-weight:700;"
        "letter-spacing:0.06em;width:100%;"
    )
    inject_block = (
        f'<div style="{marker_style}">✦ PERSONALIZED SECTION ✦</div>'
        + hero_html +
        f'<div style="{marker_style}">✦ ORIGINAL PAGE ✦</div>'
    )

    nav_end = re.search(r'</nav>', result, re.IGNORECASE)
    if nav_end:
        pos = nav_end.end()
        return result[:pos] + "\n" + inject_block + "\n" + result[pos:]

    header_end = re.search(r'</header>', result, re.IGNORECASE)
    if header_end:
        pos = header_end.end()
        return result[:pos] + "\n" + inject_block + "\n" + result[pos:]

    body_match = re.search(r'<body[^>]*>', result, re.IGNORECASE)
    if body_match:
        pos = body_match.end()
        return result[:pos] + "\n" + inject_block + "\n" + result[pos:]

    return inject_block + result


def _make_hero(ad_analysis: dict, page_content: dict) -> str:
    colors = page_content.get("brand_colors", {})
    bg = colors.get("bg_color", "#1a1a2e")
    text = colors.get("text_color", "#ffffff")
    btn = colors.get("btn_color", "#ffffff")
    btn_text = colors.get("btn_text_color", "#111111")

    headline = ad_analysis.get("headline", "Welcome")
    cta = ad_analysis.get("cta", "Learn More")
    sub = ad_analysis.get("value_prop") or ad_analysis.get("pain_point") or ""
    audience = ad_analysis.get("audience", "")

    # FIX #3 — was "background:{bg},margin-top:100%" — comma broke all inline styles
    # causing the browser to ignore the background and fall back to white
    return (
        f'<div style="position:relative;width:100%;box-sizing:border-box;background:{bg};'
        f'color:{text};padding:40px 24px;text-align:center;font-family:system-ui,sans-serif;">'
        f'<p style="font-size:11px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin:0 0 12px;opacity:0.7;">{audience.upper()}</p>'
        f'<h2 style="font-size:clamp(22px,3.5vw,40px);font-weight:800;'
        f'line-height:1.2;margin:0 auto 12px;max-width:680px;">{headline}</h2>'
        f'<p style="font-size:16px;opacity:0.85;max-width:560px;'
        f'margin:0 auto 24px;line-height:1.6;">{sub}</p>'
        f'<a href="#" style="display:inline-block;background:{btn};color:{btn_text};'
        f'padding:12px 28px;border-radius:6px;font-size:15px;font-weight:700;'
        f'text-decoration:none;">{cta} →</a>'
        f'</div>'
    )


def _fallback(ad_analysis: dict, page_content: dict) -> dict:
    hero_html = _make_hero(ad_analysis, page_content)
    personalized_html = _inject_into_page(
        page_content.get("html", ""),
        hero_html,
        ad_analysis.get("headline", "Personalized Page"),
        page_content.get("injection_point", "body"),
    )
    return {
        "personalizedHtml": personalized_html,
        "changes": [
            "Hero injected below navbar using brand colors",
            f"Headline: \"{ad_analysis.get('headline', '')}\"",
            f"CTA: \"{ad_analysis.get('cta', '')}\"",
        ],
        "score": 70,
    }