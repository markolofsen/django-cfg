# 🚀 Django-CFG Unified Task Testing System

Unified testing system for all django-cfg background tasks including knowbase, payments, and future modules.

## 📋 Features

- **Unified Configuration**: Shared configuration across all task modules
- **Smart Worker Management**: Automatic worker startup/shutdown per queue
- **Comprehensive Testing**: End-to-end task processing verification
- **Flexible Execution**: Test individual modules or all together
- **Clean Environment**: Automatic cleanup of test data and workers
- **Detailed Logging**: Real-time logs and comprehensive reporting

## 🏗️ Architecture

```
test_tasks/
├── core/
│   └── shared.sh           # Shared configuration and utilities
├── modules/
│   ├── knowbase/
│   │   ├── config.sh       # Knowbase-specific configuration
│   │   └── test_knowbase.sh # Knowbase module test
│   └── payments/
│       ├── config.sh       # Payments-specific configuration
│       ├── test_payments.sh # Payments webhook test
│       └── test_usage_tracking.sh # Usage tracking test
├── runners/
│   ├── run_all.sh          # Main test runner (all modules)
│   ├── run_module.sh       # Single module runner
│   ├── quick_test.sh       # Quick test runner
│   └── simple_test.sh      # Simple test runner
├── docs/
│   ├── README.md           # This file
│   └── USAGE_TRACKING_TEST.md # Usage tracking documentation
```

## 🚀 Quick Start

### Test All Modules
```bash
./scripts/test_tasks/runners/run_all.sh
```

### Test Specific Module
```bash
./scripts/test_tasks/runners/run_module.sh knowbase
./scripts/test_tasks/runners/run_module.sh payments
./scripts/test_tasks/runners/run_module.sh payments usage  # Usage tracking test
```

### Quick Test (Reduced Timeouts)
```bash
./scripts/test_tasks/runners/run_all.sh --quick
./scripts/test_tasks/runners/run_module.sh --quick knowbase
```

### Cleanup Only
```bash
./scripts/test_tasks/runners/run_all.sh --cleanup
```

## 📊 What Gets Tested

### Knowbase Module (`knowbase` queue)
1. ✅ **Document Creation**: Creates test document via Django ORM
2. ✅ **Task Triggering**: Document creation triggers async processing 
3. ✅ **Worker Processing**: Dramatiq worker processes document in `knowbase` queue
4. ✅ **Chunking & Embeddings**: Document gets chunked and embeddings generated
5. ✅ **Status Verification**: Confirms document status changed to "completed"
6. ✅ **Data Validation**: Verifies chunks were created in database

### Payments Module (`payments` queue)
1. ✅ **Payment Creation**: Creates test payment via Django ORM
2. ✅ **Webhook Task**: Manually triggers webhook processing task
3. ✅ **Worker Processing**: Dramatiq worker processes webhook in `payments` queue  
4. ✅ **Event Recording**: Webhook processing creates PaymentEvent records
5. ✅ **Status Updates**: Payment status gets updated based on webhook
6. ✅ **Idempotency**: Confirms webhook idempotency keys work correctly

## ⚙️ Configuration

### Redis Configuration
```bash
REDIS_HOST="localhost"
REDIS_PORT="6379" 
REDIS_DB="2"              # Matches TaskConfig auto-initialization
```

### Worker Configuration
```bash
WORKER_PROCESSES="2"      # Number of worker processes
WORKER_THREADS="2"        # Number of threads per process
TEST_TIMEOUT="60"         # Test timeout in seconds
```

### Auto-Generated Queues
The system tests the queues that django-cfg automatically generates:

**Development Mode**: `["default", "knowbase", "payments"]`  
**Production Mode**: `["critical", "high", "default", "low", "background", "knowbase", "payments"]`

## 📝 Logs & Monitoring

### Log Files
- **Worker Logs**: `/tmp/django_cfg_tasks/{queue}_worker.log`
- **PID Files**: `/tmp/django_cfg_tasks/{queue}_worker.pid`

### Real-time Monitoring
```bash
# Monitor knowbase worker
tail -f /tmp/django_cfg_tasks/knowbase_worker.log

# Monitor payments worker  
tail -f /tmp/django_cfg_tasks/payments_worker.log
```

## 🔧 Environment Requirements

1. **Poetry**: For dependency management and virtual environment
2. **Redis**: Running on localhost:6379 (or configured host/port)
3. **Django**: Configured with django-cfg and enabled modules
4. **Database**: PostgreSQL or SQLite with proper migrations

### Validation
The system automatically validates:
- ✅ `manage.py` exists in project directory
- ✅ Poetry is installed and available
- ✅ Redis is running and accessible
- ✅ Django settings are properly configured

## 🎯 Usage Examples

### Basic Testing
```bash
# Test everything
./scripts/test_tasks/run_tests.sh

# Test only knowbase
./scripts/test_tasks/run_tests.sh knowbase

# Test only payments
./scripts/test_tasks/run_tests.sh payments
```

### Advanced Options
```bash
# Quick test with reduced timeouts
./scripts/test_tasks/run_tests.sh --quick all

# Verbose output for debugging
./scripts/test_tasks/run_tests.sh --verbose knowbase

# Clean up test data and workers
./scripts/test_tasks/run_tests.sh --cleanup
```

### Development Workflow
```bash
# 1. Start development
./scripts/test_tasks/run_tests.sh --cleanup  # Clean slate

# 2. Test specific feature  
./scripts/test_tasks/run_tests.sh knowbase   # Test document processing

# 3. Test integration
./scripts/test_tasks/run_tests.sh           # Test all modules

# 4. Quick validation
./scripts/test_tasks/run_tests.sh --quick   # Fast feedback
```

## 🐛 Troubleshooting

### Common Issues

#### Worker Won't Start
```bash
# Check Redis
redis-cli ping

# Check port conflicts
lsof -i :6379

# Check logs
tail -f /tmp/django_cfg_tasks/knowbase_worker.log
```

#### Tasks Not Processing
```bash
# Verify queue configuration
poetry run python manage.py shell -c "
from django_cfg.modules.django_tasks import get_task_service
service = get_task_service()
print('Queues:', service.config.dramatiq.queues)
"

# Check worker logs for errors
grep -i error /tmp/django_cfg_tasks/*.log
```

#### Database Issues
```bash
# Run migrations
poetry run python manage.py migrate

# Check database connection
poetry run python manage.py shell -c "
from django.db import connection
print('Database:', connection.settings_dict['NAME'])
"
```

### Debug Mode
Set environment variable for verbose debugging:
```bash
export DEBUG_TASKS=true
./scripts/test_tasks/run_tests.sh --verbose
```

## 🔄 Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Test Django-CFG Tasks
  run: |
    cd django_sample
    ./scripts/test_tasks/run_tests.sh --quick
```

### Docker Example
```dockerfile
RUN cd django_sample && ./scripts/test_tasks/run_tests.sh --quick
```

## 📈 Performance Metrics

The test system provides timing information:
- **Worker Startup Time**: ~2-3 seconds
- **Task Processing Time**: ~5-10 seconds per task
- **Full Test Suite**: ~30-60 seconds (depending on modules)
- **Quick Mode**: ~15-30 seconds

## 🔮 Future Enhancements

- [ ] **Agents Module**: Add testing for AI agent tasks
- [ ] **Performance Tests**: Load testing with multiple concurrent tasks  
- [ ] **Integration Tests**: Cross-module task dependencies
- [ ] **Metrics Collection**: Detailed performance and reliability metrics
- [ ] **Web Dashboard**: Real-time monitoring UI
- [ ] **Slack Integration**: Notifications for test results

## 📚 Related Documentation

- [Django-CFG Tasks Documentation](../../../src/django_cfg/apps/tasks/@docs/)
- [Knowbase Tasks](../../../src/django_cfg/apps/knowbase/@docs/tasks.md)
- [Payments Tasks](../../../src/django_cfg/apps/payments/@dev/TASK_INTEGRATION_GUIDE.md)
- [Legacy Test Systems](../test_dramatiq_old/) (for reference)

---

*Built with ❤️ for the Django-CFG ecosystem*
