"""
Generic RPC Request/Response Models.

Type-safe RPC models with Generic support for typed parameters and results.
Uses Pydantic 2 for validation and serialization.

File size: ~200 lines
"""

from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Optional

from .base import BaseRPCRequest, BaseRPCResponse

# Type variables for generic RPC models
TParams = TypeVar("TParams", bound=BaseModel)
TResult = TypeVar("TResult", bound=BaseModel)


class RPCRequest(BaseRPCRequest, Generic[TParams]):
    """
    Generic RPC request with typed parameters.

    Type-safe wrapper ensuring parameters are validated Pydantic models.
    Prevents raw dictionary usage and provides IDE autocomplete.

    Example:
        >>> from pydantic import BaseModel
        >>>
        >>> class EchoParams(BaseModel):
        ...     message: str
        >>>
        >>> request = RPCRequest[EchoParams](
        ...     method="echo",
        ...     params=EchoParams(message="Hello"),
        ...     reply_to="list:response:abc123"
        ... )
        >>> print(request.params.message)  # "Hello"
    """

    params: TParams = Field(
        ...,
        description="Typed parameters for RPC method",
    )

    def get_params_dict(self) -> dict:
        """
        Get parameters as dictionary.

        Returns:
            Dictionary representation of params

        Example:
            >>> request = RPCRequest[EchoParams](...)
            >>> params_dict = request.get_params_dict()
            >>> print(params_dict)  # {"message": "Hello"}
        """
        return self.params.model_dump()


class RPCResponse(BaseRPCResponse, Generic[TResult]):
    """
    Generic RPC response with typed result.

    Type-safe wrapper ensuring results are validated Pydantic models.
    Result is None if success=False (error occurred).

    Example:
        >>> class EchoResult(BaseModel):
        ...     echoed: str
        ...     length: int
        >>>
        >>> # Success response
        >>> response = RPCResponse[EchoResult](
        ...     correlation_id=request.correlation_id,
        ...     success=True,
        ...     result=EchoResult(echoed="Hello", length=5)
        ... )
        >>>
        >>> # Error response
        >>> response = RPCResponse[EchoResult](
        ...     correlation_id=request.correlation_id,
        ...     success=False,
        ...     error="Connection failed",
        ...     error_code="connection_error"
        ... )
    """

    result: Optional[TResult] = Field(
        default=None,
        description="Typed result data (None if error)",
    )

    def get_result_dict(self) -> Optional[dict]:
        """
        Get result as dictionary.

        Returns:
            Dictionary representation of result, or None

        Example:
            >>> response = RPCResponse[EchoResult](...)
            >>> if response.success:
            ...     result_dict = response.get_result_dict()
        """
        if self.result is None:
            return None
        return self.result.model_dump()


# ==================== Example Models ====================

class EchoParams(BaseModel):
    """
    Parameters for echo RPC method.

    Simple example for testing RPC layer.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Message to echo back",
    )


class EchoResult(BaseModel):
    """
    Result of echo RPC method.

    Returns the original message and its length.
    """

    echoed: str = Field(
        ...,
        description="Echoed message",
    )

    length: int = Field(
        ...,
        ge=0,
        description="Length of echoed message",
    )


# ==================== Usage Examples ====================

"""
Type-safe RPC call example:

>>> # Define params and result models
>>> class UserProfileParams(BaseModel):
...     user_id: str = Field(..., min_length=1)
>>>
>>> class UserProfileResult(BaseModel):
...     user_id: str
...     username: str
...     email: str
>>>
>>> # Create type-safe request
>>> request = RPCRequest[UserProfileParams](
...     method="user.get_profile",
...     params=UserProfileParams(user_id="123"),
...     reply_to="list:response:abc123"
... )
>>>
>>> # Response with validation
>>> response = RPCResponse[UserProfileResult](
...     correlation_id=request.correlation_id,
...     success=True,
...     result=UserProfileResult(
...         user_id="123",
...         username="john_doe",
...         email="john@example.com"
...     )
... )
>>>
>>> # Type-safe access
>>> if response.success and response.result:
...     print(response.result.username)  # IDE knows this is str!
"""


__all__ = [
    "RPCRequest",
    "RPCResponse",
    "EchoParams",
    "EchoResult",
]
