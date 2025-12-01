## News AI Emailer

This project scrapes the latest news from `stiripesurse.ro` and `biziday.ro`, sends the content to OpenAI for an in-depth HTML analysis, and can optionally email the resulting report via Gmail.

The code is structured into small, focused modules and packages:
- `config/__init__.py` – central configuration and environment handling (`settings`, `AIConfig`, `NewsConfig`, `GmailConfig`)
- `config/prompts.py` – AI prompt templates (e.g. `NEWS_ANALYSIS_PROMPT`)
- `functions/scraping.py` – scraping `stiripesurse.ro`, `biziday.ro` și pagini web arbitrare
- `functions/ai_client.py` – OpenAI client and HTML response cleaning
- `functions/email_service.py` – email formatting and Gmail sending
- `main.py` – orchestration / entrypoint

### Prerequisites

- Python **3.10+**
- `uv` (Python packaging & runtime manager)
  - Install on Windows (PowerShell):

```powershell
pip install uv
```

### Setup with uv

From the project root:

```powershell
cd "C:\Users\stoia\Desktop\AI Sandbox\OpenAItest"

# Create a virtual environment and install dependencies
uv sync
```

`uv sync` reads `pyproject.toml`, creates a virtual environment, and installs all required packages.

### Configuration

The application uses environment variables for secrets and basic runtime configuration.

- `OPENAI_API_KEY` – your OpenAI API key (required for AI analysis)
- `EMAIL_RECIPIENTS` – optional, comma-separated list of email addresses to send the report to

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=sk-...
EMAIL_RECIPIENTS=you@example.com,another@example.com
```

`config/__init__.py` loads this file automatically via `python-dotenv`.

### Gmail API Setup

To enable email sending through Gmail, you must configure Google OAuth2 and place `credentials.json` in the project root.

#### 1. Access Google Cloud Console

- Go to `https://console.cloud.google.com/`
- Sign in with the Google account you want to use for sending emails

#### 2. Create a new project (or use an existing one)

- Click the project selector (top bar, next to "Google Cloud")
- Click **NEW PROJECT**
- Name it (e.g. "News Email Sender")
- Click **CREATE**

#### 3. Enable Gmail API

- Use the top search bar to search for **"Gmail API"**
- Click **Gmail API** from the results
- Click **ENABLE**

#### 4. Configure OAuth Consent Screen

- In the left menu, go to **APIs & Services → OAuth consent screen**
- Select **External** (for testing) or **Internal** (if you have Google Workspace)
- Click **CREATE**
- Fill in:
  - **App name**: e.g. "News Email Sender"
  - **User support email**: your email
  - **Developer contact information**: your email
- Click **SAVE AND CONTINUE**
- On **Scopes**, click **SAVE AND CONTINUE** (default scopes are fine)
- On **Test users**, click **ADD USERS** and add the email you will use to send mails
- Click **SAVE AND CONTINUE**
- On **Summary**, review and click **BACK TO DASHBOARD**

#### 5. Create OAuth 2.0 Credentials

- Go to **APIs & Services → Credentials**
- Click **CREATE CREDENTIALS** (top)
- Select **OAuth client ID**
- If you see an error about the consent screen, finish step 4 first
- For **Application type**, choose **Desktop app**
- Name it (e.g. "News Sender Desktop")
- Click **CREATE**
- A popup will show the Client ID and Client Secret
- Click **DOWNLOAD JSON**
- **Save the downloaded file as `credentials.json` in the project root folder**

#### 6. Verify the file structure

Your `credentials.json` should look like this:

```json
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

#### 7. Test the setup

- Run the script (with email sending enabled): `python main.py` or `uv run main.py`
- On first run, a browser window will open
- Log in with the Google account added as a test user
- Grant the requested permissions
- The application will automatically create `token.json` in the project root for future runs

#### Important notes

- In "Testing" mode, tokens may expire after a few days
- For production, you should publish the app from the Google Cloud Console
- Make sure `credentials.json` is in your `.gitignore` (never commit it to git!)

### Running the Script

You can run the main flow directly with uv:

```powershell
uv run main.py
```

By default, this will:
- Scrape news from `stiripesurse.ro`
- Generate an HTML analysis using OpenAI
- **Not** send any emails (HTML is generated only)

To send emails, you can either:

- Modify the `if __name__ == "__main__":` block in `main.py` to:

```python
run_daily_news_flow(send_email=True)
```

or

- Import and call `run_daily_news_flow` from another script with `send_email=True` and optionally pass a custom list of recipients:

```python
from main import run_daily_news_flow

run_daily_news_flow(send_email=True, recipients=["you@example.com"])
```

### Code Overview

- **`functions.scraping.scrape_stiripesurse`**: fetches and optionally formats the latest news from `stiripesurse.ro`.
- **`functions.scraping.scrape_biziday`**: fetches and optionally formats the latest news from `biziday.ro`.
- **`functions.ai_client.get_ai_info`**: sends the formatted news to OpenAI using the structured prompt in `config.prompts` and cleans the HTML response.
- **`functions.email_service.send_email_with_gmail`**: builds a multipart (plain + HTML) email and sends it via the Gmail API.
- **`main.run_daily_news_flow`**: coordinates scraping, AI analysis, and optional email sending using configuration from `config.settings`.

### Development Notes

- All configurable pieces (model name, max tokens, news URLs, Gmail file names, default subject, recipients) live in `config/__init__.py` and/or environment variables.
- Prompt details are isolated in `config/prompts.py` for easier iteration without touching core logic.
- Each module has a single responsibility, which simplifies testing and future extensions (e.g., adding more news sources or output channels).


