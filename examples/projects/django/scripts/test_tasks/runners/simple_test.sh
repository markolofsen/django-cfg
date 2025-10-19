#!/bin/bash

# Simple Task Test for debugging

set -e

# Get script directory and project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Simple Task Test"
echo "Script dir: $SCRIPT_DIR"
echo "Project dir: $PROJECT_DIR"

# Check if we're in right place
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    echo "❌ manage.py not found in $PROJECT_DIR"
    exit 1
fi

echo "✅ Found manage.py"

# Test basic Django command
cd "$PROJECT_DIR"
echo "🔧 Testing Django shell access..."

poetry run python manage.py shell -c "
print('Django is working!')
try:
    from django_cfg.apps.knowbase.models import Document
    print('✅ Knowbase models imported successfully')
except ImportError as e:
    print(f'❌ Knowbase import failed: {e}')

try:
    from django_cfg.apps.payments.models import UniversalPayment
    print('✅ Payments models imported successfully')
except ImportError as e:
    print(f'❌ Payments import failed: {e}')

try:
    from django_cfg.models.tasks import TaskConfig
    print('✅ TaskConfig imported successfully')
except ImportError as e:
    print(f'❌ TaskConfig import failed: {e}')
"

echo "🎯 Test completed"
