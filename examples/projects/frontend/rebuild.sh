#!/bin/bash

# Rebuild script for Django-CFG Frontend
# This script removes old build and creates a fresh one

set -e  # Exit on error

echo "🗑️  Removing old frontend build..."
rm -rf ../django_cfg/frontend

echo "✅ Removed old build"
echo ""

echo "🏗️  Building fresh static export..."
cd /Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/django-cfg/projects/django-cfg-dev/src/@frontend
make build-admin

echo ""
echo "✅ Build complete!"
echo ""
echo "📂 Check results:"
echo "   ls -la ../django_cfg/frontend/admin/"
