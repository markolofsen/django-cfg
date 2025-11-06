"""
Generate Centrifugo WebSocket clients.

Usage:
    python manage.py generate_centrifugo
    make centrifugo

Workflow:
    1. Generate Centrifugo WebSocket clients (Python, TypeScript, Go)
    2. Copy TypeScript clients to Next.js admin (centrifugo/generated/)

Output:
    - openapi/centrifugo/python/: Python client
    - openapi/centrifugo/typescript/: TypeScript client
    - openapi/centrifugo/go/: Go client
    - django_admin/apps/admin/src/centrifugo/generated/: TypeScript client (copy)
"""

import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Generate Centrifugo WebSocket clients'

    def handle(self, *args, **options):
        self.stdout.write('🔌 Starting Centrifugo generation...')

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        projects_root = base_dir.parent
        openapi_dir = base_dir / "openapi"
        centrifugo_output_dir = openapi_dir / "centrifugo"

        # Step 1: Generate Centrifugo WebSocket clients
        self.stdout.write('\n⚙️  Generating Centrifugo WebSocket clients...')
        try:
            call_command(
                'generate_centrifugo_clients',
                output=str(centrifugo_output_dir),
                all=True,
                verbose=False
            )
            self.stdout.write(self.style.SUCCESS('✅ Centrifugo clients generated'))
            self.stdout.write(self.style.SUCCESS('   📁 Python: openapi/centrifugo/python/'))
            self.stdout.write(self.style.SUCCESS('   📁 TypeScript: openapi/centrifugo/typescript/'))
            self.stdout.write(self.style.SUCCESS('   📁 Go: openapi/centrifugo/go/'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Centrifugo generation failed: {e}'))
            import traceback
            traceback.print_exc()
            return

        # Step 2: Copy Centrifugo TypeScript clients to Next.js admin
        self.stdout.write('\n📦 Copying Centrifugo TypeScript clients to Next.js admin...')
        centrifugo_ts_source = centrifugo_output_dir / "typescript"
        admin_centrifugo_target = projects_root / "django_admin" / "apps" / "admin" / "src" / "centrifugo" / "generated"

        if centrifugo_ts_source.exists():
            try:
                # Remove old Centrifugo clients
                if admin_centrifugo_target.exists():
                    shutil.rmtree(admin_centrifugo_target)

                # Create target directory
                admin_centrifugo_target.mkdir(parents=True, exist_ok=True)

                # Copy only .ts files
                ts_files = list(centrifugo_ts_source.glob('*.ts'))
                if ts_files:
                    for ts_file in ts_files:
                        shutil.copy2(ts_file, admin_centrifugo_target / ts_file.name)

                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Centrifugo clients ({len(ts_files)} .ts files) → {admin_centrifugo_target.relative_to(projects_root)}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  No .ts files found in {centrifugo_ts_source.relative_to(base_dir)}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to copy Centrifugo clients: {e}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Centrifugo TypeScript clients not found at {centrifugo_ts_source.relative_to(base_dir)}'
            ))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n🎉 Centrifugo generation completed!'))
        self.stdout.write(self.style.SUCCESS('   📂 openapi/centrifugo: Full Centrifugo clients (Python, TypeScript, Go)'))
        self.stdout.write(self.style.SUCCESS('   🔌 Next.js admin: Centrifugo clients in src/centrifugo/generated/'))
