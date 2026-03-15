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
    OpenAPIInfo,
    DjangoGlobalMetadata,
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
        is_response_model=True,
    )

    # UserRequest schema
    user_request_schema = IRSchemaObject(
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
        is_request_model=True,
        related_response="User",
    )

    # List users operation
    list_users_op = IROperationObject(
        operation_id="users_list",
        http_method="GET",
        path="/api/users/",
        tags=["Users"],
        description="List all users",
        parameters=[
            IRParameterObject(
                name="page",
                location="query",
                schema_type="integer",
                required=False,
            ),
            IRParameterObject(
                name="page_size",
                location="query",
                schema_type="integer",
                required=False,
            ),
        ],
        request_body=None,
        responses={
            200: IRResponseObject(
                status_code=200,
                description="Successful response",
                schema_name="User",
                is_array=True,
                items_schema_name="User",
            )
        },
    )

    # Create user operation
    create_user_op = IROperationObject(
        operation_id="users_create",
        http_method="POST",
        path="/api/users/",
        tags=["Users"],
        description="Create a new user",
        parameters=[],
        request_body=IRRequestBodyObject(
            schema_name="UserRequest",
            required=True,
        ),
        responses={
            201: IRResponseObject(
                status_code=201,
                description="User created",
                schema_name="User",
            )
        },
    )

    # Get user operation
    get_user_op = IROperationObject(
        operation_id="users_retrieve",
        http_method="GET",
        path="/api/users/{id}/",
        tags=["Users"],
        description="Get user by ID",
        parameters=[
            IRParameterObject(
                name="id",
                location="path",
                schema_type="integer",
                required=True,
            ),
        ],
        request_body=None,
        responses={
            200: IRResponseObject(
                status_code=200,
                description="Successful response",
                schema_name="User",
            ),
            404: IRResponseObject(
                status_code=404,
                description="User not found",
                schema_name=None,
            ),
        },
    )

    # Delete user operation (empty response)
    delete_user_op = IROperationObject(
        operation_id="users_delete",
        http_method="DELETE",
        path="/api/users/{id}/",
        tags=["Users"],
        description="Delete a user",
        parameters=[
            IRParameterObject(
                name="id",
                location="path",
                schema_type="integer",
                required=True,
            ),
        ],
        request_body=None,
        responses={
            204: IRResponseObject(
                status_code=204,
                description="User deleted",
                schema_name=None,
            )
        },
    )

    # Create IR context
    context = IRContext(
        openapi_info=OpenAPIInfo(
            version="3.1.0",
            title="Test API",
            api_version="1.0.0",
        ),
        django_metadata=DjangoGlobalMetadata(
            component_split_request=True,
            component_split_patch=True,
        ),
        schemas={
            "User": user_schema,
            "UserRequest": user_request_schema,
        },
        operations={
            "users_list": list_users_op,
            "users_create": create_user_op,
            "users_retrieve": get_user_op,
            "users_delete": delete_user_op,
        },
    )

    return context


def test_combined_proto_generation():
    """Test 1: Combined file generation."""
    context = create_test_context()

    generator = ProtoGenerator(
        context=context,
        split_files=False,
        package_name="test.api.v1",
    )

    files = generator.generate()
    assert len(files) > 0, "Should generate at least one file"

    for file in files:
        assert file.path, "File should have a path"
        assert file.content, "File should have content"


def test_split_proto_generation():
    """Test 2: Split files generation."""
    context = create_test_context()

    generator_split = ProtoGenerator(
        context=context,
        split_files=True,
        package_name="test.api.v1",
    )

    split_files = generator_split.generate()
    assert len(split_files) > 0, "Should generate at least one file"

    for file in split_files:
        assert file.path, "File should have a path"
        assert file.content, "File should have content"


def main():
    """Run basic proto generation test."""
    print("Testing Proto Generator...\n")

    # Create test context
    context = create_test_context()

    # Test 1: Combined file generation
    print("Test 1: Generating combined api.proto file")
    generator = ProtoGenerator(
        context=context,
        split_files=False,
        package_name="test.api.v1",
    )

    files = generator.generate()
    print(f"Generated {len(files)} file(s)")

    for file in files:
        print(f"\n{'=' * 60}")
        print(f"File: {file.path}")
        print(f"Description: {file.description}")
        print(f"Size: {len(file.content)} bytes")
        print(f"{'=' * 60}")
        print(file.content)

    # Test 2: Split files generation
    print("\n\nTest 2: Generating split messages.proto and services.proto")
    generator_split = ProtoGenerator(
        context=context,
        split_files=True,
        package_name="test.api.v1",
    )

    split_files = generator_split.generate()
    print(f"Generated {len(split_files)} file(s)")

    for file in split_files:
        print(f"\n{'=' * 60}")
        print(f"File: {file.path}")
        print(f"Description: {file.description}")
        print(f"Size: {len(file.content)} bytes")
        print(f"{'=' * 60}")
        print(file.content[:500] + "..." if len(file.content) > 500 else file.content)

    print("\n\nAll tests passed!")


if __name__ == "__main__":
    main()
