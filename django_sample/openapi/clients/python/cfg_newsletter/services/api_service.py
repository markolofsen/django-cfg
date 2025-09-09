import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def api_newsletter_campaigns_partial_update(
    id: int, data: PatchedNewsletterCampaignRequest, api_config_override: Optional[APIConfig] = None
) -> NewsletterCampaign:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/newsletter/campaigns/{id}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("patch", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return NewsletterCampaign(**response.json()) if response.json() is not None else NewsletterCampaign()


def api_newsletter_unsubscribe_update(
    data: UnsubscribeRequest, api_config_override: Optional[APIConfig] = None
) -> Unsubscribe:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/newsletter/unsubscribe/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Unsubscribe(**response.json()) if response.json() is not None else Unsubscribe()


def api_newsletter_unsubscribe_partial_update(
    data: PatchedUnsubscribeRequest, api_config_override: Optional[APIConfig] = None
) -> Unsubscribe:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/newsletter/unsubscribe/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("patch", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return Unsubscribe(**response.json()) if response.json() is not None else Unsubscribe()
