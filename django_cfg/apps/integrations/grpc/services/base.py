"""
Base service classes for gRPC.

Provides convenient base classes with Django integration.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import grpc
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

logger = logging.getLogger(__name__)

User = get_user_model()


class BaseService:
    """
    Base class for gRPC services with Django integration.

    Features:
    - Easy access to authenticated user
    - Permission checking helpers
    - Error handling utilities
    - Context helpers

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.services.base import BaseService
        from myapp_pb2 import UserResponse
        from myapp_pb2_grpc import UserServiceServicer

        class UserService(BaseService, UserServiceServicer):
            def GetUser(self, request, context):
                # Get authenticated user
                user = self.get_user(context)

                # Check permission
                if not user.has_perm('myapp.view_user'):
                    self.abort_permission_denied(context, "No permission to view users")

                # Your logic
                return UserResponse(id=user.id, username=user.username)
        ```
    """

    def get_user(self, context: grpc.ServicerContext) -> Optional[User]:
        """
        Get authenticated user from context.

        Args:
            context: gRPC servicer context

        Returns:
            Authenticated User instance or None

        Example:
            >>> user = self.get_user(context)
            >>> if user:
            ...     print(f"User: {user.username}")
        """
        return getattr(context, "user", None)

    def require_user(self, context: grpc.ServicerContext) -> User:
        """
        Get authenticated user or abort if not authenticated.

        Args:
            context: gRPC servicer context

        Returns:
            Authenticated User instance

        Raises:
            grpc.RpcError: UNAUTHENTICATED if user not authenticated

        Example:
            >>> user = self.require_user(context)
            >>> # user is guaranteed to be authenticated here
        """
        user = self.get_user(context)
        if not user:
            self.abort_unauthenticated(context, "Authentication required")
        return user

    def check_permission(
        self,
        context: grpc.ServicerContext,
        permission: str,
        obj: Any = None,
    ) -> bool:
        """
        Check if user has permission.

        Args:
            context: gRPC servicer context
            permission: Permission string (e.g., 'myapp.view_user')
            obj: Object to check permission for (optional)

        Returns:
            True if user has permission

        Example:
            >>> if not self.check_permission(context, 'myapp.view_user'):
            ...     self.abort_permission_denied(context)
        """
        user = self.get_user(context)
        if not user:
            return False

        return user.has_perm(permission, obj)

    def require_permission(
        self,
        context: grpc.ServicerContext,
        permission: str,
        obj: Any = None,
        message: str = None,
    ):
        """
        Require user to have permission or abort.

        Args:
            context: gRPC servicer context
            permission: Permission string (e.g., 'myapp.view_user')
            obj: Object to check permission for (optional)
            message: Custom error message (optional)

        Raises:
            grpc.RpcError: PERMISSION_DENIED if permission check fails

        Example:
            >>> self.require_permission(context, 'myapp.view_user')
            >>> # user has permission, continue...
        """
        if not self.check_permission(context, permission, obj):
            if message is None:
                message = f"Permission '{permission}' required"
            self.abort_permission_denied(context, message)

    def check_staff(self, context: grpc.ServicerContext) -> bool:
        """
        Check if user is staff.

        Args:
            context: gRPC servicer context

        Returns:
            True if user is staff

        Example:
            >>> if self.check_staff(context):
            ...     # Staff-only logic
        """
        user = self.get_user(context)
        return user.is_staff if user else False

    def require_staff(self, context: grpc.ServicerContext, message: str = None):
        """
        Require user to be staff or abort.

        Args:
            context: gRPC servicer context
            message: Custom error message (optional)

        Raises:
            grpc.RpcError: PERMISSION_DENIED if user is not staff

        Example:
            >>> self.require_staff(context)
            >>> # user is staff, continue...
        """
        if not self.check_staff(context):
            if message is None:
                message = "Staff access required"
            self.abort_permission_denied(context, message)

    def check_superuser(self, context: grpc.ServicerContext) -> bool:
        """
        Check if user is superuser.

        Args:
            context: gRPC servicer context

        Returns:
            True if user is superuser

        Example:
            >>> if self.check_superuser(context):
            ...     # Superuser-only logic
        """
        user = self.get_user(context)
        return user.is_superuser if user else False

    def require_superuser(self, context: grpc.ServicerContext, message: str = None):
        """
        Require user to be superuser or abort.

        Args:
            context: gRPC servicer context
            message: Custom error message (optional)

        Raises:
            grpc.RpcError: PERMISSION_DENIED if user is not superuser

        Example:
            >>> self.require_superuser(context)
            >>> # user is superuser, continue...
        """
        if not self.check_superuser(context):
            if message is None:
                message = "Superuser access required"
            self.abort_permission_denied(context, message)

    # Error handling helpers

    def abort(
        self,
        context: grpc.ServicerContext,
        code: grpc.StatusCode,
        message: str,
    ):
        """
        Abort request with error.

        Args:
            context: gRPC servicer context
            code: gRPC status code
            message: Error message

        Example:
            >>> self.abort(context, grpc.StatusCode.INVALID_ARGUMENT, "Invalid user ID")
        """
        logger.warning(f"Aborting request: {code.name} - {message}")
        context.abort(code, message)

    def abort_invalid_argument(self, context: grpc.ServicerContext, message: str = "Invalid argument"):
        """Abort with INVALID_ARGUMENT status."""
        self.abort(context, grpc.StatusCode.INVALID_ARGUMENT, message)

    def abort_not_found(self, context: grpc.ServicerContext, message: str = "Not found"):
        """Abort with NOT_FOUND status."""
        self.abort(context, grpc.StatusCode.NOT_FOUND, message)

    def abort_permission_denied(self, context: grpc.ServicerContext, message: str = "Permission denied"):
        """Abort with PERMISSION_DENIED status."""
        self.abort(context, grpc.StatusCode.PERMISSION_DENIED, message)

    def abort_unauthenticated(self, context: grpc.ServicerContext, message: str = "Unauthenticated"):
        """Abort with UNAUTHENTICATED status."""
        self.abort(context, grpc.StatusCode.UNAUTHENTICATED, message)

    def abort_unimplemented(self, context: grpc.ServicerContext, message: str = "Not implemented"):
        """Abort with UNIMPLEMENTED status."""
        self.abort(context, grpc.StatusCode.UNIMPLEMENTED, message)

    def abort_internal(self, context: grpc.ServicerContext, message: str = "Internal server error"):
        """Abort with INTERNAL status."""
        self.abort(context, grpc.StatusCode.INTERNAL, message)

    # Context helpers

    def get_metadata(self, context: grpc.ServicerContext, key: str) -> Optional[str]:
        """
        Get metadata value from context.

        Args:
            context: gRPC servicer context
            key: Metadata key

        Returns:
            Metadata value or None

        Example:
            >>> user_agent = self.get_metadata(context, 'user-agent')
        """
        metadata = dict(context.invocation_metadata())
        return metadata.get(key.lower())

    def set_metadata(self, context: grpc.ServicerContext, key: str, value: str):
        """
        Set response metadata.

        Args:
            context: gRPC servicer context
            key: Metadata key
            value: Metadata value

        Example:
            >>> self.set_metadata(context, 'x-request-id', request_id)
        """
        context.set_trailing_metadata([(key, value)])

    def get_peer(self, context: grpc.ServicerContext) -> str:
        """
        Get peer information.

        Args:
            context: gRPC servicer context

        Returns:
            Peer string

        Example:
            >>> peer = self.get_peer(context)
            >>> print(f"Request from: {peer}")
        """
        return context.peer()


class ReadOnlyService(BaseService):
    """
    Base class for read-only gRPC services.

    Automatically aborts on write operations.

    Example:
        ```python
        class UserReadService(ReadOnlyService, UserServiceServicer):
            def GetUser(self, request, context):
                # Allowed
                return UserResponse(...)

            def CreateUser(self, request, context):
                # Will abort with PERMISSION_DENIED
                self.abort_readonly(context)
        ```
    """

    def abort_readonly(self, context: grpc.ServicerContext, message: str = "Read-only service"):
        """Abort with PERMISSION_DENIED for write operations."""
        self.abort_permission_denied(context, message)


class AuthRequiredService(BaseService):
    """
    Base class for services that require authentication.

    Automatically checks for authenticated user in all methods.

    Example:
        ```python
        class UserService(AuthRequiredService, UserServiceServicer):
            def GetUser(self, request, context):
                # User is automatically required
                user = self.user  # Guaranteed to be authenticated
                return UserResponse(...)
        ```
    """

    def __init__(self):
        super().__init__()
        self._user = None

    def _ensure_auth(self, context: grpc.ServicerContext):
        """Ensure user is authenticated."""
        self._user = self.require_user(context)

    @property
    def user(self) -> User:
        """Get authenticated user (must call _ensure_auth first)."""
        if self._user is None:
            raise RuntimeError("User not set - did you call _ensure_auth?")
        return self._user


__all__ = [
    "BaseService",
    "ReadOnlyService",
    "AuthRequiredService",
]
