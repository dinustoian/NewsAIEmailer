import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class AIConfig:
    """Configuration for the OpenAI client and news analysis."""

    model: str = "gpt-5-mini"
    # gpt-5-mini does not support temperature; keep for compatibility but unused.
    temperature: float | None = None
    # Maximum number of completion tokens to generate from the model.
    max_completion_tokens: int = 32000


@dataclass
class NewsConfig:
    """Configuration for news scraping."""

    stiripesurse_url: str = "https://www.stiripesurse.ro/"
    biziday_url: str = "https://www.biziday.ro/"
    max_articles: int = 150


@dataclass
class GmailConfig:
    """Configuration for Gmail sending."""

    credentials_file: str = "credentials.json"
    token_file: str = "token.json"
    default_subject: str = "Știri de astăzi - Analiză AI"


class Settings:
    """Global application settings with environment loading."""

    def __init__(self) -> None:
        # Load environment variables from `.env` if present
        load_dotenv(override=True)

        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

        # Optional: comma-separated list of recipients
        recipients_env = os.getenv("EMAIL_RECIPIENTS", "").strip()
        self.email_recipients: list[str] = (
            [email.strip() for email in recipients_env.split(",") if email.strip()]
            if recipients_env
            else []
        )

        self.ai = AIConfig()
        self.news = NewsConfig()
        self.gmail = GmailConfig()


# Singleton-like settings instance for convenient imports
settings = Settings()



