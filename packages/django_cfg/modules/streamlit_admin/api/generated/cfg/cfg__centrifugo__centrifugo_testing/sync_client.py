from __future__ import annotations

import httpx

from .models import (
    ManualAckRequestRequest,
    ManualAckResponse,
    PublishTestRequestRequest,
    PublishTestResponse,
)


class SyncCfgCentrifugoTestingAPI:
    """Synchronous API endpoints for Centrifugo Testing."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def publish_test_create(self, data: PublishTestRequestRequest) -> PublishTestResponse:
        """
        Publish test message

        Publish test message to Centrifugo via wrapper with optional ACK
        tracking.
        """
        url = "/cfg/centrifugo/testing/publish-test/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PublishTestResponse.model_validate(response.json())


    def publish_with_logging_create(
        self,
        data: PublishTestRequestRequest,
    ) -> PublishTestResponse:
        """
        Publish with database logging

        Publish message using CentrifugoClient with database logging. This will
        create CentrifugoLog records.
        """
        url = "/cfg/centrifugo/testing/publish-with-logging/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PublishTestResponse.model_validate(response.json())


    def send_ack_create(self, data: ManualAckRequestRequest) -> ManualAckResponse:
        """
        Send manual ACK

        Manually send ACK for a message to the wrapper. Pass message_id in
        request body.
        """
        url = "/cfg/centrifugo/testing/send-ack/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return ManualAckResponse.model_validate(response.json())


