---
id: nextjs-admin-overview
title: Next.js Admin Integration
description: Integrate custom Next.js admin dashboards as secondary admin interfaces within django-cfg
sidebar_label: Overview
slug: /features/integrations/nextjs-admin
tags:
  - nextjs
  - admin
  - frontend
  - integration
---

import { NextJsAdminShowcase } from '@site/src/components';

# Next.js Admin Integration

<NextJsAdminShowcase />

---

Django-CFG provides seamless integration for embedding custom Next.js admin dashboards as secondary admin interfaces. This powerful feature allows you to combine Django's robust backend with modern React-based admin panels.

## Overview

The Next.js Admin integration enables you to:

- **Dual Admin Interface** - Run both built-in Django Unfold admin and custom Next.js admin simultaneously
- **Automatic API Generation** - Auto-generate TypeScript clients from your Django APIs
- **Unified Authentication** - Share JWT tokens between Django and Next.js seamlessly
- **Theme Synchronization** - Automatic dark/light mode sync between interfaces
- **Docker-Ready Deployment** - ZIP-based packaging with auto-extraction on first request
- **Development Hot Reload** - Full hot-reload support during development

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Admin (Unfold)                     │
│                                                               │
│  [Built-in Dashboard]  [External Next.js Admin]  [...]      │
│  ┌────────────────┐  ┌────────────────────────┐            │
│  │  Tab 1:        │  │  Tab 2:                 │            │
│  │  Built-in      │  │  Your Custom            │            │
│  │  Dashboard     │  │  Next.js Admin          │            │
│  │                │  │                         │            │
│  │  (iframe)      │  │  (iframe)               │            │
│  └────────────────┘  └────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
         │                          │
         ├─── JWT Auth ─────────────┤
         ├─── Theme Sync ───────────┤
         └─── API Calls ────────────┘
```

## Key Features

### 1. Simple Configuration

Configure your Next.js admin with just one line:

```python
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",

    # Simple configuration
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
    ),
)
```

All other settings use smart defaults that work out of the box.

### 2. Automatic API Client Generation

```bash
# Generate TypeScript clients and build Next.js
python manage.py generate_clients --typescript

# Output:
# ✅ Generated TypeScript clients
# ✅ Copied to Next.js project
# ✅ Built Next.js static export
# ✅ Created ZIP archive
```

### 3. ZIP-Based Deployment

Instead of copying thousands of files, the integration creates compressed ZIP archives:

- **Smaller Docker images** - ~5-10MB vs ~20MB+ uncompressed
- **Faster builds** - Single file copy vs thousands of files
- **Auto-extraction** - Extracts on first HTTP request automatically
- **Production-ready** - Perfect for containerized deployments

### 4. Development Workflow

Development mode supports full hot-reload:

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Next.js dev server
cd django_admin/apps/admin && pnpm dev

# Admin loads from http://localhost:3001 with hot reload!
```

## Use Cases

### Single Custom Dashboard

Perfect for projects that need a modern admin interface:

- Real-time analytics dashboards
- Custom data visualization tools
- Specialized admin workflows
- Modern UI/UX requirements

### Multiple Admin Dashboards

Ideal for enterprise applications:

- Separate dashboards for different user roles
- Department-specific admin interfaces
- Microservices with dedicated admin panels
- Multi-tenant applications

### Gradual Migration

Great for legacy projects:

- Keep existing Django admin running
- Build new features in Next.js
- Migrate incrementally
- Zero downtime transitions

## Quick Start

### 1. Configure

```python
# api/config.py
from django_cfg import DjangoConfig, NextJsAdminConfig

config = DjangoConfig(
    project_name="My Project",
    nextjs_admin=NextJsAdminConfig(
        project_path="../django_admin",
    ),
)
```

### 2. Generate API & Build

```bash
python manage.py generate_clients --typescript
```

### 3. Run

```bash
python manage.py runserver
# Visit http://localhost:8000/admin/
```

## What's Next?

<div className="row">
  <div className="col col--6">
    <div className="card">
      <div className="card__header">
        <h3>🚀 Quick Setup</h3>
      </div>
      <div className="card__body">
        <p>Get your Next.js admin running in minutes with our quick setup guide.</p>
      </div>
      <div className="card__footer">
        <a href="./quick-start" className="button button--primary button--block">Quick Start →</a>
      </div>
    </div>
  </div>
  <div className="col col--6">
    <div className="card">
      <div className="card__header">
        <h3>⚙️ Configuration</h3>
      </div>
      <div className="card__body">
        <p>Learn about all configuration options and customization possibilities.</p>
      </div>
      <div className="card__footer">
        <a href="./configuration" className="button button--primary button--block">Configuration →</a>
      </div>
    </div>
  </div>
</div>

<div className="row">
  <div className="col col--6">
    <div className="card">
      <div className="card__header">
        <h3>🔧 How It Works</h3>
      </div>
      <div className="card__body">
        <p>Understand the architecture and how components work together.</p>
      </div>
      <div className="card__footer">
        <a href="./how-it-works" className="button button--secondary button--block">Learn More →</a>
      </div>
    </div>
  </div>
  <div className="col col--6">
    <div className="card">
      <div className="card__header">
        <h3>🚢 Production Deployment</h3>
      </div>
      <div className="card__body">
        <p>Deploy your Next.js admin to production with Docker and best practices.</p>
      </div>
      <div className="card__footer">
        <a href="./deployment" className="button button--secondary button--block">Deploy →</a>
      </div>
    </div>
  </div>
</div>

## Resources

- [Configuration Reference](./configuration)
- [API Generation](./api-generation)
- [Troubleshooting Guide](./troubleshooting)
- [Examples](./examples)

:::tip Pro Tip
Start with the minimal configuration and customize only what you need. The smart defaults are designed to work for most use cases.
:::
