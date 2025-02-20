from django.db import models
import uuid
from django.core.validators import MinLengthValidator
from django.contrib.postgres.fields import ArrayField

class Game(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='game_id'
    )
    word_to_guess = models.CharField(
        max_length=5,
        validators=[MinLengthValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'game_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Game {self.id} - Word: {self.word_to_guess}"

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
        choices=LetterMatch.choices
    ),

    class Meta:
        db_table = 'guess_patterns'

    def __str__(self):
        return ''.join(self.pattern)

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