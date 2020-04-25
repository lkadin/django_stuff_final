from django.apps import AppConfig
from django.contrib import admin
import pytest
class CoupConfig(AppConfig):
    name = 'coup'

from coup.admin import Player

# from coup.models import Player
# from coup.models import Game

# print('__file__={0:<35} | __name__={1:<25} | __package__={2:<25}'.format(__file__,__name__,str(__package__)))

# @pytest.mark.django_db
def test_my_user():
    player = Player.coins
    assert player == 2
