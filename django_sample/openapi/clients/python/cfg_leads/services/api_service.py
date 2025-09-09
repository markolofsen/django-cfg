import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def api_leads_leads_list(
    ordering: Optional[str] = None,
    page: Optional[int] = None,
    search: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> PaginatedLeadSubmissionList:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {"ordering": ordering, "page": page, "search": search}

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

    return (
        PaginatedLeadSubmissionList(**response.json()) if response.json() is not None else PaginatedLeadSubmissionList()
    )


def api_leads_leads_create(
    data: LeadSubmissionRequest, api_config_override: Optional[APIConfig] = None
) -> LeadSubmission:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LeadSubmission(**response.json()) if response.json() is not None else LeadSubmission()


def api_leads_leads_retrieve(id: int, api_config_override: Optional[APIConfig] = None) -> LeadSubmission:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/{id}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

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

    return LeadSubmission(**response.json()) if response.json() is not None else LeadSubmission()


def api_leads_leads_update(
    id: int, data: LeadSubmissionRequest, api_config_override: Optional[APIConfig] = None
) -> LeadSubmission:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/{id}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("put", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LeadSubmission(**response.json()) if response.json() is not None else LeadSubmission()


def api_leads_leads_destroy(id: int, api_config_override: Optional[APIConfig] = None) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/{id}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None


def api_leads_leads_partial_update(
    id: int, data: PatchedLeadSubmissionRequest, api_config_override: Optional[APIConfig] = None
) -> LeadSubmission:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/leads/leads/{id}/"

    # Build headers - only add Authorization if token is available
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Only add Authorization header if token is available
    access_token = api_config.get_access_token()
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("patch", httpx.URL(path), headers=headers, params=query_params, json=data.dict())

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LeadSubmission(**response.json()) if response.json() is not None else LeadSubmission()
