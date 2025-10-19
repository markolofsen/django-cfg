---
title: Agent Examples
description: Django-CFG AI agents guide for examples. Build type-safe AI workflows with Django ORM integration, background processing, and production monitoring.
sidebar_label: Examples
sidebar_position: 5
keywords:
  - django AI examples
  - AI agent use cases django
  - django AI automation examples
  - pydantic AI examples
---
# Real-World Examples and Use Cases

## Example 1: E-commerce Product Analysis

### Scenario
Automatically analyze product descriptions, generate SEO content, and update product listings.

### Implementation

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    keywords = models.JSONField(default=list)
    ai_analysis = models.JSONField(null=True, blank=True)

# agents.py
from django_cfg import DjangoAgent, DjangoDeps
from pydantic import BaseModel
from typing import List

@dataclass
class ProductDeps(DjangoDeps):
    product_id: int
    
    async def get_product(self):
        return await Product.objects.aget(id=self.product_id)

class ProductAnalysis(BaseModel):
    sentiment: str
    key_features: List[str]
    target_audience: str
    price_competitiveness: str
    seo_keywords: List[str]

class SEOContent(BaseModel):
    seo_title: str
    seo_description: str
    keywords: List[str]
    content_score: float

# Create agents
product_analyzer = DjangoAgent[ProductDeps, ProductAnalysis](
    name="product_analyzer",
    deps_type=ProductDeps,
    output_type=ProductAnalysis,
    instructions="""
    Analyze product descriptions for:
    - Sentiment and appeal
    - Key features and benefits
    - Target audience
    - Price competitiveness
    - SEO keyword opportunities
    """
)

seo_generator = DjangoAgent[ProductDeps, SEOContent](
    name="seo_generator",
    deps_type=ProductDeps,
    output_type=SEOContent,
    instructions="""
    Generate SEO-optimized content:
    - Compelling title (max 60 chars)
    - Meta description (max 160 chars)
    - Relevant keywords
    - Score content quality 0-1
    """
)

# Add tools
@product_analyzer.tool
async def get_product_details(ctx: RunContext[ProductDeps]) -> str:
    """Get complete product information."""
    product = await ctx.deps.get_product()
    category = await product.category
    
    return f"""
    Product: {product.name}
    Category: {category.name}
    Price: ${product.price}
    Description: {product.description}
    """

@product_analyzer.tool
async def get_competitor_prices(ctx: RunContext[ProductDeps], category_name: str) -> str:
    """Get competitor pricing information."""
    # Simplified competitor analysis
    avg_price = await Product.objects.filter(
        category__name=category_name
    ).aggregate(avg_price=models.Avg('price'))['avg_price']
    
    return f"Average category price: ${avg_price:.2f}"

@seo_generator.tool
async def save_seo_content(
    ctx: RunContext[ProductDeps],
    seo_title: str,
    seo_description: str,
    keywords: List[str]
) -> str:
    """Save generated SEO content to product."""
    product = await ctx.deps.get_product()
    product.seo_title = seo_title
    product.seo_description = seo_description
    product.keywords = keywords
    await product.asave()
    
    return f"SEO content saved for product {product.id}"

# Orchestrator setup
product_orchestrator = SimpleOrchestrator[ProductDeps]()
product_orchestrator.register_agent(product_analyzer)
product_orchestrator.register_agent(seo_generator)

# Usage in views
async def optimize_product_seo(request, product_id):
    """Optimize product for SEO."""
    
    deps = ProductDeps(
        user_id=request.user.id,
        product_id=product_id
    )
    
    try:
        result = await product_orchestrator.execute(
            pattern="sequential",
            agents=["product_analyzer", "seo_generator"],
            prompt=f"Analyze and optimize SEO for product {product_id}",
            deps=deps
        )
        
        return JsonResponse({
            'success': True,
            'analysis': result.step_results[0]['output'],
            'seo_content': result.step_results[1]['output'],
            'execution_time': result.execution_time
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Example 2: Customer Support Automation

### Scenario
Automatically categorize support tickets, generate responses, and escalate complex issues.

### Implementation

```python
# models.py
class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    ai_response = models.TextField(blank=True)
    requires_human = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

# agents.py
@dataclass
class SupportDeps(DjangoDeps):
    ticket_id: int
    
    async def get_ticket(self):
        return await SupportTicket.objects.select_related('customer').aget(id=self.ticket_id)

class TicketAnalysis(BaseModel):
    category: str  # "billing", "technical", "general", "complaint"
    priority: str  # "low", "medium", "high", "urgent"
    sentiment: str  # "positive", "negative", "neutral"
    complexity: str  # "simple", "moderate", "complex"
    requires_human: bool
    confidence: float

class SupportResponse(BaseModel):
    response_text: str
    suggested_actions: List[str]
    escalate: bool
    follow_up_needed: bool

# Create agents
ticket_analyzer = DjangoAgent[SupportDeps, TicketAnalysis](
    name="ticket_analyzer",
    deps_type=SupportDeps,
    output_type=TicketAnalysis,
    instructions="""
    Analyze support tickets for:
    - Category (billing, technical, general, complaint)
    - Priority level based on urgency and impact
    - Customer sentiment
    - Complexity level
    - Whether human intervention is needed
    """
)

response_generator = DjangoAgent[SupportDeps, SupportResponse](
    name="response_generator",
    deps_type=SupportDeps,
    output_type=SupportResponse,
    instructions="""
    Generate helpful support responses:
    - Professional and empathetic tone
    - Address specific customer concerns
    - Provide actionable solutions
    - Suggest next steps
    - Determine if escalation needed
    """
)

# Add tools
@ticket_analyzer.tool
async def get_ticket_details(ctx: RunContext[SupportDeps]) -> str:
    """Get complete ticket information."""
    ticket = await ctx.deps.get_ticket()
    
    return f"""
    Ticket ID: {ticket.id}
    Customer: {ticket.customer.username} ({ticket.customer.email})
    Subject: {ticket.subject}
    Description: {ticket.description}
    Created: {ticket.created_at}
    """

@ticket_analyzer.tool
async def get_customer_history(ctx: RunContext[SupportDeps]) -> str:
    """Get customer's previous tickets."""
    ticket = await ctx.deps.get_ticket()
    
    previous_tickets = await SupportTicket.objects.filter(
        customer=ticket.customer
    ).exclude(id=ticket.id).order_by('-created_at')[:5].aall()
    
    if not previous_tickets:
        return "No previous tickets found"
    
    history = []
    for prev_ticket in previous_tickets:
        history.append(f"- {prev_ticket.subject} ({prev_ticket.status})")
    
    return "Previous tickets:\n" + "\n".join(history)

@response_generator.tool
async def get_knowledge_base_articles(ctx: RunContext[SupportDeps], category: str) -> str:
    """Get relevant knowledge base articles."""
    # Simplified KB lookup
    kb_articles = {
        'billing': [
            "How to update payment method",
            "Understanding your invoice",
            "Refund policy"
        ],
        'technical': [
            "Troubleshooting login issues",
            "API documentation",
            "System requirements"
        ],
        'general': [
            "Getting started guide",
            "Account settings",
            "Contact information"
        ]
    }
    
    articles = kb_articles.get(category, [])
    return "Relevant articles:\n" + "\n".join(f"- {article}" for article in articles)

@response_generator.tool
async def save_response(ctx: RunContext[SupportDeps], response_text: str, escalate: bool) -> str:
    """Save generated response to ticket."""
    ticket = await ctx.deps.get_ticket()
    ticket.ai_response = response_text
    ticket.requires_human = escalate
    
    if not escalate:
        ticket.status = 'in_progress'
    
    await ticket.asave()
    return f"Response saved for ticket {ticket.id}"

# Orchestrator setup
support_orchestrator = SimpleOrchestrator[SupportDeps]()
support_orchestrator.register_agent(ticket_analyzer)
support_orchestrator.register_agent(response_generator)

# Usage with signals
from django.db.models.signals import post_save

@receiver(post_save, sender=SupportTicket)
async def process_new_ticket(sender, instance, created, **kwargs):
    """Automatically process new support tickets."""
    
    if created:
        deps = SupportDeps(
            user_id=instance.customer.id,
            ticket_id=instance.id
        )
        
        try:
            result = await support_orchestrator.execute(
                pattern="sequential",
                agents=["ticket_analyzer", "response_generator"],
                prompt=f"Process support ticket {instance.id}",
                deps=deps
            )
            
            # Update ticket with analysis results
            analysis = result.step_results[0]['output']
            instance.category = analysis['category']
            instance.priority = analysis['priority']
            await instance.asave()
            
            # Send notification if human intervention needed
            if analysis['requires_human']:
                await notify_support_team(instance.id, analysis['priority'])
                
        except Exception as e:
            logger.error(f"Failed to process ticket {instance.id}: {e}")
```

## Example 3: Content Moderation Pipeline

### Scenario
Automatically moderate user-generated content, detect inappropriate material, and take appropriate actions.

### Implementation

```python
# models.py
class UserContent(models.Model):
    CONTENT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('review', 'Review'),
        ('message', 'Message')
    ]
    
    MODERATION_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('flagged', 'Flagged for Review')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    moderation_status = models.CharField(max_length=20, choices=MODERATION_STATUS, default='pending')
    moderation_score = models.FloatField(null=True, blank=True)
    moderation_flags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

# agents.py
class ModerationAnalysis(BaseModel):
    is_appropriate: bool
    toxicity_score: float  # 0-1, higher = more toxic
    detected_issues: List[str]  # ["spam", "hate_speech", "inappropriate_language"]
    confidence: float
    requires_human_review: bool

class ModerationAction(BaseModel):
    action: str  # "approve", "reject", "flag", "auto_edit"
    reason: str
    suggested_edit: Optional[str] = None
    notify_user: bool
    escalate: bool

# Create agents
content_moderator = DjangoAgent[DjangoDeps, ModerationAnalysis](
    name="content_moderator",
    deps_type=DjangoDeps,
    output_type=ModerationAnalysis,
    instructions="""
    Analyze content for moderation:
    - Detect toxic, harmful, or inappropriate content
    - Identify spam, hate speech, harassment
    - Check for policy violations
    - Assess if human review is needed
    - Provide confidence scores
    """
)

action_decider = DjangoAgent[DjangoDeps, ModerationAction](
    name="action_decider",
    deps_type=DjangoDeps,
    output_type=ModerationAction,
    instructions="""
    Decide moderation actions based on analysis:
    - Approve safe content automatically
    - Reject clearly inappropriate content
    - Flag borderline cases for human review
    - Suggest edits when possible
    - Determine user notification needs
    """
)

# Add tools
@content_moderator.tool
async def get_content_details(ctx: RunContext[DjangoDeps], content_id: int) -> str:
    """Get content for moderation."""
    content = await UserContent.objects.select_related('user').aget(id=content_id)
    
    return f"""
    Content ID: {content.id}
    Type: {content.content_type}
    User: {content.user.username} (joined: {content.user.date_joined})
    Title: {content.title}
    Text: {content.text}
    Created: {content.created_at}
    """

@content_moderator.tool
async def get_user_history(ctx: RunContext[DjangoDeps], user_id: int) -> str:
    """Get user's moderation history."""
    user = await User.objects.aget(id=user_id)
    
    # Get recent moderation results
    recent_content = await UserContent.objects.filter(
        user=user
    ).exclude(moderation_status='pending').order_by('-created_at')[:10].aall()
    
    if not recent_content:
        return "No previous content found"
    
    approved = sum(1 for c in recent_content if c.moderation_status == 'approved')
    rejected = sum(1 for c in recent_content if c.moderation_status == 'rejected')
    
    return f"User history: {approved} approved, {rejected} rejected out of {len(recent_content)} recent items"

@action_decider.tool
async def apply_moderation_action(
    ctx: RunContext[DjangoDeps],
    content_id: int,
    action: str,
    reason: str,
    score: float
) -> str:
    """Apply moderation decision."""
    content = await UserContent.objects.aget(id=content_id)
    
    status_map = {
        'approve': 'approved',
        'reject': 'rejected',
        'flag': 'flagged'
    }
    
    content.moderation_status = status_map.get(action, 'pending')
    content.moderation_score = score
    content.moderation_flags = [reason] if action != 'approve' else []
    await content.asave()
    
    return f"Applied {action} to content {content_id}: {reason}"

# Orchestrator setup
moderation_orchestrator = SimpleOrchestrator[DjangoDeps]()
moderation_orchestrator.register_agent(content_moderator)
moderation_orchestrator.register_agent(action_decider)

# Background processing
from django_cfg.modules.django_tasks import task

@task
async def moderate_content_batch():
    """Process pending content moderation."""
    
    pending_content = UserContent.objects.filter(
        moderation_status='pending'
    ).order_by('created_at')[:50]  # Process 50 at a time
    
    async for content in pending_content:
        deps = DjangoDeps(user_id=content.user.id)
        
        try:
            result = await moderation_orchestrator.execute(
                pattern="sequential",
                agents=["content_moderator", "action_decider"],
                prompt=f"Moderate content {content.id}",
                deps=deps
            )
            
            # Log moderation result
            logger.info(f"Moderated content {content.id}: {result.final_output}")
            
        except Exception as e:
            logger.error(f"Moderation failed for content {content.id}: {e}")

# Schedule regular moderation
# In your Django settings or celery beat schedule:
# CELERY_BEAT_SCHEDULE = {
#     'moderate-content': {
#         'task': 'moderate_content_batch',
#         'schedule': 60.0,  # Every minute
#     },
# }
```

## Example 4: Learning Management System

### Scenario
Automatically assess student submissions, provide feedback, and generate personalized learning recommendations.

### Implementation

```python
# models.py
class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    max_score = models.IntegerField(default=100)
    rubric = models.JSONField()  # Grading criteria

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    human_review_needed = models.BooleanField(default=False)

# agents.py
class AssessmentResult(BaseModel):
    score: float  # 0-100
    strengths: List[str]
    areas_for_improvement: List[str]
    detailed_feedback: str
    meets_criteria: dict  # rubric item -> bool
    confidence: float

class LearningRecommendation(BaseModel):
    recommended_resources: List[str]
    next_steps: List[str]
    difficulty_adjustment: str  # "increase", "maintain", "decrease"
    estimated_study_time: int  # minutes

# Create assessment agent
assignment_assessor = DjangoAgent[DjangoDeps, AssessmentResult](
    name="assignment_assessor",
    deps_type=DjangoDeps,
    output_type=AssessmentResult,
    instructions="""
    Assess student submissions fairly and constructively:
    - Evaluate against provided rubric
    - Identify strengths and areas for improvement
    - Provide specific, actionable feedback
    - Assign appropriate scores
    - Maintain encouraging tone
    """
)

# Usage example
async def assess_submission(submission_id: int):
    """Assess a student submission."""
    
    submission = await Submission.objects.select_related(
        'student', 'assignment'
    ).aget(id=submission_id)
    
    deps = DjangoDeps(user_id=submission.student.id)
    
    result = await assignment_assessor.run(
        prompt=f"""
        Assess this submission for assignment "{submission.assignment.title}":
        
        Assignment Description: {submission.assignment.description}
        Rubric: {json.dumps(submission.assignment.rubric, indent=2)}
        Student Submission: {submission.content}
        """,
        deps=deps
    )
    
    # Save results
    submission.ai_score = result.output.score
    submission.ai_feedback = result.output.detailed_feedback
    submission.human_review_needed = result.output.confidence < 0.8
    await submission.asave()
    
    return result.output
```

## Best Practices from Examples

### 1. Dependency Design
```python
# ✅ Good - Specific dependencies for domain
@dataclass
class ProductDeps(DjangoDeps):
    product_id: int
    
    async def get_product(self):
        return await Product.objects.aget(id=self.product_id)

# ❌ Bad - Generic dependencies everywhere
deps = DjangoDeps(user_id=user_id)  # No domain context
```

### 2. Tool Organization
```python
# ✅ Good - Tools are focused and reusable
@agent.tool
async def get_product_details(ctx: RunContext[ProductDeps]) -> str:
    """Get complete product information."""
    # Single responsibility

@agent.tool  
async def save_seo_content(ctx: RunContext[ProductDeps], **kwargs) -> str:
    """Save SEO content to product."""
    # Clear purpose
```

### 3. Error Handling
```python
# ✅ Good - Comprehensive error handling
try:
    result = await orchestrator.execute(...)
    return JsonResponse({'success': True, 'data': result.output.dict()})
except ExecutionError as e:
    logger.error(f"Execution failed: {e}")
    return JsonResponse({'error': 'Processing failed'}, status=500)
except ValidationError as e:
    return JsonResponse({'error': 'Invalid input'}, status=400)
```

### 4. Background Processing
```python
# ✅ Good - Use background tasks for heavy processing
@task
async def process_content_batch():
    """Process multiple items in background."""
    # Batch processing logic

# ❌ Bad - Blocking view with heavy processing
async def my_view(request):
    result = await heavy_orchestrator.execute(...)  # Blocks user
```

These examples show how Django Orchestrator can be used for various real-world scenarios while maintaining clean, maintainable code with proper error handling and Django integration.
