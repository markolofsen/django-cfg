"""
Testing Service.

Provides business logic for gRPC testing operations.
"""

from typing import Dict, List, Optional

from django.db import models
from django.db.models import Count
from django_cfg.modules.django_logging import get_logger

from ..models import GRPCRequestLog
from ..testing import get_example
from .service_registry import ServiceRegistryManager

logger = get_logger("grpc.testing_service")


class TestingService:
    """
    Service for gRPC testing operations.

    Provides methods to retrieve test examples, logs, and execute test calls.
    """

    def __init__(self):
        """Initialize testing service with registry manager."""
        self.registry = ServiceRegistryManager()

    def get_examples(
        self,
        service_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get example payloads for testing gRPC methods.

        Args:
            service_filter: Filter by service name
            method_filter: Filter by method name

        Returns:
            List of example dictionaries

        Example:
            >>> service = TestingService()
            >>> examples = service.get_examples(service_filter='CryptoService')
            >>> examples[0]['method']
            'GetCoin'
        """
        # Get registered services from service registry
        services = self.registry.get_all_services()

        examples = []
        for service in services:
            service_name = service.get("class_name", "")
            if not service_name:
                continue

            # Filter by service if specified
            if service_filter and service_name != service_filter:
                continue

            for method_name in service.get("methods", []):
                # Filter by method if specified
                if method_filter and method_name != method_filter:
                    continue

                # Get example from registry
                example_data = get_example(service_name, method_name)
                if example_data:
                    # Build dict directly
                    example = {
                        "service": service_name,
                        "method": method_name,
                        "description": example_data.get(
                            "description", f"{method_name} method"
                        ),
                        "payload_example": example_data.get("request", {}),
                        "expected_response": example_data.get("response", {}),
                        "metadata_example": example_data.get("metadata", {}),
                    }
                    examples.append(example)

        return examples

    def get_test_logs(
        self,
        service_filter: Optional[str] = None,
        method_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
    ):
        """
        Get test logs queryset for gRPC calls.

        Args:
            service_filter: Filter by service name
            method_filter: Filter by method name
            status_filter: Filter by status (success/error)

        Returns:
            Queryset of GRPCRequestLog (pagination handled by DRF)

        Example:
            >>> service = TestingService()
            >>> queryset = service.get_test_logs(status_filter='error')
            >>> queryset.count()
            25
        """
        # Build queryset with filters
        queryset = GRPCRequestLog.objects.all()

        if service_filter:
            queryset = queryset.filter(service_name__icontains=service_filter)
        if method_filter:
            queryset = queryset.filter(method_name__icontains=method_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    def get_test_statistics(self) -> Dict:
        """
        Get overall test statistics.

        Returns:
            Dictionary with test statistics

        Example:
            >>> service = TestingService()
            >>> stats = service.get_test_statistics()
            >>> stats['total_tests']
            1000
        """
        # Get overall stats
        stats = GRPCRequestLog.objects.aggregate(
            total_tests=Count("id"),
            successful=Count("id", filter=models.Q(status="success")),
            errors=Count("id", filter=models.Q(status="error")),
        )

        total = stats["total_tests"] or 0
        successful = stats["successful"] or 0
        success_rate = (successful / total * 100) if total > 0 else 0.0

        return {
            "total_tests": total,
            "successful": successful,
            "errors": stats["errors"] or 0,
            "success_rate": round(success_rate, 2),
        }

    def call_method(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict,
        metadata: Optional[Dict] = None,
        timeout: Optional[float] = None,
    ) -> Dict:
        """
        Call a gRPC method for testing using dynamic invocation.

        Args:
            service_name: Service name (e.g., 'apps.CryptoService')
            method_name: Method name (e.g., 'GetCoin')
            request_data: Request payload as dictionary
            metadata: Optional metadata (headers)
            timeout: Timeout in seconds (default: 5.0)

        Returns:
            Dictionary with call result (to be wrapped by view layer):
            {
                'success': bool,
                'service': str,
                'method': str,
                'duration_ms': int,
                'grpc_status_code': str,
                'response': dict (if success) or None,
                'error_message': str (if error) or None,
            }

        Example:
            >>> service = TestingService()
            >>> response = service.call_method(
            ...     service_name='apps.CryptoService',
            ...     method_name='GetCoin',
            ...     request_data={'symbol': 'BTC'},
            ...     timeout=5.0
            ... )
            >>> response['success']
            True
            >>> response['response']
            {'coin': {'symbol': 'BTC', 'price': 50000.0}}
        """
        import grpc
        from time import time

        from .grpc_client import DynamicGRPCClient
        from .config_helper import get_grpc_server_config

        # Get gRPC server config
        grpc_config = get_grpc_server_config()
        host = getattr(grpc_config, "host", "localhost")
        port = getattr(grpc_config, "port", 50051)

        # Set default timeout
        if timeout is None:
            timeout = 5.0

        logger.info(f"Calling gRPC method: {service_name}.{method_name}")

        start_time = time()

        try:
            # Create dynamic client and make the call
            with DynamicGRPCClient(host=host, port=port) as client:
                response_data = client.call_method(
                    service_name=service_name,
                    method_name=method_name,
                    request_data=request_data,
                    metadata=metadata,
                    timeout=timeout,
                )

            end_time = time()
            duration_ms = int((end_time - start_time) * 1000)

            logger.info(
                f"gRPC call successful: {service_name}.{method_name} " f"({duration_ms}ms)"
            )

            # Return success response (view layer will add request_id, status, timestamp)
            return {
                "success": True,
                "service": service_name,
                "method": method_name,
                "duration_ms": duration_ms,
                "grpc_status_code": "OK",
                "response": response_data,
                "error_message": None,
            }

        except grpc.RpcError as e:
            # Handle gRPC errors
            end_time = time()
            duration_ms = int((end_time - start_time) * 1000)

            logger.error(
                f"gRPC call failed: {service_name}.{method_name} - "
                f"{e.code()}: {e.details()} ({duration_ms}ms)"
            )

            return {
                "success": False,
                "service": service_name,
                "method": method_name,
                "duration_ms": duration_ms,
                "grpc_status_code": e.code().name,
                "response": None,
                "error_message": e.details() or f"gRPC error: {e.code()}",
            }

        except ConnectionError as e:
            # Handle connection errors
            end_time = time()
            duration_ms = int((end_time - start_time) * 1000)

            logger.error(
                f"Cannot connect to gRPC server: {host}:{port} - {e} ({duration_ms}ms)"
            )

            return {
                "success": False,
                "service": service_name,
                "method": method_name,
                "duration_ms": duration_ms,
                "grpc_status_code": "UNAVAILABLE",
                "response": None,
                "error_message": f"Cannot connect to gRPC server: {e}",
            }

        except ValueError as e:
            # Handle validation errors (service/method not found, invalid request data)
            end_time = time()
            duration_ms = int((end_time - start_time) * 1000)

            logger.error(f"Validation error: {e} ({duration_ms}ms)")

            return {
                "success": False,
                "service": service_name,
                "method": method_name,
                "duration_ms": duration_ms,
                "grpc_status_code": "INVALID_ARGUMENT",
                "response": None,
                "error_message": str(e),
            }

        except Exception as e:
            # Handle unexpected errors
            end_time = time()
            duration_ms = int((end_time - start_time) * 1000)

            logger.error(
                f"Unexpected error calling gRPC method: {e} ({duration_ms}ms)", exc_info=True
            )

            return {
                "success": False,
                "service": service_name,
                "method": method_name,
                "duration_ms": duration_ms,
                "grpc_status_code": "INTERNAL",
                "response": None,
                "error_message": f"Internal error: {str(e)}",
            }


__all__ = ["TestingService"]
