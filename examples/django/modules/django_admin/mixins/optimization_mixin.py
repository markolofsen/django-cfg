"""
Query optimization mixin for performance.
"""

import logging
from typing import List, Dict, Any
from django.contrib import admin
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class OptimizedModelAdmin(admin.ModelAdmin):
    """Optimized ModelAdmin with automatic query optimization."""
    
    # Performance settings
    list_per_page = 50
    show_full_result_count = False
    
    # Fields for optimization - override in subclasses
    select_related_fields: List[str] = []
    prefetch_related_fields: List[str] = []
    annotations: Dict[str, Any] = {}
    
    def get_queryset(self, request) -> QuerySet:
        """Optimize queryset with select_related and prefetch_related."""
        qs = super().get_queryset(request)
        
        if self.select_related_fields:
            qs = qs.select_related(*self.select_related_fields)
            logger.debug(f"Applied select_related: {self.select_related_fields}")
        
        if self.prefetch_related_fields:
            qs = qs.prefetch_related(*self.prefetch_related_fields)
            logger.debug(f"Applied prefetch_related: {self.prefetch_related_fields}")
        
        if self.annotations:
            qs = qs.annotate(**self.annotations)
            logger.debug(f"Applied annotations: {list(self.annotations.keys())}")
        
        return qs
