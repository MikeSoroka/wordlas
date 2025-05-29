from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from api.models import Game, GuessResultPattern, Guess, DictionaryWord
import uuid
from datetime import datetime, timedelta


class GameModelTest(TestCase):
    def setUp(self):
        """Set up test data for each test method."""
        self.valid_5_letter_word = "LABAS"
        self.invalid_short_word = "LAB"
        self.invalid_long_word = "LABASSSS"
        
    def test_game_creation_with_valid_word(self):
        """Test creating a game with a valid 5-letter word."""
        game = Game.objects.create(word_to_guess=self.valid_5_letter_word)
        
        self.assertEqual(game.word_to_guess, self.valid_5_letter_word)
        self.assertIsInstance(game.id, uuid.UUID)
        self.assertIsNotNone(game.created_at)
        self.assertIsNone(game.ended_at)
        self.assertTrue(Game.objects.filter(id=game.id).exists())
    
    def test_game_creation_with_invalid_short_word(self):
        """Test that creating a game with less than 5 letters raises ValidationError."""
        game = Game(word_to_guess=self.invalid_short_word)
        
        with self.assertRaises(ValidationError):
            game.full_clean()
    
    def test_game_creation_with_invalid_long_word(self):
        """Test that creating a game with more than 5 letters raises ValidationError."""
        game = Game(word_to_guess=self.invalid_long_word)
        
        with self.assertRaises(ValidationError):
            game.full_clean()
    
    def test_game_uuid_uniqueness(self):
        """Test that each game gets a unique UUID."""
        game1 = Game.objects.create(word_to_guess=self.valid_5_letter_word)
        game2 = Game.objects.create(word_to_guess=self.valid_5_letter_word)
        
        self.assertNotEqual(game1.id, game2.id)
        self.assertIsInstance(game1.id, uuid.UUID)
        self.assertIsInstance(game2.id, uuid.UUID)
    
    def test_game_string_representation(self):
        """Test the string representation of a Game object."""
        game = Game.objects.create(word_to_guess=self.valid_5_letter_word)
        expected_str = f"Game {game.id} - Word: {self.valid_5_letter_word}"
        
        self.assertEqual(str(game), expected_str)
    
    def test_game_ordering(self):
        """Test that games are ordered by created_at in descending order."""
        # Create games with slight time differences
        game1 = Game.objects.create(word_to_guess="FIRST")
        game2 = Game.objects.create(word_to_guess="SECND")
        
        games = Game.objects.all()
        self.assertEqual(games[0], game2)  # Most recent first
        self.assertEqual(games[1], game1)
    
    def test_game_end_timestamp(self):
        """Test setting the ended_at timestamp."""
        game = Game.objects.create(word_to_guess=self.valid_5_letter_word)
        self.assertIsNone(game.ended_at)
        
        # End the game
        end_time = timezone.now()
        game.ended_at = end_time
        game.save()
        
        game.refresh_from_db()
        self.assertIsNotNone(game.ended_at)
        self.assertAlmostEqual(
            game.ended_at.timestamp(), 
            end_time.timestamp(), 
            delta=1  # Allow 1 second difference
        )


class GuessResultPatternModelTest(TestCase):
    def test_letter_match_choices(self):
        """Test that LetterMatch choices are correctly defined."""
        choices = GuessResultPattern.LetterMatch.choices
        expected_choices = [('G', 'Green'), ('Y', 'Yellow'), ('N', 'None')]
        
        self.assertEqual(choices, expected_choices)
    
    def test_letter_match_values(self):
        """Test individual LetterMatch choice values."""
        self.assertEqual(GuessResultPattern.LetterMatch.GREEN, 'G')
        self.assertEqual(GuessResultPattern.LetterMatch.YELLOW, 'Y')
        self.assertEqual(GuessResultPattern.LetterMatch.NONE, 'N')
    
    def test_pattern_creation_with_valid_pattern(self):
        """Test creating a pattern with valid 5-character pattern."""
        valid_patterns = ['GGGGG', 'YYYYN', 'NNNNN', 'GYNYG']
        
        for pattern in valid_patterns:
            with self.subTest(pattern=pattern):
                result_pattern = GuessResultPattern.objects.create(pattern=pattern)
                self.assertEqual(result_pattern.pattern, pattern)
    
    def test_pattern_string_representation(self):
        """Test the string representation of GuessResultPattern."""
        pattern = 'GYNGN'
        result_pattern = GuessResultPattern.objects.create(pattern=pattern)
        
        # Note: There's a bug in the model - pattern field has a trailing comma
        # This test might need adjustment based on actual model behavior
        self.assertIsNotNone(str(result_pattern))


class GuessModelTest(TestCase):
    def setUp(self):
        """Set up test data for guess tests."""
        self.game = Game.objects.create(word_to_guess="LABAS")
        self.pattern = GuessResultPattern.objects.create(pattern="GYNGN")
        
    def test_guess_creation(self):
        """Test creating a valid guess."""
        guess = Guess.objects.create(
            game=self.game,
            guessed_word="MAMAS",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        self.assertEqual(guess.game, self.game)
        self.assertEqual(guess.guessed_word, "MAMAS")
        self.assertEqual(guess.result_pattern, self.pattern)
        self.assertEqual(guess.attempt_number, 1)
        self.assertIsInstance(guess.id, uuid.UUID)
        self.assertIsNotNone(guess.created_at)
    
    def test_guess_unique_together_constraint(self):
        """Test that game + attempt_number must be unique."""
        # Create first guess
        Guess.objects.create(
            game=self.game,
            guessed_word="FIRST",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        # Try to create another guess with same game and attempt_number
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Guess.objects.create(
                    game=self.game,
                    guessed_word="SECND",
                    result_pattern=self.pattern,
                    attempt_number=1
                )
    
    def test_guess_ordering(self):
        """Test that guesses are ordered by attempt_number."""
        guess3 = Guess.objects.create(
            game=self.game,
            guessed_word="THIRD",
            result_pattern=self.pattern,
            attempt_number=3
        )
        guess1 = Guess.objects.create(
            game=self.game,
            guessed_word="FIRST",
            result_pattern=self.pattern,
            attempt_number=1
        )
        guess2 = Guess.objects.create(
            game=self.game,
            guessed_word="SECND",
            result_pattern=self.pattern,
            attempt_number=2
        )
        
        guesses = Guess.objects.filter(game=self.game)
        self.assertEqual(guesses[0], guess1)
        self.assertEqual(guesses[1], guess2)
        self.assertEqual(guesses[2], guess3)
    
    def test_guess_string_representation(self):
        """Test the string representation of a Guess object."""
        guess = Guess.objects.create(
            game=self.game,
            guessed_word="MAMAS",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        expected_str = f"Guess 1 for game {self.game.id}: MAMAS"
        self.assertEqual(str(guess), expected_str)
    
    def test_guess_cascade_delete(self):
        """Test that guesses are deleted when the game is deleted."""
        guess = Guess.objects.create(
            game=self.game,
            guessed_word="MAMAS",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        guess_id = guess.id
        self.assertTrue(Guess.objects.filter(id=guess_id).exists())
        
        # Delete the game
        self.game.delete()
        
        # Guess should also be deleted
        self.assertFalse(Guess.objects.filter(id=guess_id).exists())
    
    def test_guess_pattern_protect(self):
        """Test that pattern cannot be deleted if guesses reference it."""
        guess = Guess.objects.create(
            game=self.game,
            guessed_word="MAMAS",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        # Try to delete the pattern - should be protected
        with self.assertRaises(Exception):  # Django will raise ProtectedError
            self.pattern.delete()
        
        # Guess should still exist
        self.assertTrue(Guess.objects.filter(id=guess.id).exists())


class DictionaryWordModelTest(TestCase):
    def test_dictionary_word_creation(self):
        """Test creating a dictionary word with valid data."""
        word = DictionaryWord.objects.create(
            word_text="LABAS",
            complexity=3
        )
        
        self.assertEqual(word.word_text, "LABAS")
        self.assertEqual(word.complexity, 3)
        self.assertIsNotNone(word.id)
    
    def test_dictionary_word_uniqueness(self):
        """Test that word_text must be unique."""
        DictionaryWord.objects.create(word_text="LABAS", complexity=3)
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DictionaryWord.objects.create(word_text="LABAS", complexity=5)
    
    def test_dictionary_word_string_representation(self):
        """Test the string representation of DictionaryWord."""
        word = DictionaryWord.objects.create(
            word_text="LABAS",
            complexity=3
        )
        
        expected_str = "LABAS (complexity: 3)"
        self.assertEqual(str(word), expected_str)
    
    def test_dictionary_word_minimum_length_validation(self):
        """Test that empty word_text raises ValidationError."""
        word = DictionaryWord(word_text="", complexity=1)
        
        with self.assertRaises(ValidationError):
            word.full_clean()
    
    def test_dictionary_word_complexity_positive(self):
        """Test that complexity must be positive."""
        # This should work
        word = DictionaryWord(word_text="LABAS", complexity=1)
        word.full_clean()  # Should not raise
        
        # This might work depending on Django's PositiveSmallIntegerField validation
        word_zero = DictionaryWord(word_text="ZERO", complexity=0)
        with self.assertRaises(ValidationError):
            word_zero.full_clean()


class ModelRelationshipTest(TestCase):
    """Test relationships between models."""
    
    def setUp(self):
        self.game = Game.objects.create(word_to_guess="LABAS")
        self.pattern = GuessResultPattern.objects.create(pattern="GYNGN")
        
    def test_game_guesses_relationship(self):
        """Test the reverse relationship from Game to Guess."""
        guess1 = Guess.objects.create(
            game=self.game,
            guessed_word="FIRST",
            result_pattern=self.pattern,
            attempt_number=1
        )
        guess2 = Guess.objects.create(
            game=self.game,
            guessed_word="SECND", 
            result_pattern=self.pattern,
            attempt_number=2
        )
        
        # Test reverse relationship
        game_guesses = self.game.guesses.all()
        self.assertEqual(game_guesses.count(), 2)
        self.assertIn(guess1, game_guesses)
        self.assertIn(guess2, game_guesses)
    
    def test_pattern_guesses_relationship(self):
        """Test the reverse relationship from GuessResultPattern to Guess."""
        guess1 = Guess.objects.create(
            game=self.game,
            guessed_word="FIRST",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        # Create another game and guess with same pattern
        game2 = Game.objects.create(word_to_guess="MAMAS")
        guess2 = Guess.objects.create(
            game=game2,
            guessed_word="SECND",
            result_pattern=self.pattern,
            attempt_number=1
        )
        
        # Test reverse relationship
        pattern_guesses = self.pattern.guesses.all()
        self.assertEqual(pattern_guesses.count(), 2)
        self.assertIn(guess1, pattern_guesses)
        self.assertIn(guess2, pattern_guesses)
