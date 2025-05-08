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
        
        # Test word that's too long
        long_word = Word(
            word="abcdefg",
            difficulty_level="easy", 
            category="noun"
        )
        with self.assertRaises(ValidationError):
            long_word.full_clean()
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        default_word = Word.objects.create(word="testas")
        self.assertEqual(default_word.difficulty_level, "medium")
        self.assertEqual(default_word.category, "noun")
        self.assertTrue(default_word.active)
    
    def test_difficulty_choices(self):
        """Test the difficulty choices."""
        # Valid difficulty
        word = Word.objects.create(
            word="namai",
            difficulty_level="hard"
        )
        self.assertEqual(word.difficulty_level, "hard")
        
        # Invalid difficulty
        invalid_word = Word(
            word="kazkas",
            difficulty_level="extreme"
        )
        with self.assertRaises(ValidationError):
            invalid_word.full_clean()
    
    def test_category_choices(self):
        """Test the category choices."""
        # Valid category
        word = Word.objects.create(
            word="žaisti",
            category="verb"
        )
        self.assertEqual(word.category, "verb")
        
        # Invalid category
        invalid_word = Word(
            word="kitas",
            category="preposition"
        )
        with self.assertRaises(ValidationError):
            invalid_word.full_clean()
