import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


def scrape_page(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.ProxyError:
        return _error("proxy_blocked", "Your network is blocking this URL.")
    except requests.exceptions.ConnectionError:
        return _error("connection_failed", f"Could not connect to {url}.")
    except requests.exceptions.Timeout:
        return _error("timeout", f"Request to {url} timed out.")
    except Exception as e:
        return _error("unknown", str(e))

    if response.status_code != 200:
        return _error("bad_status", f"Server returned HTTP {response.status_code}.")

    if response.encoding and response.encoding.lower() in ("iso-8859-1", "latin-1"):
        response.encoding = "utf-8"
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    # ── Fix charset ───────────────────────────────────────────────────────
    head = soup.find("head")
    if head:
        if not head.find("meta", charset=True):
            head.insert(0, soup.new_tag("meta", charset="utf-8"))

    # ── Absolutify URLs ───────────────────────────────────────────────────
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    _absolutify_urls(soup, base_url, url)

    # ── Add base tag ──────────────────────────────────────────────────────
    if head and not head.find("base"):
        head.insert(0, soup.new_tag("base", href=base_url + "/"))

    # ── Extract brand colors ──────────────────────────────────────────────
    brand_colors = _extract_brand_colors(soup, html)

    fixed_html = str(soup)

    # ── Extract page info ─────────────────────────────────────────────────
    title = soup.title.string.strip() if soup.title else "No title"
    h1 = soup.find("h1") or soup.find("h2")
    headline = h1.get_text(strip=True) if h1 else "No headline found"

    cta = None
    action_words = ("start", "get", "try", "sign", "join", "buy",
                    "book", "learn", "download", "open", "invest", "trade")
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        if text:
            cta = text
            break
    if not cta:
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True).lower()
            if any(w in text for w in action_words):
                cta = a.get_text(strip=True)
                break
    if not cta:
        first_link = soup.find("a")
        cta = first_link.get_text(strip=True) if first_link else "No CTA found"

    # ── Find best injection point ─────────────────────────────────────────
    injection_point = _find_injection_point(soup)

    return {
        "success": True,
        "title": title,
        "headline": headline,
        "cta": cta,
        "html": fixed_html,
        "url": url,
        "base_url": base_url,
        "brand_colors": brand_colors,
        "injection_point": injection_point,
    }


def _extract_brand_colors(soup: BeautifulSoup, html: str) -> dict:
    """
    Extract the primary brand color from the page's CSS and inline styles.
    Returns bg_color and text_color for the hero banner.
    """
    # Look for color patterns in style tags and inline styles
    all_styles = ""
    for style_tag in soup.find_all("style"):
        all_styles += style_tag.get_text()

    # Common brand color patterns — look for primary/brand/main colors
    hex_colors = re.findall(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})', all_styles)

    # Look for colors on nav/header elements (most representative of brand)
    brand_element = (
        soup.find("nav") or
        soup.find("header") or
        soup.find(class_=re.compile(r'nav|header|navbar', re.I))
    )

    primary_color = None
    if brand_element:
        style = brand_element.get("style", "")
        color_match = re.search(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,6}|rgb[^;]+)', style)
        if color_match:
            primary_color = color_match.group(1)

    # Check meta theme-color (most reliable brand color signal)
    theme_color = soup.find("meta", attrs={"name": "theme-color"})
    if theme_color and theme_color.get("content"):
        primary_color = theme_color.get("content")

    # Fallback: use most common dark hex color from styles
    if not primary_color and hex_colors:
        # Filter out whites/near-whites and pick darkest
        filtered = [c for c in hex_colors if not _is_light_color(c)]
        if filtered:
            primary_color = "#" + filtered[0]

    # Default to a neutral dark color if nothing found
    if not primary_color:
        primary_color = "#1a1a2e"

    # Determine text color based on background brightness
    text_color = "#ffffff" if _is_dark_color_str(primary_color) else "#111111"
    btn_color = _derive_button_color(primary_color)

    return {
        "bg_color": primary_color,
        "text_color": text_color,
        "btn_color": btn_color,
        "btn_text_color": "#ffffff" if _is_dark_color_str(btn_color) else "#111111",
    }


def _find_injection_point(soup: BeautifulSoup) -> str:
    """
    Finds the best CSS selector to inject the hero AFTER.
    Priority: after navbar/header → after first section → after body open
    Returns a marker string we use in personalization.py
    """
    # Look for common navbar patterns
    nav = soup.find("nav")
    if nav:
        nav["data-inject-after"] = "true"
        return "nav"

    header = soup.find("header")
    if header:
        header["data-inject-after"] = "true"
        return "header"

    # Look for sticky/fixed top bar
    for tag in soup.find_all(["div", "section"], limit=5):
        classes = " ".join(tag.get("class", []))
        if re.search(r'nav|header|topbar|top-bar|toolbar', classes, re.I):
            return "topbar"

    return "body"  # fallback — inject right after <body>


def _is_light_color(hex_str: str) -> bool:
    """Returns True if the hex color is too light (close to white)."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    try:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness > 200
    except Exception:
        return False


def _is_dark_color_str(color: str) -> bool:
    """Returns True if color string is dark enough for white text."""
    hex_str = color.lstrip("#")
    if color.startswith("rgb"):
        nums = re.findall(r'\d+', color)
        if len(nums) >= 3:
            r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
            return (r * 299 + g * 587 + b * 114) / 1000 < 128
        return True
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    try:
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return (r * 299 + g * 587 + b * 114) / 1000 < 128
    except Exception:
        return True


def _derive_button_color(bg_color: str) -> str:
    """Derives a contrasting button color from the background."""
    if _is_dark_color_str(bg_color):
        return "#ffffff"
    return "#111111"


def _absolutify_urls(soup: BeautifulSoup, base_url: str, page_url: str):
    url_attrs = {
        "img":    ["src", "data-src", "data-lazy-src"],
        "script": ["src"],
        "link":   ["href"],
        "a":      ["href"],
        "source": ["src", "srcset"],
        "video":  ["src", "poster"],
        "iframe": ["src"],
    }
    for tag_name, attrs in url_attrs.items():
        for tag in soup.find_all(tag_name):
            for attr in attrs:
                val = tag.get(attr)
                if not val:
                    continue
                if val.startswith(("data:", "#", "javascript:", "mailto:")):
                    continue
                if val.startswith(("http://", "https://")):
                    continue
                tag[attr] = urljoin(page_url, val)

    for tag in soup.find_all(srcset=True):
        srcset = tag["srcset"]
        parts = []
        for entry in srcset.split(","):
            entry = entry.strip()
            if not entry:
                continue
            pieces = entry.split()
            if pieces:
                url_part = pieces[0]
                if not url_part.startswith(("http://", "https://", "data:")):
                    url_part = urljoin(page_url, url_part)
                pieces[0] = url_part
            parts.append(" ".join(pieces))
        tag["srcset"] = ", ".join(parts)


def _error(error_type: str, message: str) -> dict:
    return {
        "success": False,
        "error_type": error_type,
        "error_message": message,
        "title": "", "headline": "", "cta": "", "html": "", "url": "",
        "brand_colors": {"bg_color": "#1a1a2e", "text_color": "#ffffff",
                         "btn_color": "#ffffff", "btn_text_color": "#111111"},
        "injection_point": "body",
    }

def detect_navbar_height(soup):
    nav = soup.find("nav")
    header = soup.find("header")

    if nav:
        return 80
    if header:
        return 90
    
    return 60  # fallback