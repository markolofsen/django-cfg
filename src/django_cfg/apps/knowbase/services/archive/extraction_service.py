"""
Archive extraction services.

Handles extraction of different archive formats and content processing.
"""

import os
import zipfile
import tarfile
import tempfile
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel

from ...models.archive import ArchiveType, ContentType
from .exceptions import ExtractionError, ContentTypeDetectionError


class ExtractedItemData(BaseModel):
    """Data structure for extracted archive item."""
    
    relative_path: str
    item_name: str
    file_size: int
    content: Optional[str] = None
    content_hash: str
    is_processable: bool
    content_type: str
    language: Optional[str] = None
    metadata: Dict[str, Any]


class ArchiveExtractionService:
    """Service for extracting archives and processing content."""
    
    # File size limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
    
    # Text file extensions
    TEXT_EXTENSIONS: Set[str] = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
        '.cpp', '.c', '.h', '.hpp', '.php', '.rb', '.cs', '.swift',
        '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.elm',
        '.md', '.txt', '.rst', '.adoc',
        '.yml', '.yaml', '.json', '.toml', '.ini', '.cfg', '.conf',
        '.xml', '.html', '.css', '.scss', '.less',
        '.sql', '.sh', '.bash', '.zsh', '.fish',
        '.dockerfile', '.makefile', '.gitignore', '.env',
        '.tf', '.hcl'
    }
    
    def extract_archive(
        self, 
        archive_path: str, 
        archive_type: str
    ) -> List[ExtractedItemData]:
        """Extract archive and return processed item data."""
        
        extract_dir = tempfile.mkdtemp(prefix='extracted_')
        
        try:
            # Extract based on type
            file_list = self._extract_by_type(archive_path, archive_type, extract_dir)
            
            # Process extracted files
            extracted_items = []
            
            for relative_path in file_list:
                full_path = os.path.join(extract_dir, relative_path)
                
                # Skip directories
                if os.path.isdir(full_path):
                    continue
                
                # Skip unwanted files
                if self._should_skip_file(relative_path):
                    continue
                
                try:
                    item_data = self._process_extracted_file(full_path, relative_path)
                    if item_data:
                        extracted_items.append(item_data)
                except Exception as e:
                    # Log error but continue with other files
                    continue
            
            return extracted_items
            
        finally:
            # Always cleanup extraction directory
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
    
    def _extract_by_type(
        self, 
        archive_path: str, 
        archive_type: str, 
        extract_dir: str
    ) -> List[str]:
        """Extract archive based on its type."""
        
        try:
            if archive_type == ArchiveType.ZIP:
                return self._extract_zip(archive_path, extract_dir)
            elif archive_type in [ArchiveType.TAR, ArchiveType.TAR_GZ, ArchiveType.TAR_BZ2]:
                return self._extract_tar(archive_path, archive_type, extract_dir)
            else:
                raise ExtractionError(
                    message=f"Unsupported archive type: {archive_type}",
                    code="UNSUPPORTED_ARCHIVE_TYPE",
                    details={"archive_type": archive_type}
                )
        except Exception as e:
            if isinstance(e, ExtractionError):
                raise
            
            raise ExtractionError(
                message=f"Failed to extract archive: {str(e)}",
                code="EXTRACTION_FAILED",
                details={"archive_path": archive_path, "error": str(e)}
            ) from e
    
    def _extract_zip(self, archive_path: str, extract_dir: str) -> List[str]:
        """Extract ZIP archive."""
        with zipfile.ZipFile(archive_path, 'r') as zip_file:
            # Check for zip bomb
            self._check_zip_bomb(zip_file)
            
            zip_file.extractall(extract_dir)
            return zip_file.namelist()
    
    def _extract_tar(
        self, 
        archive_path: str, 
        archive_type: str, 
        extract_dir: str
    ) -> List[str]:
        """Extract TAR archive (including compressed variants)."""
        
        mode_map = {
            ArchiveType.TAR: 'r',
            ArchiveType.TAR_GZ: 'r:gz',
            ArchiveType.TAR_BZ2: 'r:bz2'
        }
        
        with tarfile.open(archive_path, mode_map[archive_type]) as tar_file:
            # Security check for path traversal
            self._check_tar_security(tar_file)
            
            tar_file.extractall(extract_dir)
            return tar_file.getnames()
    
    def _check_zip_bomb(self, zip_file: zipfile.ZipFile) -> None:
        """Check for zip bomb attacks."""
        
        total_uncompressed = 0
        total_compressed = 0
        
        for info in zip_file.infolist():
            total_uncompressed += info.file_size
            total_compressed += info.compress_size
        
        # Check compression ratio
        if total_compressed > 0:
            ratio = total_uncompressed / total_compressed
            if ratio > 100:  # Suspicious compression ratio
                raise ExtractionError(
                    message="Suspicious compression ratio detected",
                    code="ZIP_BOMB_DETECTED",
                    details={
                        "compression_ratio": ratio,
                        "uncompressed_size": total_uncompressed
                    }
                )
        
        # Check total uncompressed size
        if total_uncompressed > 1024 * 1024 * 1024:  # 1GB limit
            raise ExtractionError(
                message="Archive too large when uncompressed",
                code="ARCHIVE_TOO_LARGE_UNCOMPRESSED",
                details={"uncompressed_size": total_uncompressed}
            )
    
    def _check_tar_security(self, tar_file: tarfile.TarFile) -> None:
        """Check TAR file for security issues."""
        
        for member in tar_file.getmembers():
            # Check for path traversal
            if os.path.isabs(member.name) or ".." in member.name:
                raise ExtractionError(
                    message="Path traversal attempt detected",
                    code="PATH_TRAVERSAL_DETECTED",
                    details={"member_name": member.name}
                )
            
            # Check for suspicious file sizes
            if member.size > self.MAX_FILE_SIZE * 10:  # 100MB limit per file
                raise ExtractionError(
                    message="File too large in archive",
                    code="FILE_TOO_LARGE",
                    details={
                        "file_name": member.name,
                        "file_size": member.size
                    }
                )
    
    def _should_skip_file(self, relative_path: str) -> bool:
        """Check if file should be skipped during processing."""
        
        # Normalize path for consistent checking
        relative_path_lower = relative_path.lower()
        path_parts = relative_path_lower.split('/')
        
        # Check for hidden files (starting with dot)
        for part in path_parts:
            if part.startswith('.') and part not in ['.', '..']:
                return True
        
        # Check for system/build directories
        skip_directories = {
            '__pycache__', 'node_modules', 'dist', 'build', 'target',
            '.git', '.svn', '.hg', '.vscode', '.idea', '.eclipse'
        }
        
        for part in path_parts:
            if part in skip_directories:
                return True
        
        # Check file extensions
        skip_extensions = {
            '.pyc', '.pyo', '.tmp', '.temp', '.swp', '.bak',
            '.exe', '.dll', '.so', '.dylib', '.jar', '.war', '.ear', '.iso', '.dmg'
        }
        
        for ext in skip_extensions:
            if relative_path_lower.endswith(ext):
                return True
        
        # Check specific filenames
        filename = path_parts[-1] if path_parts else ''
        skip_filenames = {'.ds_store', 'thumbs.db'}
        
        if filename in skip_filenames:
            return True
        
        # Skip very deep paths (potential zip bomb)
        if relative_path.count('/') > 10:
            return True
        
        return False
    
    def _process_extracted_file(
        self, 
        full_path: str, 
        relative_path: str
    ) -> Optional[ExtractedItemData]:
        """Process individual extracted file."""
        
        try:
            stat = os.stat(full_path)
            file_size = stat.st_size
            
            # Skip very large files
            if file_size > self.MAX_FILE_SIZE:
                return None
            
            item_name = os.path.basename(relative_path)
            
            # Detect content type and processability
            content_type = self._detect_content_type(item_name, full_path)
            is_text_file = self._is_text_file(item_name, full_path)
            is_processable = is_text_file and content_type in [
                ContentType.DOCUMENT, 
                ContentType.CODE, 
                ContentType.DATA
            ]
            
            # Extract content for processable files
            content = None
            if is_processable:
                content = self._extract_text_content(full_path)
            
            # Generate content hash
            content_hash = self._generate_content_hash(full_path, content)
            
            # Detect language
            language = self._detect_language(item_name, content_type)
            
            # Build metadata
            metadata = {
                'mime_type': mimetypes.guess_type(item_name)[0] or 'application/octet-stream',
                'is_text_file': is_text_file,
                'extraction_method': 'direct_read' if is_text_file else 'binary_skip',
                'file_extension': Path(item_name).suffix.lower(),
            }
            
            return ExtractedItemData(
                relative_path=relative_path,
                item_name=item_name,
                file_size=file_size,
                content=content,
                content_hash=content_hash,
                is_processable=is_processable,
                content_type=content_type,
                language=language,
                metadata=metadata
            )
            
        except Exception as e:
            # Return None for problematic files
            return None
    
    def _detect_content_type(self, item_name: str, full_path: str) -> str:
        """Detect content type from file extension and content."""
        
        file_path = Path(item_name)
        extension = file_path.suffix.lower()
        
        # Code files
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.hpp', '.php', '.rb', '.cs', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.elm'
        }
        
        # Document files
        document_extensions = {
            '.md', '.txt', '.rst', '.adoc', '.pdf', '.docx', '.doc'
        }
        
        # Data files
        data_extensions = {
            '.json', '.csv', '.xml', '.yml', '.yaml', '.toml', '.ini'
        }
        
        # Image files
        image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'
        }
        
        # Archive files
        archive_extensions = {
            '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'
        }
        
        if extension in code_extensions:
            return ContentType.CODE
        elif extension in document_extensions:
            return ContentType.DOCUMENT
        elif extension in data_extensions:
            return ContentType.DATA
        elif extension in image_extensions:
            return ContentType.IMAGE
        elif extension in archive_extensions:
            return ContentType.ARCHIVE
        else:
            return ContentType.UNKNOWN
    
    def _is_text_file(self, item_name: str, full_path: str) -> bool:
        """Check if file is a text file."""
        
        # Check by extension first
        file_path = Path(item_name)
        extension = file_path.suffix.lower()
        
        if extension in self.TEXT_EXTENSIONS:
            return True
        
        # Special filenames
        special_names = {
            'dockerfile', 'makefile', 'readme', 'license', 'changelog',
            '.gitignore', '.dockerignore', '.env', '.settings.example'
        }
        
        if file_path.name.lower() in special_names:
            return True
        
        # Try to detect by content (sample first 1KB)
        try:
            with open(full_path, 'rb') as f:
                sample = f.read(1024)
            
            # Check for null bytes (binary indicator)
            if b'\x00' in sample:
                return False
            
            # Try to decode as UTF-8
            try:
                sample.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
                
        except Exception:
            return False
    
    def _extract_text_content(self, full_path: str) -> Optional[str]:
        """Extract text content from file."""
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(full_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        
                    # Validate content is reasonable
                    if len(content) > 0 and len(content) < 1024 * 1024:  # Max 1MB text
                        return content
                        
                except UnicodeDecodeError:
                    continue
                except Exception:
                    break
            
            return None
            
        except Exception:
            return None
    
    def _generate_content_hash(
        self, 
        full_path: str, 
        content: Optional[str]
    ) -> str:
        """Generate SHA-256 hash of file content."""
        
        if content:
            return hashlib.sha256(content.encode()).hexdigest()
        else:
            # Hash binary file
            hash_sha256 = hashlib.sha256()
            try:
                with open(full_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
                return hash_sha256.hexdigest()
            except Exception:
                # Fallback to path-based hash
                return hashlib.sha256(full_path.encode()).hexdigest()
    
    def _detect_language(self, item_name: str, content_type: str) -> Optional[str]:
        """Detect programming language from file extension."""
        
        if content_type != ContentType.CODE:
            return None
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.go': 'golang',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.clj': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.fs': 'fsharp',
            '.elm': 'elm',
        }
        
        file_path = Path(item_name)
        extension = file_path.suffix.lower()
        
        # Special cases
        if file_path.name.lower() in ['dockerfile']:
            return 'dockerfile'
        elif file_path.name.lower() in ['makefile']:
            return 'makefile'
        
        return language_map.get(extension)


class ContentExtractionService:
    """Service for extracting content from specific file types."""
    
    def extract_pdf_content(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file."""
        # TODO: Implement PDF text extraction
        # Could use PyPDF2, pdfplumber, or similar
        return None
    
    def extract_docx_content(self, file_path: str) -> Optional[str]:
        """Extract text from DOCX file."""
        # TODO: Implement DOCX text extraction
        # Could use python-docx
        return None
    
    def extract_image_text(self, file_path: str) -> Optional[str]:
        """Extract text from image using OCR."""
        # TODO: Implement OCR text extraction
        # Could use pytesseract
        return None
