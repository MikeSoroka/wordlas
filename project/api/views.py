import json

from django.http import HttpResponseBadRequest, Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt

from api.models import Game

# TODO: switch everything to asynchronous
# /api/game/
@csrf_exempt
def handle_game_operations(request):
    if request.method == 'POST':
        word = "tempo" #TODO: change to word from dict
        game = Game(word_to_guess=word)
        game.save()

        return HttpResponse(status=200)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("id"):
            id = data.get("id")
        else:
            return HttpResponseBadRequest("No id provided PUT /api/game/")

        if data.get("isfinished"):
            end = timezone.now()

        Game.objects.filter(id=id).update(ended_at=end)

        return HttpResponse(status=200)

    else:
        raise Http404("/api/game/")