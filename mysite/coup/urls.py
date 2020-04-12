from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('start', views.startgame, name='startGame'),
    ]
urlpatterns += [
    path('showTable', views.show_table, name='showTable'),
    ]


urlpatterns += [
    path('showDeck', views.show_deck, name='showDeck'),
    ]

urlpatterns += [
    path('initialDeal', views.initial_deal, name='initialDeal'),
    ]

urlpatterns += [
    path('shuffle', views.shuffle, name='shuffle'),
    ]

urlpatterns += [
    path('actions', views.actions, name='actions'),
    ]

urlpatterns += [
    path('challenge', views.challenge, name='challenge'),
]

urlpatterns += [
    path('draw', views.draw, name='draw'),
]

urlpatterns += [
    path('loseinfluence', views.lose_influence, name='loseinfluence'),
]
urlpatterns += [
    path('lose_one_card', views.lose_one_card, name='lose_one_card'),
]
urlpatterns += [
    path('set_coins', views.set_coins, name='set_coins'),
]
urlpatterns += [
    path('clear_lobby', views.clear_lobby, name='clear_lobby'),
]

urlpatterns += [
    path('packing_slip', views.packing_slip, name='packing_slip'),
    ]
