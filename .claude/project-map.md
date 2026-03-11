# Project Map
> monorepo — A Django configuration framework providing type-safe settings and AI agent integration.
> Generated: 2026-03-10T12:07:28.055254+00:00

## Structure

- `docs/` — Root directory for the Nextra-based documentation website.
  - `docs/ai-agents/` — Documentation for AI agent framework integration and workflows.
  - `docs/api/` — API reference documentation for the framework.
  - `docs/business/` — Business-oriented documentation about cost reduction and ROI.
  - `docs/cli/` — Documentation for the command-line interface and its commands.
    - `docs/cli/commands/` — Contains _meta.ts, ai-agents.mdx, ai-docs.mdx, codegen.mdx, core-commands.mdx
  - `docs/core-concepts/` — Documentation for core design patterns like builder and generator.
  - `docs/deployment/` — Documentation for deployment, monitoring, and security setup.
  - `docs/extensions/` — Documentation for extending the framework backend and frontend.
  - `docs/features/` — Documentation for core framework features and modules.
    - `docs/features/api-generation/` — Contains _meta.ts, cli-usage.mdx, generated-clients.mdx, groups.mdx, index.mdx
    - `docs/features/built-in-apps/` — Contains _meta.ts, index.mdx, overview.mdx
    - `docs/features/drf-guide/` — Contains _meta.ts, drf-array-responses.mdx, drf-nested-serializers.mdx, drf-pagination.mdx, drf-pydantic-responses.mdx
    - `docs/features/integrations/` — Contains _meta.ts, auth.mdx, index.mdx, overview.mdx, patterns.mdx
    - `docs/features/modules/` — Contains _meta.ts, index.mdx, overview.mdx
    - `docs/features/tools/` — Contains _meta.ts
  - `docs/fundamentals/` — Documentation for core architectural concepts and system configuration.
    - `docs/fundamentals/configuration/` — Contains _meta.ts, cache.mdx, database.mdx, django-settings.mdx, email.mdx
    - `docs/fundamentals/core/` — Contains _meta.ts, architecture.mdx, index.mdx, type-safety.mdx
    - `docs/fundamentals/database/` — Contains _meta.ts, cross-database-relations.mdx, index.mdx, migrations.mdx, multi-database.mdx
    - `docs/fundamentals/imgs/` — Contains startup.png
    - `docs/fundamentals/system/` — Contains _meta.ts, cors.mdx, django-integration.mdx, index.mdx, middleware.mdx
  - `docs/getting-started/` — Documentation for initial project setup and installation.
  - `docs/guides/` — In-depth guides for application design, deployment, and runtime.
    - `docs/guides/app-design/` — Contains _meta.ts, admin.mdx, app-structure.mdx, index.mdx, managers.mdx
    - `docs/guides/django-runtime/` — Contains _meta.ts, async-orm.mdx, channels-asgi.mdx, django-testing.mdx, index.mdx
    - `docs/guides/docker/` — Contains _meta.ts, build-optimization.mdx, configuration.mdx, development.mdx, index.mdx
    - `docs/guides/module-design/` — Contains _meta.ts, architecture.mdx, async-patterns.mdx, code-style.mdx, dependency-injection.mdx
    - `docs/guides/nextjs-app-design/` — Contains _meta.ts, architecture.mdx, component-patterns.mdx, data-layer.mdx, index.mdx
    - `docs/guides/sample-project/` — Contains _meta.ts, admin-interface.mdx, api-documentation.mdx, authentication.mdx, configuration.mdx
  - `docs/updates/` — Documentation for release notes, security advisories, and blog posts.
    - `docs/updates/blog/` — Contains _meta.ts, django-configuration-debt-analysis.mdx, django-multi-tenancy-architecture-roi.mdx, django-performance-optimization-guide.mdx, django-saas-total-cost-ownership.mdx
    - `docs/updates/releases/` — Contains _meta.ts, index.mdx, v1-4-42.mdx
    - `docs/updates/security/` — Contains _meta.ts, index.mdx, nextjs-cve-2025-55184-55183.mdx, nextjs-cve-2025-66478.mdx
- `installers/` — Shell and PowerShell installation scripts for the framework.
  - `packages/django_cfg/` — Primary Python package for the Django configuration framework.
    - `packages/django_cfg/apps/` — Django app configuration and URL definitions for the package.
    - `packages/django_cfg/cli/` — Command-line interface entry point for the Django-CFG tool. **[entry: main.py]**
    - `packages/django_cfg/core/` — Core framework logic for configuration, validation, and constants.
    - `packages/django_cfg/extensions/` — Framework extension modules for dynamic loading and scheduling.
    - `packages/django_cfg/management/` — Django management command infrastructure.
    - `packages/django_cfg/middleware/` — Django middleware components for authentication, debugging, and monitoring.
    - `packages/django_cfg/mixins/` — API mixin classes for admin, client, and public endpoints.
    - `packages/django_cfg/models/` — Placeholder for Django database models.
    - `packages/django_cfg/modules/` — Base classes for framework modules.
    - `packages/django_cfg/registry/` — Service and module registry for dependency management.
    - `packages/django_cfg/routing/` — URL routing configuration and callback handlers.
    - `packages/django_cfg/stubs/` — Type stubs for Python type checking support.
    - `packages/django_cfg/templates/` — Template files and related styling documentation.

## Entry Points

- `packages/django_cfg/cli/main.py`

---
Model: cache | Tokens: 0