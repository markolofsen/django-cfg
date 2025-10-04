"""
Main document archive service.

Orchestrates the complete archive processing pipeline with synchronous processing.
"""

import os
import time
import tempfile
import hashlib
import logging
from typing import List, Dict, Any, Optional
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, Field, ValidationError

from ...models.archive import DocumentArchive, ArchiveType, ContentType
from ...models.document import DocumentCategory
from ...models.base import ProcessingStatus
from ..base import BaseService
from .exceptions import (
    ArchiveValidationError, 
    ArchiveProcessingError,
    ProcessingTimeoutError
)
from .extraction_service import ArchiveExtractionService, ExtractedItemData
from .chunking_service import ContextualChunkingService
from .vectorization_service import ArchiveVectorizationService

User = get_user_model()
logger = logging.getLogger(__name__)


class ArchiveUploadRequest(BaseModel):
    """Pydantic model for archive upload validation."""
    
    title: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = Field(None, max_length=2000)
    category_ids: List[str] = Field(default_factory=list)
    is_public: bool = Field(default=True)
    process_immediately: bool = Field(default=True)
    
    class Config:
        str_strip_whitespace = True


class ArchiveProcessingResult(BaseModel):
    """Result of archive processing operation."""
    
    archive_id: str
    status: str
    processing_time_ms: int
    items_processed: int
    chunks_created: int
    vectorized_chunks: int
    total_cost_usd: float
    error_message: Optional[str] = None


class DocumentArchiveService(BaseService):
    """Main service for document archive operations."""
    
    # Processing limits
    MAX_ARCHIVE_SIZE = 200 * 1024 * 1024  # 200MB
    MAX_ITEMS_COUNT = 2000
    MAX_PROCESSING_TIME = 120  # 2 minutes
    
    def __init__(self, user: User):
        super().__init__(user)
        self.extraction_service = ArchiveExtractionService()
        self.chunking_service = ContextualChunkingService(user)
        self.vectorization_service = ArchiveVectorizationService(user)
    
    def create_and_process_archive(
        self,
        uploaded_file: UploadedFile,
        request_data: Dict[str, Any]
    ) -> ArchiveProcessingResult:
        """Create archive and process it synchronously."""
        
        # Validate request data
        try:
            validated_request = ArchiveUploadRequest(**request_data)
        except ValidationError as e:
            raise ArchiveValidationError(
                message="Invalid request data",
                code="INVALID_REQUEST",
                details={"validation_errors": e.errors()}
            )
        
        # Create archive record
        archive = self._create_archive_record(uploaded_file, validated_request)
        
        # Process synchronously if requested
        if validated_request.process_immediately:
            return self._process_archive_sync(archive, uploaded_file)
        else:
            return ArchiveProcessingResult(
                archive_id=str(archive.id),
                status=archive.processing_status,
                processing_time_ms=0,
                items_processed=0,
                chunks_created=0,
                vectorized_chunks=0,
                total_cost_usd=0.0
            )
    
    def process_archive(self, archive: DocumentArchive) -> bool:
        """Process an existing archive by its stored file."""
        
        # Debug logging
        logger.info(f"process_archive called with archive: {archive}, type: {type(archive)}")
        
        if not archive:
            raise ArchiveProcessingError(
                message="Archive object is None",
                code="ARCHIVE_IS_NONE"
            )
        
        if not archive.archive_file:
            raise ArchiveProcessingError(
                message="Archive has no file to process",
                code="NO_FILE"
            )
        
        start_time = time.time()
        
        try:
            # Update status
            archive.processing_status = ProcessingStatus.PROCESSING
            archive.save()
            
            # Get file path from the archive_file field
            file_path = archive.archive_file.path
            
            # Extract archive
            extracted_items = self.extraction_service.extract_archive(
                file_path, 
                archive.archive_type
            )
            
            # Check processing time
            self._check_processing_timeout(start_time)
            
            # Create item records
            items = self._create_item_records(archive, extracted_items)
            
            # Check processing time again
            self._check_processing_timeout(start_time)
            
            # Generate chunks
            chunks = self._generate_chunks_for_items(items)
            
            # Check processing time again
            self._check_processing_timeout(start_time)
            
            # Vectorize chunks
            vectorization_result = self._vectorize_chunks(chunks)
            
            # Update archive statistics
            self._update_archive_statistics(archive, items, chunks, vectorization_result)
            
            # Mark as completed
            processing_time_ms = int((time.time() - start_time) * 1000)
            archive.processing_status = ProcessingStatus.COMPLETED
            archive.processed_at = timezone.now()
            archive.processing_duration_ms = processing_time_ms
            archive.save()
            
            logger.info(f"Successfully processed archive {archive.id} in {processing_time_ms}ms")
            return True
            
        except ProcessingTimeoutError:
            processing_time_ms = int((time.time() - start_time) * 1000)
            archive.processing_status = ProcessingStatus.FAILED
            archive.processing_error = "Processing timeout exceeded"
            archive.processing_duration_ms = processing_time_ms
            archive.save()
            logger.error(f"Archive processing timeout for {archive.id}")
            return False
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            archive.processing_status = ProcessingStatus.FAILED
            archive.processing_error = str(e)
            archive.processing_duration_ms = processing_time_ms
            archive.save()
            logger.error(f"Archive processing failed for {archive.id}: {e}")
            return False

    def _create_archive_record(
        self,
        uploaded_file: UploadedFile,
        request: ArchiveUploadRequest
    ) -> DocumentArchive:
        """Create initial archive record."""
        
        # Validate file
        self._validate_uploaded_file(uploaded_file)
        
        # Generate content hash
        content_hash = self._generate_file_hash(uploaded_file)
        
        # Check for duplicates
        existing = DocumentArchive.objects.filter(
            user=self.user,
            content_hash=content_hash
        ).first()
        
        if existing:
            raise ArchiveValidationError(
                message=f"Archive already exists: {existing.title}",
                code="DUPLICATE_ARCHIVE",
                details={"existing_archive_id": str(existing.id)}
            )
        
        # Detect archive type
        archive_type = self._detect_archive_type(uploaded_file.name)
        
        with transaction.atomic():
            # Create archive record
            archive = DocumentArchive.objects.create(
                user=self.user,
                title=request.title,
                description=request.description,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                archive_type=archive_type,
                content_hash=content_hash,
                is_public=request.is_public,
                processing_status=ProcessingStatus.PENDING
            )
            
            # Add categories
            if request.category_ids:
                categories = DocumentCategory.objects.filter(
                    id__in=request.category_ids
                )
                archive.categories.set(categories)
        
        return archive
    
    def _process_archive_sync(
        self,
        archive: DocumentArchive,
        uploaded_file: UploadedFile
    ) -> ArchiveProcessingResult:
        """Process archive synchronously with time limits."""
        
        start_time = time.time()
        
        try:
            # Update status
            archive.processing_status = ProcessingStatus.PROCESSING
            archive.save()
            
            # Save file temporarily
            temp_file_path = self._save_temp_file(uploaded_file, archive.id)
            
            try:
                # Extract archive
                extracted_items = self.extraction_service.extract_archive(
                    temp_file_path, 
                    archive.archive_type
                )
                
                # Check processing time
                self._check_processing_timeout(start_time)
                
                # Create item records
                items = self._create_item_records(archive, extracted_items)
                
                # Check processing time
                self._check_processing_timeout(start_time)
                
                # Generate chunks
                all_chunks = self._generate_chunks_for_items(items)
                
                # Check processing time
                self._check_processing_timeout(start_time)
                
                # Vectorize chunks
                vectorization_result = self._vectorize_chunks(all_chunks)
                
                # Update archive statistics
                self._update_archive_statistics(
                    archive, 
                    items, 
                    all_chunks, 
                    vectorization_result
                )
                
                # Mark as completed
                processing_time_ms = int((time.time() - start_time) * 1000)
                archive.processing_status = ProcessingStatus.COMPLETED
                archive.processed_at = timezone.now()
                archive.processing_duration_ms = processing_time_ms
                archive.save()
                
                return ArchiveProcessingResult(
                    archive_id=str(archive.id),
                    status=archive.processing_status,
                    processing_time_ms=processing_time_ms,
                    items_processed=len(items),
                    chunks_created=len(all_chunks),
                    vectorized_chunks=vectorization_result['vectorized_count'],
                    total_cost_usd=vectorization_result['total_cost']
                )
                
            finally:
                # Always cleanup temp file
                self._cleanup_temp_file(temp_file_path)
        
        except Exception as e:
            # Mark as failed
            processing_time_ms = int((time.time() - start_time) * 1000)
            archive.processing_status = ProcessingStatus.FAILED
            archive.processing_error = str(e)
            archive.processing_duration_ms = processing_time_ms
            archive.save()
            
            return ArchiveProcessingResult(
                archive_id=str(archive.id),
                status=archive.processing_status,
                processing_time_ms=processing_time_ms,
                items_processed=0,
                chunks_created=0,
                vectorized_chunks=0,
                total_cost_usd=0.0,
                error_message=str(e)
            )
    
    def _validate_uploaded_file(self, uploaded_file: UploadedFile) -> None:
        """Validate uploaded archive file."""
        
        # Size check
        if uploaded_file.size > self.MAX_ARCHIVE_SIZE:
            raise ArchiveValidationError(
                message=f"Archive too large: {uploaded_file.size} bytes",
                code="ARCHIVE_TOO_LARGE",
                details={
                    "file_size": uploaded_file.size,
                    "max_size": self.MAX_ARCHIVE_SIZE
                }
            )
        
        # Type check
        archive_type = self._detect_archive_type(uploaded_file.name)
        if not archive_type:
            raise ArchiveValidationError(
                message=f"Unsupported archive format: {uploaded_file.name}",
                code="UNSUPPORTED_FORMAT",
                details={"filename": uploaded_file.name}
            )
    
    def _detect_archive_type(self, filename: str) -> Optional[str]:
        """Detect archive type from filename."""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.zip'):
            return ArchiveType.ZIP
        elif filename_lower.endswith(('.tar.gz', '.tgz')):
            return ArchiveType.TAR_GZ
        elif filename_lower.endswith(('.tar.bz2', '.tbz2')):
            return ArchiveType.TAR_BZ2
        elif filename_lower.endswith('.tar'):
            return ArchiveType.TAR
        
        return None
    
    def _generate_file_hash(self, uploaded_file: UploadedFile) -> str:
        """Generate SHA-256 hash of uploaded file."""
        hash_sha256 = hashlib.sha256()
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        for chunk in uploaded_file.chunks():
            hash_sha256.update(chunk)
        
        # Reset file pointer again
        uploaded_file.seek(0)
        
        return hash_sha256.hexdigest()
    
    def _save_temp_file(self, uploaded_file: UploadedFile, archive_id: str) -> str:
        """Save uploaded file to temporary location."""
        temp_dir = tempfile.mkdtemp(prefix=f'archive_{archive_id}_')
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return temp_path
    
    def _cleanup_temp_file(self, temp_file_path: str) -> None:
        """Clean up temporary file and directory."""
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            
            # Remove directory if empty
            temp_dir = os.path.dirname(temp_file_path)
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass  # Directory not empty or other error
    
    def _check_processing_timeout(self, start_time: float) -> None:
        """Check if processing has exceeded time limit."""
        elapsed = time.time() - start_time
        if elapsed > self.MAX_PROCESSING_TIME:
            raise ProcessingTimeoutError(
                message=f"Processing timeout after {elapsed:.1f} seconds",
                code="PROCESSING_TIMEOUT",
                details={
                    "elapsed_seconds": elapsed,
                    "max_seconds": self.MAX_PROCESSING_TIME
                }
            )
    
    def _create_item_records(
        self, 
        archive: DocumentArchive, 
        extracted_items: List[ExtractedItemData]
    ) -> List:
        """Create ArchiveItem records from extracted data."""
        from ...models.archive import ArchiveItem
        
        if len(extracted_items) > self.MAX_ITEMS_COUNT:
            raise ArchiveValidationError(
                message=f"Too many items: {len(extracted_items)}",
                code="TOO_MANY_ITEMS",
                details={
                    "item_count": len(extracted_items),
                    "max_count": self.MAX_ITEMS_COUNT
                }
            )
        
        items = []
        
        # Note: Items should already be cleared by reprocess method
        
        with transaction.atomic():
            for item_data in extracted_items:
                item = ArchiveItem.objects.create(
                    user=self.user,
                    archive=archive,
                    relative_path=item_data.relative_path,
                    item_name=item_data.item_name,
                    file_size=item_data.file_size,
                    raw_content=item_data.content or '',
                    is_processable=item_data.is_processable,
                    metadata=item_data.metadata
                )
                items.append(item)
            
            # Update archive statistics
            archive.total_items = len(items)
            archive.processed_items = len(items)
            archive.save()
        
        return items
    
    def _generate_chunks_for_items(self, items: List) -> List:
        """Generate chunks for all processable items."""
        all_chunks = []
        
        for item in items:
            if item.is_processable and item.raw_content:
                chunks = self.chunking_service.create_chunks_with_context(item)
                all_chunks.extend(chunks)
                
                # Update item statistics
                item.chunks_count = len(chunks)
                item.save()
        
        return all_chunks
    
    def _vectorize_chunks(self, chunks: List) -> Dict[str, Any]:
        """Vectorize all chunks."""
        return self.vectorization_service.vectorize_chunks_batch(chunks)
    
    def _update_archive_statistics(
        self,
        archive: DocumentArchive,
        items: List,
        chunks: List,
        vectorization_result: Dict[str, Any]
    ) -> None:
        """Update archive with final statistics."""
        
        total_tokens = sum(item.total_tokens for item in items)
        total_cost = sum(item.processing_cost for item in items)
        
        archive.total_chunks = len(chunks)
        archive.vectorized_chunks = vectorization_result['vectorized_count']
        archive.total_tokens = total_tokens
        archive.total_cost_usd = total_cost
        archive.save()
    
    def get_archive_by_id(self, archive_id: str) -> Optional[DocumentArchive]:
        """Get archive by ID with user access check."""
        try:
            archive = DocumentArchive.objects.get(id=archive_id, user=self.user)
            return archive
        except DocumentArchive.DoesNotExist:
            return None
    
    def list_user_archives(
        self,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List user's archives with pagination."""
        
        queryset = DocumentArchive.objects.filter(user=self.user)
        
        if status_filter:
            queryset = queryset.filter(processing_status=status_filter)
        
        total_count = queryset.count()
        archives = list(queryset.order_by('-created_at')[offset:offset + limit])
        
        return {
            'archives': archives,
            'total_count': total_count,
            'has_more': offset + limit < total_count
        }
    
    def delete_archive(self, archive_id: str) -> bool:
        """Delete archive and all related data."""
        try:
            archive = DocumentArchive.objects.get(id=archive_id, user=self.user)
            archive.delete()
            return True
        except DocumentArchive.DoesNotExist:
            return False
