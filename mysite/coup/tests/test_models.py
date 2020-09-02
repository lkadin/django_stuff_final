from django.test import TestCase
import requests
import requests_mock

# Create your tests here.
from coup.models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory
from coup.action import get_allowed_actions
from coup.views import startgame


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

    def test_initial_deal(self):
        player = Player.objects.all()[0]
        deck = Deck(id=1)
        self.assertEqual(deck.cards_remaining(), 15 - len(Player.objects.all()) * 2)
        self.assertEqual(CardInstance.objects.all().count(), 15)
        self.assertEqual(Player.objects.all().count(), len(Player.objects.all()))
        self.assertEqual(player.cardcount(), 2)
        self.assertEqual(player.influence(), 2)

    # def test_get_allowed_actions(self):
    #     # No challenge at startup
    #     startgame(None)
    #     game = Game.objects.all()[0]
    #     game.initialDeal()
    #     game.whoseTurn == 0
    #     game.save()
    #     player1 = Player.objects.all()[0]
    #     allowed_actions = get_allowed_actions(game, player1.playerName, player1.coins)
    #     assert 'Challenge' not in allowed_actions
    #
    #     # block steal and challenge after steal for challenger
    #     player2 = Player.objects.all()[1]
    #     game.steal(player1, player2)
    #     action_history = ActionHistory(name='Steal', player1=player1, player2=player2,
    #                                    challenge_winner=None, challenge_loser=None)
    #     action_history.save()
    #     game.next_turn()
    #     game.save()
    #     allowed_actions = [action.name for action in get_allowed_actions(game, player2.playerName, player2.coins)]
    #     assert 'Block Steal' in allowed_actions
    #     assert 'Challenge' in allowed_actions
    #
    #     # no options if not your turn
    #     allowed_actions = [action.name for action in get_allowed_actions(game, player1.playerName, player1.coins)]
    #     assert allowed_actions == []
    #
    #     # challenge only after block steal from challenger
    #     game.block_steal(player2)
    #     game.save()
    #     action_history = ActionHistory(name='Block Steal', player1=player2, player2=player1,
    #                                    challenge_winner=None, challenge_loser=None)
    #     action_history.save()
    #     game.next_turn()
    #     game.save()
    #     allowed_actions = [action.name for action in get_allowed_actions(game, player1.playerName, player1.coins)]
    #     assert 'Challenge' in allowed_actions
    #     assert len(allowed_actions) == 1
    #
    #     # No challenge for player that blocked the steal
    #     allowed_actions = [action.name for action in get_allowed_actions(game, player2.playerName, player2.coins)]
    #     print("ALLOWED******************************", allowed_actions)
    #     assert 'Challenge' not in allowed_actions

    def test_lose_coins(self):
        player = Player.objects.all()[0]
        player.lose_coins(2)
        self.assertEqual(player.coins, 0)

    def test_add_coins(self):
        player = Player.objects.all()[0]
        player.add_coins(3)
        self.assertEqual(player.coins, 5)

    def test_draw_2_cards(self):
        player = Player.objects.all()[0]
        player.draw(2)
        self.assertEqual(player.cardcount(), 4)

    def test_discard(self):
        player = Player.objects.all()[0]
        cards = player.hand.all()
        player.discard(cards[0])
        self.assertEqual(player.cardcount(), 1)
        player.discard(cards[0])
        self.assertEqual(player.cardcount(), 0)

    def test_lose_influence(self):
        player = Player.objects.all()[0]
        cards = player.hand.all()
        player.lose_influence(cards[0].card.cardName)
        self.assertEqual(player.influence(), 1)

    def test_lose_last_card(self):
        player = Player.objects.all()[0]
        game = Game.objects.all()[0]
        game.current_action = 'Challenge'
        game.challenge_loser = player.playerName
        game.current_player1 = player.playerName
        game.save()
        cards = player.hand.all()
        player.discard(cards[0])
        player.lose_last_card()
        self.assertEqual(player.influence(), 0)

    def test_draw_and_discard_after_lose_influence(self):
        player = Player.objects.all()[0]
        player.draw(2)
        self.assertEqual(player.cardcount(), 4)
        self.assertEqual(player.hand.filter(status='D').count(), 4)
        player.discard(player.hand.filter(status='D')[0])
        self.assertEqual(player.hand.filter(status='D').count(), 3)
        player.discard(player.hand.filter(status='D')[0])
        self.assertEqual(player.hand.filter(status='D').count(), 2)
        self.assertEqual(player.cardcount(), 2)

    def test_swap_card(self):
        player = Player.objects.all()[0]
        cards = player.hand.all()
        card_to_swap = player.hand.filter(status='D')[0]
        player.swap(card_to_swap)
        new_cards_in_hand = player.hand.all()
        self.assertEqual(len(cards), len(new_cards_in_hand))

    def test_next_turn(self):
        game = Game.objects.all()[0]
        next_turn = game.whoseTurn + 1
        game.next_turn()
        self.assertEqual(game.whoseTurn, next_turn)

    def test_foreign_aid(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        game.take_foreign_aid(player)
        self.assertEqual(player.coins, 4)

    def test_check_winner(self):
        game = Game.objects.all()[0]
        self.assertEqual(game.ck_winner(), None)
        players = Player.objects.all()
        for player in players[1:]:
            for card in player.hand.all():
                player.lose_influence(card)
        self.assertEqual(game.ck_winner(), 'Lee')

    def test_income(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        game.take_income(player)
        self.assertEqual(player.coins, 3)

    def test_take_three_coins(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        game.take_3_coins(player)
        self.assertEqual(player.coins, 5)

    def test_card_count(self):
        player = Player.objects.all()[0]
        cards = player.hand.filter(status='D')
        self.assertEqual(player.cardcount(), len(cards))

    def test_influence(self):
        player = Player.objects.all()[0]
        self.assertEqual(player.influence(), 2)

    def test_is_card_in_hand(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        cards = player.hand.filter(status='D')
        for card in cards:
            self.assertEqual(card.card.cardName, player.is_card_in_hand(card.card.cardName, game)[0])

    def test_card_not_in_hand(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        cards = player.hand.filter(status='D')
        cards_not_in_hand = Card.objects.exclude(cardName=cards[0]).exclude(cardName=cards[1])
        for card in cards_not_in_hand:
            self.assertNotEqual(card.cardName, player.is_card_in_hand(card.cardName, game)[0])

    def test_card_in_prior_hand(self):
        cards_to_test = 'Assassin Duke'
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        game.cards_before_draw = cards_to_test
        game.save()
        action_history = ActionHistory(name='Draw', player1=player, player2=None,
                                       challenge_winner=None, challenge_loser=None)
        action_history.save()
        player = Player.objects.all()[0]
        for card in cards_to_test.split():
            self.assertEqual(card, player.is_card_in_hand(card, game)[0])
            self.assertEqual('Prior', player.is_card_in_hand(card, game)[1])

    def test_card_not_in_prior_hand(self):
        cards_to_test = 'Assassin Duke'
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        game.cards_before_draw = 'Contessa Captain'
        game.save()
        action_history = ActionHistory(name='Draw', player1=player, player2=None,
                                       challenge_winner=None, challenge_loser=None)
        action_history.save()
        player = Player.objects.all()[0]
        for card in cards_to_test.split():
            self.assertEqual(False, player.is_card_in_hand(card, game)[0])
            self.assertEqual('Prior', player.is_card_in_hand(card, game)[1])

    def test_steal(self):
        game = Game.objects.all()[0]
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]
        game.steal(player1, player2)
        self.assertEqual(player1.coins, 4)
        self.assertEqual(player2.coins, 0)

    def test_cards_remaining(self):
        deck = Deck(id=1)
        self.assertEqual(deck.cards_remaining(), 15 - len(Player.objects.all()) * 2)

    def test_add_all_actions(self):
        actions = Action.objects.all()
        self.assertEqual(len(actions), 13)

    def test_add_all_cards(self):
        cards = Card.objects.all()
        self.assertEqual(len(cards), 5)

    def test_assassinate(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        action = Action.objects.filter(name='Assassinate')[0]
        game.assassinate(player, action)
        self.assertEqual(player.coins, -1)

    def test_coup(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        action = Action.objects.filter(name='Coup')[0]
        game.coup(player, action)
        self.assertEqual(player.coins, -5)


        # with requests_mock.Mocker() as m:
        #     m.get('http://test.com', text='Hello from the mocker')
        #     response=requests.get('http://test.com').text
        #     print (type(response))
