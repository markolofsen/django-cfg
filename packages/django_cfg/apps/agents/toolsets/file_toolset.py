"""
Django file toolset for file operations.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai import RunContext
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from ..core.dependencies import DjangoDeps

logger = logging.getLogger(__name__)


class FileToolset(AbstractToolset[DjangoDeps]):
    """
    Django file toolset for safe file operations.
    
    Provides tools for:
    - File reading/writing (within allowed directories)
    - Media file handling
    - Static file operations
    - File metadata
    """
    
    def __init__(self, allowed_paths: Optional[List[str]] = None, max_file_size: int = 10 * 1024 * 1024):
        """
        Initialize file toolset.
        
        Args:
            allowed_paths: List of allowed directory paths (relative to MEDIA_ROOT)
            max_file_size: Maximum file size in bytes (default: 10MB)
        """
        self.allowed_paths = allowed_paths or ['orchestrator', 'temp']
        self.max_file_size = max_file_size
    
    @property
    def id(self) -> str:
        return "django_files"
    
    def _check_path_access(self, file_path: str) -> bool:
        """Check if file path is within allowed directories."""
        path = Path(file_path)
        
        # Normalize path and check if it's within allowed paths
        try:
            # Remove any parent directory traversal
            normalized_path = path.resolve()
            
            # Check against allowed paths
            for allowed_path in self.allowed_paths:
                allowed_full_path = Path(settings.MEDIA_ROOT) / allowed_path
                try:
                    normalized_path.relative_to(allowed_full_path.resolve())
                    return True
                except ValueError:
                    continue
            
            return False
        except Exception:
            return False
    
    def _get_safe_path(self, file_path: str, user_id: int) -> str:
        """Get safe file path with user scoping."""
        # Add user scoping to prevent access to other users' files
        safe_path = f"orchestrator/user_{user_id}/{file_path}"
        
        # Normalize and validate
        normalized = os.path.normpath(safe_path)
        
        # Ensure no directory traversal
        if '..' in normalized or normalized.startswith('/'):
            raise ValueError("Invalid file path")
        
        return normalized
    
    async def read_file(
        self, 
        ctx: RunContext[DjangoDeps], 
        file_path: str,
        encoding: str = 'utf-8'
    ) -> Optional[str]:
        """Read text file content."""
        user_id = ctx.deps.user.id
        safe_path = self._get_safe_path(file_path, user_id)
        
        try:
            if default_storage.exists(safe_path):
                with default_storage.open(safe_path, 'r') as f:
                    content = f.read()
                
                logger.debug(f"Read file: {safe_path} ({len(content)} chars)")
                return content
            else:
                logger.warning(f"File not found: {safe_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to read file '{safe_path}': {e}")
            return None
    
    async def write_file(
        self, 
        ctx: RunContext[DjangoDeps], 
        file_path: str,
        content: str,
        encoding: str = 'utf-8'
    ) -> bool:
        """Write text content to file."""
        user_id = ctx.deps.user.id
        safe_path = self._get_safe_path(file_path, user_id)
        
        # Check file size
        content_bytes = content.encode(encoding)
        if len(content_bytes) > self.max_file_size:
            logger.error(f"File too large: {len(content_bytes)} bytes > {self.max_file_size}")
            return False
        
        try:
            # Create directory if needed
            dir_path = os.path.dirname(safe_path)
            if dir_path and not default_storage.exists(dir_path):
                # Create directory structure
                parts = dir_path.split('/')
                current_path = ''
                for part in parts:
                    current_path = os.path.join(current_path, part) if current_path else part
                    if not default_storage.exists(current_path):
                        default_storage.save(f"{current_path}/.keep", ContentFile(b''))
            
            # Write file
            default_storage.save(safe_path, ContentFile(content_bytes))
            
            logger.debug(f"Wrote file: {safe_path} ({len(content_bytes)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Failed to write file '{safe_path}': {e}")
            return False
    
    async def delete_file(self, ctx: RunContext[DjangoDeps], file_path: str) -> bool:
        """Delete file."""
        user_id = ctx.deps.user.id
        safe_path = self._get_safe_path(file_path, user_id)
        
        try:
            if default_storage.exists(safe_path):
                default_storage.delete(safe_path)
                logger.debug(f"Deleted file: {safe_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {safe_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file '{safe_path}': {e}")
            return False
    
    async def list_files(
        self, 
        ctx: RunContext[DjangoDeps], 
        directory_path: str = "",
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List files in directory."""
        user_id = ctx.deps.user.id
        safe_path = self._get_safe_path(directory_path, user_id)
        
        try:
            if not default_storage.exists(safe_path):
                return []
            
            # List directory contents
            directories, files = default_storage.listdir(safe_path)
            
            results = []
            
            # Add directories
            for directory in directories:
                dir_path = os.path.join(safe_path, directory)
                results.append({
                    'name': directory,
                    'type': 'directory',
                    'path': dir_path,
                    'size': None,
                    'modified': None,
                })
            
            # Add files
            for file in files:
                file_path = os.path.join(safe_path, file)
                
                # Apply pattern filter if specified
                if pattern and pattern not in file:
                    continue
                
                try:
                    size = default_storage.size(file_path)
                    modified = default_storage.get_modified_time(file_path)
                    
                    results.append({
                        'name': file,
                        'type': 'file',
                        'path': file_path,
                        'size': size,
                        'modified': modified.isoformat() if modified else None,
                    })
                except Exception as e:
                    logger.warning(f"Could not get file info for '{file_path}': {e}")
                    results.append({
                        'name': file,
                        'type': 'file',
                        'path': file_path,
                        'size': None,
                        'modified': None,
                    })
            
            return results
        except Exception as e:
            logger.error(f"Failed to list files in '{safe_path}': {e}")
            return []
    
    async def get_file_info(
        self, 
        ctx: RunContext[DjangoDeps], 
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """Get file metadata."""
        user_id = ctx.deps.user.id
        safe_path = self._get_safe_path(file_path, user_id)
        
        try:
            if not default_storage.exists(safe_path):
                return None
            
            size = default_storage.size(safe_path)
            modified = default_storage.get_modified_time(safe_path)
            url = default_storage.url(safe_path) if hasattr(default_storage, 'url') else None
            
            return {
                'path': safe_path,
                'size': size,
                'modified': modified.isoformat() if modified else None,
                'url': url,
                'exists': True,
            }
        except Exception as e:
            logger.error(f"Failed to get file info for '{safe_path}': {e}")
            return None
    
    async def copy_file(
        self, 
        ctx: RunContext[DjangoDeps], 
        source_path: str,
        destination_path: str
    ) -> bool:
        """Copy file to new location."""
        user_id = ctx.deps.user.id
        safe_source = self._get_safe_path(source_path, user_id)
        safe_dest = self._get_safe_path(destination_path, user_id)
        
        try:
            if not default_storage.exists(safe_source):
                logger.error(f"Source file not found: {safe_source}")
                return False
            
            # Read source file
            with default_storage.open(safe_source, 'rb') as source_file:
                content = source_file.read()
            
            # Check size limit
            if len(content) > self.max_file_size:
                logger.error(f"File too large to copy: {len(content)} bytes")
                return False
            
            # Write to destination
            default_storage.save(safe_dest, ContentFile(content))
            
            logger.debug(f"Copied file: {safe_source} -> {safe_dest}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy file '{safe_source}' to '{safe_dest}': {e}")
            return False
    
    async def move_file(
        self, 
        ctx: RunContext[DjangoDeps], 
        source_path: str,
        destination_path: str
    ) -> bool:
        """Move file to new location."""
        # Copy then delete
        if await self.copy_file(ctx, source_path, destination_path):
            return await self.delete_file(ctx, source_path)
        return False
    
    async def get_storage_info(self, ctx: RunContext[DjangoDeps]) -> Dict[str, Any]:
        """Get storage backend information."""
        user_id = ctx.deps.user.id
        user_dir = self._get_safe_path("", user_id)
        
        info = {
            'storage_backend': default_storage.__class__.__name__,
            'user_directory': user_dir,
            'max_file_size': self.max_file_size,
            'allowed_paths': self.allowed_paths,
        }
        
        try:
            # Try to get user directory size
            files = await self.list_files(ctx, "")
            total_size = sum(f.get('size', 0) or 0 for f in files if f['type'] == 'file')
            file_count = sum(1 for f in files if f['type'] == 'file')
            
            info.update({
                'user_files_count': file_count,
                'user_total_size': total_size,
            })
        except Exception as e:
            logger.warning(f"Could not get storage stats: {e}")
        
        return info
