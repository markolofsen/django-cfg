"""
JWT Authentication Interceptor for gRPC.

Handles JWT token verification and Django user authentication for gRPC requests.
"""

import logging
from typing import Any, Callable, Optional

import grpc
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


class JWTAuthInterceptor(grpc.ServerInterceptor):
    """
    gRPC interceptor for JWT authentication.

    Features:
    - Extracts JWT token from metadata
    - Verifies token signature and expiration
    - Loads Django user from token
    - Sets user on request context
    - Supports public methods whitelist
    - Handles authentication errors gracefully

    Example:
        ```python
        # In Django settings (auto-configured by django-cfg)
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.auth.JWTAuthInterceptor",
            ]
        }
        ```

    Token Format:
        Authorization: Bearer <jwt_token>
    """

    def __init__(self):
        """Initialize JWT authentication interceptor."""
        self.grpc_auth_config = getattr(settings, "GRPC_AUTH", {})
        self.enabled = self.grpc_auth_config.get("enabled", True)
        self.require_auth = self.grpc_auth_config.get("require_auth", True)
        self.token_header = self.grpc_auth_config.get("token_header", "authorization")
        self.token_prefix = self.grpc_auth_config.get("token_prefix", "Bearer")
        self.public_methods = self.grpc_auth_config.get("public_methods", [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
        ])

        # JWT settings
        self.jwt_secret_key = self.grpc_auth_config.get("jwt_secret_key") or settings.SECRET_KEY
        self.jwt_algorithm = self.grpc_auth_config.get("jwt_algorithm", "HS256")
        self.jwt_verify_exp = self.grpc_auth_config.get("jwt_verify_exp", True)
        self.jwt_leeway = self.grpc_auth_config.get("jwt_leeway", 0)

    def intercept_service(self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for authentication.

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler (possibly wrapped with auth)
        """
        # Skip if auth is disabled
        if not self.enabled:
            return continuation(handler_call_details)

        # Check if method is public
        method_name = handler_call_details.method
        if method_name in self.public_methods:
            logger.debug(f"Public method accessed: {method_name}")
            return continuation(handler_call_details)

        # Extract token from metadata
        token = self._extract_token(handler_call_details.invocation_metadata)

        # If no token and auth is required, abort
        if not token:
            if self.require_auth:
                logger.warning(f"Missing authentication token for {method_name}")
                return self._abort_unauthenticated(
                    "Authentication token is required"
                )
            else:
                # Allow anonymous access
                logger.debug(f"No token provided for {method_name}, allowing anonymous access")
                return continuation(handler_call_details)

        # Verify token and get user
        user = self._verify_token(token)

        if not user:
            if self.require_auth:
                logger.warning(f"Invalid authentication token for {method_name}")
                return self._abort_unauthenticated(
                    "Invalid or expired authentication token"
                )
            else:
                # Allow anonymous access even with invalid token
                return continuation(handler_call_details)

        # Add user to context and continue
        logger.debug(f"Authenticated user {user.id} for {method_name}")
        return self._continue_with_user(continuation, handler_call_details, user)

    def _extract_token(self, metadata: tuple) -> Optional[str]:
        """
        Extract JWT token from gRPC metadata.

        Args:
            metadata: gRPC invocation metadata

        Returns:
            JWT token string or None
        """
        if not metadata:
            return None

        # Convert metadata to dict
        metadata_dict = dict(metadata)

        # Get authorization header (case-insensitive)
        auth_header = None
        for key, value in metadata_dict.items():
            if key.lower() == self.token_header.lower():
                auth_header = value
                break

        if not auth_header:
            return None

        # Extract token from "Bearer <token>" format
        if auth_header.startswith(f"{self.token_prefix} "):
            return auth_header[len(self.token_prefix) + 1:]
        elif self.token_prefix == "":
            # No prefix expected
            return auth_header
        else:
            # Invalid format
            logger.warning(f"Invalid authorization header format: {auth_header[:20]}...")
            return None

    def _verify_token(self, token: str) -> Optional[User]:
        """
        Verify JWT token and return user.

        Args:
            token: JWT token string

        Returns:
            Django User instance or None
        """
        try:
            import jwt

            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret_key,
                algorithms=[self.jwt_algorithm],
                options={
                    "verify_exp": self.jwt_verify_exp,
                },
                leeway=self.jwt_leeway,
            )

            # Extract user ID from payload
            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("Token missing user_id claim")
                return None

            # Load user from database
            try:
                user = User.objects.get(pk=user_id)
                if not user.is_active:
                    logger.warning(f"Inactive user {user_id} attempted to authenticate")
                    return None
                return user
            except User.DoesNotExist:
                logger.warning(f"User {user_id} from token does not exist")
                return None

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except ImportError:
            logger.error("PyJWT library not installed. Install with: pip install PyJWT")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None

    def _continue_with_user(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        user: User,
    ) -> grpc.RpcMethodHandler:
        """
        Continue RPC with authenticated user in context.

        Args:
            continuation: Function to invoke next interceptor or handler
            handler_call_details: Details about the RPC call
            user: Authenticated Django user

        Returns:
            RPC method handler with user context
        """
        # Get the handler
        handler = continuation(handler_call_details)

        if handler is None:
            return None

        # Wrap the handler to inject user into context
        def wrapped_unary_unary(request, context):
            # Set user on context for access in service methods
            context.user = user
            return handler.unary_unary(request, context)

        def wrapped_unary_stream(request, context):
            context.user = user
            return handler.unary_stream(request, context)

        def wrapped_stream_unary(request_iterator, context):
            context.user = user
            return handler.stream_unary(request_iterator, context)

        def wrapped_stream_stream(request_iterator, context):
            context.user = user
            return handler.stream_stream(request_iterator, context)

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


__all__ = ["JWTAuthInterceptor"]
