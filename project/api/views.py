import json

from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import render
import datetime

from django.views.decorators.csrf import csrf_exempt

from project.api.models import Game

# TODO: switch everything to asynchronous
# /api/game/
@csrf_exempt
def handle_game_operations(request):
    if request.method == 'POST':
        word = "tempo" #TODO: change to word from dict
        game = Game(word=word)
        game.save()

    elif request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("id"):
            id = data.get("id")
        else:
            raise HttpResponseBadRequest("No id provided PUT /api/game/")

        if data.get("isfinished"):
            end = datetime.datetime.now()

        Game.objects.filter(id=id).update(ended_at=end)

    else:
        raise Http404("/api/game/")