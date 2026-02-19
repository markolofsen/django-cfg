from __future__ import annotations

import httpx

from .models import (
    CfgRqTestingScheduleDemoCreateRequest,
    RunDemoRequestRequest,
    StressTestRequestRequest,
    TestScenario,
    TestingActionResponse,
)


class SyncCfgRqTestingAPI:
    """Synchronous API endpoints for RQ Testing."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def list(self) -> list[TestScenario]:
        """
        List test scenarios

        Returns list of all available test scenarios with metadata.
        """
        url = "/cfg/rq/testing/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [TestScenario.model_validate(item) for item in response.json()]


    def cleanup_destroy(
        self,
        delete_demo_jobs_only: bool | None = None,
        queue: str | None = None,
        registries: str | None = None,
    ) -> TestingActionResponse:
        """
        Cleanup test jobs

        Clean demo jobs from registries.
        """
        url = "/cfg/rq/testing/cleanup/"
        _params = {
            k: v for k, v in {
                "delete_demo_jobs_only": delete_demo_jobs_only,
                "queue": queue,
                "registries": registries,
            }.items() if v is not None
        }
        response = self._client.delete(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return TestingActionResponse.model_validate(response.json())


    def results_retrieve(
        self,
        queue: str | None = None,
        scenario: str | None = None,
    ) -> None:
        """
        Get test results

        Get aggregated results of test jobs execution.
        """
        url = "/cfg/rq/testing/results/"
        _params = {
            k: v for k, v in {
                "queue": queue,
                "scenario": scenario,
            }.items() if v is not None
        }
        response = self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def run_demo_create(self, data: RunDemoRequestRequest) -> TestingActionResponse:
        """
        Run demo task

        Enqueue a single demo task for testing.
        """
        url = "/cfg/rq/testing/run-demo/"
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
        return TestingActionResponse.model_validate(response.json())


    def schedule_demo_create(
        self,
        data: CfgRqTestingScheduleDemoCreateRequest,
    ) -> TestingActionResponse:
        """
        Schedule demo tasks

        Register demo scheduled tasks using rq-scheduler.
        """
        url = "/cfg/rq/testing/schedule-demo/"
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
        return TestingActionResponse.model_validate(response.json())


    def stress_test_create(self, data: StressTestRequestRequest) -> TestingActionResponse:
        """
        Stress test

        Generate N jobs for load testing and performance benchmarking.
        """
        url = "/cfg/rq/testing/stress-test/"
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
        return TestingActionResponse.model_validate(response.json())


