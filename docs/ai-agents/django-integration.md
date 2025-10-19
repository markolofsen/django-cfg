---
title: Django Integration
description: Django-CFG AI agents guide for django integration. Build type-safe AI workflows with Django ORM integration, background processing, and production monitoring.
sidebar_label: Django Integration
sidebar_position: 4
keywords:
  - django AI integration
  - django ORM AI agents
  - django admin AI
  - AI agents django views
---
# Django Integration - Admin, Signals, Middleware

## Automatic Setup

When you enable agents, the orchestration features are included:

```python
# api/config.py
class MyConfig(DjangoConfig):
    enable_agents: bool = True  # Enables agent orchestration
```

This automatically:
- Adds `django_cfg.apps.agents` to `INSTALLED_APPS`
- Configures orchestration and tracking features
- Sets up Django admin interfaces for agent execution
- Enables database models for workflow tracking

## Django Admin Interface

### Agent Execution Tracking

Go to `/admin/django_orchestrator/agentexecution/` to see:

```python
# What you see in admin:
class AgentExecution:
    agent_name: str           # "content_analyzer"
    started_at: datetime      # 2024-01-15 10:30:00
    completed_at: datetime    # 2024-01-15 10:30:05
    status: str              # "COMPLETED", "FAILED", "RUNNING"
    input_prompt: str        # "Analyze this content..."
    output_data: dict        # {"sentiment": "positive", ...}
    execution_time: float    # 4.2 seconds
    tokens_used: int         # 1,250 tokens
    cost: decimal           # $0.0025
    user: User              # Who triggered it
```

### Workflow Execution Tracking

Go to `/admin/django_orchestrator/workflowexecution/` to see:

```python
class WorkflowExecution:
    workflow_name: str       # "content_pipeline"
    started_at: datetime     # When workflow started
    completed_at: datetime   # When workflow finished
    status: str             # Overall workflow status
    initial_prompt: str     # Original user prompt
    final_output: dict      # Final workflow result
    user: User             # Who started the workflow
    
    # Related AgentExecutions show individual steps
```

### Admin Customization

The admin interface includes:

- **Filtering** by status, agent name, date
- **Search** by prompt content, user
- **Metrics** showing performance stats
- **Export** functionality for analysis
- **Detailed views** with JSON formatting

## Django Models Integration

### Using Django ORM in Tools

```python
@agent.tool
async def get_user_content(ctx: RunContext[DjangoDeps]) -> str:
    """Get user's latest content."""
    user = await ctx.deps.get_user()
    
    # Use Django ORM
    content = await Content.objects.filter(
        user=user,
        status='published'
    ).select_related('category').afirst()
    
    if not content:
        return "No published content found"
    
    return f"Title: {content.title}\nCategory: {content.category.name}\nText: {content.text}"

@agent.tool
async def create_content_summary(ctx: RunContext[DjangoDeps], title: str, summary: str) -> str:
    """Create new content summary."""
    user = await ctx.deps.get_user()
    
    # Create new model instance
    summary_obj = await ContentSummary.objects.acreate(
        user=user,
        title=title,
        summary=summary,
        created_by_ai=True
    )
    
    return f"Created summary with ID {summary_obj.id}"
```

### Model Relationships

```python
# models.py
class Content(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    ai_analysis = models.JSONField(null=True, blank=True)
    
class AIAnalysis(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    agent_name = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=20)
    keywords = models.JSONField(default=list)
    confidence = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

# Using in agent tools
@agent.tool
async def save_analysis_results(
    ctx: RunContext[DjangoDeps], 
    content_id: int,
    sentiment: str,
    keywords: List[str],
    confidence: float
) -> str:
    """Save AI analysis results."""
    
    content = await Content.objects.aget(id=content_id)
    
    # Create or update analysis
    analysis, created = await AIAnalysis.objects.aupdate_or_create(
        content=content,
        defaults={
            'agent_name': ctx.agent_name,
            'sentiment': sentiment,
            'keywords': keywords,
            'confidence': confidence
        }
    )
    
    action = "Created" if created else "Updated"
    return f"{action} analysis for content {content_id}"
```

## Django Signals Integration

### Automatic Workflow Triggers

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Content
from .agents import content_analyzer

@receiver(post_save, sender=Content)
async def analyze_new_content(sender, instance, created, **kwargs):
    """Automatically analyze new content."""
    
    if created and instance.status == 'draft':
        # Create dependencies
        deps = DjangoDeps(user_id=instance.user.id)
        
        # Run analysis in background
        try:
            result = await content_analyzer.run(
                prompt=f"Analyze content: {instance.title}",
                deps=deps
            )
            
            # Save results to content
            instance.ai_analysis = result.output.dict()
            await instance.asave(update_fields=['ai_analysis'])
            
        except Exception as e:
            logger.error(f"Auto-analysis failed for content {instance.id}: {e}")

# Don't forget to import signals in apps.py
class MyAppConfig(AppConfig):
    def ready(self):
        import myapp.signals  # Import signals
```

### Workflow State Changes

```python
from django_cfg.modules.django_orchestrator.models import WorkflowExecution
from django.db.models.signals import post_save

@receiver(post_save, sender=WorkflowExecution)
async def workflow_completed(sender, instance, **kwargs):
    """Handle workflow completion."""
    
    if instance.status == 'COMPLETED':
        # Send notification
        await send_notification(
            user=instance.user,
            title="Workflow Completed",
            message=f"Your {instance.workflow_name} workflow has finished successfully."
        )
        
        # Update related content
        if instance.workflow_name == 'content_pipeline':
            content_id = instance.config.get('content_id')
            if content_id:
                content = await Content.objects.aget(id=content_id)
                content.processing_status = 'completed'
                await content.asave()
```

## Middleware Integration

### Automatic Dependency Injection

```python
# middleware.py
from django_cfg.modules.django_orchestrator import DjangoDeps

class OrchestratorMiddleware:
    """Inject orchestrator dependencies into requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    async def __call__(self, request):
        # Create dependencies for authenticated users
        if request.user.is_authenticated:
            request.orchestrator_deps = DjangoDeps(
                user_id=request.user.id,
                request=request
            )
        else:
            request.orchestrator_deps = None
        
        response = await self.get_response(request)
        return response

# Usage in views
async def my_view(request):
    if request.orchestrator_deps:
        result = await my_agent.run(
            prompt="Process user request",
            deps=request.orchestrator_deps
        )
        return JsonResponse(result.output.dict())
    else:
        return JsonResponse({'error': 'Authentication required'}, status=401)
```

## Management Commands

### Built-in Commands

```bash
# Check orchestrator status
python manage.py orchestrator_status

# Create agent from template
python manage.py create_agent --name content_analyzer --type content

# Run agent manually
python manage.py run_agent content_analyzer "Analyze this text"

# Show agent metrics
python manage.py agent_metrics --agent content_analyzer
```

### Custom Management Commands

```python
# management/commands/bulk_content_analysis.py
from django.core.management.base import BaseCommand
from myapp.models import Content
from myapp.agents import content_analyzer
from django_cfg import DjangoDeps

class Command(BaseCommand):
    help = 'Analyze all unprocessed content'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)
        parser.add_argument('--user-id', type=int, required=True)
    
    async def handle(self, *args, **options):
        limit = options['limit']
        user_id = options['user_id']
        
        # Get unprocessed content
        content_items = Content.objects.filter(
            ai_analysis__isnull=True
        )[:limit]
        
        deps = DjangoDeps(user_id=user_id)
        processed = 0
        
        async for content in content_items:
            try:
                result = await content_analyzer.run(
                    prompt=f"Analyze: {content.title}",
                    deps=deps
                )
                
                content.ai_analysis = result.output.dict()
                await content.asave()
                processed += 1
                
                self.stdout.write(f"Processed content {content.id}")
                
            except Exception as e:
                self.stderr.write(f"Failed to process {content.id}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {processed} content items')
        )

# Usage:
# python manage.py bulk_content_analysis --user-id 1 --limit 50
```

## API Endpoints

### Built-in REST API

The orchestrator automatically provides REST endpoints:

```python
# GET /api/orchestrator/ai-agents/
# List all registered agents

# POST /api/orchestrator/ai-agents/{agent_name}/run/
# Execute specific agent
{
    "prompt": "Analyze this content",
    "deps": {"user_id": 123},
    "context": {"content_id": 456}
}

# GET /api/orchestrator/executions/
# List recent executions with filtering

# GET /api/orchestrator/executions/{id}/
# Get detailed execution results

# POST /api/orchestrator/workflows/execute/
# Execute multi-agent workflow
{
    "workflow_name": "content_pipeline",
    "agents": ["analyzer", "enhancer"],
    "prompt": "Process content",
    "deps": {"user_id": 123}
}
```

### Custom API Views

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_cfg import DjangoDeps
from .agents import content_analyzer

@api_view(['POST'])
async def analyze_content_api(request):
    """API endpoint for content analysis."""
    
    content_id = request.data.get('content_id')
    if not content_id:
        return Response({'error': 'content_id required'}, status=400)
    
    # Create dependencies
    deps = DjangoDeps(
        user_id=request.user.id,
        request=request
    )
    
    try:
        result = await content_analyzer.run(
            prompt=f"Analyze content {content_id}",
            deps=deps
        )
        
        return Response({
            'success': True,
            'analysis': result.output.dict(),
            'execution_time': result.execution_time,
            'tokens_used': result.tokens_used
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
```

## Testing Integration

### Django TestCase with Agents

```python
# tests.py
from django.test import TestCase
from django_cfg import DjangoAgent, DjangoDeps
from django_cfg.modules.django_orchestrator.models import TestModel
from .agents import content_analyzer

class ContentAnalyzerTest(TestCase):
    async def test_content_analysis(self):
        """Test content analyzer agent."""
        
        # Create test user and content
        user = await User.objects.acreate_user(
            username='testuser',
            email='test@example.com'
        )
        
        content = await Content.objects.acreate(
            user=user,
            title='Test Content',
            text='This is a positive article about Django.'
        )
        
        # Create dependencies
        deps = DjangoDeps(user_id=user.id)
        
        # Use TestModel for deterministic results
        test_agent = DjangoAgent[DjangoDeps, AnalysisResult](
            name="test_analyzer",
            deps_type=DjangoDeps,
            output_type=AnalysisResult,
            instructions="Analyze content sentiment",
            model=TestModel(
                custom_output_args={
                    'sentiment': 'positive',
                    'keywords': ['django', 'positive'],
                    'confidence': 0.95
                }
            )
        )
        
        # Run agent
        result = await test_agent.run(
            prompt=f"Analyze content {content.id}",
            deps=deps
        )
        
        # Assert results
        self.assertEqual(result.output.sentiment, 'positive')
        self.assertIn('django', result.output.keywords)
        self.assertEqual(result.output.confidence, 0.95)
```

## What's Next?

- **[Examples](examples)** - Real-world use cases and complete implementations
