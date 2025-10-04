#!/usr/bin/env python3
"""
Material Icons Generator for Django CFG Unfold.

This script automatically downloads the latest Material Icons from Google
and generates IDE-friendly constants for better autocompletion.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MaterialIconsGenerator:
    """Generator for Material Icons constants."""
    
    # URLs for different sources
    SOURCES = {
        'codepoints': 'https://raw.githubusercontent.com/google/material-design-icons/master/font/MaterialIcons-Regular.codepoints',
        'metadata': 'https://fonts.google.com/metadata/icons',
        'github_api': 'https://api.github.com/repos/google/material-design-icons/contents/symbols'
    }
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.icons_data: Dict[str, str] = {}
        self.categories: Dict[str, List[str]] = {}
        
    def download_codepoints(self) -> Dict[str, str]:
        """Download Material Icons codepoints from GitHub."""
        logger.info("📥 Downloading Material Icons codepoints...")
        
        try:
            response = requests.get(self.SOURCES['codepoints'], timeout=30)
            response.raise_for_status()
            
            icons = {}
            for line in response.text.strip().split('\n'):
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        codepoint = parts[1]
                        icons[name] = codepoint
            
            logger.info(f"✅ Downloaded {len(icons)} icons from codepoints")
            return icons
            
        except Exception as e:
            logger.error(f"❌ Failed to download codepoints: {e}")
            return {}
    
    def download_metadata(self) -> Dict[str, any]:
        """Download Material Icons metadata from Google Fonts."""
        logger.info("📥 Downloading Material Icons metadata...")
        
        try:
            response = requests.get(self.SOURCES['metadata'], timeout=30)
            response.raise_for_status()
            
            # Remove the first line (it's not JSON)
            content = response.text
            if content.startswith(")]}'"):
                content = content[4:]
            
            metadata = json.loads(content)
            
            # Extract icons from metadata
            icons_metadata = {}
            if 'icons' in metadata:
                for icon in metadata['icons']:
                    name = icon.get('name', '')
                    if name:
                        icons_metadata[name] = {
                            'categories': icon.get('categories', []),
                            'tags': icon.get('tags', []),
                            'version': icon.get('version', 1),
                            'popularity': icon.get('popularity', 0)
                        }
            
            logger.info(f"✅ Downloaded metadata for {len(icons_metadata)} icons")
            return icons_metadata
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to download metadata: {e}")
            return {}
    
    def categorize_icons(self, metadata: Dict[str, any]) -> Dict[str, List[str]]:
        """Categorize icons based on metadata."""
        categories = {
            'navigation': [],
            'users': [],
            'documents': [],
            'communication': [],
            'ai_automation': [],
            'actions': [],
            'status': [],
            'media': [],
            'settings': [],
            'commerce': [],
            'travel': [],
            'social': [],
            'device': [],
            'editor': [],
            'maps': [],
            'notification': [],
            'content': [],
            'hardware': [],
            'image': [],
            'av': [],
            'places': [],
            'file': [],
            'toggle': [],
        }
        
        # Keywords for categorization
        category_keywords = {
            'navigation': ['dashboard', 'menu', 'home', 'apps', 'navigate', 'arrow', 'chevron', 'expand', 'more'],
            'users': ['people', 'person', 'group', 'account', 'face', 'user', 'profile'],
            'documents': ['description', 'text', 'article', 'note', 'folder', 'file', 'document', 'page'],
            'communication': ['chat', 'message', 'email', 'mail', 'forum', 'comment', 'call', 'phone'],
            'ai_automation': ['smart', 'auto', 'sync', 'refresh', 'repeat', 'psychology', 'memory', 'robot'],
            'actions': ['play', 'pause', 'stop', 'add', 'remove', 'edit', 'delete', 'save', 'cancel', 'done'],
            'status': ['check', 'error', 'warning', 'info', 'pending', 'success', 'failed'],
            'media': ['video', 'audio', 'music', 'photo', 'image', 'camera', 'mic', 'volume'],
            'settings': ['settings', 'tune', 'build', 'construction', 'gear', 'config'],
            'commerce': ['shopping', 'cart', 'store', 'payment', 'money', 'price', 'sell'],
            'travel': ['flight', 'hotel', 'car', 'train', 'directions', 'map', 'location'],
            'social': ['share', 'favorite', 'like', 'star', 'bookmark', 'follow'],
            'device': ['phone', 'tablet', 'laptop', 'desktop', 'watch', 'tv', 'speaker'],
            'editor': ['format', 'text', 'font', 'color', 'align', 'indent', 'bold', 'italic'],
            'maps': ['map', 'location', 'place', 'pin', 'navigation', 'gps'],
            'notification': ['notification', 'alert', 'bell', 'announce'],
            'content': ['content', 'copy', 'paste', 'cut', 'select', 'clipboard'],
            'hardware': ['memory', 'storage', 'battery', 'wifi', 'bluetooth', 'usb'],
            'image': ['image', 'photo', 'picture', 'crop', 'filter', 'camera'],
            'av': ['play', 'pause', 'stop', 'volume', 'music', 'video', 'audio'],
            'places': ['home', 'work', 'school', 'hospital', 'restaurant', 'hotel'],
            'file': ['folder', 'file', 'upload', 'download', 'attach', 'archive'],
            'toggle': ['toggle', 'switch', 'radio', 'checkbox', 'on', 'off'],
        }
        
        for icon_name in self.icons_data.keys():
            # Use metadata categories if available
            if icon_name in metadata and metadata[icon_name].get('categories'):
                for cat in metadata[icon_name]['categories']:
                    cat_key = cat.lower().replace(' ', '_')
                    if cat_key in categories:
                        categories[cat_key].append(icon_name)
                        continue
            
            # Fallback to keyword matching
            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in icon_name.lower() for keyword in keywords):
                    categories[category].append(icon_name)
                    categorized = True
                    break
            
            # Default category for uncategorized icons
            if not categorized:
                categories.setdefault('other', []).append(icon_name)
        
        # Remove empty categories and sort icons
        return {k: sorted(v) for k, v in categories.items() if v}
    
    def generate_constants_file(self):
        """Generate the constants.py file with all icons."""
        logger.info("📝 Generating constants.py...")
        
        # Sort icons alphabetically
        sorted_icons = sorted(self.icons_data.keys())
        
        content = '''"""
Material Icons constants for IDE autocompletion.

This file is auto-generated by generate_icons.py script.
DO NOT EDIT MANUALLY - run the script to update.

Generated from Google Material Design Icons.
Total icons: {total_icons}
"""

from typing import Dict, Final


class Icons:
    """
    Material Design Icons constants for IDE autocompletion.
    
    Usage:
        from django_cfg.modules.django_unfold.icons import Icons
        
        # IDE will provide autocompletion
        icon = Icons.DASHBOARD
        icon = Icons.SETTINGS
        icon = Icons.PEOPLE
    """
    
'''.format(total_icons=len(sorted_icons))
        
        # Generate icon constants
        for icon_name in sorted_icons:
            # Convert to valid Python identifier
            const_name = icon_name.upper().replace('-', '_')
            # Prefix with underscore if starts with digit
            if const_name[0].isdigit():
                const_name = f'_{const_name}'
            content += f'    {const_name}: Final[str] = "{icon_name}"\n'
        
        # Add common aliases
        content += '''
    # Common aliases for better IDE experience
    USERS = PEOPLE
    USER = PERSON
    DOCUMENTS = DESCRIPTION
    FILES = INSERT_DRIVE_FILE
    FOLDERS = FOLDER
    MESSAGES = MESSAGE
    EMAILS = EMAIL
    TASKS = QUEUE
    AGENTS = SMART_TOY
    AI = SMART_TOY


'''
        
        # Generate categories
        content += '''# IDE-friendly icon categories for easy discovery
class IconCategories:
    """Categorized icon collections for easy discovery."""
    
'''
        
        for category, icons in self.categories.items():
            if len(icons) > 0:
                category_name = category.upper()
                content += f'    {category_name}: Dict[str, str] = {{\n'
                for icon in icons[:20]:  # Limit to first 20 icons per category
                    const_name = icon.upper().replace('-', '_')
                    # Prefix with underscore if starts with digit
                    if const_name[0].isdigit():
                        const_name = f'_{const_name}'
                    content += f"        '{icon}': Icons.{const_name},\n"
                content += '    }\n    \n'
        
        # Add validation function
        content += '''

# Validation function for IDE
def validate_icon_constant(icon_name: str) -> bool:
    """
    Validate that an icon constant exists.
    
    Args:
        icon_name: The icon name to validate
        
    Returns:
        True if the icon exists in Material Icons
    """
    from .icons import MaterialIcons
    return MaterialIcons.is_valid_icon(icon_name)


# Export commonly used icons for direct import
__all__ = [
    'Icons',
    'IconCategories', 
    'validate_icon_constant',
]
'''
        
        # Write to file
        output_file = self.output_dir / 'constants.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Generated {output_file} with {len(sorted_icons)} icons")
    
    def generate_readme(self):
        """Generate README.md for the icons module."""
        logger.info("📝 Generating README.md...")
        
        content = f'''# Material Icons for Django CFG Unfold

This module provides Material Design Icons integration for Django CFG Unfold admin interface.

## 📊 Statistics

- **Total Icons**: {len(self.icons_data)}
- **Categories**: {len(self.categories)}
- **Auto-generated**: Yes (via `generate_icons.py`)

## 🚀 Usage

### Basic Usage

```python
from django_cfg.modules.django_unfold.icons import Icons

# Use in navigation configuration
navigation_item = {{
    "title": "Dashboard",
    "icon": Icons.DASHBOARD,  # IDE autocompletion!
    "link": "/admin/",
}}
```

### Category-based Selection

```python
from django_cfg.modules.django_unfold.icons import IconCategories

# Get all navigation-related icons
nav_icons = IconCategories.NAVIGATION

# Get all user-related icons  
user_icons = IconCategories.USERS
```

### Validation

```python
from django_cfg.modules.django_unfold.icons import validate_icon_constant

# Validate icon exists
is_valid = validate_icon_constant(Icons.DASHBOARD)  # True
is_valid = validate_icon_constant("nonexistent")    # False
```

## 🔄 Updating Icons

To update to the latest Material Icons:

```bash
cd /path/to/django-cfg/src/django_cfg/modules/django_unfold/icons/
python generate_icons.py
```

This will:
1. Download the latest Material Icons from Google
2. Generate new `constants.py` with all icons
3. Categorize icons for easy discovery
4. Provide IDE-friendly autocompletion

## 📂 File Structure

```
icons/
├── __init__.py              # Main exports
├── constants.py             # 🤖 Auto-generated icon constants
├── icons.py                 # MaterialIcons class & validation
├── icon_validator.py        # Navigation validation utilities
├── generate_icons.py        # 🔄 Icon generator script
├── example_usage.py         # Usage examples
└── README.md               # This file
```

## 🎯 Available Categories

{self._generate_categories_list()}

## 🛠️ Development

### Adding New Categories

Edit the `category_keywords` in `generate_icons.py`:

```python
category_keywords = {{
    'my_category': ['keyword1', 'keyword2', 'keyword3'],
    # ...
}}
```

### Custom Icon Validation

```python
from django_cfg.modules.django_unfold.icons import MaterialIcons

# Check if icon exists
if MaterialIcons.is_valid_icon('my_icon'):
    print("Icon exists!")

# Get suggestions for invalid icons
suggestions = MaterialIcons.suggest_similar_icons('invalid_icon')
print(f"Did you mean: {{suggestions}}")
```

## 📋 Icon Guidelines

1. **Use Constants**: Always use `Icons.CONSTANT_NAME` instead of strings
2. **Validate**: Use validation functions to check icon existence
3. **Categories**: Browse `IconCategories` for organized icon selection
4. **Update Regularly**: Run the generator script to get latest icons

## 🔗 Resources

- [Material Design Icons](https://fonts.google.com/icons)
- [Google Material Icons GitHub](https://github.com/google/material-design-icons)
- [Django Unfold Documentation](https://unfoldadmin.com/)

---

*This file is auto-generated. Last updated: {self._get_current_timestamp()}*
'''
        
        # Write to file
        output_file = self.output_dir / 'README.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Generated {output_file}")
    
    def _generate_categories_list(self) -> str:
        """Generate markdown list of categories."""
        lines = []
        for category, icons in self.categories.items():
            icon_count = len(icons)
            example_icons = ', '.join(icons[:5])
            if len(icons) > 5:
                example_icons += f", ... (+{len(icons) - 5} more)"
            
            lines.append(f"- **{category.title()}** ({icon_count} icons): {example_icons}")
        
        return '\n'.join(lines)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for documentation."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """Run the complete icon generation process."""
        logger.info("🚀 Starting Material Icons generation...")
        
        # Download icons data
        self.icons_data = self.download_codepoints()
        if not self.icons_data:
            logger.error("❌ Failed to download icons data")
            return False
        
        # Download metadata for categorization
        metadata = self.download_metadata()
        
        # Categorize icons
        self.categories = self.categorize_icons(metadata)
        logger.info(f"📂 Categorized icons into {len(self.categories)} categories")
        
        # Generate files
        self.generate_constants_file()
        self.generate_readme()
        
        logger.info("🎉 Icon generation completed successfully!")
        return True


def main():
    """Main entry point."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    generator = MaterialIconsGenerator(script_dir)
    success = generator.run()
    
    if success:
        print("\n✅ Material Icons updated successfully!")
        print("📝 Files generated:")
        print(f"   - {script_dir / 'constants.py'}")
        print(f"   - {script_dir / 'README.md'}")
        print("\n💡 Don't forget to commit the changes!")
    else:
        print("\n❌ Icon generation failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
