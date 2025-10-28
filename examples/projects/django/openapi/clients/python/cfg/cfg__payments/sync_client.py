from __future__ import annotations

import httpx

from .models import *


class SyncCfgPaymentsAPI:
    """Synchronous API endpoints for Payments."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def balance_retrieve(self) -> Balance:
        """
        Get user balance

        Get current user balance and transaction statistics
        """
        url = "/cfg/payments/balance/"
        response = self._client.get(url)
        response.raise_for_status()
        return Balance.model_validate(response.json())


    def currencies_list(self) -> None:
        """
        Get available currencies

        Returns list of available currencies with token+network info
        """
        url = "/cfg/payments/currencies/"
        response = self._client.get(url)
        response.raise_for_status()


    def payments_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedPaymentListList]:
        """
        ViewSet for payment operations. Endpoints: - GET /payments/ - List
        user's payments - GET /payments/{id}/ - Get payment details - POST
        /payments/create/ - Create new payment - GET /payments/{id}/status/ -
        Check payment status - POST /payments/{id}/confirm/ - Confirm payment
        """
        url = "/cfg/payments/payments/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedPaymentListList.model_validate(response.json())


    def payments_retrieve(self, id: str) -> PaymentDetail:
        """
        ViewSet for payment operations. Endpoints: - GET /payments/ - List
        user's payments - GET /payments/{id}/ - Get payment details - POST
        /payments/create/ - Create new payment - GET /payments/{id}/status/ -
        Check payment status - POST /payments/{id}/confirm/ - Confirm payment
        """
        url = f"/cfg/payments/payments/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return PaymentDetail.model_validate(response.json())


    def payments_confirm_create(self, id: str) -> PaymentList:
        """
        POST /api/v1/payments/{id}/confirm/ Confirm payment (user clicked "I
        have paid"). Checks status with provider and creates transaction if
        completed.
        """
        url = f"/cfg/payments/payments/{id}/confirm/"
        response = self._client.post(url)
        response.raise_for_status()
        return PaymentList.model_validate(response.json())


    def payments_status_retrieve(self, id: str) -> list[PaymentList]:
        """
        GET /api/v1/payments/{id}/status/?refresh=true Check payment status
        (with optional refresh from provider). Query params: - refresh: boolean
        (default: false) - Force refresh from provider
        """
        url = f"/cfg/payments/payments/{id}/status/"
        response = self._client.get(url)
        response.raise_for_status()
        return PaymentList.model_validate(response.json())


    def payments_create_create(self) -> PaymentList:
        """
        POST /api/v1/payments/create/ Create new payment. Request body: {
        "amount_usd": "100.00", "currency_code": "USDTTRC20", "description":
        "Optional description" }
        """
        url = "/cfg/payments/payments/create/"
        response = self._client.post(url)
        response.raise_for_status()
        return PaymentList.model_validate(response.json())


    def transactions_list(self, limit: int | None = None, offset: int | None = None, type: str | None = None) -> None:
        """
        Get user transactions

        Get user transactions with pagination and filtering
        """
        url = "/cfg/payments/transactions/"
        response = self._client.get(url, params={"limit": limit if limit is not None else None, "offset": offset if offset is not None else None, "type": type if type is not None else None})
        response.raise_for_status()


