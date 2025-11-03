"""
Simple example demonstrating Django Orchestrator usage.
"""

import asyncio

from django.contrib.auth.models import User
from pydantic import BaseModel

from django_cfg.modules.django_orchestrator import (
    DjangoAgent,
    DjangoDeps,
    RunContext,
    SimpleOrchestrator,
)


# Define output model
class GreetingResult(BaseModel):
    """Result from greeting agent."""
    greeting: str
    personalized: bool
    user_info: str


# Create agent
greeting_agent = DjangoAgent[DjangoDeps, GreetingResult](
    name="greeting_agent",
    deps_type=DjangoDeps,
    output_type=GreetingResult,
    instructions="Generate personalized greetings for users"
)


# Add tools to agent
@greeting_agent.tool
async def get_user_info(ctx: RunContext[DjangoDeps]) -> str:
    """Get user information for personalization."""
    user = ctx.deps.user
    return f"User: {user.username}, Email: {user.email}, Joined: {user.date_joined}"


@greeting_agent.tool
async def get_time_of_day(ctx: RunContext[DjangoDeps]) -> str:
    """Get current time of day for greeting."""
    from datetime import datetime
    hour = datetime.now().hour

    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"


async def simple_example():
    """Run simple orchestrator example."""
    print("🤖 Django Orchestrator Simple Example")
    print("=" * 50)

    # Create test user (in real app, get from request)
    try:
        user = await User.objects.aget(username='testuser')
    except User.DoesNotExist:
        user = await User.objects.acreate_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

    # Create dependencies
    deps = DjangoDeps(user=user)

    # Create orchestrator
    orchestrator = SimpleOrchestrator()
    orchestrator.register_agent(greeting_agent)

    # Execute single agent
    print("\n1. Single Agent Execution:")
    results = await orchestrator.execute(
        pattern="sequential",
        agents=["greeting_agent"],
        prompt="Create a personalized greeting",
        deps=deps
    )

    result = results[0]
    print(f"✅ Agent: {result.agent_name}")
    print(f"✅ Output: {result.output}")
    print(f"✅ Execution Time: {result.execution_time:.2f}s")
    print(f"✅ Tokens Used: {result.tokens_used}")

    # Get metrics
    print("\n2. Agent Metrics:")
    metrics = greeting_agent.get_metrics()
    for key, value in metrics.items():
        print(f"📊 {key}: {value}")

    # Get orchestrator metrics
    print("\n3. Orchestrator Metrics:")
    orch_metrics = orchestrator.get_metrics()
    for key, value in orch_metrics.items():
        print(f"📈 {key}: {value}")


async def multi_agent_example():
    """Run multi-agent orchestrator example."""
    print("\n🤖 Multi-Agent Example")
    print("=" * 30)

    # Create additional agents
    analyzer_agent = DjangoAgent[DjangoDeps, BaseModel](
        name="content_analyzer",
        deps_type=DjangoDeps,
        output_type=BaseModel,
        instructions="Analyze content sentiment and topics"
    )

    formatter_agent = DjangoAgent[DjangoDeps, BaseModel](
        name="content_formatter",
        deps_type=DjangoDeps,
        output_type=BaseModel,
        instructions="Format content for display"
    )

    # Create orchestrator
    orchestrator = SimpleOrchestrator()
    orchestrator.register_agent(analyzer_agent)
    orchestrator.register_agent(formatter_agent)

    # Get user
    user = await User.objects.aget(username='testuser')
    deps = DjangoDeps(user=user)

    # Execute sequential workflow
    print("\n1. Sequential Workflow:")
    results = await orchestrator.execute(
        pattern="sequential",
        agents=["content_analyzer", "content_formatter"],
        prompt="Analyze and format this content: Hello world!",
        deps=deps
    )

    for i, result in enumerate(results, 1):
        print(f"Step {i} - {result.agent_name}: {result.success}")

    # Execute parallel workflow
    print("\n2. Parallel Workflow:")
    results = await orchestrator.execute(
        pattern="parallel",
        agents=["content_analyzer", "content_formatter"],
        prompt="Process content in parallel",
        deps=deps,
        max_concurrent=2
    )

    successful = sum(1 for r in results if r.success)
    print(f"✅ {successful}/{len(results)} agents completed successfully")


if __name__ == "__main__":
    # Run examples
    asyncio.run(simple_example())
    asyncio.run(multi_agent_example())
