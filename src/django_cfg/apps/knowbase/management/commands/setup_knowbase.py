"""
Setup command for Knowledge Base application.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    """Setup Knowledge Base with pgvector extension and initial data."""
    
    help = 'Setup Knowledge Base with pgvector extension and run migrations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-extensions',
            action='store_true',
            help='Skip creating PostgreSQL extensions',
        )
    
    def handle(self, *args, **options):
        """Execute the setup process."""
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Knowledge Base...')
        )
        
        # Step 1: Create PostgreSQL extensions
        if not options['skip_extensions']:
            self.create_extensions()
        
        
        self.stdout.write(
            self.style.SUCCESS('✅ Knowledge Base setup completed!')
        )
    
    def create_extensions(self):
        """Create required PostgreSQL extensions."""
        self.stdout.write('📦 Creating PostgreSQL extensions...')
        
        try:
            with connection.cursor() as cursor:
                # Create pgvector extension
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.stdout.write('  ✓ pgvector extension created')
                
                # Create pg_trgm for text search
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                self.stdout.write('  ✓ pg_trgm extension created')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Failed to create extensions: {e}')
            )
            self.stdout.write(
                self.style.WARNING('  ⚠️  You may need to create extensions manually as superuser')
            )
    