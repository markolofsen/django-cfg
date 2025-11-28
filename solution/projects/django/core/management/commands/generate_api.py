"""
Generate and deploy API clients for Django-CFG Solution.

Usage:
    python manage.py generate_api
    make api

Workflow:
    1. Generate OpenAPI clients (django-cfg) with auto-copy to Next.js admin

Architecture:
    - Next.js admin (django_admin/apps/admin):
        - src/api/generated/: OpenAPI clients (auto-copied via NextJsAdminConfig)

Note:
    - Next.js admin gets OpenAPI clients via NextJsAdminConfig.auto_copy_api=true
    - Group 'cfg' is excluded from Next.js admin auto-copy
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Generate and deploy API clients for Django-CFG Solution'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting API generation...')

        # Generate OpenAPI clients (includes auto-copy to Next.js admin)
        self.stdout.write('\n⚙️  Generating OpenAPI clients...')
        try:
            call_command('generate_clients')
            self.stdout.write(self.style.SUCCESS('✅ OpenAPI clients generated'))
            self.stdout.write(self.style.SUCCESS('   🎯 Auto-copied to Next.js admin via NextJsAdminConfig'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Generation failed: {e}'))
            return

        # Summary
        self.stdout.write(self.style.SUCCESS('\n🎉 API generation completed!'))
        self.stdout.write(self.style.SUCCESS('   🎯 Next.js admin: OpenAPI clients auto-copied to src/api/generated/'))
