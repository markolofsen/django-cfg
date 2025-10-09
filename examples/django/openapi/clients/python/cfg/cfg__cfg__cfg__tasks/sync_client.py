from __future__ import annotations

import httpx

from .models import *


class SyncCfgTasksAPI:
    """Synchronous API endpoints for Cfg Tasks."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def cfg_tasks_api_clear_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Clear all test data from Redis.
        """
        url = "/cfg/tasks/api/clear/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_clear_queues_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Clear all tasks from all Dramatiq queues.
        """
        url = "/cfg/tasks/api/clear-queues/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_purge_failed_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Purge all failed tasks from queues.
        """
        url = "/cfg/tasks/api/purge-failed/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_queues_manage_create(self, data: QueueActionRequest) -> QueueAction:
        """
        Manage queue operations (clear, purge, etc.).
        """
        url = "/cfg/tasks/api/queues/manage/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return QueueAction.model_validate(response.json())


    def cfg_tasks_api_queues_status_retrieve(self) -> QueueStatus:
        """
        Get current status of all queues.
        """
        url = "/cfg/tasks/api/queues/status/"
        response = self._client.get(url)
        response.raise_for_status()
        return QueueStatus.model_validate(response.json())


    def cfg_tasks_api_simulate_create(self, data: APIResponseRequest) -> APIResponse:
        """
        Simulate test data for dashboard testing.
        """
        url = "/cfg/tasks/api/simulate/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_tasks_list_retrieve(self) -> APIResponse:
        """
        Get paginated task list with filtering.
        """
        url = "/cfg/tasks/api/tasks/list/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_tasks_stats_retrieve(self) -> TaskStatistics:
        """
        Get task execution statistics.
        """
        url = "/cfg/tasks/api/tasks/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return TaskStatistics.model_validate(response.json())


    def cfg_tasks_api_workers_list_retrieve(self) -> APIResponse:
        """
        Get detailed list of workers.
        """
        url = "/cfg/tasks/api/workers/list/"
        response = self._client.get(url)
        response.raise_for_status()
        return APIResponse.model_validate(response.json())


    def cfg_tasks_api_workers_manage_create(self, data: WorkerActionRequest) -> WorkerAction:
        """
        Manage worker operations.
        """
        url = "/cfg/tasks/api/workers/manage/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return WorkerAction.model_validate(response.json())


