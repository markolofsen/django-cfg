"""
🌳 Django CFG Tree Command

Display Django project structure in a tree format based on configuration.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_cfg.core.config import get_current_config
from django_cfg.utils.path_resolution import PathResolver


class Command(BaseCommand):
    """Display Django project structure in tree format."""
    
    help = "Display Django project structure based on django-cfg configuration"
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--depth', '-L',
            type=int,
            default=5,
            help='Maximum depth to display (default: 5)'
        )
        parser.add_argument(
            '--all', '-a',
            action='store_true',
            help='Show all files including hidden ones'
        )
        parser.add_argument(
            '--dirs-only', '-d',
            action='store_true',
            help='Show directories only'
        )
        parser.add_argument(
            '--no-ignore', '-n',
            action='store_true',
            help='Do not ignore common directories (node_modules, .git, etc.)'
        )
        parser.add_argument(
            '--custom-ignore',
            type=str,
            help='Custom ignore pattern (pipe-separated, e.g., "*.pyc|temp|logs")'
        )
        parser.add_argument(
            '--include-docs',
            action='store_true',
            help='Legacy option - @docs directories are now included by default'
        )
        parser.add_argument(
            '--include-docker',
            action='store_true', 
            help='Include Docker configuration and volumes'
        )
        parser.add_argument(
            '--include-logs',
            action='store_true',
            help='Include log files and directories'
        )
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output to file instead of stdout'
        )
        parser.add_argument(
            '--format',
            choices=['tree', 'json', 'xml'],
            default='tree',
            help='Output format (default: tree)'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Get django-cfg configuration
            config = get_current_config()
            
            # Determine base directory
            base_dir = self.get_base_directory(config)
            
            self.stdout.write(
                self.style.SUCCESS(f"📁 Django Project Structure: {base_dir}")
            )
            
            # Try to get environment info
            try:
                env_info = getattr(config, 'environment', 'unknown')
                if hasattr(config, '_environment'):
                    env_info = config._environment or 'unknown'
                self.stdout.write(
                    self.style.HTTP_INFO(f"🔧 Environment: {env_info}")
                )
            except Exception:
                pass
                
            self.stdout.write("")
            
            # Check if tree command is available
            if not self.is_tree_available():
                self.stdout.write(
                    self.style.WARNING("⚠️  'tree' command not found. Using fallback implementation.")
                )
                self.display_fallback_tree(base_dir, options)
            else:
                self.display_tree(base_dir, options)
                
        except Exception as e:
            raise CommandError(f"Failed to display project tree: {e}")
    
    def get_base_directory(self, config) -> Path:
        """Get the base directory for the Django project tree."""
        try:
            # First try to use PathResolver to find the actual Django project root
            return PathResolver.find_project_root()
        except Exception:
            try:
                # Try to get from config
                if hasattr(config, 'base_dir') and config.base_dir:
                    return Path(config.base_dir)
                
                # Fallback to Django BASE_DIR
                if hasattr(settings, 'BASE_DIR'):
                    return Path(settings.BASE_DIR)
                
                # Last resort: current working directory
                return Path.cwd()
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Could not determine base directory: {e}")
                )
                return Path.cwd()
    
    def is_tree_available(self) -> bool:
        """Check if tree command is available."""
        try:
            subprocess.run(['tree', '--version'], 
                         capture_output=True, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def build_ignore_pattern(self, options) -> str:
        """Build ignore pattern for tree command."""
        if options['no_ignore']:
            return ""
        
        # Default ignore patterns
        default_ignores = [
            'node_modules',
            '.git',
            '.venv',
            'venv',
            '.env',
            '.DS_Store',
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            'coverage',
            '.tox',
            'dist',
            'build',
            '*.egg-info',
            'staticfiles',
            'media',
            '@old*',
            'parsers',
            'openapi',
            'modules',
            'django_cfg',
            # Package manager files
            'package-lock.json',
            'pnpm-lock.yaml', 
            'poetry.lock',
            'yarn.lock',
            # Empty/system directories
            'db',
            'static'
        ]
        
        # Conditionally add patterns based on options
        # Note: @docs folders are now included by default to show documentation
        # Use --include-docs flag is kept for backward compatibility but doesn't exclude @docs anymore
            
        if not options.get('include_docker'):
            default_ignores.extend([
                'docker',
                'devops'
            ])
            
        if not options.get('include_logs'):
            default_ignores.extend([
                'logs',
                '*.log',
                'log'
            ])
        
        # Add custom ignores
        if options['custom_ignore']:
            custom_ignores = options['custom_ignore'].split('|')
            default_ignores.extend(custom_ignores)
        
        return '|'.join(default_ignores)
    
    def display_tree(self, base_dir: Path, options):
        """Display tree using system tree command."""
        try:
            # Build tree command
            cmd = ['tree']
            
            # Add ignore pattern
            ignore_pattern = self.build_ignore_pattern(options)
            if ignore_pattern:
                cmd.extend(['-I', ignore_pattern])
            
            # Add options
            cmd.append('--dirsfirst')  # Directories first
            
            if options['depth']:
                cmd.extend(['-L', str(options['depth'])])
            
            if options['dirs_only']:
                cmd.append('-d')
            
            if options['all']:
                cmd.append('-a')
            
            # Add format options
            if options['format'] == 'json':
                cmd.append('-J')
            elif options['format'] == 'xml':
                cmd.append('-X')
            
            # Add base directory
            cmd.append(str(base_dir))
            
            # Execute command
            if options['output']:
                with open(options['output'], 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Tree output saved to: {options['output']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Tree command failed: {result.stderr}")
                    )
            else:
                result = subprocess.run(cmd, text=True)
                if result.returncode != 0:
                    self.stdout.write(
                        self.style.ERROR("❌ Tree command failed")
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to execute tree command: {e}")
            )
            self.display_fallback_tree(base_dir, options)
    
    def display_fallback_tree(self, base_dir: Path, options):
        """Fallback tree implementation using Python."""
        self.stdout.write("🐍 Using Python fallback implementation:")
        self.stdout.write("")
        
        ignore_patterns = self.build_ignore_pattern(options).split('|') if not options['no_ignore'] else []
        
        def should_ignore(path: Path) -> bool:
            """Check if path should be ignored."""
            name = path.name
            for pattern in ignore_patterns:
                if pattern.startswith('*'):
                    if name.endswith(pattern[1:]):
                        return True
                elif pattern.endswith('*'):
                    if name.startswith(pattern[:-1]):
                        return True
                elif pattern == name:
                    return True
            return False
        
        def print_tree(directory: Path, prefix: str = "", depth: int = 0):
            """Recursively print directory tree."""
            if options['depth'] and depth >= options['depth']:
                return
            
            try:
                items = []
                for item in directory.iterdir():
                    if not options['all'] and item.name.startswith('.'):
                        continue
                    if should_ignore(item):
                        continue
                    items.append(item)
                
                # Sort: directories first, then files
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    
                    if item.is_dir():
                        self.stdout.write(f"{prefix}{current_prefix}📁 {item.name}/")
                        if not options['dirs_only']:
                            next_prefix = prefix + ("    " if is_last else "│   ")
                            print_tree(item, next_prefix, depth + 1)
                    elif not options['dirs_only']:
                        # Add file type emoji
                        emoji = self.get_file_emoji(item)
                        self.stdout.write(f"{prefix}{current_prefix}{emoji} {item.name}")
                        
            except PermissionError:
                self.stdout.write(f"{prefix}❌ Permission denied")
        
        print_tree(base_dir)
    
    def get_file_emoji(self, file_path: Path) -> str:
        """Get emoji for file type."""
        suffix = file_path.suffix.lower()
        
        emoji_map = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.html': '🌐',
            '.css': '🎨',
            '.scss': '🎨',
            '.json': '📋',
            '.yaml': '📄',
            '.yml': '📄',
            '.toml': '⚙️',
            '.ini': '⚙️',
            '.cfg': '⚙️',
            '.conf': '⚙️',
            '.md': '📝',
            '.txt': '📄',
            '.log': '📊',
            '.sql': '🗄️',
            '.db': '🗄️',
            '.sqlite': '🗄️',
            '.sqlite3': '🗄️',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.svg': '🖼️',
            '.ico': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.requirements': '📋',
            'requirements.txt': '📋',
            'Dockerfile': '🐳',
            'docker-compose.yml': '🐳',
            'manage.py': '⚙️',
            'setup.py': '⚙️',
            'pyproject.toml': '📦',
            'poetry.lock': '🔒',
            'Pipfile': '📦',
            'Pipfile.lock': '🔒',
        }
        
        # Check full filename first
        if file_path.name in emoji_map:
            return emoji_map[file_path.name]
        
        # Then check extension
        return emoji_map.get(suffix, '📄')
