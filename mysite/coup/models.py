from django.db import models
from django.db.models import Max
import random


class Function(models.Model):
    methodName = models.CharField(max_length=20, blank=True, null=True)
    arguments = models.TextField()
    action = models.ForeignKey("Action", on_delete=models.CASCADE, default=0)


class ActionHistory(models.Model):
    name = models.CharField(max_length=20, default="Assassinate")
    tran_date = models.DateTimeField(auto_now_add=True, blank=True)
    player1 = models.CharField(max_length=20, default="Lee")
    player2 = models.CharField(max_length=20, null=True, blank=True)
    challenge_winner = models.CharField(max_length=20, null=True, blank=True)
    challenge_loser = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return "{}->{}->{}".format(self.player1, self.name, str(self.player2 or ''))


class Action(models.Model):
    name = models.CharField(max_length=20, default="Assassinate")
    player2_required = models.BooleanField(default=False)
    coins_required = models.IntegerField(default=0)
    url = models.CharField(max_length=20, default='actions')
    pending_required = models.BooleanField(default=False)
    description = models.CharField(max_length=30, default=name)
    coins_to_lose_in_challenge = models.IntegerField(default=0)
    card_required = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    cardName = models.CharField(max_length=20, default="Assassin")

    def __str__(self):
        return self.cardName


class CardInstance(models.Model):
    card = models.ForeignKey('Card', on_delete=models.SET_NULL, null=True)
    shuffle_order = models.IntegerField(null=True)

    def __str__(self):
        return self.card.cardName

    CARD_STATUS = (
        ('U', 'Up'),
        ('D', 'Down'),
    )
    status = models.CharField(max_length=1, choices=CARD_STATUS, blank=True, default='D', help_text='Card status')


class Player(models.Model):
    playerName = models.CharField(max_length=20, default="Lee")
    playerNumber = models.IntegerField(default=0)
    coins = models.IntegerField(default=2)
    hand = models.ManyToManyField(CardInstance)

    def __str__(self):
        return self.playerName

    def add_coins(self, num_coins):
        self.coins += num_coins

    def lose_coins(self, num_coins):
        self.coins -= num_coins

    def influence(self):
        return sum(1 for card in self.hand.all() if card.status == "D")

    def draw(self, number_of_cards):
        self.deck = Deck.objects.all()[0]
        for _ in range(number_of_cards):
            self.selected_card = self.deck.draw_card()
            self.hand.add(self.selected_card)
        self.save()

    def swap(self, card_name):
        self.card_name = card_name
        self.discard(self.card_name)
        self.draw(1)
        self.save()

    def discard(self, card_name):
        self.card_name = card_name
        self.card_id = Card.objects.filter(cardName=self.card_name)[0].id
        self.card = self.hand.filter(card_id=self.card_id).filter(status='D')[0]
        self.deck = Deck.objects.all()[0]
        self.deck.return_card(self.card)
        self.hand.remove(self.card)
        self.deck.shuffle()
        self.deck.save()
        self.save()

    def card_count(self):
        return len(self.hand.all())

    def lose_influence(self, card_name):
        self.card_name = card_name
        self.card_id = Card.objects.filter(cardName=card_name)[0].id
        self.card = self.hand.filter(card_id=self.card_id).filter(status='D')[0]
        self.card.status = 'U'
        self.card.save()
        self.save()

    def lose_last_card(self):
        game = Game.objects.all()[0]
        if self.influence() > 1:
            return False
        elif self.influence() == 0:
            return True
        else:
            game.finish_lose_influence(self.hand.filter(status='D')[0].card.cardName)
            game.save()
            return True

    def is_card_in_hand(self, cards_to_check, game):
        self.cards_to_check = cards_to_check.split(',')
        self.cards_in_hand = [card.card.cardName for card in self.hand.filter(status="D")]

        if game.get_prior_action_info()[0] == 'Draw':
            for card in game.cards_before_draw.split():
                if card in self.cards_to_check:
                    return card, 'Prior'
            return False, 'Prior'

        for card in self.cards_to_check:
            if card not in self.cards_in_hand:
                return False, "Current"
            else:
                return card, 'Current'


class Deck(models.Model):
    cards = models.ManyToManyField(CardInstance)

    def __str__(self):
        return "Deck"

    def cards_remaining(self):
        self.cnt = 0
        for self.card in self.cards.all().order_by('shuffle_order'):
            if self.card.shuffle_order is not None:
                self.cnt += 1
        return self.cnt

    def cards_available(self):
        self.cards_avail = []
        for self.card in self.cards.all():
            if self.card.shuffle_order is not None:
                self.cards_avail.append(self.card)
        return self.cards_avail

    def build(self):
        cis = CardInstance.objects.all()
        for ci in cis:
            ci.save()
            self.cards.add(ci)

    def shuffle(self):
        self.cards_left = CardInstance.objects.exclude(shuffle_order=None)
        for i in range(self.cards_left.count() - 1, -1, -1):
            r = random.randint(0, i)

            self.card1 = self.cards_left.filter(shuffle_order=i)[0]
            self.card2 = self.cards_left.filter(shuffle_order=r)[0]
            self.card1.shuffle_order, self.card2.shuffle_order = self.card2.shuffle_order, self.card1.shuffle_order
            self.card1.save()
            self.card2.save()

    def draw_card(self):
        self.max_card = CardInstance.objects.all().aggregate(Max('shuffle_order'))
        self.max = self.max_card['shuffle_order__max']
        self.card = CardInstance.objects.get(shuffle_order=self.max)
        self.card.shuffle_order = None
        self.card.save()
        return self.card

    def return_card(self, card):
        self.card = card
        self.max_card = CardInstance.objects.all().aggregate(Max('shuffle_order'))
        self.max = self.max_card['shuffle_order__max'] + 1
        self.card.shuffle_order = self.max
        self.card.save()


class Lobby(models.Model):
    player_name = models.CharField(max_length=20)


class Game(models.Model):
    NUM_OF_CARDS = models.IntegerField(default=2)
    whoseTurn = models.IntegerField(default=0)
    current_action = models.CharField(max_length=20, null=True, blank=True)
    current_player1 = models.CharField(max_length=20, null=True, blank=True)
    current_player2 = models.CharField(max_length=20, null=True, blank=True)
    challenger = models.CharField(max_length=20, null=True, blank=True)
    redoMessage = models.CharField(max_length=30, blank=True, null=True)
    pending_action = models.BooleanField(default=False)
    player2_turn = models.BooleanField(default=False)
    challenge_in_progress = models.BooleanField(default=False)
    challenge_winner = models.CharField(max_length=20, null=True, blank=True)
    challenge_loser = models.CharField(max_length=20, null=True, blank=True)
    discards = models.CharField(max_length=60, null=True, blank=True)
    cards_before_draw = models.CharField(max_length=60, null=True, blank=True)
    second_player = models.CharField(max_length=20, null=True, blank=True)
    in_progress = models.BooleanField(default=False)
    number_of_players = models.IntegerField(default=0)

    @staticmethod
    def del_card_instances():
        CardInstance.objects.all().delete()

    def build_cards(self):
        self.order = 0
        for card in Card.objects.all():
            for _ in range(3):
                card.cardinstance_set.create(shuffle_order=self.order)
                self.order += 1
                card.save()

    def rebuild_cards(self):
        for self.cnt, card in enumerate(CardInstance.objects.exclude(shuffle_order=None)):
            card.shuffle_order = self.cnt
            card.save()

    def initialize(self):
        ActionHistory.objects.all().delete()
        Card.objects.all().delete()
        Action.objects.all().delete()
        self.add_all_actions()
        self.add_all_cards()
        self.del_card_instances()
        self.build_cards()
        self.cards_before_draw = None
        self.challenger = None
        self.discards = None
        self.deck = Deck(id=1)
        self.deck.save()
        self.deck.build()
        self.deck.shuffle()
        self.deck.save()
        Player.objects.all().delete()

        # todo:replace with lobby /login
        self.in_progress = True
        self.add_all_players()
        self.initialDeal()

    def reset(self):
        self.in_progress = False

    def clear_lobby(self):
        Lobby.objects.all().delete()

    def initialDeal(self):
        self.deck = Deck.objects.all()[0]
        players = Player.objects.all()
        for _ in range(self.NUM_OF_CARDS):
            for player in players:
                player.hand.add(self.deck.draw_card())
                self.deck.save()

    def add_all_players(self):
        player_number = 0
        lobby_visitors = Lobby.objects.all()
        for name in lobby_visitors:
            player = Player(playerName=name.player_name, playerNumber=player_number)
            player.save()
            player_number += 1
        self.number_of_players = player_number

    def add_all_actions(self):

        self.action = Action(name="Assassinate", player2_required=False, coins_required=3, url='actions',
                             pending_required=True, description="is assassinating",
                             coins_to_lose_in_challenge=0, card_required="Assassin")
        self.action.save()
        self.action = Action(name="Coup", player2_required=False, coins_required=7, url='actions',
                             pending_required=True, description="is Couping",
                             coins_to_lose_in_challenge=0)
        self.action.save()
        self.action = Action(name="Steal", player2_required=False, coins_required=0, url='actions',
                             pending_required=False, description="Stole from",
                             coins_to_lose_in_challenge=2, card_required='Captain')
        self.action.save()
        self.action = Action(name="Take 3 coins", player2_required=False, coins_required=0, url='actions',
                             pending_required=False, description="is taking 3 coins",
                             coins_to_lose_in_challenge=3, card_required='Duke')
        self.action.save()
        self.action = Action(name="Foreign Aid", player2_required=False, coins_required=0, url='actions',
                             pending_required=False, description="is taking Foreign Aid",
                             coins_to_lose_in_challenge=2)
        self.action.save()
        self.action = Action(name="Income", player2_required=False, coins_required=0, url='actions',
                             pending_required=False, description="is taking income",
                             coins_to_lose_in_challenge=0)
        self.action.save()
        self.action = Action(name="Block Steal", player2_required=False, coins_required=100, url='actions',
                             pending_required=False, description="is blocking a steal",
                             coins_to_lose_in_challenge=0, card_required='Captain,Ambassador')
        self.action.save()
        self.action = Action(name="Challenge", player2_required=False, coins_required=100, url='actions',
                             pending_required=False, description="won the challenge",
                             coins_to_lose_in_challenge=0)
        self.action.save()
        self.action = Action(name="Draw", player2_required=False, coins_required=0, url='actions',
                             pending_required=True, description="is drawing new cards",
                             coins_to_lose_in_challenge=0, card_required='Ambassador')
        self.action.save()
        self.action = Action(name="Lose Influence", player2_required=False, coins_required=100, url='loseinfluence',
                             pending_required=False, description="is losing influence",
                             coins_to_lose_in_challenge=0)
        self.action.save()
        self.action = Action(name="Allow Steal", player2_required=False, coins_required=100, url='actions',
                             pending_required=False, description="is allowing steal",
                             coins_to_lose_in_challenge=0)
        self.action.save()
        self.action = Action(name="Block Assassinate", player2_required=False, coins_required=100, url='actions',
                             pending_required=False, description="is blocking the assassination",
                             coins_to_lose_in_challenge=0, card_required='Contessa')
        self.action.save()
        self.action = Action(name="Block Foreign Aid", player2_required=False, coins_required=100, url='actions',
                             pending_required=False, description="is blocking foreign aid",
                             coins_to_lose_in_challenge=2, card_required='Duke')
        self.action.save()

    def add_all_cards(self):
        self.card = Card(cardName="Captain")
        self.card.save()
        self.card = Card(cardName="Ambassador")
        self.card.save()
        self.card = Card(cardName="Duke")
        self.card.save()
        self.card = Card(cardName="Contessa")
        self.card.save()
        self.card = Card(cardName="Assassin")
        self.card.save()

    def draw(self):

        if not self.discard_required():
            player1 = Player.objects.get(playerName=self.current_player1)
            self.cards_before_draw = " ".join([card.card.cardName for card in player1.hand.filter(status='D')])
            player1.draw(2)
            self.player2 = None
            self.pending_action = True
            self.save()
        else:
            if self.pending_action and not self.discards:
                return
            discards = self.discards.split()
            if discards:
                self.discard_cards(discards)
                self.pending_action = False
                self.save()
                return True

    def assassinate(self, player1, action):
        player1.lose_coins(action.coins_required)
        player1.save()

    def take_3_coins(self, player1):
        player1.add_coins(3)

    def take_income(self, player1):
        player1.add_coins(1)

    def take_foreign_aid(self, player1):
        player1.add_coins(2)

    def block_assassinate(self):
        self.current_player2 = None
        self.pending_action = False
        self.save()

    def coup(self, player1, action):
        player1.lose_coins(action.coins_required)
        player1.save()

    def block_foreign_aid(self):
        prior_action_name, prior_player_name, prior_player_name2 = self.get_prior_action_info()
        prior_player = Player.objects.get(playerName=prior_player_name)
        prior_action = Action.objects.get(name=prior_action_name)
        prior_player.lose_coins(prior_action.coins_to_lose_in_challenge)
        prior_player.save()
        self.save()

    def block_steal(self, player1):
        self.prior_action_name, self.prior_player_name, self.prior_player_name2 = self.get_prior_action_info()
        self.player2 = self.get_player_from_player_name(self.prior_player_name)
        player1.add_coins(2)
        player1.save()
        self.player2.lose_coins(2)
        self.player2.save()
        self.pending_action = False
        self.save()

    def next_turn(self):
        self.whoseTurn = (self.whoseTurn + 1) % self.number_of_players
        while not Player.objects.get(playerNumber=self.whoseTurn).influence():
            self.whoseTurn = (self.whoseTurn + 1) % self.number_of_players

    def finish_turn(self, action=None):
        if action:
            if action.name in ('Draw', "Income", "Take 3 coins", "Foreign Aid"):
                self.current_player2 = None
                self.save()
            action_history = ActionHistory(name=action.name, player1=self.current_player1, player2=self.current_player2,
                                           challenge_winner=self.challenge_winner, challenge_loser=self.challenge_loser)
            action_history.save()
        if not self.pending_action and not self.challenge_in_progress:
            self.clear_current()
            self.save()

    def current_player_name(self):
        self.players = [self.player for self.player in Player.objects.all()]
        return self.players[self.whoseTurn].playerName

    def ck_winner(self):
        self.players = Player.objects.all()
        count = 0
        for self.player in self.players:
            if self.player.influence() > 0:
                count += 1
                self.winner = self.player.playerName
        if count == 1:
            return self.winner

    def clear_current(self):
        self.current_action = None
        self.current_player1 = None
        self.current_player2 = None
        self.pending_action = False
        self.player2_turn = False
        self.challenge_in_progress = False
        self.challenge_winner = None
        self.challenge_loser = None

    def eligible_players(self):
        eligible = []
        players = Player.objects.all()
        for player in players:
            if player.playerName == self.current_player_name():
                continue
            if player.influence() > 0 and player.coins >= 2:
                eligible.append(player)
        return eligible

    def eligibleCoupAssassinate(self):
        eligible = []
        players = Player.objects.all()
        for player in players:
            if player.playerName == self.current_player_name():
                continue
            if player.influence() > 0:
                eligible.append(player)
        return eligible

    def lose_all_cards(self, player_name):
        self.player = self.get_player_from_player_name(player_name)
        self.cards = self.player.hand.filter(status='D')
        for self.card in self.cards:
            self.player.lose_influence(self.card.card.cardName)
        self.pending_action = False
        action_history = ActionHistory(name='Challenge', player1=self.challenger, player2=self.current_player2,
                                       challenge_winner=self.challenge_winner, challenge_loser=self.challenge_loser)
        action_history.save()
        action_history = ActionHistory(name='Lose Influence', player1=self.challenge_loser,
                                       player2=self.card.card.cardName,
                                       challenge_winner=self.challenge_winner, challenge_loser=self.challenge_loser)
        action_history.save()
        if not self.player.influence() and self.whoseTurn == self.player.playerNumber:
            self.next_turn()

    def finish_lose_influence(self, card_name):
        action = Action.objects.get(name=self.current_action)
        if action.name != 'Challenge':
            player = self.get_player_from_player_name(self.current_player2)
            action_history = ActionHistory(name='Lose Influence', player1=self.current_player2, player2=card_name,
                                           challenge_winner=self.challenge_winner, challenge_loser=self.challenge_loser)

        if action.name == "Challenge":
            player = self.get_player_from_player_name(self.challenge_loser)
            action_history = ActionHistory(name='Lose Influence', player1=self.challenge_loser, player2=card_name,
                                           challenge_winner=self.challenge_winner, challenge_loser=self.challenge_loser)
        action_history.save()
        player.lose_influence(card_name)
        if not player.influence() and self.whoseTurn == player.playerNumber:
            self.next_turn()
        player.save()
        self.clear_current()
        self.save()

    def get_player_from_player_name(self, player_name):
        self.player_name = player_name
        return Player.objects.get(playerName=self.player_name)

    def steal(self, player1, player2):
        player1.add_coins(2)
        player1.save()
        player2.lose_coins(2)
        player2.save()
        self.pending_action = False
        self.save()

    def discard_cards(self, cards_to_keep):
        self.cards_to_discard = []
        player = Player.objects.get(playerName=self.current_player1)
        self.cards_in_hand = player.hand.filter(status='D')
        for x in self.cards_in_hand:
            if x.card.cardName not in cards_to_keep:
                self.cards_to_discard.append(x.card.cardName)
            if x.card.cardName in cards_to_keep:
                cards_to_keep.remove(x.card.cardName)

        for card in self.cards_to_discard:
            player.discard(card)
            player.save()

    def discard_required(self):
        try:
            player = self.get_player_from_player_name(self.current_player1)
        except:
            return False
        return player.card_count() > 2

    def challenge(self):

        def prepare_to_lose_all_cards():
            self.lose_all_cards(self.challenge_loser)
            self.finish_turn()
            self.save()
            self.challenge_in_progress = False
            self.clear_current()
            self.save()

        self.challenge_in_progress = True
        prior_action_name, prior_player_name, prior_player_name2 = self.get_prior_action_info()
        prior_action = Action.objects.get(name=prior_action_name)  # action being challenged?
        prior_player = Player.objects.get(playerName=prior_player_name)  # player being challenged ?
        current_player = Player.objects.get(playerName=self.current_player1)  # is this always the same as challenger?
        if prior_action_name not in (
                "Take 3 coins", "Block Steal", "Steal", "Assassinate", "Block Assassinate", "Block Foreign Aid",
                "Draw"):
            return
        # self.current_player2 = prior_player_name  # why do we need this?
        # self.save()  # why?
        self.card_in_hand, self.where_from = prior_player.is_card_in_hand(prior_action.card_required, self)
        if self.card_in_hand:  # challenge not successful
            self.challenge_loser = self.challenger
            self.challenge_winner = prior_player_name
            if self.where_from == 'Current':
                prior_player.swap(self.card_in_hand)  # swap out winning card
                prior_player.save()
            if prior_action_name == "Assassinate" or self.get_player_from_player_name(
                    self.challenge_loser).influence() == 1:
                prepare_to_lose_all_cards()
                return

            if self.get_player_from_player_name(self.challenge_loser).influence() == 1:
                prepare_to_lose_all_cards()
                return

        else:  # challenge is successful
            self.challenge_loser = prior_player_name
            self.challenge_winner = self.challenger

            if prior_action_name in ('Steal', 'Block Steal'):
                current_player.add_coins(prior_action.coins_to_lose_in_challenge)
                current_player.add_coins(2)
                prior_player.lose_coins(2)
                prior_player.save()
                current_player.save()
            if prior_action_name not in ('Steal', 'Block Steal'):
                prior_player.lose_coins(prior_action.coins_to_lose_in_challenge)
                if self.get_player_from_player_name(self.challenge_loser).influence() == 1:
                    prepare_to_lose_all_cards()
                    return

            if prior_action_name == "Block Assassinate":
                prepare_to_lose_all_cards()
                return
        self.save()
        self.current_action = 'Challenge'

    def get_prior_action_info(self):
        self.prior_player_name2 = None
        try:
            self.prior_action_name = ActionHistory.objects.all().order_by('-id')[0].name
            self.prior_player_name = ActionHistory.objects.all().order_by('-id')[0].player1
            self.prior_player_name2 = ActionHistory.objects.all().order_by('-id')[0].player2
        except:
            self.prior_action_name = None
            self.prior_player_name = None

        return self.prior_action_name, self.prior_player_name, self.prior_player_name2

    def get_second_prior_action_info(self):
        try:
            self.prior_action_name = ActionHistory.objects.all().order_by('-id')[1].name
            self.prior_player_name = ActionHistory.objects.all().order_by('-id')[1].player1
            self.prior_player_name2 = ActionHistory.objects.all().order_by('-id')[1].player2
        except:
            self.prior_action_name = None
            self.prior_player_name = None
            self.prior_player_name2 = None
        return self.prior_action_name, self.prior_player_name, self.prior_player_name2
