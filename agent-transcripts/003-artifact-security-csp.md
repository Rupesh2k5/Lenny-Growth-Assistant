# Agent Transcript 003: Artifact Viewer Security & HTML Sandboxing Architecture

**Timestamp**: 2026-08-24T11:20:00Z  
**Agent Role**: Forward Deployed Engineer Assistant  
**Topic**: Mitigating XSS, DOM Leakage, and Enforcing Strict Iframe Sandboxing

---

## 1. Security Threat Model for AI Artifacts
- **Vulnerability**: An LLM generating raw HTML/CSS/JS could inadvertently or maliciously emit scripts attempting to access `window.parent.localStorage`, hijack user cookies, exfiltrate session data, or perform clickjacking.
- **Requirement**: The in-app Artifact Viewer must render rich interactive widgets (e.g. calculators, sliders, charts) safely without compromising host application integrity.

## 2. Security Solution & Defense-in-Depth
1. **Server-Side Sanitization**:
   - `backend/app/core/security.py` runs incoming HTML through an HTML sanitizer stripping dangerous attributes (`onload`, `onerror`, `javascript:` URIs) while retaining safe SVG, inline CSS styles, and standard HTML5 elements.
2. **Strict Client-Side Iframe Sandboxing**:
   - The React `SandboxedFrame` component injects the sanitized HTML into an `<iframe>` configured with:
     ```html
     <iframe
       sandbox="allow-scripts"
       referrerpolicy="no-referrer"
       csp="default-src 'self' 'unsafe-inline'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;"
     />
     ```
   - **Crucial Rule**: `allow-same-origin` is **strictly omitted**. As a result, the script executing inside the iframe treats the parent frame as a completely different origin, making it impossible to read parent cookies or local storage.

## 3. Verification
- Injected test payloads with `parent.localStorage.getItem('token')` and verified that browsers threw standard `SecurityError: Blocked a frame with origin "null" from accessing a cross-origin frame`.
