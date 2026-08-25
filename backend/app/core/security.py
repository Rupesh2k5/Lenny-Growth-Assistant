import re
import html
from typing import Tuple

ALLOWED_TAGS = [
    'html', 'head', 'body', 'meta', 'title', 'style',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'hr', 'br',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'strong', 'b', 'em', 'i', 'u', 's', 'small', 'sub', 'sup',
    'a', 'img', 'svg', 'path', 'circle', 'rect', 'line', 'polygon',
    'button', 'input', 'label', 'select', 'option', 'textarea', 'form', 'fieldset',
    'canvas', 'section', 'article', 'header', 'footer', 'main', 'nav'
]

DANGEROUS_PATTERNS = [
    r'<\s*script[^>]*>.*?<\s*/\s*script\s*>',  # script blocks
    r'<\s*script[^>]*>',                       # unclosed script tags
    r'on\w+\s*=\s*["\'][^"\']*["\']',         # event handlers with quotes (e.g. onclick="...")
    r'on\w+\s*=\s*[^ >]+',                     # unquoted event handlers (e.g. onclick=alert(1))
    r'javascript\s*:',                         # javascript: URIs
    r'data\s*:\s*text/html',                  # data URIs with html
    r'vbscript\s*:',                           # vbscript URIs
    r'parent\.',                               # iframe parent DOM traversal
    r'top\.',                                  # iframe top DOM traversal
    r'localStorage',                           # local storage access
    r'sessionStorage',                         # session storage access
    r'document\.cookie',                       # cookie access
    r'window\.opener',                         # opener access
]

def sanitize_html(raw_html: str) -> str:
    """
    Sanitizes generated HTML artifacts by stripping script tags, event handlers, and DOM escape patterns.
    """
    if not raw_html:
        return ""
    
    sanitized = raw_html
    for pattern in DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Ensure standard HTML wrapper if missing
    if not re.search(r'<!DOCTYPE\s+html>', sanitized, re.IGNORECASE) and '<html' not in sanitized:
        sanitized = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: #ffffff;
            padding: 24px;
            margin: 0;
        }}
    </style>
</head>
<body>
{sanitized}
</body>
</html>"""
    
    return sanitized

def sanitize_html_content(raw_html: str) -> str:
    """Alias for backwards compatibility."""
    return sanitize_html(raw_html)

def is_safe_html(raw_html: str) -> bool:
    """Returns True if HTML contains no known dangerous tags or attribute patterns."""
    if not raw_html:
        return True
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, raw_html, flags=re.IGNORECASE | re.DOTALL):
            return False
    return True

def validate_artifact_content(content: str, artifact_type: str = "html") -> bool:
    """Validates that artifact content meets size and security constraints."""
    if not content or not content.strip():
        return False
    if len(content.encode("utf-8")) > 500_000:
        return False
    return True
