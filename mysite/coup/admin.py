from django.contrib import admin

# Register your models here.
from .models import Player, Card, Action, Deck, Game, CardInstance, Function, Lobby
admin.site.register(Player)
admin.site.register(Card)
admin.site.register(Deck)
admin.site.register(Game)
admin.site.register(CardInstance)
admin.site.register(Lobby)


class FunctionInline(admin.TabularInline):
    model = Function
    extra = 1


# Define the admin class
class ActionAdmin(admin.ModelAdmin):
    inlines = [FunctionInline]


# Register the admin class with the associated model
admin.site.register(Action, ActionAdmin)
