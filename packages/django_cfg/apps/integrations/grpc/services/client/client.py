"""
Dynamic gRPC Client using Reflection API.

Allows calling gRPC methods without importing generated stubs.
Uses gRPC Server Reflection to discover services and methods dynamically.
"""

from __future__ import annotations

import grpc
from typing import Any, Dict, Optional, TYPE_CHECKING

from google.protobuf import descriptor_pb2, descriptor_pool, json_format, message_factory

# Try v1alpha first, fallback to v1 if needed
try:
    from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc
except ImportError:
    from grpc_reflection.v1 import reflection_pb2, reflection_pb2_grpc

from django_cfg.utils import get_logger

# Import configuration classes
from ...configs.channels import ClientChannelConfig
from ...configs.tls import TLSConfig
from ...configs.constants import (
    GRPC_DEFAULT_HOST,
    GRPC_DEFAULT_PORT,
    GRPC_CHANNEL_READY_TIMEOUT,
    GRPC_RPC_CALL_TIMEOUT,
)

if TYPE_CHECKING:
    pass

logger = get_logger("grpc.dynamic_client")


class DynamicGRPCClient:
    """
    Dynamic gRPC client using server reflection.

    Features:
    - Discovers services and methods dynamically
    - Creates protobuf messages from JSON
    - Invokes methods without compiled stubs
    - Handles unary-unary methods (streaming support can be added)
    - Configurable via ClientChannelConfig and TLSConfig

    Usage:
        >>> client = DynamicGRPCClient(host='localhost', port=50051)
        >>> response = client.call_method(
        ...     service='apps.CryptoService',
        ...     method='GetCoin',
        ...     request_data={'symbol': 'BTC'}
        ... )
        >>> print(response)
        {'coin': {'symbol': 'BTC', 'price': 50000.0}}

        # With configuration
        >>> config = ClientChannelConfig(
        ...     address="grpc.example.com:443",
        ...     use_tls=True,
        ...     max_retries=5,
        ... )
        >>> client = DynamicGRPCClient(config=config)
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        use_tls: bool = None,
        config: ClientChannelConfig = None,
        tls_config: TLSConfig = None,
    ):
        """
        Initialize dynamic gRPC client.

        Args:
            host: gRPC server host (deprecated, use config)
            port: gRPC server port (deprecated, use config)
            use_tls: Whether to use secure channel (deprecated, use config)
            config: ClientChannelConfig with all settings
            tls_config: TLSConfig for TLS settings

        Raises:
            ConnectionError: If cannot connect to gRPC server
        """
        # Build configuration from parameters
        if config is not None:
            self._config = config
            self.host = config.host
            self.port = config.port
            self.use_tls = config.use_tls
        else:
            # Legacy parameter support
            self.host = host if host is not None else GRPC_DEFAULT_HOST
            self.port = port if port is not None else GRPC_DEFAULT_PORT
            self.use_tls = use_tls if use_tls is not None else False
            self._config = ClientChannelConfig(
                address=f"{self.host}:{self.port}",
                use_tls=self.use_tls,
            )

        self._tls_config = tls_config
        address = self._config.address

        # Get channel options from config
        channel_options = self._config.get_channel_options()

        try:
            if self.use_tls:
                # Use TLSConfig for credentials if provided
                if self._tls_config and self._tls_config.enabled:
                    credentials = self._tls_config.get_channel_credentials()
                    # Add TLS-specific options
                    channel_options.extend(self._tls_config.get_channel_options())
                else:
                    credentials = grpc.ssl_channel_credentials()
                self.channel = grpc.secure_channel(address, credentials, options=channel_options)
            else:
                self.channel = grpc.insecure_channel(address, options=channel_options)

            # Test connection
            grpc.channel_ready_future(self.channel).result(timeout=GRPC_CHANNEL_READY_TIMEOUT)

            self.reflection_stub = reflection_pb2_grpc.ServerReflectionStub(self.channel)

            # Cache for file descriptors to avoid repeated reflection calls
            # Key: service_name, Value: (all_file_descriptors, main_file_descriptor)
            self._file_descriptor_cache: Dict[str, tuple] = {}
            # Cache for message classes created from descriptors
            self._message_classes_cache: Dict[str, Any] = {}

            # Connection state monitoring
            self._is_connected = True  # Assume connected after successful init
            self._connectivity_callbacks = []

            # Subscribe to connectivity state changes
            self.channel.subscribe(
                self._on_connectivity_change,
                try_to_connect=True
            )

            logger.info(f"DynamicGRPCClient initialized for {address}")

        except Exception as e:
            logger.error(f"Failed to initialize gRPC client: {e}")
            raise ConnectionError(f"Cannot connect to gRPC server at {address}: {e}") from e

    def call_method(
        self,
        service_name: str,
        method_name: str,
        request_data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Call a gRPC method dynamically.

        Args:
            service_name: Full service name (e.g., 'apps.CryptoService')
            method_name: Method name (e.g., 'GetCoin')
            request_data: Request payload as dictionary
            metadata: Optional gRPC metadata (headers)
            timeout: Timeout in seconds (default: 5.0)

        Returns:
            Response as dictionary

        Raises:
            grpc.RpcError: If gRPC call fails
            ValueError: If service/method not found
            Exception: For other errors

        Example:
            >>> client = DynamicGRPCClient()
            >>> response = client.call_method(
            ...     'myapp.UserService',
            ...     'GetUser',
            ...     {'user_id': 123},
            ...     metadata={'authorization': 'Bearer token'},
            ...     timeout=5.0
            ... )
        """
        # Set default timeout
        if timeout is None:
            timeout = self._config.call_timeout

        logger.debug(f"Calling {service_name}.{method_name} with payload: {request_data}")

        try:
            # 1. Get all file descriptors for this service (including dependencies)
            file_descriptors, main_file_descriptor = self._get_file_descriptors(service_name)

            # 2. Get service descriptor from main file
            service_descriptor = self._get_service_descriptor(main_file_descriptor, service_name)

            # 3. Get method descriptor
            method_descriptor = self._find_method_descriptor(service_descriptor, method_name)
            if not method_descriptor:
                raise ValueError(f"Method '{method_name}' not found in service '{service_name}'")

            # 4. Build message classes from ALL file descriptors using GetMessages
            # This will create classes for all messages in all files (including dependencies)
            # input_type and output_type are like ".crypto.GetCoinRequest" (with leading dot)
            # GetMessages returns keys WITHOUT leading dot, so we need to strip it
            request_type_name = method_descriptor.input_type.lstrip('.')
            response_type_name = method_descriptor.output_type.lstrip('.')

            logger.info(f"🔍 Building message classes for: request={request_type_name}, response={response_type_name}")

            # Use GetMessages to build all message classes
            message_classes = message_factory.GetMessages(file_descriptors)

            logger.info(f"📦 Built {len(message_classes)} message classes: {list(message_classes.keys())[:10]}...")

            # Get the specific classes we need
            if request_type_name not in message_classes:
                available_keys = list(message_classes.keys())
                raise ValueError(f"Request message type '{request_type_name}' not found in built classes. Available keys: {available_keys}")
            if response_type_name not in message_classes:
                available_keys = list(message_classes.keys())
                raise ValueError(f"Response message type '{response_type_name}' not found in built classes. Available keys: {available_keys}")

            request_class = message_classes[request_type_name]
            response_class = message_classes[response_type_name]

            logger.info(f"✅ Got message classes: request={request_class.__name__}, response={response_class.__name__}")

            # Parse request JSON to protobuf message
            request_message = json_format.ParseDict(request_data, request_class())

            # 6. Prepare metadata
            grpc_metadata = self._prepare_metadata(metadata)

            # 7. Invoke method
            full_method = f"/{service_name}/{method_name}"

            logger.debug(f"Invoking gRPC method: {full_method}")

            # Make unary-unary call
            response = self.channel.unary_unary(
                full_method,
                request_serializer=request_message.SerializeToString,
                response_deserializer=response_class.FromString,
            )(request_message, metadata=grpc_metadata, timeout=timeout)

            # 8. Convert response to JSON
            response_dict = json_format.MessageToDict(
                response,
                preserving_proto_field_name=True,
            )

            logger.debug(f"Response received: {response_dict}")

            return response_dict

        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {e.code()} - {e.details()}", exc_info=True)
            raise

        except json_format.ParseError as e:
            logger.error(f"JSON to Protobuf conversion failed: {e}", exc_info=True)
            raise ValueError(f"Invalid request data format: {e}") from e

        except Exception as e:
            logger.error(f"Unexpected error during gRPC call: {e}", exc_info=True)
            raise

    def _get_file_descriptors(self, service_name: str) -> tuple:
        """
        Get all file descriptors for service using reflection.

        Uses cache to avoid repeated reflection calls for the same service.

        Args:
            service_name: Full service name (e.g., 'crypto.CryptoService')

        Returns:
            Tuple of (all_file_descriptors_list, main_file_descriptor)

        Raises:
            ValueError: If service not found via reflection
        """
        # Check cache first
        if service_name in self._file_descriptor_cache:
            logger.debug(f"Using cached file descriptors for {service_name}")
            return self._file_descriptor_cache[service_name]

        logger.debug(f"Fetching file descriptor for {service_name} via reflection")

        try:
            # Create reflection request
            request = reflection_pb2.ServerReflectionRequest(file_containing_symbol=service_name)

            # Make reflection call
            responses = self.reflection_stub.ServerReflectionInfo(iter([request]))

            # Parse response
            for response in responses:
                if response.HasField("file_descriptor_response"):
                    # Get ALL file descriptor proto bytes (includes dependencies)
                    file_descriptor_protos_bytes = (
                        response.file_descriptor_response.file_descriptor_proto
                    )

                    # Parse ALL file descriptors (dependencies + main file)
                    # Reflection returns them in order: dependencies first, main file last
                    all_file_descriptors = []
                    main_file_descriptor_proto = None
                    service_short_name = service_name.split(".")[-1]  # e.g., "CryptoService"

                    for fd_bytes in file_descriptor_protos_bytes:
                        file_descriptor_proto = descriptor_pb2.FileDescriptorProto()
                        file_descriptor_proto.ParseFromString(fd_bytes)
                        all_file_descriptors.append(file_descriptor_proto)

                        messages = [msg.name for msg in file_descriptor_proto.message_type]
                        logger.info(f"✅ Parsed file descriptor: {file_descriptor_proto.name} (package: {file_descriptor_proto.package}, services: {[svc.name for svc in file_descriptor_proto.service]}, messages: {messages})")

                        # Check if this file contains our service
                        for service in file_descriptor_proto.service:
                            if service.name == service_short_name:
                                main_file_descriptor_proto = file_descriptor_proto
                                logger.info(f"🎯 Found service '{service_short_name}' in file: {file_descriptor_proto.name}")

                    # Cache ALL descriptors and main one
                    if main_file_descriptor_proto:
                        self._file_descriptor_cache[service_name] = (all_file_descriptors, main_file_descriptor_proto)

                        logger.info(
                            f"📦 Loaded {len(all_file_descriptors)} file descriptors for {service_name}"
                        )

                        return (all_file_descriptors, main_file_descriptor_proto)

                elif response.HasField("error_response"):
                    error_code = response.error_response.error_code
                    error_message = response.error_response.error_message
                    raise ValueError(
                        f"Reflection error for '{service_name}': "
                        f"code={error_code}, message={error_message}"
                    )

            raise ValueError(
                f"Service '{service_name}' not found via reflection. "
                f"Ensure the gRPC server has reflection enabled."
            )

        except grpc.RpcError as e:
            logger.error(f"Reflection API call failed: {e.code()} - {e.details()}")
            raise ValueError(
                f"Cannot fetch service descriptor for '{service_name}'. "
                f"Is reflection enabled on the gRPC server?"
            ) from e

    def _get_service_descriptor(
        self, file_descriptor: descriptor_pb2.FileDescriptorProto, service_name: str
    ):
        """
        Get service descriptor from file descriptor.

        Args:
            file_descriptor: FileDescriptorProto
            service_name: Full service name (e.g., 'apps.CryptoService')

        Returns:
            ServiceDescriptorProto

        Raises:
            ValueError: If service not found in file descriptor
        """
        # Extract short service name (last part after dot)
        service_short_name = service_name.split(".")[-1]

        for service in file_descriptor.service:
            if service.name == service_short_name:
                logger.debug(f"Found service descriptor: {service.name}")
                return service

        raise ValueError(
            f"Service '{service_name}' not found in file descriptor '{file_descriptor.name}'"
        )

    def _find_method_descriptor(self, service_descriptor, method_name: str):
        """
        Find method descriptor in service.

        Args:
            service_descriptor: ServiceDescriptorProto
            method_name: Method name (e.g., 'GetCoin')

        Returns:
            MethodDescriptorProto or None
        """
        for method in service_descriptor.method:
            if method.name == method_name:
                logger.debug(
                    f"Found method descriptor: {method.name} "
                    f"(input: {method.input_type}, output: {method.output_type})"
                )
                return method
        return None

    def _prepare_metadata(self, metadata: Optional[Dict[str, str]]) -> Optional[list]:
        """
        Convert metadata dict to gRPC metadata format.

        Args:
            metadata: Dictionary of metadata key-value pairs

        Returns:
            List of tuples [(key, value), ...] or None
        """
        if not metadata:
            return None

        return [(key, value) for key, value in metadata.items()]

    # === Connection State Monitoring ===

    def _on_connectivity_change(self, connectivity):
        """
        Callback for connectivity state changes.

        Args:
            connectivity: grpc.ChannelConnectivity enum value
        """
        state_name = self._get_state_name(connectivity)
        logger.info(f"gRPC channel state: {state_name}")

        # Update connection status
        if connectivity == grpc.ChannelConnectivity.READY:
            self._is_connected = True
            logger.info("✅ gRPC connection established")

        elif connectivity == grpc.ChannelConnectivity.TRANSIENT_FAILURE:
            self._is_connected = False
            logger.warning("⚠️ gRPC connection lost - will retry")
            # Clear caches on connection loss
            self.clear_cache()

        elif connectivity == grpc.ChannelConnectivity.SHUTDOWN:
            self._is_connected = False
            logger.info("🔌 gRPC channel closed")

        # Notify callbacks
        for callback in self._connectivity_callbacks:
            try:
                callback(connectivity)
            except Exception as e:
                logger.error(f"Connectivity callback error: {e}")

    def _get_state_name(self, connectivity) -> str:
        """Get human-readable state name."""
        names = {
            grpc.ChannelConnectivity.IDLE: "IDLE",
            grpc.ChannelConnectivity.CONNECTING: "CONNECTING",
            grpc.ChannelConnectivity.READY: "READY",
            grpc.ChannelConnectivity.TRANSIENT_FAILURE: "TRANSIENT_FAILURE",
            grpc.ChannelConnectivity.SHUTDOWN: "SHUTDOWN",
        }
        return names.get(connectivity, "UNKNOWN")

    def add_connectivity_callback(self, callback):
        """
        Add callback for connectivity changes.

        Args:
            callback: Function to call on state change (receives connectivity enum)

        Example:
            >>> def on_change(state):
            ...     print(f"State: {state}")
            >>> client.add_connectivity_callback(on_change)
        """
        self._connectivity_callbacks.append(callback)

    def is_connected(self) -> bool:
        """
        Check if channel is connected.

        Returns:
            True if channel is in READY state
        """
        return self._is_connected

    def wait_for_ready(self, timeout: float = 10):
        """
        Wait for channel to be ready.

        Args:
            timeout: Max wait time in seconds

        Raises:
            TimeoutError: If not ready within timeout
        """
        import time

        deadline = time.time() + timeout

        while time.time() < deadline:
            state = self.channel._channel.check_connectivity_state(False)
            if state == grpc.ChannelConnectivity.READY:
                self._is_connected = True
                return
            time.sleep(0.1)

        raise TimeoutError(f"Channel not ready after {timeout}s")

    def is_healthy(self) -> bool:
        """
        Check if connection is healthy using Health Checking Protocol.

        Combines:
        1. Channel connectivity state
        2. gRPC health check protocol

        Returns:
            True if both channel and server are healthy
        """
        # Check channel state first
        if not self.is_connected():
            logger.debug("Health check: Channel not connected")
            return False

        # Check server health via Health protocol
        try:
            from grpc_health.v1 import health_pb2, health_pb2_grpc

            health_stub = health_pb2_grpc.HealthStub(self.channel)
            response = health_stub.Check(
                health_pb2.HealthCheckRequest(service=""),
                timeout=5
            )

            is_serving = response.status == health_pb2.HealthCheckResponse.SERVING

            if is_serving:
                logger.debug("Health check: ✅ SERVING")
            else:
                logger.warning(f"Health check: ❌ Status={response.status}")

            return is_serving

        except grpc.RpcError as e:
            logger.error(f"Health check failed: {e.code()} - {e.details()}")
            return False
        except ImportError:
            logger.warning("grpcio-health-checking not installed, skipping health check")
            # Fallback to just connectivity check
            return self.is_connected()

    def check_service_health(self, service_name: str) -> bool:
        """
        Check health of specific service.

        Args:
            service_name: Service name (e.g., "apps.CryptoService")

        Returns:
            True if service is healthy (SERVING status)
        """
        if not self.is_connected():
            return False

        try:
            from grpc_health.v1 import health_pb2, health_pb2_grpc

            health_stub = health_pb2_grpc.HealthStub(self.channel)
            response = health_stub.Check(
                health_pb2.HealthCheckRequest(service=service_name),
                timeout=5
            )

            if response.status == health_pb2.HealthCheckResponse.SERVING:
                return True
            elif response.status == health_pb2.HealthCheckResponse.SERVICE_UNKNOWN:
                logger.error(f"Service '{service_name}' not found")
            else:
                logger.warning(f"Service '{service_name}' unhealthy: {response.status}")

            return False

        except grpc.RpcError as e:
            logger.error(f"Health check for '{service_name}' failed: {e}")
            return False
        except ImportError:
            logger.warning("grpcio-health-checking not installed")
            return self.is_connected()

    def clear_cache(self):
        """Clear file descriptor cache."""
        self._file_descriptor_cache.clear()
        logger.debug("File descriptor cache cleared")

    def close(self):
        """Close gRPC channel."""
        if self.channel:
            self.channel.close()
            logger.info("gRPC channel closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self):
        """String representation."""
        return f"<DynamicGRPCClient channel={self.channel}>"


__all__ = ["DynamicGRPCClient"]
