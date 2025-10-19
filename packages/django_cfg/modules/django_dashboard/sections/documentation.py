"""Documentation section for dashboard."""

import inspect
import os
from pathlib import Path
from typing import Any, Dict, List

from django.core.management import get_commands, load_command_class

from .base import DataSection


class DocumentationSection(DataSection):
    """
    Management commands documentation section.

    Displays the README.md file from django_cfg/management/ directory.
    """

    template_name = "admin/sections/documentation_section.html"
    title = "Commands Documentation"
    icon = "description"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add documentation data directly to context (not nested under 'data')."""
        # Call parent but skip DataSection's get_data() nesting
        context = super(DataSection, self).get_context_data(**kwargs)
        # Add our data directly to context
        context.update(self.get_data())
        return context

    def find_module_readme(self, module_name: str) -> str:
        """Find and read README.md from module's management directory."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            import django_cfg
            django_cfg_path = Path(django_cfg.__file__).parent

            # Try different paths
            possible_paths = [
                django_cfg_path / 'modules' / module_name / 'management' / 'README.md',
                django_cfg_path / 'management' / 'commands' / module_name / 'README.md',
            ]

            for readme_path in possible_paths:
                if readme_path.exists():
                    logger.info(f"Found module README at: {readme_path}")
                    with open(readme_path, encoding='utf-8') as f:
                        return f.read()
        except Exception as e:
            logger.debug(f"Could not find README for module {module_name}: {e}")

        return ""

    def get_commands_structure(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get structured command data grouped by app."""
        import logging
        logger = logging.getLogger(__name__)

        # Get all management commands
        commands = get_commands()

        # Filter only django_cfg commands
        django_cfg_commands = {
            name: app for name, app in commands.items()
            if 'django_cfg' in app
        }

        logger.info(f"Found {len(django_cfg_commands)} django_cfg commands")

        # Group commands by app
        commands_by_app = {}

        for cmd_name, app_name in sorted(django_cfg_commands.items()):
            try:
                # Load the command class
                try:
                    command = load_command_class(app_name, cmd_name)
                except (ImportError, ModuleNotFoundError) as e:
                    logger.debug(f"Skipping command {cmd_name}: module not found - {e}")
                    continue

                # Use app_name as group key
                if app_name not in commands_by_app:
                    # Create display name from app_name
                    display_name = app_name.replace('django_cfg.modules.', '').replace('django_cfg', 'Django CFG').replace('_', ' ').title()

                    commands_by_app[app_name] = {
                        'name': app_name,
                        'display_name': display_name,
                        'commands': []
                    }

                # Extract command information
                command_info = {
                    'name': cmd_name,
                    'help': getattr(command, 'help', 'No description available'),
                    'docstring': inspect.cleandoc(command.__doc__) if command.__doc__ else '',
                    'web_executable': getattr(command, 'web_executable', None),
                    'requires_input': getattr(command, 'requires_input', None),
                    'is_destructive': getattr(command, 'is_destructive', None),
                    'arguments': []
                }

                # Get arguments
                try:
                    parser = command.create_parser('', cmd_name)
                    actions = [action for action in parser._actions if action.dest != 'help']

                    for action in actions:
                        if action.option_strings:
                            command_info['arguments'].append({
                                'options': action.option_strings,
                                'help': action.help or 'No description',
                                'default': action.default if action.default != '==SUPPRESS==' else None,
                                'required': getattr(action, 'required', False),
                            })
                except Exception as e:
                    logger.debug(f"Could not extract arguments for {cmd_name}: {e}")

                commands_by_app[app_name]['commands'].append(command_info)

            except Exception as e:
                logger.error(f"Error loading command {cmd_name}: {e}")
                continue

        return commands_by_app

    def generate_documentation_from_commands(self) -> str:
        """Generate markdown documentation from command docstrings and module READMEs."""
        import logging
        logger = logging.getLogger(__name__)

        markdown_lines = []
        markdown_lines.append("# Django-CFG Management Commands\n\n")

        # Check for main README.md
        try:
            import django_cfg
            django_cfg_path = Path(django_cfg.__file__).parent
            main_readme_path = django_cfg_path / 'management' / 'README.md'

            if main_readme_path.exists():
                logger.info("Found main management README.md, using it as primary documentation")
                with open(main_readme_path, encoding='utf-8') as f:
                    return f.read()  # Use existing README if it exists
        except Exception as e:
            logger.debug(f"No main README found, continuing with auto-generation: {e}")

        markdown_lines.append("_Auto-generated documentation from command docstrings and module READMEs._\n\n")

        # Get all management commands
        commands = get_commands()

        # Filter only django_cfg commands
        django_cfg_commands = {
            name: app for name, app in commands.items()
            if 'django_cfg' in app
        }

        logger.info(f"Found {len(django_cfg_commands)} django_cfg commands")

        # Group commands by module
        commands_by_module = {}
        module_paths = {}  # Store module paths for README lookup

        for cmd_name, app_name in sorted(django_cfg_commands.items()):
            try:
                # Load the command class
                command = load_command_class(app_name, cmd_name)

                # Get module path
                module_path = command.__module__
                if 'modules' in module_path:
                    # Extract module name like 'django_ngrok', 'django_tasks', etc.
                    parts = module_path.split('.')
                    if 'modules' in parts:
                        module_idx = parts.index('modules')
                        if len(parts) > module_idx + 1:
                            module_name = parts[module_idx + 1]
                        else:
                            module_name = 'core'
                    else:
                        module_name = 'core'
                else:
                    module_name = 'core'

                if module_name not in commands_by_module:
                    commands_by_module[module_name] = []
                    module_paths[module_name] = module_path

                commands_by_module[module_name].append((cmd_name, command))

            except Exception as e:
                logger.error(f"Error loading command {cmd_name}: {e}")
                continue

        # Generate documentation for each module
        for module_name in sorted(commands_by_module.keys()):
            markdown_lines.append(f"\n## {module_name.replace('_', ' ').title()} Commands\n\n")

            # Check for module-specific README
            module_readme = self.find_module_readme(module_name)
            if module_readme:
                markdown_lines.append(f"_{module_name} module documentation:_\n\n")
                markdown_lines.append(module_readme)
                markdown_lines.append("\n\n### Available Commands\n\n")

            for cmd_name, command_class in sorted(commands_by_module[module_name]):
                markdown_lines.append(f"\n#### `{cmd_name}`\n\n")

                # Get help text
                if hasattr(command_class, 'help'):
                    markdown_lines.append(f"{command_class.help}\n\n")

                # Get class docstring
                if command_class.__doc__:
                    doc = inspect.cleandoc(command_class.__doc__)
                    markdown_lines.append(f"{doc}\n\n")

                # Get metadata
                metadata = []
                if hasattr(command_class, 'web_executable'):
                    metadata.append(f"**Web Executable**: {'Yes' if command_class.web_executable else 'No'}")
                if hasattr(command_class, 'requires_input'):
                    metadata.append(f"**Requires Input**: {'Yes' if command_class.requires_input else 'No'}")
                if hasattr(command_class, 'is_destructive'):
                    metadata.append(f"**Destructive**: {'Yes' if command_class.is_destructive else 'No'}")

                if metadata:
                    markdown_lines.append("**Metadata:**\n\n")
                    for meta in metadata:
                        markdown_lines.append(f"- {meta}\n")
                    markdown_lines.append("\n")

                # Get arguments
                try:
                    parser = command_class.create_parser('', cmd_name)
                    actions = [action for action in parser._actions if action.dest != 'help']

                    if actions:
                        markdown_lines.append("**Arguments:**\n\n")
                        for action in actions:
                            if action.option_strings:
                                opts = ', '.join(f"`{opt}`" for opt in action.option_strings)
                                help_text = action.help or 'No description'
                                markdown_lines.append(f"- {opts}: {help_text}\n")
                        markdown_lines.append("\n")
                except Exception as e:
                    logger.debug(f"Could not extract arguments for {cmd_name}: {e}")

                # Add usage example if available in docstring
                if command_class.__doc__ and '```' in command_class.__doc__:
                    markdown_lines.append("**Example:**\n\n")

        return ''.join(markdown_lines)

    def get_data(self) -> Dict[str, Any]:
        """Get structured command documentation data."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            commands_structure = self.get_commands_structure()

            return {
                'commands_by_module': commands_structure,
                'total_commands': sum(len(app['commands']) for app in commands_structure.values()),
                'total_modules': len(commands_structure),
            }
        except Exception as e:
            logger.error(f"Error generating command structure: {e}", exc_info=True)
            return {
                'commands_by_module': {},
                'total_commands': 0,
                'total_modules': 0,
                'error': str(e)
            }

    def get_data_old(self) -> Dict[str, Any]:
        """DEPRECATED: Get documentation content from README.md or auto-generate from docstrings."""
        import logging
        logger = logging.getLogger(__name__)

        # Check if we should use auto-generation
        use_autogen = os.environ.get('DJANGO_CFG_AUTOGEN_DOCS', 'true').lower() == 'true'

        readme_content = ""
        documentation_html = ""
        readme_path = None
        readme_exists = False

        if use_autogen:
            # Auto-generate documentation from command docstrings
            logger.info("Auto-generating documentation from command docstrings")
            try:
                readme_content = self.generate_documentation_from_commands()

                # Convert to HTML
                try:
                    import markdown
                    documentation_html = markdown.markdown(
                        readme_content,
                        extensions=[
                            'markdown.extensions.fenced_code',
                            'markdown.extensions.tables',
                            'markdown.extensions.toc',
                            'markdown.extensions.nl2br',
                            'markdown.extensions.sane_lists',
                        ]
                    )
                    logger.info("Auto-generated documentation rendered successfully")
                except ImportError:
                    logger.warning("Markdown library not available, will display as plain text")

                readme_exists = True
                readme_path = "Auto-generated from docstrings"

            except Exception as e:
                logger.error(f"Error auto-generating documentation: {e}", exc_info=True)
                readme_content = f"Error auto-generating documentation: {str(e)}"
        else:
            # Use static README.md file
            # Try multiple path resolution strategies
            possible_paths = [
                # Strategy 1: Relative to this file
                Path(__file__).parent.parent.parent / 'management' / 'README.md',
                # Strategy 2: Using django_cfg module location
                Path(__file__).parent.parent.parent / 'management' / 'README.md',
                # Strategy 3: Absolute path for django_cfg package
                Path('/Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/django-cfg/projects/django-cfg-dev/src/django_cfg/management/README.md'),
            ]

            # Find the first existing path
            for path in possible_paths:
                if path.exists():
                    readme_path = path
                    logger.info(f"Found README.md at: {readme_path}")
                    break

            # If still not found, try using django_cfg module import
            if not readme_path or not readme_path.exists():
                try:
                    import django_cfg
                    django_cfg_path = Path(django_cfg.__file__).parent
                    readme_path = django_cfg_path / 'management' / 'README.md'
                    logger.info(f"Using django_cfg module path: {readme_path}")
                except Exception as e:
                    logger.error(f"Error finding django_cfg module: {e}")
                    readme_path = possible_paths[0]  # Fallback to first path

            try:
                if readme_path and readme_path.exists():
                    logger.info(f"Reading README from: {readme_path}")
                    with open(readme_path, encoding='utf-8') as f:
                        readme_content = f.read()
                    logger.info(f"README content loaded: {len(readme_content)} characters")

                    # Try to convert markdown to HTML
                    try:
                        import markdown
                        documentation_html = markdown.markdown(
                            readme_content,
                            extensions=[
                                'markdown.extensions.fenced_code',
                                'markdown.extensions.tables',
                                'markdown.extensions.toc',
                                'markdown.extensions.nl2br',
                                'markdown.extensions.sane_lists',
                            ]
                        )
                        logger.info("Markdown rendered successfully")
                    except ImportError:
                        logger.warning("Markdown library not available, will display as plain text")
                        pass

                    readme_exists = True
                else:
                    logger.error(f"README.md not found at: {readme_path}")
                    readme_content = "README.md not found. Searched paths:\n" + "\n".join(str(p) for p in possible_paths)

            except Exception as e:
                logger.error(f"Error loading documentation: {e}", exc_info=True)
                readme_content = f"Error loading documentation: {str(e)}"

        return {
            'readme_content': readme_content,
            'documentation_content': documentation_html if documentation_html else None,
            'readme_path': str(readme_path) if readme_path else 'Not found',
            'readme_exists': readme_exists,
        }
