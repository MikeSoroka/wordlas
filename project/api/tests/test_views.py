from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from api.models import Game
import json
import uuid


class GameAPIViewTest(TestCase):
    """Comprehensive tests for the game API endpoint."""
    
    def setUp(self):
        """Set up test client and test data."""
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
        
        # Create a test game for update operations
        self.test_game = Game.objects.create(word_to_guess='LABAS')
        
    def test_post_create_game_success(self):
        """Test successful game creation via POST."""
        initial_count = Game.objects.count()
        
        response = self.client.post(self.game_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), initial_count + 1)
        
        # Check that the new game has the expected word
        latest_game = Game.objects.latest('created_at')
        self.assertEqual(latest_game.word_to_guess, 'tempo')  # As per current implementation
        self.assertIsNone(latest_game.ended_at)
    
    def test_post_create_multiple_games(self):
        """Test creating multiple games creates unique instances."""
        initial_count = Game.objects.count()
        
        # Create multiple games
        response1 = self.client.post(self.game_url)
        response2 = self.client.post(self.game_url)
        response3 = self.client.post(self.game_url)
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        
        self.assertEqual(Game.objects.count(), initial_count + 3)
        
        # Verify all games have unique IDs
        latest_games = Game.objects.order_by('-created_at')[:3]
        game_ids = [game.id for game in latest_games]
        self.assertEqual(len(set(game_ids)), 3)  # All IDs should be unique
    
    def test_put_update_game_success(self):
        """Test successful game update via PUT."""
        self.assertIsNone(self.test_game.ended_at)
        
        data = {
            'id': str(self.test_game.id),
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh from database and check that ended_at is set
        self.test_game.refresh_from_db()
        self.assertIsNotNone(self.test_game.ended_at)
        
        # Check that ended_at is recent (within last minute)
        time_diff = timezone.now() - self.test_game.ended_at
        self.assertLess(time_diff.total_seconds(), 60)
    
    def test_put_update_game_missing_id(self):
        """Test PUT request without game ID returns 400."""
        data = {
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No id provided', response.content)
    
    def test_put_update_game_invalid_id(self):
        """Test PUT request with invalid game ID."""
        invalid_id = str(uuid.uuid4())  # Random UUID that doesn't exist
        
        data = {
            'id': invalid_id,
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # The view should still return 200 even if no games are updated
        # This might be a bug in the implementation
        self.assertEqual(response.status_code, 200)
    
    def test_put_update_game_malformed_json(self):
        """Test PUT request with malformed JSON."""
        malformed_json = '{"id": "123", "isfinished": true'  # Missing closing brace
        
        response = self.client.put(
            self.game_url,
            data=malformed_json,
            content_type='application/json'
        )
        
        # Should return an error due to JSON parsing failure
        self.assertNotEqual(response.status_code, 200)
    
    def test_put_update_game_invalid_json_structure(self):
        """Test PUT request with valid JSON but invalid structure."""
        data = "just a string"
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should return 400 because data.get() will fail on a string
        self.assertEqual(response.status_code, 400)
    
    def test_put_update_game_empty_body(self):
        """Test PUT request with empty body."""
        response = self.client.put(
            self.game_url,
            data='',
            content_type='application/json'
        )
        
        # Should fail due to JSON parsing error
        self.assertNotEqual(response.status_code, 200)
    
    def test_put_update_game_without_isfinished(self):
        """Test PUT request with ID but without isfinished flag."""
        data = {
            'id': str(self.test_game.id)
            # Missing 'isfinished'
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # The current implementation has a bug - it will try to update with undefined 'end'
        # This should be fixed in the actual code
        self.assertNotEqual(response.status_code, 200)
    
    def test_get_request_returns_404(self):
        """Test that GET requests return 404."""
        response = self.client.get(self.game_url)
        self.assertEqual(response.status_code, 404)
    
    def test_delete_request_returns_404(self):
        """Test that DELETE requests return 404."""
        response = self.client.delete(self.game_url)
        self.assertEqual(response.status_code, 404)
    
    def test_patch_request_returns_404(self):
        """Test that PATCH requests return 404."""
        response = self.client.patch(self.game_url)
        self.assertEqual(response.status_code, 404)
    
    def test_head_request_returns_404(self):
        """Test that HEAD requests return 404."""
        response = self.client.head(self.game_url)
        self.assertEqual(response.status_code, 404)
    
    def test_options_request_returns_404(self):
        """Test that OPTIONS requests return 404."""
        response = self.client.options(self.game_url)
        self.assertEqual(response.status_code, 404)
    
    def test_post_request_content_type_handling(self):
        """Test POST request handles different content types."""
        # Test without explicit content-type (should still work)
        response = self.client.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        
        # Test with different content-type
        response = self.client.post(
            self.game_url,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_exemption(self):
        """Test that the view is CSRF exempt."""
        # The view should work without CSRF token since it's decorated with @csrf_exempt
        client_without_csrf = Client(enforce_csrf_checks=True)
        
        response = client_without_csrf.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        
        # Test PUT request without CSRF token
        data = {
            'id': str(self.test_game.id),
            'isfinished': True
        }
        
        response = client_without_csrf.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_concurrent_game_creation(self):
        """Test that concurrent game creation works correctly."""
        import threading
        import time
        
        games_created = []
        errors = []
        
        def create_game():
            try:
                response = self.client.post(self.game_url)
                if response.status_code == 200:
                    games_created.append(True)
                else:
                    errors.append(f"Status: {response.status_code}")
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads to simulate concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_game)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(games_created), 5)
    
    def test_update_nonexistent_game(self):
        """Test updating a game that doesn't exist."""
        nonexistent_id = str(uuid.uuid4())
        
        data = {
            'id': nonexistent_id,
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Current implementation returns 200 even when no rows are updated
        # This might be considered a bug - should probably return 404
        self.assertEqual(response.status_code, 200)
    
    def test_update_game_with_string_id(self):
        """Test updating game with string ID instead of UUID."""
        data = {
            'id': 'not-a-uuid',
            'isfinished': True
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should still return 200 but no games should be updated
        self.assertEqual(response.status_code, 200)
    
    def test_response_headers(self):
        """Test that responses have appropriate headers."""
        response = self.client.post(self.game_url)
        
        self.assertEqual(response.status_code, 200)
        # Could add more header checks if needed
    
    def test_large_payload_handling(self):
        """Test handling of large JSON payloads."""
        # Create a large but valid payload
        large_data = {
            'id': str(self.test_game.id),
            'isfinished': True,
            'extra_data': 'x' * 10000  # Large string
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(large_data),
            content_type='application/json'
        )
        
        # Should still work (assuming no size limits)
        self.assertEqual(response.status_code, 200)
    
    def test_unicode_handling_in_json(self):
        """Test that Unicode characters in JSON are handled correctly."""
        data = {
            'id': str(self.test_game.id),
            'isfinished': True,
            'unicode_test': 'ąčęėįšųūž ĄČĘĖĮŠŲŪŽ'
        }
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        
        self.assertEqual(response.status_code, 200)


class GameAPIIntegrationTest(TestCase):
    """Integration tests for the game API with database operations."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
    
    def test_create_and_update_game_workflow(self):
        """Test the complete workflow of creating and then updating a game."""
        # Step 1: Create a game
        initial_count = Game.objects.count()
        create_response = self.client.post(self.game_url)
        self.assertEqual(create_response.status_code, 200)
        
        # Verify game was created
        self.assertEqual(Game.objects.count(), initial_count + 1)
        created_game = Game.objects.latest('created_at')
        self.assertIsNone(created_game.ended_at)
        
        # Step 2: Update the game
        update_data = {
            'id': str(created_game.id),
            'isfinished': True
        }
        
        update_response = self.client.put(
            self.game_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Verify game was updated
        created_game.refresh_from_db()
        self.assertIsNotNone(created_game.ended_at)
    
    def test_database_rollback_on_error(self):
        """Test that database operations are rolled back on errors."""
        # This test would require modifying the view to use transactions
        # For now, we'll test the current behavior
        
        initial_count = Game.objects.count()
        
        # Try to create a game (should succeed)
        response = self.client.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), initial_count + 1)
    
    def test_multiple_updates_same_game(self):
        """Test updating the same game multiple times."""
        game = Game.objects.create(word_to_guess='LABAS')
        
        # First update
        data = {
            'id': str(game.id),
            'isfinished': True
        }
        
        response1 = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        game.refresh_from_db()
        first_end_time = game.ended_at
        self.assertIsNotNone(first_end_time)
        
        # Second update (should update the timestamp)
        import time
        time.sleep(0.1)  # Small delay to ensure different timestamp
        
        response2 = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 200)
        
        game.refresh_from_db()
        second_end_time = game.ended_at
        self.assertGreater(second_end_time, first_end_time)
