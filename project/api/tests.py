from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from api.models import Game, DictionaryWord, GameStatistics
import uuid
import json
import datetime


class GameTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(word_to_guess='tempo')
        self.game_url = reverse('handle_game_operations')

    def test_create_game(self):
        response = self.client.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(Game.objects.latest('created_at').word_to_guess, 'tempo')

    def test_update_game(self):
        # Create a game instance to update
        game = Game.objects.create(word_to_guess='tempo')

        # Update the game to set it as finished
        data = {
            'id': str(game.id),
            'isfinished': True
        }
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        # Refresh game from DB
        game.refresh_from_db()
        self.assertIsNotNone(game.ended_at)
        self.assertTrue(isinstance(game.ended_at, datetime.datetime))

    def test_update_game_no_id(self):
        data = {
            'isfinished': True
        }
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_method(self):
        response = self.client.get(self.game_url)
        self.assertEqual(response.status_code, 404)

    def test_game_creation_with_invalid_word(self):
        # Test creating a game with an empty word
        data = {'word_to_guess': ''}
        response = self.client.post(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_game_creation_with_valid_word(self):
        # Test creating a game with a valid word
        data = {'word_to_guess': 'valid'}
        response = self.client.post(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 2)


class DictionaryWordTestCase(TestCase):
    def setUp(self):
        self.word = DictionaryWord.objects.create(
            word_text='test',
            complexity=1
        )

    def test_word_creation(self):
        self.assertEqual(self.word.word_text, 'test')
        self.assertEqual(self.word.complexity, 1)

    def test_word_str_representation(self):
        self.assertEqual(str(self.word), 'test (complexity: 1)')

    def test_word_unique_constraint(self):
        # Try to create another word with the same text
        with self.assertRaises(Exception):
            DictionaryWord.objects.create(
                word_text='test',
                complexity=2
            )

    def test_word_min_length_validation(self):
        # Try to create a word with empty text
        with self.assertRaises(Exception):
            DictionaryWord.objects.create(
                word_text='',
                complexity=1
            )


class GameStatisticsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.stats = GameStatistics.objects.create(user=self.user)

    def test_statistics_creation(self):
        """Test that statistics are created correctly"""
        self.assertEqual(self.stats.games_played, 0)
        self.assertEqual(self.stats.games_won, 0)
        self.assertEqual(self.stats.current_streak, 0)
        self.assertEqual(self.stats.max_streak, 0)
        self.assertEqual(self.stats.average_guesses, 0.0)

    def test_update_statistics_win(self):
        """Test updating statistics after a win"""
        self.stats.update_statistics(won_game=True, guesses_count=4)
        
        self.assertEqual(self.stats.games_played, 1)
        self.assertEqual(self.stats.games_won, 1)
        self.assertEqual(self.stats.current_streak, 1)
        self.assertEqual(self.stats.max_streak, 1)
        self.assertEqual(self.stats.average_guesses, 4.0)

    def test_update_statistics_loss(self):
        """Test updating statistics after a loss"""
        self.stats.update_statistics(won_game=False)
        
        self.assertEqual(self.stats.games_played, 1)
        self.assertEqual(self.stats.games_won, 0)
        self.assertEqual(self.stats.current_streak, 0)
        self.assertEqual(self.stats.max_streak, 0)
        self.assertEqual(self.stats.average_guesses, 0.0)

    def test_streak_calculation(self):
        """Test streak calculation over multiple games"""
        # Win first game
        self.stats.update_statistics(won_game=True, guesses_count=3)
        self.assertEqual(self.stats.current_streak, 1)
        self.assertEqual(self.stats.max_streak, 1)

        # Win second game
        self.stats.update_statistics(won_game=True, guesses_count=4)
        self.assertEqual(self.stats.current_streak, 2)
        self.assertEqual(self.stats.max_streak, 2)

        # Lose third game
        self.stats.update_statistics(won_game=False)
        self.assertEqual(self.stats.current_streak, 0)
        self.assertEqual(self.stats.max_streak, 2)

        # Win fourth game
        self.stats.update_statistics(won_game=True, guesses_count=5)
        self.assertEqual(self.stats.current_streak, 1)
        self.assertEqual(self.stats.max_streak, 2)

    def test_average_guesses_calculation(self):
        """Test average guesses calculation"""
        # First win with 3 guesses
        self.stats.update_statistics(won_game=True, guesses_count=3)
        self.assertEqual(self.stats.average_guesses, 3.0)

        # Second win with 5 guesses
        self.stats.update_statistics(won_game=True, guesses_count=5)
        self.assertEqual(self.stats.average_guesses, 4.0)

        # Third win with 4 guesses
        self.stats.update_statistics(won_game=True, guesses_count=4)
        self.assertEqual(self.stats.average_guesses, 4.0)  # (3 + 5 + 4) / 3 = 4.0


class GameStatisticsSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_statistics_creation_on_user_creation(self):
        """Test that statistics are created when a new user is created"""
        self.assertTrue(GameStatistics.objects.filter(user=self.user).exists())
        stats = GameStatistics.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 0)
        self.assertEqual(stats.games_won, 0)

    def test_statistics_update_on_game_completion(self):
        """Test that statistics are updated when a game is completed"""
        # Create a game
        game = Game.objects.create(
            user=self.user,
            word_to_guess='test'
        )
        
        # Complete the game
        game.ended_at = datetime.datetime.now()
        game.save()

        # Get updated statistics
        stats = GameStatistics.objects.get(user=self.user)
        self.assertEqual(stats.games_played, 1)
