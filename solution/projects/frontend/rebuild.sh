#!/bin/bash

# Rebuild script for Django-CFG Frontend
# This script removes old build and creates a fresh one

set -e  # Exit on error

echo "🗑️  Removing old frontend build..."
rm -rf ../django_cfg/frontend

echo "✅ Removed old build"
echo ""

echo "🏗️  Building fresh static export..."
cd /Users/markinmatrix/workspace/@projects/django-cfg/projects/django-cfg/src/@frontend
make build-admin

echo ""
echo "✅ Build complete!"
echo ""
echo "📂 Check results:"
echo "   ls -la ../django_cfg/frontend/admin/"
