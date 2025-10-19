"""
Generate and deploy API clients for Django-CFG Example.

Usage:
    python manage.py generate_api

Workflow:
    1. Generate OpenAPI clients (django-cfg)
    2. Copy CFG → @api package
    3. Copy Profiles + Trading + Crypto → demo app
    4. Build @api package

Architecture:
    - @api package: CFG endpoints (shared across all apps)
    - Demo app: Profiles + Trading + Crypto in generated/
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
        self.stdout.write('⚙️  Generating OpenAPI clients...')
        try:
            call_command('generate_clients')
            self.stdout.write(self.style.SUCCESS('✅ OpenAPI clients generated'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Generation failed: {e}'))
            return

        # Paths setup
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        ts_source = base_dir / "openapi" / "clients" / "typescript"
        projects_root = base_dir.parent

        # Step 2: Copy CFG to @api package
        self.stdout.write('\n📦 Copying CFG to @api package...')
        ts_cfg_source = ts_source / "cfg"
        api_package_ts = projects_root / "frontend" / "packages" / "api" / "src" / "cfg" / "generated"

        if not ts_cfg_source.exists():
            self.stdout.write(self.style.ERROR(f'❌ CFG source not found: {ts_cfg_source}'))
            return

        try:
            # Remove old CFG
            if api_package_ts.exists():
                shutil.rmtree(api_package_ts)

            # Copy new CFG
            api_package_ts.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(ts_cfg_source, api_package_ts, dirs_exist_ok=True)

            self.stdout.write(self.style.SUCCESS(
                f'✅ CFG → {api_package_ts.relative_to(projects_root)}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to copy CFG: {e}'))
            return

        # Step 3: Copy Profiles + Trading + Crypto to demo app
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

        # Step 4: Build @api package
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
        self.stdout.write(self.style.SUCCESS('   📦 @api package: CFG endpoints (shared)'))
        self.stdout.write(self.style.SUCCESS('   🎨 demo app: Profiles + Trading + Crypto in generated/'))
