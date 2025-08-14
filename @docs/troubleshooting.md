# 🐛 Troubleshooting Guide - Configuration Issues %%PRIORITY:HIGH%%

## 🎯 Quick Summary
Comprehensive troubleshooting guide for the isolated Django configuration system covering common issues, diagnostic tools, and step-by-step resolution procedures.

## 📋 Table of Contents
1. [Quick Diagnostic Tools](#quick-diagnostic-tools)
2. [Common Issues](#common-issues)
3. [Environment Problems](#environment-problems)
4. [Performance Issues](#performance-issues)
5. [Security Problems](#security-problems)
6. [Production Issues](#production-issues)

## 🔑 Key Concepts at a Glance
- **Fail-fast diagnosis**: Issues caught early with clear error messages
- **Self-diagnostic tools**: Built-in validation and health checks
- **Systematic approach**: Step-by-step resolution procedures
- **Recovery strategies**: Rollback and failover procedures
- **Prevention**: Best practices to avoid common issues

## 🚀 Quick Diagnostic Tools

### Configuration Health Check
```python
# Run comprehensive configuration health check
def config_health_check():
    """Quick configuration health check."""
    
    from api.config import ConfigToolkit
    import traceback
    
    print("🔍 Configuration Health Check")
    print("=" * 40)
    
    checks = [
        ("Import ConfigToolkit", lambda: __import__('api.config').config.ConfigToolkit),
        ("Access debug setting", lambda: ConfigToolkit.debug),
        ("Access secret key", lambda: len(ConfigToolkit.secret_key) >= 32),
        ("Access database URL", lambda: ConfigToolkit.database_url.startswith(('sqlite://', 'postgresql://', 'mysql://'))),
        ("Generate Django settings", lambda: len(ConfigToolkit.get_django_settings()) > 10),
        ("Validate configuration", lambda: ConfigToolkit.validate_all_configurations()),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if result:
                print(f"✅ {check_name}")
                passed += 1
            else:
                print(f"❌ {check_name}: Failed validation")
                failed += 1
        except Exception as e:
            print(f"❌ {check_name}: {e}")
            failed += 1
    
    print("=" * 40)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ Configuration is healthy")
        return True
    else:
        print("❌ Configuration has issues - see details above")
        return False

# Run health check
if __name__ == "__main__":
    config_health_check()
```

### Environment Debug Tool
```python
# Debug environment detection and variables
def debug_environment():
    """Debug environment detection and variables."""
    
    import os
    from pathlib import Path
    
    print("🌍 Environment Debug Information")
    print("=" * 40)
    
    # Environment detection
    print("Environment Detection:")
    print(f"  DJANGO_ENV: {os.getenv('DJANGO_ENV', 'not set')}")
    print(f"  DEBUG: {os.getenv('DEBUG', 'not set')}")
    print(f"  DOCKER: {os.getenv('DOCKER', 'not set')}")
    print(f"  /.dockerenv exists: {Path('/.dockerenv').exists()}")
    
    # ConfigToolkit detection results
    try:
        from api.config import ConfigToolkit
        print(f"\nConfigToolkit Results:")
        print(f"  Environment: {ConfigToolkit.environment}")
        print(f"  Is Production: {ConfigToolkit.is_production}")
        print(f"  Is Development: {ConfigToolkit.is_development}")
        print(f"  Is Docker: {ConfigToolkit.is_docker}")
    except Exception as e:
        print(f"\nConfigToolkit Error: {e}")
    
    # Environment files
    print(f"\nEnvironment Files:")
    env_files = ['.env', '.env.local', '.env.dev', '.env.prod', '.env.test']
    for env_file in env_files:
        path = Path(env_file)
        if path.exists():
            print(f"  ✅ {env_file}: {path.stat().st_size} bytes")
        else:
            print(f"  ❌ {env_file}: not found")
    
    # Critical environment variables
    print(f"\nCritical Environment Variables:")
    critical_vars = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS', 'CORS_ENABLED']
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'key' in var.lower() or 'password' in var.lower():
                masked_value = value[:5] + '***' + value[-3:] if len(value) > 8 else '***'
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: not set")

# Run environment debug
debug_environment()
```

### Performance Diagnostic
```python
# Diagnose configuration performance issues
def diagnose_performance():
    """Diagnose configuration performance issues."""
    
    import time
    import psutil
    import gc
    
    print("⚡ Configuration Performance Diagnosis")
    print("=" * 40)
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    # Test initialization performance
    print("1. Initialization Performance:")
    start_time = time.perf_counter()
    from api.config import ConfigToolkit
    _ = ConfigToolkit.debug  # Trigger initialization
    init_time = time.perf_counter() - start_time
    
    status = "✅" if init_time < 0.05 else "⚠️" if init_time < 0.1 else "❌"
    print(f"   {status} Initialization: {init_time*1000:.2f}ms (target: <50ms)")
    
    # Test memory usage
    current_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = current_memory - initial_memory
    status = "✅" if memory_increase < 10 else "⚠️" if memory_increase < 20 else "❌"
    print(f"   {status} Memory increase: {memory_increase:.2f}MB (target: <10MB)")
    
    # Test access performance
    print("\n2. Runtime Access Performance:")
    start_time = time.perf_counter()
    for _ in range(1000):
        _ = ConfigToolkit.debug
        _ = ConfigToolkit.database_url
        _ = ConfigToolkit.secret_key
    access_time = time.perf_counter() - start_time
    
    status = "✅" if access_time < 0.001 else "⚠️" if access_time < 0.01 else "❌"
    print(f"   {status} 1000 accesses: {access_time*1000:.2f}ms (target: <1ms)")
    
    # Test Django settings generation
    print("\n3. Django Settings Generation:")
    start_time = time.perf_counter()
    django_settings = ConfigToolkit.get_django_settings()
    generation_time = time.perf_counter() - start_time
    
    status = "✅" if generation_time < 0.02 else "⚠️" if generation_time < 0.05 else "❌"
    print(f"   {status} Settings generation: {generation_time*1000:.2f}ms (target: <20ms)")
    print(f"   📊 Generated {len(django_settings)} Django settings")
    
    # Memory cleanup test
    print("\n4. Memory Cleanup:")
    gc.collect()
    final_memory = process.memory_info().rss / 1024 / 1024
    total_increase = final_memory - initial_memory
    print(f"   📊 Total memory increase: {total_increase:.2f}MB")

# Run performance diagnosis
diagnose_performance()
```

## 🚨 Common Issues

### Issue 1: ConfigToolkit Import Error
**Symptoms**: `ImportError: cannot import name 'ConfigToolkit'`

**Diagnosis**:
```python
# Check if configuration module exists
import sys
from pathlib import Path

def diagnose_import_error():
    print("🔍 Diagnosing ConfigToolkit import error")
    
    # Check if api.config module exists
    api_config_path = Path('api/config')
    print(f"api/config directory exists: {api_config_path.exists()}")
    
    if api_config_path.exists():
        config_files = list(api_config_path.rglob('*.py'))
        print(f"Python files in api/config: {len(config_files)}")
        for file in config_files:
            print(f"  - {file}")
    
    # Check Python path
    print(f"Current working directory: {Path.cwd()}")
    print(f"Python path includes current directory: {'.' in sys.path or str(Path.cwd()) in sys.path}")
    
    # Try importing step by step
    try:
        import api
        print("✅ 'api' module imported successfully")
    except ImportError as e:
        print(f"❌ Cannot import 'api': {e}")
        return
    
    try:
        import api.config
        print("✅ 'api.config' module imported successfully")
    except ImportError as e:
        print(f"❌ Cannot import 'api.config': {e}")
        return
    
    try:
        from api.config import ConfigToolkit
        print("✅ ConfigToolkit imported successfully")
    except ImportError as e:
        print(f"❌ Cannot import ConfigToolkit: {e}")

diagnose_import_error()
```

**Solutions**:
1. **Check file structure**:
   ```bash
   # Ensure proper file structure
   ls -la api/config/
   # Should show __init__.py and other config files
   ```

2. **Check __init__.py**:
   ```python
   # api/config/__init__.py should contain:
   from .toolkit import ConfigToolkit
   
   __all__ = ['ConfigToolkit']
   ```

3. **Check Python path**:
   ```python
   # Add current directory to Python path if needed
   import sys
   sys.path.insert(0, '.')
   ```

### Issue 2: Environment Variable Not Found
**Symptoms**: Configuration using default values instead of environment variables

**Diagnosis**:
```python
def diagnose_env_vars():
    """Diagnose environment variable loading issues."""
    
    import os
    from pathlib import Path
    
    print("🔍 Environment Variable Diagnosis")
    
    # Check environment files
    env_files = ['.env', '.env.dev', '.env.prod', '.env.local']
    loaded_file = None
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"✅ Found {env_file}")
            with open(env_file) as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                print(f"   {len(lines)} non-comment lines")
                loaded_file = env_file
            break
    else:
        print("❌ No .env files found")
    
    # Check specific variables
    test_vars = ['DEBUG', 'SECRET_KEY', 'DATABASE_URL']
    print(f"\nEnvironment Variables:")
    
    for var in test_vars:
        env_value = os.getenv(var)
        if env_value:
            # Mask sensitive values
            if 'key' in var.lower() or 'secret' in var.lower():
                masked = env_value[:5] + '***' if len(env_value) > 5 else '***'
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {env_value}")
        else:
            print(f"  ❌ {var}: not set")
    
    # Check if env file variables are loaded
    if loaded_file:
        print(f"\nChecking {loaded_file} content:")
        with open(loaded_file) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    var_name = line.split('=')[0]
                    if var_name in test_vars:
                        env_loaded = os.getenv(var_name) is not None
                        status = "✅" if env_loaded else "❌"
                        print(f"  {status} Line {line_num}: {var_name} {'loaded' if env_loaded else 'not loaded'}")

diagnose_env_vars()
```

**Solutions**:
1. **Create missing .env file**:
   ```bash
   # Create .env.dev for development
   cat > .env.dev << EOF
   DEBUG=true
   SECRET_KEY=dev-secret-key-change-me
   DATABASE_URL=sqlite:///./dev.db
   EOF
   ```

2. **Check file permissions**:
   ```bash
   # Ensure .env file is readable
   chmod 644 .env.dev
   ```

3. **Manual environment variable loading**:
   ```python
   # Force load environment variables
   from pathlib import Path
   import os
   
   env_file = Path('.env.dev')
   if env_file.exists():
       with open(env_file) as f:
           for line in f:
               if '=' in line and not line.startswith('#'):
                   key, value = line.strip().split('=', 1)
                   os.environ[key] = value
   ```

### Issue 3: Pydantic Validation Error
**Symptoms**: `ValidationError` when accessing configuration

**Diagnosis**:
```python
def diagnose_validation_error():
    """Diagnose Pydantic validation errors."""
    
    import os
    
    print("🔍 Pydantic Validation Diagnosis")
    
    # Test individual configuration components
    components = [
        ('SECRET_KEY', 'string', 'min 32 characters'),
        ('DEBUG', 'boolean', 'true/false'),
        ('DATABASE_URL', 'string', 'valid URL format'),
        ('API_PAGE_SIZE', 'integer', '1-100'),
    ]
    
    for var_name, expected_type, requirements in components:
        value = os.getenv(var_name)
        print(f"\n{var_name}:")
        print(f"  Value: {value}")
        print(f"  Type: {type(value).__name__}")
        print(f"  Expected: {expected_type} ({requirements})")
        
        # Type-specific validation
        if var_name == 'SECRET_KEY':
            if value and len(value) >= 32:
                print("  ✅ Valid")
            else:
                print("  ❌ Too short or missing")
        
        elif var_name == 'DEBUG':
            if value and value.lower() in ['true', 'false', '1', '0']:
                print("  ✅ Valid")
            else:
                print("  ❌ Invalid boolean format")
        
        elif var_name == 'DATABASE_URL':
            if value and any(value.startswith(prefix) for prefix in ['sqlite://', 'postgresql://', 'mysql://']):
                print("  ✅ Valid")
            else:
                print("  ❌ Invalid URL format")
        
        elif var_name == 'API_PAGE_SIZE':
            try:
                if value:
                    size = int(value)
                    if 1 <= size <= 100:
                        print("  ✅ Valid")
                    else:
                        print("  ❌ Out of range (1-100)")
                else:
                    print("  ✅ Will use default")
            except ValueError:
                print("  ❌ Not a valid integer")

diagnose_validation_error()
```

**Solutions**:
1. **Fix validation errors**:
   ```bash
   # Fix common validation issues
   export SECRET_KEY="django-secret-key-with-at-least-32-characters"
   export DEBUG="true"
   export DATABASE_URL="sqlite:///./dev.db"
   export API_PAGE_SIZE="25"
   ```

2. **Check Pydantic version**:
   ```bash
   # Ensure compatible Pydantic version
   pip install "pydantic>=2.0,<3.0"
   ```

3. **Debug specific validation**:
   ```python
   # Test specific field validation
   from pydantic import ValidationError
   
   try:
       from api.config import ConfigToolkit
       debug_value = ConfigToolkit.debug
   except ValidationError as e:
       print("Validation errors:")
       for error in e.errors():
           print(f"  Field: {error['loc']}")
           print(f"  Error: {error['msg']}")
           print(f"  Input: {error['input']}")
   ```

## 🌍 Environment Problems

### Environment Detection Issues
**Symptoms**: Wrong environment detected (prod vs dev)

**Diagnosis**:
```python
def diagnose_environment_detection():
    """Diagnose environment detection issues."""
    
    import os
    from pathlib import Path
    
    print("🌍 Environment Detection Diagnosis")
    print("=" * 40)
    
    # Check environment indicators
    indicators = [
        ('DJANGO_ENV', os.getenv('DJANGO_ENV')),
        ('DEBUG', os.getenv('DEBUG')),
        ('DOCKER', os.getenv('DOCKER')),
        ('/.dockerenv exists', Path('/.dockerenv').exists()),
        ('HEROKU_APP_NAME', os.getenv('HEROKU_APP_NAME')),
        ('AWS_LAMBDA_FUNCTION_NAME', os.getenv('AWS_LAMBDA_FUNCTION_NAME')),
    ]
    
    print("Environment Indicators:")
    for name, value in indicators:
        print(f"  {name}: {value}")
    
    # Show detection logic result
    try:
        from api.config import ConfigToolkit
        print(f"\nDetection Results:")
        print(f"  Environment: {ConfigToolkit.environment}")
        print(f"  Is Production: {ConfigToolkit.is_production}")
        print(f"  Is Development: {ConfigToolkit.is_development}")
        print(f"  Is Docker: {ConfigToolkit.is_docker}")
    except Exception as e:
        print(f"\nDetection Error: {e}")
    
    # Show which .env file should be used
    expected_env_files = {
        'production': '.env.prod',
        'development': '.env.dev',
        'testing': '.env.test',
        'docker': '.env or .env.prod'
    }
    
    try:
        expected_file = expected_env_files.get(ConfigToolkit.environment, '.env')
        print(f"\nExpected env file: {expected_file}")
        if Path(expected_file.split(' or ')[0]).exists():
            print(f"✅ {expected_file.split(' or ')[0]} exists")
        else:
            print(f"❌ {expected_file.split(' or ')[0]} missing")
    except:
        pass

diagnose_environment_detection()
```

**Solutions**:
1. **Force environment**:
   ```bash
   # Explicitly set environment
   export DJANGO_ENV=development
   # or
   export DJANGO_ENV=production
   ```

2. **Fix Docker detection**:
   ```bash
   # For Docker environments
   export DOCKER=true
   ```

3. **Create correct env file**:
   ```bash
   # Ensure correct env file exists
   cp .env.example .env.dev  # for development
   cp .env.example .env.prod # for production
   ```

### Path Resolution Issues
**Symptoms**: FileNotFoundError for media, static, or log files

**Diagnosis**:
```python
def diagnose_path_issues():
    """Diagnose path resolution issues."""
    
    from pathlib import Path
    
    print("📁 Path Resolution Diagnosis")
    print("=" * 40)
    
    try:
        from api.config import ConfigToolkit
        
        paths = [
            ('base_dir', ConfigToolkit.base_dir),
            ('media_dir', ConfigToolkit.media_dir),
            ('static_dir', ConfigToolkit.static_dir),
            ('logs_dir', ConfigToolkit.logs_dir),
        ]
        
        for name, path in paths:
            print(f"\n{name}:")
            print(f"  Path: {path}")
            print(f"  Absolute: {path.resolve()}")
            print(f"  Exists: {path.exists()}")
            print(f"  Is directory: {path.is_dir() if path.exists() else 'N/A'}")
            print(f"  Writable: {os.access(path.parent, os.W_OK) if path.parent.exists() else 'N/A'}")
            
            # Try to create directory if it doesn't exist
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ Created directory")
                except Exception as e:
                    print(f"  ❌ Cannot create: {e}")
    
    except Exception as e:
        print(f"❌ Path diagnosis failed: {e}")

import os
diagnose_path_issues()
```

**Solutions**:
1. **Create missing directories**:
   ```bash
   # Create required directories
   mkdir -p logs media staticfiles
   chmod 755 logs media staticfiles
   ```

2. **Fix permissions**:
   ```bash
   # Fix directory permissions
   chmod -R 755 logs media staticfiles
   chown -R $USER:$USER logs media staticfiles
   ```

3. **Use absolute paths in production**:
   ```bash
   # Set absolute paths for production
   export MEDIA_DIR=/app/media
   export STATIC_DIR=/app/staticfiles
   export LOGS_DIR=/app/logs
   ```

## ⚡ Performance Issues

### Slow Configuration Loading
**Symptoms**: Application startup >100ms

**Diagnosis & Solutions**:
```python
def diagnose_slow_loading():
    """Diagnose and fix slow configuration loading."""
    
    import time
    import cProfile
    import pstats
    from io import StringIO
    
    print("⚡ Slow Loading Diagnosis")
    print("=" * 40)
    
    # Profile configuration loading
    pr = cProfile.Profile()
    pr.enable()
    
    start_time = time.perf_counter()
    from api.config import ConfigToolkit
    _ = ConfigToolkit.debug  # Trigger initialization
    total_time = time.perf_counter() - start_time
    
    pr.disable()
    
    print(f"Total loading time: {total_time*1000:.2f}ms")
    
    if total_time > 0.1:  # >100ms
        print("❌ Loading is too slow")
        
        # Show profiling results
        s = StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(10)  # Top 10 slowest functions
        
        print("\nTop slow functions:")
        print(s.getvalue())
        
        # Common solutions
        print("\n🔧 Potential Solutions:")
        print("1. Reduce number of environment variables")
        print("2. Optimize .env file size")
        print("3. Use lazy loading for non-critical configs")
        print("4. Cache configuration validation results")
    else:
        print("✅ Loading time is acceptable")

diagnose_slow_loading()
```

### High Memory Usage
**Symptoms**: Configuration using >10MB memory

**Diagnosis & Solutions**:
```python
def diagnose_memory_usage():
    """Diagnose high memory usage."""
    
    import gc
    import psutil
    import tracemalloc
    
    print("💾 Memory Usage Diagnosis")
    print("=" * 40)
    
    # Start memory tracking
    tracemalloc.start()
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    # Load configuration
    from api.config import ConfigToolkit
    django_settings = ConfigToolkit.get_django_settings()
    
    # Measure memory usage
    gc.collect()
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    print(f"Memory increase: {memory_increase:.2f}MB")
    
    if memory_increase > 10:  # >10MB
        print("❌ Memory usage is too high")
        
        # Get memory snapshot
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        print("\nTop memory allocations:")
        for stat in top_stats[:5]:
            print(f"  {stat.size / 1024 / 1024:.2f}MB: {stat}")
        
        # Solutions
        print("\n🔧 Potential Solutions:")
        print("1. Use __slots__ in configuration classes")
        print("2. Avoid caching large strings")
        print("3. Use weak references for caches")
        print("4. Lazy load non-critical configurations")
    else:
        print("✅ Memory usage is acceptable")

diagnose_memory_usage()
```

## 🔐 Security Problems

### Insecure Production Configuration
**Symptoms**: Security warnings in production

**Diagnosis & Solutions**:
```python
def diagnose_security_issues():
    """Diagnose production security issues."""
    
    print("🔐 Security Issues Diagnosis")
    print("=" * 40)
    
    try:
        from api.config import ConfigToolkit
        
        if not ConfigToolkit.is_production:
            print("ℹ️ Not in production mode - security checks skipped")
            return
        
        # Security checks
        issues = []
        
        # Check DEBUG setting
        if ConfigToolkit.debug:
            issues.append("DEBUG=True in production")
        
        # Check SECRET_KEY
        if len(ConfigToolkit.secret_key) < 32:
            issues.append("SECRET_KEY too short")
        if ConfigToolkit.secret_key.startswith('django-insecure'):
            issues.append("Using default insecure SECRET_KEY")
        
        # Check HTTPS settings
        if not ConfigToolkit.ssl_enabled:
            issues.append("SSL not enabled")
        
        # Check CORS settings
        if ConfigToolkit.cors_enabled and ConfigToolkit.cors_allow_all_origins:
            issues.append("CORS allows all origins")
        
        # Check allowed hosts
        if not ConfigToolkit.allowed_hosts or '*' in ConfigToolkit.allowed_hosts:
            issues.append("ALLOWED_HOSTS not properly configured")
        
        # Check database SSL
        if not ConfigToolkit.database_ssl_required:
            issues.append("Database SSL not required")
        
        # Check API security
        if not ConfigToolkit.api_rate_limit_enabled:
            issues.append("API rate limiting disabled")
        if ConfigToolkit.api_docs_enabled:
            issues.append("API documentation enabled in production")
        
        # Report issues
        if issues:
            print("❌ Security issues found:")
            for issue in issues:
                print(f"  - {issue}")
            
            print("\n🔧 Solutions:")
            print("1. Set DEBUG=false")
            print("2. Generate strong SECRET_KEY (50+ characters)")
            print("3. Enable SSL_ENABLED=true")
            print("4. Configure specific CORS_ALLOWED_ORIGINS")
            print("5. Set specific ALLOWED_HOSTS")
            print("6. Enable DATABASE_SSL_REQUIRED=true")
            print("7. Enable API_RATE_LIMIT_ENABLED=true")
            print("8. Set API_DOCS_ENABLED=false")
        else:
            print("✅ No security issues found")
    
    except Exception as e:
        print(f"❌ Security diagnosis failed: {e}")

diagnose_security_issues()
```

## 🚀 Production Issues

### Database Connection Problems
**Symptoms**: Database connection errors in production

**Diagnosis & Solutions**:
```python
def diagnose_database_issues():
    """Diagnose database connection issues."""
    
    print("🗄️ Database Issues Diagnosis")
    print("=" * 40)
    
    try:
        from api.config import ConfigToolkit
        from django.db import connection
        import time
        
        print(f"Database URL: {ConfigToolkit.database_url[:20]}...")
        print(f"SSL required: {ConfigToolkit.database_ssl_required}")
        print(f"Max connections: {ConfigToolkit.database_max_connections}")
        
        # Test basic connection
        print("\n1. Testing basic connection:")
        try:
            start_time = time.perf_counter()
            connection.ensure_connection()
            connect_time = time.perf_counter() - start_time
            print(f"✅ Connected in {connect_time*1000:.2f}ms")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return
        
        # Test query execution
        print("\n2. Testing query execution:")
        try:
            start_time = time.perf_counter()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            query_time = time.perf_counter() - start_time
            print(f"✅ Query executed in {query_time*1000:.2f}ms")
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        # Test connection pooling
        print("\n3. Testing connection info:")
        print(f"Connection queries: {len(connection.queries)}")
        print(f"Connection vendor: {connection.vendor}")
        
        # Connection health recommendations
        print("\n🔧 Recommendations:")
        if connect_time > 0.1:
            print("- Connection time >100ms - check network latency")
        if query_time > 0.05:
            print("- Query time >50ms - check database performance")
        print("- Monitor connection pool usage")
        print("- Enable connection health checks")
        
    except Exception as e:
        print(f"❌ Database diagnosis failed: {e}")

diagnose_database_issues()
```

### Cache Connection Problems
**Symptoms**: Cache errors or timeouts

**Diagnosis & Solutions**:
```python
def diagnose_cache_issues():
    """Diagnose cache connection issues."""
    
    print("🗃️ Cache Issues Diagnosis")
    print("=" * 40)
    
    try:
        from api.config import ConfigToolkit
        from django.core.cache import cache
        import time
        
        print(f"Cache backend: {ConfigToolkit.cache_backend}")
        if ConfigToolkit.cache_backend == 'redis':
            print(f"Redis URL: {ConfigToolkit.cache_redis_url[:20]}...")
        
        # Test cache operations
        print("\n1. Testing cache set/get:")
        try:
            start_time = time.perf_counter()
            cache.set('test_key', 'test_value', 10)
            set_time = time.perf_counter() - start_time
            
            start_time = time.perf_counter()
            value = cache.get('test_key')
            get_time = time.perf_counter() - start_time
            
            if value == 'test_value':
                print(f"✅ Cache working - set: {set_time*1000:.2f}ms, get: {get_time*1000:.2f}ms")
            else:
                print(f"❌ Cache returned wrong value: {value}")
        except Exception as e:
            print(f"❌ Cache operation failed: {e}")
        
        # Test cache deletion
        print("\n2. Testing cache deletion:")
        try:
            cache.delete('test_key')
            value = cache.get('test_key')
            if value is None:
                print("✅ Cache deletion works")
            else:
                print(f"❌ Key not deleted: {value}")
        except Exception as e:
            print(f"❌ Cache deletion failed: {e}")
        
        # Redis-specific tests
        if ConfigToolkit.cache_backend == 'redis':
            print("\n3. Testing Redis connection:")
            try:
                import redis
                r = redis.from_url(ConfigToolkit.cache_redis_url)
                info = r.info()
                print(f"✅ Redis connected - version: {info['redis_version']}")
                print(f"   Connected clients: {info['connected_clients']}")
                print(f"   Used memory: {info['used_memory_human']}")
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
        
        print("\n🔧 Recommendations:")
        if set_time > 0.01 or get_time > 0.01:
            print("- Cache operations >10ms - check Redis performance")
        print("- Monitor cache hit/miss ratios")
        print("- Set appropriate cache timeouts")
        
    except Exception as e:
        print(f"❌ Cache diagnosis failed: {e}")

diagnose_cache_issues()
```

## 🛠️ Recovery Procedures

### Configuration Reset
```python
def reset_configuration():
    """Reset configuration to safe defaults."""
    
    import os
    from pathlib import Path
    
    print("🔄 Resetting Configuration")
    print("=" * 40)
    
    # Create safe .env file
    safe_env_content = """# Safe default configuration
DEBUG=true
SECRET_KEY=django-insecure-safe-default-key-change-me-in-production
DATABASE_URL=sqlite:///./dev.db
CORS_ENABLED=true
CSRF_ENABLED=true
SSL_ENABLED=false
API_RATE_LIMIT_ENABLED=false
API_DOCS_ENABLED=true
CACHE_BACKEND=memory
EMAIL_BACKEND=console
LOG_LEVEL=DEBUG
"""
    
    # Backup existing .env if it exists
    env_file = Path('.env')
    if env_file.exists():
        backup_file = Path('.env.backup')
        env_file.rename(backup_file)
        print(f"✅ Backed up existing .env to .env.backup")
    
    # Write safe configuration
    env_file.write_text(safe_env_content)
    print(f"✅ Created safe .env file")
    
    # Clear environment variables
    config_vars = [
        'DEBUG', 'SECRET_KEY', 'DATABASE_URL', 'CORS_ENABLED',
        'API_RATE_LIMIT_ENABLED', 'SSL_ENABLED'
    ]
    
    for var in config_vars:
        if var in os.environ:
            del os.environ[var]
    
    print("✅ Cleared environment variables")
    
    # Test new configuration
    try:
        # Force reload configuration
        if 'api.config' in sys.modules:
            del sys.modules['api.config']
        
        from api.config import ConfigToolkit
        debug = ConfigToolkit.debug
        print(f"✅ Configuration reset successful - DEBUG: {debug}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

# Run configuration reset
import sys
reset_configuration()
```

## 🏷️ Metadata
**Tags**: `troubleshooting, diagnosis, debugging, recovery, configuration`  
**Added in**: `v4.0`  
**Performance**: `%%PERFORMANCE:HIGH%%` - Fast diagnostic tools  
**Security**: `%%SECURITY:HIGH%%` - Security issue detection  
**Complexity**: `%%COMPLEXITY:MODERATE%%` - Systematic troubleshooting  
%%AI_HINT: This is a comprehensive troubleshooting guide with diagnostic tools and solutions%%

## ✅ Quality Gates
- [ ] All diagnostic tools provide clear results
- [ ] Common issues have step-by-step solutions
- [ ] Recovery procedures are tested and work
- [ ] Security issues are detected and fixable
- [ ] Performance problems have optimization guides

**Remember**: When in doubt, run the configuration health check first. Most issues can be diagnosed and resolved using the built-in diagnostic tools!
