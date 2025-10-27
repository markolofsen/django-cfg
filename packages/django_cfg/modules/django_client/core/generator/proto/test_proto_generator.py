"""
Simple test for Proto Generator.

This script demonstrates basic proto generation functionality.
Run with: python -m django_cfg.modules.django_client.core.generator.proto.test_proto_generator
"""

from django_cfg.modules.django_client.core.ir import (
    IRContext,
    IROperationObject,
    IRParameterObject,
    IRRequestBodyObject,
    IRResponseObject,
    IRSchemaObject,
    MediaTypeObject,
)
from django_cfg.modules.django_client.core.generator.proto import ProtoGenerator


def create_test_context() -> IRContext:
    """Create a simple test IR context."""

    # User schema
    user_schema = IRSchemaObject(
        name="User",
        type="object",
        properties={
            "id": IRSchemaObject(
                name="id",
                type="integer",
                format="int64",
                nullable=False,
            ),
            "username": IRSchemaObject(
                name="username",
                type="string",
                nullable=False,
            ),
            "email": IRSchemaObject(
                name="email",
                type="string",
                format="email",
                nullable=True,
            ),
            "status": IRSchemaObject(
                name="status",
                type="string",
                enum=["active", "inactive", "banned"],
                nullable=False,
            ),
            "created_at": IRSchemaObject(
                name="created_at",
                type="string",
                format="date-time",
                nullable=False,
            ),
        },
        required=["id", "username", "status", "created_at"],
    )

    # List users operation
    list_users_op = IROperationObject(
        operation_id="users_list",
        method="GET",
        path="/api/users/",
        tags=["Users"],
        description="List all users",
        parameters=[
            IRParameterObject(
                name="page",
                in_location="query",
                required=False,
                schema=IRSchemaObject(type="integer", format="int32"),
            ),
            IRParameterObject(
                name="page_size",
                in_location="query",
                required=False,
                schema=IRSchemaObject(type="integer", format="int32"),
            ),
        ],
        request_body=None,
        responses={
            200: IRResponseObject(
                description="Successful response",
                content={
                    "application/json": MediaTypeObject(
                        schema=IRSchemaObject(
                            type="array",
                            items=user_schema,
                        )
                    )
                },
            )
        },
    )

    # Create user operation
    create_user_op = IROperationObject(
        operation_id="users_create",
        method="POST",
        path="/api/users/",
        tags=["Users"],
        description="Create a new user",
        parameters=[],
        request_body=IRRequestBodyObject(
            required=True,
            content={
                "application/json": MediaTypeObject(
                    schema=IRSchemaObject(
                        name="UserRequest",
                        type="object",
                        properties={
                            "username": IRSchemaObject(
                                name="username",
                                type="string",
                            ),
                            "email": IRSchemaObject(
                                name="email",
                                type="string",
                                format="email",
                            ),
                        },
                        required=["username"],
                    )
                )
            },
        ),
        responses={
            201: IRResponseObject(
                description="User created",
                content={
                    "application/json": MediaTypeObject(schema=user_schema)
                },
            )
        },
    )

    # Get user operation
    get_user_op = IROperationObject(
        operation_id="users_retrieve",
        method="GET",
        path="/api/users/{id}/",
        tags=["Users"],
        description="Get user by ID",
        parameters=[
            IRParameterObject(
                name="id",
                in_location="path",
                required=True,
                schema=IRSchemaObject(type="integer", format="int64"),
            ),
        ],
        request_body=None,
        responses={
            200: IRResponseObject(
                description="Successful response",
                content={
                    "application/json": MediaTypeObject(schema=user_schema)
                },
            ),
            404: IRResponseObject(
                description="User not found",
                content={},
            ),
        },
    )

    # Delete user operation (empty response)
    delete_user_op = IROperationObject(
        operation_id="users_delete",
        method="DELETE",
        path="/api/users/{id}/",
        tags=["Users"],
        description="Delete a user",
        parameters=[
            IRParameterObject(
                name="id",
                in_location="path",
                required=True,
                schema=IRSchemaObject(type="integer", format="int64"),
            ),
        ],
        request_body=None,
        responses={
            204: IRResponseObject(
                description="User deleted",
                content={},
            )
        },
    )

    # Create IR context
    context = IRContext(
        schemas={"User": user_schema},
        operations={
            "users_list": list_users_op,
            "users_create": create_user_op,
            "users_retrieve": get_user_op,
            "users_delete": delete_user_op,
        },
        security_schemes={},
        request_models={},
        response_models={"User": user_schema},
        patch_models={},
        enum_schemas={},
        operations_by_tag={"Users": [list_users_op, create_user_op, get_user_op, delete_user_op]},
    )

    return context


def main():
    """Run basic proto generation test."""
    print("🧪 Testing Proto Generator...\n")

    # Create test context
    context = create_test_context()

    # Test 1: Combined file generation
    print("📝 Test 1: Generating combined api.proto file")
    generator = ProtoGenerator(
        context=context,
        split_files=False,
        package_name="test.api.v1",
    )

    files = generator.generate()
    print(f"✅ Generated {len(files)} file(s)")

    for file in files:
        print(f"\n{'=' * 60}")
        print(f"File: {file.path}")
        print(f"Description: {file.description}")
        print(f"Size: {len(file.content)} bytes")
        print(f"{'=' * 60}")
        print(file.content)

    # Test 2: Split files generation
    print("\n\n📝 Test 2: Generating split messages.proto and services.proto")
    generator_split = ProtoGenerator(
        context=context,
        split_files=True,
        package_name="test.api.v1",
    )

    split_files = generator_split.generate()
    print(f"✅ Generated {len(split_files)} file(s)")

    for file in split_files:
        print(f"\n{'=' * 60}")
        print(f"File: {file.path}")
        print(f"Description: {file.description}")
        print(f"Size: {len(file.content)} bytes")
        print(f"{'=' * 60}")
        print(file.content[:500] + "..." if len(file.content) > 500 else file.content)

    print("\n\n✅ All tests passed!")


if __name__ == "__main__":
    main()
