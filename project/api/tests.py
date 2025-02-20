from django.test import TestCase, Client
from django.urls import reverse
from api.models import Game
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
