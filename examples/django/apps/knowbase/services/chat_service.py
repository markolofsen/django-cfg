"""
RAG-powered chat service.
"""

from typing import List, Dict, Any, Optional
from django.utils import timezone
from django_cfg.modules.django_llm.llm.models import ChatCompletionResponse
from ..models import ChatSession, ChatMessage, DocumentChunk
from ..utils.validation import clean_search_results, safe_float
from .base import BaseService
from .search_service import SearchService
from .prompt_builder import SystemPromptBuilder


class ChatService(BaseService):
    """RAG-powered chat service with context management."""
    
    def __init__(self, user):
        super().__init__(user)
        self.search_service = SearchService(user)
    
    def create_session(
        self,
        title: str = "",
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_context_chunks: int = 5
    ) -> ChatSession:
        """Create new chat session."""
        
        session = ChatSession.objects.create(
            user=self.user,
            title=title or "New Chat Session",
            model_name=model_name,
            temperature=temperature,
            max_context_chunks=max_context_chunks,
            is_active=True
        )
        
        return session
    
    def process_query(
        self,
        session_id: str,
        query: str,
        max_tokens: int = 1000,
        include_sources: bool = True,
        enable_diagrams: bool = False
    ) -> Dict[str, Any]:
        """Process chat query with RAG context."""
        
        # Get session
        session = ChatSession.objects.get(
            id=session_id,
            user=self.user,
            is_active=True
        )
        
        # Perform universal semantic search for context (documents + archives + external data)
        # Using type-specific thresholds automatically
        raw_search_results = self.search_service.semantic_search_universal(
            query=query,
            limit=session.max_context_chunks,
            threshold=None,  # Use type-specific thresholds from configuration
            include_documents=True,
            include_archives=True,
            include_external=True
        )
        
        # Clean search results to remove invalid similarity scores
        search_results = clean_search_results(raw_search_results)
        
        # Build context messages
        context_messages = self._build_context_messages(
            session=session,
            query=query,
            search_results=search_results,
            enable_diagrams=enable_diagrams
        )
        
        # Generate LLM response (now returns ChatCompletionResponse Pydantic model)
        response: ChatCompletionResponse = self.llm_client.chat_completion(
            messages=context_messages,
            model=session.model_name,
            temperature=session.temperature,
            max_tokens=max_tokens
        )
        
        # Save user message
        context_chunk_ids = []
        for result in search_results:
            if result['type'] == 'document':
                context_chunk_ids.append(f"doc:{result['chunk'].id}")
            elif result['type'] == 'archive':
                context_chunk_ids.append(f"archive:{result['chunk'].id}")
            elif result['type'] == 'external_data':
                context_chunk_ids.append(f"external:{result['chunk'].id}")
        
        user_message = ChatMessage.objects.create(
            session=session,
            user=self.user,
            role=ChatMessage.MessageRole.USER,
            content=query,
            context_chunks=context_chunk_ids
        )
        
        # Save assistant response
        assistant_message = ChatMessage.objects.create(
            session=session,
            user=self.user,
            role=ChatMessage.MessageRole.ASSISTANT,
            content=response.content,
            tokens_used=response.tokens_used,
            cost_usd=response.cost_usd,
            processing_time_ms=int(response.processing_time * 1000),
            model_name=session.model_name,
            finish_reason=response.finish_reason
        )
        
        # Update session statistics (messages_count is handled by signals)
        session.total_tokens_used += response.tokens_used
        session.total_cost_usd = safe_float(session.total_cost_usd, 0.0) + safe_float(response.cost_usd, 0.0)
        session.save()
        
        # Auto-generate session title if empty
        if not session.title or session.title == "New Chat Session":
            session.title = query[:50] + "..." if len(query) > 50 else query
            session.save()
        
        result = {
            'message_id': str(assistant_message.id),
            'content': response.content,
            'tokens_used': response.tokens_used,
            'cost_usd': safe_float(response.cost_usd, 0.0),
            'processing_time_ms': int(response.processing_time * 1000),
            'model_used': session.model_name
        }
        
        if include_sources:
            # Search results are already cleaned by clean_search_results()
            result['sources'] = [
                {
                    'type': search_result['type'],
                    'source_title': search_result['source_title'],
                    'chunk_content': search_result['content'][:200] + "..." if len(search_result['content']) > 200 else search_result['content'],
                    'similarity': search_result['similarity'],  # Already validated
                    'metadata': search_result['metadata']
                }
                for search_result in search_results
            ]
        
        return result
    
    def _build_context_messages(
        self,
        session: ChatSession,
        query: str,
        search_results: List[Dict[str, Any]],
        enable_diagrams: bool = False
    ) -> List[Dict[str, str]]:
        """Build context messages for LLM."""
        
        messages = []
        
        # Build system message using SystemPromptBuilder
        if enable_diagrams:
            system_message = SystemPromptBuilder.build_diagram_enhanced_prompt(
                search_results=search_results if search_results else None
            )
        else:
            system_message = SystemPromptBuilder.build_conversation_prompt(
                search_results=search_results if search_results else None
            )
        
        messages.append({
            "role": "system",
            "content": system_message
        })
        
        # Add recent conversation history (last 5 messages)
        recent_messages = list(ChatMessage.objects.filter(
            session=session
        ).order_by('-created_at')[:5])
        
        # Reverse to get chronological order
        for message in reversed(recent_messages):
            messages.append({
                "role": message.role,
                "content": message.content
            })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        return messages
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat session message history."""
        
        # Verify session access
        session = ChatSession.objects.get(
            id=session_id,
            user=self.user
        )
        
        messages = ChatMessage.objects.filter(
            session=session
        ).order_by('created_at')[:limit]
        
        return list(messages)
    
    def list_sessions(self, active_only: bool = True) -> List[ChatSession]:
        """List user chat sessions."""
        
        queryset = ChatSession.objects.filter(user=self.user)
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return list(queryset.order_by('-created_at'))
    
    def delete_session(self, session_id: str) -> bool:
        """Delete chat session and all messages."""
        try:
            session = ChatSession.objects.get(
                id=session_id,
                user=self.user
            )
            session.delete()
            return True
        except ChatSession.DoesNotExist:
            return False
