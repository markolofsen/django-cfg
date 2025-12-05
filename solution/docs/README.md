# Django-CFG Project Documentation

Welcome to your Django-CFG project! This directory contains setup guides and documentation.

## Quick Links

- [Setup Guide](./SETUP.md) - First-time project setup
- [Configuration Guide](./CONFIGURATION.md) - Environment and config files
- [AI Documentation](./AI-DOCS.md) - MCP server for AI assistants
- [Docker Guide](./DOCKER.md) - Container deployment

## Project Structure

```
your-project/
├── docker/                    # Docker deployment
│   ├── docker-compose-local.yaml
│   ├── docker-compose-production.yaml
│   └── services/
├── docs/                      # This directory
└── projects/
    ├── django/                # Django backend
    │   ├── api/
    │   │   ├── config.py      # Django-CFG configuration
    │   │   └── environment/
    │   │       ├── .env       # Environment variables
    │   │       ├── .env.prod  # Production overrides
    │   │       └── loader.py  # Pydantic settings
    │   ├── apps/              # Your Django apps
    │   ├── manage.py
    │   └── pyproject.toml
    ├── frontend/              # Next.js frontend
    └── electron/              # Desktop app (optional)
```

## Getting Started

1. Read [Setup Guide](./SETUP.md)
2. Configure [Environment](./CONFIGURATION.md)
3. Run your project

## Online Documentation

Full documentation: https://djangocfg.com/docs

## Support

- GitHub: https://github.com/markolofsen/django-cfg
- Issues: https://github.com/markolofsen/django-cfg/issues
