# test_settings.py
"""
Test-specific Django settings for running tests efficiently.
This file should be placed in your project root directory.
"""

from .settings import *

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug toolbar and other dev tools in tests
DEBUG = False
TEMPLATE_DEBUG = False

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Disable cache during tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use local email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable static files handling during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# test_runner.py
"""
Custom test runner with additional functionality.
Place this in your project root or in a utils directory.
"""

import os
import sys
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.test.utils import get_runner


class WordlasTestRunner(DiscoverRunner):
    """Custom test runner for Wordlas project."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def setup_test_environment(self, **kwargs):
        """Set up test environment with custom settings."""
        super().setup_test_environment(**kwargs)
        
        # Add any custom test environment setup here
        print("Setting up Wordlas test environment...")
        
        # Ensure we're using test settings
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.test_settings')
    
    def teardown_test_environment(self, **kwargs):
        """Clean up after tests."""
        super().teardown_test_environment(**kwargs)
        print("Tearing down Wordlas test environment...")
    
    def setup_databases(self, **kwargs):
        """Set up test databases."""
        print("Setting up test databases...")
        return super().setup_databases(**kwargs)
    
    def teardown_databases(self, old_config, **kwargs):
        """Clean up test databases."""
        print("Tearing down test databases...")
        super().teardown_databases(old_config, **kwargs)


# conftest.py (for pytest configuration)
"""
PyTest configuration file.
Place this in your project root directory if using pytest.
"""

import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure():
    """Configure Django for pytest."""
    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SITE_ID=1,
        SECRET_KEY='test-secret-key',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='project.urls',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
        MIDDLEWARE=[
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'api',
            'main',
        ],
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ],
    )
    django.setup()


@pytest.fixture(scope='function')
def db_setup():
    """Set up database for each test function."""
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)


# test commands and scripts

# run_tests.py
"""
Comprehensive test runner script.
Usage: python run_tests.py [options]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_django_tests():
    """Run Django unit tests."""
    print("Running Django unit tests...")
    
    cmd = [
        sys.executable, 
        'manage.py', 
        'test',
        '--settings=project.test_settings',
        '--verbosity=2',
        '--keepdb'  # Keep test database for faster subsequent runs
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Django tests passed!")
    else:
        print("❌ Django tests failed!")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_javascript_tests():
    """Run JavaScript tests if Jest is configured."""
    print("Running JavaScript tests...")
    
    # Check if Jest is available
    jest_config = Path('jest.config.js')
    package_json = Path('package.json')
    
    if not (jest_config.exists() or package_json.exists()):
        print("⚠️  No Jest configuration found. Skipping JavaScript tests.")
        return True
    
    try:
        result = subprocess.run(['npm', 'test'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ JavaScript tests passed!")
        else:
            print("❌ JavaScript tests failed!")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️  npm not found. Skipping JavaScript tests.")
        return True

def run_coverage_analysis():
    """Run test coverage analysis."""
    print("Running coverage analysis...")
    
    try:
        # Install coverage if not available
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                      capture_output=True)
        
        # Run tests with coverage
        cmd = [
            sys.executable, '-m', 'coverage', 'run',
            '--source', '.',
            '--omit', '*/migrations/*,*/venv/*,*/env/*,*/tests/*,manage.py,*/settings/*',
            'manage.py', 'test',
            '--settings=project.test_settings'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Generate coverage report
            subprocess.run([sys.executable, '-m', 'coverage', 'report'])
            subprocess.run([sys.executable, '-m', 'coverage', 'html'])
            print("✅ Coverage analysis complete! Check htmlcov/index.html for detailed report.")
        else:
            print("❌ Coverage analysis failed!")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Coverage analysis failed: {e}")
        return False

def run_specific_tests(test_path):
    """Run specific test files or classes."""
    print(f"Running specific tests: {test_path}")
    
    cmd = [
        sys.executable,
        'manage.py',
        'test',
        test_path,
        '--settings=project.test_settings',
        '--verbosity=2'
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Wordlas project tests')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage analysis')
    parser.add_argument('--js-only', action='store_true',
                       help='Run only JavaScript tests')
    parser.add_argument('--django-only', action='store_true',
                       help='Run only Django tests')
    parser.add_argument('--specific', type=str,
                       help='Run specific test (e.g., api.tests.GameModelTest)')
    
    args = parser.parse_args()
    
    success = True
    
    if args.specific:
        success = run_specific_tests(args.specific)
    elif args.js_only:
        success = run_javascript_tests()
    elif args.django_only:
        success = run_django_tests()
    elif args.coverage:
        success = run_coverage_analysis()
    else:
        # Run all tests
        print("Running all tests...")
        django_success = run_django_tests()
        js_success = run_javascript_tests()
        success = django_success and js_success
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()


# Makefile (optional - for easier test running)
"""
Makefile for common test operations.
Place this in your project root directory.
"""

MAKEFILE_CONTENT = """
# Wordlas Test Commands

.PHONY: test test-django test-js test-coverage test-fast help

# Default target
help:
	@echo "Available test commands:"
	@echo "  test          - Run all tests"
	@echo "  test-django   - Run only Django tests"
	@echo "  test-js       - Run only JavaScript tests"
	@echo "  test-coverage - Run tests with coverage analysis"
	@echo "  test-fast     - Run tests without coverage (faster)"
	@echo "  test-models   - Run only model tests"
	@echo "  test-views    - Run only view tests"
	@echo "  test-forms    - Run only form tests"
	@echo "  clean-test    - Clean test artifacts"

test:
	python run_tests.py

test-django:
	python run_tests.py --django-only

test-js:
	python run_tests.py --js-only

test-coverage:
	python run_tests.py --coverage

test-fast:
	python manage.py test --settings=project.test_settings --keepdb

test-models:
	python manage.py test api.test_models main.test_models --settings=project.test_settings

test-views:
	python manage.py test api.test_views main.test_views --settings=project.test_settings

test-forms:
	python manage.py test main.test_forms --settings=project.test_settings

test-integration:
	python manage.py test integration_tests --settings=project.test_settings

clean-test:
	rm -rf htmlcov/
	rm -f .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Install test dependencies
install-test-deps:
	pip install coverage pytest pytest-django
	npm install --save-dev jest jsdom

# Create test database
create-test-db:
	python manage.py migrate --settings=project.test_settings

# Run specific test by name
test-specific:
	@read -p "Enter test path (e.g., api.tests.GameModelTest.test_game_creation): " test_path; \
	python manage.py test $$test_path --settings=project.test_settings -v 2
"""

# GitHub Actions CI/CD configuration
GITHUB_ACTIONS_CONFIG = """
# .github/workflows/tests.yml
name: Wordlas Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: wordlas_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage pytest pytest-django
    
    - name: Install JavaScript dependencies
      run: |
        npm install
        npm install --save-dev jest jsdom
    
    - name: Run Django tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/wordlas_test
      run: |
        python manage.py test --settings=project.test_settings
    
    - name: Run JavaScript tests
      run: |
        npm test
    
    - name: Generate coverage report
      run: |
        coverage run --source='.' manage.py test --settings=project.test_settings
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
"""

# Package.json for JavaScript testing
PACKAGE_JSON_CONFIG = """
{
  "name": "wordlas-frontend-tests",
  "version": "1.0.0",
  "description": "Frontend tests for Wordlas game",
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "devDependencies": {
    "jest": "^27.0.0",
    "jsdom": "^16.0.0",
    "jquery": "^3.6.0"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/jest.setup.js"],
    "collectCoverageFrom": [
      "main/static/js/*.js",
      "!main/static/js/jquery-*.js"
    ],
    "coverageDirectory": "js-coverage",
    "coverageReporters": ["text", "lcov", "html"]
  }
}
"""

# Write configuration files
def write_config_files():
    """Write all configuration files to appropriate locations."""
    
    configs = {
        'Makefile': MAKEFILE_CONTENT,
        '.github/workflows/tests.yml': GITHUB_ACTIONS_CONFIG,
        'package.json': PACKAGE_JSON_CONFIG
    }
    
    for filename, content in configs.items():
        print(f"Configuration for {filename}:")
        print(content)
        print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    write_config_files()
