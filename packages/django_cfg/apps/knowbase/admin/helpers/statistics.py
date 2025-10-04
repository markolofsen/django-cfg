"""
Statistics calculation for document admin changelist views.

Provides reusable statistics aggregation logic for admin interfaces.
"""

from django.db.models import Count, Sum, Avg, Q


class DocumentStatistics:
    """Calculate statistics for document admin."""

    @staticmethod
    def get_document_stats(queryset):
        """
        Calculate document statistics.

        Args:
            queryset: Document queryset to aggregate

        Returns:
            dict: Statistics including counts, tokens, and costs
        """
        stats = queryset.aggregate(
            total_documents=Count('id'),
            total_chunks=Sum('chunks_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('total_cost_usd')
        )

        status_counts = dict(
            queryset.values_list('processing_status').annotate(
                count=Count('id')
            )
        )

        return {
            'total_documents': stats['total_documents'] or 0,
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_cost': f"${(stats['total_cost'] or 0):.6f}",
            'status_counts': status_counts
        }


class ChunkStatistics:
    """Calculate statistics for chunk admin."""

    @staticmethod
    def get_chunk_stats(queryset):
        """
        Calculate chunk statistics.

        Args:
            queryset: DocumentChunk queryset to aggregate

        Returns:
            dict: Statistics including counts, tokens, and costs
        """
        stats = queryset.aggregate(
            total_chunks=Count('id'),
            total_tokens=Sum('token_count'),
            total_characters=Sum('character_count'),
            total_embedding_cost=Sum('embedding_cost'),
            avg_tokens_per_chunk=Avg('token_count')
        )

        model_counts = dict(
            queryset.values_list('embedding_model').annotate(
                count=Count('id')
            )
        )

        return {
            'total_chunks': stats['total_chunks'] or 0,
            'total_tokens': stats['total_tokens'] or 0,
            'total_characters': stats['total_characters'] or 0,
            'total_embedding_cost': f"${(stats['total_embedding_cost'] or 0):.6f}",
            'avg_tokens_per_chunk': f"{(stats['avg_tokens_per_chunk'] or 0):.0f}",
            'model_counts': model_counts
        }


class CategoryStatistics:
    """Calculate statistics for category admin."""

    @staticmethod
    def get_category_stats(queryset):
        """
        Calculate category statistics.

        Args:
            queryset: DocumentCategory queryset to aggregate

        Returns:
            dict: Statistics including public/private counts
        """
        stats = queryset.aggregate(
            total_categories=Count('id'),
            public_categories=Count('id', filter=Q(is_public=True)),
            private_categories=Count('id', filter=Q(is_public=False))
        )

        return {
            'total_categories': stats['total_categories'] or 0,
            'public_categories': stats['public_categories'] or 0,
            'private_categories': stats['private_categories'] or 0
        }
