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
        cnt = 0
        for card in self.hand.all():
            if card.status == "D":
                cnt += 1
        return cnt

    def draw(self, number_of_cards):
        self.deck = Deck.objects.all()[0]
        self.deck.shuffle()
        for cards in range(number_of_cards):
            self.hand.add(self.deck.draw_card())
        self.save()

    def swap(self, cardname):
        self.cardname = cardname
        self.discard(self.cardname)
        self.draw(1)
        self.save()

    def discard(self, cardname):
        self.cardname = cardname
        self.card_id = Card.objects.filter(cardName=self.cardname)[0].id
        self.card = self.hand.filter(card_id=self.card_id).filter(status='D')[0]
        self.deck = Deck.objects.all()[0]
        self.deck.return_card(self.card)
        self.hand.remove(self.card)
        self.deck.save()
        self.save()

    def cardcount(self):
        return len(self.hand.all())

    def lose_influence(self, cardname):
        self.cardname = cardname
        self.card_id = Card.objects.filter(cardName=cardname)[0].id
        self.card = self.hand.filter(card_id=self.card_id).filter(status='D')[0]
        self.card.status = 'U'
        self.card.save()
        self.save()

    def is_card_in_hand(self, card_name):
        card_names = card_name.split(',')
        for card in self.hand.all():
            if card.card.cardName in card_names:
                if card.status == 'D':
                    return card.card.cardName


class Deck(models.Model):
    cards = models.ManyToManyField(CardInstance)

    def __str__(self):
        return "Deck"

    def cardsremaining(self):
        self.cnt = 0
        for self.card in self.cards.all():
            if self.card.shuffle_order is not None:
                self.cnt += 1
        return self.cnt

    def cardsavailable(self):
        self.cardsavail = []
        for self.card in self.cards.all():
            if self.card.shuffle_order is not None:
                self.cardsavail.append(self.card)
        return self.cardsavail

    def build(self):
        cis = CardInstance.objects.all()
        for ci in cis:
            ci.save()
            self.cards.add(ci)

    def shuffle(self):
        self.cardsleft = CardInstance.objects.exclude(shuffle_order=None)
        for i in range(self.cardsleft.count() - 1, -1, -1):
            r = random.randint(0, i)
            self.card1 = self.cardsleft.filter(shuffle_order=i)[0]
            self.card2 = self.cardsleft.filter(shuffle_order=r)[0]
            self.card1.shuffle_order, self.card2.shuffle_order = self.card2.shuffle_order, self.card1.shuffle_order
            self.card1.save()
            self.card2.save()

    def draw_card(self):
        self.shuffle()
        self.maxcard = CardInstance.objects.all().aggregate(Max('shuffle_order'))
        self.max = self.maxcard['shuffle_order__max']
        self.card = CardInstance.objects.get(shuffle_order=self.max)
        self.card.shuffle_order = None
        self.card.save()
        return self.card

    def return_card(self, card):
        self.card = card
        self.maxcard = CardInstance.objects.all().aggregate(Max('shuffle_order'))
        self.max = self.maxcard['shuffle_order__max'] + 1
        self.card.shuffle_order = self.max
        self.card.save()


class Game(models.Model):
    NUM_OF_CARDS = models.IntegerField(default=2)
    whoseTurn = models.IntegerField(default=0)
    current_action = models.CharField(max_length=20, null=True, blank=True)
    current_player1 = models.CharField(max_length=20, null=True, blank=True)
    current_player2 = models.CharField(max_length=20, null=True, blank=True)
    redoMessage = models.CharField(max_length=30, blank=True, null=True)
    pending_action = models.BooleanField(default=False)
    player2_turn = models.BooleanField(default=False)
    challenge_in_progress = models.BooleanField(default=False)
    challenge_winner = models.CharField(max_length=20, null=True, blank=True)
    challenge_loser = models.CharField(max_length=20, null=True, blank=True)

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

    def initialize(self):
        ActionHistory.objects.all().delete()
        self.del_card_instances()
        self.build_cards()
        deck = Deck(id=1)
        deck.save()
        deck.build()
        deck.shuffle()
        deck.save()
        Player.objects.all().delete()
        # todo:replace with lobby /login
        self.add_all_players()
        self.initialDeal()

    def initialDeal(self):
        self.deck = Deck.objects.all()[0]
        self.deck.shuffle()
        self.deck.save()
        players = Player.objects.all()
        for i in range(self.NUM_OF_CARDS):
            for player in players:
                player.hand.add(self.deck.draw_card())
                self.deck.save()

    @staticmethod
    def add_all_players():
        player = Player(playerName="Lee", playerNumber=0)
        player.save()
        player = Player(playerName="Adina", playerNumber=1)
        player.save()
        player = Player(playerName="Sam", playerNumber=2)
        player.save()
        player = Player(playerName="Jamie", playerNumber=3)
        player.save()

    def nextTurn(self):
        self.player_whose_turn = Player.objects.get(playerNumber=self.whoseTurn)
        # if not (self.current_action == "Challenge" and self.current_player2 == self.currentPlayerName()):
        print(self.current_action, self.challenge_loser, self.currentPlayerName())
        if self.current_action != "Challenge" or (
                self.current_action == 'Challenge' and self.challenge_loser == self.currentPlayerName()):
            self.whoseTurn = (self.whoseTurn + 1) % 4
            while not Player.objects.get(playerNumber=self.whoseTurn).influence():
                self.whoseTurn = (self.whoseTurn + 1) % 4

    def currentPlayerName(self):
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

    def clearCurrent(self):
        self.current_action = None
        self.current_player1 = None
        self.current_player2 = None
        self.pending_action = False
        self.player2_turn = False
        self.challenge_in_progress = False
        self.challenge_winner = None
        self.challenge_loser = None

    @staticmethod
    def getPlayerFromPlayerName(playerName):
        return Player.objects.get(playerName=playerName)

    def discard_cards(self, cards):
        player = Player.objects.get(playerName=self.current_player1)
        for card in cards:
            player.discard(card)
            player.save()

    def discardRequired(self):
        player = self.getPlayerFromPlayerName(self.current_player1)
        if player.cardcount() > 2:
            return True
        else:
            return False

    def playerRequired(self):
        if self.current_player2:
            return
        actionName = self.current_action
        action = Action.objects.get(name=actionName)
        return action.player2_required

    def lose_influence_required(self):
        # todo: if only one card left , make this automatic
        if self.current_action in ("Assassinate", "Coup") and self.current_player2:
            player2 = Player.objects.get(playerName=self.current_player2)
            if player2.influence == 1:
                print(' I am here')
                pass
                # todo: Get ird of last card in hand and move on
            self.player2_turn = True
            self.save()
            return True
        else:
            return False

    def challenge(self):

        def determine_challenge(self, prior_action):
            self.current_player2 = prior_player_name
            if prior_player.is_card_in_hand(prior_action.card_required):  # challenge not successful
                # self.current_player2 = current_player.playerName
                self.challenge_loser = current_player.playerName
                self.challenge_winner = prior_player_name
                prior_player.swap(prior_player.is_card_in_hand(prior_action.card_required))
            else:  # challenge is successful
                prior_player.lose_coins(prior_action.coins_to_lose_in_challenge)
                current_player.add_coins(prior_action.coins_to_lose_in_challenge)
                prior_player.save()
                # self.current_player2 = prior_player_name
                self.challenge_loser = prior_player_name
                self.challenge_winner = current_player.playerName
            self.current_action = 'Challenge'

        self.challenge_in_progress = True
        prior_action_name, prior_player_name = self.get_prior_action_info()
        prior_action = Action.objects.get(name=prior_action_name)
        prior_player = Player.objects.get(playerName=prior_player_name)
        current_player = Player.objects.get(playerName=self.current_player1)

        if prior_action_name in (
                "Take 3 coins", "Block Steal", "Steal", "Assassinate", "Block Assassinate", "Block Foreign Aid"):
            determine_challenge(self, prior_action)

    @staticmethod
    def get_prior_action_info():
        try:
            prior_action_name = ActionHistory.objects.all().order_by('-id')[0].name
            prior_player_name = ActionHistory.objects.all().order_by('-id')[0].player1
        except:
            prior_action_name = None
            prior_player_name = None
        return prior_action_name, prior_player_name
