from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.lead_submission_error import LeadSubmissionError
from ...models.lead_submission_request import LeadSubmissionRequest
from ...models.lead_submission_response import LeadSubmissionResponse
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/leads/leads/submit/",
    }

    if isinstance(body, LeadSubmissionRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, LeadSubmissionRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, LeadSubmissionRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    if response.status_code == 201:
        response_201 = LeadSubmissionResponse.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = LeadSubmissionError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Response[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    """Submit Lead Form

     Submit a new lead from frontend contact form with automatic Telegram notifications.

    Args:
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[LeadSubmissionError, LeadSubmissionResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Optional[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    """Submit Lead Form

     Submit a new lead from frontend contact form with automatic Telegram notifications.

    Args:
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[LeadSubmissionError, LeadSubmissionResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Response[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    """Submit Lead Form

     Submit a new lead from frontend contact form with automatic Telegram notifications.

    Args:
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[LeadSubmissionError, LeadSubmissionResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Optional[Union[LeadSubmissionError, LeadSubmissionResponse]]:
    """Submit Lead Form

     Submit a new lead from frontend contact form with automatic Telegram notifications.

    Args:
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[LeadSubmissionError, LeadSubmissionResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
