from django.shortcuts import render, redirect
from .models import Player,  Deck, Action, Game, Lobby, ActionHistory
from .action import get_initial_action_data, take_action, get_request, finish_challenge, get_allowed_actions
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
            'login_screen_org.html',
            context={'names': names, 'in_progress': in_progress})
    else:
        return render(
            request,
            'no_more.html')


def startgame(request):
    game = Game.objects.all()[0]
    lobby_visitors = Lobby.objects.all()
    if len(lobby_visitors) < 2:
        return redirect(index)
    game.initialize()
    game.clear_current()
    game.whoseTurn = random.randint(0, game.number_of_players - 1)
    game.save()
    Deck.objects.all().delete()
    deck = Deck(id=1)
    deck.save()
    deck.build()
    return redirect(show_table)


def show_table(request):
    players = Player.objects.all()
    action_history = ActionHistory.objects.all().order_by('-id')[:16]
    game = Game.objects.all()[0]
    cards = []
    current_player_coins = players.get(playerNumber=game.whoseTurn).coins
    request_player = request.user.get_username()
    actions = get_allowed_actions(game, request_player, current_player_coins)

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
                     'eligible': game.eligible_players(), 'eligible_coup_assassinate': game.eligibleCoupAssassinate(),
                     'prior_player_name': prior_player_name}
        )
    else:
        game.finish_turn()
        game.reset()
        game.save()
        return render(
            request,
            'game_over.html',
            context={'players': players, 'actions': actions, 'game': game, 'winner': game.ck_winner(),
                     'actionhistory': action_history}
        )


def show_deck(request):
    deck = Deck.objects.all()[0]
    cards_remaining = deck.cards_remaining
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
        card_name = request.POST.get('cardnames', None)
        game = Game.objects.all()[0]
        game.finish_lose_influence(card_name)
        game.save()
        return redirect(show_table)
    else:
        game = Game.objects.all()[0]
        if game.current_action == 'Challenge':
            player = game.get_player_from_player_name(game.challenge_loser)
        else:
            player = game.get_player_from_player_name(game.current_player2)
        if player.lose_last_card():
            game.finish_turn
            game.clear_current()
            game.save()
            return redirect(show_table)
        return render(request, 'lose_influence.html', {'player': player, 'cards': player.hand.filter(status='D')})


def challenge(request):
    get_request(request)
    game = Game.objects.all()[0]
    game.challenger = request.user.username
    game.pending_action = True
    game.current_action = 'Challenge'
    game.challenge_in_progress = True
    game.challenge()
    game.save()
    if game.challenge_in_progress:
        finish_challenge()
    return redirect(show_table)


def draw(request):
    get_initial_action_data(request)
    action = Action.objects.get(name='Draw')
    # todo - start timer for challenge prior to draw OR save off cards and restore if challenge successful
    game = Game.objects.all()[0]
    game.current_action = 'Draw'
    if not game.draw():
        player = game.get_player_from_player_name(game.current_player1)
        return render(request, 'discard.html', {'player': player, 'cards': player.hand.filter(status='D')})
    else:
        game.next_turn()
        game.finish_turn(action)
        return redirect(show_table)


def actions(request):
    def your_turn():
        game = Game.objects.all()[0]
        request_name = request.GET.get('playerName', None)
        action_name = request.GET.get('action', None)
        if game.current_player_name() == request_name or action_name == 'Block Steal' \
                or action_name == 'Block Assassinate':
            return True

    get_initial_action_data(request)
    if your_turn():
        take_action()
    game = Game.objects.all()[0]
    if game.challenge_in_progress:
        get_initial_action_data(request)
        take_action()
    if game.current_action == 'Coup':
        player = game.get_player_from_player_name(game.current_player2)
        if player.lose_last_card():
            return redirect(show_table)
    if game.current_action == 'Challenge':
        player = game.get_player_from_player_name(game.current_player2)
        if player.lose_last_card():
            return redirect(show_table)
    return redirect(show_table)


def lose_one_card(request):
    for player in Player.objects.all():
        card_name = player.hand.all()[0].card.cardName
        player.lose_influence(card_name)
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
