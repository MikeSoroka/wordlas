from django import forms
from django.core.exceptions import ValidationError
import re

class WordForm(forms.Form):
    """
    Form for validating words with Lithuanian characters
    """
    word = forms.CharField(
        max_length=5,
        min_length=5,
        widget=forms.TextInput(attrs={
            'class': 'word-input',
            'placeholder': 'Įveskite 5 raidžių žodį',
        })
    )

    def clean_word(self):
        """
        Custom validation to ensure only valid Lithuanian characters are used
        """
        word = self.cleaned_data['word'].upper()
        
        # Regex pattern for valid Lithuanian characters
        # Lithuanian alphabet: A Ą B C Č D E Ę Ė F G H I Į Y J K L M N O P R S Š T U Ų Ū V Z Ž
        lithuanian_pattern = r'^[AĄBCČDEĘĖFGHIĮYJKLMNOPRSŠTUŲŪVZŽ]{5}$'
        
        if not re.match(lithuanian_pattern, word):
            raise ValidationError('Žodyje gali būti naudojamos tik lietuviškos raidės.')
        
        return word 