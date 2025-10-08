from __future__ import annotations

import httpx

from .models import *


class CfgTasksAPI:
    """API endpoints for Tasks."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def api_clear_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Clear all test data from Redis.
        """
        url = "/tasks/api/clear/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_clear_queues_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Clear all tasks from all Dramatiq queues.
        """
        url = "/tasks/api/clear-queues/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_purge_failed_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Purge all failed tasks from queues.
        """
        url = "/tasks/api/purge-failed/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_queues_manage_create(self, data: QueueActionRequest) -> QueueAction:
        """
        Manage queue operations (clear, purge, etc.).
        """
        url = "/tasks/api/queues/manage/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return QueueAction.model_validate(response.json())


    async def api_queues_status_retrieve(self) -> QueueStatus:
        """
        Get current status of all queues.
        """
        url = "/tasks/api/queues/status/"
        response = await self._client.get(url)
        response.raise_for_status()
        return QueueStatus.model_validate(response.json())


    async def api_simulate_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Simulate test data for dashboard testing.
        """
        url = "/tasks/api/simulate/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_tasks_list_retrieve(self) -> APIResponse:
        """
        Get paginated task list with filtering.
        """
        url = "/tasks/api/tasks/list/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_tasks_stats_retrieve(self) -> TaskStatistics:
        """
        Get task execution statistics.
        """
        url = "/tasks/api/tasks/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return TaskStatistics.model_validate(response.json())


    async def api_workers_list_retrieve(self) -> APIResponse:
        """
        Get detailed list of workers.
        """
        url = "/tasks/api/workers/list/"
        response = await self._client.get(url)
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    async def api_workers_manage_create(self, data: WorkerActionRequest) -> WorkerAction:
        """
        Manage worker operations.
        """
        url = "/tasks/api/workers/manage/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return WorkerAction.model_validate(response.json())


