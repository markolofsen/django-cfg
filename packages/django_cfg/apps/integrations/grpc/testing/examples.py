"""
Example payloads for gRPC method testing.

This registry provides example request payloads and expected responses
for common gRPC methods. Used by the Testing API to provide interactive
examples.

To add your own examples, extend the EXAMPLES_REGISTRY dictionary:

    EXAMPLES_REGISTRY['YourService'] = {
        'YourMethod': {
            'description': 'Description of what this method does',
            'payload': {'field': 'value'},
            'expected_response': {'result': 'value'},
            'metadata': {'authorization': 'Bearer TOKEN'},
        }
    }
"""

from typing import Any, Dict, Optional

# Global examples registry
# Structure: {ServiceName: {MethodName: {description, payload, expected_response, metadata}}}
EXAMPLES_REGISTRY: Dict[str, Dict[str, Dict[str, Any]]] = {
    # Example: User Service
    "UserService": {
        "GetUser": {
            "description": "Get user by ID",
            "payload": {"user_id": 123},
            "expected_response": {
                "id": 123,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2025-01-01T00:00:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_TOKEN"},
        },
        "ListUsers": {
            "description": "List users with pagination",
            "payload": {"page": 1, "page_size": 10, "filter": ""},
            "expected_response": {
                "users": [
                    {"id": 1, "username": "user1", "email": "user1@example.com"},
                    {"id": 2, "username": "user2", "email": "user2@example.com"},
                ],
                "total": 25,
                "page": 1,
                "page_size": 10,
            },
            "metadata": {"authorization": "Bearer YOUR_TOKEN"},
        },
        "CreateUser": {
            "description": "Create a new user",
            "payload": {
                "username": "new_user",
                "email": "new@example.com",
                "password": "secure_password_123",
            },
            "expected_response": {
                "id": 456,
                "username": "new_user",
                "email": "new@example.com",
                "created_at": "2025-11-03T12:00:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_ADMIN_TOKEN"},
        },
        "UpdateUser": {
            "description": "Update user information",
            "payload": {
                "user_id": 123,
                "username": "updated_username",
                "email": "updated@example.com",
            },
            "expected_response": {
                "id": 123,
                "username": "updated_username",
                "email": "updated@example.com",
                "updated_at": "2025-11-03T12:00:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_TOKEN"},
        },
        "DeleteUser": {
            "description": "Delete user by ID",
            "payload": {"user_id": 123},
            "expected_response": {"success": True, "message": "User deleted"},
            "metadata": {"authorization": "Bearer YOUR_ADMIN_TOKEN"},
        },
    },
    # Example: Product Service
    "ProductService": {
        "GetProduct": {
            "description": "Get product by ID",
            "payload": {"product_id": 456},
            "expected_response": {
                "id": 456,
                "name": "Example Product",
                "price": 29.99,
                "currency": "USD",
                "in_stock": True,
            },
            "metadata": {},
        },
        "ListProducts": {
            "description": "List products with filters",
            "payload": {
                "page": 1,
                "page_size": 20,
                "category": "electronics",
                "min_price": 10.0,
                "max_price": 100.0,
            },
            "expected_response": {
                "products": [
                    {
                        "id": 1,
                        "name": "Product 1",
                        "price": 29.99,
                        "category": "electronics",
                    }
                ],
                "total": 50,
                "page": 1,
                "page_size": 20,
            },
            "metadata": {},
        },
        "CreateProduct": {
            "description": "Create a new product",
            "payload": {
                "name": "New Product",
                "description": "Product description",
                "price": 49.99,
                "currency": "USD",
                "category": "electronics",
            },
            "expected_response": {
                "id": 789,
                "name": "New Product",
                "price": 49.99,
                "created_at": "2025-11-03T12:00:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_ADMIN_TOKEN"},
        },
    },
    # Example: Order Service
    "OrderService": {
        "CreateOrder": {
            "description": "Create a new order",
            "payload": {
                "user_id": 123,
                "items": [
                    {"product_id": 456, "quantity": 2, "price": 29.99},
                    {"product_id": 789, "quantity": 1, "price": 49.99},
                ],
                "shipping_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "country": "USA",
                    "postal_code": "10001",
                },
            },
            "expected_response": {
                "order_id": "ORD-2025-001",
                "status": "pending",
                "total_amount": 109.97,
                "currency": "USD",
                "created_at": "2025-11-03T12:00:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_TOKEN"},
        },
        "GetOrder": {
            "description": "Get order by ID",
            "payload": {"order_id": "ORD-2025-001"},
            "expected_response": {
                "order_id": "ORD-2025-001",
                "user_id": 123,
                "status": "delivered",
                "total_amount": 109.97,
                "currency": "USD",
                "items": [
                    {"product_id": 456, "quantity": 2, "price": 29.99},
                    {"product_id": 789, "quantity": 1, "price": 49.99},
                ],
                "created_at": "2025-11-03T12:00:00Z",
                "delivered_at": "2025-11-05T15:30:00Z",
            },
            "metadata": {"authorization": "Bearer YOUR_TOKEN"},
        },
    },
}


def get_example(
    service_name: str, method_name: str
) -> Optional[Dict[str, Any]]:
    """
    Get example payload for a specific service method.

    Args:
        service_name: Name of the service (e.g., 'UserService')
        method_name: Name of the method (e.g., 'GetUser')

    Returns:
        Example dictionary with payload, expected_response, etc. or None

    Example:
        >>> example = get_example('UserService', 'GetUser')
        >>> example['payload']
        {'user_id': 123}
    """
    service_examples = EXAMPLES_REGISTRY.get(service_name)
    if not service_examples:
        return None

    method_example = service_examples.get(method_name)
    return method_example


def register_example(
    service_name: str,
    method_name: str,
    description: str,
    payload: Dict[str, Any],
    expected_response: Dict[str, Any],
    metadata: Optional[Dict[str, str]] = None,
) -> None:
    """
    Register a new example for a service method.

    Args:
        service_name: Name of the service
        method_name: Name of the method
        description: Description of what the method does
        payload: Example request payload
        expected_response: Example expected response
        metadata: Optional metadata (headers)

    Example:
        >>> register_example(
        ...     'MyService',
        ...     'MyMethod',
        ...     'Does something',
        ...     {'param': 'value'},
        ...     {'result': 'success'},
        ...     {'authorization': 'Bearer TOKEN'}
        ... )
    """
    if service_name not in EXAMPLES_REGISTRY:
        EXAMPLES_REGISTRY[service_name] = {}

    EXAMPLES_REGISTRY[service_name][method_name] = {
        "description": description,
        "payload": payload,
        "expected_response": expected_response,
        "metadata": metadata or {},
    }


__all__ = [
    "EXAMPLES_REGISTRY",
    "get_example",
    "register_example",
]
