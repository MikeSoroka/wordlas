# run_tests_simple.py
"""
Simplified test runner without NPM dependencies.
Usage: python run_tests_simple.py [options]
"""

import os
import sys
import subprocess
import argparse


def run_django_tests():
    """Run Django unit tests."""
    print("🧪 Running Django unit tests...")
    
    cmd = [
        sys.executable, 
        'project/manage.py', 
        'test',
        '--settings=project.test_settings',
        '--verbosity=2',
        '--keepdb'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Django tests passed!")
    else:
        print("❌ Django tests failed!")
    
    return result.returncode == 0


def run_javascript_browser_tests():
    """Run JavaScript tests through browser automation."""
    print("🌐 Running JavaScript browser tests...")
    
    # Run only the JavaScript integration tests
    cmd = [
        sys.executable, 
        'manage.py', 
        'test',
        'javascript_integration_tests',
        '--settings=project.test_settings',
        '--verbosity=2'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ JavaScript browser tests passed!")
    else:
        print("⚠️  JavaScript browser tests failed (Chrome WebDriver might not be available)")
    
    return result.returncode == 0


def run_coverage_analysis():
    """Run test coverage analysis."""
    print("📊 Running coverage analysis...")
    
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
        
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            # Generate coverage report
            subprocess.run([sys.executable, '-m', 'coverage', 'report'])
            subprocess.run([sys.executable, '-m', 'coverage', 'html'])
            print("✅ Coverage analysis complete! Check htmlcov/index.html")
        else:
            print("❌ Coverage analysis failed!")
        
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Coverage analysis failed: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Wordlas tests (No NPM required)')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage analysis')
    parser.add_argument('--browser', action='store_true',
                       help='Include browser-based JavaScript tests')
    parser.add_argument('--quick', action='store_true',
                       help='Run only essential tests quickly')
    parser.add_argument('--specific', type=str,
                       help='Run specific test (e.g., api.test_models)')
    
    args = parser.parse_args()
    
    success = True
    
    if args.specific:
        print(f"🎯 Running specific test: {args.specific}")
        cmd = [sys.executable, 'manage.py', 'test', args.specific, 
               '--settings=project.test_settings', '--verbosity=2']
        result = subprocess.run(cmd)
        success = result.returncode == 0
        
    elif args.coverage:
        success = run_coverage_analysis()
        
    elif args.quick:
        print("⚡ Running quick essential tests...")
        # Run only model and form tests for speed
        cmd = [sys.executable, 'manage.py', 'test', 
               'api.test_models', 'main.test_forms',
               '--settings=project.test_settings', '--verbosity=1']
        result = subprocess.run(cmd)
        success = result.returncode == 0
        
    else:
        # Run all tests
        print("🚀 Running all tests...")
        django_success = run_django_tests()
        
        js_success = True
        if args.browser:
            js_success = run_javascript_browser_tests()
        
        success = django_success and js_success
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()


# Simplified Makefile (No NPM commands)
SIMPLE_MAKEFILE = """
# Wordlas Test Commands (No NPM Required)

.PHONY: test test-quick test-coverage test-models test-forms test-views test-api help clean

help:
	@echo "Available commands:"
	@echo "  test          - Run all Django tests"
	@echo "  test-quick    - Run essential tests only (fast)"
	@echo "  test-coverage - Run tests with coverage analysis"
	@echo "  test-models   - Run only model tests"
	@echo "  test-forms    - Run only form tests"
	@echo "  test-views    - Run only view tests"
	@echo "  test-api      - Run only API tests"
	@echo "  test-browser  - Run with browser JavaScript tests"
	@echo "  clean         - Clean test artifacts"

test:
	python run_tests_simple.py

test-quick:
	python run_tests_simple.py --quick

test-coverage:
	python run_tests_simple.py --coverage

test-browser:
	python run_tests_simple.py --browser

test-models:
	python manage.py test api.test_models main.test_models --settings=project.test_settings

test-forms:
	python manage.py test main.test_forms --settings=project.test_settings

test-views:
	python manage.py test api.test_views main.test_views --settings=project.test_settings

test-api:
	python manage.py test api --settings=project.test_settings

clean:
	rm -rf htmlcov/
	rm -f .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache/

# Setup for development
setup-dev:
	pip install -r requirements.txt
	pip install coverage factory-boy
	python manage.py migrate --settings=project.test_settings

# Optional: Install Selenium for browser tests (only if needed)
setup-browser-tests:
	pip install selenium
	@echo "Note: You'll need to install ChromeDriver separately"
	@echo "Visit: https://chromedriver.chromium.org/"
"""


# requirements-test.txt (Minimal testing dependencies)
TEST_REQUIREMENTS = """
# Essential testing dependencies (No NPM/Node.js required)
coverage>=6.0
factory-boy>=3.2.0

# Optional: Only install if you want browser-based JavaScript testing
# selenium>=4.0.0

# Optional: Alternative to unittest
# pytest>=7.0.0
# pytest-django>=4.5.0
"""


# Simple GitHub Actions (No Node.js)
SIMPLE_GITHUB_ACTIONS = """
# .github/workflows/tests.yml - Simplified without Node.js
name: Wordlas Tests (Django Only)

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
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage factory-boy
    
    - name: Run Django tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/wordlas_test
      run: |
        python manage.py test --settings=project.test_settings
    
    - name: Generate coverage report
      run: |
        coverage run --source='.' manage.py test --settings=project.test_settings
        coverage xml
        coverage report
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
"""


# Quick setup script
SETUP_SCRIPT = """
#!/bin/bash
# setup_tests.sh - Quick test setup (No NPM)

echo "🚀 Setting up Wordlas testing environment..."

# Install Python test dependencies
echo "📦 Installing Python test dependencies..."
pip install coverage factory-boy

# Optional: Install Selenium for browser tests
read -p "Install Selenium for browser-based JavaScript tests? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install selenium
    echo "⚠️  Note: You'll need to install ChromeDriver separately"
    echo "   Visit: https://chromedriver.chromium.org/"
fi

# Create test database
echo "🗄️  Setting up test database..."
python manage.py migrate --settings=project.test_settings

# Run a quick test to verify setup
echo "🧪 Running a quick test to verify setup..."
python manage.py test api.test_models.GameModelTest.test_game_creation_with_valid_word --settings=project.test_settings

echo "✅ Test setup complete!"
echo ""
echo "Usage:"
echo "  python run_tests_simple.py           # Run all tests"
echo "  python run_tests_simple.py --quick   # Quick essential tests"
echo "  python run_tests_simple.py --coverage # With coverage"
echo "  make test                            # Using Makefile"
"""


def create_test_files():
    """Generate all simplified test configuration files."""
    
    files = {
        'Makefile': SIMPLE_MAKEFILE,
        'requirements-test.txt': TEST_REQUIREMENTS,
        '.github/workflows/tests.yml': SIMPLE_GITHUB_ACTIONS,
        'setup_tests.sh': SETUP_SCRIPT
    }
    
    print("📁 Simplified Test Configuration Files:")
    print("=" * 50)
    
    for filename, content in files.items():
        print(f"\n## {filename}")
        print("-" * 30)
        print(content.strip())
        print()


if __name__ == '__main__':
    create_test_files()
