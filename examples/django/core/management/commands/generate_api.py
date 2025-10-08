"""
Generate and deploy API clients for Django-CFG Example.

Usage:
    python manage.py generate_api

Workflow:
    1. Generate OpenAPI clients (django-revolution)
    2. Copy TypeScript to ../api/generated (one level up from django/)
"""

import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Generate and deploy API clients for Django-CFG Example'

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

        # Step 2: Copy TypeScript to parent directory
        self.stdout.write('🔄 Copying to API directory...')

        # base_dir is django-cfg-example/django
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        ts_source = base_dir / "openapi" / "clients" / "typescript"

        # Target: one level up from django/ -> django-cfg-example/api/generated
        target = base_dir.parent / "api" / "generated"

        if not ts_source.exists():
            self.stdout.write(self.style.ERROR(f'❌ TypeScript source not found: {ts_source}'))
            return

        try:
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(ts_source, target, dirs_exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'✅ Copied to: {target}'))
            self.stdout.write(self.style.SUCCESS('\n🎉 API generation completed!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to copy: {e}'))
