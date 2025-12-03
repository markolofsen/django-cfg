"""
Django management command to download admin panel assets.

Use this command to:
- Pre-download admin.zip in CI/CD pipelines
- Prepare offline servers
- Force re-download corrupted assets

Usage:
    python manage.py download_admin          # Download if missing
    python manage.py download_admin --force  # Force re-download
    python manage.py download_admin --check  # Check status only
"""

from django.core.management.base import BaseCommand, CommandError

from django_cfg.apps.system.frontend.utils.downloader import (
    download_frontend_asset,
    get_asset_path,
    _needs_update,
    _get_package_version,
)


class Command(BaseCommand):
    help = 'Download admin panel assets from GitHub'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-download even if asset exists',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check status only, do not download',
        )

    def handle(self, *args, **options):
        force = options['force']
        check_only = options['check']

        # Get asset path
        asset_path = get_asset_path('admin')
        if not asset_path:
            raise CommandError('Admin asset not configured in FRONTEND_ASSETS')

        version_file = asset_path.with_suffix('.version')
        package_version = _get_package_version()

        # Status check
        if asset_path.exists():
            local_version = version_file.read_text().strip() if version_file.exists() else 'unknown'
            size_mb = asset_path.stat().st_size / (1024 * 1024)

            self.stdout.write(self.style.SUCCESS(
                f'\n  Admin panel status:\n'
                f'  -------------------\n'
                f'  Path:            {asset_path}\n'
                f'  Size:            {size_mb:.1f} MB\n'
                f'  Local version:   {local_version}\n'
                f'  Package version: {package_version}\n'
                f'  Needs update:    {_needs_update(asset_path)}\n'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'\n  Admin panel status:\n'
                f'  -------------------\n'
                f'  Status: NOT INSTALLED\n'
                f'  Path:   {asset_path}\n'
            ))

        # Check only mode
        if check_only:
            if asset_path.exists() and not _needs_update(asset_path):
                self.stdout.write(self.style.SUCCESS('  Status: UP TO DATE'))
                return

            if asset_path.exists():
                self.stdout.write(self.style.WARNING('  Status: UPDATE AVAILABLE'))
            else:
                self.stdout.write(self.style.ERROR('  Status: MISSING'))
            return

        # Download logic
        if asset_path.exists() and not force and not _needs_update(asset_path):
            self.stdout.write(self.style.SUCCESS(
                '\n  Admin panel is up to date. Use --force to re-download.'
            ))
            return

        # Download
        action = 'Re-downloading' if force else 'Downloading'
        self.stdout.write(f'\n  {action} admin panel from GitHub...\n')

        try:
            success = download_frontend_asset('admin', force=True)

            if success:
                size_mb = asset_path.stat().st_size / (1024 * 1024)
                self.stdout.write(self.style.SUCCESS(
                    f'\n  Download complete!\n'
                    f'  Size: {size_mb:.1f} MB\n'
                    f'  Path: {asset_path}\n'
                ))
            else:
                raise CommandError('Download failed. Check logs for details.')

        except Exception as e:
            raise CommandError(f'Download failed: {e}')
