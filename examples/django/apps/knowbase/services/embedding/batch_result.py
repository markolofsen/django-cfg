"""
Batch processing result builder.

This module provides a clean way to build BatchProcessingResult
from individual batch operations without using raw dicts.
"""

from typing import List
from .models import BatchProcessingResult, EmbeddingResult


class BatchResultBuilder:
    """Builder for BatchProcessingResult to avoid raw dict usage."""
    
    def __init__(self, total_chunks: int):
        self.total_chunks = total_chunks
        self.successful_chunks = 0
        self.failed_chunks = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.errors: List[str] = []
        self.start_time: float = 0.0
    
    def add_successful_result(self, result: EmbeddingResult) -> None:
        """Add a successful embedding result."""
        if result.success:
            self.successful_chunks += 1
            self.total_tokens += result.tokens
            self.total_cost += result.cost
        else:
            self.add_failed_result(result.error or "Unknown error")
    
    def add_failed_result(self, error: str) -> None:
        """Add a failed result."""
        self.failed_chunks += 1
        self.errors.append(error)
    
    def add_batch_results(self, results: List[EmbeddingResult]) -> None:
        """Add multiple results from a batch."""
        for result in results:
            if result.success:
                self.add_successful_result(result)
            else:
                self.add_failed_result(result.error or "Unknown error")
    
    def add_batch_error(self, error: str, chunk_count: int) -> None:
        """Add an error that affected an entire batch."""
        self.failed_chunks += chunk_count
        self.errors.append(error)
    
    def build(self, processing_time: float) -> BatchProcessingResult:
        """Build the final BatchProcessingResult."""
        return BatchProcessingResult(
            total_chunks=self.total_chunks,
            successful_chunks=self.successful_chunks,
            failed_chunks=self.failed_chunks,
            total_tokens=self.total_tokens,
            total_cost=self.total_cost,
            processing_time=processing_time,
            errors=self.errors
        )
