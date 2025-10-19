---
title: Maintenance Commands
description: Django-CFG CLI maintenance commands. Command-line interface for maintenance commands with examples, options, and production workflows.
sidebar_label: Maintenance
sidebar_position: 5
keywords:
  - django-cfg maintenance
  - django-cfg command maintenance
  - cli maintenance
---

# Maintenance Mode Commands

Commands for managing maintenance mode and Cloudflare integration.

## Maintenance Mode

### `maintenance`

Manage maintenance mode for your application.

```bash
python manage.py maintenance [ACTION] [OPTIONS]
```

**Actions:**
- `enable` - Enable maintenance mode
- `disable` - Disable maintenance mode
- `status` - Show maintenance status

**Options:**
- `--cloudflare` - Sync with Cloudflare

**Examples:**

```bash
# Enable maintenance mode
python manage.py maintenance enable

# Enable with Cloudflare sync
python manage.py maintenance enable --cloudflare

# Disable maintenance mode
python manage.py maintenance disable

# Disable with Cloudflare sync
python manage.py maintenance disable --cloudflare

# Check status
python manage.py maintenance status
```

---

## Cloudflare Integration

### `sync_cloudflare`

Sync maintenance mode with Cloudflare.

```bash
python manage.py sync_cloudflare [OPTIONS]
```

**Options:**
- `--enable` - Enable Cloudflare maintenance
- `--disable` - Disable Cloudflare maintenance

**Examples:**

```bash
# Enable Cloudflare maintenance page
python manage.py sync_cloudflare --enable

# Disable Cloudflare maintenance page
python manage.py sync_cloudflare --disable
```

**What it does:**
- Updates Cloudflare page rules
- Activates maintenance page
- Preserves admin access
- Logs all changes

---

## Scheduled Maintenance

### `process_scheduled_maintenance`

Process scheduled maintenance windows automatically.

```bash
python manage.py process_scheduled_maintenance
```

**Features:**
- Checks scheduled maintenance windows
- Automatically enables/disables maintenance
- Sends notifications
- Logs all actions

**Cron Setup:**

```bash
# Check every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py process_scheduled_maintenance

# Check every minute for precise timing
* * * * * cd /path/to/project && python manage.py process_scheduled_maintenance
```

---

## Common Workflows

### Manual Maintenance

```bash
# 1. Enable maintenance
python manage.py maintenance enable --cloudflare

# 2. Perform updates
python manage.py migrate_all
python manage.py collectstatic --noinput

# 3. Disable maintenance
python manage.py maintenance disable --cloudflare
```

### Scheduled Maintenance

```bash
# Schedule maintenance in Django admin
# Then let cron handle it automatically
```

### Emergency Maintenance

```bash
# Quick enable
python manage.py maintenance enable --cloudflare

# Check status
python manage.py maintenance status
```

---

## Configuration

### Django Configuration

```python
# config.py
class MyConfig(DjangoConfig):
    # Enable maintenance app
    enable_maintenance: bool = True

    # Cloudflare configuration
    cloudflare_api_key: str = env.cloudflare.api_key
    cloudflare_zone_id: str = env.cloudflare.zone_id
```

### Environment Variables

```yaml
# config.dev.yaml
cloudflare:
  api_key: "your_cloudflare_api_key"
  zone_id: "your_zone_id"
  email: "your@email.com"
```

---

## Best Practices

### 1. Always Use Cloudflare Sync

```bash
# ✅ GOOD - Syncs with Cloudflare
python manage.py maintenance enable --cloudflare

# ⚠️ LIMITED - Only Django, no CDN
python manage.py maintenance enable
```

### 2. Test Maintenance Page First

```bash
# Enable, test, then disable
python manage.py maintenance enable
# Test page appearance
python manage.py maintenance disable
```

### 3. Schedule During Low Traffic

```bash
# Schedule for 2 AM - 4 AM
# Add to Django admin maintenance schedule
```

### 4. Monitor Scheduled Tasks

```bash
# Check cron logs
tail -f /var/log/syslog | grep maintenance
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[Maintenance App Guide](/features/built-in-apps/operations/maintenance)** - Complete documentation

---

**Maintenance mode without downtime stress!** 🔧
