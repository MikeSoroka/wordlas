from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Word

class WordModelTest(TestCase):
    """Test cases for the Word model."""
    
    def setUp(self):
        """Set up test data."""
        self.word = Word.objects.create(
            word="labas",
            difficulty_level="medium",
            category="noun"
        )
    
    def test_word_creation(self):
        """Test that a word can be created with valid data."""
        self.assertEqual(self.word.word, "labas")
        self.assertEqual(self.word.difficulty_level, "medium")
        self.assertEqual(self.word.category, "noun")
        self.assertTrue(self.word.active)
        self.assertIsNotNone(self.word.created_at)
        self.assertIsNotNone(self.word.updated_at)
    
    def test_word_string_representation(self):
        """Test the string representation of a word."""
        self.assertEqual(str(self.word), "labas")
    
    def test_word_uniqueness(self):
        """Test that two words cannot have the same value."""
        duplicate_word = Word(
            word="labas",
            difficulty_level="easy",
            category="verb"
        )
        with self.assertRaises(Exception):
            duplicate_word.save()
    
    def test_word_length_validation(self):
        """Test that a word must be exactly 5 characters."""
        # Test word that's too short
        short_word = Word(
            word="abc",
            difficulty_level="easy",
            category="noun"
        )
        with self.assertRaises(ValidationError):
            short_word.full_clean()
        
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
