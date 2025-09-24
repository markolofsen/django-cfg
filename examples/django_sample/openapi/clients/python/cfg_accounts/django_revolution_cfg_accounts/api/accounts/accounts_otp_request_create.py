from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.otp_error_response import OTPErrorResponse
from ...models.otp_request_request import OTPRequestRequest
from ...models.otp_request_response import OTPRequestResponse
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        OTPRequestRequest,
        OTPRequestRequest,
        OTPRequestRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/accounts/otp/request/",
    }

    if isinstance(body, OTPRequestRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, OTPRequestRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, OTPRequestRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[OTPErrorResponse, OTPRequestResponse]]:
    if response.status_code == 200:
        response_200 = OTPRequestResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OTPErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = OTPErrorResponse.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[OTPErrorResponse, OTPRequestResponse]]:
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
        OTPRequestRequest,
        OTPRequestRequest,
        OTPRequestRequest,
    ],
) -> Response[Union[OTPErrorResponse, OTPRequestResponse]]:
    """Request OTP code to email or phone.

    Args:
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OTPErrorResponse, OTPRequestResponse]]
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
        OTPRequestRequest,
        OTPRequestRequest,
        OTPRequestRequest,
    ],
) -> Optional[Union[OTPErrorResponse, OTPRequestResponse]]:
    """Request OTP code to email or phone.

    Args:
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OTPErrorResponse, OTPRequestResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        OTPRequestRequest,
        OTPRequestRequest,
        OTPRequestRequest,
    ],
) -> Response[Union[OTPErrorResponse, OTPRequestResponse]]:
    """Request OTP code to email or phone.

    Args:
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OTPErrorResponse, OTPRequestResponse]]
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
        OTPRequestRequest,
        OTPRequestRequest,
        OTPRequestRequest,
    ],
) -> Optional[Union[OTPErrorResponse, OTPRequestResponse]]:
    """Request OTP code to email or phone.

    Args:
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.
        body (OTPRequestRequest): Serializer for OTP request.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OTPErrorResponse, OTPRequestResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
