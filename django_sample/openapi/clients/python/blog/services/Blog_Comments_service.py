import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def api_blog_comments_list(
    author: Optional[int] = None,
    is_approved: Optional[bool] = None,
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    parent: Optional[int] = None,
    post: Optional[int] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedCommentList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/comments/"

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
        "is_approved": is_approved,
        "ordering": ordering,
        "page": page,
        "parent": parent,
        "post": post,
    }

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PaginatedCommentList(**response.json()) if response.json() is not None else PaginatedCommentList()


def api_blog_comments_create(data: CommentRequest, api_config_override: Optional[APIConfig] = None) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/comments/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_comments_retrieve(id: int, api_config_override: Optional[APIConfig] = None) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_comments_update(id: int, data: CommentRequest, api_config_override: Optional[APIConfig] = None) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_comments_destroy(id: int, api_config_override: Optional[APIConfig] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None


def api_blog_posts_comments_list(
    post_slug: str,
    author: Optional[int] = None,
    is_approved: Optional[bool] = None,
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    parent: Optional[int] = None,
    post: Optional[int] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedCommentList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{post_slug}/comments/"

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
        "is_approved": is_approved,
        "ordering": ordering,
        "page": page,
        "parent": parent,
        "post": post,
    }

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return PaginatedCommentList(**response.json()) if response.json() is not None else PaginatedCommentList()


def api_blog_posts_comments_create(
    post_slug: str, data: CommentRequest, api_config_override: Optional[APIConfig] = None
) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{post_slug}/comments/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_posts_comments_retrieve(
    id: int, post_slug: str, api_config_override: Optional[APIConfig] = None
) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{post_slug}/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_posts_comments_update(
    id: int, post_slug: str, data: CommentRequest, api_config_override: Optional[APIConfig] = None
) -> Comment:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{post_slug}/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Comment(**response.json()) if response.json() is not None else Comment()


def api_blog_posts_comments_destroy(id: int, post_slug: str, api_config_override: Optional[APIConfig] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/blog/posts/{post_slug}/comments/{id}/"

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

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None
