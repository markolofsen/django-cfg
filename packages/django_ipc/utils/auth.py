"""
Authentication Utilities for WebSocket Server.

Provides JWT and token-based authentication.

File size: ~350 lines
"""

from typing import Optional, Dict, Any, Set
from datetime import datetime, timezone
import jwt
from loguru import logger

from ..server.config import AuthMode


class AuthenticationError(Exception):
    """Authentication failed."""

    pass


class JWTAuthenticator:
    """
    JWT token authenticator.

    Validates JWT tokens and extracts user information.

    Example:
        >>> auth = JWTAuthenticator(
        ...     secret="your-secret-key",
        ...     algorithm="HS256",
        ... )
        >>>
        >>> # Validate token
        >>> user_id = auth.authenticate("eyJ...")
        >>> print(f"Authenticated user: {user_id}")
    """

    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        audience: Optional[str] = None,
        issuer: Optional[str] = None,
    ):
        """
        Initialize JWT authenticator.

        Args:
            secret: JWT secret key
            algorithm: JWT algorithm (default: HS256)
            audience: Expected audience (optional)
            issuer: Expected issuer (optional)
        """
        self.secret = secret
        self.algorithm = algorithm
        self.audience = audience
        self.issuer = issuer

    def authenticate(self, token: str) -> str:
        """
        Authenticate JWT token and extract user ID.

        Args:
            token: JWT token string

        Returns:
            User ID from token

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )

            # Extract user ID (try multiple common claims)
            user_id = (
                payload.get("user_id")
                or payload.get("sub")
                or payload.get("id")
            )

            if not user_id:
                raise AuthenticationError("Token missing user_id/sub/id claim")

            return str(user_id)

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")

        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def get_payload(self, token: str) -> Dict[str, Any]:
        """
        Get full JWT payload.

        Args:
            token: JWT token string

        Returns:
            Token payload dict

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            return jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")


class TokenAuthenticator:
    """
    Simple token authenticator.

    Validates tokens against allowed set.

    Example:
        >>> auth = TokenAuthenticator(
        ...     allowed_tokens={"token123", "token456"},
        ... )
        >>>
        >>> # Validate token
        >>> user_id = auth.authenticate("token123")
    """

    def __init__(
        self,
        allowed_tokens: Set[str],
        extract_user_id: bool = False,
    ):
        """
        Initialize token authenticator.

        Args:
            allowed_tokens: Set of allowed token strings
            extract_user_id: If True, use token as user_id (default: False)
        """
        self.allowed_tokens = allowed_tokens
        self.extract_user_id = extract_user_id

    def authenticate(self, token: str) -> Optional[str]:
        """
        Authenticate token.

        Args:
            token: Token string

        Returns:
            User ID (token itself if extract_user_id=True, else None)

        Raises:
            AuthenticationError: If token not allowed
        """
        if token not in self.allowed_tokens:
            raise AuthenticationError("Invalid token")

        return token if self.extract_user_id else None


class NoAuthenticator:
    """
    No authentication (allow all).

    Use only for development/testing.
    """

    def authenticate(self, token: str) -> Optional[str]:
        """
        No authentication - always succeeds.

        Args:
            token: Token string (ignored)

        Returns:
            None (no user ID)
        """
        return None


class AuthManager:
    """
    Authentication manager.

    Manages authentication based on configured mode.

    Example:
        >>> from django_ipc.server.config import WSServerConfig, AuthMode
        >>>
        >>> config = WSServerConfig(
        ...     auth_mode=AuthMode.JWT,
        ...     jwt_secret="your-secret",
        ... )
        >>>
        >>> auth_manager = AuthManager.from_config(config)
        >>>
        >>> # Authenticate
        >>> user_id = auth_manager.authenticate("Bearer eyJ...")
    """

    def __init__(self, authenticator):
        """
        Initialize auth manager.

        Args:
            authenticator: Authenticator instance
        """
        self.authenticator = authenticator

    @classmethod
    def from_config(cls, config) -> "AuthManager":
        """
        Create AuthManager from server config.

        Args:
            config: WSServerConfig instance

        Returns:
            AuthManager instance

        Raises:
            ValueError: If auth mode is invalid or config is missing
        """
        if config.auth_mode == AuthMode.NONE:
            logger.warning("Authentication disabled - use only for development!")
            authenticator = NoAuthenticator()

        elif config.auth_mode == AuthMode.JWT:
            if not config.jwt_secret:
                raise ValueError("jwt_secret required for JWT auth mode")

            authenticator = JWTAuthenticator(
                secret=config.jwt_secret,
                algorithm=config.jwt_algorithm,
            )

        elif config.auth_mode == AuthMode.TOKEN:
            if not config.allowed_tokens:
                raise ValueError("allowed_tokens required for TOKEN auth mode")

            authenticator = TokenAuthenticator(
                allowed_tokens=config.allowed_tokens,
            )

        else:
            raise ValueError(f"Unsupported auth mode: {config.auth_mode}")

        return cls(authenticator)

    def authenticate(self, auth_header: str) -> Optional[str]:
        """
        Authenticate using auth header.

        Args:
            auth_header: Authorization header value (e.g., "Bearer <token>")

        Returns:
            User ID or None

        Raises:
            AuthenticationError: If authentication fails
        """
        # Extract token from header
        token = self._extract_token(auth_header)

        # Authenticate
        return self.authenticator.authenticate(token)

    def _extract_token(self, auth_header: str) -> str:
        """
        Extract token from Authorization header.

        Args:
            auth_header: Authorization header value

        Returns:
            Token string

        Raises:
            AuthenticationError: If header format is invalid
        """
        if not auth_header:
            raise AuthenticationError("Missing authorization header")

        parts = auth_header.split()

        if len(parts) != 2:
            raise AuthenticationError("Invalid authorization header format")

        scheme, token = parts

        if scheme.lower() != "bearer":
            raise AuthenticationError(f"Unsupported auth scheme: {scheme}")

        return token


__all__ = [
    "AuthenticationError",
    "JWTAuthenticator",
    "TokenAuthenticator",
    "NoAuthenticator",
    "AuthManager",
]
