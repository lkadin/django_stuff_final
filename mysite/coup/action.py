from .models import Player, Action, Game


def take_action():
    game = Game.objects.all()[0]
    action = Action.objects.get(name=game.current_action)
    player1 = Player.objects.get(playerName=game.current_player1)
    try:
        player2 = Player.objects.get(playerName=game.current_player2)
    except:
        player2 = None

    if game.current_action == 'Challenge' and not game.pending_action:
        print ("Curent action challenge")
        game.clearCurrent()
        print ("Action-{}".format(game.current_action))
        game.save()

    if game.current_action == 'Assassinate' and not game.pending_action:
        game.next_turn()
        game.assassinate(player1, action)

    if game.current_action == 'Coup' and not game.pending_action:
        game.next_turn()
        game.coup(player1, action)

    if game.current_action == "Income":
        game.next_turn()
        game.take_income(player1)

    if game.current_action == "Foreign Aid":
        game.next_turn()
        game.take_foreign_aid(player1)

    if game.current_action == "Take 3 coins":
        game.next_turn()
        game.take_3_coins(player1)

    if game.current_action == "Steal":
        game.next_turn()
        game.steal(player1, player2)

    if game.current_action == "Block Steal":
        game.block_steal(player1)

    if game.current_action == "Block Foreign Aid":
        game.block_foreign_aid()

    if game.current_action == "Block Assassinate":
        game.block_assassinate()

    if action.pending_required and not game.pending_action:
        game.pending_action = True
        game.save()

    player1.save()

    game.finish_turn(action)
    return


def finish_challenge():
    game = Game.objects.all()[0]
    action = Action.objects.get(name=game.current_action)
    player1 = Player.objects.get(playerName=game.current_player1)
    if action.pending_required and not game.pending_action:
        game.pending_action = True
        game.save()
    player1.save()
    game.finish_turn(action)
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
    return


def getrequest(request):
    playerName1 = request.GET.get('playerName', None)
    actionName = request.GET.get('action', None)
    playerName2 = request.GET.get('name', None)
    if actionName in ['Challenge', 'Block Steal'] and request.user.username:
        playerName1 = request.user.username
    game = Game.objects.all()[0]
    game.current_player1 = playerName1
    game.current_action = actionName
    game.current_player2 = playerName2
    game.save()
    return
