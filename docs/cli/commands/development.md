---
title: Development Commands
description: Django-CFG CLI development commands. Command-line interface for development commands with examples, options, and production workflows.
sidebar_label: Development
sidebar_position: 8
keywords:
  - django-cfg development
  - django-cfg command development
  - cli development
---

# Development Commands

Commands for development, testing, and debugging Django-CFG projects.

## Development Server

### `runserver_ngrok`

Run development server with ngrok tunnel for webhook testing.

```bash
python manage.py runserver_ngrok [OPTIONS]
```

**Options:**
- `--domain TEXT` - Custom ngrok domain
- `--no-ngrok` - Disable ngrok for this session
- `[address:port]` - Custom address and port

**Examples:**

```bash
# Start server with ngrok tunnel
python manage.py runserver_ngrok

# Use custom ngrok domain
python manage.py runserver_ngrok --domain myapp

# Custom port
python manage.py runserver_ngrok 0.0.0.0:8080

# Disable ngrok for this session
python manage.py runserver_ngrok --no-ngrok
```

**Features:**
- ✅ Automatic ngrok tunnel creation
- ✅ Public URL for webhooks
- ✅ ALLOWED_HOSTS auto-configuration
- ✅ Tunnel status monitoring

**Output:**
```
✅ Ngrok tunnel ready: https://abc123.ngrok.io
Django development server is running at http://127.0.0.1:8000/
Public URL: https://abc123.ngrok.io
```

---

## Testing Commands

### `test_email`

Test email configuration and send test messages.

```bash
python manage.py test_email [OPTIONS]
```

**Options:**
- `--to TEXT` - Recipient email address
- `--subject TEXT` - Email subject (default: "Django-CFG Test Email")
- `--backend TEXT` - Email backend to test

**Examples:**

```bash
# Test email to specific address
python manage.py test_email --to admin@example.com

# Custom subject
python manage.py test_email --to test@test.com --subject "Configuration Test"

# Test specific backend
python manage.py test_email --to admin@test.com --backend sendgrid
```

---

### `test_telegram`

Test Telegram bot configuration.

```bash
python manage.py test_telegram [OPTIONS]
```

**Options:**
- `--message TEXT` - Test message to send
- `--chat-id TEXT` - Target chat ID (optional)

**Examples:**

```bash
# Send test message
python manage.py test_telegram --message "Hello from Django-CFG!"

# Send to specific chat
python manage.py test_telegram --message "Test" --chat-id "-1001234567890"
```

---

### `test_twilio`

Test Twilio SMS and WhatsApp messaging.

```bash
python manage.py test_twilio [OPTIONS]
```

**Options:**
- `--to TEXT` - Phone number to send test message to
- `--message TEXT` - Message to send
- `--whatsapp` - Send WhatsApp message (default: SMS)
- `--content-sid TEXT` - Content template SID for WhatsApp

**Examples:**

```bash
# Test SMS
python manage.py test_twilio --to "+1234567890" --message "Test SMS"

# Test WhatsApp
python manage.py test_twilio --to "+1234567890" --message "Test WhatsApp" --whatsapp

# Test WhatsApp template
python manage.py test_twilio --to "+1234567890" --whatsapp --content-sid "HXxxxxx"
```

---

### `test_otp`

Test OTP authentication system.

```bash
python manage.py test_otp [OPTIONS]
```

**Options:**
- `--email TEXT` - Email address to test
- `--phone TEXT` - Phone number to test (for SMS OTP)

**Examples:**

```bash
# Test email OTP
python manage.py test_otp --email user@example.com

# Test SMS OTP
python manage.py test_otp --phone "+1234567890"
```

---

## Script Execution

### `script`

Run custom scripts with full Django context.

```bash
python manage.py script SCRIPT_PATH [SCRIPT_ARGS]
```

**Arguments:**
- `SCRIPT_PATH` - Path to Python script
- `SCRIPT_ARGS` - Arguments to pass to script

**Examples:**

```bash
# Run Python script with Django context
python manage.py script my_script.py

# Pass arguments to script
python manage.py script data_import.py --file data.csv

# Run with specific settings
python manage.py script --settings myproject.settings.dev cleanup.py
```

**Script Example:**

```python
# my_script.py
import sys
from myapp.models import User

def main():
    print(f"Total users: {User.objects.count()}")

    if len(sys.argv) > 1:
        username = sys.argv[1]
        user = User.objects.get(username=username)
        print(f"Found user: {user.email}")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python manage.py script my_script.py admin
```

---

## Project Structure

### `tree`

Display Django project structure with documentation.

```bash
python manage.py tree [OPTIONS]
```

**Options:**
- `--depth INTEGER` - Limit depth
- `--include-docs` - Include documentation files
- `--python-only` - Show only Python files

**Examples:**

```bash
# Show project structure
python manage.py tree

# Limit depth
python manage.py tree --depth 3

# Include documentation files
python manage.py tree --include-docs

# Show only Python files
python manage.py tree --python-only
```

**Output:**
```
📁 myproject/
├── 📄 manage.py
├── 📁 myproject/
│   ├── 📄 __init__.py
│   ├── 📄 config.py
│   ├── 📄 settings.py
│   ├── 📄 urls.py
│   └── 📄 wsgi.py
├── 📁 apps/
│   ├── 📁 blog/
│   ├── 📁 shop/
│   └── 📁 profiles/
└── 📁 static/
```

---

## Code Generation

### `generate`

Generate Django components (models, views, serializers).

```bash
python manage.py generate TYPE NAME [FIELDS]
```

**Types:**
- `model` - Generate model
- `crud` - Generate complete CRUD
- `api` - Generate API views

**Examples:**

```bash
# Generate model
python manage.py generate model Product name:str price:decimal

# Generate complete CRUD
python manage.py generate crud Product

# Generate API views
python manage.py generate api Product --viewset
```

---

## Development Workflows

### Complete Development Setup

```bash
# 1. Create project
django-cfg create-project "My Project"
cd my_project

# 2. Validate configuration
python manage.py validate_config

# 3. Setup database
python manage.py migrate_all

# 4. Create superuser
python manage.py createsuperuser

# 5. Start development server with ngrok
python manage.py runserver_ngrok
```

---

### Webhook Development Workflow

```bash
# 1. Start server with ngrok
python manage.py runserver_ngrok

# Output: Public URL: https://abc123.ngrok.io

# 2. Configure webhook in external service
# Use: https://abc123.ngrok.io/api/webhooks/stripe/

# 3. Monitor webhook events
# Check Django admin: /admin/payments/webhook/

# 4. Test webhook
curl -X POST https://abc123.ngrok.io/api/webhooks/stripe/ \
  -H "Content-Type: application/json" \
  -d '{"event": "test"}'
```

---

### Testing Workflow

```bash
# 1. Test email configuration
python manage.py test_email --to admin@test.com

# 2. Test Telegram bot
python manage.py test_telegram --message "Deploy test"

# 3. Test SMS/WhatsApp
python manage.py test_twilio --to "+1234567890"

# 4. Test OTP system
python manage.py test_otp --email user@test.com

# 5. Run unit tests
python manage.py test
```

---

### Script Development Workflow

```bash
# 1. Create script
cat > scripts/import_users.py << EOF
from myapp.models import User
import csv

def main():
    with open('users.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            User.objects.create(
                username=row['username'],
                email=row['email']
            )
    print("Import complete!")

if __name__ == "__main__":
    main()
EOF

# 2. Run script
python manage.py script scripts/import_users.py

# 3. Check results
python manage.py shell -c "from myapp.models import User; print(User.objects.count())"
```

---

## Best Practices

### 1. Use Ngrok for Webhook Development

```bash
# ✅ GOOD - Ngrok for webhooks
python manage.py runserver_ngrok

# ❌ LIMITED - Local only
python manage.py runserver
```

### 2. Test All Integrations Before Deploy

```bash
# Comprehensive testing
python manage.py test_email --to admin@test.com
python manage.py test_telegram --message "Test"
python manage.py test_twilio --to "+1234567890"
python manage.py test_otp --email user@test.com
python manage.py test_providers
```

### 3. Use Scripts for Data Operations

```bash
# ✅ GOOD - Reusable script
python manage.py script import_data.py

# ❌ BAD - One-off shell commands
python manage.py shell -c "complex_command_here"
```

### 4. Generate Code for Consistency

```bash
# ✅ GOOD - Generated code follows patterns
python manage.py generate model Product name:str price:decimal

# ❌ BAD - Manual coding with inconsistencies
```

### 5. Monitor Project Structure

```bash
# Regular structure checks
python manage.py tree --depth 3
```

---

## Troubleshooting

### Ngrok Not Starting

```bash
# Check ngrok installation
which ngrok

# Install ngrok
# macOS
brew install ngrok

# Ubuntu
sudo snap install ngrok

# Check ngrok config
python manage.py show_config --section ngrok
```

### Email Test Failing

```bash
# Check email configuration
python manage.py check_settings --email-test

# Verify SMTP settings
python manage.py show_config --section email
```

### Script Execution Errors

```bash
# Run with verbose output
python manage.py script my_script.py --verbosity 2

# Check Django context
python manage.py shell -c "import django; print(django.__version__)"
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[Ngrok Integration](/features/integrations/ngrok/overview)** - Webhook testing
- **[Core Commands](./core-commands)** - Project setup

---

**Development made productive!** 🛠️
