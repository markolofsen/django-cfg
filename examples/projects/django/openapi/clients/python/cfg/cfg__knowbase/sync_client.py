from __future__ import annotations

import httpx

from .models import *


class SyncCfgKnowbaseAPI:
    """Synchronous API endpoints for Knowbase."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def admin_chat_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedChatResponseList]:
        """
        Chat query endpoints.
        """
        url = "/cfg/knowbase/admin/chat/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedChatResponseList.model_validate(item) for item in data.get("results", [])]


    def admin_chat_create(self, data: ChatResponseRequest) -> ChatResponse:
        """
        Chat query endpoints.
        """
        url = "/cfg/knowbase/admin/chat/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatResponse.model_validate(response.json())


    def admin_chat_retrieve(self, id: str) -> ChatResponse:
        """
        Chat query endpoints.
        """
        url = f"/cfg/knowbase/admin/chat/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ChatResponse.model_validate(response.json())


    def admin_chat_update(self, id: str, data: ChatResponseRequest) -> ChatResponse:
        """
        Chat query endpoints.
        """
        url = f"/cfg/knowbase/admin/chat/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatResponse.model_validate(response.json())


    def admin_chat_partial_update(self, id: str, data: PatchedChatResponseRequest | None = None) -> ChatResponse:
        """
        Chat query endpoints.
        """
        url = f"/cfg/knowbase/admin/chat/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return ChatResponse.model_validate(response.json())


    def admin_chat_destroy(self, id: str) -> None:
        """
        Chat query endpoints.
        """
        url = f"/cfg/knowbase/admin/chat/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def admin_chat_history_retrieve(self, id: str) -> ChatHistory:
        """
        Get chat history

        Get chat session history.
        """
        url = f"/cfg/knowbase/admin/chat/{id}/history/"
        response = self._client.get(url)
        response.raise_for_status()
        return ChatHistory.model_validate(response.json())


    def admin_chat_query_create(self, data: ChatQueryRequest) -> ChatResponse:
        """
        Process chat query with RAG

        Process chat query with RAG context.
        """
        url = "/cfg/knowbase/admin/chat/query/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatResponse.model_validate(response.json())


    def admin_documents_list(self, page: int | None = None, page_size: int | None = None, status: str | None = None) -> list[PaginatedDocumentList]:
        """
        List user documents

        List user documents with filtering and pagination.
        """
        url = "/cfg/knowbase/admin/documents/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "status": status if status is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedDocumentList.model_validate(item) for item in data.get("results", [])]


    def admin_documents_create(self, data: DocumentCreateRequest) -> Document:
        """
        Upload new document

        Upload and process a new knowledge document
        """
        url = "/cfg/knowbase/admin/documents/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Document.model_validate(response.json())


    def admin_documents_retrieve(self, id: str) -> Document:
        """
        Get document details

        Get document by ID.
        """
        url = f"/cfg/knowbase/admin/documents/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return Document.model_validate(response.json())


    def admin_documents_update(self, id: str, data: DocumentRequest) -> Document:
        """
        Document management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/admin/documents/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Document.model_validate(response.json())


    def admin_documents_partial_update(self, id: str, data: PatchedDocumentRequest | None = None) -> Document:
        """
        Document management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/admin/documents/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return Document.model_validate(response.json())


    def admin_documents_destroy(self, id: str) -> None:
        """
        Delete document

        Delete document and all associated chunks.
        """
        url = f"/cfg/knowbase/admin/documents/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def admin_documents_reprocess_create(self, id: str, data: DocumentRequest) -> Document:
        """
        Reprocess document

        Trigger reprocessing of document chunks and embeddings
        """
        url = f"/cfg/knowbase/admin/documents/{id}/reprocess/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return Document.model_validate(response.json())


    def admin_documents_status_retrieve(self, id: str) -> DocumentProcessingStatus:
        """
        Get document processing status

        Get document processing status.
        """
        url = f"/cfg/knowbase/admin/documents/{id}/status/"
        response = self._client.get(url)
        response.raise_for_status()
        return DocumentProcessingStatus.model_validate(response.json())


    def admin_documents_stats_retrieve(self) -> DocumentStats:
        """
        Get processing statistics

        Get user's document processing statistics.
        """
        url = "/cfg/knowbase/admin/documents/stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return DocumentStats.model_validate(response.json())


    def admin_sessions_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedChatSessionList]:
        """
        List user chat sessions

        List user chat sessions with filtering.
        """
        url = "/cfg/knowbase/admin/sessions/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedChatSessionList.model_validate(item) for item in data.get("results", [])]


    def admin_sessions_create(self, data: ChatSessionCreateRequest) -> ChatSession:
        """
        Create new chat session

        Create new chat session.
        """
        url = "/cfg/knowbase/admin/sessions/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def admin_sessions_retrieve(self, id: str) -> ChatSession:
        """
        Chat session management endpoints.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def admin_sessions_update(self, id: str, data: ChatSessionRequest) -> ChatSession:
        """
        Chat session management endpoints.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def admin_sessions_partial_update(self, id: str, data: PatchedChatSessionRequest | None = None) -> ChatSession:
        """
        Chat session management endpoints.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def admin_sessions_destroy(self, id: str) -> None:
        """
        Chat session management endpoints.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def admin_sessions_activate_create(self, id: str, data: ChatSessionRequest) -> ChatSession:
        """
        Activate chat session

        Activate chat session.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/activate/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def admin_sessions_archive_create(self, id: str, data: ChatSessionRequest) -> ChatSession:
        """
        Archive chat session

        Archive (deactivate) chat session.
        """
        url = f"/cfg/knowbase/admin/sessions/{id}/archive/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ChatSession.model_validate(response.json())


    def categories_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedPublicCategoryList]:
        """
        List public categories

        Get list of all public categories
        """
        url = "/cfg/knowbase/categories/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPublicCategoryList.model_validate(item) for item in data.get("results", [])]


    def categories_retrieve(self, id: str) -> PublicCategory:
        """
        Get public category details

        Get category details by ID (public access)
        """
        url = f"/cfg/knowbase/categories/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return PublicCategory.model_validate(response.json())


    def documents_list(self, category: str | None = None, page: int | None = None, page_size: int | None = None, search: str | None = None) -> list[PaginatedPublicDocumentListList]:
        """
        List public documents

        Get list of all completed and publicly accessible documents
        """
        url = "/cfg/knowbase/documents/"
        response = self._client.get(url, params={"category": category if category is not None else None, "page": page if page is not None else None, "page_size": page_size if page_size is not None else None, "search": search if search is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedPublicDocumentListList.model_validate(item) for item in data.get("results", [])]


    def documents_retrieve(self, id: str) -> PublicDocument:
        """
        Get public document details

        Get document details by ID (public access)
        """
        url = f"/cfg/knowbase/documents/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return PublicDocument.model_validate(response.json())


    def system_archives_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedDocumentArchiveListList]:
        """
        Document archive management endpoints - Admin only.
        """
        url = "/cfg/knowbase/system/archives/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedDocumentArchiveListList.model_validate(item) for item in data.get("results", [])]


    def system_archives_create(self, data: InlineRequestBody) -> ArchiveProcessingResult:
        """
        Upload and process archive

        Upload archive file and process it synchronously
        """
        url = "/cfg/knowbase/system/archives/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ArchiveProcessingResult.model_validate(response.json())


    def system_archives_retrieve(self, id: str) -> DocumentArchiveDetail:
        """
        Document archive management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/archives/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return DocumentArchiveDetail.model_validate(response.json())


    def system_archives_update(self, id: str, data: DocumentArchiveRequest) -> DocumentArchive:
        """
        Document archive management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/archives/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return DocumentArchive.model_validate(response.json())


    def system_archives_partial_update(self, id: str, data: PatchedDocumentArchiveRequest | None = None) -> DocumentArchive:
        """
        Document archive management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/archives/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return DocumentArchive.model_validate(response.json())


    def system_archives_destroy(self, id: str) -> None:
        """
        Document archive management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/archives/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def system_archives_file_tree_retrieve(self, id: str) -> None:
        """
        Get archive file tree

        Get hierarchical file tree structure
        """
        url = f"/cfg/knowbase/system/archives/{id}/file_tree/"
        response = self._client.get(url)
        response.raise_for_status()


    def system_archives_items_list(self, id: str, page: int | None = None, page_size: int | None = None) -> list[PaginatedArchiveItemList]:
        """
        Get archive items

        Get all items in the archive
        """
        url = f"/cfg/knowbase/system/archives/{id}/items/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedArchiveItemList.model_validate(item) for item in data.get("results", [])]


    def system_archives_search_create(self, id: str, data: ArchiveSearchRequestRequest, page: int | None = None, page_size: int | None = None) -> PaginatedArchiveSearchResultList:
        """
        Search archive chunks

        Semantic search within archive chunks
        """
        url = f"/cfg/knowbase/system/archives/{id}/search/"
        response = self._client.post(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None}, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return PaginatedArchiveSearchResultList.model_validate(response.json())


    def system_archives_revectorize_create(self, data: ChunkRevectorizationRequestRequest) -> VectorizationResult:
        """
        Re-vectorize chunks

        Re-vectorize specific chunks
        """
        url = "/cfg/knowbase/system/archives/revectorize/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return VectorizationResult.model_validate(response.json())


    def system_archives_statistics_retrieve(self) -> ArchiveStatistics:
        """
        Get archive statistics

        Get processing and vectorization statistics
        """
        url = "/cfg/knowbase/system/archives/statistics/"
        response = self._client.get(url)
        response.raise_for_status()
        return ArchiveStatistics.model_validate(response.json())


    def system_archives_vectorization_stats_retrieve(self) -> VectorizationStatistics:
        """
        Get vectorization statistics

        Get vectorization statistics for archives
        """
        url = "/cfg/knowbase/system/archives/vectorization_stats/"
        response = self._client.get(url)
        response.raise_for_status()
        return VectorizationStatistics.model_validate(response.json())


    def system_chunks_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedArchiveItemChunkList]:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = "/cfg/knowbase/system/chunks/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedArchiveItemChunkList.model_validate(item) for item in data.get("results", [])]


    def system_chunks_create(self, data: ArchiveItemChunkRequest) -> ArchiveItemChunk:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = "/cfg/knowbase/system/chunks/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ArchiveItemChunk.model_validate(response.json())


    def system_chunks_retrieve(self, id: str) -> ArchiveItemChunkDetail:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/chunks/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ArchiveItemChunkDetail.model_validate(response.json())


    def system_chunks_update(self, id: str, data: ArchiveItemChunkRequest) -> ArchiveItemChunk:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/chunks/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ArchiveItemChunk.model_validate(response.json())


    def system_chunks_partial_update(self, id: str, data: PatchedArchiveItemChunkRequest | None = None) -> ArchiveItemChunk:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/chunks/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return ArchiveItemChunk.model_validate(response.json())


    def system_chunks_destroy(self, id: str) -> None:
        """
        Archive item chunk management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/chunks/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def system_chunks_context_retrieve(self, id: str) -> ArchiveItemChunkDetail:
        """
        Get chunk context

        Get full context metadata for chunk
        """
        url = f"/cfg/knowbase/system/chunks/{id}/context/"
        response = self._client.get(url)
        response.raise_for_status()
        return ArchiveItemChunkDetail.model_validate(response.json())


    def system_chunks_vectorize_create(self, id: str, data: ArchiveItemChunkRequest) -> None:
        """
        Vectorize chunk

        Generate embedding for specific chunk
        """
        url = f"/cfg/knowbase/system/chunks/{id}/vectorize/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()


    def system_items_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedArchiveItemList]:
        """
        Archive item management endpoints - Admin only.
        """
        url = "/cfg/knowbase/system/items/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedArchiveItemList.model_validate(item) for item in data.get("results", [])]


    def system_items_create(self, data: ArchiveItemRequest) -> ArchiveItem:
        """
        Archive item management endpoints - Admin only.
        """
        url = "/cfg/knowbase/system/items/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ArchiveItem.model_validate(response.json())


    def system_items_retrieve(self, id: str) -> ArchiveItemDetail:
        """
        Archive item management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/items/{id}/"
        response = self._client.get(url)
        response.raise_for_status()
        return ArchiveItemDetail.model_validate(response.json())


    def system_items_update(self, id: str, data: ArchiveItemRequest) -> ArchiveItem:
        """
        Archive item management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/items/{id}/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return ArchiveItem.model_validate(response.json())


    def system_items_partial_update(self, id: str, data: PatchedArchiveItemRequest | None = None) -> ArchiveItem:
        """
        Archive item management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/items/{id}/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return ArchiveItem.model_validate(response.json())


    def system_items_destroy(self, id: str) -> None:
        """
        Archive item management endpoints - Admin only.
        """
        url = f"/cfg/knowbase/system/items/{id}/"
        response = self._client.delete(url)
        response.raise_for_status()


    def system_items_chunks_list(self, id: str, page: int | None = None, page_size: int | None = None) -> list[PaginatedArchiveItemChunkList]:
        """
        Get item chunks

        Get all chunks for this item
        """
        url = f"/cfg/knowbase/system/items/{id}/chunks/"
        response = self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedArchiveItemChunkList.model_validate(item) for item in data.get("results", [])]


    def system_items_content_retrieve(self, id: str) -> ArchiveItemDetail:
        """
        Get item content

        Get full content of archive item
        """
        url = f"/cfg/knowbase/system/items/{id}/content/"
        response = self._client.get(url)
        response.raise_for_status()
        return ArchiveItemDetail.model_validate(response.json())


