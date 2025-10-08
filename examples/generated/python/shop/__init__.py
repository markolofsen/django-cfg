"""
Django CFG Sample API - API Client with JWT Management

Usage:
    >>> from api import API
    >>>
    >>> api = API('https://api.example.com')
    >>>
    >>> # Set JWT token
    >>> api.set_token('your-jwt-token', 'refresh-token')
    >>>
    >>> # Use API
    >>> async with api:
    ...     posts = await api.posts.list()
    ...     user = await api.users.retrieve(1)
    >>>
    >>> # Check authentication
    >>> if api.is_authenticated():
    ...     # ...
    >>>
    >>> # Get OpenAPI schema
    >>> schema = api.get_schema()
"""

from __future__ import annotations

import threading
from typing import Any

import httpx

from .client import APIClient
from .schema import OPENAPI_SCHEMA
from .logger import LoggerConfig
from .retry import RetryConfig
from .shop__blog__blog_categories import ShopBlogCategoriesAPI
from .shop__blog__blog_comments import ShopBlogCommentsAPI
from .shop__blog__blog_posts import ShopBlogPostsAPI
from .shop__blog__blog_tags import ShopBlogTagsAPI
from .shop__shop__shop_categories import ShopCategoriesAPI
from .shop__shop__shop_orders import ShopOrdersAPI
from .shop__shop__shop_products import ShopProductsAPI
from .shop__blog import ShopBlogAPI
from . import enums
from .enums import OrderDetail.status, OrderList.status, PatchedPostUpdateRequest.status, PostCreate.status, PostCreateRequest.status, PostDetail.status, PostDetailRequest.status, PostLike.reaction, PostList.status, PostUpdate.status, PostUpdateRequest.status, ProductDetail.status, ProductList.status

TOKEN_KEY = "auth_token"
REFRESH_TOKEN_KEY = "refresh_token"

class API:
    """
    API Client wrapper with JWT token management.

    This class provides:
    - Thread-safe JWT token storage
    - Automatic Authorization header injection
    - Context manager support for async operations
    - Optional retry and logging configuration

    Example:
        >>> api = API('https://api.example.com')
        >>> api.set_token('jwt-token')
        >>> async with api:
        ...     users = await api.users.list()
        >>>
        >>> # With retry and logging
        >>> api = API(
        ...     'https://api.example.com',
        ...     retry_config=RetryConfig(max_attempts=5),
        ...     logger_config=LoggerConfig(enabled=True)
        ... )
    """

    def __init__(
        self,
        base_url: str,
        logger_config: LoggerConfig | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Any
    ):
        """
        Initialize API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            retry_config: Retry configuration (None to disable retry)
            **kwargs: Additional httpx.AsyncClient kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._kwargs = kwargs
        self._logger_config = logger_config
        self._retry_config = retry_config
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._lock = threading.Lock()
        self._client: APIClient | None = None
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize API client with current token."""
        # Create httpx client with auth header if token exists
        headers = {}
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'

        kwargs = {**self._kwargs}
        if headers:
            kwargs['headers'] = headers

        # Create new APIClient
        self._client = APIClient(
            self.base_url,
            logger_config=self._logger_config,
            retry_config=self._retry_config,
            **kwargs
        )

    @property
    def shop_blog_categories(self) -> ShopBlogCategoriesAPI:
        """Access Blog - Categories endpoints."""
        return self._client.shop_blog_categories

    @property
    def shop_blog_comments(self) -> ShopBlogCommentsAPI:
        """Access Blog - Comments endpoints."""
        return self._client.shop_blog_comments

    @property
    def shop_blog_posts(self) -> ShopBlogPostsAPI:
        """Access Blog - Posts endpoints."""
        return self._client.shop_blog_posts

    @property
    def shop_blog_tags(self) -> ShopBlogTagsAPI:
        """Access Blog - Tags endpoints."""
        return self._client.shop_blog_tags

    @property
    def shop_categories(self) -> ShopCategoriesAPI:
        """Access Shop - Categories endpoints."""
        return self._client.shop_categories

    @property
    def shop_orders(self) -> ShopOrdersAPI:
        """Access Shop - Orders endpoints."""
        return self._client.shop_orders

    @property
    def shop_products(self) -> ShopProductsAPI:
        """Access Shop - Products endpoints."""
        return self._client.shop_products

    @property
    def shop_blog(self) -> ShopBlogAPI:
        """Access blog endpoints."""
        return self._client.shop_blog

    def get_token(self) -> str | None:
        """Get current JWT token."""
        with self._lock:
            return self._token

    def get_refresh_token(self) -> str | None:
        """Get current refresh token."""
        with self._lock:
            return self._refresh_token

    def set_token(self, token: str, refresh_token: str | None = None) -> None:
        """
        Set JWT token and refresh token.

        Args:
            token: JWT access token
            refresh_token: JWT refresh token (optional)
        """
        with self._lock:
            self._token = token
            if refresh_token:
                self._refresh_token = refresh_token

        # Reinitialize clients with new token
        self._init_clients()

    def clear_tokens(self) -> None:
        """Clear all tokens."""
        with self._lock:
            self._token = None
            self._refresh_token = None

        # Reinitialize clients without token
        self._init_clients()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.get_token() is not None

    def set_base_url(self, url: str) -> None:
        """
        Update base URL and reinitialize clients.

        Args:
            url: New base URL
        """
        self.base_url = url.rstrip('/')
        self._init_clients()

    def get_base_url(self) -> str:
        """Get current base URL."""
        return self.base_url

    def get_schema(self) -> dict[str, Any]:
        """
        Get OpenAPI schema.

        Returns:
            Complete OpenAPI specification for this API
        """
        return OPENAPI_SCHEMA

    async def __aenter__(self) -> 'API':
        """Async context manager entry."""
        if self._client:
            await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.close()

__all__ = [
    "API",
    "APIClient",
]