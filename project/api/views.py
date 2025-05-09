import json
import random

from django.http import HttpResponseBadRequest, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from api.models import Game, GameStatistics, Guess, GuessResultPattern

# Word list for the game
WORDS = [
    'LABAS', 'DIENA', 'NAMAS', 'MEILĖ', 'DUONA',
    'KATĖS', 'ŠALIS', 'GĖLĖS', 'LAIMĖ', 'ŽEMĖ',
    'SAULĖ', 'MĖNUO', 'VYRAS', 'KARTU', 'MEDIS',
    'ŠUNIS', 'KALBA', 'METAI', 'AKMUO', 'RANKA',
    'TALKA', 'DURYS', 'KNYGA', 'DRĄSA', 'LAPAS',
    'SODAS', 'GATVĖ', 'KELIO', 'VĖJAS', 'ŽODIS',
    'VAKAR', 'RYTAS', 'VAIKO', 'DARBO', 'ŠOKIS',
    'IDĖJA', 'VIETA', 'KODAS', 'GERAI'
]

def create_guess_result_pattern(guess, target_word):
    """Create a pattern for a guess result."""
    pattern = ['N'] * 5  # Initialize with all None
    target_letters = list(target_word.upper())
    guess_letters = list(guess.upper())
    
    # First pass: mark correct positions (G)
    for i in range(5):
        if guess_letters[i] == target_letters[i]:
            pattern[i] = 'G'
            target_letters[i] = None  # Mark as used
    
    # Second pass: mark wrong positions (Y)
    for i in range(5):
        if pattern[i] == 'N':  # Skip already marked positions
            if guess_letters[i] in target_letters:
                pattern[i] = 'Y'
                # Remove the first occurrence of this letter
                target_letters[target_letters.index(guess_letters[i])] = None
    
    return ''.join(pattern)

# TODO: switch everything to asynchronous
# /api/game/
@csrf_exempt
def handle_game_operations(request):
    if request.method == 'POST':
        try:
            # Select a random word from the list
            word = random.choice(WORDS)
            game = Game(word_to_guess=word)
            if request.user.is_authenticated:
                game.user = request.user
            game.save()

            return JsonResponse({
                'id': str(game.id),
                'word': game.word_to_guess
            })
        except Exception as e:
            return HttpResponseBadRequest(f"Failed to create game: {str(e)}")

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            if not data.get("id"):
                return HttpResponseBadRequest("No id provided PUT /api/game/")

            if data.get("isfinished"):
                end = timezone.now()
                # Get the game instance
                try:
                    with transaction.atomic():
                        game = Game.objects.get(id=data["id"])
                        if request.user.is_authenticated and not game.user:
                            game.user = request.user
                        
                        # Create the final guess if provided
                        if data.get("final_guess"):
                            pattern_str = create_guess_result_pattern(data["final_guess"], game.word_to_guess)
                            pattern, _ = GuessResultPattern.objects.get_or_create(pattern=pattern_str)
                            
                            # Get the next attempt number
                            next_attempt = game.guesses.count() + 1
                            
                            # Create the guess
                            Guess.objects.create(
                                game=game,
                                guessed_word=data["final_guess"],
                                result_pattern=pattern,
                                attempt_number=next_attempt
                            )
                        
                        game.ended_at = end
                        game.save(update_fields=['ended_at', 'user'])
                        
                        # Statistics are updated automatically by the signal
                except Game.DoesNotExist:
                    return HttpResponseBadRequest("Game not found")

            return HttpResponse(status=200)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON in request body")
        except Exception as e:
            return HttpResponseBadRequest(f"Failed to process request: {str(e)}")

    else:
        raise Http404("/api/game/")

@login_required
def get_statistics(request):
    """
    Get user's game statistics.
    """
    try:
        stats = GameStatistics.objects.get(user=request.user)
        win_percentage = (stats.games_won / stats.games_played * 100) if stats.games_played > 0 else 0
        
        return JsonResponse({
            'games_played': stats.games_played,
            'win_percentage': round(win_percentage, 1),
            'current_streak': stats.current_streak,
            'max_streak': stats.max_streak,
            'average_guesses': round(stats.average_guesses, 1)
        })
    except GameStatistics.DoesNotExist:
        return JsonResponse({
            'games_played': 0,
            'win_percentage': 0,
            'current_streak': 0,
            'max_streak': 0,
            'average_guesses': 0
        })