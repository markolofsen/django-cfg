from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.category import Category
from ...models.patched_category_request import PatchedCategoryRequest
from typing import cast


def _get_kwargs(
    slug: str,
    *,
    body: Union[
        PatchedCategoryRequest,
        PatchedCategoryRequest,
        PatchedCategoryRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/blog/categories/{slug}/".format(
            slug=slug,
        ),
    }

    if isinstance(body, PatchedCategoryRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, PatchedCategoryRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, PatchedCategoryRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Category]:
    if response.status_code == 200:
        response_200 = Category.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Category]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCategoryRequest,
        PatchedCategoryRequest,
        PatchedCategoryRequest,
    ],
) -> Response[Category]:
    """ViewSet for blog categories.

    Args:
        slug (str):
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Category]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCategoryRequest,
        PatchedCategoryRequest,
        PatchedCategoryRequest,
    ],
) -> Optional[Category]:
    """ViewSet for blog categories.

    Args:
        slug (str):
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Category
    """

    return sync_detailed(
        slug=slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCategoryRequest,
        PatchedCategoryRequest,
        PatchedCategoryRequest,
    ],
) -> Response[Category]:
    """ViewSet for blog categories.

    Args:
        slug (str):
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Category]
    """

    kwargs = _get_kwargs(
        slug=slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    slug: str,
    *,
    client: AuthenticatedClient,
    body: Union[
        PatchedCategoryRequest,
        PatchedCategoryRequest,
        PatchedCategoryRequest,
    ],
) -> Optional[Category]:
    """ViewSet for blog categories.

    Args:
        slug (str):
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.
        body (PatchedCategoryRequest): Serializer for blog categories.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Category
    """

    return (
        await asyncio_detailed(
            slug=slug,
            client=client,
            body=body,
        )
    ).parsed
