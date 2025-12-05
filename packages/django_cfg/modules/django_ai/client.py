"""
DjangoCFG Documentation Client.

HTTP client for accessing DjangoCFG documentation via MCP server API.
"""

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote_plus
from urllib.error import URLError, HTTPError

# SSL context without verification (for environments with cert issues)
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE


# API Configuration
MCP_BASE_URL = "https://mcp.djangocfg.com"
API_SEARCH_ENDPOINT = "/api/search"
API_INFO_ENDPOINT = "/api/info"
DEFAULT_TIMEOUT = 10  # seconds


@dataclass
class SearchResult:
    """Single search result from documentation."""
    title: str
    content: str
    url: str
    score: float = 0.0
    category: str = ""

    def __str__(self) -> str:
        return f"[{self.title}] {self.content[:100]}..."

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "score": self.score,
            "category": self.category,
        }


class DjangoCfgDocsClient:
    """
    Client for DjangoCFG Documentation API.

    Provides access to documentation search and info endpoints.

    Example:
        client = DjangoCfgDocsClient()
        results = client.search("database configuration")
        for r in results:
            print(r.title, r.url)
    """

    def __init__(
        self,
        base_url: str = MCP_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _make_request(self, endpoint: str, params: dict | None = None) -> dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        if params:
            url = f"{url}?{urlencode(params, quote_via=quote_plus)}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "DjangoCFG-AI-Client/1.0",
        }

        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=self.timeout, context=_ssl_context) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)
        except HTTPError as e:
            raise DocsClientError(f"HTTP Error {e.code}: {e.reason}") from e
        except URLError as e:
            raise DocsClientError(f"Connection error: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise DocsClientError(f"Invalid JSON response: {e}") from e

    def search(
        self,
        query: str,
        limit: int = 5,
        category: str | None = None
    ) -> list[SearchResult]:
        """
        Search documentation.

        Args:
            query: Search query string
            limit: Maximum number of results (default: 5)
            category: Optional category filter

        Returns:
            List of SearchResult objects
        """
        params = {"q": query, "limit": limit}
        if category:
            params["category"] = category

        data = self._make_request(API_SEARCH_ENDPOINT, params)

        results = []
        for item in data.get("results", data if isinstance(data, list) else []):
            results.append(SearchResult(
                title=item.get("title", ""),
                content=item.get("content", item.get("snippet", "")),
                url=item.get("url", ""),
                score=item.get("score", 0.0),
                category=item.get("category", ""),
            ))

        return results

    def get_info(self, topic: str) -> dict[str, Any]:
        """
        Get detailed info about a specific topic.

        Args:
            topic: Topic name (e.g., "DatabaseConfig", "CacheConfig")

        Returns:
            Dictionary with topic information
        """
        params = {"topic": topic}
        return self._make_request(API_INFO_ENDPOINT, params)

    def get_mcp_config(self) -> dict:
        """
        Get MCP server configuration for AI assistants.

        Returns:
            MCP configuration dictionary
        """
        return {
            "mcpServers": {
                "djangocfg-docs": {
                    "url": f"{self.base_url}/mcp"
                }
            }
        }


class DocsClientError(Exception):
    """Exception raised for documentation client errors."""
    pass


# Convenience functions
_default_client: DjangoCfgDocsClient | None = None


def _get_client() -> DjangoCfgDocsClient:
    """Get or create default client."""
    global _default_client
    if _default_client is None:
        _default_client = DjangoCfgDocsClient()
    return _default_client


def search(query: str, limit: int = 5) -> list[SearchResult]:
    """
    Search DjangoCFG documentation.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of SearchResult objects

    Example:
        >>> from django_cfg.modules.django_ai import search
        >>> results = search("database configuration")
        >>> for r in results:
        ...     print(r.title)
    """
    return _get_client().search(query, limit)


def get_docs(query: str, limit: int = 3) -> str:
    """
    Get documentation as formatted text.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        Formatted documentation string

    Example:
        >>> from django_cfg.modules.django_ai import get_docs
        >>> print(get_docs("How to configure PostgreSQL?"))
    """
    results = search(query, limit)

    if not results:
        return f"No documentation found for: {query}"

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"## {i}. {r.title}")
        output.append(r.content)
        if r.url:
            output.append(f"📖 Read more: {r.url}")
        output.append("")

    return "\n".join(output)


def get_info(topic: str) -> dict[str, Any]:
    """
    Get detailed info about a topic.

    Args:
        topic: Topic name

    Returns:
        Topic information dictionary
    """
    return _get_client().get_info(topic)
