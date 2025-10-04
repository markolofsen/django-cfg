"""
Path resolution utilities for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Specific exception handling
- No string manipulation for paths (use pathlib)
"""

import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from django_cfg.core.exceptions import ConfigurationError


class PathResolver:
    """
    Utility class for resolving Django project paths and structure.
    
    Automatically detects:
    - Project root directory (where manage.py is located)
    - URL configuration module
    - WSGI application module
    - Project structure and apps
    """
    
    @classmethod
    def find_project_root(cls, start_path: Optional[Path] = None) -> Path:
        """
        Find Django project root directory by looking for manage.py.
        
        Args:
            start_path: Starting directory for search (defaults to cwd)
            
        Returns:
            Path to project root directory
            
        Raises:
            ConfigurationError: If project root cannot be found
        """
        try:
            # Start from provided path or current working directory
            current_path = start_path or Path.cwd()
            
            # Look for manage.py in current directory and parents
            for path in [current_path] + list(current_path.parents):
                manage_py = path / "manage.py"
                if manage_py.exists() and manage_py.is_file():
                    return path
            
            # If not found, check if we're in a subdirectory of a Django project
            # Look for common Django project indicators
            for path in [current_path] + list(current_path.parents):
                # Check for settings.py or wsgi.py in subdirectories
                for subdir in path.iterdir():
                    if subdir.is_dir():
                        settings_py = subdir / "settings.py"
                        wsgi_py = subdir / "wsgi.py"
                        if settings_py.exists() or wsgi_py.exists():
                            # Found Django app directory, parent might be project root
                            manage_py = path / "manage.py"
                            if manage_py.exists():
                                return path
            
            raise ConfigurationError(
                "Cannot find Django project root directory",
                context={
                    'start_path': str(start_path) if start_path else str(Path.cwd()),
                    'searched_paths': [str(p) for p in [current_path] + list(current_path.parents)]
                },
                suggestions=[
                    "Ensure manage.py exists in your project root",
                    "Run django_cfg from within a Django project directory",
                    "Specify project root explicitly if needed"
                ]
            )
            
        except ConfigurationError:
            raise  # Re-raise our own exceptions
        except Exception as e:
            raise ConfigurationError(
                f"Failed to find project root: {e}",
                context={'start_path': str(start_path) if start_path else str(Path.cwd())}
            ) from e
    
    @classmethod
    def detect_root_urlconf(cls, project_root: Optional[Path] = None) -> Optional[str]:
        """
        Auto-detect Django ROOT_URLCONF setting.
        
        Args:
            project_root: Project root directory
            
        Returns:
            ROOT_URLCONF module path or None if not found
        """
        try:
            if project_root is None:
                project_root = cls.find_project_root()
            
            # Look for common URL configuration patterns
            candidates = [
                "urls.py",  # Root level urls.py
                "config/urls.py",  # Config directory
                "core/urls.py",  # Core directory
            ]
            
            # Also check for directories that might contain urls.py
            for item in project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    urls_py = item / "urls.py"
                    if urls_py.exists():
                        candidates.append(f"{item.name}/urls.py")
            
            # Check each candidate
            for candidate in candidates:
                urls_file = project_root / candidate
                if urls_file.exists() and urls_file.is_file():
                    # Convert file path to module path
                    module_path = candidate.replace('/', '.').replace('.py', '')
                    
                    # Verify it's a valid URL configuration by checking content
                    if cls._is_valid_urlconf(urls_file):
                        return module_path
            
            return None
            
        except Exception as e:
            # Don't raise exception for auto-detection failures
            return None
    
    @classmethod
    def detect_wsgi_application(cls, project_root: Optional[Path] = None) -> Optional[str]:
        """
        Auto-detect Django WSGI_APPLICATION setting.
        
        Args:
            project_root: Project root directory
            
        Returns:
            WSGI_APPLICATION module path or None if not found
        """
        try:
            if project_root is None:
                project_root = cls.find_project_root()
            
            # Look for common WSGI application patterns
            candidates = [
                "wsgi.py",  # Root level wsgi.py
                "config/wsgi.py",  # Config directory
                "core/wsgi.py",  # Core directory
            ]
            
            # Also check for directories that might contain wsgi.py
            for item in project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    wsgi_py = item / "wsgi.py"
                    if wsgi_py.exists():
                        candidates.append(f"{item.name}/wsgi.py")
            
            # Check each candidate
            for candidate in candidates:
                wsgi_file = project_root / candidate
                if wsgi_file.exists() and wsgi_file.is_file():
                    # Convert file path to module path with application
                    module_path = candidate.replace('/', '.').replace('.py', '')
                    
                    # Verify it's a valid WSGI application by checking content
                    if cls._is_valid_wsgi(wsgi_file):
                        return f"{module_path}.application"
            
            return None
            
        except Exception as e:
            # Don't raise exception for auto-detection failures
            return None
    
    @classmethod
    def discover_project_apps(cls, project_root: Optional[Path] = None) -> List[str]:
        """
        Discover Django apps in the project.
        
        Args:
            project_root: Project root directory
            
        Returns:
            List of discovered Django app names
        """
        try:
            if project_root is None:
                project_root = cls.find_project_root()
            
            apps = []
            
            # Look for directories with apps.py or models.py
            for item in project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check for Django app indicators
                    app_indicators = [
                        item / "apps.py",
                        item / "models.py",
                        item / "views.py",
                        item / "__init__.py",
                    ]
                    
                    # Must have __init__.py and at least one other indicator
                    has_init = (item / "__init__.py").exists()
                    has_indicator = any(indicator.exists() for indicator in app_indicators[:-1])
                    
                    if has_init and has_indicator:
                        apps.append(item.name)
            
            # Also look for nested apps (e.g., src/myapp/)
            common_app_dirs = ["src", "apps", "modules"]
            for app_dir_name in common_app_dirs:
                app_dir = project_root / app_dir_name
                if app_dir.exists() and app_dir.is_dir():
                    for item in app_dir.iterdir():
                        if item.is_dir() and not item.name.startswith('.'):
                            # Check for Django app indicators
                            app_indicators = [
                                item / "apps.py",
                                item / "models.py", 
                                item / "views.py",
                                item / "__init__.py",
                            ]
                            
                            has_init = (item / "__init__.py").exists()
                            has_indicator = any(indicator.exists() for indicator in app_indicators[:-1])
                            
                            if has_init and has_indicator:
                                apps.append(f"{app_dir_name}.{item.name}")
            
            return sorted(apps)
            
        except Exception as e:
            # Don't raise exception for discovery failures
            return []
    
    @classmethod
    def get_project_structure_info(cls, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get comprehensive project structure information.
        
        Args:
            project_root: Project root directory
            
        Returns:
            Dictionary with project structure details
        """
        try:
            if project_root is None:
                project_root = cls.find_project_root()
            
            return {
                'project_root': str(project_root),
                'root_urlconf': cls.detect_root_urlconf(project_root),
                'wsgi_application': cls.detect_wsgi_application(project_root),
                'discovered_apps': cls.discover_project_apps(project_root),
                'has_manage_py': (project_root / "manage.py").exists(),
                'has_requirements': any([
                    (project_root / "requirements.txt").exists(),
                    (project_root / "pyproject.toml").exists(),
                    (project_root / "Pipfile").exists(),
                ]),
                'has_docker': any([
                    (project_root / "Dockerfile").exists(),
                    (project_root / "docker-compose.yml").exists(),
                    (project_root / "docker-compose.yaml").exists(),
                ]),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to analyze project structure: {e}",
                context={'project_root': str(project_root) if project_root else 'unknown'}
            ) from e
    
    @classmethod
    def _is_valid_urlconf(cls, urls_file: Path) -> bool:
        """
        Check if file appears to be a valid Django URL configuration.
        
        Args:
            urls_file: Path to urls.py file
            
        Returns:
            True if file appears to be valid URL configuration
        """
        try:
            content = urls_file.read_text(encoding='utf-8')
            
            # Look for common URL configuration patterns
            indicators = [
                'urlpatterns',
                'path(',
                'url(',
                'include(',
                'django.urls',
                'from django.urls',
            ]
            
            return any(indicator in content for indicator in indicators)
            
        except Exception:
            return False
    
    @classmethod
    def _is_valid_wsgi(cls, wsgi_file: Path) -> bool:
        """
        Check if file appears to be a valid Django WSGI application.
        
        Args:
            wsgi_file: Path to wsgi.py file
            
        Returns:
            True if file appears to be valid WSGI application
        """
        try:
            content = wsgi_file.read_text(encoding='utf-8')
            
            # Look for common WSGI application patterns
            indicators = [
                'application',
                'get_wsgi_application',
                'django.core.wsgi',
                'from django.core.wsgi',
                'WSGI_APPLICATION',
            ]
            
            return any(indicator in content for indicator in indicators)
            
        except Exception:
            return False
    
    @classmethod
    def resolve_relative_path(cls, path: str, project_root: Optional[Path] = None) -> Path:
        """
        Resolve relative path against project root.
        
        Args:
            path: Relative path string
            project_root: Project root directory
            
        Returns:
            Resolved absolute path
        """
        try:
            if project_root is None:
                project_root = cls.find_project_root()
            
            path_obj = Path(path)
            
            if path_obj.is_absolute():
                return path_obj
            else:
                return project_root / path_obj
                
        except Exception as e:
            raise ConfigurationError(
                f"Failed to resolve path '{path}': {e}",
                context={'path': path, 'project_root': str(project_root) if project_root else 'unknown'}
            ) from e


# Export the main class
__all__ = [
    "PathResolver",
]
