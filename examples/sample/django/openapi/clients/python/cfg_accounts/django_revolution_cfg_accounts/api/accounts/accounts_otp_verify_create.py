from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.otp_error_response import OTPErrorResponse
from ...models.otp_verify_request import OTPVerifyRequest
from ...models.otp_verify_response import OTPVerifyResponse
from typing import cast


def _get_kwargs(
    *,
    body: Union[
        OTPVerifyRequest,
        OTPVerifyRequest,
        OTPVerifyRequest,
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/accounts/otp/verify/",
    }

    if isinstance(body, OTPVerifyRequest):
        _kwargs["json"] = body.to_dict()

        headers["Content-Type"] = "application/json"
    if isinstance(body, OTPVerifyRequest):
        _kwargs["data"] = body.to_dict()

        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if isinstance(body, OTPVerifyRequest):
        _kwargs["files"] = body.to_multipart()

        headers["Content-Type"] = "multipart/form-data"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[OTPErrorResponse, OTPVerifyResponse]]:
    if response.status_code == 200:
        response_200 = OTPVerifyResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OTPErrorResponse.from_dict(response.json())

        return response_400

    if response.status_code == 410:
        response_410 = OTPErrorResponse.from_dict(response.json())

        return response_410

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[OTPErrorResponse, OTPVerifyResponse]]:
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
        OTPVerifyRequest,
        OTPVerifyRequest,
        OTPVerifyRequest,
    ],
) -> Response[Union[OTPErrorResponse, OTPVerifyResponse]]:
    """Verify OTP code and return JWT tokens.

    Args:
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OTPErrorResponse, OTPVerifyResponse]]
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
        OTPVerifyRequest,
        OTPVerifyRequest,
        OTPVerifyRequest,
    ],
) -> Optional[Union[OTPErrorResponse, OTPVerifyResponse]]:
    """Verify OTP code and return JWT tokens.

    Args:
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OTPErrorResponse, OTPVerifyResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: Union[
        OTPVerifyRequest,
        OTPVerifyRequest,
        OTPVerifyRequest,
    ],
) -> Response[Union[OTPErrorResponse, OTPVerifyResponse]]:
    """Verify OTP code and return JWT tokens.

    Args:
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[OTPErrorResponse, OTPVerifyResponse]]
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
        OTPVerifyRequest,
        OTPVerifyRequest,
        OTPVerifyRequest,
    ],
) -> Optional[Union[OTPErrorResponse, OTPVerifyResponse]]:
    """Verify OTP code and return JWT tokens.

    Args:
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.
        body (OTPVerifyRequest): Serializer for OTP verification.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[OTPErrorResponse, OTPVerifyResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
