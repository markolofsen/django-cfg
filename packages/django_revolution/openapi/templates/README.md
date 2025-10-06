# 📁 Templates Directory Structure

This directory contains Jinja2 templates for generating client code in different languages.

## 🏗️ Structure

```
templates/
├── typescript/          # TypeScript client templates
│   ├── index.ts.j2                    # Main TypeScript index file
│   ├── index_consolidated.ts.j2       # Consolidated index for all zones
│   └── package.json.j2                # NPM package configuration
└── python/             # Python client templates
    ├── __init__.py.j2                 # Python package initialization
    ├── apiconfig_pydantic_2.jinja2    # Pydantic v2 API configuration
    └── httpx.jinja2                   # HTTP client implementation
```

## 🔧 Usage

### TypeScript Templates
Used by:
- `generator.py` - Main generator coordinator
- `monorepo_sync.py` - Multi-monorepo synchronization
- `heyapi_ts.py` - TypeScript client generator

### Python Templates
Used by:
- `python_client.py` - Python client generator

## 📝 Template Variables

### Common Variables
- `zone_name` - Name of the API zone
- `title` - Human-readable title
- `description` - Zone description
- `version` - Package version
- `generation_time` - ISO timestamp of generation

### TypeScript Specific
- `apps` - List of Django apps in the zone

### Python Specific
- Custom template variables defined in `python_client.py`

## 🚀 Adding New Templates

1. Create template file with `.j2` or `.jinja2` extension
2. Place in appropriate language directory
3. Update corresponding generator to use the template
4. Test template rendering with sample data

## 🔄 Template Updates

When updating templates:
1. Maintain backward compatibility when possible
2. Update all generators that use the template
3. Test with existing zones
4. Update documentation if variables change
