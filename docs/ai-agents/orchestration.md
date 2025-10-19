---
title: Agent Orchestration
description: Django-CFG AI agents guide for orchestration. Build type-safe AI workflows with Django ORM integration, background processing, and production monitoring.
sidebar_label: Orchestration
sidebar_position: 3
keywords:
  - AI workflow orchestration
  - multi-agent django
  - django agent coordination
  - AI pipeline django
---
# Orchestration - Coordinating Multiple Agents

## What is Orchestration?

Orchestration is coordinating multiple agents to work together on complex tasks. Think of it like a conductor leading an orchestra - each agent has a specific role, and the orchestrator coordinates their performance.

## SimpleOrchestrator

The main class for coordinating agents:

```python
from django_cfg import SimpleOrchestrator

# Create orchestrator
orchestrator = SimpleOrchestrator[DjangoDeps]()

# Register agents
orchestrator.register_agent(content_analyzer)
orchestrator.register_agent(content_enhancer)
orchestrator.register_agent(content_publisher)
```

## Execution Patterns

### Sequential Execution

Agents run one after another, output from Agent N becomes input for Agent N+1:

```python
# Sequential workflow
result = await orchestrator.execute(
    pattern="sequential",
    agents=["content_analyzer", "content_enhancer", "content_publisher"],
    prompt="Process this article for publication",
    deps=deps
)

# Flow:
# 1. content_analyzer: analyzes content → analysis result
# 2. content_enhancer: takes analysis → enhanced content  
# 3. content_publisher: takes enhanced content → published article
```

### Real Example: Content Pipeline

```python
from django_cfg import DjangoAgent, SimpleOrchestrator, DjangoDeps
from pydantic import BaseModel
from typing import List

# Define output models
class AnalysisResult(BaseModel):
    sentiment: str
    keywords: List[str]
    readability_score: float
    suggestions: List[str]

class EnhancementResult(BaseModel):
    enhanced_text: str
    improvements_made: List[str]
    seo_optimized: bool

class PublishResult(BaseModel):
    published: bool
    url: str
    social_media_posts: List[str]

# Create agents
analyzer = DjangoAgent[DjangoDeps, AnalysisResult](
    name="content_analyzer",
    deps_type=DjangoDeps,
    output_type=AnalysisResult,
    instructions="Analyze content quality, sentiment, and SEO potential"
)

enhancer = DjangoAgent[DjangoDeps, EnhancementResult](
    name="content_enhancer", 
    deps_type=DjangoDeps,
    output_type=EnhancementResult,
    instructions="Enhance content based on analysis suggestions"
)

publisher = DjangoAgent[DjangoDeps, PublishResult](
    name="content_publisher",
    deps_type=DjangoDeps,
    output_type=PublishResult,
    instructions="Publish content and create social media posts"
)

# Add tools to agents
@analyzer.tool
async def get_content_text(ctx: RunContext[DjangoDeps], content_id: int) -> str:
    content = await Content.objects.aget(id=content_id)
    return content.text

@enhancer.tool
async def save_enhanced_content(ctx: RunContext[DjangoDeps], content_id: int, enhanced_text: str) -> str:
    content = await Content.objects.aget(id=content_id)
    content.enhanced_text = enhanced_text
    await content.asave()
    return f"Enhanced content saved for {content_id}"

@publisher.tool
async def publish_to_cms(ctx: RunContext[DjangoDeps], content_id: int) -> str:
    content = await Content.objects.aget(id=content_id)
    content.status = "published"
    content.published_at = timezone.now()
    await content.asave()
    return f"Published content {content_id} to CMS"

# Create orchestrator and register agents
orchestrator = SimpleOrchestrator[DjangoDeps]()
orchestrator.register_agent(analyzer)
orchestrator.register_agent(enhancer)
orchestrator.register_agent(publisher)
```

## Using the Orchestrator

### In Django Views

```python
async def process_content_pipeline(request, content_id):
    """Process content through full pipeline."""
    
    # Create dependencies
    deps = DjangoDeps(user_id=request.user.id)
    
    try:
        # Execute full pipeline
        result = await orchestrator.execute(
            pattern="sequential",
            agents=["content_analyzer", "content_enhancer", "content_publisher"],
            prompt=f"Process content {content_id} through full publication pipeline",
            deps=deps
        )
        
        # Check if workflow completed successfully
        if result.status == "completed":
            return JsonResponse({
                'success': True,
                'workflow_status': result.status,
                'final_result': result.final_output.dict(),
                'steps_completed': len(result.step_results),
                'total_execution_time': result.execution_time
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error_message,
                'failed_at_step': result.failed_step
            }, status=500)
            
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Pipeline execution failed'
        }, status=500)
```

### Background Task Processing

```python
from django_cfg.modules.django_tasks import task

@task
async def process_content_background(content_id: int, user_id: int):
    """Process content in background."""
    
    deps = DjangoDeps(user_id=user_id)
    
    try:
        result = await orchestrator.execute(
            pattern="sequential",
            agents=["content_analyzer", "content_enhancer"],
            prompt=f"Analyze and enhance content {content_id}",
            deps=deps
        )
        
        # Send notification to user
        if result.status == "completed":
            await send_notification(
                user_id=user_id,
                message=f"Content {content_id} processing completed",
                data=result.final_output.dict()
            )
        
    except Exception as e:
        logger.error(f"Background processing failed: {e}")
        await send_notification(
            user_id=user_id,
            message=f"Content {content_id} processing failed: {e}",
            error=True
        )

# Usage in view
async def start_background_processing(request, content_id):
    # Queue background task
    await process_content_background.send(
        content_id=content_id,
        user_id=request.user.id
    )
    
    return JsonResponse({
        'message': 'Processing started in background',
        'content_id': content_id
    })
```

## Workflow Configuration

### Dynamic Workflows

```python
from django_cfg.modules.django_orchestrator import WorkflowConfig

# Define workflow configurations
CONTENT_WORKFLOWS = {
    "quick_analysis": WorkflowConfig(
        name="quick_analysis",
        steps=["content_analyzer"],
        strategy="sequential",
        description="Quick content analysis only"
    ),
    
    "full_pipeline": WorkflowConfig(
        name="full_pipeline", 
        steps=["content_analyzer", "content_enhancer", "content_publisher"],
        strategy="sequential",
        description="Complete content processing pipeline"
    ),
    
    "analysis_and_enhancement": WorkflowConfig(
        name="analysis_and_enhancement",
        steps=["content_analyzer", "content_enhancer"],
        strategy="sequential", 
        description="Analyze and enhance content without publishing"
    )
}

async def execute_workflow(request, workflow_name: str, content_id: int):
    """Execute predefined workflow."""
    
    if workflow_name not in CONTENT_WORKFLOWS:
        return JsonResponse({'error': 'Unknown workflow'}, status=400)
    
    workflow = CONTENT_WORKFLOWS[workflow_name]
    deps = DjangoDeps(user_id=request.user.id)
    
    result = await orchestrator.execute(
        pattern=workflow.strategy,
        agents=workflow.steps,
        prompt=f"Execute {workflow.description} for content {content_id}",
        deps=deps
    )
    
    return JsonResponse({
        'workflow': workflow.name,
        'status': result.status,
        'result': result.final_output.dict()
    })
```

## Error Handling and Recovery

### Handling Agent Failures

```python
async def robust_pipeline_execution(content_id: int, user_id: int):
    """Execute pipeline with error handling."""
    
    deps = DjangoDeps(user_id=user_id)
    
    try:
        result = await orchestrator.execute(
            pattern="sequential",
            agents=["content_analyzer", "content_enhancer", "content_publisher"],
            prompt=f"Process content {content_id}",
            deps=deps
        )
        
        return result
        
    except ExecutionError as e:
        logger.error(f"Pipeline failed: {e}")
        
        # Try fallback workflow (analysis only)
        try:
            fallback_result = await orchestrator.execute(
                pattern="sequential", 
                agents=["content_analyzer"],
                prompt=f"Analyze content {content_id} (fallback)",
                deps=deps
            )
            
            logger.info(f"Fallback analysis completed for content {content_id}")
            return fallback_result
            
        except ExecutionError as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise
```

## Monitoring and Metrics

### Orchestrator Metrics

```python
# Get orchestrator performance metrics
metrics = orchestrator.get_metrics()

print(f"Total workflows executed: {metrics['total_executions']}")
print(f"Success rate: {metrics['success_rate']:.1%}")
print(f"Average execution time: {metrics['avg_execution_time']:.2f}s")
print(f"Most used workflow: {metrics['most_used_pattern']}")

# Agent-specific metrics within orchestrator
for agent_name, agent_metrics in metrics['agent_metrics'].items():
    print(f"{agent_name}:")
    print(f"  - Executions: {agent_metrics['executions']}")
    print(f"  - Avg time: {agent_metrics['avg_time']:.2f}s")
    print(f"  - Error rate: {agent_metrics['error_rate']:.1%}")
```

### Workflow Tracking in Admin

The Django admin interface shows:

1. **WorkflowExecution** records:
   - Workflow name and configuration
   - Start/end times
   - Overall status
   - Final output

2. **AgentExecution** records (linked to workflow):
   - Individual agent performance
   - Step-by-step execution details
   - Token usage and costs

## Best Practices

### ✅ Good Practices

```python
# 1. Create orchestrator once, reuse
orchestrator = SimpleOrchestrator[DjangoDeps]()  # Module level

# 2. Register all agents at startup
orchestrator.register_agent(analyzer)
orchestrator.register_agent(enhancer)

# 3. Use meaningful agent names
agents=["content_analyzer", "seo_optimizer", "social_publisher"]

# 4. Handle errors gracefully
try:
    result = await orchestrator.execute(...)
except ExecutionError as e:
    # Handle specific error
    pass

# 5. Monitor performance
metrics = orchestrator.get_metrics()
```

### ❌ Bad Practices

```python
# 1. Creating orchestrator in views
def my_view(request):
    orchestrator = SimpleOrchestrator()  # Slow!

# 2. Not handling errors
result = await orchestrator.execute(...)  # Can crash

# 3. Using unclear agent names
agents=["agent1", "agent2", "agent3"]  # Confusing

# 4. Not monitoring performance
# No metrics collection or monitoring
```

## What's Next?

- **[Django Integration](django-integration)** - Admin interface, signals, middleware
- **[Examples](examples)** - Real-world use cases and patterns
