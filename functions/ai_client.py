from __future__ import annotations

import re
from typing import Optional

try:
    from openai import OpenAI

    AI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    AI_AVAILABLE = False

from config import settings
from config.prompts import NEWS_ANALYSIS_PROMPT


def clean_ai_html_response(ai_response: str) -> str:
    """
    Clean the AI response to extract actual HTML code.

    The AI often wraps HTML in markdown code blocks or escapes it.
    """
    content = ai_response.strip()

    # Remove markdown code blocks (```html ... ```)
    if "```" in content:
        pattern = r"```(?:html|HTML)?\s*\n?(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = match.group(1).strip()

    # Unescape HTML entities if needed
    if "&lt;" in content or "&gt;" in content or "&amp;" in content:
        from html import unescape

        content = unescape(content)

    # Remove any leading/trailing text that's not HTML
    doctype_match = re.search(r"<!DOCTYPE[^>]*>", content, re.IGNORECASE)
    html_match = re.search(r"<html[^>]*>", content, re.IGNORECASE)

    if doctype_match:
        content = content[doctype_match.start() :]
    elif html_match:
        content = content[html_match.start() :]

    # Remove any text after </html> tag
    html_end_match = re.search(r"</html>", content, re.IGNORECASE)
    if html_end_match:
        content = content[: html_end_match.end()]
    cleaned = content.strip()

    # Remove known generic disclaimer about stiripesurse.ro reliability if present
    disclaimer_snippet = (
        "Site-ul stiripesurse.ro este cunoscut pentru o gamă variată de știri"
    )
    if disclaimer_snippet in cleaned:
        cleaned = re.sub(
            r"<p[^>]*>[^<]*Site-ul stiripesurse\\.ro[^<]*</p>",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
    return cleaned


def get_ai_info(news: str) -> str:
    """
    Send news to OpenAI and get formatted analysis.

    Returns:
        AI analysis as an HTML string.
    """
    if not AI_AVAILABLE:
        print(
            "Error: OpenAI library not installed. Install with: pip install openai"
        )
        return news

    api_key: Optional[str] = settings.openai_api_key
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment variables")
        return news

    try:
        print("🤖 Asking AI for analysis...")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=settings.ai.model,
            messages=[
                {
                    "role": "user",
                    "content": NEWS_ANALYSIS_PROMPT.format(news=news),
                }
            ],
            # gpt-5-mini does not support a temperature parameter; rely on model defaults.
            max_completion_tokens=settings.ai.max_completion_tokens,
        )
        ai_content = response.choices[0].message.content
        print("✅ AI analysis received!")
        cleaned_html = clean_ai_html_response(ai_content)
        return cleaned_html
    except Exception as e:  # pragma: no cover - network/API errors
        print(f"Error calling OpenAI: {e}")
        return news



