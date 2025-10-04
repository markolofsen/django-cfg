"""
CLI Utilities for django-cfg

Common functions used across CLI commands.
"""

import sys
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
import sysconfig


def get_package_info() -> Dict[str, Any]:
    """Get django-cfg package information."""
    try:
        import django_cfg
        package_path = Path(django_cfg.__file__).parent
        
        # Get version from package
        version = getattr(django_cfg, '__version__', '1.0.0')
        try:
            from importlib.metadata import version as get_version
            version = get_version("django-cfg")
        except:
            pass
        
        return {
            "version": version,
            "path": package_path,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "installed": True,
        }
    except ImportError:
        return {
            "version": "unknown",
            "path": None,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "installed": False,
        }


def find_template_archive() -> Optional[Path]:
    """Find template archive in various locations."""
    search_paths = []
    
    try:
        import django_cfg
        package_path = Path(django_cfg.__file__).parent
        
        # Method 1: Package template_archive directory
        search_paths.append(package_path / "template_archive" / "django_sample.zip")
        
        # Method 2: Site-packages shared data
        site_packages = Path(sysconfig.get_paths()["purelib"])
        search_paths.append(site_packages / "django_cfg" / "template_archive" / "django_sample.zip")
        
        # Method 3: Development installation - src directory
        dev_path = package_path.parent.parent / "src" / "django_cfg" / "template_archive" / "django_sample.zip"
        search_paths.append(dev_path)
        
    except ImportError:
        pass
    
    # Method 4: Relative to CLI files (development)
    cli_path = Path(__file__).parent.parent.parent.parent
    search_paths.append(cli_path / "src" / "django_cfg" / "template_archive" / "django_sample.zip")
    
    # Return first existing path
    for path in search_paths:
        if path.exists():
            return path
    
    return None


def get_template_info() -> Dict[str, Any]:
    """Get information about available template archive."""
    archive_path = find_template_archive()
    
    if not archive_path:
        return {
            "available": False,
            "path": None,
            "name": "django_sample",
            "type": "archive",
        }
    
    try:
        stat = archive_path.stat()
        
        # Count files and validate archive
        file_count = 0
        is_valid = False
        try:
            with zipfile.ZipFile(archive_path, 'r') as archive:
                file_count = len(archive.namelist())
                archive.testzip()  # Test if archive is valid
                is_valid = True
        except zipfile.BadZipFile:
            is_valid = False
        
        return {
            "available": True,
            "path": archive_path,
            "name": "django_sample",
            "type": "archive",
            "size_bytes": stat.st_size,
            "size_kb": stat.st_size / 1024,
            "file_count": file_count,
            "is_valid": is_valid,
        }
        
    except Exception:
        return {
            "available": False,
            "path": archive_path,
            "name": "django_sample",
            "type": "archive",
            "is_valid": False,
        }


def check_dependencies(dependencies: Dict[str, str]) -> Dict[str, bool]:
    """
    Check which dependencies are installed.
    
    Args:
        dependencies: Dict of {package_name: import_name}
    
    Returns:
        Dict of {package_name: is_installed}
    """
    results = {}
    
    for pkg_name, import_name in dependencies.items():
        try:
            __import__(import_name.replace("-", "_"))
            results[pkg_name] = True
        except ImportError:
            results[pkg_name] = False
    
    return results


def get_standard_dependencies() -> Dict[str, str]:
    """Get standard django-cfg dependencies for checking."""
    return {
        # Core integrations
        "django": "django",
        "pydantic": "pydantic",
        "pydantic-yaml": "pydantic_yaml",
        
        # Services
        "twilio": "twilio",
        "sendgrid": "sendgrid",
        "openai": "openai",
        "telegram-bot-api": "telebot",
        
        # Admin & UI
        "django-unfold": "unfold",
        "django-constance": "constance",
        
        # API & Documentation
        "djangorestframework": "rest_framework",
        "drf-spectacular": "drf_spectacular",
        
        # Tasks & Background Processing
        "dramatiq": "dramatiq",
        "redis": "redis",
        
        # Development
        "ngrok": "ngrok",
        "click": "click",
    }


def validate_project_name(name: str) -> bool:
    """Validate project name."""
    if not name or not name.strip():
        return False
    
    # Add more validation rules as needed
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    return not any(char in name for char in invalid_chars)


def format_dependency_status(deps: Dict[str, bool], show_installed: bool = True, show_missing: bool = True) -> str:
    """Format dependency status for display."""
    lines = []
    
    for dep_name, is_installed in deps.items():
        if is_installed and show_installed:
            lines.append(f"   ✅ {dep_name}")
        elif not is_installed and show_missing:
            lines.append(f"   ⚪ {dep_name}")
    
    return "\n".join(lines)
