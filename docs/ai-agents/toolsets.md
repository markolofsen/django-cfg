---
title: Agent Toolsets
description: Django-CFG AI agents guide for toolsets. Build type-safe AI workflows with Django ORM integration, background processing, and production monitoring.
sidebar_label: Toolsets
sidebar_position: 6
keywords:
  - django-cfg toolsets
  - django toolsets
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Agent Toolsets

:::tip[Powerful Agent Capabilities]
Django-CFG provides **comprehensive toolsets** that give AI agents powerful capabilities to interact with Django applications - cache, ORM, files, and Django-specific operations.
:::

Django-CFG provides **comprehensive toolsets** that give AI agents powerful capabilities to interact with Django applications, including cache operations, ORM queries, file handling, and Django-specific functionality.

## Overview

:::info[Built-in Toolsets]
Four powerful toolsets ready to use out of the box:
- ✅ **Cache Toolset** - Redis, Memcached, database cache
- ✅ **ORM Toolset** - Type-safe database queries
- ✅ **File Toolset** - File system operations
- ✅ **Django Toolset** - Django utilities
- ✅ **Custom Toolsets** - Extensible framework
:::

## Quick Start

### Using Built-in Toolsets

```python
from django_cfg.apps.agents import Agent
from django_cfg.apps.agents.toolsets import (
    CacheToolset, 
    ORMToolset, 
    FileToolset, 
    DjangoToolset
)

# Create agent with multiple toolsets
agent = Agent(
    model='gpt-4',
    system_prompt="You are a helpful Django assistant with access to cache, database, and file operations.",
    toolsets=[
        CacheToolset(cache_alias='default', key_prefix='agent'),
        ORMToolset(allowed_models=['auth.User', 'myapp.Product']),
        FileToolset(base_path='/app/media/', allowed_extensions=['.jpg', '.png', '.pdf']),
        DjangoToolset()
    ]
)

# Agent can now use all toolset capabilities
result = agent.run(
    "Cache the user count and save it to a file",
    deps=DjangoDeps(user=request.user)
)
```

## Toolset Reference

<Tabs>
  <TabItem value="cache" label="Cache Toolset" default>

### Cache Operations

```python
from django_cfg.apps.agents.toolsets import CacheToolset

# Initialize cache toolset
cache_toolset = CacheToolset(
    cache_alias='default',
    key_prefix='agent_cache'
)

# Agent with cache capabilities
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to Django cache operations. You can:
    - Store and retrieve cached data
    - Manage cache keys and expiration
    - Get cache statistics
    - Clear cache when needed
    """,
    toolsets=[cache_toolset]
)

# Example agent interactions
result = agent.run("Store the current user count in cache for 1 hour")
# Agent will use cache_set tool to store User.objects.count()

result = agent.run("Get the cached user count")
# Agent will use cache_get tool to retrieve the value

result = agent.run("Clear all cache keys starting with 'user_'")
# Agent will use cache_delete_pattern tool
```

:::note[Cache Toolset Benefits]
**Use Cache Toolset when agents need to:**
- ✅ Store temporary data (session data, API responses)
- ✅ Reduce database load (cache query results)
- ✅ Improve performance (avoid repeated calculations)
- ✅ Share data between agent executions

**Performance:**
- **Cache hit**: ~1ms response time
- **Cost savings**: 80% reduction in LLM calls with caching
- **Scalability**: Supports Redis, Memcached, database backends
:::

  </TabItem>
  <TabItem value="orm" label="ORM Toolset">

### Database Operations

```python
from django_cfg.apps.agents.toolsets import ORMToolset

# Initialize ORM toolset with model restrictions
orm_toolset = ORMToolset(
    allowed_models=[
        'auth.User',
        'auth.Group',
        'myapp.Product',
        'myapp.Order',
        'myapp.Customer'
    ],
    read_only=False,  # Allow write operations
    max_results=100   # Limit query results
)

# Agent with database access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to Django ORM operations. You can:
    - Query models safely with type checking
    - Create, update, and delete records
    - Perform complex queries with filters
    - Aggregate data and generate reports

    Always follow these rules:
    - Validate data before creating/updating
    - Use transactions for multiple operations
    - Respect model permissions and constraints
    """,
    toolsets=[orm_toolset]
)

# Example queries
result = agent.run("Find all active users who joined in the last 30 days")
result = agent.run("Create a new product with name 'AI Assistant' and price $99.99")
result = agent.run("Update all orders with status 'pending' to 'processing'")
```

:::warning[ORM Security]
**Security considerations:**
- ⚠️ **Model restrictions** - Limit `allowed_models` to necessary models only
- ⚠️ **Read-only mode** - Use `read_only=True` for reporting agents
- ⚠️ **Query limits** - Set `max_results` to prevent memory issues
- ⚠️ **Permissions** - Respect Django model permissions

**Best practices:**
- ✅ Use specific model lists (not `['*']` in production)
- ✅ Enable read-only for data analysis agents
- ✅ Validate all input data before database operations
- ✅ Use transactions for multi-step operations
:::

  </TabItem>
  <TabItem value="file" label="File Toolset">

### File Operations

```python
from django_cfg.apps.agents.toolsets import FileToolset

# Initialize file toolset with security restrictions
file_toolset = FileToolset(
    base_path='/app/media/',
    allowed_extensions=['.jpg', '.png', '.gif', '.pdf', '.txt', '.csv'],
    max_file_size=10 * 1024 * 1024,  # 10MB limit
    allowed_operations=['read', 'write', 'delete', 'list']
)

# Agent with file access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to file system operations. You can:
    - Read and write files safely
    - Process images and documents
    - Generate reports and exports
    - Manage file uploads and downloads

    Security rules:
    - Only access files within allowed directories
    - Validate file types and sizes
    - Sanitize file names and paths
    """,
    toolsets=[file_toolset, ORMToolset()]
)

# Example file operations
result = agent.run("Read the latest sales report CSV and summarize the data")
result = agent.run("Generate a PDF report of all active users")
result = agent.run("Process uploaded product images and create thumbnails")
```

:::danger[File Security Critical]
**File operations are high-risk. Always:**
- 🔒 **Restrict base_path** - Never use system root `/`
- 🔒 **Whitelist extensions** - Block executables (.exe, .sh, .py)
- 🔒 **Limit file size** - Prevent disk space attacks
- 🔒 **Sanitize paths** - Prevent directory traversal (../)
- 🔒 **Validate content** - Check file type matches extension

**Dangerous patterns to avoid:**
- ❌ `base_path='/'` - Full system access
- ❌ `allowed_extensions=['*']` - Any file type
- ❌ `max_file_size=None` - Unlimited uploads
- ❌ No path validation - Directory traversal attacks
:::

  </TabItem>
  <TabItem value="django" label="Django Toolset">

### Django Integration

```python
from django_cfg.apps.agents.toolsets import DjangoToolset

# Initialize Django toolset
django_toolset = DjangoToolset(
    allowed_commands=['collectstatic', 'migrate', 'check'],
    allowed_settings=['DEBUG', 'ALLOWED_HOSTS'],
    enable_admin_access=True
)

# Agent with Django access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to Django framework operations. You can:
    - Run management commands
    - Access Django settings
    - Interact with admin interface
    - Monitor application health

    Use Django best practices and security guidelines.
    """,
    toolsets=[django_toolset]
)

# Example Django operations
result = agent.run("Check if there are any pending migrations")
result = agent.run("Collect static files for production deployment")
result = agent.run("Validate current Django configuration")
```

:::warning[Django Toolset Permissions]
**Management commands can be dangerous:**
- ⚠️ Restrict `allowed_commands` to safe operations only
- ⚠️ Never allow destructive commands (`flush`, `sqlflush`)
- ⚠️ Limit settings access to non-sensitive values
- ⚠️ Use with admin/staff users only

**Safe commands:**
- ✅ `check` - Validate configuration
- ✅ `migrate` - Apply migrations (with caution)
- ✅ `collectstatic` - Collect static files
- ✅ `clearsessions` - Remove expired sessions

**Dangerous commands:**
- ❌ `flush` - Deletes all data
- ❌ `shell` - Python shell access
- ❌ `dbshell` - Database shell access
- ❌ `runserver` - Development server
:::

  </TabItem>
</Tabs>

### Cache Tool Functions

The Cache Toolset provides these tools to agents:

```python
# Available cache tools:
@tool
def cache_get(key: str, default: Any = None) -> Any:
    """Get value from cache"""
    
@tool  
def cache_set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
    """Set value in cache with optional timeout"""
    
@tool
def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    
@tool
def cache_get_many(keys: List[str]) -> Dict[str, Any]:
    """Get multiple values from cache"""
    
@tool
def cache_set_many(data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
    """Set multiple values in cache"""
    
@tool
def cache_delete_pattern(pattern: str) -> int:
    """Delete keys matching pattern"""
    
@tool
def cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    
@tool
def cache_clear() -> bool:
    """Clear entire cache"""
```

### Advanced Cache Usage

```python
class SmartCacheAgent(Agent):
    """Agent with intelligent caching strategies"""
    
    def __init__(self):
        super().__init__(
            model='gpt-4',
            system_prompt="""
            You are a caching expert. You can:
            1. Analyze data access patterns
            2. Implement smart caching strategies
            3. Optimize cache performance
            4. Monitor cache hit rates
            
            Always consider:
            - Cache expiration times based on data volatility
            - Memory usage and cache size limits
            - Cache invalidation strategies
            """,
            toolsets=[
                CacheToolset(cache_alias='default'),
                CacheToolset(cache_alias='redis', key_prefix='redis_cache'),
                ORMToolset()  # For database queries
            ]
        )
    
    def optimize_user_data_caching(self, user_id: int):
        """Optimize caching for user-specific data"""
        return self.run(f"""
        Analyze and optimize caching for user {user_id}:
        1. Cache user profile data for 30 minutes
        2. Cache user preferences for 1 hour  
        3. Cache user activity for 5 minutes
        4. Set up cache warming for frequently accessed data
        """, deps=DjangoDeps(user_id=user_id))

# Usage
cache_agent = SmartCacheAgent()
result = cache_agent.optimize_user_data_caching(user_id=123)
```

## 🗃️ ORM Toolset

### Database Operations

```python
from django_cfg.apps.agents.toolsets import ORMToolset

# Initialize ORM toolset with model restrictions
orm_toolset = ORMToolset(
    allowed_models=[
        'auth.User',
        'auth.Group', 
        'myapp.Product',
        'myapp.Order',
        'myapp.Customer'
    ],
    read_only=False,  # Allow write operations
    max_results=100   # Limit query results
)

# Agent with database access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to Django ORM operations. You can:
    - Query models safely with type checking
    - Create, update, and delete records
    - Perform complex queries with filters
    - Aggregate data and generate reports
    
    Always follow these rules:
    - Validate data before creating/updating
    - Use transactions for multiple operations
    - Respect model permissions and constraints
    """,
    toolsets=[orm_toolset]
)

# Example queries
result = agent.run("Find all active users who joined in the last 30 days")
result = agent.run("Create a new product with name 'AI Assistant' and price $99.99")
result = agent.run("Update all orders with status 'pending' to 'processing'")
```

### ORM Tool Functions

```python
# Available ORM tools:
@tool
def model_query(
    model: str, 
    filters: Dict[str, Any] = None,
    exclude: Dict[str, Any] = None,
    order_by: List[str] = None,
    limit: int = None
) -> List[Dict[str, Any]]:
    """Query model with filters"""

@tool
def model_get(model: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Get single model instance"""

@tool
def model_create(model: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new model instance"""

@tool
def model_update(
    model: str, 
    filters: Dict[str, Any],
    data: Dict[str, Any]
) -> int:
    """Update model instances"""

@tool
def model_delete(model: str, filters: Dict[str, Any]) -> int:
    """Delete model instances"""

@tool
def model_aggregate(
    model: str,
    aggregations: Dict[str, str],
    filters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Perform aggregations"""

@tool
def model_count(model: str, filters: Dict[str, Any] = None) -> int:
    """Count model instances"""

@tool
def model_exists(model: str, filters: Dict[str, Any]) -> bool:
    """Check if instances exist"""
```

### Advanced ORM Usage

```python
class DataAnalysisAgent(Agent):
    """Agent specialized in data analysis and reporting"""
    
    def __init__(self):
        super().__init__(
            model='gpt-4',
            system_prompt="""
            You are a data analyst with access to the database. You can:
            1. Generate comprehensive reports
            2. Identify trends and patterns
            3. Perform statistical analysis
            4. Create data visualizations
            
            Always:
            - Use efficient queries with proper indexing
            - Aggregate data at the database level when possible
            - Provide insights along with raw data
            """,
            toolsets=[
                ORMToolset(allowed_models=['*'], read_only=True),
                CacheToolset()  # Cache expensive queries
            ]
        )
    
    def generate_sales_report(self, start_date: str, end_date: str):
        """Generate comprehensive sales report"""
        return self.run(f"""
        Generate a sales report for {start_date} to {end_date}:
        
        1. Total sales and revenue
        2. Top-selling products
        3. Customer acquisition metrics
        4. Geographic sales distribution
        5. Daily/weekly trends
        
        Cache the results for 1 hour and provide actionable insights.
        """)

# Usage
analyst = DataAnalysisAgent()
report = analyst.generate_sales_report('2023-11-01', '2023-11-30')
```

## 📁 File Toolset

### File Operations

```python
from django_cfg.apps.agents.toolsets import FileToolset

# Initialize file toolset with security restrictions
file_toolset = FileToolset(
    base_path='/app/media/',
    allowed_extensions=['.jpg', '.png', '.gif', '.pdf', '.txt', '.csv'],
    max_file_size=10 * 1024 * 1024,  # 10MB limit
    allowed_operations=['read', 'write', 'delete', 'list']
)

# Agent with file access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to file system operations. You can:
    - Read and write files safely
    - Process images and documents
    - Generate reports and exports
    - Manage file uploads and downloads
    
    Security rules:
    - Only access files within allowed directories
    - Validate file types and sizes
    - Sanitize file names and paths
    """,
    toolsets=[file_toolset, ORMToolset()]
)

# Example file operations
result = agent.run("Read the latest sales report CSV and summarize the data")
result = agent.run("Generate a PDF report of all active users")
result = agent.run("Process uploaded product images and create thumbnails")
```

### File Tool Functions

```python
# Available file tools:
@tool
def file_read(path: str, encoding: str = 'utf-8') -> str:
    """Read file content"""

@tool
def file_write(path: str, content: str, encoding: str = 'utf-8') -> bool:
    """Write content to file"""

@tool
def file_append(path: str, content: str, encoding: str = 'utf-8') -> bool:
    """Append content to file"""

@tool
def file_delete(path: str) -> bool:
    """Delete file"""

@tool
def file_exists(path: str) -> bool:
    """Check if file exists"""

@tool
def file_info(path: str) -> Dict[str, Any]:
    """Get file information"""

@tool
def file_list(directory: str, pattern: str = '*') -> List[str]:
    """List files in directory"""

@tool
def file_copy(source: str, destination: str) -> bool:
    """Copy file"""

@tool
def file_move(source: str, destination: str) -> bool:
    """Move file"""

@tool
def directory_create(path: str) -> bool:
    """Create directory"""

@tool
def directory_delete(path: str, recursive: bool = False) -> bool:
    """Delete directory"""
```

### Advanced File Processing

```python
class DocumentProcessorAgent(Agent):
    """Agent specialized in document processing"""
    
    def __init__(self):
        super().__init__(
            model='gpt-4',
            system_prompt="""
            You are a document processing specialist. You can:
            1. Process various file formats (PDF, CSV, images)
            2. Extract and analyze content
            3. Generate reports and summaries
            4. Convert between formats
            
            Always:
            - Validate file integrity before processing
            - Handle errors gracefully
            - Provide progress updates for large files
            """,
            toolsets=[
                FileToolset(base_path='/app/media/'),
                ORMToolset()  # For storing results
            ]
        )
    
    def process_invoice_batch(self, directory: str):
        """Process batch of invoice PDFs"""
        return self.run(f"""
        Process all PDF invoices in {directory}:
        
        1. Extract invoice data (amount, date, vendor)
        2. Validate data integrity
        3. Store in database
        4. Generate processing report
        5. Move processed files to archive
        
        Handle any errors gracefully and report issues.
        """)

# Usage
processor = DocumentProcessorAgent()
result = processor.process_invoice_batch('/app/media/invoices/pending/')
```

## Django Toolset

### Django Integration

```python
from django_cfg.apps.agents.toolsets import DjangoToolset

# Initialize Django toolset
django_toolset = DjangoToolset(
    allowed_commands=['collectstatic', 'migrate', 'check'],
    allowed_settings=['DEBUG', 'ALLOWED_HOSTS'],
    enable_admin_access=True
)

# Agent with Django access
agent = Agent(
    model='gpt-4',
    system_prompt="""
    You have access to Django framework operations. You can:
    - Run management commands
    - Access Django settings
    - Interact with admin interface
    - Monitor application health
    
    Use Django best practices and security guidelines.
    """,
    toolsets=[django_toolset]
)

# Example Django operations
result = agent.run("Check if there are any pending migrations")
result = agent.run("Collect static files for production deployment")
result = agent.run("Validate current Django configuration")
```

### Django Tool Functions

```python
# Available Django tools:
@tool
def run_management_command(command: str, args: List[str] = None) -> str:
    """Run Django management command"""

@tool
def get_setting(name: str) -> Any:
    """Get Django setting value"""

@tool
def check_migrations(app: str = None) -> Dict[str, Any]:
    """Check migration status"""

@tool
def get_installed_apps() -> List[str]:
    """Get list of installed Django apps"""

@tool
def get_url_patterns() -> List[Dict[str, str]]:
    """Get URL patterns"""

@tool
def validate_configuration() -> Dict[str, Any]:
    """Validate Django configuration"""

@tool
def get_database_info() -> Dict[str, Any]:
    """Get database configuration info"""

@tool
def clear_cache(cache_name: str = 'default') -> bool:
    """Clear Django cache"""
```

## Custom Toolsets

### Creating Custom Toolsets

```python
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai import tool
from django_cfg.apps.agents.core.dependencies import DjangoDeps

class PaymentToolset(AbstractToolset[DjangoDeps]):
    """Custom toolset for payment operations"""
    
    def __init__(self, payment_provider: str = 'stripe'):
        self.payment_provider = payment_provider
    
    @property
    def id(self) -> str:
        return f"payment_{self.payment_provider}"
    
    @tool
    def process_payment(
        self, 
        amount: float, 
        currency: str = 'USD',
        customer_id: str = None
    ) -> Dict[str, Any]:
        """Process payment through payment provider"""
        # Implementation for payment processing
        return {
            'status': 'success',
            'transaction_id': 'txn_123456',
            'amount': amount,
            'currency': currency
        }
    
    @tool
    def refund_payment(self, transaction_id: str, amount: float = None) -> Dict[str, Any]:
        """Refund payment"""
        # Implementation for refund processing
        return {
            'status': 'refunded',
            'refund_id': 'ref_123456',
            'amount': amount
        }
    
    @tool
    def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get payment status"""
        # Implementation for status check
        return {
            'transaction_id': transaction_id,
            'status': 'completed',
            'amount': 99.99
        }

# Use custom toolset
payment_agent = Agent(
    model='gpt-4',
    system_prompt="You can process payments and handle refunds.",
    toolsets=[
        PaymentToolset(payment_provider='stripe'),
        ORMToolset(allowed_models=['myapp.Order', 'myapp.Payment'])
    ]
)

result = payment_agent.run(
    "Process a $99.99 payment for order #12345 and update the order status"
)
```

### Toolset Best Practices

```python
class SecureAPIToolset(AbstractToolset[DjangoDeps]):
    """Example of secure toolset with proper validation"""
    
    def __init__(self, api_key: str, rate_limit: int = 100):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self._request_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        if self._request_count >= self.rate_limit:
            raise Exception(f"Rate limit exceeded: {self.rate_limit} requests")
        self._request_count += 1
        return True
    
    def _validate_permissions(self, ctx: RunContext[DjangoDeps]) -> bool:
        """Validate user permissions"""
        if not ctx.deps.user or not ctx.deps.user.is_authenticated:
            raise Exception("Authentication required")
        return True
    
    @tool
    def secure_api_call(
        self, 
        ctx: RunContext[DjangoDeps],
        endpoint: str, 
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make secure API call with validation"""
        # Validate permissions and rate limits
        self._validate_permissions(ctx)
        self._check_rate_limit()
        
        # Sanitize input
        if data:
            data = self._sanitize_data(data)
        
        # Make API call
        # ... implementation
        
        return {'status': 'success', 'data': 'response'}
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data"""
        # Remove dangerous keys, validate types, etc.
        sanitized = {}
        for key, value in data.items():
            if key not in ['__', 'eval', 'exec']:  # Basic sanitization
                sanitized[key] = value
        return sanitized
```

## 🧪 Testing Toolsets

### Unit Tests for Toolsets

```python
from django.test import TestCase
from django_cfg.apps.agents.toolsets import CacheToolset, ORMToolset
from django_cfg.apps.agents.core.dependencies import DjangoDeps

class ToolsetTest(TestCase):
    def setUp(self):
        self.cache_toolset = CacheToolset()
        self.orm_toolset = ORMToolset(allowed_models=['auth.User'])
        self.deps = DjangoDeps()
    
    def test_cache_operations(self):
        """Test cache toolset operations"""
        # Test cache set
        result = self.cache_toolset.cache_set('test_key', 'test_value', 300)
        self.assertTrue(result)
        
        # Test cache get
        value = self.cache_toolset.cache_get('test_key')
        self.assertEqual(value, 'test_value')
        
        # Test cache delete
        deleted = self.cache_toolset.cache_delete('test_key')
        self.assertTrue(deleted)
    
    def test_orm_operations(self):
        """Test ORM toolset operations"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create test user
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        created_user = self.orm_toolset.model_create('auth.User', user_data)
        self.assertIn('id', created_user)
        
        # Query user
        users = self.orm_toolset.model_query('auth.User', {'username': 'testuser'})
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'testuser')
```

## Related Documentation

- [**Agent Creation**](/ai-agents/creating-agents) - Creating custom agents
- [**Django Integration**](/ai-agents/django-integration) - Django-specific features
- [**Agent Examples**](/ai-agents/examples) - Practical examples
- [**Core Architecture**](/fundamentals/core/architecture) - System architecture

Agent toolsets provide powerful capabilities for AI agents to interact with your Django applications! 🛠️

TAGS: agents, toolsets, cache, orm, files, django, ai-tools
DEPENDS_ON: [agents, cache, database, files]
USED_BY: [ai-agents, automation, data-processing]
