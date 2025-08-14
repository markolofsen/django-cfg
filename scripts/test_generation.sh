#!/bin/bash

# Django Revolution - Test Generation Script
# Run this script from the django_revolution directory

set -e  # Exit on any error

echo "🚀 Starting Django Revolution test generation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if django_sample directory exists
if [ ! -d "django_sample" ]; then
    print_error "django_sample directory not found!"
    print_status "Please ensure you're running this from the django_revolution directory"
    exit 1
fi

# Change to django_sample directory where manage.py is located
print_status "Changing to django_sample directory..."
cd django_sample

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found in django_sample directory!"
    exit 1
fi

# Set correct PYTHONPATH and run generation
print_status "Setting PYTHONPATH and running test generation..."
PYTHONPATH=..:.: python teststest_real_generation.py

if [ $? -eq 0 ]; then
    print_success "Test generation completed successfully!"
else
    print_error "Test generation failed!"
    exit 1
fi

echo "✅ All done!" 