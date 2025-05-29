from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from api.models import Game, GuessResultPattern, Guess, DictionaryWord
from main.forms import WordForm, UserRegisterForm
import json


class GameFlowIntegrationTest(TestCase):
    """Integration tests for complete game flow."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
        self.index_url = reverse('index')
        
        # Create test patterns
        self.green_pattern = GuessResultPattern.objects.create(pattern="GGGGG")
        self.mixed_pattern = GuessResultPattern.objects.create(pattern="GYNGN")
        
    def test_complete_game_creation_and_guess_flow(self):
        """Test creating a game and adding guesses through the full flow."""
        # Step 1: Create a game
        create_response = self.client.post(self.game_url)
        self.assertEqual(create_response.status_code, 200)
        
        # Get the created game
        game = Game.objects.latest('created_at')
        self.assertEqual(game.word_to_guess, 'tempo')
        
        # Step 2: Add some guesses to the game
        guess1 = Guess.objects.create(
            game=game,
            guessed_word="LABAS",
            result_pattern=self.mixed_pattern,
            attempt_number=1
        )
        
        guess2 = Guess.objects.create(
            game=game,
            guessed_word="TEMPO",
            result_pattern=self.green_pattern,
            attempt_number=2
        )
        
        # Step 3: Verify game state
        self.assertEqual(game.guesses.count(), 2)
        self.assertEqual(game.guesses.first(), guess1)  # Ordered by attempt_number
        self.assertEqual(game.guesses.last(), guess2)
        
        # Step 4: End the game
        end_data = {
            'id': str(game.id),
            'isfinished': True
        }
        
        end_response = self.client.put(
            self.game_url,
            data=json.dumps(end_data),
            content_type='application/json'
        )
        
        self.assertEqual(end_response.status_code, 200)
        
        # Verify game is ended
        game.refresh_from_db()
        self.assertIsNotNone(game.ended_at)
    
    def test_multiple_games_with_guesses(self):
        """Test creating multiple games and adding guesses to each."""
        games = []
        
        # Create 3 games
        for i in range(3):
            response = self.client.post(self.game_url)
            self.assertEqual(response.status_code, 200)
            game = Game.objects.latest('created_at')
            games.append(game)
        
        # Add guesses to each game
        for i, game in enumerate(games):
            for attempt in range(1, 4):  # 3 guesses per game
                Guess.objects.create(
                    game=game,
                    guessed_word=f"WORD{attempt}",
                    result_pattern=self.mixed_pattern,
                    attempt_number=attempt
                )
        
        # Verify each game has 3 guesses
        for game in games:
            self.assertEqual(game.guesses.count(), 3)
            
        # Verify total guess count
        self.assertEqual(Guess.objects.count(), 9)
        
        # End all games
        for game in games:
            end_data = {
                'id': str(game.id),
                'isfinished': True
            }
            
            response = self.client.put(
                self.game_url,
                data=json.dumps(end_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Verify all games are ended
        for game in games:
            game.refresh_from_db()
            self.assertIsNotNone(game.ended_at)


class UserAuthenticationIntegrationTest(TestCase):
    """Integration tests for user authentication flow."""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('user_login')
        self.index_url = reverse('index')
        
    def test_complete_user_registration_and_login_flow(self):
        """Test registering a new user and then logging in."""
        # Step 1: Register a new user
        registration_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        
        register_response = self.client.post(self.register_url, data=registration_data)
        
        # Should redirect to index after successful registration
        self.assertEqual(register_response.status_code, 302)
        self.assertEqual(register_response.url, reverse('index'))
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        
        # Step 2: Log out (simulate user logging out)
        self.client.logout()
        
        # Step 3: Log in with the created user
        login_data = {
            'username': 'testuser',
            'password': 'complexpassword123'
        }
        
        login_response = self.client.post(self.login_url, data=login_data)
        
        # Should redirect to index after successful login
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse('index'))
        
        # Step 4: Verify user is authenticated
        # Make a request to index and check that user is logged in
        index_response = self.client.get(self.index_url)
        self.assertEqual(index_response.status_code, 200)
        
        # Check that the user is in the request context (if available)
        if hasattr(index_response, 'context') and index_response.context:
            self.assertTrue(index_response.context['user'].is_authenticated)
    
    def test_login_with_invalid_credentials(self):
        """Test login attempt with invalid credentials."""
        # Create a user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='correctpassword'
        )
        
        # Try to login with wrong password
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data=login_data)
        
        # Should not redirect (stays on login page)
        self.assertEqual(response.status_code, 200)
        
        # Should contain error message
        self.assertContains(response, 'Invalid username or password')
    
    def test_registration_with_existing_email(self):
        """Test registration attempt with already used email."""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )
        
        # Try to register with same email
        registration_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        
        response = self.client.post(self.register_url, data=registration_data)
        
        # Should not redirect (stays on registration page)
        self.assertEqual(response.status_code, 200)
        
        # Should contain error message
        self.assertContains(response, 'Email address already in use')
        
        # New user should not be created
        self.assertFalse(User.objects.filter(username='newuser').exists())


class FormAndViewIntegrationTest(TestCase):
    """Integration tests for forms working with views."""
    
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        
    def test_word_form_in_index_view(self):
        """Test that WordForm is properly integrated in the index view."""
        response = self.client.get(self.index_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'word-input')  # CSS class from WordForm
        self.assertContains(response, 'Įveskite 5 raidžių žodį')  # Placeholder text
        
        # Check that form is in context
        if hasattr(response, 'context'):
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], WordForm)
    
    def test_word_form_post_to_index(self):
        """Test posting word form data to index view."""
        # Test with valid Lithuanian word
        valid_data = {'word': 'LABAS'}
        response = self.client.post(self.index_url, data=valid_data)
        
        # Should process successfully
        self.assertEqual(response.status_code, 200)
        
        # Test with invalid word
        invalid_data = {'word': 'HELLO'}
        response = self.client.post(self.index_url, data=invalid_data)
        
        # Should still return 200 but with form errors
        self.assertEqual(response.status_code, 200)
        if hasattr(response, 'context') and 'form' in response.context:
            form = response.context['form']
            self.assertFalse(form.is_valid())


class DatabaseIntegrationTest(TestCase):
    """Integration tests for database operations across models."""
    
    def test_cascade_deletion_integrity(self):
        """Test that cascade deletions maintain database integrity."""
        # Create a game
        game = Game.objects.create(word_to_guess="LABAS")
        
        # Create patterns
        pattern1 = GuessResultPattern.objects.create(pattern="GYNGN")
        pattern2 = GuessResultPattern.objects.create(pattern="NNNNN")
        
        # Create guesses
        guess1 = Guess.objects.create(
            game=game,
            guessed_word="FIRST",
            result_pattern=pattern1,
            attempt_number=1
        )
        guess2 = Guess.objects.create(
            game=game,
            guessed_word="SECND",
            result_pattern=pattern2,
            attempt_number=2
        )
        
        # Verify initial state
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(GuessResultPattern.objects.count(), 2)
        self.assertEqual(Guess.objects.count(), 2)
        
        # Delete the game - should cascade to guesses
        game.delete()
        
        # Verify guesses are deleted but patterns remain
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(GuessResultPattern.objects.count(), 2)  # Protected from deletion
        self.assertEqual(Guess.objects.count(), 0)  # Cascade deleted
    
    def test_pattern_protection_from_deletion(self):
        """Test that patterns with associated guesses cannot be deleted."""
        # Create game and pattern
        game = Game.objects.create(word_to_guess="LABAS")
        pattern = GuessResultPattern.objects.create(pattern="GYNGN")
        
        # Create guess that references the pattern
        guess = Guess.objects.create(
            game=game,
            guessed_word="GUESS",
            result_pattern=pattern,
            attempt_number=1
        )
        
        # Try to delete the pattern - should be protected
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            pattern.delete()
        
        # Pattern and guess should still exist
        self.assertTrue(GuessResultPattern.objects.filter(id=pattern.id).exists())
        self.assertTrue(Guess.objects.filter(id=guess.id).exists())
    
    def test_dictionary_word_uniqueness_across_operations(self):
        """Test dictionary word uniqueness during various operations."""
        # Create initial word
        word1 = DictionaryWord.objects.create(
            word_text="UNIQUE",
            complexity=3
        )
        
        # Try to create duplicate
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DictionaryWord.objects.create(
                    word_text="UNIQUE",
                    complexity=5
                )
        
        # Original word should still exist
        self.assertTrue(DictionaryWord.objects.filter(id=word1.id).exists())
        self.assertEqual(DictionaryWord.objects.filter(word_text="UNIQUE").count(), 1)
        
        # Create word with different text should work
        word2 = DictionaryWord.objects.create(
            word_text="DIFFERENT",
            complexity=2
        )
        
        self.assertEqual(DictionaryWord.objects.count(), 2)


class APIAndDatabaseIntegrationTest(TestCase):
    """Integration tests for API operations with database consistency."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
    
    def test_api_operations_maintain_database_consistency(self):
        """Test that API operations maintain database consistency."""
        initial_game_count = Game.objects.count()
        
        # Create multiple games via API
        for i in range(5):
            response = self.client.post(self.game_url)
            self.assertEqual(response.status_code, 200)
        
        # Verify all games were created
        self.assertEqual(Game.objects.count(), initial_game_count + 5)
        
        # Get all created games
        games = Game.objects.order_by('-created_at')[:5]
        
        # Update each game via API
        for game in games:
            update_data = {
                'id': str(game.id),
                'isfinished': True
            }
            
            response = self.client.put(
                self.game_url,
                data=json.dumps(update_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # Verify all games are marked as ended
        for game in games:
            game.refresh_from_db()
            self.assertIsNotNone(game.ended_at)
        
        # Verify database consistency
        ended_games = Game.objects.filter(ended_at__isnull=False)
        self.assertGreaterEqual(ended_games.count(), 5)
    
    def test_concurrent_api_operations(self):
        """Test that concurrent API operations don't cause database issues."""
        import threading
        
        results = []
        errors = []
        
        def create_and_update_game():
            try:
                # Create game
                create_response = self.client.post(self.game_url)
                if create_response.status_code != 200:
                    errors.append(f"Create failed: {create_response.status_code}")
                    return
                
                # Get the created game
                game = Game.objects.latest('created_at')
                
                # Update game
                update_data = {
                    'id': str(game.id),
                    'isfinished': True
                }
                
                update_response = self.client.put(
                    self.game_url,
                    data=json.dumps(update_data),
                    content_type='application/json'
                )
                
                if update_response.status_code == 200:
                    results.append(game.id)
                else:
                    errors.append(f"Update failed: {update_response.status_code}")
                    
            except Exception as e:
                errors.append(str(e))
        
        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_and_update_game)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 3)
        
        # Verify all games are in database and properly updated
        for game_id in results:
            game = Game.objects.get(id=game_id)
            self.assertIsNotNone(game.ended_at)


class ThemeIntegrationTest(TestCase):
    """Integration tests for theme functionality."""
    
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
    
    def test_theme_context_processor(self):
        """Test that theme context processor works with views."""
        # Test default theme (light)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        
        if hasattr(response, 'context'):
            self.assertIn('theme', response.context)
            self.assertEqual(response.context['theme'], 'light')
        
        # Test with dark theme cookie
        self.client.cookies['theme'] = 'dark'
        response = self.client.get(self.index_url)
        
        if hasattr(response, 'context'):
            self.assertEqual(response.context['theme'], 'dark')
    
    def test_theme_in_template_rendering(self):
        """Test that theme is properly used in template rendering."""
        # Test light theme
        response = self.client.get(self.index_url)
        self.assertNotContains(response, 'data-theme="dark"')
        
        # Test dark theme
        self.client.cookies['theme'] = 'dark'
        response = self.client.get(self.index_url)
        self.assertContains(response, 'data-theme="dark"')
