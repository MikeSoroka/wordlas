from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from main.forms import UserRegisterForm, UserLoginForm, WordForm


class WordFormTest(TestCase):
    """Comprehensive tests for WordForm with Lithuanian character validation."""
    
    def test_valid_basic_lithuanian_words(self):
        """Test that basic Lithuanian words are accepted."""
        valid_words = [
            'LABAS',  # Basic Lithuanian word
            'DIENA',  # Another basic word
            'NAMAS',  # Another basic word
            'DUONA',  # Basic word
            'KATĖS',  # With Ė
        ]
        
        for word in valid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertTrue(form.is_valid(), f"Word '{word}' should be valid but got errors: {form.errors}")
                self.assertEqual(form.cleaned_data['word'], word.upper())
    
    def test_valid_words_with_special_lithuanian_characters(self):
        """Test words with all Lithuanian special characters."""
        valid_words = [
            'MEILĖ',  # With Ė
            'ŽĄSIS',  # With Ž and Ą  
            'ĄČĘĖĮ',  # Only special characters
            'ŠŲŪŽĖ',  # More special characters
            'ĮŠŪŽĄ',  # Different combination
            'ČĘĖĮŠ',  # Another combination
            'ŲŪŽĄČ',  # Different pattern
        ]
        
        for word in valid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertTrue(form.is_valid(), f"Word '{word}' should be valid but got errors: {form.errors}")
                self.assertEqual(form.cleaned_data['word'], word.upper())
    
    def test_case_insensitive_validation(self):
        """Test that lowercase and mixed case words are converted to uppercase."""
        test_cases = [
            ('labas', 'LABAS'),
            ('LabaS', 'LABAS'),
            ('LABAS', 'LABAS'),
            ('meilė', 'MEILĖ'),
            ('MeIlĖ', 'MEILĖ'),
            ('žąsis', 'ŽĄSIS'),
        ]
        
        for input_word, expected_output in test_cases:
            with self.subTest(input_word=input_word):
                form = WordForm(data={'word': input_word})
                self.assertTrue(form.is_valid(), f"Word '{input_word}' should be valid")
                self.assertEqual(form.cleaned_data['word'], expected_output)
    
    def test_invalid_non_lithuanian_characters(self):
        """Test that words with non-Lithuanian characters are rejected."""
        invalid_words = [
            'HELLO',  # English letters only
            'WORLD',  # English with W
            'TÆST',   # Non-Lithuanian special character Æ
            'ÖÄËÄ',   # German/Nordic characters  
            'CAFÉ',   # French accent
            'NIÑO',   # Spanish Ñ
            'МОСКВ',  # Cyrillic
            'ΑΒΓΔΕ',  # Greek
        ]
        
        for word in invalid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid")
                self.assertIn('word', form.errors)
                self.assertIn('lietuviškos raidės', str(form.errors['word']))
    
    def test_invalid_words_with_numbers(self):
        """Test that words containing numbers are rejected."""
        invalid_words = [
            'TEST5',
            'LA8AS',
            '12345',
            'LAB4S',
            'A1B2C',
        ]
        
        for word in invalid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid")
                self.assertIn('word', form.errors)
    
    def test_invalid_words_with_special_symbols(self):
        """Test that words with special symbols are rejected."""
        invalid_words = [
            'ABC!D',
            'LAB@S', 
            'TEST#',
            'WOR$D',
            'HEL%O',
            'WOR&D',
            'TES*T',
            'LAB+S',
            'WOR=D',
            'TES-T',
            'LAB_S',
            'WOR|D',
            'TES\\T',
            'LAB/S',
            'WOR?D',
            'TES.T',
            'LAB,S',
            'WOR;D',
            'TES:T',
            "LAB'S",
            'WOR"D',
            'TES[T',
            'LAB]S',
            'WOR{D',
            'TES}T',
        ]
        
        for word in invalid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid")
                self.assertIn('word', form.errors)
    
    def test_invalid_word_length_too_short(self):
        """Test that words shorter than 5 characters are rejected."""
        short_words = ['A', 'AB', 'ABC', 'ABCD', 'LAB', 'Ž', 'ŽĘ']
        
        for word in short_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid (too short)")
                self.assertIn('word', form.errors)
    
    def test_invalid_word_length_too_long(self):
        """Test that words longer than 5 characters are rejected."""
        long_words = [
            'ABCDEF', 
            'LABASSO', 
            'ŽĄČĘĖĮŠŲŪŽ',  # 10 Lithuanian chars
            'VERYLONGWORD'
        ]
        
        for word in long_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid (too long)")
                self.assertIn('word', form.errors)
    
    def test_empty_word(self):
        """Test that empty word is rejected."""
        form = WordForm(data={'word': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('word', form.errors)
    
    def test_whitespace_in_word(self):
        """Test that words with whitespace are rejected."""
        invalid_words = [
            'LAB S',
            ' LABAS',
            'LABAS ',
            'LA AS',
            'L A B A S',
            '\tLABAS',
            'LABAS\n',
        ]
        
        for word in invalid_words:
            with self.subTest(word=repr(word)):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word {repr(word)} should be invalid")
    
    def test_form_widget_attributes(self):
        """Test that the form widget has correct attributes."""
        form = WordForm()
        widget = form.fields['word'].widget
        
        self.assertIn('word-input', widget.attrs.get('class', ''))
        self.assertEqual(widget.attrs.get('placeholder'), 'Įveskite 5 raidžių žodį')
    
    def test_form_field_properties(self):
        """Test that the form field has correct properties."""
        form = WordForm()
        field = form.fields['word']
        
        self.assertEqual(field.max_length, 5)
        self.assertEqual(field.min_length, 5)
    
    def test_mixed_valid_invalid_characters(self):
        """Test words that mix valid and invalid characters."""
        invalid_words = [
            'LABA5',  # 4 Lithuanian + 1 number
            'LABxS',  # 4 Lithuanian + 1 English
            'ŽĄx23',  # 2 Lithuanian + 3 invalid
            'ĖĘ!@#',  # 2 Lithuanian + 3 symbols
        ]
        
        for word in invalid_words:
            with self.subTest(word=word):
                form = WordForm(data={'word': word})
                self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid")


class UserRegisterFormTest(TestCase):
    """Tests for UserRegisterForm."""
    
    def setUp(self):
        """Create a user for email uniqueness tests."""
        self.existing_user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='testpass123'
        )
    
    def test_valid_registration_form(self):
        """Test valid registration data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid but got errors: {form.errors}")
    
    def test_email_uniqueness_validation(self):
        """Test that duplicate email addresses are rejected."""
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Same as existing user
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Email address already in use', str(form.errors['email']))
    
    def test_email_case_insensitive_uniqueness(self):
        """Test that email uniqueness is case insensitive."""
        form_data = {
            'username': 'newuser',
            'email': 'EXISTING@EXAMPLE.COM',  # Same email, different case
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = UserRegisterForm(data=form_data)
        # This test depends on how Django handles email case sensitivity
        # May need adjustment based on actual behavior
        self.assertFalse(form.is_valid())
    
    def test_required_fields(self):
        """Test that all required fields are validated."""
        # Test missing username
        form = UserRegisterForm(data={
            'email': 'test@example.com',
            'password1': 'pass123',
            'password2': 'pass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Test missing email
        form = UserRegisterForm(data={
            'username': 'testuser',
            'password1': 'pass123',
            'password2': 'pass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_password_mismatch(self):
        """Test that mismatched passwords are rejected."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword123'
        }
        
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_saves_user(self):
        """Test that the form correctly saves a new user."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(User.objects.filter(username='newuser').exists())


class UserLoginFormTest(TestCase):
    """Tests for UserLoginForm."""
    
    def test_valid_login_form(self):
        """Test valid login form data."""
        form_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')
        self.assertEqual(form.cleaned_data['password'], 'testpassword')
    
    def test_missing_username(self):
        """Test that missing username is rejected."""
        form = UserLoginForm(data={'password': 'testpassword'})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_missing_password(self):
        """Test that missing password is rejected."""
        form = UserLoginForm(data={'username': 'testuser'})
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    def test_empty_form(self):
        """Test that empty form is rejected."""
        form = UserLoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_form_widget_attributes(self):
        """Test that form widgets have correct CSS classes and placeholders."""
        form = UserLoginForm()
        
        username_widget = form.fields['username'].widget
        password_widget = form.fields['password'].widget
        
        self.assertIn('form-control', username_widget.attrs.get('class', ''))
        self.assertEqual(username_widget.attrs.get('placeholder'), 'Username')
        
        self.assertIn('form-control', password_widget.attrs.get('class', ''))
        self.assertEqual(password_widget.attrs.get('placeholder'), 'Password')
    
    def test_username_max_length(self):
        """Test username field max length."""
        form = UserLoginForm()
        self.assertEqual(form.fields['username'].max_length, 150)
    
    def test_password_widget_type(self):
        """Test that password field uses PasswordInput widget."""
        form = UserLoginForm()
        from django.forms.widgets import PasswordInput
        self.assertIsInstance(form.fields['password'].widget, PasswordInput)


class FormIntegrationTest(TestCase):
    """Integration tests for forms working together."""
    
    def test_word_form_in_template_context(self):
        """Test that WordForm can be used in template context."""
        form = WordForm()
        
        # Test that form can be rendered (basic check)
        self.assertIsNotNone(str(form))
        self.assertIn('word', str(form))
    
    def test_multiple_form_validation(self):
        """Test validating multiple forms simultaneously."""
        word_form = WordForm(data={'word': 'LABAS'})
        login_form = UserLoginForm(data={'username': 'test', 'password': 'pass'})
        
        self.assertTrue(word_form.is_valid())
        self.assertTrue(login_form.is_valid())
    
    def test_form_error_messages_in_lithuanian(self):
        """Test that error messages contain Lithuanian text where appropriate."""
        form = WordForm(data={'word': 'HELLO'})
        self.assertFalse(form.is_valid())
        
        error_message = str(form.errors['word'])
        self.assertIn('lietuviškos raidės', error_message)
