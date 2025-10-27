"""
Generate and deploy API clients for Django-CFG Example.

Usage:
    python manage.py generate_api
    make api

Workflow:
    1. Generate OpenAPI clients (django-cfg)
    2. Generate Centrifugo WebSocket RPC clients
    3. Copy Centrifugo TypeScript RPC clients → demo app (rpc/generated/)
    4. Copy Profiles + Trading + Crypto → demo app (api/generated/)
    5. Build @api package

Architecture:
    - Demo app:
        - api/generated/: Profiles + Trading + Crypto OpenAPI clients
        - rpc/generated/: Centrifugo WebSocket RPC clients (TypeScript)
    - opensdk/: Full Centrifugo WebSocket RPC clients (Python, TypeScript, Go)

Note:
    - CFG clients are NOT copied to @api package (Step 3 disabled)
"""

import shutil
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Generate and deploy API clients for Django-CFG Example'

    # API groups for demo app
    API_GROUPS = ['profiles', 'trading', 'crypto']

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting API generation...')

        # Step 1: Generate OpenAPI clients
        self.stdout.write('\n⚙️  Generating OpenAPI clients...')
        try:
            call_command('generate_clients')
            self.stdout.write(self.style.SUCCESS('✅ OpenAPI clients generated'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Generation failed: {e}'))
            return

        # Paths setup
        base_dir = Path(__file__).resolve().parent.parent.parent.parent

        # Step 2: Generate Centrifugo WebSocket RPC clients
        self.stdout.write('\n🔌 Generating Centrifugo WebSocket RPC clients...')
        opensdk_dir = base_dir / "opensdk"

        try:
            call_command('generate_centrifugo_clients',
                        output=str(opensdk_dir),
                        all=True,
                        verbose=False)
            self.stdout.write(self.style.SUCCESS('✅ Centrifugo clients generated'))
            self.stdout.write(self.style.SUCCESS(f'   📁 Python: opensdk/python/'))
            self.stdout.write(self.style.SUCCESS(f'   📁 TypeScript: opensdk/typescript/'))
            self.stdout.write(self.style.SUCCESS(f'   📁 Go: opensdk/go/'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Centrifugo generation failed: {e}'))
            self.stdout.write(self.style.WARNING('   (Continuing with OpenAPI clients only)'))
        ts_source = base_dir / "openapi" / "clients" / "typescript"
        projects_root = base_dir.parent

        # Step 3: Copy Centrifugo TypeScript RPC clients to demo app
        self.stdout.write('\n🔌 Copying Centrifugo TypeScript RPC clients to demo app...')
        centrifugo_ts_source = opensdk_dir / "typescript"
        demo_rpc_target = projects_root / "frontend" / "apps" / "demo" / "src" / "rpc" / "generated"

        if centrifugo_ts_source.exists():
            try:
                # Remove old RPC clients
                if demo_rpc_target.exists():
                    shutil.rmtree(demo_rpc_target)

                # Create target directory
                demo_rpc_target.mkdir(parents=True, exist_ok=True)

                # Copy only .ts files
                ts_files = list(centrifugo_ts_source.glob('*.ts'))
                if ts_files:
                    for ts_file in ts_files:
                        shutil.copy2(ts_file, demo_rpc_target / ts_file.name)

                    self.stdout.write(self.style.SUCCESS(
                        f'✅ Centrifugo RPC ({len(ts_files)} .ts files) → {demo_rpc_target.relative_to(projects_root)}'
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

        # Step 4: Copy Profiles + Trading + Crypto to demo app
        self.stdout.write('\n🎨 Copying Profiles + Trading + Crypto to demo app...')
        demo_api_base = projects_root / "frontend" / "apps" / "demo" / "src" / "api" / "generated"

        # Copy groups to demo app
        for group in self.API_GROUPS:
            group_source = ts_source / group
            group_target = demo_api_base / group

            if not group_source.exists():
                self.stdout.write(self.style.WARNING(f'⚠️  {group} not found, skipping'))
                continue

            try:
                # Remove old group
                if group_target.exists():
                    shutil.rmtree(group_target)

                # Copy new group
                group_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(group_source, group_target, dirs_exist_ok=True)

                self.stdout.write(self.style.SUCCESS(
                    f'✅ {group} → {group_target.relative_to(projects_root)}'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to copy {group}: {e}'))

        # Step 5: Build @api package
        self.stdout.write('\n🔨 Building @api package...')
        api_package_dir = projects_root / "frontend" / "packages" / "api"

        try:
            result = subprocess.run(
                ['pnpm', 'build'],
                cwd=str(api_package_dir),
                capture_output=True,
                text=True,
                check=True
            )
            self.stdout.write(self.style.SUCCESS('✅ @api package built successfully'))
            if result.stdout:
                self.stdout.write(result.stdout)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'❌ Build failed: {e}'))
            if e.stdout:
                self.stdout.write(e.stdout)
            if e.stderr:
                self.stdout.write(self.style.ERROR(e.stderr))
            return
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('❌ pnpm not found. Please install pnpm.'))
            return

        self.stdout.write(self.style.SUCCESS('\n🎉 API generation completed!'))
        self.stdout.write(self.style.SUCCESS('   🎨 demo app: Profiles + Trading + Crypto in api/generated/'))
        self.stdout.write(self.style.SUCCESS('   🔌 demo app: Centrifugo WebSocket RPC clients in rpc/generated/'))
        self.stdout.write(self.style.SUCCESS('   📂 opensdk: Full clients (Python, TypeScript, Go)'))
