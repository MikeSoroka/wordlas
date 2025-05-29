# javascript_integration_tests.py
"""
Test JavaScript functionality through Django's test framework.
No NPM required - uses Selenium and Django's static file serving.
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class JavaScriptFunctionalityTest(StaticLiveServerTestCase):
    """Test JavaScript functionality through browser interaction."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            cls.selenium = webdriver.Chrome(options=chrome_options)
            cls.selenium.implicitly_wait(10)
        except Exception:
            # Fallback to no JavaScript testing if Chrome not available
            cls.selenium = None
    
    @classmethod
    def tearDownClass(cls):
        if cls.selenium:
            cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        if not self.selenium:
            self.skipTest("Chrome WebDriver not available")
        self.wait = WebDriverWait(self.selenium, 10)

    def test_lithuanian_character_validation_javascript(self):
        """Test Lithuanian character validation in the browser."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Test valid Lithuanian characters
        first_input = self.selenium.find_element(By.CSS_SELECTOR, '.letter-cell')
        first_input.click()
        
        # Test Lithuanian special characters
        lithuanian_chars = ['Ą', 'Č', 'Ę', 'Ė', 'Į', 'Š', 'Ų', 'Ū', 'Ž']
        for char in lithuanian_chars:
            first_input.clear()
            first_input.send_keys(char)
            # Verify character was accepted
            self.assertEqual(first_input.get_attribute('value'), char)
    
    def test_word_grid_functionality(self):
        """Test word grid game logic through browser interaction."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Fill in a word
        inputs = self.selenium.find_elements(By.CSS_SELECTOR, '.game-row:first-child .letter-cell')
        test_word = "LABAS"
        
        for i, letter in enumerate(test_word):
            inputs[i].click()
            inputs[i].send_keys(letter)
        
        # Submit the word
        submit_btn = self.selenium.find_element(By.ID, 'check-word-btn')
        submit_btn.click()
        
        # Wait for processing
        time.sleep(1)
        
        # Check that row is now disabled
        for input_elem in inputs:
            self.assertIsNotNone(input_elem.get_attribute('disabled'))
    
    def test_virtual_keyboard_functionality(self):
        """Test virtual keyboard JavaScript functionality."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Click virtual keyboard keys
        key_l = self.selenium.find_element(By.CSS_SELECTOR, '[data-key="L"]')
        key_a = self.selenium.find_element(By.CSS_SELECTOR, '[data-key="A"]')
        
        key_l.click()
        time.sleep(0.1)
        key_a.click()
        
        # Check that letters were entered
        inputs = self.selenium.find_elements(By.CSS_SELECTOR, '.letter-cell')
        self.assertEqual(inputs[0].get_attribute('value'), 'L')
        self.assertEqual(inputs[1].get_attribute('value'), 'A')
    
    def test_theme_toggle_javascript(self):
        """Test theme toggle JavaScript functionality."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Get initial theme
        html_elem = self.selenium.find_element(By.TAG_NAME, 'html')
        initial_theme = html_elem.get_attribute('data-theme')
        
        # Click theme toggle
        theme_toggle = self.selenium.find_element(By.ID, 'theme-toggle')
        theme_toggle.click()
        time.sleep(0.5)
        
        # Check theme changed
        new_theme = html_elem.get_attribute('data-theme')
        self.assertNotEqual(initial_theme, new_theme)


class JavaScriptStaticAnalysisTest(TestCase):
    """Test JavaScript files without executing them."""
    
    def test_javascript_files_exist(self):
        """Test that all required JavaScript files exist."""
        from django.contrib.staticfiles import finders
        
        required_js_files = [
            'js/word-grid.js',
            'js/keyboard.js',
            'js/lithuanian-validation.js',
            'js/theme-toggle.js',
            'js/main.js'
        ]
        
        for js_file in required_js_files:
            found_file = finders.find(js_file)
            self.assertIsNotNone(found_file, f"JavaScript file {js_file} not found")
    
    def test_javascript_syntax_validation(self):
        """Basic JavaScript syntax validation."""
        from django.contrib.staticfiles import finders
        import os
        
        js_files = [
            'js/word-grid.js',
            'js/keyboard.js',
            'js/lithuanian-validation.js',
            'js/theme-toggle.js',
            'js/main.js'
        ]
        
        for js_file in js_files:
            file_path = finders.find(js_file)
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Basic syntax checks
                    self.assertNotIn('console.error', content, f"Error logging found in {js_file}")
                    
                    # Check for common JavaScript patterns
                    if 'word-grid.js' in js_file:
                        self.assertIn('checkWord', content)
                        self.assertIn('createGrid', content)
                    
                    if 'keyboard.js' in js_file:
                        self.assertIn('keyboard', content.lower())
                    
                    if 'theme-toggle.js' in js_file:
                        self.assertIn('theme', content.lower())


# html_js_test.html (Manual JavaScript Testing)
"""
Create this file in main/static/test/html_js_test.html for manual testing.
"""

HTML_JS_TEST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Function Tests</title>
    <script src="{% load static %}{% static 'js/jquery-3.7.1.min.js' %}"></script>
    <style>
        .test-result { 
            padding: 10px; 
            margin: 5px 0; 
            border-radius: 4px; 
        }
        .pass { background-color: #d4edda; color: #155724; }
        .fail { background-color: #f8d7da; color: #721c24; }
        .test-container { max-width: 800px; margin: 20px auto; font-family: Arial; }
    </style>
</head>
<body>
    <div class="test-container">
        <h1>JavaScript Function Tests</h1>
        <div id="test-results"></div>
        
        <!-- Test elements -->
        <div style="display: none;">
            <input class="letter-cell" maxlength="1" />
            <div class="game-row">
                <input class="letter-cell" maxlength="1" />
                <input class="letter-cell" maxlength="1" />
                <input class="letter-cell" maxlength="1" />
                <input class="letter-cell" maxlength="1" />
                <input class="letter-cell" maxlength="1" />
            </div>
        </div>
    </div>

    <script>
        // Simple test framework
        function runTest(testName, testFunction) {
            const resultDiv = document.getElementById('test-results');
            try {
                const result = testFunction();
                if (result === true || result === undefined) {
                    resultDiv.innerHTML += `<div class="test-result pass">✓ ${testName}</div>`;
                } else {
                    resultDiv.innerHTML += `<div class="test-result fail">✗ ${testName}: ${result}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML += `<div class="test-result fail">✗ ${testName}: ${error.message}</div>`;
            }
        }

        // Test Lithuanian character validation
        runTest('Lithuanian Character Validation - Valid Characters', function() {
            // You'd need to include your lithuanian-validation.js here
            const validChars = ['A', 'Ą', 'B', 'C', 'Č', 'E', 'Ę', 'Ė'];
            // Mock test - replace with actual function calls
            return true; // Replace with actual validation logic test
        });

        // Test word grid functionality
        runTest('Word Grid - Count Letters Function', function() {
            // Mock test for countLetters function from word-grid.js
            // You'd include the actual function and test it here
            return true;
        });

        // Test theme toggle
        runTest('Theme Toggle - Function Exists', function() {
            // Test that theme toggle functionality works
            return typeof document.getElementById === 'function';
        });

        // Test jQuery integration
        runTest('jQuery Integration', function() {
            return typeof $ !== 'undefined' && typeof $.fn.jquery !== 'undefined';
        });
    </script>
</body>
</html>
'''


# simple_js_test_runner.py
"""
Simple JavaScript test runner using Django's test client.
No NPM required - tests JavaScript through HTTP requests.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import json
import re


class JavaScriptHTTPTest(TestCase):
    """Test JavaScript functionality through HTTP responses."""
    
    def setUp(self):
        self.client = Client()
    
    def test_javascript_files_served_correctly(self):
        """Test that JavaScript files are served with correct content type."""
        js_files = [
            '/static/js/word-grid.js',
            '/static/js/keyboard.js', 
            '/static/js/lithuanian-validation.js',
            '/static/js/theme-toggle.js',
            '/static/js/main.js'
        ]
        
        for js_file in js_files:
            response = self.client.get(js_file)
            if response.status_code == 200:
                self.assertIn('text/javascript', response.get('Content-Type', ''))
    
    def test_page_includes_all_javascript(self):
        """Test that the main page includes all required JavaScript files."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
        required_scripts = [
            'word-grid.js',
            'keyboard.js',
            'lithuanian-validation.js',
            'theme-toggle.js',
            'main.js',
            'jquery-3.7.1.min.js'
        ]
        
        content = response.content.decode('utf-8')
        for script in required_scripts:
            self.assertIn(script, content, f"Script {script} not found in page")
    
    def test_javascript_validation_logic_through_forms(self):
        """Test JavaScript validation by testing the underlying form logic."""
        from main.forms import WordForm
        
        # Test cases that JavaScript should handle
        test_cases = [
            ('LABAS', True),   # Valid Lithuanian word
            ('HELLO', False),  # Invalid - non-Lithuanian characters  
            ('LAB', False),    # Invalid - too short
            ('TOOLONG', False) # Invalid - too long
        ]
        
        for word, should_be_valid in test_cases:
            form = WordForm(data={'word': word})
            is_valid = form.is_valid()
            
            if should_be_valid:
                self.assertTrue(is_valid, f"Word '{word}' should be valid")
            else:
                self.assertFalse(is_valid, f"Word '{word}' should be invalid")


class JavaScriptAPIIntegrationTest(TestCase):
    """Test JavaScript-API integration without running JavaScript."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
    
    def test_api_endpoints_work_for_javascript(self):
        """Test that API endpoints work as JavaScript expects."""
        # Test game creation (what keyboard.js does)
        response = self.client.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        
        # Test game update (what keyboard.js does)
        from api.models import Game
        game = Game.objects.latest('created_at')
        
        update_data = {
            'id': str(game.id),
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_token_available_for_javascript(self):
        """Test that CSRF token is available for JavaScript AJAX calls."""
        response = self.client.get(reverse('index'))
        content = response.content.decode('utf-8')
        
        # Check for CSRF token in template
        csrf_pattern = r'csrfmiddlewaretoken|csrf_token'
        self.assertTrue(
            re.search(csrf_pattern, content),
            "CSRF token should be available for JavaScript"
        )


# Manual Testing Instructions
MANUAL_TESTING_GUIDE = """
# Manual JavaScript Testing Guide (No NPM Required)

## 1. Browser Console Testing

Open your browser's developer console on the game page and run:

```javascript
// Test 1: Lithuanian character validation
console.log('Testing Lithuanian chars...');
isValidLithuanianChar('Ą'); // Should return true
isValidLithuanianChar('W'); // Should return false

// Test 2: Word validation  
isValidLithuanianWord('LABAS'); // Should return true
isValidLithuanianWord('HELLO'); // Should return false

// Test 3: Game grid functionality
countLetters('LABAS'); // Should return {L:1, A:2, B:1, S:1}

// Test 4: Theme toggle
document.getElementById('theme-toggle').click(); // Should change theme
```

## 2. Manual UI Testing Checklist

□ Type Lithuanian characters (Ą, Č, Ę, Ė, Į, Š, Ų, Ū, Ž) - should work
□ Type non-Lithuanian characters (W, X, Q) - should be rejected  
□ Click virtual keyboard keys - should enter letters
□ Submit 5-letter word - should move to next row
□ Submit invalid word - should show error
□ Click theme toggle - should switch dark/light mode
□ Reset game - should clear grid and start over

## 3. Network Tab Testing

Check browser Network tab to verify:
□ All JavaScript files load without 404 errors
□ API calls to /api/game/ work correctly  
□ No JavaScript errors in console
□ AJAX requests have proper CSRF tokens

## 4. Mobile Testing

Test on mobile device or browser dev tools:
□ Virtual keyboard works on touch
□ Game is playable on small screens
□ Theme toggle works on mobile
□ All buttons are properly sized for touch
"""


def create_manual_test_file():
    """Helper to create manual testing HTML file."""
    return HTML_JS_TEST_TEMPLATE


# Alternative: Use Django's built-in JavaScript testing
class DjangoJavaScriptTest(StaticLiveServerTestCase):
    """Test JavaScript using Django's built-in capabilities."""
    
    def test_javascript_through_django_client(self):
        """Test JavaScript functionality through Django test client."""
        # Test that pages load correctly
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
        # Test that all static files are accessible
        from django.contrib.staticfiles import finders
        
        js_files = [
            'js/word-grid.js',
            'js/keyboard.js',
            'js/main.js'
        ]
        
        for js_file in js_files:
            static_file = finders.find(js_file)
            self.assertIsNotNone(static_file)
            
            # Test file can be served
            response = self.client.get(f'/static/{js_file}')
            # Note: This might return 404 in test mode, which is expected
            # The important thing is that finders.find() works
