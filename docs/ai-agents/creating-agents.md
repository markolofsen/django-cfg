---
title: Creating AI Agents
description: Django-CFG AI agents guide for creating agents. Build type-safe AI workflows with Django ORM integration, background processing, and production monitoring.
sidebar_label: Creating Agents
sidebar_position: 2
keywords:
  - create django AI agent
  - pydantic AI agent
  - django agent tutorial
  - AI agent tools django
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Creating Agents - Detailed Guide

:::info[Complete Agent Guide]
Learn how to create **type-safe AI agents** with Django integration. This guide covers everything from basic agents to advanced patterns with tools and error handling.
:::

## Agent Anatomy

Every agent consists of 4 parts:

```python
agent = DjangoAgent[DepsT, OutputT](
    name="my_agent",           # 1. Name (unique)
    deps_type=DjangoDeps,      # 2. Dependencies type
    output_type=MyResult,      # 3. Result type
    instructions="Do this..."   # 4. Instructions for LLM
)
```

:::tip[Type Safety]
The `DjangoAgent[DepsT, OutputT]` pattern provides **full type safety** - your IDE will autocomplete and type-check all inputs and outputs.
:::

## 1. Defining Types

### Dependencies (DjangoDeps)

```python
from dataclasses import dataclass
from django_cfg import DjangoDeps

# Basic dependencies (ready to use)
deps = DjangoDeps(user_id=123)
user = await deps.get_user()  # Get User object

# Extended dependencies
@dataclass
class ContentDeps(DjangoDeps):
    content_id: int
    category: str = "general"
    
    async def get_content(self):
        return await Content.objects.aget(id=self.content_id)
```

### Results (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ContentAnalysis(BaseModel):
    sentiment: str = Field(..., description="positive/negative/neutral")
    keywords: List[str] = Field(default_factory=list)
    summary: str = Field(..., max_length=500)
    confidence: float = Field(..., ge=0, le=1)
    
class ProcessingResult(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    errors: List[str] = Field(default_factory=list)
```

## 2. Creating Agent

<Tabs>
  <TabItem value="simple" label="Simple Agent" default>

### Simple Agent

```python
from django_cfg import DjangoAgent, DjangoDeps, RunContext

# Create agent
summarizer = DjangoAgent[DjangoDeps, ProcessingResult](
    name="content_summarizer",
    deps_type=DjangoDeps,
    output_type=ProcessingResult,
    instructions="""
    You are a content summarizer.
    Create concise, informative summaries of text content.
    Always return success=True if summary was created.
    """
)
```

:::note[Simple Agent Use Cases]
Simple agents are ideal for:
- **Content summarization** - Quick summaries
- **Sentiment analysis** - Basic text analysis
- **Classification** - Categorize content
- **Translation** - Simple text translation

**When to use:**
- Single-purpose tasks
- No database access needed
- Fast execution required
:::

  </TabItem>
  <TabItem value="advanced" label="Advanced Agent">

### Agent with Settings

```python
advanced_agent = DjangoAgent[ContentDeps, ContentAnalysis](
    name="content_analyzer",
    deps_type=ContentDeps,
    output_type=ContentAnalysis,
    instructions="Analyze content for sentiment and extract keywords",
    model="openai:gpt-4o",           # Specific model
    timeout=120,                     # 2 minute timeout
    max_retries=2,                   # Maximum 2 attempts
    enable_caching=True              # Enable caching
)
```

:::tip[Advanced Agent Configuration]
**Configuration options:**
- `model` - Specific LLM model to use
- `timeout` - Maximum execution time (seconds)
- `max_retries` - Retry failed executions
- `enable_caching` - Cache responses (80% cost reduction)
- `temperature` - Creativity level (0-1)
- `max_tokens` - Response length limit

**Best practices:**
- ✅ Use GPT-4o for complex reasoning
- ✅ Use GPT-4o-mini for simple tasks (10x cheaper)
- ✅ Enable caching for repeated queries
- ✅ Set reasonable timeouts (30-120s)
:::

  </TabItem>
  <TabItem value="specialized" label="Specialized Agents">

### Specialized Agent Types

**Content Processing Agent:**
```python
content_processor = DjangoAgent[ContentDeps, ProcessingResult](
    name="content_processor",
    instructions="Process and transform content based on rules",
    model="gpt-4o-mini",  # Cost-effective for processing
    timeout=60
)
```

**Customer Support Agent:**
```python
support_agent = DjangoAgent[SupportDeps, SupportResponse](
    name="support_agent",
    instructions="Provide helpful customer support responses",
    model="gpt-4o",  # Better understanding for support
    temperature=0.7,  # More natural responses
    timeout=90
)
```

**Data Analysis Agent:**
```python
analyst_agent = DjangoAgent[AnalysisDeps, AnalysisReport](
    name="data_analyst",
    instructions="Analyze data and generate insights",
    model="gpt-4o",  # Complex reasoning needed
    timeout=180,  # Longer timeout for analysis
    enable_caching=True
)
```

:::info[Choosing the Right Agent Type]
**By task complexity:**
- **Simple** (summarize, classify) → gpt-4o-mini, 30s timeout
- **Medium** (analyze, extract) → gpt-4o-mini, 60s timeout
- **Complex** (reasoning, multi-step) → gpt-4o, 120s+ timeout

**By cost priority:**
- **High volume, simple** → gpt-4o-mini ($0.001/call)
- **Low volume, complex** → gpt-4o ($0.01/call)
- **Balance** → gpt-4o-mini with caching ($0.0002/call)
:::

  </TabItem>
</Tabs>

## 3. Adding Tools

### Basic Tools

```python
@summarizer.tool
async def get_content_by_id(ctx: RunContext[DjangoDeps], content_id: int) -> str:
    """Get content by ID."""
    try:
        content = await Content.objects.aget(id=content_id)
        return content.text
    except Content.DoesNotExist:
        return f"Content with ID {content_id} not found"

@summarizer.tool
async def save_summary(ctx: RunContext[DjangoDeps], content_id: int, summary: str) -> str:
    """Save summary."""
    content = await Content.objects.aget(id=content_id)
    content.summary = summary
    await content.asave()
    return f"Summary saved for content {content_id}"
```

### Tools with Permissions

```python
@advanced_agent.tool
async def get_user_content(ctx: RunContext[ContentDeps]) -> str:
    """Get user content with permission check."""
    user = await ctx.deps.get_user()
    content = await ctx.deps.get_content()
    
    # Permission check
    if content.user != user and not content.is_public:
        raise PermissionError("Access denied to private content")
    
    return content.text

@advanced_agent.tool
async def update_content_metadata(
    ctx: RunContext[ContentDeps], 
    keywords: List[str], 
    sentiment: str
) -> str:
    """Update content metadata."""
    content = await ctx.deps.get_content()
    user = await ctx.deps.get_user()
    
    # Only owner can update
    if content.user != user:
        return "Permission denied"
    
    content.keywords = keywords
    content.sentiment = sentiment
    content.analyzed_at = timezone.now()
    await content.asave()
    
    return f"Updated metadata for content {content.id}"
```

### Tools for External APIs

```python
@advanced_agent.tool
async def search_related_content(ctx: RunContext[ContentDeps], query: str) -> str:
    """Find related content."""
    from django.db.models import Q
    
    # Search by keywords
    related = await Content.objects.filter(
        Q(title__icontains=query) | Q(keywords__contains=[query])
    ).exclude(id=ctx.deps.content_id)[:5].aall()
    
    if not related:
        return "No related content found"
    
    results = []
    for content in related:
        results.append(f"- {content.title} (ID: {content.id})")
    
    return "Related content:\n" + "\n".join(results)

@advanced_agent.tool
async def call_external_api(ctx: RunContext[ContentDeps], endpoint: str) -> str:
    """Call external API."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.example.com/{endpoint}")
            return response.text
        except Exception as e:
            return f"API call failed: {e}"
```

## 4. Using Agents

### Simple Execution

```python
async def analyze_content(request, content_id):
    # Create dependencies
    deps = ContentDeps(
        user_id=request.user.id,
        content_id=content_id,
        category="article"
    )
    
    # Run agent
    result = await advanced_agent.run(
        prompt=f"Analyze content {content_id} for sentiment and keywords",
        deps=deps
    )
    
    # Check result
    if result.output.confidence > 0.8:
        return JsonResponse({
            'sentiment': result.output.sentiment,
            'keywords': result.output.keywords,
            'summary': result.output.summary
        })
    else:
        return JsonResponse({'error': 'Low confidence analysis'}, status=400)
```

### With Error Handling

```python
from django_cfg.modules.django_orchestrator import ExecutionError

async def safe_content_analysis(request, content_id):
    deps = ContentDeps(user_id=request.user.id, content_id=content_id)
    
    try:
        result = await advanced_agent.run(
            prompt="Analyze this content thoroughly",
            deps=deps
        )
        
        # Log successful execution
        logger.info(f"Analysis completed for content {content_id}")
        
        return JsonResponse({
            'success': True,
            'data': result.output.dict(),
            'execution_time': result.execution_time,
            'tokens_used': result.tokens_used
        })
        
    except ExecutionError as e:
        logger.error(f"Agent execution failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
    except PermissionError as e:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)
```

## 5. Metrics and Monitoring

### Getting Agent Metrics

```python
# Metrics for specific agent
metrics = advanced_agent.get_metrics()
print(f"Executions: {metrics['execution_count']}")
print(f"Avg time: {metrics['avg_execution_time']:.2f}s")
print(f"Error rate: {metrics['error_rate']:.1%}")
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
```

### Monitoring in Django Admin

1. Go to `/admin/django_orchestrator/agentexecution/`
2. See all agent runs:
   - Execution time
   - Tokens used
   - Cost
   - Status (success/error)
   - Input and output data

## 6. Best Practices

### ✅ Good

```python
# Create agents at module level (once)
content_agent = DjangoAgent[ContentDeps, ContentAnalysis](...)

# Use typing
async def process_content(ctx: RunContext[ContentDeps]) -> str:
    content = await ctx.deps.get_content()
    return content.text

# Handle errors
try:
    result = await agent.run(prompt, deps)
except ExecutionError:
    # handle error
```

### ❌ Bad

```python
# Create agents in view (every time)
def my_view(request):
    agent = DjangoAgent(...)  # Slow!

# Ignore types
def get_data(ctx) -> str:  # No typing
    return "data"

# Don't handle errors
result = await agent.run(prompt, deps)  # Can crash
```

## What's Next?

- **[Orchestration](orchestration)** - Coordinating multiple agents
- **[Django Integration](django-integration)** - Admin, signals, middleware
- **[Examples](examples)** - Real-world use cases