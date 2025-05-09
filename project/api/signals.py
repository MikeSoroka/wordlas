from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from .models import Game, GameStatistics


@receiver(post_save, sender=User)
def create_user_statistics(sender, instance, created, **kwargs):
    """
    Create GameStatistics when a new user is created.
    """
    if created:
        GameStatistics.objects.create(user=instance)


@receiver(post_save, sender=Game)
def update_game_statistics(sender, instance, created, **kwargs):
    """
    Update user statistics when a game is completed.
    """
    # Only process if:
    # 1. This is an update (not creation)
    # 2. The game has ended
    # 3. The game has a user
    if not created and instance.ended_at and instance.user:
        try:
            with transaction.atomic():
                # Get or create statistics for the user
                stats, _ = GameStatistics.objects.get_or_create(user=instance.user)
                
                # Calculate if the game was won
                won_game = instance.is_won()
                guesses_count = instance.guesses_count()
                
                # Update statistics
                stats.update_statistics(won_game=won_game, guesses_count=guesses_count)
        except Exception as e:
            # Log the error but don't raise it to prevent signal failure
            print(f"Error updating statistics for game {instance.id}: {str(e)}") 