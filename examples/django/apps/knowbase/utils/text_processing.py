"""
Text processing utilities for document chunking and cleaning.
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from bs4 import BeautifulSoup, NavigableString


class ChunkConfig(BaseModel):
    """Pydantic configuration for text chunking."""
    
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=8000,
        description="Size of each text chunk in characters"
    )
    
    overlap: int = Field(
        default=200,
        ge=0,
        description="Overlap between consecutive chunks in characters"
    )
    
    separators: List[str] = Field(
        default_factory=lambda: ["\n\n", "\n", ". ", " "],
        description="List of separators for text splitting in order of preference"
    )
    
    @validator('overlap')
    def validate_overlap(cls, v, values):
        """Ensure overlap is less than chunk_size."""
        chunk_size = values.get('chunk_size', 1000)
        if v >= chunk_size:
            raise ValueError(f"Overlap ({v}) must be less than chunk_size ({chunk_size})")
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class TextProcessor:
    """Text cleaning and preprocessing utilities."""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        
        # First, check if content contains HTML and clean it
        if self.is_html_content(text):
            text = self.clean_html_content(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', '', text)
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Remove extra spaces around punctuation
        text = re.sub(r'\s+([\.,:;!?])', r'\1', text)
        text = re.sub(r'([\.,:;!?])\s+', r'\1 ', text)
        
        # Strip and normalize
        text = text.strip()
        
        return text
    
    def is_html_content(self, text: str) -> bool:
        """Detect if content contains HTML tags."""
        html_pattern = re.compile(r'<[^>]+>')
        return bool(html_pattern.search(text))
    
    def clean_html_content(self, html_content: str) -> str:
        """
        Convert HTML content to clean text while preserving structure.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Clean text with preserved structure
        """
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Convert to structured text
            text = self._extract_structured_text(soup)
            
            return text
            
        except Exception as e:
            # Fallback to simple tag removal if parsing fails
            text = re.sub(r'<[^>]+>', '', html_content)
            return text
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """Remove unwanted HTML elements."""
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'meta', 'link']):
            element.decompose()
        
        # Remove comments
        from bs4 import Comment
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove empty elements
        for element in soup.find_all():
            if not element.get_text(strip=True) and not element.name in ['br', 'hr', 'img']:
                element.decompose()
    
    def _extract_structured_text(self, soup: BeautifulSoup) -> str:
        """
        Extract text while preserving document structure.
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Structured text content
        """
        # Start with basic text extraction with proper spacing
        text = soup.get_text(separator=' ', strip=True)
        
        # Process specific elements for better structure
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text = element.get_text(strip=True)
            if header_text and header_text in text:
                text = text.replace(header_text, f'\n\n{header_text}\n')
        
        for element in soup.find_all(['li']):
            li_text = element.get_text(strip=True)
            if li_text and li_text in text:
                text = text.replace(li_text, f'\n• {li_text}')
        
        # Clean up excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
        text = re.sub(r'\n{3,}', '\n\n', text)  # More than 2 newlines to 2
        text = text.strip()
        
        return text
    
    def extract_metadata(self, text: str) -> dict:
        """Extract basic metadata from text."""
        
        lines = text.split('\n')
        
        metadata = {
            'character_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(lines),
            'paragraph_count': len([line for line in lines if line.strip()]),
            'has_code': bool(re.search(r'```|`[^`]+`', text)),
            'has_urls': bool(re.search(r'https?://\S+', text)),
            'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)),
            'is_html': self.is_html_content(text)
        }
        
        # Add HTML-specific metadata if content is HTML
        if metadata['is_html']:
            html_metadata = self._extract_html_metadata(text)
            metadata.update(html_metadata)
        
        return metadata
    
    def _extract_html_metadata(self, html_content: str) -> dict:
        """Extract HTML-specific metadata."""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Count different HTML elements
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            paragraphs = soup.find_all('p')
            lists = soup.find_all(['ul', 'ol'])
            list_items = soup.find_all('li')
            links = soup.find_all('a')
            images = soup.find_all('img')
            tables = soup.find_all('table')
            
            return {
                'html_headers_count': len(headers),
                'html_paragraphs_count': len(paragraphs),
                'html_lists_count': len(lists),
                'html_list_items_count': len(list_items),
                'html_links_count': len(links),
                'html_images_count': len(images),
                'html_tables_count': len(tables),
                'html_has_forms': bool(soup.find('form')),
                'html_has_media': bool(soup.find_all(['img', 'video', 'audio'])),
            }
        except:
            return {
                'html_parsing_error': True
            }


class SemanticChunker:
    """Intelligent text chunking with semantic awareness."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        # Handle None separators for backward compatibility
        if separators is None:
            separators = ["\n\n", "\n", ". ", " "]
            
        self.config = ChunkConfig(
            chunk_size=chunk_size,
            overlap=overlap,
            separators=separators
        )
    
    def create_chunks(self, text: str) -> List[str]:
        """Split text into semantic chunks."""
        
        if len(text) <= self.config.chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by separators in order of preference
        segments = self._split_by_separators(text, self.config.separators)
        
        for segment in segments:
            # If segment alone is too big, split it further
            if len(segment) > self.config.chunk_size:
                # Split large segment
                sub_chunks = self._split_large_segment(segment)
                
                # Add current chunk if it exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Add all but last sub-chunk
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1] if sub_chunks else ""
                
            # If adding segment would exceed chunk size
            elif len(current_chunk) + len(segment) > self.config.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = segment
            else:
                current_chunk += segment
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Add overlap between chunks
        if self.config.overlap > 0:
            chunks = self._add_overlap(chunks)
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _split_by_separators(self, text: str, separators: List[str]) -> List[str]:
        """Split text by separators in order of preference."""
        
        segments = [text]
        
        for separator in separators:
            new_segments = []
            for segment in segments:
                if separator in segment:
                    parts = segment.split(separator)
                    for i, part in enumerate(parts):
                        if i > 0:
                            new_segments.append(separator + part)
                        else:
                            new_segments.append(part)
                else:
                    new_segments.append(segment)
            segments = new_segments
        
        return segments
    
    def _split_large_segment(self, segment: str) -> List[str]:
        """Split a segment that's too large."""
        
        chunks = []
        start = 0
        
        while start < len(segment):
            end = start + self.config.chunk_size
            
            if end >= len(segment):
                chunks.append(segment[start:])
                break
            
            # Try to find a good breaking point
            break_point = self._find_break_point(segment, start, end)
            
            chunks.append(segment[start:break_point])
            start = break_point - self.config.overlap if break_point > self.config.overlap else break_point
        
        return chunks
    
    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """Find a good breaking point near the end position."""
        
        # Look for sentence endings
        for i in range(end - 1, start + self.config.chunk_size // 2, -1):
            if text[i] in '.!?':
                return i + 1
        
        # Look for paragraph breaks
        for i in range(end - 1, start + self.config.chunk_size // 2, -1):
            if text[i] == '\n':
                return i + 1
        
        # Look for word boundaries
        for i in range(end - 1, start + self.config.chunk_size // 2, -1):
            if text[i] == ' ':
                return i + 1
        
        # No good break point found, use hard limit
        return end
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between consecutive chunks."""
        
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            current_chunk = chunks[i]
            
            # Get overlap from previous chunk
            overlap_text = prev_chunk[-self.config.overlap:] if len(prev_chunk) > self.config.overlap else prev_chunk
            
            # Add overlap to current chunk
            overlapped_chunk = overlap_text + " " + current_chunk
            overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks


# Convenience function for backward compatibility
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Convenience function to chunk text with default settings.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunker = SemanticChunker(
        chunk_size=chunk_size,
        overlap=overlap
    )
    return chunker.create_chunks(text)
