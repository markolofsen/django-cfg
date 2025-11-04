"""
API Key Authentication Interceptor for gRPC.

Handles API key verification and Django user authentication for gRPC requests.
Simple, secure, and manageable through Django admin.
"""

import asyncio
import contextvars
import logging
from typing import Callable, Optional

import grpc
import grpc.aio
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()

# Context variables for passing user/api_key between async interceptors
_grpc_user_var: contextvars.ContextVar = contextvars.ContextVar('grpc_user', default=None)
_grpc_api_key_var: contextvars.ContextVar = contextvars.ContextVar('grpc_api_key', default=None)


class ApiKeyAuthInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC interceptor for API key authentication.

    Features:
    - Validates API keys from database (GrpcApiKey model)
    - Accepts Django SECRET_KEY for development/internal use
    - Loads Django user from API key
    - Sets user on request context
    - Supports public methods whitelist
    - Tracks API key usage
    - Handles authentication errors gracefully

    Example:
        ```python
        # In Django settings (auto-configured by django-cfg)
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.auth.ApiKeyAuthInterceptor",
            ]
        }
        ```

    API Key Format:
        x-api-key: <api_key_string>

    Or for SECRET_KEY:
        x-api-key: <Django SECRET_KEY>
    """

    def __init__(self):
        """Initialize API key authentication interceptor."""
        self.grpc_auth_config = getattr(settings, "GRPC_AUTH", {})
        self.enabled = self.grpc_auth_config.get("enabled", True)
        self.require_auth = self.grpc_auth_config.get("require_auth", False)

        # API Key settings
        self.api_key_header = self.grpc_auth_config.get("api_key_header", "x-api-key")
        self.accept_django_secret_key = self.grpc_auth_config.get(
            "accept_django_secret_key", True
        )

        # Public methods (don't require auth)
        self.public_methods = self.grpc_auth_config.get("public_methods", [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ])

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for authentication (async).

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler (possibly wrapped with auth)
        """
        # Skip if auth is disabled
        if not self.enabled:
            return await continuation(handler_call_details)

        # Check if method is public
        method_name = handler_call_details.method
        if method_name in self.public_methods:
            logger.debug(f"Public method accessed: {method_name}")
            return await continuation(handler_call_details)

        # Extract API key from metadata
        api_key = self._extract_api_key(handler_call_details.invocation_metadata)

        # If no API key provided
        if not api_key:
            if self.require_auth:
                logger.warning(f"Missing API key for {method_name}")
                return self._abort_unauthenticated("API key is required")
            else:
                # Allow anonymous access (no user/api_key in context)
                logger.debug(f"No API key provided for {method_name}, allowing anonymous access")
                return await continuation(handler_call_details)

        # Verify API key and get user + api_key instance (async)
        user, api_key_instance = await self._verify_api_key(api_key)

        # If API key is valid, ALWAYS set user and api_key in context (even if require_auth=False)
        if user:
            logger.debug(f"Authenticated user {user.id} ({user.username}) for {method_name}")
            return await self._continue_with_user(continuation, handler_call_details, user, api_key_instance)

        # API key provided but invalid
        if self.require_auth:
            logger.warning(f"Invalid API key for {method_name}")
            return self._abort_unauthenticated("Invalid or expired API key")
        else:
            # Allow anonymous access even with invalid key
            logger.debug(f"Invalid API key for {method_name}, allowing anonymous access")
            return await continuation(handler_call_details)

    def _extract_api_key(self, metadata: tuple) -> Optional[str]:
        """
        Extract API key from gRPC metadata.

        Args:
            metadata: gRPC invocation metadata

        Returns:
            API key string or None
        """
        if not metadata:
            return None

        # Convert metadata to dict (case-insensitive lookup)
        metadata_dict = dict(metadata)

        # Get API key header (case-insensitive)
        for key, value in metadata_dict.items():
            if key.lower() == self.api_key_header.lower():
                return value

        return None

    async def _verify_api_key(self, api_key: str) -> tuple[Optional[User], Optional["GrpcApiKey"]]:
        """
        Verify API key and return user and api_key instance (async).

        Checks:
        1. Django SECRET_KEY (if enabled)
        2. GrpcApiKey model in database

        Args:
            api_key: API key string

        Returns:
            Tuple of (Django User instance or None, GrpcApiKey instance or None)
        """
        # Check if it's Django SECRET_KEY
        if self.accept_django_secret_key and api_key == settings.SECRET_KEY:
            logger.debug("API key matches Django SECRET_KEY")
            # For SECRET_KEY, return first superuser or None (no api_key instance)
            try:
                # Wrap Django ORM in asyncio.to_thread()
                superuser = await asyncio.to_thread(
                    lambda: User.objects.filter(is_superuser=True, is_active=True).first()
                )
                if superuser:
                    return superuser, None
                else:
                    logger.warning("No active superuser found for SECRET_KEY authentication")
                    return None, None
            except Exception as e:
                logger.error(f"Error loading superuser for SECRET_KEY: {e}")
                return None, None

        # Check API key in database
        try:
            from django_cfg.apps.integrations.grpc.models import GrpcApiKey

            # Wrap Django ORM in asyncio.to_thread()
            api_key_obj = await asyncio.to_thread(
                lambda: GrpcApiKey.objects.filter(key=api_key, is_active=True).first()
            )

            if api_key_obj and api_key_obj.is_valid:
                # Update usage tracking (also wrapped in to_thread)
                await asyncio.to_thread(api_key_obj.mark_used)
                logger.debug(f"Valid API key for user {api_key_obj.user.id} ({api_key_obj.user.username})")
                return api_key_obj.user, api_key_obj
            else:
                logger.debug("API key not found or invalid in database")
                return None, None

        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None, None

    async def _continue_with_user(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        user: User,
        api_key_instance: Optional["GrpcApiKey"] = None,
    ) -> grpc.RpcMethodHandler:
        """
        Continue RPC with authenticated user and api_key in context (async).

        Args:
            continuation: Function to invoke next interceptor or handler
            handler_call_details: Details about the RPC call
            user: Authenticated Django user
            api_key_instance: GrpcApiKey instance used for authentication (if applicable)

        Returns:
            RPC method handler with user and api_key context
        """
        # Get the handler (await because continuation is async)
        handler = await continuation(handler_call_details)

        if handler is None:
            return None

        # Wrap the handler to inject user and api_key into contextvars (not context directly)
        # All wrappers must be async for grpc.aio
        async def wrapped_unary_unary(request, context):
            # Set context variables for async context
            _grpc_user_var.set(user)
            _grpc_api_key_var.set(api_key_instance)
            logger.info(f"[Auth] Set contextvar api_key = {api_key_instance} (user={user})")
            return await handler.unary_unary(request, context)

        async def wrapped_unary_stream(request, context):
            # Set context variables for async context
            _grpc_user_var.set(user)
            _grpc_api_key_var.set(api_key_instance)
            logger.info(f"[Auth] Set contextvar api_key = {api_key_instance} (user={user})")
            async for response in handler.unary_stream(request, context):
                yield response

        async def wrapped_stream_unary(request_iterator, context):
            # Set context variables for async context
            _grpc_user_var.set(user)
            _grpc_api_key_var.set(api_key_instance)
            return await handler.stream_unary(request_iterator, context)

        async def wrapped_stream_stream(request_iterator, context):
            # Set context variables for async context
            _grpc_user_var.set(user)
            _grpc_api_key_var.set(api_key_instance)
            async for response in handler.stream_stream(request_iterator, context):
                yield response

        # Return wrapped handler based on type
        return grpc.unary_unary_rpc_method_handler(
            wrapped_unary_unary,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        ) if handler.unary_unary else (
            grpc.unary_stream_rpc_method_handler(
                wrapped_unary_stream,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            ) if handler.unary_stream else (
                grpc.stream_unary_rpc_method_handler(
                    wrapped_stream_unary,
                    request_deserializer=handler.request_deserializer,
                    response_serializer=handler.response_serializer,
                ) if handler.stream_unary else (
                    grpc.stream_stream_rpc_method_handler(
                        wrapped_stream_stream,
                        request_deserializer=handler.request_deserializer,
                        response_serializer=handler.response_serializer,
                    ) if handler.stream_stream else None
                )
            )
        )

    def _abort_unauthenticated(self, message: str) -> grpc.RpcMethodHandler:
        """
        Return handler that aborts with UNAUTHENTICATED status.

        Args:
            message: Error message

        Returns:
            RPC method handler that aborts
        """
        def abort(*args, **kwargs):
            context = args[1] if len(args) > 1 else None
            if context:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, message)

        return grpc.unary_unary_rpc_method_handler(
            abort,
            request_deserializer=lambda x: x,
            response_serializer=lambda x: x,
        )


__all__ = ["ApiKeyAuthInterceptor", "get_current_grpc_user", "get_current_grpc_api_key"]


def get_current_grpc_user():
    """Get current gRPC user from context variables (async-safe)."""
    return _grpc_user_var.get()


def get_current_grpc_api_key():
    """Get current gRPC API key from context variables (async-safe)."""
    return _grpc_api_key_var.get()
