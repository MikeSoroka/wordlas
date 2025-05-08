from django.test import TestCase
from .forms import WordForm

# Create your tests here.

class LithuanianCharacterValidationTest(TestCase):
    def test_valid_word_with_lithuanian_characters(self):
        """Test that words with valid Lithuanian characters are accepted"""
        valid_words = [
            'LABAS',  # Basic Lithuanian word
            'MEILĖ',  # With special character Ė
            'ŽĄSIS',  # With special characters Ž and Ą
            'ĄČĘĖĮ',  # Only special Lithuanian characters
            'ŠŲŪŽĖ'   # More special Lithuanian characters
        ]
        
        for word in valid_words:
            form = WordForm(data={'word': word})
            self.assertTrue(form.is_valid(), f"Word '{word}' should be valid")
    
    def test_invalid_word_with_non_lithuanian_characters(self):
        """Test that words with non-Lithuanian characters are rejected"""
        invalid_words = [
            'HELLO',  # English word with non-Lithuanian character W
            'WORLD',  # English word with non-Lithuanian character W
            'TEST5',  # Contains number
            'TÆST',   # Contains non-Lithuanian character Æ
            'ИМЯ',    # Cyrillic characters
            'ÖÄËÄ',   # Non-Lithuanian special characters
            'ABC!D'    # Contains special character !
        ]
        
        for word in invalid_words:
            form = WordForm(data={'word': word})
            self.assertFalse(form.is_valid(), f"Word '{word}' should be invalid")
    
    def test_word_length_validation(self):
        """Test that words must be exactly 5 characters"""
        # Test too short
        form = WordForm(data={'word': 'ABCD'})
        self.assertFalse(form.is_valid())
        
        # Test too long
        form = WordForm(data={'word': 'ABCDEF'})
        self.assertFalse(form.is_valid())
        
        # Test empty
        form = WordForm(data={'word': ''})
        self.assertFalse(form.is_valid())
    
    def test_case_insensitivity(self):
        """Test that lowercase letters are converted to uppercase"""
        form = WordForm(data={'word': 'labas'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['word'], 'LABAS')
