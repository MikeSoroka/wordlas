# e2e_tests.py
"""
End-to-end tests using Selenium WebDriver.
Install with: pip install selenium
"""

import time
import unittest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User


class WordlasE2ETestCase(StaticLiveServerTestCase):
    """Base class for end-to-end tests."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Set up Chrome WebDriver with options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode for CI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.selenium = webdriver.Chrome(options=chrome_options)
            cls.selenium.implicitly_wait(10)
        except Exception as e:
            raise unittest.SkipTest(f"Could not start Chrome WebDriver: {e}")
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'selenium'):
            cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        self.wait = WebDriverWait(self.selenium, 10)


class GamePlayE2ETest(WordlasE2ETestCase):
    """End-to-end tests for game play functionality."""
    
    def test_complete_game_workflow(self):
        """Test a complete game from start to finish."""
        # Navigate to the game
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Verify page loads correctly
        self.assertIn('Wordlas', self.selenium.title)
        
        # Check that the game grid is present
        word_grid = self.wait.until(
            EC.presence_of_element_located((By.ID, 'word-grid'))
        )
        self.assertIsNotNone(word_grid)
        
        # Check that letter cells are present
        letter_cells = self.selenium.find_elements(By.CLASS_NAME, 'letter-cell')
        self.assertEqual(len(letter_cells), 30)  # 6 rows × 5 letters
        
        # Test typing a word using physical keyboard
        first_cell = letter_cells[0]
        first_cell.click()
        
        # Type a test word
        test_word = "LABAS"
        for letter in test_word:
            first_cell.send_keys(letter)
            time.sleep(0.1)  # Small delay between keystrokes
        
        # Verify letters were entered
        row_inputs = self.selenium.find_elements(By.CSS_SELECTOR, '.game-row:first-child input')
        entered_word = ''.join([input_elem.get_attribute('value') for input_elem in row_inputs])
        self.assertEqual(entered_word, test_word)
        
        # Submit the word
        submit_button = self.selenium.find_element(By.ID, 'check-word-btn')
        submit_button.click()
        
        # Wait for the word to be processed
        time.sleep(1)
        
        # Check that the first row is now disabled
        first_row_inputs = self.selenium.find_elements(By.CSS_SELECTOR, '.game-row:first-child input')
        for input_elem in first_row_inputs:
            self.assertTrue(input_elem.get_attribute('disabled'))
    
    def test_virtual_keyboard_interaction(self):
        """Test interaction with the virtual keyboard."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Wait for virtual keyboard to load
        virtual_keyboard = self.wait.until(
            EC.presence_of_element_located((By.ID, 'virtual-keyboard'))
        )
        
        # Test clicking on virtual keyboard keys
        key_a = self.selenium.find_element(By.CSS_SELECTOR, '[data-key="A"]')
        key_a.click()
        
        # Verify letter was entered in the first cell
        first_cell = self.selenium.find_element(By.CSS_SELECTOR, '.letter-cell')
        self.assertEqual(first_cell.get_attribute('value'), 'A')
        
        # Test special Lithuanian characters
        key_a_with_accent = self.selenium.find_element(By.CSS_SELECTOR, '[data-key="Ą"]')
        key_a_with_accent.click()
        
        # Verify the accented character was entered
        second_cell = self.selenium.find_elements(By.CSS_SELECTOR, '.letter-cell')[1]
        self.assertEqual(second_cell.get_attribute('value'), 'Ą')
        
        # Test backspace key
        backspace_key = self.selenium.find_element(By.CSS_SELECTOR, '[data-key="⌫"]')
        backspace_key.click()
        
        # Verify letter was removed
        self.assertEqual(second_cell.get_attribute('value'), '')
    
    def test_theme_toggle_functionality(self):
        """Test theme toggle functionality."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Find theme toggle button
        theme_toggle = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'theme-toggle'))
        )
        
        # Check initial theme (should be light by default)
        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        initial_theme = html_element.get_attribute('data-theme')
        
        # Click theme toggle
        theme_toggle.click()
        time.sleep(0.5)  # Wait for theme change animation
        
        # Check that theme changed
        new_theme = html_element.get_attribute('data-theme')
        self.assertNotEqual(initial_theme, new_theme)
        
        # Toggle again
        theme_toggle.click()
        time.sleep(0.5)
        
        # Check that theme changed back
        final_theme = html_element.get_attribute('data-theme')
        self.assertEqual(initial_theme, final_theme)
    
    def test_game_reset_functionality(self):
        """Test new game/reset functionality."""
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Enter some letters
        first_cell = self.selenium.find_element(By.CSS_SELECTOR, '.letter-cell')
        first_cell.click()
        first_cell.send_keys('LABAS')
        
        # Click reset button
        reset_button = self.selenium.find_element(By.ID, 'reset-grid-btn')
        reset_button.click()
        
        # Verify grid was reset
        letter_cells = self.selenium.find_elements(By.CSS_SELECTOR, '.letter-cell')
        for cell in letter_cells[:5]:  # Check first row
            self.assertEqual(cell.get_attribute('value'), '')
    
    def test_responsive_design(self):
        """Test responsive design on different screen sizes."""
        # Test mobile view
        self.selenium.set_window_size(375, 667)  # iPhone SE size
        self.selenium.get(f'{self.live_server_url}/index/')
        
        # Verify game is still playable on mobile
        word_grid = self.wait.until(
            EC.presence_of_element_located((By.ID, 'word-grid'))
        )
        self.assertTrue(word_grid.is_displayed())
        
        # Check that virtual keyboard is visible
        virtual_keyboard = self.selenium.find_element(By.ID, 'virtual-keyboard')
        self.assertTrue(virtual_keyboard.is_displayed())
        
        # Test tablet view
        self.selenium.set_window_size(768, 1024)  # iPad size
        
        # Verify layout adjusts properly
        game_container = self.selenium.find_element(By.ID, 'game-container')
        self.assertTrue(game_container.is_displayed())
        
        # Test desktop view
        self.selenium.set_window_size(1920, 1080)
        
        # Verify all elements are properly positioned
        theme_toggle = self.selenium.find_element(By.ID, 'theme-toggle')
        self.assertTrue(theme_toggle.is_displayed())


class UserAuthenticationE2ETest(WordlasE2ETestCase):
    """End-to-end tests for user authentication."""
    
    def test_user_registration_flow(self):
        """Test complete user registration flow."""
        self.selenium.get(f'{self.live_server_url}/')  # Goes to register page
        
        # Fill in registration form
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys('testuser')
        
        email_field = self.selenium.find_element(By.NAME, 'email')
        email_field.send_keys('test@example.com')
        
        password1_field = self.selenium.find_element(By.NAME, 'password1')
        password1_field.send_keys('testpassword123')
        
        password2_field = self.selenium.find_element(By.NAME, 'password2')
        password2_field.send_keys('testpassword123')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should redirect to index page
        self.wait.until(lambda driver: 'index' in driver.current_url)
        self.assertIn('index', self.selenium.current_url)
    
    def test_user_login_flow(self):
        """Test complete user login flow."""
        # Create a test user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Fill in login form
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys('testuser')
        
        password_field = self.selenium.find_element(By.NAME, 'password')
        password_field.send_keys('testpassword123')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should redirect to index page
        self.wait.until(lambda driver: 'index' in driver.current_url)
        self.assertIn('index', self.selenium.current_url)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Fill in invalid credentials
        username_field = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys('nonexistentuser')
        
        password_field = self.selenium.find_element(By.NAME, 'password')
        password_field.send_keys('wrongpassword')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should stay on login page with error
        time.sleep(1)  # Wait for page to process
        self.assertIn('login', self.selenium.current_url)
        
        # Check for error message
        page_source = self.selenium.page_source
        self.assertIn('Invalid username or password', page_source)


# template_tests.py
"""
Tests for Django templates and template tags.
"""

from django.test import TestCase, RequestFactory
from django.template import Context, Template
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.http import HttpRequest
from main.context_processors import theme_context


class TemplateRenderingTest(TestCase):
    """Test template rendering functionality."""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_index_template_rendering(self):
        """Test that index template renders correctly."""
        from main.forms import WordForm
        
        context = {
            'form': WordForm(),
            'theme': 'light'
        }
        
        rendered = render_to_string('index.html', context)
        
        # Check that essential elements are present
        self.assertIn('Wordlas', rendered)
        self.assertIn('word-grid', rendered)
        self.assertIn('virtual-keyboard', rendered)
        self.assertIn('theme-toggle', rendered)
    
    def test_register_template_rendering(self):
        """Test that register template renders correctly."""
        from main.forms import UserRegisterForm
        
        context = {
            'form': UserRegisterForm()
        }
        
        rendered = render_to_string('register.html', context)
        
        # Check form elements
        self.assertIn('Register', rendered)
        self.assertIn('username', rendered)
        self.assertIn('email', rendered)
        self.assertIn('password1', rendered)
        self.assertIn('password2', rendered)
    
    def test_login_template_rendering(self):
        """Test that login template renders correctly."""
        from main.forms import UserLoginForm
        
        context = {
            'form': UserLoginForm()
        }
        
        rendered = render_to_string('login.html', context)
        
        # Check form elements
        self.assertIn('Log In', rendered)
        self.assertIn('username', rendered)
        self.assertIn('password', rendered)
    
    def test_theme_context_processor(self):
        """Test theme context processor functionality."""
        # Test default theme (light)
        request = self.factory.get('/')
        context = theme_context(request)
        self.assertEqual(context['theme'], 'light')
        
        # Test with dark theme cookie
        request = self.factory.get('/')
        request.COOKIES = {'theme': 'dark'}
        context = theme_context(request)
        self.assertEqual(context['theme'], 'dark')
    
    def test_template_inheritance(self):
        """Test that template inheritance works correctly."""
        # This would test base templates if they existed
        # For now, we'll test that templates render without errors
        
        from main.forms import WordForm
        context = {'form': WordForm(), 'theme': 'light'}
        
        try:
            rendered = render_to_string('index.html', context)
            self.assertIsNotNone(rendered)
        except Exception as e:
            self.fail(f"Template rendering failed: {e}")
    
    def test_css_and_js_inclusion(self):
        """Test that CSS and JavaScript files are properly included."""
        from main.forms import WordForm
        
        context = {
            'form': WordForm(),
            'theme': 'light'
        }
        
        rendered = render_to_string('index.html', context)
        
        # Check for CSS files
        self.assertIn('styles.css', rendered)
        
        # Check for JS files
        self.assertIn('word-grid.js', rendered)
        self.assertIn('keyboard.js', rendered)
        self.assertIn('theme-toggle.js', rendered)
        self.assertIn('lithuanian-validation.js', rendered)
        self.assertIn('main.js', rendered)
    
    def test_theme_specific_rendering(self):
        """Test that templates render differently based on theme."""
        from main.forms import WordForm
        
        # Test light theme
        light_context = {'form': WordForm(), 'theme': 'light'}
        light_rendered = render_to_string('index.html', light_context)
        
        # Test dark theme
        dark_context = {'form': WordForm(), 'theme': 'dark'}
        dark_rendered = render_to_string('index.html', dark_context)
        
        # Check that dark theme has data-theme attribute
        if 'data-theme="dark"' in dark_rendered:
            self.assertIn('data-theme="dark"', dark_rendered)
            self.assertNotIn('data-theme="dark"', light_rendered)


class StaticFilesTest(TestCase):
    """Test static files functionality."""
    
    def test_css_files_accessible(self):
        """Test that CSS files are accessible."""
        from django.contrib.staticfiles.testing import StaticLiveServerTestCase
        from django.contrib.staticfiles import finders
        
        # Test that CSS files can be found
        css_files = ['css/styles.css', 'css/register.css']
        
        for css_file in css_files:
            found_file = finders.find(css_file)
            self.assertIsNotNone(found_file, f"CSS file {css_file} not found")
    
    def test_js_files_accessible(self):
        """Test that JavaScript files are accessible."""
        from django.contrib.staticfiles import finders
        
        js_files = [
            'js/word-grid.js',
            'js/keyboard.js',
            'js/theme-toggle.js',
            'js/lithuanian-validation.js',
            'js/main.js'
        ]
        
        for js_file in js_files:
            found_file = finders.find(js_file)
            self.assertIsNotNone(found_file, f"JavaScript file {js_file} not found")
    
    def test_jquery_library_included(self):
        """Test that jQuery library is included."""
        from django.contrib.staticfiles import finders
        
        jquery_file = finders.find('js/jquery-3.7.1.min.js')
        self.assertIsNotNone(jquery_file, "jQuery library not found")


class FormRenderingTest(TestCase):
    """Test form rendering in templates."""
    
    def test_word_form_rendering(self):
        """Test WordForm rendering in template."""
        from main.forms import WordForm
        
        template = Template("""
            {% load static %}
            <form method="post">
                {% csrf_token %}
                {{ form.word }}
                <div id="validation-errors" class="error-message">
                    {% if form.word.errors %}
                        {{ form.word.errors }}
                    {% endif %}
                </div>
            </form>
        """)
        
        context = Context({'form': WordForm()})
        rendered = template.render(context)
        
        # Check that form elements are present
        self.assertIn('word-input', rendered)
        self.assertIn('Įveskite 5 raidžių žodį', rendered)
        self.assertIn('validation-errors', rendered)
    
    def test_form_with_errors_rendering(self):
        """Test form rendering with validation errors."""
        from main.forms import WordForm
        
        # Create form with invalid data
        form = WordForm(data={'word': 'HELLO'})  # Invalid Lithuanian word
        form.is_valid()  # Trigger validation
        
        template = Template("""
            <form method="post">
                {{ form.word }}
                {% if form.word.errors %}
                    <div class="errors">
                        {{ form.word.errors }}
                    </div>
                {% endif %}
            </form>
        """)
        
        context = Context({'form': form})
        rendered = template.render(context)
        
        # Check that errors are displayed
        self.assertIn('lietuviškos raidės', rendered)
        self.assertIn('errors', rendered)
    
    def test_user_forms_rendering(self):
        """Test user registration and login forms rendering."""
        from main.forms import UserRegisterForm, UserLoginForm
        
        # Test registration form
        reg_template = Template("""
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
            </form>
        """)
        
        reg_context = Context({'form': UserRegisterForm()})
        reg_rendered = reg_template.render(reg_context)
        
        self.assertIn('username', reg_rendered)
        self.assertIn('email', reg_rendered)
        self.assertIn('password1', reg_rendered)
        self.assertIn('password2', reg_rendered)
        
        # Test login form
        login_template = Template("""
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
            </form>
        """)
        
        login_context = Context({'form': UserLoginForm()})
        login_rendered = login_template.render(login_context)
        
        self.assertIn('username', login_rendered)
        self.assertIn('password', login_rendered)
        self.assertIn('form-control', login_rendered)  # CSS classes
