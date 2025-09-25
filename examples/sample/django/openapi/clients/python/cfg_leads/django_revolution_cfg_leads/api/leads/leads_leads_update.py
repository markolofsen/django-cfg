from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.lead_submission import LeadSubmission
from ...models.lead_submission_request import LeadSubmissionRequest
from typing import cast


def _get_kwargs(
    id: int,
    *,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/leads/leads/{id}/".format(
            id=id,
        ),
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
) -> Optional[LeadSubmission]:
    if response.status_code == 200:
        response_200 = LeadSubmission.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[LeadSubmission]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Response[LeadSubmission]:
    """ViewSet for Lead model.

    Provides only submission functionality for leads from frontend forms.

    Args:
        id (int):
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LeadSubmission]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Optional[LeadSubmission]:
    """ViewSet for Lead model.

    Provides only submission functionality for leads from frontend forms.

    Args:
        id (int):
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LeadSubmission
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Response[LeadSubmission]:
    """ViewSet for Lead model.

    Provides only submission functionality for leads from frontend forms.

    Args:
        id (int):
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LeadSubmission]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient,
    body: Union[
        LeadSubmissionRequest,
        LeadSubmissionRequest,
        LeadSubmissionRequest,
    ],
) -> Optional[LeadSubmission]:
    """ViewSet for Lead model.

    Provides only submission functionality for leads from frontend forms.

    Args:
        id (int):
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.
        body (LeadSubmissionRequest): Serializer for lead form submission from frontend.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LeadSubmission
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
