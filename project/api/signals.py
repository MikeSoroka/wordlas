from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
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
    if not created and instance.ended_at and instance.user:
        # Get or create statistics for the user
        stats, _ = GameStatistics.objects.get_or_create(user=instance.user)
        
        # Calculate if the game was won (you'll need to implement this logic)
        won_game = instance.is_won()  # You need to implement this method in Game model
        guesses_count = instance.guesses_count()  # You need to implement this method in Game model
        
        # Update statistics
        stats.update_statistics(won_game=won_game, guesses_count=guesses_count) 