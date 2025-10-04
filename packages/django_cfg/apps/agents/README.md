# Django Orchestrator

Universal agent orchestration system for Django applications using Pydantic AI.

## Quick Start

```python
from django_cfg.modules.django_orchestrator import DjangoAgent, SimpleOrchestrator, DjangoDeps
from pydantic import BaseModel

# Define output model
class GreetingResult(BaseModel):
    greeting: str
    personalized: bool

# Create agent
agent = DjangoAgent[DjangoDeps, GreetingResult](
    name="greeter",
    deps_type=DjangoDeps,
    output_type=GreetingResult,
    instructions="Generate personalized greetings"
)

# Use orchestrator
orchestrator = SimpleOrchestrator()
orchestrator.register_agent(agent)

# Execute
deps = await DjangoDeps.from_user_id(user_id)
results = await orchestrator.execute(
    pattern="sequential",
    agents=["greeter"],
    prompt="Say hello",
    deps=deps
)
```

## Features

- 🎯 **Type-Safe Agents** - Full typing with `Agent[DepsT, OutputT]`
- 🔧 **Django Integration** - Native ORM, signals, and task support
- 📊 **Multiple Patterns** - Sequential, parallel, conditional execution
- ⚡ **KISS Design** - Simple, clean, no overengineering
- 🔄 **Reuses Existing** - Built on django_llm module
- 🧪 **Easy Testing** - Mock-friendly design

## Installation

Add to your Django settings:

```python
INSTALLED_APPS = [
    'django_cfg.modules.django_orchestrator',
]
```

Run migrations:

```bash
python manage.py migrate django_orchestrator
```

## Documentation

See the complete documentation in the `@docs2/` directory:

- **[index.md](@docs2/index.md)** - Module overview
- **[quick-start.md](@docs2/quick-start.md)** - Get started in 5 minutes
- **[api.md](@docs2/api.md)** - Complete API reference
- **[examples.md](@docs2/examples.md)** - Real-world usage patterns

## Architecture

```
django_orchestrator/
├── core/
│   ├── agent.py           # DjangoAgent wrapper
│   ├── orchestrator.py    # Main orchestrator
│   ├── dependencies.py    # Dependency injection
│   ├── models.py          # Data models
│   └── exceptions.py      # Custom exceptions
├── models/
│   ├── execution.py       # Execution tracking
│   ├── registry.py        # Agent registry
│   └── toolsets.py        # Tool management
├── examples/
│   └── simple_example.py  # Working examples
└── tests/
    └── test_core.py        # Test suite
```

## Examples

### Basic Agent

```python
@agent.tool
async def get_user_data(ctx: RunContext[DjangoDeps]) -> str:
    user = await User.objects.aget(id=ctx.deps.user.id)
    return f"User: {user.username}"

result = await agent.run("Get user info", deps=deps)
```

### Multi-Agent Pipeline

```python
orchestrator.register_agent(analyzer)
orchestrator.register_agent(processor)

results = await orchestrator.execute(
    pattern="sequential",
    agents=["analyzer", "processor"],
    prompt="Process content",
    deps=deps
)
```

## Testing

Run tests:

```bash
python -m pytest django_cfg/modules/django_orchestrator/tests/
```

## License

Part of django-cfg package.
