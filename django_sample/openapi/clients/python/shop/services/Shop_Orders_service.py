import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def api_shop_orders_list(
    customer: Optional[int] = None,
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedOrderListList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/shop/orders/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {
        "customer": customer,
        "ordering": ordering,
        "page": page,
        "search": search,
        "status": status,
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

    return PaginatedOrderListList(**response.json()) if response.json() is not None else PaginatedOrderListList()


def api_shop_orders_retrieve(id: int, api_config_override: Optional[APIConfig] = None) -> OrderDetail:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/shop/orders/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
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

    return OrderDetail(**response.json()) if response.json() is not None else OrderDetail()
