---
title: CLI Commands Reference
sidebar_position: 4
keywords:
  - django client cli
  - generate_client command
  - validate_openapi command
  - django api validation
  - openapi client generation
description: Complete reference for Django Client CLI commands - generate API clients, validate OpenAPI schemas, and auto-fix serializer issues.
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# CLI Commands Reference

The `django_client` module provides powerful management commands for generating API clients and validating OpenAPI schema quality.

## Commands Overview

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `generate_client` | Generate TypeScript and Python clients | Multi-group generation, dry-run, interactive mode |
| `validate_openapi` | Validate and fix OpenAPI schema quality | Auto-fix issues, detailed reports, rule-based validation |

---

## `generate_client`

Generate type-safe TypeScript and Python API clients from your Django REST Framework API.

### Basic Usage

```bash
# Generate all configured groups
python manage.py generate_client

# Generate specific groups
python manage.py generate_client --groups core billing

# Generate Python only
python manage.py generate_client --python

# Generate TypeScript only
python manage.py generate_client --typescript
```

### Command Options

#### Generation Options

**`--groups [GROUP ...]`**
- Generate specific groups only
- Default: all configured groups
```bash
python manage.py generate_client --groups core custom
```

**`--python`**
- Generate Python client only (skip TypeScript)
```bash
python manage.py generate_client --python
```

**`--typescript`**
- Generate TypeScript client only (skip Python)
```bash
python manage.py generate_client --typescript
```

**`--no-python`**
- Skip Python client generation
```bash
python manage.py generate_client --no-python
```

**`--no-typescript`**
- Skip TypeScript client generation
```bash
python manage.py generate_client --no-typescript
```

#### Utility Options

**`--dry-run`**
- Validate configuration without generating files
- Shows what will be generated
```bash
python manage.py generate_client --dry-run
```

**`--list-groups`**
- List all configured groups and exit
- Shows group details and matched apps
```bash
python manage.py generate_client --list-groups
```

**`--validate`**
- Validate configuration and show statistics
```bash
python manage.py generate_client --validate
```

**`--interactive` / `-i`**
- Run in interactive mode with prompts
- Requires `click` package
```bash
python manage.py generate_client --interactive
```

### Examples

<Tabs>
  <TabItem value="basic" label="Basic Generation" default>

Generate all configured groups:

```bash
python manage.py generate_client
```

**Output:**
```
Generating clients for 2 group(s):

  • core (Core API)
  • billing (Billing API)

Languages:
  → Python
  → TypeScript

============================================================

📦 Processing group: core
  Apps: users, accounts, profiles
  → Generating OpenAPI schema...
  ✅ Schema saved: openapi/schemas/core.json
  → Parsing to IR...
  ✅ Parsed: 15 schemas, 42 operations
  → Generating Python client...
  ✅ Python client: openapi/clients/python/core (38 files)
  → Generating TypeScript client...
  ✅ TypeScript client: openapi/clients/typescript/core (52 files)
  → Archiving...
  ✅ Archived: openapi/archive/core_2025-01-15_14-30-00.zip

📦 Processing group: billing
  Apps: payments, subscriptions
  → Generating OpenAPI schema...
  ✅ Schema saved: openapi/schemas/billing.json
  → Parsing to IR...
  ✅ Parsed: 8 schemas, 24 operations
  → Generating Python client...
  ✅ Python client: openapi/clients/python/billing (22 files)
  → Generating TypeScript client...
  ✅ TypeScript client: openapi/clients/typescript/billing (31 files)
  → Archiving...
  ✅ Archived: openapi/archive/billing_2025-01-15_14-30-15.zip

============================================================

✅ Successfully generated clients for 2 group(s)!

Output directory: /path/to/project/openapi
  Python:     openapi/clients/python
  TypeScript: openapi/clients/typescript
```

  </TabItem>
  <TabItem value="specific-groups" label="Specific Groups">

Generate only specific groups:

```bash
python manage.py generate_client --groups core custom
```

This is useful when you only changed specific apps, want faster generation during development, or need to regenerate a failed group.

  </TabItem>
  <TabItem value="python-only" label="Python Only">

Generate Python clients only:

```bash
python manage.py generate_client --python
```

Perfect for backend microservices, Python-to-Python API communication, and testing Python client in isolation.

  </TabItem>
  <TabItem value="typescript-only" label="TypeScript Only">

Generate TypeScript clients only:

```bash
python manage.py generate_client --typescript
```

Perfect for frontend development, React/Next.js projects, and React Native apps.

  </TabItem>
  <TabItem value="dry-run" label="Dry Run">

Preview what will be generated:

```bash
python manage.py generate_client --dry-run
```

**Output:**
```
🔍 DRY RUN MODE - No files will be generated

Generating clients for 2 group(s):

  • core (Core API)
  • billing (Billing API)

Languages:
  → Python
  → TypeScript

✅ Dry run completed - no files generated
```

Useful for verifying group configuration, checking which apps are matched, and CI/CD validation.

  </TabItem>
  <TabItem value="list-groups" label="List Groups">

Show all configured groups:

```bash
python manage.py generate_client --list-groups
```

**Output:**
```
Configured groups (3):

  • core
    Title: Core API
    Apps: 2 pattern(s)
    Matched: 5 app(s)
      - users
      - accounts
      - profiles
      - auth
      - sessions

  • billing
    Title: Billing API
    Apps: 2 pattern(s)
    Matched: 3 app(s)
      - payments
      - subscriptions
      - invoices

  • content
    Title: Content API
    Apps: 1 pattern(s)
    Matched: 0 apps
```

  </TabItem>
  <TabItem value="validate" label="Validate Config">

Validate configuration and show statistics:

```bash
python manage.py generate_client --validate
```

**Output:**
```
Validating configuration...
✅ Configuration is valid!

Statistics:
  • Total groups: 3
  • Total apps in groups: 8
  • Ungrouped apps: 4

Warning: 4 apps not in any group:
  - admin
  - contenttypes
  - sessions
  - messages
```

  </TabItem>
</Tabs>

### Workflow Integration

#### Pre-Deployment Script

```bash
#!/bin/bash
# scripts/generate_clients.sh

set -e

echo "🚀 Generating API clients..."
python manage.py generate_client

echo "✅ Validating TypeScript..."
cd frontend && pnpm tsc --noEmit

echo "✅ Validating Python..."
cd ../backend && mypy api_client/

echo "🎉 Clients generated and validated!"
```

#### GitHub Actions

```yaml
name: Generate API Clients

on:
  push:
    paths:
      - 'api/**'
      - '**/serializers.py'
      - '**/views.py'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate clients
        run: python manage.py generate_client

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add openapi/
          git commit -m "chore: update API clients [skip ci]" || true
          git push
```

#### Docker Build

```dockerfile
FROM python:3.12

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Generate clients during build
RUN python manage.py generate_client

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## `validate_openapi`

Validate and auto-fix OpenAPI schema quality issues in Django REST Framework serializers.

### Why Validation Matters

Poor OpenAPI schema quality causes:
- ❌ Missing type hints → `Any` types in generated clients
- ❌ Missing help text → No documentation in generated code
- ❌ Ambiguous field types → Runtime errors
- ❌ Missing `read_only` → Write attempts on read-only fields

The validator finds and fixes these issues automatically.

### Basic Usage

```bash
# Check all serializers
python manage.py validate_openapi

# Check specific app
python manage.py validate_openapi --app users

# Auto-fix issues
python manage.py validate_openapi --fix

# Preview fixes without applying
python manage.py validate_openapi --fix --dry-run

# Generate HTML report
python manage.py validate_openapi --report html
```

### Command Options

#### Scope Options

**`--app APP_NAME`**
- Check specific Django app only
```bash
python manage.py validate_openapi --app accounts
```

**`--file PATH`**
- Check specific file only
```bash
python manage.py validate_openapi --file users/serializers.py
```

**`--pattern PATTERN`**
- File pattern to match (default: `*serializers.py`)
```bash
python manage.py validate_openapi --pattern "*api.py"
```

#### Action Options

**`--fix`**
- Apply auto-fixes to issues
```bash
python manage.py validate_openapi --fix
```

**`--dry-run`**
- Preview fixes without applying changes
```bash
python manage.py validate_openapi --fix --dry-run
```

**`--no-confirm`**
- Skip confirmation prompts when fixing
```bash
python manage.py validate_openapi --fix --no-confirm
```

#### Reporting Options

**`--report {console,json,html}`**
- Report format (default: console)
```bash
python manage.py validate_openapi --report html
```

**`--output PATH`**
- Output file for JSON/HTML reports
```bash
python manage.py validate_openapi --report html --output report.html
```

**`--summary`**
- Show summary only (compact output)
```bash
python manage.py validate_openapi --summary
```

#### Filtering Options

**`--severity {error,warning,info}`**
- Filter by minimum severity level
```bash
python manage.py validate_openapi --severity error
```

**`--rule RULE_ID`**
- Check specific rule only
```bash
python manage.py validate_openapi --rule type-hint-001
```

**`--fixable-only`**
- Show only auto-fixable issues
```bash
python manage.py validate_openapi --fixable-only
```

#### Utility Options

**`--list-rules`**
- List all validation rules and exit
```bash
python manage.py validate_openapi --list-rules
```

**`--verbose`**
- Show detailed output
```bash
python manage.py validate_openapi --verbose
```

### Validation Rules

Common validation rules include:

| Rule ID | Name | Severity | Auto-Fixable |
|---------|------|----------|--------------|
| `type-hint-001` | Missing type hints | Error | Yes |
| `help-text-001` | Missing help_text | Warning | No |
| `read-only-001` | Missing read_only | Warning | Yes |
| `default-001` | Missing default values | Info | No |
| `max-length-001` | Missing max_length | Warning | Yes |

View all rules:
```bash
python manage.py validate_openapi --list-rules
```

### Examples

<Tabs>
  <TabItem value="basic-check" label="Basic Check" default>

Check all serializers:

```bash
python manage.py validate_openapi
```

**Output:**
```
🔍 Scanning for issues...

Found 12 issues in 5 files:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
users/serializers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Line 15: UserSerializer.email
  ❌ ERROR [type-hint-001] Missing type hint
    → Add type hint: email: str = serializers.EmailField(...)
    ✅ Auto-fixable

  Line 18: UserSerializer.bio
  ⚠️  WARNING [help-text-001] Missing help_text
    → Add: help_text="User biography"

  Line 22: UserSerializer.created_at
  ⚠️  WARNING [read-only-001] Missing read_only=True
    → Add: read_only=True
    ✅ Auto-fixable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
accounts/serializers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Line 30: AccountSerializer.balance
  ❌ ERROR [type-hint-001] Missing type hint
    → Add type hint: balance: Decimal = serializers.DecimalField(...)
    ✅ Auto-fixable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  • Total issues: 12
  • Errors: 5
  • Warnings: 6
  • Info: 1
  • Auto-fixable: 8

💡 Tip: Run with --fix to auto-fix 8 issue(s)
```

  </TabItem>
  <TabItem value="auto-fix" label="Auto-Fix">

Auto-fix issues:

```bash
python manage.py validate_openapi --fix
```

**Output:**
```
🔍 Scanning for issues...

Found 12 issues (8 fixable)

🔧 Applying fixes...

✅ Fixed: users/serializers.py:15 [type-hint-001]
✅ Fixed: users/serializers.py:22 [read-only-001]
✅ Fixed: accounts/serializers.py:30 [type-hint-001]
✅ Fixed: payments/serializers.py:45 [max-length-001]
... (4 more)

✅ Successfully fixed 8 issue(s)!

Remaining issues: 4 (manual fix required)
```

  </TabItem>
  <TabItem value="dry-run" label="Dry Run">

Preview fixes without applying:

```bash
python manage.py validate_openapi --fix --dry-run
```

Shows what would be fixed without modifying files.

  </TabItem>
  <TabItem value="specific-app" label="Specific App">

Check specific app:

```bash
python manage.py validate_openapi --app users
```

Only scans serializers in the `users` app.

  </TabItem>
  <TabItem value="html-report" label="HTML Report">

Generate HTML report:

```bash
python manage.py validate_openapi --report html --output validation_report.html
```

Creates an interactive HTML report with sortable/filterable issue table, statistics and charts, code snippets with syntax highlighting, and fix suggestions.

  </TabItem>
  <TabItem value="errors-only" label="Errors Only">

Show only errors:

```bash
python manage.py validate_openapi --severity error
```

Filters out warnings and info messages.

  </TabItem>
  <TabItem value="summary" label="Summary">

Show compact summary:

```bash
python manage.py validate_openapi --summary
```

**Output:**
```
Summary:
  • Total files checked: 15
  • Files with issues: 5
  • Total issues: 12
  • Errors: 5 (4 fixable)
  • Warnings: 6 (3 fixable)
  • Info: 1 (1 fixable)
```

  </TabItem>
</Tabs>

### Workflow Integration

#### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Validating OpenAPI schemas..."

# Check only staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "serializers.py$")

if [ -n "$STAGED_FILES" ]; then
    for file in $STAGED_FILES; do
        python manage.py validate_openapi --file "$file" --severity error
        if [ $? -ne 0 ]; then
            echo "❌ Validation failed for $file"
            echo "💡 Run: python manage.py validate_openapi --file $file --fix"
            exit 1
        fi
    done
fi

echo "✅ All schemas valid"
```

#### CI/CD Pipeline

```yaml
name: Validate OpenAPI Schemas

on:
  pull_request:
    paths:
      - '**/*serializers.py'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate schemas
        run: |
          python manage.py validate_openapi --severity error
          python manage.py validate_openapi --report html --output report.html

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: report.html
```

#### Weekly Report

```bash
#!/bin/bash
# scripts/weekly_validation.sh

# Generate comprehensive report
python manage.py validate_openapi \
  --report html \
  --output "reports/validation_$(date +%Y-%m-%d).html"

# Send to team (example with curl)
curl -X POST https://your-webhook.com/reports \
  -F "file=@reports/validation_$(date +%Y-%m-%d).html"
```

---

## Common Workflows

### Development Workflow

During active development:

```bash
# 1. Validate configuration
python manage.py generate_client --validate

# 2. List groups and check matched apps
python manage.py generate_client --list-groups

# 3. Validate OpenAPI quality
python manage.py validate_openapi --app myapp

# 4. Fix issues
python manage.py validate_openapi --app myapp --fix

# 5. Generate clients
python manage.py generate_client
```

### Pre-Deployment Checklist

Before deploying to production:

```bash
# 1. Validate everything
python manage.py validate_openapi --severity error

# 2. Generate fresh clients
python manage.py generate_client

# 3. Run type checks
cd frontend && pnpm tsc --noEmit
cd ../backend && mypy api_client/

# 4. Commit changes
git add openapi/
git commit -m "chore: update API clients"
```

### Debugging Issues

When generation fails:

```bash
# 1. Check configuration
python manage.py generate_client --validate

# 2. List groups
python manage.py generate_client --list-groups

# 3. Dry run to see what would happen
python manage.py generate_client --dry-run

# 4. Validate schemas
python manage.py validate_openapi --verbose

# 5. Generate specific group
python manage.py generate_client --groups problematic_group
```

---

## Troubleshooting

### `generate_client` Issues

**"OpenAPI client generation is not enabled"**
```python
# Enable in django-cfg configuration
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    enabled=True,  # ← Must be True
    # ...
)
```

**"No groups to generate"**
- Check that groups are configured
- Run `--list-groups` to see matched apps
- Verify app names match installed apps

**"No apps matched for group"**
- Check app name patterns in group configuration
- Run `--list-groups` to see matched apps
- Verify apps are in `INSTALLED_APPS`

### `validate_openapi` Issues

**"No issues found" but clients have `any` types**
- Check that serializers have type hints
- Run with `--verbose` flag
- Verify correct serializer file pattern

**"Auto-fix failed"**
- Run with `--dry-run` to preview changes
- Check file permissions
- Review error messages with `--verbose`

---

## Best Practices

### 1. Run Validation Before Generation

Always validate schemas before generating clients:

```bash
python manage.py validate_openapi --severity error --fix
python manage.py generate_client
```

### 2. Use Dry Run for Testing

Test configuration changes with dry-run:

```bash
python manage.py generate_client --dry-run
```

### 3. Generate Regularly

Regenerate clients after any API changes:

```bash
# After modifying serializers
python manage.py generate_client
```

### 4. Version Control Clients

Always commit generated clients:

```bash
git add openapi/
git commit -m "chore: update API clients"
```

### 5. CI/CD Integration

Automate generation in your CI/CD pipeline (see workflow examples above).

---

## Next Steps

- **[Configuration](./overview#configuration)** - Configure django_client
- **[Getting Started](./getting-started)** - Installation guide
- **[Examples](./examples)** - Usage examples
