from __future__ import annotations

import httpx

from .models import *


class CryptoCryptoAPI:
    """API endpoints for Crypto."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def coins_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedCoinListList]:
        """
        List coins

        ViewSet for cryptocurrency coins.
        """
        url = "/api/crypto/coins/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedCoinListList.model_validate(response.json())


    async def coins_retrieve(self, id: int) -> Coin:
        """
        Get coin details

        ViewSet for cryptocurrency coins.
        """
        url = f"/api/crypto/coins/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Coin.model_validate(response.json())


    async def coins_stats_retrieve(self) -> CoinStats:
        """
        Get coin statistics

        Get cryptocurrency statistics.
        """
        url = "/api/crypto/coins/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return CoinStats.model_validate(response.json())


    async def exchanges_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedExchangeList]:
        """
        List exchanges

        ViewSet for cryptocurrency exchanges.
        """
        url = "/api/crypto/exchanges/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedExchangeList.model_validate(response.json())


    async def exchanges_retrieve(self, slug: str) -> Exchange:
        """
        Get exchange details

        ViewSet for cryptocurrency exchanges.
        """
        url = f"/api/crypto/exchanges/{slug}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Exchange.model_validate(response.json())


    async def wallets_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedWalletList]:
        """
        List wallets

        ViewSet for user wallets.
        """
        url = "/api/crypto/wallets/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        return PaginatedWalletList.model_validate(response.json())


    async def wallets_retrieve(self, id: str) -> Wallet:
        """
        Get wallet details

        ViewSet for user wallets.
        """
        url = f"/api/crypto/wallets/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return Wallet.model_validate(response.json())


