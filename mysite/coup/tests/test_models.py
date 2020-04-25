from django.test import TestCase

# Create your tests here.

from ..models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory
from ..views import startgame


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
        deck.shuffle()
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
        player = Player(playerName="Jamie", playerNumber=3)
        player.save()
        game.initialDeal()
        game.number_of_players = 4
        game.save()

    def test_initial_deal(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        deck = Deck(id=1)
        self.assertEquals(deck.cardsremaining(), 7)
        self.assertEquals(CardInstance.objects.all().count(), 15)
        self.assertEqual(Player.objects.all().count(), 4)
        self.assertEqual(player.cardcount(), 2)
        self.assertEqual(player.influence(), 2)

    def test_player(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        # test lose coins
        player.lose_coins(2)
        self.assertEqual(player.coins, 0)
        # test add coins
        player.add_coins(3)
        self.assertEqual(player.coins, 3)
        # test draw 2 crads
        player.draw(2)
        self.assertEqual(player.cardcount(), 4)
        cards = player.hand.all()
        # test discard
        player.discard(cards[0])
        self.assertEqual(player.cardcount(), 3)
        player.discard(cards[0])
        self.assertEqual(player.cardcount(), 2)
        # test lose influence
        player.lose_influence(cards[0].card.cardName)
        self.assertEqual(player.influence(), 1)
        # test draw and discard after lose influence
        player.draw(2)
        self.assertEqual(player.cardcount(), 4)
        self.assertEqual(player.hand.filter(status='D').count(), 3)
        player.discard(player.hand.filter(status='D')[0])
        self.assertEqual(player.hand.filter(status='D').count(), 2)
        player.discard(player.hand.filter(status='D')[0])
        self.assertEqual(player.hand.filter(status='D').count(), 1)
        self.assertEqual(player.cardcount(), 2)

        # test swap card
        player.swap(player.hand.filter(status='D')[0])
        new_cards_in_hand = list(player.hand.all())
        self.assertNotEqual(player.hand.all()[0], new_cards_in_hand[0])

        # test next turn
        next_turn = game.whoseTurn + 1
        game.next_turn()
        self.assertEqual(game.whoseTurn, next_turn)

