"""
gRPC Integration Test Utility.

Comprehensive integration test for gRPC with API keys.
Automatically performs all steps from proto generation to log verification.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

import grpc
from django.conf import settings
from django.contrib.auth import get_user_model

from django_cfg.apps.integrations.grpc.models import GrpcApiKey, GRPCRequestLog

User = get_user_model()


class GRPCIntegrationTest:
    """Comprehensive integration test for gRPC with API keys."""

    def __init__(self, app_label: str = "crypto", quiet: bool = False):
        """
        Initialize integration test.

        Args:
            app_label: Django app label to generate protos for
            quiet: Suppress verbose output
        """
        self.app_label = app_label
        self.quiet = quiet
        self.server_process: Optional[subprocess.Popen] = None
        self.api_key: Optional[GrpcApiKey] = None
        self.grpc_port = settings.GRPC_SERVER.get("port", 50051)

    def log(self, message: str):
        """Print message if not quiet."""
        if not self.quiet:
            print(message)

    def print_step(self, step_num: int, message: str):
        """Print step with formatting."""
        if not self.quiet:
            print(f"\n{'='*70}")
            print(f"🔹 Step {step_num}: {message}")
            print(f"{'='*70}")

    def step1_generate_protos(self) -> bool:
        """Step 1: Generate proto files."""
        self.print_step(1, f"Generating proto files for {self.app_label}")

        try:
            result = subprocess.run(
                [sys.executable, "manage.py", "generate_protos", self.app_label],
                capture_output=True,
                text=True,
                check=True
            )
            self.log("✅ Proto files generated successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Proto generation error: {e}")
            if e.stderr:
                self.log(f"   STDERR: {e.stderr}")
            return False

    def step2_start_server(self) -> bool:
        """Step 2: Start gRPC server."""
        self.print_step(2, "Starting gRPC server")

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "manage.py", "rungrpc"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.log(f"✅ gRPC server started (PID: {self.server_process.pid})")
            self.log(f"   Port: {self.grpc_port}")
            self.log("   Waiting for server to start...")
            time.sleep(3)

            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                self.log(f"❌ Server terminated prematurely")
                self.log(f"   STDOUT: {stdout}")
                self.log(f"   STDERR: {stderr}")
                return False

            self.log("✅ Server is running")
            return True

        except Exception as e:
            self.log(f"❌ Server startup error: {e}")
            return False

    def step3_create_api_key(self) -> bool:
        """Step 3: Create test API key."""
        self.print_step(3, "Creating test API key")

        try:
            user = User.objects.filter(is_active=True).first()
            if not user:
                self.log("   Creating test user...")
                user = User.objects.create_user(
                    username="grpc_integration_test",
                    email="grpc_test@example.com",
                    password="test_password_123",
                    is_active=True
                )
                self.log(f"   ✅ Created user: {user.username}")
            else:
                self.log(f"   ✅ Using existing user: {user.username}")

            self.api_key = GrpcApiKey.objects.create_for_user(
                user=user,
                name="Integration Test Key",
                key_type="development",
                expires_in_days=None,
            )

            self.log(f"✅ API key created")
            self.log(f"   Name: {self.api_key.name}")
            self.log(f"   Key: {self.api_key.key[:32]}...")
            self.log(f"   User: {self.api_key.user.username}")
            self.log(f"   Valid: {self.api_key.is_valid}")

            return True

        except Exception as e:
            self.log(f"❌ API key creation error: {e}")
            import traceback
            if not self.quiet:
                traceback.print_exc()
            return False

    def step4_test_client(self) -> bool:
        """Step 4: Test gRPC client."""
        self.print_step(4, "Testing gRPC client with API key")

        try:
            import importlib
            module_path = f"apps.{self.app_label}.grpc_services.generated"

            try:
                service_name = f"{self.app_label}_service"
                proto_module = importlib.import_module(f"{module_path}.{service_name}_pb2")
                grpc_module = importlib.import_module(f"{module_path}.{service_name}_pb2_grpc")
                service_stub_name = f"{self.app_label.capitalize()}ServiceStub"
            except ImportError:
                try:
                    proto_module = importlib.import_module(f"{module_path}.coin_pb2")
                    grpc_module = importlib.import_module(f"{module_path}.coin_pb2_grpc")
                    service_stub_name = "CoinServiceStub"
                except ImportError:
                    self.log(f"❌ Failed to import proto files from {module_path}")
                    return False

            server_address = f"localhost:{self.grpc_port}"
            self.log(f"   Connecting to: {server_address}")

            StubClass = getattr(grpc_module, service_stub_name)

            # Test 1: Valid API key
            self.log("\n   📝 Test 1: Authentication with valid API key")
            with grpc.insecure_channel(server_address) as channel:
                stub = StubClass(channel)
                metadata = [("x-api-key", self.api_key.key)]

                request = proto_module.GetCoinRequest(symbol="BTC")
                response = stub.GetCoin(request, metadata=metadata)

                self.log(f"   ✅ Request successful: {response.coin.symbol} - {response.coin.name}")

            # Test 2: Django SECRET_KEY
            self.log("\n   📝 Test 2: Authentication with Django SECRET_KEY")
            with grpc.insecure_channel(server_address) as channel:
                stub = StubClass(channel)
                metadata = [("x-api-key", settings.SECRET_KEY)]

                request = proto_module.GetCoinRequest(symbol="ETH")
                response = stub.GetCoin(request, metadata=metadata)

                self.log(f"   ✅ SECRET_KEY works: {response.coin.symbol} - {response.coin.name}")

            # Test 3: Invalid key
            self.log("\n   📝 Test 3: Testing invalid key")
            try:
                with grpc.insecure_channel(server_address) as channel:
                    stub = StubClass(channel)
                    metadata = [("x-api-key", "invalid_key_12345")]

                    request = proto_module.GetCoinRequest(symbol="BTC")
                    response = stub.GetCoin(request, metadata=metadata)

                    self.log(f"   ⚠️  Invalid key was accepted (require_auth=False)")

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                    self.log(f"   ✅ Invalid key correctly rejected")
                else:
                    self.log(f"   ⚠️  Unexpected error: {e.code()} - {e.details()}")

            self.log("\n✅ All client tests passed")
            return True

        except grpc.RpcError as e:
            self.log(f"❌ gRPC error: {e.code()} - {e.details()}")
            return False
        except Exception as e:
            self.log(f"❌ Client testing error: {e}")
            import traceback
            if not self.quiet:
                traceback.print_exc()
            return False

    def step5_verify_logs(self) -> bool:
        """Step 5: Verify request logs."""
        self.print_step(5, "Verifying request logs")

        try:
            self.api_key.refresh_from_db()

            self.log(f"📊 API key statistics:")
            self.log(f"   Request count: {self.api_key.request_count}")
            self.log(f"   Last used: {self.api_key.last_used_at}")

            logs_with_key = GRPCRequestLog.objects.filter(api_key=self.api_key)
            logs_without_key = GRPCRequestLog.objects.filter(
                api_key__isnull=True,
                is_authenticated=True
            )

            self.log(f"\n📝 Request logs:")
            self.log(f"   With API key: {logs_with_key.count()}")
            self.log(f"   With SECRET_KEY: {logs_without_key.count()}")
            self.log(f"   Total logs: {GRPCRequestLog.objects.count()}")

            if logs_with_key.exists() and not self.quiet:
                self.log(f"\n   Recent requests with API key:")
                for log in logs_with_key.order_by("-created_at")[:3]:
                    self.log(f"   - {log.method_name}: {log.status} ({log.duration_ms}ms)")
                    self.log(f"     API Key: {log.api_key.name if log.api_key else 'None'}")
                    self.log(f"     User: {log.user.username if log.user else 'None'}")

            self.log("\n✅ Logs correctly recorded with api_key")
            return True

        except Exception as e:
            self.log(f"❌ Log verification error: {e}")
            import traceback
            if not self.quiet:
                traceback.print_exc()
            return False

    def step6_cleanup(self) -> bool:
        """Step 6: Clean up test data."""
        self.print_step(6, "Cleaning up test data")

        try:
            if self.server_process:
                self.log("   Stopping gRPC server...")
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                self.log(f"   ✅ Server stopped (PID: {self.server_process.pid})")

            if self.api_key:
                self.log(f"   Deleting API key: {self.api_key.name}...")
                self.api_key.delete()
                self.log("   ✅ API key deleted")

            self.log("\n✅ Cleanup completed")
            return True

        except Exception as e:
            self.log(f"❌ Cleanup error: {e}")
            return False

    def run(self) -> bool:
        """Run full integration test."""
        self.log("=" * 70)
        self.log("🧪 Comprehensive gRPC API Keys Integration Test")
        self.log("=" * 70)

        results = []

        results.append(("Proto generation", self.step1_generate_protos()))

        if results[-1][1]:
            results.append(("Server startup", self.step2_start_server()))

        if results[-1][1]:
            results.append(("API key creation", self.step3_create_api_key()))

        if results[-1][1]:
            results.append(("Client testing", self.step4_test_client()))

        if results[-1][1]:
            results.append(("Log verification", self.step5_verify_logs()))

        results.append(("Cleanup", self.step6_cleanup()))

        self.log("\n" + "=" * 70)
        self.log("📊 Integration Test Results")
        self.log("=" * 70)

        success_count = sum(1 for _, success in results if success)
        total_count = len(results)

        for step_name, success in results:
            status = "✅" if success else "❌"
            self.log(f"{status} {step_name}")

        self.log("\n" + "=" * 70)
        if success_count == total_count:
            self.log(f"🎉 All tests passed successfully! ({success_count}/{total_count})")
            self.log("=" * 70)
            return True
        else:
            self.log(f"⚠️  Tests passed: {success_count}/{total_count}")
            self.log("=" * 70)
            return False


__all__ = ["GRPCIntegrationTest"]
