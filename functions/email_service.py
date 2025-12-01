from __future__ import annotations

import base64
import os
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Union

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GMAIL_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    GMAIL_AVAILABLE = False

from config import settings


def prepare_html_for_email(html_content: str) -> str:
    """
    Convert a full HTML document to email-compatible HTML.

    Email clients typically expect only the `<body>` contents.
    """
    # Extract body content using regex (works even without BeautifulSoup)
    body_pattern = r"<body[^>]*>(.*?)</body>"
    body_match = re.search(body_pattern, html_content, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1).strip()
        if (
            body_content
            and "<!DOCTYPE" not in body_content
            and not body_content.strip().startswith("<html")
        ):
            return body_content

    # If BeautifulSoup is available, use it for more robust parsing
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html_content, "html.parser")
        if soup.find("html"):
            body_tag = soup.find("body")
            if body_tag:
                body_html = body_tag.decode_contents().strip()
                if (
                    "<!DOCTYPE" not in body_html
                    and not body_html.strip().startswith("<html")
                ):
                    return body_html
        return str(soup).strip()
    except Exception:
        pass

    # If no body tag found, check if it's already body content
    if not html_content.strip().startswith("<!DOCTYPE") and not html_content.strip().startswith(
        "<html"
    ):
        return html_content

    return html_content


def plain_text_to_html(text: str) -> str:
    """
    Convert plain text to HTML with proper styling and formatting.
    """
    # Escape HTML special characters
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    # Split into lines and process
    lines = text.split("\n")
    html_lines: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines but preserve spacing
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<br>")
            continue

        # Detect bullet points
        if stripped.startswith("- ") or stripped.startswith("• "):
            if not in_list:
                html_lines.append(
                    '<ul style="margin: 10px 0; padding-left: 20px;">'
                )
                in_list = True
            content = stripped[2:].strip()
            html_lines.append(
                f'<li style="margin: 5px 0; line-height: 1.6;">{content}</li>'
            )

        # Detect sub-bullets (indented with spaces and dash)
        elif stripped.startswith("  - "):
            if not in_list:
                html_lines.append(
                    '<ul style="margin: 10px 0; padding-left: 20px;">'
                )
                in_list = True
            content = stripped[4:].strip()
            html_lines.append(
                f'<li style="margin: 5px 0; line-height: 1.6; margin-left: 20px;">{content}</li>'
            )

        # Bold sections (ALL CAPS or ending with colon)
        elif stripped.isupper() or (stripped.endswith(":") and len(stripped) > 3):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(
                '<h3 style="color: #1a3a52; margin: 15px 0 10px 0;'
                ' font-size: 16px; font-weight: bold;">'
                f"{stripped}</h3>"
            )

        # Regular paragraphs
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(
                f'<p style="margin: 8px 0; line-height: 1.6; color: #333;">{stripped}</p>'
            )

    # Close any open list
    if in_list:
        html_lines.append("</ul>")

    # Join and create complete HTML
    body_content = "\n".join(html_lines)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{
            color: #1a3a52;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
            margin: 0 0 20px 0;
        }}
        h3 {{
            color: #1a3a52;
            margin: 20px 0 10px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        p {{
            margin: 10px 0;
            line-height: 1.7;
        }}
        ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        li {{
            margin: 8px 0;
            line-height: 1.7;
        }}
        .section {{
            border-left: 4px solid #2196F3;
            padding-left: 15px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_content}
        <div class="footer">
            <p>Email generat automat - {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        </div>
    </div>
</body>
</html>"""

    return html


def send_email_with_gmail(
    to_email: Union[str, list[str]],
    subject: str,
    body: str,
    credentials_file: Optional[str] = None,
    token_file: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    is_html: bool = True,
) -> bool:
    """
    Send an email using the Gmail API with OAuth2 authentication.
    
    Args:
        from_name: Display name for sender (e.g., "AI News"). If provided,
                   the From header will show as "AI News <email@example.com>"
    """
    if not GMAIL_AVAILABLE:
        print(
            "Error: Google API libraries not installed. Install with: "
            "pip install google-auth google-auth-oauthlib "
            "google-auth-httplib2 google-api-python-client"
        )
        return False

    # Gmail API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    creds = None

    credentials_file = credentials_file or settings.gmail.credentials_file
    token_file = token_file or settings.gmail.token_file

    # Load existing token if available
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")
            creds = None

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None

        if not creds:
            if not os.path.exists(credentials_file):
                print(
                    f"Error: {credentials_file} not found. Please download OAuth2 "
                    "credentials from Google Cloud Console."
                )
                return False

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error during authentication: {e}")
                return False

    # Save the credentials for the next run
    try:
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    except Exception as e:
        print(f"Warning: Could not save token: {e}")

    try:
        # Build the Gmail service
        service = build("gmail", "v1", credentials=creds)

        # Get user's email if not provided
        if not from_email:
            profile = service.users().getProfile(userId="me").execute()
            from_email = profile["emailAddress"]

        # Create the email message
        message = MIMEMultipart("alternative")
        message["to"] = ", ".join(to_email) if isinstance(to_email, list) else to_email
        # Format "From" with display name if provided (e.g., "AI News <email@example.com>")
        if from_name:
            from email.utils import formataddr
            message["from"] = formataddr((from_name, from_email))
        else:
            message["from"] = from_email
        message["subject"] = subject
        message["MIME-Version"] = "1.0"

        # Add body to email
        if is_html:
            # Check if it's already HTML
            if not body.startswith("<!DOCTYPE") and not body.startswith("<html") and not body.strip().startswith("<"):
                # Convert plain text to HTML
                body = plain_text_to_html(body)

            # Extract only the body content (email clients don't like full HTML documents)
            if (
                body.startswith("<!DOCTYPE")
                or body.startswith("<html")
                or "<body" in body
            ):
                html_body = prepare_html_for_email(body)
            else:
                html_body = body

            # Clean any remaining DOCTYPE/html tags
            if "<!DOCTYPE" in html_body or html_body.strip().startswith("<html"):
                html_body = re.sub(
                    r"<!DOCTYPE[^>]*>", "", html_body, flags=re.IGNORECASE
                )
                html_body = re.sub(
                    r"<html[^>]*>", "", html_body, flags=re.IGNORECASE
                )
                html_body = re.sub(r"</html>", "", html_body, flags=re.IGNORECASE)
                html_body = re.sub(
                    r"<head[^>]*>.*?</head>",
                    "",
                    html_body,
                    flags=re.DOTALL | re.IGNORECASE,
                )
                html_body = html_body.strip()

            # Create plain text version from HTML
            try:
                from bs4 import BeautifulSoup  # type: ignore

                soup = BeautifulSoup(html_body, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                plain_text = soup.get_text(separator="\n", strip=True)
            except Exception:
                plain_text = re.sub(r"<[^>]+>", "", html_body)
                plain_text = re.sub(r"\n\s*\n", "\n\n", plain_text).strip()

            # Create and attach MIME parts
            plain_part = MIMEText(plain_text, "plain", "utf-8")
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(plain_part)
            message.attach(html_part)
        else:
            message.attach(MIMEText(body, "plain", "utf-8"))

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Send the message
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        print(f"✅ Email sent successfully! Message ID: {send_message['id']}")
        return True

    except HttpError as error:  # pragma: no cover - network/API errors
        print(f"An error occurred while sending email: {error}")
        return False
    except Exception as e:  # pragma: no cover - unexpected errors
        print(f"Unexpected error: {e}")
        return False



