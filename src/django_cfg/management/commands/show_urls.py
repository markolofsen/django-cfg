"""
Django management command to display all URL patterns in the project.
"""

import re
from typing import List, Tuple, Optional
from django.core.management.base import BaseCommand, CommandParser
from django.urls import get_resolver
from django.conf import settings
from django.utils.termcolors import make_style


class Command(BaseCommand):
    """
    Display all URL patterns in the Django project.
    
    This command recursively walks through all URL patterns and displays them
    in a hierarchical format with colors and filtering options.
    """
    
    help = 'Display all URL patterns in the project'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define color styles
        self.styles = {
            'SUCCESS': make_style(opts=('bold',), fg='green'),
            'WARNING': make_style(opts=('bold',), fg='yellow'),
            'ERROR': make_style(opts=('bold',), fg='red'),
            'HTTP_200': make_style(fg='green'),
            'HTTP_400': make_style(fg='yellow'),
            'HTTP_500': make_style(fg='red'),
            'URL': make_style(fg='cyan'),
            'NAME': make_style(fg='blue'),
            'INCLUDE': make_style(opts=('bold',), fg='magenta'),
            'NAMESPACE': make_style(opts=('bold',), fg='yellow'),
        }

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            '--format',
            choices=['list', 'tree', 'table'],
            default='tree',
            help='Output format (default: tree)'
        )
        parser.add_argument(
            '--filter',
            type=str,
            help='Filter URLs by pattern (regex supported)'
        )
        parser.add_argument(
            '--namespace',
            type=str,
            help='Show URLs only from specific namespace'
        )
        parser.add_argument(
            '--plain',
            action='store_true',
            help='Plain output without colors'
        )
        parser.add_argument(
            '--include-unnamed',
            action='store_true',
            help='Include URLs without names'
        )
        parser.add_argument(
            '--show-methods',
            action='store_true',
            help='Show HTTP methods for each URL'
        )
        parser.add_argument(
            '--show-views',
            action='store_true',
            help='Show view functions/classes'
        )

    def handle(self, *args, **options) -> None:
        """Main command handler."""
        self.options = options
        
        # Disable colors if requested
        if options['plain'] or options.get('no_color', False):
            for key in self.styles:
                self.styles[key] = lambda x: x

        self.stdout.write(
            self.styles['SUCCESS']('🌐 Django URL Patterns')
        )
        self.stdout.write('=' * 50)
        
        # Show Django Revolution info if available
        if hasattr(settings, 'DJANGO_REVOLUTION'):
            self._show_revolution_info()
        
        # Get and display URL patterns
        resolver = get_resolver()
        patterns = self._collect_patterns(resolver.url_patterns)
        
        # Filter patterns if requested
        if options['filter']:
            patterns = self._filter_patterns(patterns, options['filter'])
        
        if options['namespace']:
            patterns = self._filter_by_namespace(patterns, options['namespace'])
        
        # Display patterns in requested format
        if options['format'] == 'list':
            self._display_list(patterns)
        elif options['format'] == 'table':
            self._display_table(patterns)
        else:
            self._display_tree(patterns)
        
        self.stdout.write(f"\n📊 Total URLs: {len(patterns)}")

    def _show_revolution_info(self) -> None:
        """Display Django Revolution configuration info."""
        revolution = settings.DJANGO_REVOLUTION
        
        self.stdout.write(
            self.styles['NAMESPACE']('\n📋 Django Revolution Configuration:')
        )
        self.stdout.write(f"  API Prefix: {revolution.get('api_prefix', 'N/A')}")
        self.stdout.write(f"  Debug: {revolution.get('debug', 'N/A')}")
        
        zones = revolution.get('zones', {})
        if zones:
            self.stdout.write(f"  Zones: {', '.join(zones.keys())}")
        self.stdout.write('')

    def _collect_patterns(
        self, 
        urlpatterns, 
        prefix: str = '', 
        namespace: str = ''
    ) -> List[Tuple[str, str, str, str, Optional[str]]]:
        """
        Recursively collect all URL patterns.
        
        Returns list of tuples: (pattern, name, namespace, view, methods)
        """
        patterns = []
        
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # This is an include() pattern
                new_prefix = prefix + str(pattern.pattern)
                new_namespace = namespace
                
                if hasattr(pattern, 'namespace') and pattern.namespace:
                    new_namespace = (
                        f"{namespace}:{pattern.namespace}" 
                        if namespace 
                        else pattern.namespace
                    )
                
                # Add the include pattern itself
                patterns.append((
                    new_prefix,
                    f"[INCLUDE: {getattr(pattern, 'app_name', 'unknown')}]",
                    new_namespace,
                    'include',
                    None
                ))
                
                # Recursively collect nested patterns
                patterns.extend(
                    self._collect_patterns(
                        pattern.url_patterns, 
                        new_prefix, 
                        new_namespace
                    )
                )
            else:
                # Regular URL pattern
                full_pattern = prefix + str(pattern.pattern)
                name = getattr(pattern, 'name', None)
                view_name = self._get_view_name(pattern)
                methods = self._get_http_methods(pattern)
                
                patterns.append((
                    full_pattern,
                    name or '[unnamed]',
                    namespace,
                    view_name,
                    methods
                ))
        
        return patterns

    def _get_view_name(self, pattern) -> str:
        """Get the view function/class name from a URL pattern."""
        try:
            if hasattr(pattern, 'callback'):
                callback = pattern.callback
                if hasattr(callback, '__name__'):
                    return callback.__name__
                elif hasattr(callback, '__class__'):
                    return callback.__class__.__name__
                else:
                    return str(callback)
            return 'unknown'
        except Exception:
            return 'unknown'

    def _get_http_methods(self, pattern) -> Optional[str]:
        """Get HTTP methods supported by a URL pattern."""
        if not self.options['show_methods']:
            return None
        
        try:
            # Try to get methods from the view
            if hasattr(pattern, 'callback'):
                callback = pattern.callback
                if hasattr(callback, 'cls'):
                    # DRF ViewSet or APIView
                    view_class = callback.cls
                    if hasattr(view_class, 'http_method_names'):
                        return ', '.join(view_class.http_method_names).upper()
                elif hasattr(callback, 'view_class'):
                    # Class-based view
                    view_class = callback.view_class
                    if hasattr(view_class, 'http_method_names'):
                        return ', '.join(view_class.http_method_names).upper()
            return 'GET, POST, PUT, PATCH, DELETE'  # Default assumption
        except Exception:
            return None

    def _filter_patterns(
        self, 
        patterns: List[Tuple], 
        filter_pattern: str
    ) -> List[Tuple]:
        """Filter patterns by regex."""
        try:
            regex = re.compile(filter_pattern, re.IGNORECASE)
            return [
                pattern for pattern in patterns
                if regex.search(pattern[0]) or regex.search(pattern[1])
            ]
        except re.error:
            self.stdout.write(
                self.styles['ERROR'](f"Invalid regex pattern: {filter_pattern}")
            )
            return patterns

    def _filter_by_namespace(
        self, 
        patterns: List[Tuple], 
        namespace: str
    ) -> List[Tuple]:
        """Filter patterns by namespace."""
        return [
            pattern for pattern in patterns
            if pattern[2] and namespace in pattern[2]
        ]

    def _display_tree(self, patterns: List[Tuple]) -> None:
        """Display patterns in tree format."""
        self.stdout.write(self.styles['SUCCESS']('\n🌳 URL Tree:'))
        self.stdout.write('-' * 30)
        
        for pattern, name, namespace, view, methods in patterns:
            # Format the output
            if '[INCLUDE:' in name:
                # Include pattern
                icon = '📁'
                pattern_display = self.styles['INCLUDE'](pattern)
                name_display = self.styles['NAMESPACE'](name)
            elif name == '[unnamed]' and not self.options['include_unnamed']:
                continue
            else:
                # Regular pattern
                icon = '🔗'
                pattern_display = self.styles['URL'](pattern)
                name_display = self.styles['NAME'](name)
            
            # Build the line
            line = f"{icon} {pattern_display}"
            if name and name != '[unnamed]':
                line += f" -> {name_display}"
            
            if namespace:
                line += f" [{self.styles['NAMESPACE'](namespace)}]"
            
            if self.options['show_views'] and view and view != 'include':
                line += f" ({view})"
            
            if methods:
                line += f" [{methods}]"
            
            self.stdout.write(line)

    def _display_list(self, patterns: List[Tuple]) -> None:
        """Display patterns in simple list format."""
        self.stdout.write(self.styles['SUCCESS']('\n📋 URL List:'))
        self.stdout.write('-' * 20)
        
        for i, (pattern, name, namespace, view, methods) in enumerate(patterns, 1):
            if name == '[unnamed]' and not self.options['include_unnamed']:
                continue
            
            line = f"{i:3d}. {self.styles['URL'](pattern)}"
            if name and name != '[unnamed]':
                line += f" ({self.styles['NAME'](name)})"
            
            self.stdout.write(line)

    def _display_table(self, patterns: List[Tuple]) -> None:
        """Display patterns in table format."""
        self.stdout.write(self.styles['SUCCESS']('\n📊 URL Table:'))
        self.stdout.write('-' * 80)
        
        # Header
        headers = ['Pattern', 'Name', 'Namespace', 'View']
        if self.options['show_methods']:
            headers.append('Methods')
        
        header_line = ' | '.join(f"{h:<20}" for h in headers)
        self.stdout.write(self.styles['SUCCESS'](header_line))
        self.stdout.write('-' * len(header_line))
        
        # Rows
        for pattern, name, namespace, view, methods in patterns:
            if name == '[unnamed]' and not self.options['include_unnamed']:
                continue
            
            row = [
                pattern[:20],
                (name or '')[:20],
                (namespace or '')[:20],
                (view or '')[:20]
            ]
            
            if self.options['show_methods']:
                row.append((methods or '')[:20])
            
            row_line = ' | '.join(f"{cell:<20}" for cell in row)
            self.stdout.write(row_line)
