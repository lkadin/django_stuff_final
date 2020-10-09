import requests
import responses

from coup.models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory
from coup.action import get_allowed_actions, take_action, get_initial_action_data
from coup.views import startgame, actions
from django.test import TestCase, Client
from django.urls import reverse


class GameModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        game = Game(id=1,
                    NUM_OF_CARDS=2)

        ActionHistory.objects.all().delete()
        Card.objects.all().delete()
        Action.objects.all().delete()
        game.add_all_actions()
        game.add_all_cards()
        game.del_card_instances()
        game.build_cards()
        deck = Deck(id=1)
        deck.save()
        deck.build()
        # deck.shuffle()
        deck.save()
        Player.objects.all().delete()

        # todo:replace with lobby /login
        game.in_progress = True
        # game.add_all_players()
        player = Player(playerName="Lee", playerNumber=0)
        player.save()
        player = Player(playerName="Adina", playerNumber=1)
        player.save()
        player = Player(playerName="Sam", playerNumber=2)
        player.save()
        # player = Player(playerName="Jamie", playerNumber=3)
        # player.save()
        game.initialDeal()
        game.number_of_players = len(Player.objects.all())
        game.save()

    def test_get_allowed_actions(self):
        # No challenge at startup
        startgame(None)
        game = Game.objects.all()[0]
        game.initialDeal()
        game.whoseTurn == 0
        game.save()
        player1 = Player.objects.all()[0]
        allowed_actions = get_allowed_actions(game, player1.playerName, player1.coins)
        assert 'Challenge' not in allowed_actions

        # block steal and challenge after steal for challenger
        player2 = Player.objects.all()[1]
        game.steal(player1, player2)
        action_history = ActionHistory(name='Steal', player1=player1, player2=player2,
                                       challenge_winner=None, challenge_loser=None)
        action_history.save()
        game.next_turn()
        game.save()
        allowed_actions = [action.name for action in get_allowed_actions(game, player2.playerName, player2.coins)]
        assert 'Block Steal' in allowed_actions
        assert 'Challenge' in allowed_actions

        # no options if not your turn
        allowed_actions = [action.name for action in get_allowed_actions(game, player1.playerName, player1.coins)]
        assert allowed_actions == []

        # challenge only after block steal from challenger
        game.block_steal(player2)
        game.save()
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]
        action_history = ActionHistory(name='Block Steal', player1=player2, player2=player1,
                                       challenge_winner=None, challenge_loser=None)
        action_history.save()
        game.next_turn()
        game.save()
        allowed_actions = [action.name for action in get_allowed_actions(game, player1.playerName, player1.coins)]
        assert 'Challenge' in allowed_actions
        assert len(allowed_actions) == 1
        game = Game.objects.all()[0]

        # No challenge for player that blocked the steal
        allowed_actions = [action.name for action in get_allowed_actions(game, player2.playerName, player2.coins)]
        print("ALLOWED******************************", allowed_actions)
        assert 'Challenge' not in allowed_actions

    @responses.activate
    def test_simulate_data_cannot_be_found(self):
        responses.add(
            responses.GET,
            "http://api.zippopotam.us/us/90210",
            json={"error": "No data exists for US zip code 90210", "method": 'GET'},
            status=404
        )
        response = requests.get("http://api.zippopotam.us/us/90210")
        assert response.status_code == 404
        response_body = response.json()
        assert response_body["error"] == "No data exists for US zip code 90210"
        # get_initial_action_data(response.request)

    def test_take_action(self):
        game = Game.objects.first()
        number = game.whoseTurn
        player = Player.objects.get(playerNumber=number)
        print (player.coins)
        name = player.playerName
        resp = self.client.post('/coup/actions', {'action': 'Income', 'playerName': name})
        assert resp.status_code == 302
        player = Player.objects.get(playerNumber=number)
        print(player.coins)
