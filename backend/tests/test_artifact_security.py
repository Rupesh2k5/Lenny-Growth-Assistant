import pytest
from app.core.security import sanitize_html, is_safe_html, validate_artifact_content

def test_sanitize_blocks_script_tags():
    malicious_html = """
    <div>
        <h1>Growth Strategy Dashboard</h1>
        <script>alert("XSS Attack!");</script>
        <p>Safe content</p>
    </div>
    """
    sanitized = sanitize_html(malicious_html)
    assert "<script>" not in sanitized
    assert "alert(" not in sanitized
    assert "Safe content" in sanitized

def test_sanitize_blocks_inline_event_handlers():
    malicious_html = '<button onclick="evilFunction()">Click me</button><img src="x" onerror="alert(1)">'
    sanitized = sanitize_html(malicious_html)
    assert "onclick" not in sanitized
    assert "onerror" not in sanitized

def test_sanitize_blocks_javascript_urls():
    malicious_html = '<a href="javascript:stealTokens()">Malicious Link</a>'
    sanitized = sanitize_html(malicious_html)
    assert "javascript:" not in sanitized

def test_validate_artifact_content_safe_html():
    safe_html = """
    <div style="font-family: sans-serif; padding: 20px;">
        <h2>Elena Verna Growth Loop Simulator</h2>
        <input type="range" id="retention" min="1" max="100" value="40">
        <div id="output">Output: 40%</div>
    </div>
    """
    valid = validate_artifact_content(safe_html, artifact_type="html")
    assert valid is True
