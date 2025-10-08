from __future__ import annotations

from typing import Any, Optional

import httpx

from .shop__blog__blog_categories.sync_client import SyncShopBlogCategoriesAPI
from .shop__blog__blog_comments.sync_client import SyncShopBlogCommentsAPI
from .shop__blog__blog_posts.sync_client import SyncShopBlogPostsAPI
from .shop__blog__blog_tags.sync_client import SyncShopBlogTagsAPI
from .shop__shop__shop_categories.sync_client import SyncShopCategoriesAPI
from .shop__shop__shop_orders.sync_client import SyncShopOrdersAPI
from .shop__shop__shop_products.sync_client import SyncShopProductsAPI
from .shop__blog.sync_client import SyncShopBlogAPI
from .logger import APILogger, LoggerConfig
from .retry import RetryConfig, RetryAsyncClient


class SyncAPIClient:
    """
    Synchronous API client for Django CFG Sample API.

    Usage:
        >>> with SyncAPIClient(base_url='https://api.example.com') as client:
        ...     users = client.users.list()
        ...     post = client.posts.create(data=new_post)
    """

    def __init__(
        self,
        base_url: str,
        logger_config: Optional[LoggerConfig] = None,
        **kwargs: Any,
    ):
        """
        Initialize sync API client.

        Args:
            base_url: Base API URL (e.g., 'https://api.example.com')
            logger_config: Logger configuration (None to disable logging)
            **kwargs: Additional httpx.Client kwargs
        """
        self.base_url = base_url.rstrip('/')
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=30.0,
            **kwargs,
        )

        # Initialize logger
        self.logger: Optional[APILogger] = None
        if logger_config is not None:
            self.logger = APILogger(logger_config)

        # Initialize sub-clients
        self.shop_blog_categories = SyncShopBlogCategoriesAPI(self._client)
        self.shop_blog_comments = SyncShopBlogCommentsAPI(self._client)
        self.shop_blog_posts = SyncShopBlogPostsAPI(self._client)
        self.shop_blog_tags = SyncShopBlogTagsAPI(self._client)
        self.shop_categories = SyncShopCategoriesAPI(self._client)
        self.shop_orders = SyncShopOrdersAPI(self._client)
        self.shop_products = SyncShopProductsAPI(self._client)
        self.shop_blog = SyncShopBlogAPI(self._client)

    def __enter__(self) -> 'SyncAPIClient':
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.close()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()