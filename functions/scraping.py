from __future__ import annotations

import re
from typing import Union

try:
    import requests
    from bs4 import BeautifulSoup

    SCRAPING_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SCRAPING_AVAILABLE = False

from config import settings


def _default_headers() -> dict:
    """Common HTTP headers for scraping requests."""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }


def scrape_stiripesurse(return_formatted: bool = False) -> Union[list, str]:
    """
    Scrape news from stiripesurse.ro and optionally format it.

    Returns:
        Either a list of article dicts or a formatted string.
    """
    if not SCRAPING_AVAILABLE:
        print(
            "Error: requests and BeautifulSoup not installed. "
            "Install with: pip install requests beautifulsoup4"
        )
        return [] if not return_formatted else ""

    url = settings.news.stiripesurse_url

    try:
        print("📰 Scraping news from stiripesurse.ro...")
        response = requests.get(url, headers=_default_headers(), timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Find articles
        articles: list[dict[str, str]] = []
        for article in soup.find_all("article")[: settings.news.max_articles]:
            title_elem = article.find(["h2", "h3", "a"])
            link_elem = article.find("a", href=True)

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.stiripesurse.ro" + link

                articles.append({"title": title, "link": link})

        print(f"✅ Found {len(articles)} articles")
        if return_formatted:
            formatted = "Știri din stiripesurse.ro:\n\n"
            for i, article in enumerate(articles, 1):
                formatted += f"{i}. {article['title']}\n   {article['link']}\n\n"
            return formatted

        return articles

    except Exception as e:  # pragma: no cover - network errors
        print(f"Error: {e}")
        return [] if not return_formatted else ""


def scrape_biziday(return_formatted: bool = False) -> Union[list, str]:
    """
    Scrape headlines from biziday.ro and optionally format them.

    The homepage groups multiple short, verified news items. We extract
    each bullet-like item as a separate "article" with title and link.

    Returns:
        Either a list of {"title": ..., "link": ...} dicts
        or a formatted string suitable for sending to the AI.
    """
    if not SCRAPING_AVAILABLE:
        print(
            "Error: requests and BeautifulSoup not installed. "
            "Install with: pip install requests beautifulsoup4"
        )
        return [] if not return_formatted else ""

    base_url = settings.news.biziday_url.rstrip("/")

    try:
        print("📰 Scraping news from biziday.ro...")

        articles: list[dict[str, str]] = []
        seen_keys: set[tuple[str, str]] = set()

        def extract_from_soup(soup: "BeautifulSoup") -> None:
            """Extract candidate items from a Biziday soup into the articles list."""
            # Heuristic 1: try to find the main "Știri verificate" (verified news) section
            verified_header = None
            for tag in soup.find_all(["h1", "h2", "h3", "strong"]):
                text = tag.get_text(strip=True)
                if "Știri verificate" in text:
                    verified_header = tag
                    break

            candidate_lis: list = []
            if verified_header:
                # Look for the first <ul> or container following the header
                next_container = verified_header.find_next(
                    ["ul", "div", "section"], recursive=False
                )
                if not next_container:
                    next_container = verified_header.find_next(
                        ["ul", "div", "section"]
                    )
                if next_container:
                    candidate_lis = next_container.find_all("li", recursive=True)

            # Fallback: if we didn't find a dedicated list, collect <li> items
            if not candidate_lis:
                candidate_lis = soup.find_all("li")

            for li in candidate_lis:
                # Skip menu / cookie / footer items heuristically
                parent_id = li.parent.get("id", "") if li.parent else ""
                parent_class = (
                    " ".join(li.parent.get("class", [])) if li.parent else ""
                )
                if any(
                    key in (parent_id + parent_class).lower()
                    for key in ["menu", "cookie", "footer", "privacy"]
                ):
                    continue

                text = li.get_text(" ", strip=True)
                if not text:
                    continue

                # Many Biziday bullets end with "Biziday · [date]"
                cleaned_text = re.sub(
                    r"Biziday\s*·\s*\d{4}-\d{2}-\d{2}.*$", "", text
                ).strip()
                cleaned_text = cleaned_text or text

                # Extract first link if present
                link_tag = li.find("a", href=True)
                link = link_tag["href"].strip() if link_tag else base_url
                if link and not link.startswith("http"):
                    # Make relative URLs absolute
                    link = base_url + "/" + link.lstrip("/")

                key = (cleaned_text, link)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                articles.append({"title": cleaned_text, "link": link})

                if len(articles) >= settings.news.max_articles:
                    return

        # Biziday usually uses pagination like /page/2/, /page/3/ etc.
        max_pages = 8  # roughly equivalent to 7–8 "More news" clicks
        for page in range(1, max_pages + 1):
            if len(articles) >= settings.news.max_articles:
                break

            if page == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}/page/{page}/"

            try:
                response = requests.get(page_url, headers=_default_headers(), timeout=10)
                response.raise_for_status()
            except Exception as e:  # pragma: no cover - network errors
                print(f"Error fetching Biziday page {page}: {e}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            extract_from_soup(soup)

        print(f"✅ Found {len(articles)} Biziday items")

        if return_formatted:
            formatted = "Știri din biziday.ro (Știri verificate):\n\n"
            for i, article in enumerate(articles, 1):
                formatted += f"{i}. {article['title']}\n   {article['link']}\n\n"
            return formatted

        return articles

    except Exception as e:  # pragma: no cover - network errors
        print(f"Error scraping biziday.ro: {e}")
        return [] if not return_formatted else ""


def scrape_web(url: str) -> dict:
    """
    Scrape content from an arbitrary URL and extract basic information.

    Returns:
        dict with title, text, and links.
    """
    if not SCRAPING_AVAILABLE:
        print("Error: requests and BeautifulSoup not installed")
        return {"title": "", "text": "", "links": []}

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        # Get title
        title = soup.title.string if soup.title else url

        # Get links
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True)
            if link_text:
                links.append({"href": href[:50], "text": link_text[:60]})

        print(f"Title: {title}")
        print(f"Found {len(soup.find_all('h1'))} h1 tags")
        print(f"Found {len(soup.find_all('h2'))} h2 tags")
        print(f"Found {len(soup.find_all('h3'))} h3 tags")
        print(f"Found {len(soup.find_all('a', href=True))} links")

        print("\nFirst 10 links:")
        for link in links[:10]:
            print(f" {link['href']:50} -> {link['text'][:60]}")

        return {"title": title, "text": text, "links": links}

    except Exception as e:  # pragma: no cover - network errors
        print(f"Error: {e}")
        return {"title": "", "text": "", "links": []}



