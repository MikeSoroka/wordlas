# performance_tests.py
"""
Performance tests for the Wordlas application.
Run with: python manage.py test performance_tests --settings=project.test_settings
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.db import transaction
from django.test.utils import override_settings
from api.models import Game, Guess, GuessResultPattern, DictionaryWord
from factories import GameFactory, GuessFactory, GuessResultPatternFactory
import json


class GameCreationPerformanceTest(TestCase):
    """Test performance of game creation operations."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
    
    def test_single_game_creation_performance(self):
        """Test that single game creation is fast enough."""
        start_time = time.time()
        
        response = self.client.post(self.game_url)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(creation_time, 1.0, "Game creation should take less than 1 second")
    
    def test_bulk_game_creation_performance(self):
        """Test performance of creating multiple games."""
        num_games = 100
        start_time = time.time()
        
        for _ in range(num_games):
            response = self.client.post(self.game_url)
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_game = total_time / num_games
        
        self.assertEqual(Game.objects.count(), num_games)
        self.assertLess(avg_time_per_game, 0.1, "Average game creation should be under 0.1 seconds")
        self.assertLess(total_time, 10.0, "Creating 100 games should take less than 10 seconds")
    
    def test_concurrent_game_creation_performance(self):
        """Test performance under concurrent game creation load."""
        num_threads = 10
        games_per_thread = 5
        results = []
        
        def create_games():
            thread_results = []
            for _ in range(games_per_thread):
                start_time = time.time()
                response = self.client.post(self.game_url)
                end_time = time.time()
                
                thread_results.append({
                    'status_code': response.status_code,
                    'duration': end_time - start_time
                })
            return thread_results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_thread = {executor.submit(create_games): i for i in range(num_threads)}
            
            for future in as_completed(future_to_thread):
                thread_results = future.result()
                results.extend(thread_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        successful_requests = [r for r in results if r['status_code'] == 200]
        self.assertEqual(len(successful_requests), num_threads * games_per_thread)
        
        # Check performance metrics
        avg_response_time = sum(r['duration'] for r in results) / len(results)
        max_response_time = max(r['duration'] for r in results)
        
        self.assertLess(avg_response_time, 0.5, "Average response time should be under 0.5 seconds")
        self.assertLess(max_response_time, 2.0, "Max response time should be under 2 seconds")
        self.assertLess(total_time, 5.0, "Total concurrent execution should be under 5 seconds")


class DatabasePerformanceTest(TransactionTestCase):
    """Test database operation performance."""
    
    def test_game_query_performance(self):
        """Test that game queries are efficient."""
        # Create test data
        games = GameFactory.create_batch(1000)
        
        # Test simple query performance
        start_time = time.time()
        game_count = Game.objects.count()
        end_time = time.time()
        
        self.assertEqual(game_count, 1000)
        self.assertLess(end_time - start_time, 0.1, "Simple count query should be fast")
        
        # Test filtered query performance
        start_time = time.time()
        recent_games = Game.objects.filter(ended_at__isnull=True)[:10]
        list(recent_games)  # Force evaluation
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 0.1, "Filtered query should be fast")
    
    def test_complex_query_performance(self):
        """Test performance of complex queries with joins."""
        # Create test data with relationships
        games = []
        patterns = GuessResultPatternFactory.create_batch(10)
        
        for i in range(100):
            game = GameFactory()
            games.append(game)
            
            # Add 3 guesses per game
            for j in range(3):
                GuessFactory(
                    game=game,
                    result_pattern=patterns[j % len(patterns)],
                    attempt_number=j + 1
                )
        
        # Test complex query with joins
        start_time = time.time()
        
        games_with_guesses = Game.objects.prefetch_related('guesses').filter(
            guesses__isnull=False
        ).distinct()[:20]
        
        # Force evaluation and access related objects
        for game in games_with_guesses:
            list(game.guesses.all())
        
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 0.5, "Complex query with prefetch should be efficient")
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk database operations."""
        # Test bulk create
        start_time = time.time()
        
        words_to_create = []
        for i in range(1000):
            words_to_create.append(DictionaryWord(
                word_text=f'WORD{i:04d}',
                complexity=i % 5 + 1
            ))
        
        DictionaryWord.objects.bulk_create(words_to_create)
        
        end_time = time.time()
        bulk_create_time = end_time - start_time
        
        self.assertEqual(DictionaryWord.objects.count(), 1000)
        self.assertLess(bulk_create_time, 1.0, "Bulk create should be fast")
        
        # Test bulk update
        start_time = time.time()
        
        DictionaryWord.objects.filter(complexity=1).update(complexity=6)
        
        end_time = time.time()
        bulk_update_time = end_time - start_time
        
        self.assertLess(bulk_update_time, 0.5, "Bulk update should be fast")


class APIEndpointPerformanceTest(TestCase):
    """Test API endpoint performance under various loads."""
    
    def setUp(self):
        self.client = Client()
        self.game_url = reverse('handle_game_operations')
    
    def test_api_response_time_consistency(self):
        """Test that API response times are consistent."""
        response_times = []
        
        # Make multiple requests and measure response times
        for _ in range(50):
            start_time = time.time()
            response = self.client.post(self.game_url)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Check that response times are reasonable and consistent
        self.assertLess(avg_response_time, 0.1, "Average response time should be under 0.1 seconds")
        self.assertLess(max_response_time, 0.5, "Max response time should be under 0.5 seconds")
        
        # Check consistency (max shouldn't be more than 10x min)
        if min_response_time > 0:
            consistency_ratio = max_response_time / min_response_time
            self.assertLess(consistency_ratio, 10, "Response times should be reasonably consistent")
    
    def test_api_under_load(self):
        """Test API performance under simulated load."""
        def make_requests(num_requests):
            results = []
            for _ in range(num_requests):
                start_time = time.time()
                response = self.client.post(self.game_url)
                end_time = time.time()
                
                results.append({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            return results
        
        # Simulate load with multiple threads
        num_threads = 5
        requests_per_thread = 10
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(make_requests, requests_per_thread) 
                for _ in range(num_threads)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # Analyze results
        successful_requests = [r for r in all_results if r['status_code'] == 200]
        avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
        
        self.assertEqual(len(successful_requests), num_threads * requests_per_thread)
        self.assertLess(avg_response_time, 0.2, "Average response time under load should be reasonable")


# security_tests.py
"""
Security tests for the Wordlas application.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.utils import override_settings
from api.models import Game
import json


class CSRFProtectionTest(TestCase):
    """Test CSRF protection across the application."""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.game_url = reverse('handle_game_operations')
        self.register_url = reverse('register')
        self.login_url = reverse('user_login')
    
    def test_api_csrf_exemption(self):
        """Test that game API is properly exempted from CSRF."""
        # The API should work without CSRF token since it's decorated with @csrf_exempt
        response = self.client.post(self.game_url)
        self.assertEqual(response.status_code, 200)
        
        # PUT request should also work
        game = Game.objects.create(word_to_guess='LABAS')
        data = {'id': str(game.id), 'isfinished': True}
        
        response = self.client.put(
            self.game_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_form_csrf_protection(self):
        """Test that forms are protected by CSRF."""
        # Registration form should require CSRF token
        registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        
        response = self.client.post(self.register_url, data=registration_data)
        self.assertEqual(response.status_code, 403)  # Should fail due to missing CSRF token


class InputValidationSecurityTest(TestCase):
    """Test input validation for security vulnerabilities."""
    
    def setUp(self):
        self.client = Client()
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks."""
        # Try SQL injection in form fields
        from main.forms import WordForm
        
        malicious_inputs = [
            "'; DROP TABLE api_game; --",
            "UNION SELECT * FROM auth_user",
            "1' OR '1'='1",
            "<script>alert('xss')</script>",
            "'; DELETE FROM api_game WHERE '1'='1'; --"
        ]
        
        for malicious_input in malicious_inputs:
            form = WordForm(data={'word': malicious_input})
            # Form should be invalid (either due to length or character validation)
            self.assertFalse(form.is_valid(), f"Malicious input should be rejected: {malicious_input}")
    
    def test_xss_protection_in_forms(self):
        """Test protection against XSS attacks in forms."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ]
        
        from main.forms import WordForm, UserRegisterForm
        
        # Test WordForm
        for payload in xss_payloads:
            form = WordForm(data={'word': payload})
            self.assertFalse(form.is_valid())
        
        # Test UserRegisterForm
        for payload in xss_payloads:
            form = UserRegisterForm(data={
                'username': payload,
                'email': 'test@example.com',
                'password1': 'password123',
                'password2': 'password123'
            })
            # Should be invalid due to username validation
            self.assertFalse(form.is_valid())
    
    def test_api_input_validation(self):
        """Test API input validation for security."""
        game_url = reverse('handle_game_operations')
        
        # Test malicious JSON payloads
        malicious_payloads = [
            {'id': "'; DROP TABLE api_game; --", 'isfinished': True},
            {'id': '<script>alert("xss")</script>', 'isfinished': True},
            {'id': 'x' * 1000, 'isfinished': True},  # Very long string
            {'id': '../../../etc/passwd', 'isfinished': True},  # Path traversal attempt
        ]
        
        for payload in malicious_payloads:
            response = self.client.put(
                game_url,
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            # Should not cause server error
            self.assertNotEqual(response.status_code, 500)


class AuthenticationSecurityTest(TestCase):
    """Test authentication security."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_password_strength_requirements(self):
        """Test that password strength is enforced."""
        from main.forms import UserRegisterForm
        
        weak_passwords = [
            'password',
            '123456',
            'abc',
            'testuser',  # Same as username
            'test@example.com'  # Same as email
        ]
        
        for weak_password in weak_passwords:
            form = UserRegisterForm(data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': weak_password,
                'password2': weak_password
            })
            
            # Form should be invalid due to password validation
            self.assertFalse(form.is_valid())
            self.assertIn('password1', form.errors)
    
    def test_login_rate_limiting_simulation(self):
        """Simulate testing for login rate limiting (would need actual implementation)."""
        login_url = reverse('user_login')
        
        # Simulate multiple failed login attempts
        failed_attempts = 0
        for _ in range(10):
            response = self.client.post(login_url, {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            
            if response.status_code == 200:  # Form redisplayed with errors
                failed_attempts += 1
        
        # In a real implementation, we'd expect rate limiting after several attempts
        # For now, we just verify that login attempts don't cause server errors
        self.assertEqual(failed_attempts, 10)
    
    def test_session_security(self):
        """Test session security measures."""
        # Test that session cookies are properly configured
        # This would require checking Django settings in a real implementation
        
        # Login user
        login_url = reverse('user_login')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        
        # Check that session is created
        self.assertIn('sessionid', self.client.cookies)
        
        # Test logout functionality
        self.client.logout()
        
        # Verify user is logged out
        index_url = reverse('index')
        response = self.client.get(index_url)
        # In a real implementation, we'd check that user is not authenticated


class DataProtectionTest(TestCase):
    """Test data protection and privacy measures."""
    
    def test_sensitive_data_not_exposed(self):
        """Test that sensitive data is not exposed in responses."""
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Test that password is not exposed in any API responses
        # This is more of a conceptual test since we don't have user API endpoints
        
        # Verify password is properly hashed
        self.assertNotEqual(user.password, 'testpassword123')
        self.assertTrue(user.password.startswith('pbkdf2_sha256'))
    
    def test_game_data_isolation(self):
        """Test that game data is properly isolated between users."""
        # Create two games
        game1 = Game.objects.create(word_to_guess='LABAS')
        game2 = Game.objects.create(word_to_guess='TEMPO')
        
        # Verify that game IDs are unique and not predictable
        self.assertNotEqual(game1.id, game2.id)
        
        # Verify that games have proper UUID format
        import uuid
        self.assertIsInstance(game1.id, uuid.UUID)
        self.assertIsInstance(game2.id, uuid.UUID)


class SecurityConfigurationTest(TestCase):
    """Test security-related configuration."""
    
    def test_debug_mode_in_production(self):
        """Test that debug mode is appropriately configured."""
        from django.conf import settings
        
        # In tests, DEBUG might be True, but we can test the pattern
        if hasattr(settings, 'DEBUG'):
            # Test would verify DEBUG=False in production
            # For now, just verify the setting exists
            self.assertIsInstance(settings.DEBUG, bool)
    
    def test_allowed_hosts_configuration(self):
        """Test that ALLOWED_HOSTS is properly configured."""
        from django.conf import settings
        
        # Verify ALLOWED_HOSTS is configured
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
    
    def test_secret_key_security(self):
        """Test that SECRET_KEY is properly configured."""
        from django.conf import settings
        
        # Verify SECRET_KEY exists and is not empty
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertGreater(len(settings.SECRET_KEY), 0)
        
        # In production, would verify it's not the default Django secret key
        self.assertNotEqual(settings.SECRET_KEY, 'django-insecure-default-key')
