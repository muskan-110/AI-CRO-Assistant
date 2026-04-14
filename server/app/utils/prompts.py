def ad_analysis_prompt(is_image: bool) -> str:
    base = """You are an expert digital marketing analyst.
Analyze this ad creative and extract the REAL marketing intent.
 
STRICT RULES:
- Decode irony correctly: "THIS IS AN AD FOR MEN" from L'Oreal = women empowerment
- Stay grounded — only report what is actually visible in the ad
- Never invent claims not present in the ad
- Be specific about audience, tone, and value prop
 
Return ONLY valid JSON — no markdown, no explanation:
{
  "headline": "real value proposition max 10 words",
  "cta": "call-to-action text from ad",
  "theme": "product category e.g. Beauty, FinTech, SaaS, DEI",
  "audience": "specific audience e.g. corporate executives, new traders",
  "tone": "emotional tone e.g. bold and empowering, urgent, friendly",
  "pain_point": "specific problem the ad addresses",
  "value_prop": "specific benefit being offered"
}"""
    if not is_image:
        base += "\n\nAd creative provided as URL or text description."
    return base


# def personalization_prompt(ad_analysis: dict, page_content: dict) -> str:
#     return f"""You are a CRO expert. Write a hero banner HTML snippet to inject at the top of an existing webpage.

# CONTEXT — what the ad promises:
# - Headline: {ad_analysis.get('headline', '')}
# - CTA: {ad_analysis.get('cta', '')}
# - Audience: {ad_analysis.get('audience', '')}
# - Tone: {ad_analysis.get('tone', '')}
# - Pain Point: {ad_analysis.get('pain_point', '')}
# - Value Prop: {ad_analysis.get('value_prop', '')}
# - Theme: {ad_analysis.get('theme', '')}

# ORIGINAL PAGE (keep its identity intact):
# - Title: {page_content.get('title', '')}
# - Headline: {page_content.get('headline', '')}
# - CTA: {page_content.get('cta', '')}

# STRICT RULES — you MUST follow these:
# 1. Write ONLY a hero banner <div> snippet — NOT a full HTML page
# 2. The hero must be RELEVANT to the original page's topic + the ad message combined
# 3. Do NOT completely replace the page identity — enhance it
# 4. Keep the headline closely tied to BOTH the ad AND the page topic
# 5. Use inline CSS only — no external stylesheets
# 6. Make it visually polished with a strong background color, white text, clear CTA button
# 7. Hero should be max 300px tall — compact, not full-screen takeover
# 8. Do NOT hallucinate stats or claims not supported by the ad

# ANTI-HALLUCINATION CHECK:
# - If ad is about beauty products → hero must mention beauty/cosmetics
# - If ad is about trading → hero must mention trading/investing  
# - If ad is about DEI → hero must mention leadership/workplace diversity
# - The hero content must logically connect the ad to the page

# Return ONLY this JSON and nothing else. No markdown. No explanation:
# {{"heroHtml":"YOUR_HERO_DIV_HERE","newTitle":"NEW TITLE","changes":["change 1","change 2","change 3"],"score":85}}

# Escape all double quotes inside HTML as \\" and newlines as \\n.
# The heroHtml must start with <div and end with </div>."""