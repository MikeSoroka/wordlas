# factories.py
"""
Test factories for creating test data using Factory Boy.
Install with: pip install factory-boy
"""

import factory
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from api.models import Game, GuessResultPattern, Guess, DictionaryWord


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        
        password = extracted or 'defaultpassword123'
        self.set_password(password)
        self.save()


class SuperUserFactory(UserFactory):
    """Factory for creating superusers."""
    
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f'admin{n}')


class GameFactory(factory.django.DjangoModelFactory):
    """Factory for creating test games."""
    
    class Meta:
        model = Game
    
    word_to_guess = factory.Iterator([
        'LABAS', 'DIENA', 'NAMAS', 'MEILĖ', 'DUONA',
        'KATĖS', 'ŠALIS', 'GĖLĖS', 'LAIMĖ', 'ŽEMĖ'
    ])
    created_at = factory.LazyFunction(timezone.now)
    ended_at = None
    
    @classmethod
    def create_finished_game(cls, **kwargs):
        """Create a finished game with ended_at set."""
        game = cls(**kwargs)
        game.ended_at = timezone.now()
        game.save()
        return game
    
    @classmethod
    def create_with_guesses(cls, num_guesses=3, **kwargs):
        """Create a game with a specified number of guesses."""
        game = cls(**kwargs)
        
        # Create patterns for the guesses
        patterns = [
            GuessResultPatternFactory(),
            GuessResultPatternFactory(pattern='GYNGN'),
            GuessResultPatternFactory(pattern='GGGGG')
        ]
        
        # Create guesses
        for i in range(num_guesses):
            GuessFactory(
                game=game,
                attempt_number=i + 1,
                result_pattern=patterns[i % len(patterns)]
            )
        
        return game


class GuessResultPatternFactory(factory.django.DjangoModelFactory):
    """Factory for creating guess result patterns."""
    
    class Meta:
        model = GuessResultPattern
    
    pattern = factory.Iterator([
        'GGGGG',  # All correct
        'NNNNN',  # All wrong
        'GYNGN',  # Mixed
        'YYYGG',  # Mostly yellow with some green
        'GNNGG',  # Green at corners
        'YNGYN',  # Alternating
    ])


class GuessFactory(factory.django.DjangoModelFactory):
    """Factory for creating test guesses."""
    
    class Meta:
        model = Guess
    
    game = factory.SubFactory(GameFactory)
    guessed_word = factory.Iterator([
        'LABAS', 'TEMPO', 'MAMAS', 'TĖVAS', 'VAIKAS',
        'MERGĖ', 'VYRAS', 'ŽMONA', 'DRĄSA', 'ŠEIMA'
    ])
    result_pattern = factory.SubFactory(GuessResultPatternFactory)
    attempt_number = factory.Sequence(lambda n: n + 1)
    created_at = factory.LazyFunction(timezone.now)
    
    @classmethod
    def create_winning_guess(cls, game=None, **kwargs):
        """Create a guess that matches the game's word."""
        if game is None:
            game = GameFactory()
        
        winning_pattern = GuessResultPatternFactory(pattern='GGGGG')
        
        return cls(
            game=game,
            guessed_word=game.word_to_guess,
            result_pattern=winning_pattern,
            **kwargs
        )


class DictionaryWordFactory(factory.django.DjangoModelFactory):
    """Factory for creating dictionary words."""
    
    class Meta:
        model = DictionaryWord
        django_get_or_create = ('word_text',)
    
    word_text = factory.Iterator([
        'LABAS', 'DIENA', 'NAMAS', 'MEILĖ', 'DUONA', 'KATĖS', 'ŠALIS',
        'GĖLĖS', 'LAIMĖ', 'ŽEMĖ', 'SAULĖ', 'MĖNUO', 'VYRAS', 'KARTU',
        'MEDIS', 'ŠUNIS', 'KALBA', 'METAI', 'AKMUO', 'RANKA', 'TALKA',
        'DURYS', 'KNYGA', 'DRĄSA', 'LAPAS', 'SODAS', 'GATVĖ', 'KELIO',
        'VĖJAS', 'ŽODIS', 'VAKAR', 'RYTAS', 'VAIKO', 'DARBO', 'ŠOKIS'
    ])
    complexity = factory.Iterator([1, 2, 3, 4, 5])
    
    @classmethod
    def create_batch_by_complexity(cls, complexity_level, count=5):
        """Create multiple words with the same complexity level."""
        return cls.create_batch(count, complexity=complexity_level)


# fixtures.py
"""
Test fixtures for common test data.
"""

import pytest
from django.contrib.auth.models import User
from api.models import Game, GuessResultPattern, Guess, DictionaryWord


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )


@pytest.fixture
def superuser():
    """Create a test superuser."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123'
    )


@pytest.fixture
def game():
    """Create a test game."""
    return Game.objects.create(word_to_guess='LABAS')


@pytest.fixture
def finished_game():
    """Create a finished test game."""
    from django.utils import timezone
    game = Game.objects.create(word_to_guess='TEMPO')
    game.ended_at = timezone.now()
    game.save()
    return game


@pytest.fixture
def guess_patterns():
    """Create common guess result patterns."""
    patterns = {
        'all_correct': GuessResultPattern.objects.create(pattern='GGGGG'),
        'all_wrong': GuessResultPattern.objects.create(pattern='NNNNN'),
        'mixed': GuessResultPattern.objects.create(pattern='GYNGN'),
        'mostly_yellow': GuessResultPattern.objects.create(pattern='YYYGG'),
    }
    return patterns


@pytest.fixture
def game_with_guesses(game, guess_patterns):
    """Create a game with multiple guesses."""
    guesses = []
    
    guess_data = [
        ('MAMAS', guess_patterns['mixed']),
        ('TĖVAS', guess_patterns['mostly_yellow']),
        ('LABAS', guess_patterns['all_correct']),
    ]
    
    for i, (word, pattern) in enumerate(guess_data):
        guess = Guess.objects.create(
            game=game,
            guessed_word=word,
            result_pattern=pattern,
            attempt_number=i + 1
        )
        guesses.append(guess)
    
    return game, guesses


@pytest.fixture
def dictionary_words():
    """Create a set of dictionary words with different complexities."""
    words = []
    word_data = [
        ('LABAS', 1), ('DIENA', 2), ('NAMAS', 1),
        ('MEILĖ', 3), ('DUONA', 2), ('KATĖS', 4),
        ('ŠALIS', 3), ('GĖLĖS', 4), ('LAIMĖ', 5)
    ]
    
    for word_text, complexity in word_data:
        word = DictionaryWord.objects.create(
            word_text=word_text,
            complexity=complexity
        )
        words.append(word)
    
    return words


@pytest.fixture
def lithuanian_test_words():
    """Common Lithuanian words for testing validation."""
    return {
        'valid_5_letter': [
            'LABAS', 'DIENA', 'NAMAS', 'MEILĖ', 'DUONA',
            'ŽĄSIS', 'ĄČĘĖĮ', 'ŠŲŪŽĖ'
        ],
        'valid_with_specials': [
            'MEILĖ', 'ŽĄSIS', 'ĄČĘĖĮ', 'ŠŲŪŽĖ', 'ĮŠŪŽĄ'
        ],
        'invalid_chars': [
            'HELLO', 'WORLD', 'TEST5', 'LAB@S', 'TÆST'
        ],
        'invalid_length': [
            'LAB', 'ABCD', 'LABASSO', 'VERYLONGWORD'
        ]
    }


# test_data.py
"""
Static test data and constants.
"""

# Lithuanian alphabet for validation testing
LITHUANIAN_ALPHABET = {
    'vowels': ['A', 'Ą', 'E', 'Ę', 'Ė', 'I', 'Į', 'Y', 'O', 'U', 'Ų', 'Ū'],
    'consonants': ['B', 'C', 'Č', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'Š', 'T', 'V', 'Z', 'Ž'],
    'special_chars': ['Ą', 'Č', 'Ę', 'Ė', 'Į', 'Š', 'Ų', 'Ū', 'Ž'],
    'non_lithuanian': ['W', 'X', 'Q', 'Ö', 'Ä', 'Ü', 'Ñ', 'Ç']
}

# Test game scenarios
GAME_SCENARIOS = {
    'quick_win': {
        'target_word': 'LABAS',
        'guesses': [
            {'word': 'LABAS', 'result': ['G', 'G', 'G', 'G', 'G']}
        ]
    },
    'close_loss': {
        'target_word': 'LABAS',
        'guesses': [
            {'word': 'MAMAS', 'result': ['N', 'G', 'N', 'G', 'G']},
            {'word': 'TĖVAS', 'result': ['N', 'N', 'N', 'G', 'G']},
            {'word': 'RAMAS', 'result': ['N', 'G', 'N', 'G', 'G']},
            {'word': 'ŠABAS', 'result': ['N', 'G', 'N', 'G', 'G']},
            {'word': 'KABAS', 'result': ['N', 'G', 'N', 'G', 'G']},
            {'word': 'NABAS', 'result': ['N', 'G', 'N', 'G', 'G']}
        ]
    },
    'gradual_discovery': {
        'target_word': 'TEMPO',
        'guesses': [
            {'word': 'LABAS', 'result': ['N', 'N', 'N', 'N', 'N']},
            {'word': 'MEILĖ', 'result': ['Y', 'Y', 'N', 'N', 'N']},
            {'word': 'TEMPU', 'result': ['G', 'G', 'G', 'G', 'N']},
            {'word': 'TEMPO', 'result': ['G', 'G', 'G', 'G', 'G']}
        ]
    }
}

# Form test data
FORM_TEST_DATA = {
    'valid_registration': {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'complexpassword123',
        'password2': 'complexpassword123'
    },
    'invalid_registration': [
        {
            'data': {'username': 'testuser', 'email': 'invalid-email', 'password1': 'pass', 'password2': 'pass'},
            'expected_errors': ['email', 'password1']
        },
        {
            'data': {'username': '', 'email': 'test@example.com', 'password1': 'pass123', 'password2': 'different'},
            'expected_errors': ['username', 'password2']
        }
    ],
    'valid_login': {
        'username': 'testuser',
        'password': 'testpassword123'
    },
    'invalid_login': [
        {'username': '', 'password': 'testpassword123'},
        {'username': 'testuser', 'password': ''},
        {'username': '', 'password': ''}
    ]
}

# API test data
API_TEST_DATA = {
    'valid_game_creation': {
        'method': 'POST',
        'expected_status': 200,
        'expected_word': 'tempo'  # Current hardcoded word
    },
    'valid_game_update': {
        'method': 'PUT',
        'data': {'id': 'PLACEHOLDER_UUID', 'isfinished': True},
        'expected_status': 200
    },
    'invalid_game_update': [
        {
            'data': {'isfinished': True},  # Missing ID
            'expected_status': 400,
            'expected_message': 'No id provided'
        },
        {
            'data': {'id': 'invalid-uuid', 'isfinished': True},
            'expected_status': 200  # Current implementation returns 200 even for invalid IDs
        }
    ]
}

# Performance test data
PERFORMANCE_TEST_DATA = {
    'load_test_scenarios': [
        {'concurrent_users': 10, 'requests_per_user': 5},
        {'concurrent_users': 50, 'requests_per_user': 3},
        {'concurrent_users': 100, 'requests_per_user': 2}
    ],
    'stress_test_data': {
        'max_games_to_create': 1000,
        'max_guesses_per_game': 6,
        'timeout_seconds': 30
    }
}


# mixins.py
"""
Test mixins for common test functionality.
"""

class GameTestMixin:
    """Mixin providing common game testing utilities."""
    
    def create_game_with_word(self, word='LABAS'):
        """Create a game with a specific word."""
        return Game.objects.create(word_to_guess=word)
    
    def create_finished_game(self, word='TEMPO'):
        """Create a finished game."""
        from django.utils import timezone
        game = Game.objects.create(word_to_guess=word)
        game.ended_at = timezone.now()
        game.save()
        return game
    
    def add_guesses_to_game(self, game, guess_data):
        """Add multiple guesses to a game.
        
        Args:
            game: Game instance
            guess_data: List of tuples (word, pattern_string, attempt_number)
        """
        guesses = []
        for word, pattern_str, attempt_num in guess_data:
            pattern, _ = GuessResultPattern.objects.get_or_create(pattern=pattern_str)
            guess = Guess.objects.create(
                game=game,
                guessed_word=word,
                result_pattern=pattern,
                attempt_number=attempt_num
            )
            guesses.append(guess)
        return guesses
    
    def assert_game_state(self, game, expected_state):
        """Assert game is in expected state.
        
        Args:
            game: Game instance
            expected_state: Dict with keys like 'ended', 'word', 'guess_count'
        """
        if 'ended' in expected_state:
            if expected_state['ended']:
                self.assertIsNotNone(game.ended_at)
            else:
                self.assertIsNone(game.ended_at)
        
        if 'word' in expected_state:
            self.assertEqual(game.word_to_guess, expected_state['word'])
        
        if 'guess_count' in expected_state:
            self.assertEqual(game.guesses.count(), expected_state['guess_count'])


class FormTestMixin:
    """Mixin providing common form testing utilities."""
    
    def assert_form_valid(self, form_class, data):
        """Assert that form is valid with given data."""
        form = form_class(data=data)
        self.assertTrue(form.is_valid(), f"Form should be valid but got errors: {form.errors}")
        return form
    
    def assert_form_invalid(self, form_class, data, expected_errors=None):
        """Assert that form is invalid with given data."""
        form = form_class(data=data)
        self.assertFalse(form.is_valid(), "Form should be invalid")
        
        if expected_errors:
            for field in expected_errors:
                self.assertIn(field, form.errors, f"Expected error in field '{field}'")
        
        return form
    
    def assert_form_field_error(self, form, field_name, error_message_contains=None):
        """Assert that a specific form field has an error."""
        self.assertIn(field_name, form.errors)
        
        if error_message_contains:
            field_errors = str(form.errors[field_name])
            self.assertIn(error_message_contains, field_errors)


class APITestMixin:
    """Mixin providing common API testing utilities."""
    
    def assert_api_response(self, response, expected_status=200, expected_content=None):
        """Assert API response has expected status and content."""
        self.assertEqual(response.status_code, expected_status)
        
        if expected_content:
            if isinstance(expected_content, dict):
                response_data = response.json()
                for key, value in expected_content.items():
                    self.assertEqual(response_data.get(key), value)
            elif isinstance(expected_content, str):
                self.assertIn(expected_content.encode(), response.content)
    
    def make_api_request(self, method, url, data=None, content_type='application/json'):
        """Make an API request with proper formatting."""
        if method.upper() == 'POST':
            return self.client.post(url, data=data, content_type=content_type)
        elif method.upper() == 'PUT':
            import json
            return self.client.put(
                url, 
                data=json.dumps(data) if data else None, 
                content_type=content_type
            )
        elif method.upper() == 'GET':
            return self.client.get(url)
        elif method.upper() == 'DELETE':
            return self.client.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


class DatabaseTestMixin:
    """Mixin providing database testing utilities."""
    
    def assert_database_count(self, model_class, expected_count):
        """Assert that model has expected number of instances."""
        actual_count = model_class.objects.count()
        self.assertEqual(
            actual_count, 
            expected_count,
            f"Expected {expected_count} {model_class.__name__} instances, got {actual_count}"
        )
    
    def assert_instance_exists(self, model_class, **filter_kwargs):
        """Assert that an instance exists with given filters."""
        exists = model_class.objects.filter(**filter_kwargs).exists()
        self.assertTrue(
            exists,
            f"No {model_class.__name__} instance found with filters: {filter_kwargs}"
        )
    
    def assert_instance_does_not_exist(self, model_class, **filter_kwargs):
        """Assert that no instance exists with given filters."""
        exists = model_class.objects.filter(**filter_kwargs).exists()
        self.assertFalse(
            exists,
            f"{model_class.__name__} instance found with filters: {filter_kwargs}"
        )
