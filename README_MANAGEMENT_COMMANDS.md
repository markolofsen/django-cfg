# Django Config Toolkit - Management Commands

This document describes the management commands available in Django Config Toolkit for enhanced Django project management.

## Available Commands

### 1. `migrator` - Smart Database Migration Tool

Interactive migration tool for multiple databases with ConfigToolkit integration.

```bash
# Interactive mode
python manage.py migrator

# Automatic mode
python manage.py migrator --auto

# Migrate specific database
python manage.py migrator --database cars_db

# Migrate specific app
python manage.py migrator --app data_cars
```

**Features:**
- 🔄 Full migration for all databases
- 📝 Create migrations only
- 🔍 Database status reporting
- ⚙️ ConfigToolkit integration
- 📊 Individual database migration
- 🎯 App-specific migration

### 2. `auto_generate` - Configuration File Generator

Generate configuration files, models, and Django components.

```bash
# Interactive mode
python manage.py auto_generate

# Generate all components
python manage.py auto_generate --all

# Generate configuration files only
python manage.py auto_generate --config

# Generate model files only
python manage.py auto_generate --models
```

**Generated Files:**
- `config.py` - Main configuration file
- `database_config.py` - Database configuration
- `security_config.py` - Security settings
- `models/base.py` - Base model classes
- `models/api.py` - API model classes
- `.env.template` - Environment template
- `settings_template.py` - Django settings template

### 3. `create_token` - Token Generation Tool

Generate API tokens, authentication tokens, and secret keys.

```bash
# Interactive mode
python manage.py create_token

# Create token for specific user
python manage.py create_token --user admin --type api --length 64

# Generate Django secret key
python manage.py create_token --type secret
```

**Token Types:**
- 🔑 API Tokens
- 🔐 Authentication Tokens
- 🔒 Secret Keys
- 👤 User-specific Tokens
- 📝 Django Secret Keys

### 4. `superuser` - Enhanced Superuser Creation

Create superusers with validation and configuration.

```bash
# Interactive mode
python manage.py superuser

# Non-interactive mode
python manage.py superuser --username admin --email admin@example.com --password secret123
```

**Features:**
- ✅ Email validation
- 🔒 Password strength checking
- 👤 User existence validation
- 💾 Credentials storage
- 📋 Next steps guidance

### 5. `test_email` - Email Configuration Testing

Test email configuration and send test emails.

```bash
# Interactive mode
python manage.py test_email

# Test configuration only
python manage.py test_email --config

# Send test email
python manage.py test_email --to user@example.com --subject "Test" --message "Hello"
```

**Features:**
- 🔧 Email configuration testing
- 📤 Test email sending
- 📋 Settings reporting
- 🔍 SMTP connection testing
- 📝 Email template generation

### 6. `script` - Script Management Tool

Run custom scripts and manage Django applications.

```bash
# Interactive mode
python manage.py script

# List available scripts
python manage.py script --list

# Create new script
python manage.py script --create my_script

# Run specific script
python manage.py script --script my_script

# Open Django shell
python manage.py script --shell
```

**Features:**
- 📋 Script listing
- ➕ Script creation
- ▶️ Script execution
- 🐚 Django shell access
- 🔍 System checks
- 🧹 Project cleaning
- 📊 Project information

### 7. `check_settings` - Settings Validation

Comprehensive validation of Django settings and configuration.

```bash
# Interactive mode
python manage.py check_settings

# Run all checks
python manage.py check_settings --all

# Check specific areas
python manage.py check_settings --security
python manage.py check_settings --database
python manage.py check_settings --email
python manage.py check_settings --cache
python manage.py check_settings --static

# Export report
python manage.py check_settings --export report.txt
```

**Validation Areas:**
- 🔒 Security Settings
- 🗄️ Database Configuration
- 📧 Email Settings
- 💾 Cache Configuration
- 📁 Static Files
- ⚙️ ConfigToolkit Integration

## Configuration Integration

All commands are designed to work seamlessly with ConfigToolkit:

### Database Management
- Automatic detection of multiple databases from `DATABASE_URL_*` environment variables
- Smart routing based on database names (e.g., `cars`, `analytics`, `cache`)
- Integration with ConfigToolkit's database configuration

### Environment Detection
- Automatic environment detection (development, production, docker)
- Environment-specific validation and warnings
- ConfigToolkit property access throughout commands

### Security Features
- Production-ready security checks
- SSL/TLS validation
- Secret key generation and validation
- CORS and CSRF configuration validation

## Usage Examples

### Setting up a new project:

```bash
# 1. Generate configuration files
python manage.py auto_generate --all

# 2. Create superuser
python manage.py superuser

# 3. Check settings
python manage.py check_settings --all

# 4. Run migrations
python manage.py migrator --auto
```

### Managing multiple databases:

```bash
# Check database status
python manage.py migrator

# Show ConfigToolkit info
python manage.py migrator  # Select "Show ConfigToolkit Info"

# Migrate specific database
python manage.py migrator --database cars_db
```

### Testing email configuration:

```bash
# Test email setup
python manage.py test_email --config

# Send test email
python manage.py test_email --to admin@example.com --subject "Test" --message "Hello"
```

## File Structure

Generated files are organized as follows:

```
project/
├── config.py                 # Main configuration
├── database_config.py        # Database settings
├── security_config.py        # Security settings
├── .env.template            # Environment template
├── settings_template.py     # Django settings template
├── models/
│   ├── base.py             # Base models
│   └── api.py              # API models
├── scripts/                 # Custom scripts
├── tokens/                  # Generated tokens
├── superusers/              # Superuser details
├── emails/                  # Email logs
└── reports/                 # Settings reports
```

## Dependencies

The management commands require the following dependencies:

```python
# In pyproject.toml or requirements.txt
questionary>=2.0.0  # For interactive menus
psutil>=5.0.0       # For system metrics (health checks)
```

## Contributing

To add new management commands:

1. Create a new command file in `django_cfg/management/commands/`
2. Inherit from `BaseCommand`
3. Use ConfigToolkit for configuration access
4. Add interactive menu support with questionary
5. Include comprehensive error handling
6. Add documentation to this README

## License

MIT License - see the main LICENSE file for details.
