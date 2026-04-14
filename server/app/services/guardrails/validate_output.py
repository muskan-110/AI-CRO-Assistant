def validate_output(result):
    # Ensure heroHtml exists
    if "heroHtml" not in result:
        result["heroHtml"] = "<div>Fallback content</div>"

    # Prevent empty CTA
    if "cta" in result and not result["cta"]:
        result["cta"] = "Get Started"

    # Prevent huge HTML
    if len(result.get("heroHtml", "")) > 2000:
        result["heroHtml"] = result["heroHtml"][:2000]

    return result