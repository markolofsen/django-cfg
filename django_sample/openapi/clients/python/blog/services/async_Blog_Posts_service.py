import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


async def api_blog_posts_list(
    author: Optional[int] = None,
    category: Optional[int] = None,
    is_featured: Optional[bool] = None,
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[int]] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedPostListList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {
        "author": author,
        "category": category,
        "is_featured": is_featured,
        "ordering": ordering,
        "page": page,
        "search": search,
        "status": status,
        "tags": tags,
    }

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PaginatedPostListList(**response.json()) if response.json() is not None else PaginatedPostListList()


async def api_blog_posts_create(data: PostCreateRequest, api_config_override: Optional[APIConfig] = None) -> PostCreate:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PostCreate(**response.json()) if response.json() is not None else PostCreate()


async def api_blog_posts_retrieve(slug: str, api_config_override: Optional[APIConfig] = None) -> PostDetail:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{slug}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PostDetail(**response.json()) if response.json() is not None else PostDetail()


async def api_blog_posts_update(
    slug: str, data: PostUpdateRequest, api_config_override: Optional[APIConfig] = None
) -> PostUpdate:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{slug}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PostUpdate(**response.json()) if response.json() is not None else PostUpdate()


async def api_blog_posts_destroy(slug: str, api_config_override: Optional[APIConfig] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{slug}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None


async def api_blog_posts_like_create(
    slug: str, data: PostDetailRequest, api_config_override: Optional[APIConfig] = None
) -> PostDetail:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{slug}/like/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PostDetail(**response.json()) if response.json() is not None else PostDetail()


async def api_blog_posts_likes_list(
    slug: str,
    author: Optional[int] = None,
    category: Optional[int] = None,
    is_featured: Optional[bool] = None,
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[int]] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedPostLikeList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{slug}/likes/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {
        "author": author,
        "category": category,
        "is_featured": is_featured,
        "ordering": ordering,
        "page": page,
        "search": search,
        "status": status,
        "tags": tags,
    }

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PaginatedPostLikeList(**response.json()) if response.json() is not None else PaginatedPostLikeList()


async def api_blog_posts_featured_retrieve(api_config_override: Optional[APIConfig] = None) -> PostDetail:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/featured/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PostDetail(**response.json()) if response.json() is not None else PostDetail()


async def api_blog_posts_stats_retrieve(api_config_override: Optional[APIConfig] = None) -> BlogStats:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/stats/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    async with httpx.AsyncClient(base_url=base_path, verify=api_config.verify) as client:
        response = await client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return BlogStats(**response.json()) if response.json() is not None else BlogStats()
