from django.test import TestCase

# Create your tests here.
import coup.action
from coup.models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory


class GameModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        game = Game(id=1,
                    NUM_OF_CARDS=2)
        game.initialize()
        game.clear_current()
        game.save()
        game.in_progress = True
        player = Player(playerName="Lee", playerNumber=0)
        player.save()
        player = Player(playerName="Adina", playerNumber=1)
        player.save()
        game.initialDeal()
        game.save()
        # player = Player(playerName="Sam", playerNumber=2)
        # player.save()
        # # player = Player(playerName="Jamie", playerNumber=3)
        # # player.save()
        game.number_of_players = len(Player.objects.all())
        game.save()

    def test_block_steal(self):
        deck = Deck(id=1)
        game = Game.objects.all()[0]
        game.current_action = 'Steal'
        game.current_player1 = Player.objects.all()[0].playerName
        game.current_player2 = Player.objects.all()[1].playerName
        game.save()
        coup.action.take_action()
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]

        self.assertEqual(player1.coins, 4)
        self.assertEqual(player2.coins, 0)

        player1.discard(player1.hand.all()[0])
        player1.save()
        player1.discard(player1.hand.all()[0])
        player1.save()
        player2.discard(player2.hand.all()[0])
        player2.save()
        player2.discard(player2.hand.all()[0])
        player2.save()

        first_pick = CardInstance.objects.all()[2]
        first_pick.shuffle_order = None
        first_pick.save()
        player1.hand.add(first_pick)

        second_pick = CardInstance.objects.all()[3]
        second_pick.shuffle_order = None
        second_pick.save()
        player1.hand.add(second_pick)
        player1.save()

        first_pick = CardInstance.objects.all()[0]
        first_pick.shuffle_order = None
        first_pick.save()
        player2.hand.add(first_pick)

        second_pick = CardInstance.objects.all()[1]
        second_pick.shuffle_order = None
        second_pick.save()
        player2.hand.add(second_pick)
        deck.save()

        player2.lose_influence('Captain')
        player2.save()
        game.rebuild_cards()

        game.current_action = 'Block Steal'
        game.current_player1 = Player.objects.all()[1].playerName
        game.current_player2 = Player.objects.all()[0].playerName
        game.save()

        coup.action.take_action()
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]
        self.assertEqual(player1.coins, 2)
        self.assertEqual(player2.coins, 2)

        game.current_action = 'Challenge'
        game.current_player1 = Player.objects.all()[0].playerName
        game.current_player2 = Player.objects.all()[1].playerName
        game.challenger = game.current_player1
        game.pending_action = True
        game.challenge_in_progress = True
        game.save()
        game.challenge()
        game.current_player1 = Player.objects.all()[0].playerName
        game.current_action = 'Challenge'
        game.save()
        if game.challenge_in_progress:
            coup.action.finish_challenge()
        game.save()
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]
        self.assertEqual(player1.coins, 2)
        self.assertEqual(player2.coins, 2)

