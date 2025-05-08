from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Create your models here.
class Word(models.Model):
    """Model for Lithuanian words used in the game."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    CATEGORY_CHOICES = [
        ('noun', 'Noun'),
        ('verb', 'Verb'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('other', 'Other'),
    ]
    
    word = models.CharField(
        max_length=5, 
        unique=True, 
        validators=[MinLengthValidator(5), MaxLengthValidator(5)],
        help_text="The Lithuanian 5-letter word"
    )
    difficulty_level = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_CHOICES, 
        default='medium',
        help_text="The difficulty level of the word"
    )
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='noun',
        help_text="The grammatical category of the word"
    )
    active = models.BooleanField(
        default=True,
        help_text="Whether this word is active in the game"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.word
    
    class Meta:
        verbose_name = "Lithuanian Word"
        verbose_name_plural = "Lithuanian Words"
        ordering = ['word']
