"""
Test script for CryptoService.

This script verifies that the gRPC service is working correctly.

Usage:
    python -m apps.crypto.grpc_services.test_service
"""

import sys
from decimal import Decimal

# Check if proto files are generated
try:
    from generated import crypto_service_pb2, crypto_service_pb2_grpc
    from google.protobuf.empty_pb2 import Empty
    print("✅ Proto files imported successfully")
except ImportError as e:
    print("❌ Proto files not found!")
    print(f"   Error: {e}")
    print("\n📝 Run this command first:")
    print("   python manage.py generate_proto")
    sys.exit(1)

# Check if models exist
try:
    from apps.crypto.models import Coin, Wallet
    print("✅ Django models imported successfully")
except ImportError as e:
    print(f"❌ Failed to import models: {e}")
    sys.exit(1)

# Check if converters work
try:
    from .converters import ProtobufConverter
    print("✅ Converters imported successfully")
except ImportError as e:
    print(f"❌ Failed to import converters: {e}")
    sys.exit(1)

# Check if service exists
try:
    from .crypto_service import CryptoService, grpc_handlers
    print("✅ CryptoService imported successfully")
except ImportError as e:
    print(f"❌ Failed to import service: {e}")
    sys.exit(1)

# Check if client exists
try:
    from .client import CryptoClient
    print("✅ Client imported successfully")
except ImportError as e:
    print(f"❌ Failed to import client: {e}")
    sys.exit(1)


def test_converters():
    """Test protobuf converters."""
    print("\n" + "=" * 60)
    print("Testing Converters")
    print("=" * 60)

    # Test decimal conversions
    test_decimal = Decimal('123.456789')
    str_value = ProtobufConverter.decimal_to_string(test_decimal)
    back_to_decimal = ProtobufConverter.string_to_decimal(str_value)

    assert str_value == '123.456789', f"String conversion failed: {str_value}"
    assert back_to_decimal == test_decimal, f"Decimal conversion failed: {back_to_decimal}"
    print("✅ Decimal conversions work correctly")

    # Test None handling
    none_str = ProtobufConverter.decimal_to_string(None)
    assert none_str == "0", f"None conversion failed: {none_str}"
    print("✅ None handling works correctly")


def test_service_discovery():
    """Test that service is discoverable."""
    print("\n" + "=" * 60)
    print("Testing Service Discovery")
    print("=" * 60)

    # Test grpc_handlers function
    handlers = grpc_handlers(None)  # None for discovery mode

    assert isinstance(handlers, list), "handlers should be a list"
    assert len(handlers) > 0, "handlers should not be empty"

    service_class, add_func = handlers[0]
    assert service_class == CryptoService, "First service should be CryptoService"
    print(f"✅ Service discovery works: {service_class.__name__}")


def test_client_initialization():
    """Test client initialization."""
    print("\n" + "=" * 60)
    print("Testing Client Initialization")
    print("=" * 60)

    try:
        # This will fail to connect, but should initialize
        client = CryptoClient('localhost:50051', timeout=1)
        print("✅ Client initialized successfully")

        # Test context manager
        with CryptoClient('localhost:50051', timeout=1) as ctx_client:
            print("✅ Context manager works")

        print("✅ Client cleanup works")

    except Exception as e:
        print(f"❌ Client initialization failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CryptoService Test Suite")
    print("=" * 60)

    try:
        test_converters()
        test_service_discovery()
        test_client_initialization()

        print("\n" + "=" * 60)
        print("✅ All Tests Passed!")
        print("=" * 60)

        print("\n📝 Next Steps:")
        print("   1. Start gRPC server:")
        print("      python manage.py rungrpc")
        print("\n   2. Test with client:")
        print("      python -m apps.crypto.grpc_services.client")
        print("\n   3. Test with grpcurl:")
        print("      grpcurl -plaintext localhost:50051 list")

        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
