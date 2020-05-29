from django.test import TestCase

# Create your tests here.

from coup.models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory


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
        player = Player.objects.all()[0]
        deck = Deck(id=1)
        self.assertEqual(deck.cards_remaining(), 7)
        self.assertEqual(CardInstance.objects.all().count(), 15)
        self.assertEqual(Player.objects.all().count(), 4)
        self.assertEqual(player.cardcount(), 2)
        self.assertEqual(player.influence(), 2)

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
        print(len(cards))
        card_to_swap = player.hand.filter(status='D')[0]
        player.swap(card_to_swap)
        new_cards_in_hand = player.hand.all()
        print(len(new_cards_in_hand))
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

    def test_cardcount(self):
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

    def test_steal(self):
        game = Game.objects.all()[0]
        player1 = Player.objects.all()[0]
        player2 = Player.objects.all()[1]
        game.steal(player1, player2)
        self.assertEqual(player1.coins, 4)
        self.assertEqual(player2.coins, 0)

    # def test_block_steal(self):
    #     game = Game.objects.all()[0]
    #     player1 = Player.objects.all()[0]
    #     player2 = Player.objects.all()[1]
    #     game.steal(player1, player2)
    #     game.block_steal(player1)
    #     self.assertEqual(player1.coins, 2)
    #     self.assertEqual(player2.coins, 2)

    def test_cards_remaining(self):
        deck = Deck(id=1)
        self.assertEqual(deck.cards_remaining(), 7)

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
        self.assertEqual(player.coins,-1)

    def test_coup(self):
        game = Game.objects.all()[0]
        player = Player.objects.all()[0]
        action = Action.objects.filter(name='Coup')[0]
        game.coup(player, action)
        self.assertEqual(player.coins,-5)