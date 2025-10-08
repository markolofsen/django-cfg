from __future__ import annotations

from typing import Any, Optional

import httpx

from .shop__blog__blog_categories import ShopBlogCategoriesAPI
from .shop__blog__blog_comments import ShopBlogCommentsAPI
from .shop__blog__blog_posts import ShopBlogPostsAPI
from .shop__blog__blog_tags import ShopBlogTagsAPI
from .shop__shop__shop_categories import ShopCategoriesAPI
from .shop__shop__shop_orders import ShopOrdersAPI
from .shop__shop__shop_products import ShopProductsAPI
from .shop__blog import ShopBlogAPI
from .logger import APILogger, LoggerConfig
from .retry import RetryConfig, RetryAsyncClient


class APIClient:
    """
    Async API client for Django CFG Sample API.

    Usage:
        >>> async with APIClient(base_url='https://api.example.com') as client:
        ...     users = await client.users.list()
        ...     post = await client.posts.create(data=new_post)
        >>>
        >>> # With retry configuration
        >>> retry_config = RetryConfig(max_attempts=5, min_wait=2.0)
        >>> async with APIClient(base_url='https://api.example.com', retry_config=retry_config) as client:
        ...     users = await client.users.list()
    """

    def __init__(
        self,
        base_url: str,
        logger_config: Optional[LoggerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        **kwargs: Any,
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

        # Create HTTP client with or without retry
        if retry_config is not None:
            self._client = RetryAsyncClient(
                base_url=self.base_url,
                retry_config=retry_config,
                timeout=30.0,
                **kwargs,
            )
        else:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                **kwargs,
            )

        # Initialize logger
        self.logger: Optional[APILogger] = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.shop_blog_categories = ShopBlogCategoriesAPI(self._client)
        self.shop_blog_comments = ShopBlogCommentsAPI(self._client)
        self.shop_blog_posts = ShopBlogPostsAPI(self._client)
        self.shop_blog_tags = ShopBlogTagsAPI(self._client)
        self.shop_categories = ShopCategoriesAPI(self._client)
        self.shop_orders = ShopOrdersAPI(self._client)
        self.shop_products = ShopProductsAPI(self._client)
        self.shop_blog = ShopBlogAPI(self._client)

    async def __aenter__(self) -> 'APIClient':
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()