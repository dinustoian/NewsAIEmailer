from __future__ import annotations

"""
Entry point for the news scraping + AI analysis workflow.

This module delegates responsibilities to:
- scraping.py        → scraping news and arbitrary web pages
- ai_client.py       → talking to OpenAI and cleaning the HTML
- email_service.py   → formatting and sending Gmail emails
- config.py          → centralised configuration and environment handling
"""

from typing import Optional

from config import settings
from functions.ai_client import get_ai_info
from functions.email_service import send_email_with_gmail
from functions.scraping import scrape_biziday, scrape_stiripesurse


def run_daily_news_flow(
    send_email: bool = False,
    recipients: Optional[list[str]] = None,
) -> None:
    """
    Orchestrate the full flow:

    1. Scrape news from stiripesurse.ro and biziday.ro
    2. Build the combined news text and send it to the AI for HTML analysis
    3. Optionally send the final AI result via Gmail
    """
    # 1. Scrape news from both sources
    news_stiripesurse = scrape_stiripesurse(return_formatted=True)
    news_biziday = scrape_biziday(return_formatted=True)

    combined_news = f"{news_stiripesurse}\n\n{news_biziday}"

    # 2. Get AI HTML analysis on combined news
    info_html = get_ai_info(combined_news)

    # 3. Optionally send email(s) with the final AI result only
    if send_email:
        recipients = recipients or settings.email_recipients
        if not recipients:
            print(
                "\n⚠️ No email recipients configured. "
                "Set EMAIL_RECIPIENTS in .env or pass a list of recipients."
            )
            return

        for recipient in recipients:
            if recipient:
                send_email_with_gmail(
                    to_email=recipient,
                    subject=settings.gmail.default_subject,
                    body=info_html,
                    is_html=True,
                )
    else:
        # If not sending email, just print a short message
        print("\nAI analysis generated (HTML). Email sending is disabled in this run.")


if __name__ == "__main__":
    # By default, keep the same behaviour as the original script:
    # generate the AI analysis and send it by email (since this is your workflow).
    run_daily_news_flow(send_email=True)


