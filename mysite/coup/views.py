from django.shortcuts import render, redirect
from .models import Player, Card, Deck, Action, Game, Lobby, ActionHistory, Function
from .action import get_initial_action_data, take_action, getrequest, finish_challenge
import random

def index(request):
    game = Game.objects.all()[0]
    in_progress = game.in_progress
    lobby_visitors = Lobby.objects.all()
    names = [lobby.player_name for lobby in lobby_visitors]
    if len(names) <= 6:
        if request.user.username not in names and request.user.username:
            lobby = Lobby(player_name=request.user.username)
            lobby.save()
        return render(
            request,
            'login_screen.html',
            context={'names': names, 'in_progress': in_progress})
    else:
        return render(
            request,
            'no_more.html')

def startgame(request):
    game = Game.objects.all()[0]
    lobby_visitors = Lobby.objects.all()
    # if game.in_progress:
    #     return redirect(index)
    if len(lobby_visitors) < 2:
        return redirect(index)
    game.initialize()
    game.clearCurrent()
    game.whoseTurn = random.randint(0, game.number_of_players - 1)
    game.save()
    Deck.objects.all().delete()
    deck = Deck(id=1)
    deck.save()
    deck.build()
    return redirect(show_table)


def show_table(request):
    def get_allowed_actions():
        prior_action_name, prior_player_name, prior_player_name2 = game.get_prior_action_info()

        if request.user.get_username() == game.currentPlayerName():
            if current_player_coins >= 10:
                actions = Action.objects.filter(name="Coup")
            else:
                actions = Action.objects.filter(coins_required__lte=current_player_coins)
                if prior_action_name not in ('Income', 'Draw', 'Challenge', 'Lose Influence', None, 'Foreign Aid'):
                    challenge = Action.objects.filter(name__in=['Challenge'])
                    actions = actions.union(challenge)
                if prior_action_name == 'Foreign Aid':
                    block_foriegn_aid = Action.objects.filter(name__in=['Block Foreign Aid'])
                    actions = actions.union(block_foriegn_aid)

        if request.user.get_username() != game.currentPlayerName():
            if prior_action_name not in (
                    'Income', 'Draw', 'Challenge', 'Lose Influence',
                    None) and request.user.get_username() != prior_player_name:
                actions = Action.objects.filter(name__in=['Challenge'])
                if prior_action_name == 'Foreign Aid':
                    block_foriegn_aid = Action.objects.filter(name__in=['Block Foreign Aid'])
                    # challenge = Action.objects.filter(name__in=['Challenge'])
                    actions = actions.union(block_foriegn_aid)
            else:
                actions = []

        if game.current_player2:
            actions = []

        if request.user.get_username() == game.current_player2 and game.current_action == 'Assassinate':
            actions = Action.objects.filter(name__in=["Lose Influence", "Block Assassinate", "Challenge"])

        if request.user.get_username() == game.current_player2 and game.current_action in ('Coup'):
            actions = Action.objects.filter(name__in=["Lose Influence"])

        if request.user.get_username() == game.challenge_loser and game.current_action in ('Challenge'):
            actions = Action.objects.filter(name__in=["Lose Influence"])

        if request.user.get_username() == game.current_player2 and game.current_action == 'Steal':
            actions = Action.objects.filter(name__in=["Block Steal", "Allow Steal", 'Challenge'])
        if not game.current_action:
            try:
                actions = actions.exclude(name__in=['Block Steal'])
            except:
                pass
        if not request.user.get_username():
            actions = []

        if prior_action_name == 'Steal' and request.user.get_username() == prior_player_name2:
            block_steal = Action.objects.filter(name__in=['Block Steal'])
            actions = actions.union(block_steal)
        return actions

    players = Player.objects.all()
    action_history = ActionHistory.objects.all().order_by('-id')[:16]
    game = Game.objects.all()[0]
    cards = []
    current_player_coins = players.get(playerNumber=game.whoseTurn).coins
    actions = get_allowed_actions()
    try:
        action_description = Action.objects.get(name=game.current_action).description
    except:
        action_description = None

    for player in players:
        for card in player.hand.all():
            cards.append(card)

    if not game.ck_winner():
        prior_action_name, prior_player_name, prior_player_name2 = game.get_prior_action_info()
        return render(
            request,
            'table.html',
            context={'players': players, 'actions': actions, 'game': game,
                     'current_player_name': request.user.username, 'actionhistory': action_history, 'cards': cards,
                     'current_player_coins': current_player_coins, 'action_description': action_description,
                     'eligible': game.eligiblePlayers(), 'eligible_coup_assassinate': game.eligibleCoupAssassinate(),
                     'prior_player_name': prior_player_name}
        )
    else:
        game.reset()
        game.save()
        return render(
            request,
            'game_over.html',
            context={'players': players, 'actions': actions, 'game': game, 'winner': game.ck_winner()}
        )


def show_deck(request):
    deck = Deck.objects.all()[0]
    cards_remaining = deck.cardsremaining
    return render(
        request,
        'show_deck.html',
        context={'deck': deck, 'cardsremaining': cards_remaining}
    )


def initial_deal(request):
    game = Game.objects.get(id=80)
    players = Player.objects.all()
    game.initialDeal()
    return render(
        request,
        'table.html',
        context={'players': players}
    )

def shuffle(request):
    deck = Deck.objects.get(id=1)
    deck.shuffle()
    deck.save()
    return render(
        request,
        'show_deck.html',
        context={'deck': deck}
    )


def lose_influence(request):
    if request.method == 'POST':
        cardName = request.POST.get('cardnames', None)
        game = Game.objects.all()[0]
        game.finish_lose_influence(cardName)
        game.save()
        return redirect(show_table)
    else:
        game = Game.objects.all()[0]
        if game.current_action == 'Challenge':
            player = game.getPlayerFromPlayerName(game.challenge_loser)
        else:
            player = game.getPlayerFromPlayerName(game.current_player2)
        if player.lose_last_card():
            return redirect(show_table)
        return render(request, 'lose_influence.html', {'player': player, 'cards': player.hand.filter(status='D')})


def challenge(request):
    getrequest(request)
    game = Game.objects.all()[0]
    game.pending_action = True
    game.current_action = 'Challenge'
    game.challenge_in_progress = True
    game.challenge()
    game.save()
    if game.challenge_in_progress:
        # take_action()
        finish_challenge()
    return redirect(show_table)


def draw(request):
    get_initial_action_data(request)
    action = Action.objects.get(name='Draw')
    game = Game.objects.all()[0]
    if not game.draw():
        player = game.getPlayerFromPlayerName(game.current_player1)
        return render(request, 'discard.html', {'player': player, 'cards': player.hand.filter(status='D')})
    else:
        game.finish_turn(action)
        return redirect(show_table)


def actions(request):
    get_initial_action_data(request)
    take_action()
    game = Game.objects.all()[0]
    if game.challenge_in_progress:
        get_initial_action_data(request)
        take_action()
    if game.current_action == 'Coup':
        player = game.getPlayerFromPlayerName(game.current_player2)
        if player.lose_last_card():
            return redirect(show_table)
    return redirect(show_table)


def lose_one_card(request):
    for player in Player.objects.all():
        cardname = player.hand.all()[0].card.cardName
        player.lose_influence(cardname)
    return redirect(show_table)


def set_coins(request):
    for player in Player.objects.all():
        player.coins = 8
        player.save()
    return redirect(show_table)


def clear_lobby(request):
    game = Game.objects.all()[0]
    game.clear_lobby()
    game.save()
    return redirect(index)
