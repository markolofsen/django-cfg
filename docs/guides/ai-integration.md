---
title: AI Integration Guide
description: Django-CFG ai integration guide. Practical tutorial for ai integration guide with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: AI Integration
sidebar_position: 3
keywords:
  - django-cfg ai integration
  - django-cfg guide ai integration
  - how to ai integration django
---

# AI Integration Guide

Integrate AI agents with Django-CFG using type-safe configuration and environment-based secrets.

## Configuration Setup

### 1. YAML Configuration

```yaml
# environment/config.yaml
api_keys:
  openai: "${OPENAI_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000
```

### 2. Environment Loader

```python
# environment/loader.py
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as
from pathlib import Path

class APIKeysConfig(BaseModel):
    openai: str
    anthropic: str | None = None

class LLMSettings(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000

class EnvironmentConfig(BaseModel):
    api_keys: APIKeysConfig
    llm: LLMSettings

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
env: EnvironmentConfig = parse_yaml_raw_as(
    EnvironmentConfig,
    config_path.read_text()
)
```

### 3. Django-CFG Integration

```python
# config.py
from django_cfg import DjangoConfig
from .environment import env

class MyProjectConfig(DjangoConfig):
    enable_agents: bool = True  # Enable AI agents app
    enable_knowbase: bool = True  # Enable knowledge base

    # API keys from environment (type-safe!)
    api_keys: dict[str, str] = {
        "openai": env.api_keys.openai,
        "anthropic": env.api_keys.anthropic or "",
    }

config = MyProjectConfig()
```

## Using AI Agents

### Basic Agent

```python
# agents/customer_support.py
from django_cfg.modules.django_llm import LLMClient

class CustomerSupportAgent:
    def __init__(self):
        self.llm = LLMClient(
            provider="openai",
            api_key=config.api_keys["openai"],
            model="gpt-4",
        )

    def answer_question(self, question: str, context: dict) -> str:
        prompt = f"""
        Question: {question}
        Context: {context}

        Provide a helpful answer.
        """
        return self.llm.generate(prompt)
```

### Knowledge Base Integration

```python
# Using with knowledge base
from django_cfg.apps.knowbase.services import KnowledgeBaseService

class SmartSupportAgent:
    def __init__(self):
        self.kb = KnowledgeBaseService()
        self.llm = LLMClient(
            provider="openai",
            api_key=config.api_keys["openai"],
        )

    def answer_with_context(self, question: str):
        # Search knowledge base
        docs = self.kb.search(question, limit=3)

        # Generate answer with context
        context = "\n\n".join(doc.content for doc in docs)
        prompt = f"""
        Context from knowledge base:
        {context}

        User question: {question}

        Answer based on the context above.
        """
        return self.llm.generate(prompt)
```

## Advanced Configuration

### Multiple LLM Providers

```yaml
# environment/config.yaml
llm:
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4"
      temperature: 0.7

    anthropic:
      api_key: "${ANTHROPIC_API_KEY}"
      model: "claude-3-sonnet-20240229"
      temperature: 0.7

  default_provider: "openai"
```

```python
# environment/loader.py
class LLMProviderConfig(BaseModel):
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None

class LLMSettings(BaseModel):
    providers: dict[str, LLMProviderConfig]
    default_provider: str = "openai"

# config.py
from .environment import env

class MyProjectConfig(DjangoConfig):
    enable_agents: bool = True

    # Extract API keys from provider configs
    api_keys: dict[str, str] = {
        name: provider.api_key
        for name, provider in env.llm.providers.items()
    }
```

### Custom Tools

```python
# tools/search.py
from typing import Any

def search_products(query: str) -> list[dict[str, Any]]:
    """Search product catalog."""
    from shop.models import Product
    return list(
        Product.objects.filter(name__icontains=query)
        .values('id', 'name', 'price')
    )

# agents/shopping_assistant.py
class ShoppingAssistant:
    def __init__(self):
        self.llm = LLMClient(
            provider="openai",
            api_key=config.api_keys["openai"],
            tools=[
                {
                    "name": "search_products",
                    "description": "Search for products in catalog",
                    "function": search_products,
                }
            ]
        )

    def help_customer(self, message: str):
        return self.llm.generate(message, use_tools=True)
```

## Production Best Practices

### 1. Environment Variables

```bash
# .env.production
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Secret Management

```python
# config.py
import os
from django_cfg import DjangoConfig

class ProductionConfig(DjangoConfig):
    enable_agents: bool = True

    # Fail fast if keys missing
    api_keys: dict[str, str] = {
        "openai": os.environ["OPENAI_API_KEY"],  # Will raise if missing
    }

    @property
    def is_production(self) -> bool:
        return not self.debug

    def validate_api_keys(self):
        """Validate API keys at startup."""
        if self.is_production:
            required = ["openai"]
            missing = [k for k in required if not self.api_keys.get(k)]
            if missing:
                raise ValueError(f"Missing API keys: {missing}")
```

### 3. Rate Limiting

```python
from django.core.cache import cache
from time import sleep

class RateLimitedLLM:
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.llm = LLMClient(...)

    def generate(self, prompt: str) -> str:
        # Simple rate limiting
        key = "llm_requests"
        count = cache.get(key, 0)
        if count >= self.rpm:
            sleep(60)
            cache.set(key, 0, 60)

        cache.incr(key, 1)
        return self.llm.generate(prompt)
```

## Testing

```python
# tests/test_ai_integration.py
from django.test import TestCase
from unittest.mock import patch, MagicMock

class AIIntegrationTest(TestCase):
    @patch('django_cfg.modules.django_llm.LLMClient')
    def test_customer_support_agent(self, mock_llm):
        mock_llm.return_value.generate.return_value = "Test response"

        agent = CustomerSupportAgent()
        response = agent.answer_question(
            "How do I reset my password?",
            context={"user_id": 123}
        )

        assert response == "Test response"
        mock_llm.return_value.generate.assert_called_once()
```

## See Also

### AI Features & Integration

**AI Agents Framework:**
- [**AI Agents Introduction**](/ai-agents/introduction) - Complete agent framework overview
- [**Creating Agents**](/ai-agents/creating-agents) - Build custom AI agents
- [**Agent Toolsets**](/ai-agents/toolsets) - Define agent tools and capabilities
- [**Orchestration**](/ai-agents/orchestration) - Multi-agent workflows
- [**Django Integration**](/ai-agents/django-integration) - Django-specific agent features
- [**AI Examples**](/ai-agents/examples) - Real-world AI agent examples

**Knowledge Base & RAG:**
- [**Knowledge Base Overview**](/features/built-in-apps/ai-knowledge/overview) - Semantic search and RAG
- [**Knowledge Base Setup**](/features/built-in-apps/ai-knowledge/knowbase-setup) - Getting started
- [**Data Integration**](/features/built-in-apps/ai-knowledge/knowbase-data-integration) - Ingest documents
- [**Chat & Search**](/features/built-in-apps/ai-knowledge/knowbase-chat-search) - Query interface

**LLM Module:**
- [**LLM Module Overview**](/features/modules/llm/overview) - Multi-provider LLM integration

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with AI features
- [**Configuration Guide**](/getting-started/configuration) - YAML configuration setup
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Advanced Configuration:**
- [**Environment Variables**](/fundamentals/configuration/environment) - Secure API key management
- [**Environment Detection**](/fundamentals/configuration/environment) - Environment-based AI config
- [**Type-Safe Configuration**](/fundamentals/core/type-safety) - AI config validation

### Background Processing & Tools

**Task Processing:**
- [**ReArq Integration**](/features/integrations/rearq/overview) - Async AI processing
- [**Background Tasks**](/features/built-in-apps/operations/tasks) - Task queue for AI jobs

**CLI & Management:**
- [**AI Agent Commands**](/cli/commands/ai-agents) - Manage agents via CLI
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Troubleshooting**](/guides/troubleshooting) - Common AI integration issues

### Production & Deployment

**Production Setup:**
- [**Production Config**](./production-config) - Production AI configuration
- [**Docker Deployment**](/guides/docker/production) - Deploy AI features
- [**Examples Guide**](./examples) - Production AI patterns

**Note:** This guide uses YAML-based configuration with Pydantic models. See [Configuration Guide](/getting-started/configuration) for complete setup.
