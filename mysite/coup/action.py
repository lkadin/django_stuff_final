from .models import Player, Card, Deck, Action, Game, CardInstance, ActionHistory


def take_action():
    game = Game.objects.all()[0]
    action = Action.objects.get(name=game.current_action)
    player1 = Player.objects.get(playerName=game.current_player1)

    print(game.current_action, game.pending_action)
    if game.current_action == 'Assassinate' and not game.pending_action:
        player1.lose_coins(3)
        player1.save()

    if game.current_action == "Draw":
        if not game.discardRequired():
            player1 = Player.objects.get(playerName=game.current_player1)
            player1.draw(2)
            game.pending_action = True
        else:
            discards = game.discards.split()
            if discards:
                game.discard_cards(discards)
                game.pending_action = False
                game.save()
                return

    if action.pending_required and not game.pending_action:
        game.pending_action = True
        game.save()
        return

    # game = Game.objects.all()[0]

    if game.current_action == "Income":
        player1.add_coins(1)
    elif game.current_action == "Foreign Aid":
        player1.add_coins(2)
    elif game.current_action == "Take 3 coins":
        player1.add_coins(3)


    elif game.current_action == "Block Steal":
        game.clearCurrent()
        game.save()

    elif game.current_action == "Block Foreign Aid":
        prior_action_name, prior_player_name = game.get_prior_action_info()
        prior_player = Player.objects.get(playerName=prior_player_name)
        prior_action = Action.objects.get(name=prior_action_name)
        prior_player.lose_coins(prior_action.coins_to_lose_in_challenge)
        prior_player.save()
        game.clearCurrent()
        game.save()

    elif game.current_action == "Block Assassinate":
        game.clearCurrent()
        game.save()

    elif game.current_action == 'Challenge':
        if not game.challenge_in_progress:
            game.challenge()
            game.save()
        else:
            return

    elif game.current_action == 'Allow Steal':
        prior_action_name, prior_player_name = game.get_prior_action_info()
        player2 = Player.objects.get(playerName=prior_player_name)
        player2.add_coins(2)
        player2.save()
        player1.lose_coins(2)
        player2.save()
        game.clearCurrent()
        game.save()
        # return

    # elif action.player2_required:
    #     if request.method == 'GET':
    #         return

    # playerName2 = game.current_player2
    # if not playerName2:
    #     playerName2 = request.POST.get('name', None)
    #     game.player2_turn = True
    #     game.current_player2 = playerName2
    #     game.save()
    #     return

    player1.save()
    actionhistory = ActionHistory(name=action.name, player1=game.currentPlayerName(), player2=game.current_player2,
                                  challenge_winner=game.challenge_winner, challenge_loser=game.challenge_loser)
    actionhistory.save()
    game.save()
    return


def get_initial_action_data(request):
    game = Game.objects.all()[0]
    if request.method == 'GET':
        getrequest(request)

    if request.method == 'POST':
        discards = request.POST.getlist('cardnames', None)
        if discards:
            discard_str = ''
            for card in discards:
                discard_str += card + " "
            game.discards = discard_str
            game.save()
        playerName2 = request.POST.get('name', None)
        if playerName2:
            game.player2_turn = True
            game.current_player2 = playerName2
            game.save()

    take_action()
    return


def getrequest(request):
    playerName1 = request.GET.get('playerName', None)
    actionName = request.GET.get('action', None)
    if actionName == 'Challenge' and request.user.username:
        playerName1 = request.user.username

    game = Game.objects.all()[0]
    game.current_player1 = playerName1
    game.current_action = actionName
    game.save()
    return


def finish_lose_influence(cardName):
    game = Game.objects.all()[0]
    action = Action.objects.get(name=game.current_action)
    prior_action_name, prior_player_name = game.get_prior_action_info()
    if action.name != 'Challenge':
        player2 = game.getPlayerFromPlayerName(game.current_player2)
        player2.lose_influence(cardName)
        print(player2.playerName, player2.coins)
        # player2.lose_coins(action.coins_required)
        player2.save()

    if action.name == "Challenge":
        loser = game.getPlayerFromPlayerName(game.challenge_loser)
        loser.lose_influence(cardName)
        loser.save()
        game.current_player2 = prior_player_name
        game.save()
    game.nextTurn()
    game.clearCurrent()
    game.save()
    return
