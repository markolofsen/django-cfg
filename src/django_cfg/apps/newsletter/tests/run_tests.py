#!/usr/bin/env python3
"""
Script to run newsletter manager tests
"""
import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import and run tests
from django.test.utils import get_runner
from django.conf import settings

def run_tests():
    """Run the newsletter tests"""
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modules to run
    test_modules = [
        'mailer.tests.test_newsletter_manager',
        'mailer.tests.test_newsletter_models',
    ]
    
    print("Running Newsletter Manager Tests...")
    print("=" * 50)
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 