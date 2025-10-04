"""
Knowledge Base statistics command.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper
from django.db.models.functions import Extract
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Command(BaseCommand):
    """Display Knowledge Base statistics."""
    
    help = 'Display Knowledge Base usage statistics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Show statistics for specific user (username)',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics',
        )
    
    def handle(self, *args, **options):
        """Display statistics."""
        
        from ...models import Document, DocumentChunk, ChatSession, ChatMessage
        
        self.stdout.write(
            self.style.SUCCESS('📊 Knowledge Base Statistics')
        )
        self.stdout.write('=' * 50)
        
        # Filter by user if specified
        user_filter = {}
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                user_filter['user'] = user
                self.stdout.write(f"👤 User: {user.username}")
                self.stdout.write('-' * 30)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{options['user']}' not found")
                )
                return
        
        # Document statistics
        # Calculate processing duration in database
        processing_time_expr = ExpressionWrapper(
            Extract(F('processing_completed_at') - F('processing_started_at'), 'epoch'),
            output_field=models.FloatField()
        )
        
        doc_stats = Document.objects.filter(**user_filter).aggregate(
            total_docs=Count('id'),
            completed_docs=Count('id', filter=Q(processing_status='completed')),
            total_chunks=Sum('chunks_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd'),
            avg_processing_time=Avg(processing_time_expr, filter=Q(
                processing_started_at__isnull=False,
                processing_completed_at__isnull=False
            ))
        )
        
        self.stdout.write("📄 Documents:")
        self.stdout.write(f"  Total: {doc_stats['total_docs'] or 0}")
        self.stdout.write(f"  Completed: {doc_stats['completed_docs'] or 0}")
        self.stdout.write(f"  Success Rate: {((doc_stats['completed_docs'] or 0) / (doc_stats['total_docs'] or 1) * 100):.1f}%")
        
        self.stdout.write("\n📝 Content:")
        self.stdout.write(f"  Total Chunks: {doc_stats['total_chunks'] or 0}")
        self.stdout.write(f"  Total Tokens: {doc_stats['total_tokens'] or 0}")
        
        self.stdout.write("\n💰 Costs:")
        self.stdout.write(f"  Total Cost: ${(doc_stats['total_cost'] or 0):.6f}")
        
        # Chat statistics
        chat_stats = ChatSession.objects.filter(**user_filter).aggregate(
            total_sessions=Count('id'),
            active_sessions=Count('id', filter=Q(is_active=True)),
            total_messages=Sum('messages_count'),
            total_chat_tokens=Sum('total_tokens_used'),
            total_chat_cost=Sum('total_cost_usd')
        )
        
        self.stdout.write("\n💬 Chat:")
        self.stdout.write(f"  Total Sessions: {chat_stats['total_sessions'] or 0}")
        self.stdout.write(f"  Active Sessions: {chat_stats['active_sessions'] or 0}")
        self.stdout.write(f"  Total Messages: {chat_stats['total_messages'] or 0}")
        self.stdout.write(f"  Chat Tokens: {chat_stats['total_chat_tokens'] or 0}")
        self.stdout.write(f"  Chat Cost: ${(chat_stats['total_chat_cost'] or 0):.6f}")
        
        # Detailed statistics
        if options['detailed']:
            self.show_detailed_stats(user_filter)
    
    def show_detailed_stats(self, user_filter):
        """Show detailed statistics."""
        from ...models import Document, ChatSession
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📈 Detailed Statistics")
        self.stdout.write("=" * 50)
        
        # Processing status breakdown
        status_counts = Document.objects.filter(**user_filter).values(
            'processing_status'
        ).annotate(count=Count('id'))
        
        self.stdout.write("\n📊 Document Status Breakdown:")
        for status in status_counts:
            self.stdout.write(f"  {status['processing_status']}: {status['count']}")
        
        # Model usage breakdown
        model_counts = ChatSession.objects.filter(**user_filter).values(
            'model_name'
        ).annotate(count=Count('id'))
        
        self.stdout.write("\n🤖 Model Usage:")
        for model in model_counts:
            self.stdout.write(f"  {model['model_name']}: {model['count']} sessions")
        
        # Top documents by cost
        top_docs = Document.objects.filter(
            **user_filter
        ).order_by('-total_cost_usd')[:5]
        
        self.stdout.write("\n💸 Most Expensive Documents:")
        for doc in top_docs:
            self.stdout.write(f"  {doc.title[:40]}...: ${doc.total_cost_usd:.6f}")
        
        # Recent activity
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        recent_docs = Document.objects.filter(
            **user_filter,
            created_at__gte=week_ago
        ).count()
        
        recent_sessions = ChatSession.objects.filter(
            **user_filter,
            created_at__gte=week_ago
        ).count()
        
        self.stdout.write("\n📅 Recent Activity (Last 7 Days):")
        self.stdout.write(f"  New Documents: {recent_docs}")
        self.stdout.write(f"  New Chat Sessions: {recent_sessions}")
