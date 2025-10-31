---
title: Cron Scheduling System
description: Type-safe cron job scheduling with django-crontab integration for automated task execution
sidebar_label: Overview & Philosophy
sidebar_position: 1
tags:
  - scheduling
  - cron
  - django-crontab
  - automation
  - background-jobs
keywords:
  - django-cfg cron
  - django crontab
  - scheduled tasks
  - cron jobs
---

# Cron Scheduling System

> **📚 Part of**: [Modules](/features/modules/overview) - Explore all django-cfg modules

Type-safe cron job scheduling with declarative configuration, automatic crontab management, and production-ready features for django-cfg projects.

---

## Quick Navigation

### For Developers
- [Quick Start](#quick-start) - Get started in 5 minutes
- [Configuration](#configuration) - Declarative cron setup
- [Job Types](#job-types) - Commands and callables
- [Examples](#examples) - Practical code examples

### For DevOps
- [Installation](#installation) - System crontab setup
- [Management](#management) - Update and monitor jobs
- [Production](#production-best-practices) - Production deployment
- [Timezone Awareness](#7-timezone-awareness) - Critical timezone configuration
- [Troubleshooting](#troubleshooting) - Common issues

---

## Philosophy

### "Type-Safe Configuration"
Define cron jobs with Pydantic models, not string manipulation:

```python
from django_cfg import CrontabConfig, CrontabJobConfig

crontab = CrontabConfig(
    enabled=True,
    lock_jobs=True,  # Prevent concurrent execution
    jobs=[
        CrontabJobConfig(
            name="sync_balances",
            command="sync_account_balances",
            minute="*/5",
            hour="*",
        ),
    ],
)
```

### "Declarative Over Imperative"
Jobs defined in `config.py` automatically sync to system crontab:

- ✅ **No Manual Editing** - No need to manually edit crontab files
- ✅ **Version Controlled** - Jobs tracked in source control
- ✅ **Environment Aware** - Different schedules per environment
- ✅ **Type Validated** - Catch errors before deployment

### "Production-Ready Features"
Built for enterprise applications:

- ✅ **Lock Files** - Prevent overlapping job execution
- ✅ **Error Handling** - Configurable retry and error modes
- ✅ **Environment Prefixes** - Set DJANGO_SETTINGS_MODULE automatically
- ✅ **Job Management** - Enable/disable jobs without code changes
- ✅ **Monitoring** - Track execution via Django logs

---

## Key Features

### Django Integration
- **Management Commands** - Schedule any Django command
- **Python Callables** - Schedule any Python function
- **Settings Integration** - Automatic settings module injection
- **ORM Access** - Full Django ORM available in jobs

### Schedule Control
- **Cron Syntax** - Full cron expression support
- **Flexible Timing** - Minutes, hours, days, weeks, months
- **Validation** - Schedule validation at configuration time
- **Common Patterns** - Pre-defined schedules for common use cases

### Reliability
- **Lock Mechanism** - Distributed lock files prevent concurrent runs
- **Error Modes** - Configure retry, ignore, or fail behavior
- **Logging** - Comprehensive execution logging
- **Monitoring** - Track job execution in system logs

### Management
- **CLI Commands** - Add, remove, show jobs via `manage.py`
- **Live Updates** - Update schedules without downtime
- **Job Control** - Enable/disable individual jobs
- **Dry Run** - Test jobs before scheduling

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| CrontabConfig Model | ✅ Complete | Type-safe Pydantic configuration |
| CrontabJobConfig Model | ✅ Complete | Individual job configuration |
| Settings Generator | ✅ Complete | Auto-generate CRONJOBS settings |
| Apps Integration | ✅ Complete | Auto-add django_crontab to INSTALLED_APPS |
| Schedule Validation | ✅ Complete | Cron syntax validation |
| Lock Files | ✅ Complete | Prevent concurrent execution |
| Management Commands | ✅ Complete | Via django-crontab CLI |
| Documentation | ✅ Complete | Full docs with examples |

---

## Quick Start

### 1. Configuration

Add cron configuration to your django-cfg settings:

```python title="config.py"
from django_cfg import DjangoConfig, CrontabConfig, CrontabJobConfig

class Config(DjangoConfig):
    project_name = "My Project"

    # Enable cron scheduling
    crontab = CrontabConfig(
        enabled=True,
        command_prefix='DJANGO_SETTINGS_MODULE=myproject.settings',
        lock_jobs=True,
        comment="My Project automated tasks",
        jobs=[
            # Sync data every 5 minutes
            CrontabJobConfig(
                name="sync_data_frequent",
                job_type="command",
                command="sync_data",
                command_args=["--ignore-errors"],
                command_kwargs={"verbosity": 0},
                minute="*/5",
                hour="*",
                comment="Frequent data sync (quiet mode)",
            ),
            # Daily cleanup at 2 AM
            CrontabJobConfig(
                name="cleanup_daily",
                job_type="command",
                command="cleanup_old_data",
                minute="0",
                hour="2",
                comment="Daily cleanup at 2 AM",
            ),
        ],
    )

config = Config()
```

### 2. Install Jobs

Add jobs to system crontab:

```bash
# Activate virtual environment
source .venv/bin/activate

# Add jobs to crontab
python manage.py crontab add

# Verify installation
python manage.py crontab show
```

### 3. Verify

Check system crontab:

```bash
# View crontab entries
crontab -l

# Expected output:
# BEGIN My Project automated tasks
# */5 * * * * DJANGO_SETTINGS_MODULE=myproject.settings /path/.venv/bin/python /path/manage.py crontab run abc123
# 0 2 * * * DJANGO_SETTINGS_MODULE=myproject.settings /path/.venv/bin/python /path/manage.py crontab run xyz789
# END My Project automated tasks
```

---

## Configuration

### Minimal Configuration

```python
from django_cfg import CrontabConfig, CrontabJobConfig

crontab = CrontabConfig(
    enabled=True,
    jobs=[
        CrontabJobConfig(
            name="my_job",
            command="my_command",
            minute="0",
            hour="*",
        ),
    ],
)
```

### Complete Configuration

```python
crontab = CrontabConfig(
    # Enable/disable all jobs
    enabled=True,

    # Environment prefix (injected before every command)
    command_prefix='DJANGO_SETTINGS_MODULE=myproject.settings',

    # Environment suffix (appended after every command)
    command_suffix='',

    # Use lock files to prevent concurrent execution
    lock_jobs=True,

    # Comment added to crontab file
    comment="My Project automated tasks",

    # Job definitions
    jobs=[
        CrontabJobConfig(
            # Job identification
            name="unique_job_name",
            enabled=True,
            comment="Optional job description",

            # Job type: "command" or "callable"
            job_type="command",

            # For management commands
            command="my_management_command",
            command_args=["--flag", "value"],
            command_kwargs={"verbosity": 1},

            # Schedule (cron format)
            minute="*/5",        # 0-59, *, */N, comma-separated
            hour="*",            # 0-23, *, */N, comma-separated
            day_of_week="*",     # 0-6 (Sun=0), *, */N
            day_of_month="*",    # 1-31, *, */N
            month_of_year="*",   # 1-12, *, */N
        ),
    ],
)
```

### Schedule Patterns

```python
# Every 5 minutes
CrontabJobConfig(name="every_5min", command="task", minute="*/5", hour="*")

# Every hour at :30
CrontabJobConfig(name="hourly", command="task", minute="30", hour="*")

# Every 2 hours
CrontabJobConfig(name="every_2h", command="task", minute="0", hour="*/2")

# Daily at 2:00 AM
CrontabJobConfig(name="daily", command="task", minute="0", hour="2")

# Weekdays at 9:00 AM
CrontabJobConfig(name="weekdays", command="task", minute="0", hour="9", day_of_week="1-5")

# First day of month at 3:00 AM
CrontabJobConfig(name="monthly", command="task", minute="0", hour="3", day_of_month="1")

# Multiple times (at :00, :15, :30, :45)
CrontabJobConfig(name="4times", command="task", minute="0,15,30,45", hour="*")
```

---

## Job Types

### Management Commands

Schedule Django management commands:

```python
CrontabJobConfig(
    name="sync_data",
    job_type="command",
    command="sync_data",              # Command name
    command_args=["--force"],          # Positional arguments
    command_kwargs={"verbosity": 1},   # Keyword arguments
    minute="*/10",
    hour="*",
)
```

**Generated Django call:**
```python
django.core.management.call_command('sync_data', '--force', verbosity=1)
```

### Python Callables

Schedule any Python function:

```python
CrontabJobConfig(
    name="cleanup_task",
    job_type="callable",
    callable_path="myapp.tasks.cleanup_old_files",
    callable_args=[],
    callable_kwargs={"days": 7},
    minute="0",
    hour="3",
)
```

**Function signature:**
```python
# myapp/tasks.py
def cleanup_old_files(days: int = 7):
    """Clean up files older than N days."""
    # Your implementation
    pass
```

---

## Examples

### Real-World Use Cases

#### Data Synchronization

```python
jobs=[
    # Frequent quiet sync every 5 minutes
    CrontabJobConfig(
        name="sync_balances_frequent",
        command="sync_account_balances",
        command_args=["--ignore-errors"],
        command_kwargs={"verbosity": 0},
        minute="*/5",
        comment="Sync balances (quiet)",
    ),

    # Verbose hourly sync for monitoring
    CrontabJobConfig(
        name="sync_balances_verbose",
        command="sync_account_balances",
        command_args=["--verbose"],
        command_kwargs={"verbosity": 1},
        minute="0",
        hour="*",
        comment="Sync balances (verbose for logs)",
    ),
]
```

#### Daily Reports

```python
CrontabJobConfig(
    name="generate_daily_report",
    command="generate_report",
    command_args=["--type=daily", "--email-admins"],
    minute="0",
    hour="9",
    day_of_week="1-5",  # Weekdays only
    comment="Daily report at 9 AM (weekdays)",
)
```

#### Database Maintenance

```python
jobs=[
    # Clean old sessions daily at 2 AM
    CrontabJobConfig(
        name="cleanup_sessions",
        command="clearsessions",
        minute="0",
        hour="2",
        comment="Django session cleanup",
    ),

    # Database vacuum weekly (Sunday 3 AM)
    CrontabJobConfig(
        name="vacuum_db",
        job_type="callable",
        callable_path="myapp.maintenance.vacuum_database",
        minute="0",
        hour="3",
        day_of_week="0",
        comment="Weekly database vacuum",
    ),
]
```

#### Cache Warming

```python
CrontabJobConfig(
    name="warm_cache",
    command="warm_cache",
    command_args=["--endpoints=/api/popular/,/api/trending/"],
    minute="*/15",
    hour="8-22",  # Only during business hours
    comment="Warm cache every 15min (8 AM - 10 PM)",
)
```

---

## Installation

### Adding Jobs

```bash
# Show what will be added (dry run)
python manage.py crontab show

# Add jobs to system crontab
python manage.py crontab add

# Verify installation
crontab -l | grep "My Project"
```

### Updating Jobs

After changing `config.py`:

```bash
# Remove old jobs
python manage.py crontab remove

# Add updated jobs
python manage.py crontab add

# Or combine:
python manage.py crontab remove && python manage.py crontab add
```

### Removing Jobs

```bash
# Remove all django-cfg jobs
python manage.py crontab remove

# Verify removal
crontab -l
```

---

## Management

### Viewing Jobs

```bash
# Show active jobs via Django
python manage.py crontab show

# Output:
# Currently active jobs in crontab:
# abc123 -> ('*/5 * * * *', 'django.core.management.call_command',
#            ['sync_data'], {'verbosity': 0})
```

### Testing Jobs

```bash
# Run job manually by hash
python manage.py crontab run abc123

# Run command directly for testing
python manage.py sync_data --dry-run
python manage.py sync_data --verbose
```

### Enabling/Disabling Jobs

```python
# In config.py - disable individual job
CrontabJobConfig(
    name="my_job",
    enabled=False,  # Job won't be added to crontab
    # ...
)

# Or disable all jobs
crontab = CrontabConfig(
    enabled=False,  # All jobs disabled
    jobs=[...],
)
```

After changing:

```bash
python manage.py crontab remove
python manage.py crontab add
```

---

## Production Best Practices

### 1. Use Lock Files

Prevent overlapping job execution:

```python
crontab = CrontabConfig(
    lock_jobs=True,  # Creates lock files in /tmp/
    jobs=[...],
)
```

**Lock file behavior:**
- Created before job starts
- Deleted after job completes
- Prevents duplicate execution
- Located in `/tmp/[project]_[job_hash].lock`

### 2. Configure Error Handling

```python
# Ignore errors and continue
CrontabJobConfig(
    command="sync_data",
    command_args=["--ignore-errors"],
    command_kwargs={"verbosity": 0},  # Quiet mode
)

# Verbose mode for monitoring
CrontabJobConfig(
    command="sync_data",
    command_kwargs={"verbosity": 1},  # Log everything
)
```

### 3. Dual-Mode Scheduling

Run jobs frequently (quiet) and less frequently (verbose):

```python
jobs=[
    # Every 5 minutes - quiet
    CrontabJobConfig(
        name="sync_quiet",
        command="sync_data",
        command_args=["--ignore-errors"],
        command_kwargs={"verbosity": 0},
        minute="*/5",
    ),

    # Every hour - verbose (for monitoring)
    CrontabJobConfig(
        name="sync_verbose",
        command="sync_data",
        command_kwargs={"verbosity": 1},
        minute="0",
        hour="*",
    ),
]
```

### 4. Stagger Job Execution

Avoid resource contention:

```python
jobs=[
    CrontabJobConfig(name="job1", minute="0", hour="*"),   # :00
    CrontabJobConfig(name="job2", minute="15", hour="*"),  # :15
    CrontabJobConfig(name="job3", minute="30", hour="*"),  # :30
    CrontabJobConfig(name="job4", minute="45", hour="*"),  # :45
]
```

### 5. Environment Configuration

Set environment variables:

```python
crontab = CrontabConfig(
    command_prefix='DJANGO_SETTINGS_MODULE=myproject.settings LOG_LEVEL=info',
    jobs=[...],
)
```

### 6. Logging Configuration

Configure Django logging for cron jobs:

```python
# In Django settings
LOGGING = {
    'handlers': {
        'cron_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cron.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.core.management': {
            'handlers': ['cron_file'],
            'level': 'INFO',
        },
    },
}
```

### 7. Timezone Awareness

**Critical:** System cron executes jobs in the **server's timezone**, not Django's `TIME_ZONE` setting.

#### Check Server Timezone

```bash
# View current timezone
date
timedatectl  # On systemd systems

# Expected output:
# Time zone: UTC (UTC, +0000)
```

#### Configure Server Timezone

```bash
# Set timezone to UTC (recommended for servers)
sudo timedatectl set-timezone UTC

# Or set to specific timezone
sudo timedatectl set-timezone America/New_York

# Verify
date
```

#### Django vs System Time

```python
# Django settings (affects application logic)
TIME_ZONE = 'America/New_York'  # Django's timezone
USE_TZ = True                    # Enable timezone support

# ⚠️ Important: Cron jobs run in SERVER timezone, not Django's TIME_ZONE
```

#### Best Practices

**1. Use UTC on servers (recommended):**
```bash
# Server timezone = UTC
sudo timedatectl set-timezone UTC
```

```python
# Django settings
TIME_ZONE = 'UTC'
USE_TZ = True

# Cron jobs
CrontabJobConfig(
    name="daily_report",
    command="generate_report",
    minute="0",
    hour="9",  # 9:00 UTC
)
```

**2. Or explicitly handle timezone differences:**
```python
# If server is UTC, but you want jobs at EST times:
# 9 AM EST = 2 PM UTC (EST is UTC-5, or UTC-4 during DST)
CrontabJobConfig(
    name="daily_report_est",
    command="generate_report",
    minute="0",
    hour="14",  # 2 PM UTC = 9 AM EST (standard time)
    comment="Daily report at 9 AM EST (14:00 UTC)",
)
```

**3. Document timezone in job comments:**
```python
CrontabJobConfig(
    name="sync_markets",
    command="sync_exchange_markets",
    minute="0",
    hour="2",
    comment="Daily sync at 2 AM UTC (9 PM EST previous day)",
)
```

#### Common Timezone Pitfall

```python
# ❌ WRONG: Assuming cron uses Django's TIME_ZONE
# Django settings: TIME_ZONE = 'America/New_York'
CrontabJobConfig(
    hour="9",  # You expect 9 AM EST
)
# But if server is UTC, this runs at 9 AM UTC = 4 AM EST!

# ✅ CORRECT: Calculate based on server timezone
CrontabJobConfig(
    hour="14",  # 9 AM EST = 14:00 UTC
    comment="9 AM EST (14:00 UTC)",
)
```

#### Verify Job Execution Times

```bash
# After installing cron jobs, verify they run at expected times
crontab -l

# Monitor first execution
tail -f /var/log/syslog | grep CRON
tail -f logs/cron.log

# Check what time job actually ran
python manage.py shell
>>> from django.utils import timezone
>>> timezone.now()  # Current time in Django's timezone
```

---

## Troubleshooting

### Jobs Not Running

**Check crontab installation:**

```bash
# Verify jobs are in crontab
crontab -l | grep "My Project"

# Check system cron logs
tail -f /var/log/syslog | grep CRON  # Ubuntu/Debian
tail -f /var/log/cron                # CentOS/RHEL
```

**Verify paths:**

```bash
# Check Python path
which python
.venv/bin/python --version

# Check manage.py path
ls -la manage.py
```

### Jobs Stuck/Long Running

**Check lock files:**

```bash
# Find lock files
find /tmp -name "*myproject*.lock" -type f

# Remove stale locks (older than 1 hour)
find /tmp -name "*myproject*.lock" -type f -mmin +60 -delete
```

### Permission Errors

```bash
# Check crontab access
crontab -l

# Check log directory permissions
ls -la logs/
chmod 755 logs

# Check manage.py permissions
chmod +x manage.py
```

### Database Connection Errors

```bash
# Test database connection
python manage.py dbshell

# Check DATABASE_URL
cat .env | grep DATABASE_URL

# Verify settings
python manage.py check
```

### Command Not Found

**Ensure command exists:**

```bash
# List all commands
python manage.py help

# Test command manually
python manage.py [command_name] --help
```

### Jobs Running at Wrong Time

**Timezone mismatch:**

```bash
# Check server timezone
date
timedatectl

# Check if it matches your expectations
# Cron runs in SERVER timezone, NOT Django's TIME_ZONE
```

**Solution:**

```python
# If server is UTC but you want EST times:
# Calculate hour offset: 9 AM EST = 14:00 UTC (EST is UTC-5)
CrontabJobConfig(
    name="morning_job",
    hour="14",  # 9 AM EST in UTC
    comment="Runs at 9 AM EST (14:00 UTC)",
)
```

**Quick check:**
```bash
# After job should have run, check logs
tail -f /var/log/syslog | grep CRON
tail -f logs/cron.log

# Verify time in Django shell
python manage.py shell
>>> from django.utils import timezone
>>> timezone.now()
```

See [Timezone Awareness](#7-timezone-awareness) for detailed configuration.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          django_cfg.models.crontab                     │ │
│  │                                                         │ │
│  │  ├─ CrontabConfig (main configuration)                │ │
│  │  ├─ CrontabJobConfig (individual jobs)                │ │
│  │  ├─ Schedule validation                               │ │
│  │  └─ Django settings generation                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     django_cfg.core.generation.crontab                 │ │
│  │                                                         │ │
│  │  ├─ CrontabSettingsGenerator                          │ │
│  │  └─ CRONJOBS settings generation                      │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │     Django Settings (settings.py)    │
         │                                       │
         │  • CRONJOBS = [(schedule, cmd), ...] │
         │  • CRONTAB_COMMAND_PREFIX            │
         │  • CRONTAB_LOCK_JOBS                 │
         │  • CRONTAB_COMMENT                   │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │       django-crontab package         │
         │                                       │
         │  manage.py crontab add/remove/show   │
         └──────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │      System Crontab (/var/cron)      │
         │                                       │
         │  */5 * * * * /path/python ...        │
         │  0 2 * * * /path/python ...          │
         └──────────────────────────────────────┘
```

### Execution Flow

1. **Configuration**: Define jobs in `config.py` using `CrontabConfig`
2. **Generation**: django-cfg generates `CRONJOBS` in Django settings
3. **Registration**: django-crontab added to `INSTALLED_APPS` automatically
4. **Installation**: Run `manage.py crontab add` to install to system crontab
5. **Execution**: System cron executes jobs at scheduled times
6. **Monitoring**: View execution logs in Django logs and syslog

---

## Cron Syntax Reference

### Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6) (Sunday=0)
│ │ │ │ │
* * * * *
```

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `*/N` | Every N units | `*/5 * * * *` = every 5 minutes |
| `,` | List of values | `0,30 * * * *` = at :00 and :30 |
| `-` | Range of values | `9-17 * * * *` = 9 AM to 5 PM |

### Common Schedules

```python
"* * * * *"      # Every minute
"*/5 * * * *"    # Every 5 minutes
"0 * * * *"      # Every hour
"0 */2 * * *"    # Every 2 hours
"0 0 * * *"      # Daily at midnight
"0 2 * * *"      # Daily at 2 AM
"0 9 * * 1-5"    # Weekdays at 9 AM
"0 0 * * 0"      # Sundays at midnight
"0 0 1 * *"      # First day of month
"0 0 1 1 *"      # January 1st (yearly)
```

---

## See Also

### Core Documentation
- **[Getting Started](/getting-started/intro)** - Set up django-cfg with cron
- **[Configuration Guide](/fundamentals/configuration)** - Configure your project
- **[Type Safety](/fundamentals/core/type-safety)** - Pydantic configuration

### Related Features
- **[ReArq Integration](/features/integrations/rearq/overview)** - Async task queue (alternative to cron)
- **[Modules Overview](/features/modules/overview)** - All available modules
- **[Email Module](/features/modules/email/overview)** - Send emails from cron jobs
- **[Telegram Module](/features/modules/telegram/overview)** - Telegram notifications

### External Documentation
- **[django-crontab](https://github.com/kraiz/django-crontab)** - Underlying crontab package
- **[Crontab Guru](https://crontab.guru/)** - Interactive cron schedule editor

---

**Status**: Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-31
