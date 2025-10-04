"""
Django ORM toolset for database operations.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai import RunContext
from django.db import models
from django.apps import apps

from ..core.dependencies import DjangoDeps

logger = logging.getLogger(__name__)


class ORMToolset(AbstractToolset[DjangoDeps]):
    """
    Django ORM toolset for safe database operations.
    
    Provides tools for:
    - Model queries (read-only by default)
    - Data aggregation
    - Relationship traversal
    - Safe filtering
    """
    
    def __init__(self, read_only: bool = True, allowed_models: Optional[List[str]] = None):
        """
        Initialize ORM toolset.
        
        Args:
            read_only: If True, only allow read operations
            allowed_models: List of allowed models in format "app_label.model_name"
        """
        self.read_only = read_only
        self.allowed_models = set(allowed_models) if allowed_models else None
    
    @property
    def id(self) -> str:
        return "django_orm"
    
    def _check_model_access(self, app_label: str, model_name: str) -> bool:
        """Check if model access is allowed."""
        if self.allowed_models is None:
            return True
        
        model_key = f"{app_label}.{model_name}"
        return model_key in self.allowed_models
    
    def _get_model(self, app_label: str, model_name: str) -> models.Model:
        """Get Django model class with access check."""
        if not self._check_model_access(app_label, model_name):
            raise PermissionError(f"Access to model '{app_label}.{model_name}' not allowed")
        
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            raise ValueError(f"Model '{app_label}.{model_name}' not found")
    
    async def count_objects(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count objects in model with optional filters."""
        model = self._get_model(app_label, model_name)
        
        queryset = model.objects.all()
        
        if filters:
            # Apply safe filters
            safe_filters = self._sanitize_filters(filters)
            queryset = queryset.filter(**safe_filters)
        
        return await queryset.acount()
    
    async def get_object(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        object_id: Union[int, str]
    ) -> Optional[Dict[str, Any]]:
        """Get single object by ID."""
        model = self._get_model(app_label, model_name)
        
        try:
            obj = await model.objects.aget(pk=object_id)
            return self._serialize_object(obj)
        except model.DoesNotExist:
            return None
    
    async def list_objects(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """List objects with pagination and filtering."""
        model = self._get_model(app_label, model_name)
        
        queryset = model.objects.all()
        
        # Apply filters
        if filters:
            safe_filters = self._sanitize_filters(filters)
            queryset = queryset.filter(**safe_filters)
        
        # Apply ordering
        if order_by:
            # Sanitize order_by field
            order_field = order_by.lstrip('-')
            if hasattr(model, order_field):
                queryset = queryset.order_by(order_by)
        
        # Get total count
        total_count = await queryset.acount()
        
        # Apply pagination
        queryset = queryset[offset:offset + limit]
        
        # Serialize objects
        objects = []
        async for obj in queryset:
            objects.append(self._serialize_object(obj))
        
        return {
            'objects': objects,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_next': offset + limit < total_count,
            'has_previous': offset > 0,
        }
    
    async def aggregate_data(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        aggregations: Dict[str, str],
        filters: Optional[Dict[str, Any]] = None,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform aggregations on model data."""
        from django.db.models import Count, Sum, Avg, Max, Min
        
        model = self._get_model(app_label, model_name)
        
        queryset = model.objects.all()
        
        # Apply filters
        if filters:
            safe_filters = self._sanitize_filters(filters)
            queryset = queryset.filter(**safe_filters)
        
        # Prepare aggregation functions
        agg_functions = {
            'count': Count,
            'sum': Sum,
            'avg': Avg,
            'max': Max,
            'min': Min,
        }
        
        agg_kwargs = {}
        for alias, agg_spec in aggregations.items():
            if ':' in agg_spec:
                func_name, field_name = agg_spec.split(':', 1)
            else:
                func_name = agg_spec
                field_name = 'id'  # Default field
            
            if func_name.lower() in agg_functions:
                agg_func = agg_functions[func_name.lower()]
                if func_name.lower() == 'count':
                    agg_kwargs[alias] = agg_func(field_name)
                else:
                    agg_kwargs[alias] = agg_func(field_name)
        
        # Perform aggregation
        if group_by and hasattr(model, group_by):
            # Group by field
            result = []
            async for item in queryset.values(group_by).annotate(**agg_kwargs):
                result.append(item)
            return {'grouped_results': result}
        else:
            # Simple aggregation
            result = await queryset.aaggregate(**agg_kwargs)
            return result
    
    async def search_objects(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        search_fields: List[str],
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search objects using icontains on specified fields."""
        from django.db.models import Q
        
        model = self._get_model(app_label, model_name)
        
        # Build search query
        search_q = Q()
        for field in search_fields:
            if hasattr(model, field):
                search_q |= Q(**{f"{field}__icontains": query})
        
        if not search_q:
            return []
        
        # Execute search
        queryset = model.objects.filter(search_q)[:limit]
        
        results = []
        async for obj in queryset:
            results.append(self._serialize_object(obj))
        
        return results
    
    async def get_related_objects(
        self, 
        ctx: RunContext[DjangoDeps], 
        app_label: str, 
        model_name: str,
        object_id: Union[int, str],
        relation_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get related objects through foreign key or many-to-many."""
        model = self._get_model(app_label, model_name)
        
        try:
            obj = await model.objects.aget(pk=object_id)
        except model.DoesNotExist:
            return []
        
        # Check if relation exists
        if not hasattr(obj, relation_name):
            return []
        
        relation = getattr(obj, relation_name)
        
        # Handle different relation types
        if hasattr(relation, 'all'):
            # Many-to-many or reverse foreign key
            related_objects = relation.all()[:limit]
        else:
            # Single related object
            if relation:
                return [self._serialize_object(relation)]
            else:
                return []
        
        results = []
        async for related_obj in related_objects:
            results.append(self._serialize_object(related_obj))
        
        return results
    
    def _sanitize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize filters to prevent dangerous operations."""
        safe_filters = {}
        
        # Allowed lookup types
        allowed_lookups = {
            'exact', 'iexact', 'contains', 'icontains', 'startswith', 'istartswith',
            'endswith', 'iendswith', 'gt', 'gte', 'lt', 'lte', 'in', 'isnull',
            'date', 'year', 'month', 'day', 'week_day', 'hour', 'minute', 'second'
        }
        
        for key, value in filters.items():
            # Check for dangerous operations
            if '__' in key:
                field, lookup = key.rsplit('__', 1)
                if lookup in allowed_lookups:
                    safe_filters[key] = value
            else:
                # Direct field lookup (exact)
                safe_filters[key] = value
        
        return safe_filters
    
    def _serialize_object(self, obj: models.Model) -> Dict[str, Any]:
        """Serialize Django model object to dictionary."""
        data = {}
        
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            
            # Handle special field types
            if hasattr(value, 'isoformat'):
                # DateTime fields
                data[field.name] = value.isoformat()
            elif hasattr(value, '__dict__') and hasattr(value, 'pk'):
                # Related objects - just include ID and str representation
                data[field.name] = {
                    'id': value.pk,
                    'str': str(value)
                }
            else:
                data[field.name] = value
        
        # Add primary key and string representation
        data['pk'] = obj.pk
        data['str'] = str(obj)
        
        return data
