from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('start', views.startgame, name='startGame'),
]
urlpatterns += [
    path('showTable', views.showtable, name='showTable'),
]

urlpatterns += [
    path('showDeck', views.showdeck, name='showDeck'),
]

urlpatterns += [
    path('initialDeal', views.initialdeal, name='initialDeal'),
]

urlpatterns += [
    path('shuffle', views.shuffle, name='shuffle'),
]

urlpatterns += [
    path('actions', views.actions, name='actions'),
]

urlpatterns += [
    path('loseinfluence', views.loseinfluence, name='loseinfluence'),
]
urlpatterns += [
    path('lose_one_card', views.lose_one_card, name='lose_one_card'),
]
