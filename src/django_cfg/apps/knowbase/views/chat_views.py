"""
Chat API views for RAG-powered conversations.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..models import ChatSession
from ..services import ChatService
from ..serializers import (
    ChatSessionCreateSerializer,
    ChatSessionSerializer,
    ChatQuerySerializer,
    ChatResponseSerializer,
    ChatHistorySerializer
)
from .base import BaseKnowledgeViewSet


class ChatSessionViewSet(BaseKnowledgeViewSet):
    """Chat session management endpoints."""
    
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    service_class = ChatService
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ChatSessionCreateSerializer
        return ChatSessionSerializer
    
    @extend_schema(
        summary="Create new chat session",
        responses={201: ChatSessionSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new chat session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = self.get_service()
        session = service.create_session(
            title=serializer.validated_data['title'],
            model_name=serializer.validated_data['model_name'],
            temperature=serializer.validated_data['temperature'],
            max_context_chunks=serializer.validated_data['max_context_chunks']
        )
        
        response_serializer = ChatSessionSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="List user chat sessions",
        responses={200: ChatSessionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List user chat sessions with filtering."""
        # Add filtering by is_active
        queryset = self.get_queryset()
        
        # Filter by active status if requested
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Archive chat session",
        responses={200: ChatSessionSerializer}
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive (deactivate) chat session."""
        session = self.get_object()
        session.archive()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Activate chat session",
        responses={200: ChatSessionSerializer}
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate chat session."""
        session = self.get_object()
        session.activate()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)


class ChatViewSet(BaseKnowledgeViewSet):
    """Chat query endpoints."""
    
    service_class = ChatService
    serializer_class = ChatResponseSerializer
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'query':
            return ChatQuerySerializer
        elif self.action == 'history':
            return ChatHistorySerializer
        return ChatResponseSerializer
    
    @extend_schema(
        summary="Process chat query with RAG",
        request=ChatQuerySerializer,
        responses={200: ChatResponseSerializer},
        examples=[
            OpenApiExample(
                "Simple Query",
                value={
                    "query": "What is machine learning?",
                    "max_tokens": 1000,
                    "include_sources": True
                }
            )
        ]
    )
    @method_decorator(ratelimit(key='user', rate='30/m', method='POST'))
    @action(detail=False, methods=['post'])
    def query(self, request):
        """Process chat query with RAG context."""
        serializer = ChatQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = self.get_service()
        
        # Create session if not provided
        session_id = serializer.validated_data.get('session_id')
        if not session_id:
            session = service.create_session()
            session_id = str(session.id)
        else:
            session_id = str(session_id)
        
        # Process query
        result = service.process_query(
            session_id=session_id,
            query=serializer.validated_data['query'],
            max_tokens=serializer.validated_data['max_tokens'],
            include_sources=serializer.validated_data['include_sources']
        )
        
        return Response(result)
    
    @extend_schema(
        summary="Get chat history",
        responses={200: ChatHistorySerializer}
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get chat session history."""
        service = self.get_service()
        messages = service.get_session_history(session_id=pk)
        
        data = {
            'session_id': pk,
            'messages': messages,
            'total_messages': len(messages)
        }
        
        serializer = ChatHistorySerializer(data)
        return Response(serializer.data)