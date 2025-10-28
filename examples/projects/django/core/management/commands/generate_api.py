"""
Generate and deploy API clients for Django-CFG Solution.

Usage:
    python manage.py generate_api
    make api

Workflow:
    1. Generate OpenAPI clients (django-cfg) with auto-copy to Next.js admin
    2. Generate Centrifugo WebSocket RPC clients
    3. Copy Centrifugo TypeScript RPC clients to Next.js admin (rpc/generated/)

Architecture:
    - Next.js admin (django_admin/apps/admin):
        - src/api/generated/: OpenAPI clients (auto-copied via NextJsAdminConfig)
        - src/rpc/generated/: Centrifugo WebSocket RPC clients (TypeScript)
    - opensdk/: Full Centrifugo WebSocket RPC clients (Python, TypeScript, Go)

Note:
    - Next.js admin gets OpenAPI clients via NextJsAdminConfig.auto_copy_api=true
    - Group 'cfg' is excluded from Next.js admin auto-copy
"""

import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Generate and deploy API clients for Django-CFG Solution'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting API generation...')

        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        projects_root = base_dir.parent

        # Step 1: Generate OpenAPI clients (includes auto-copy to Next.js admin)
        self.stdout.write('\n⚙️  Generating OpenAPI clients...')
        try:
            call_command('generate_clients')
            self.stdout.write(self.style.SUCCESS('✅ OpenAPI clients generated'))
            self.stdout.write(self.style.SUCCESS('   🎯 Auto-copied to Next.js admin via NextJsAdminConfig'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Generation failed: {e}'))
            return

        # Step 2: Generate Centrifugo WebSocket RPC clients
        self.stdout.write('\n🔌 Generating Centrifugo WebSocket RPC clients...')
        opensdk_dir = base_dir / "opensdk"

        try:
            call_command(
                'generate_centrifugo_clients',
                output=str(opensdk_dir),
                all=True,
                verbose=False
            )
            self.stdout.write(self.style.SUCCESS('✅ Centrifugo clients generated'))
            self.stdout.write(self.style.SUCCESS('   📁 Python: opensdk/python/'))
            self.stdout.write(self.style.SUCCESS('   📁 TypeScript: opensdk/typescript/'))
            self.stdout.write(self.style.SUCCESS('   📁 Go: opensdk/go/'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Centrifugo generation failed: {e}'))
            self.stdout.write(self.style.WARNING('   (Continuing with OpenAPI clients only)'))

        # Step 3: Copy Centrifugo TypeScript RPC clients to Next.js admin
        self.stdout.write('\n🔌 Copying Centrifugo TypeScript RPC clients to Next.js admin...')
        centrifugo_ts_source = opensdk_dir / "typescript"
        admin_rpc_target = projects_root / "django_admin" / "apps" / "admin" / "src" / "rpc" / "generated"

        if centrifugo_ts_source.exists():
            try:
                # Remove old RPC clients
                if admin_rpc_target.exists():
                    shutil.rmtree(admin_rpc_target)

                # Create target directory
                admin_rpc_target.mkdir(parents=True, exist_ok=True)

                # Copy only .ts files
                ts_files = list(centrifugo_ts_source.glob('*.ts'))
                if ts_files:
                    for ts_file in ts_files:
                        shutil.copy2(ts_file, admin_rpc_target / ts_file.name)

                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Centrifugo RPC ({len(ts_files)} .ts files) → {admin_rpc_target.relative_to(projects_root)}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'⚠️  No .ts files found in {centrifugo_ts_source.relative_to(base_dir)}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to copy Centrifugo RPC clients: {e}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Centrifugo TypeScript clients not found at {centrifugo_ts_source.relative_to(base_dir)}'
            ))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n🎉 API generation completed!'))
        self.stdout.write(self.style.SUCCESS('   🎯 Next.js admin: OpenAPI clients auto-copied to src/api/generated/'))
        self.stdout.write(self.style.SUCCESS('   🔌 Next.js admin: Centrifugo RPC clients in src/rpc/generated/'))
        self.stdout.write(self.style.SUCCESS('   📂 opensdk: Full Centrifugo clients (Python, TypeScript, Go)'))
