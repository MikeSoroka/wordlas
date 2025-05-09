from django.db import models
import uuid
from django.core.validators import MinLengthValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class Game(models.Model):
    """
    Represents a game session.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='game_id'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='games'
    )
    word_to_guess = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'game_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Game {self.id} - {self.word_to_guess}"

    def is_won(self):
        """
        Check if the game was won by comparing the last guess with the word to guess.
        """
        if not self.ended_at:
            return False
            
        # Get the last guess from the game
        last_guess = self.guesses.order_by('-created_at').first()
        if not last_guess:
            return False
            
        # Compare the guess with the word to guess
        return last_guess.guessed_word.lower() == self.word_to_guess.lower()

    def guesses_count(self):
        """
        Get the number of guesses made in the game.
        """
        return self.guesses.count()

    def is_guess_correct(self, guess):
        """
        Check if a guess matches the word to guess.
        """
        return guess.lower() == self.word_to_guess.lower()

class GuessResultPattern(models.Model):
    class LetterMatch(models.TextChoices):
        GREEN = 'G', 'Green'
        YELLOW = 'Y', 'Yellow'
        NONE = 'N', 'None'

    id = models.AutoField(
        primary_key=True,
        db_column='pattern_id'
    )
    pattern = models.CharField(
        max_length=5,
        validators=[MinLengthValidator(5)],
        choices=LetterMatch.choices,
        default='NNNNN',  # Default to all None
        null=True,  # Allow null temporarily for migration
        blank=True  # Allow blank temporarily for migration
    )

    class Meta:
        db_table = 'guess_patterns'

    def __str__(self):
        return self.pattern or 'NNNNN'  # Return default if pattern is None

class Guess(models.Model):
    """
    Represents a single guess attempt within a game.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='guess_id'
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='guesses'
    )
    guessed_word = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    result_pattern = models.ForeignKey(
        GuessResultPattern,
        on_delete=models.PROTECT,
        related_name='guesses'
    )
    attempt_number = models.PositiveIntegerField()

    class Meta:
        db_table = 'game_guesses'
        ordering = ['attempt_number']
        unique_together = ['game', 'attempt_number']

    def __str__(self):
        return f"Guess {self.attempt_number} for game {self.game_id}: {self.guessed_word}"

class DictionaryWord(models.Model):
    """
    Represents a word in the Lithuanian dictionary.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='word_id'
    )
    word_text = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(1)]
    )
    complexity = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'dictionary_words'
        indexes = [
            models.Index(fields=['word_text']),
            models.Index(fields=['complexity'])
        ]

    def __str__(self):
        return f"{self.word_text} (complexity: {self.complexity})"

class GameStatistics(models.Model):
    """
    Represents statistics for a user's games.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='game_statistics'
    )
    games_played = models.PositiveIntegerField(default=0)
    games_won = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    max_streak = models.PositiveIntegerField(default=0)
    average_guesses = models.FloatField(default=0.0)
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'game_statistics'
        verbose_name_plural = 'Game Statistics'

    def __str__(self):
        return f"{self.user.username}'s Statistics"

    def update_statistics(self, won_game=False, guesses_count=None):
        """
        Update statistics after a game is completed.
        """
        self.games_played += 1
        
        if won_game:
            self.games_won += 1
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
            
            if guesses_count is not None:
                # Update average guesses
                total_guesses = self.average_guesses * (self.games_won - 1)
                self.average_guesses = (total_guesses + guesses_count) / self.games_won
        else:
            self.current_streak = 0
        
        self.save()