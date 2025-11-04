"""
Django management command for gRPC integration testing.

Usage:
    python manage.py test_grpc_integration
    python manage.py test_grpc_integration --app crypto
    python manage.py test_grpc_integration --quiet
"""

import sys

from django_cfg.management.utils import SafeCommand

from django_cfg.apps.integrations.grpc.utils import GRPCIntegrationTest


class Command(SafeCommand):
    command_name = 'test_grpc_integration'
    help = "Run comprehensive gRPC integration test with API keys"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            default="crypto",
            help="Django app label to test (default: crypto)",
        )
        parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Suppress verbose output",
        )

    def handle(self, *args, **options):
        app_label = options["app"]
        quiet = options["quiet"]

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(f"Starting gRPC integration test for app: {app_label}")
            )

        # Создаем и запускаем тест
        test = GRPCIntegrationTest(app_label=app_label, quiet=quiet)

        try:
            success = test.run()

            if success:
                self.stdout.write(
                    self.style.SUCCESS("\n✅ Integration test completed successfully!")
                )
                sys.exit(0)
            else:
                self.stdout.write(
                    self.style.ERROR("\n❌ Integration test failed!")
                )
                sys.exit(1)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("\n⚠️  Test interrupted by user")
            )
            test.step6_cleanup()
            sys.exit(1)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Critical error: {e}")
            )
            import traceback
            traceback.print_exc()
            test.step6_cleanup()
            sys.exit(1)
