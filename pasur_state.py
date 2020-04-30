'''
Kodiak Criprad
kconrad1@uw.edu
Passur Game State
'''

import random as r
import json
from flask.json import JSONEncoder

SUITS = ["S", "H", "C", "D"]

class Card:
    def __init__(self, number, suit): # initialized with suit as string
        self.number = number # no 0
        self.suit = suit

    def __str__(self):
        n=""
        if self.number == 1:
            n = "A"
        elif self.number <= 10:
            n = str(self.number)
        else:
            if self.number == 11: n = "J"
            if self.number == 12: n = "Q"
            if self.number == 13: n = "K"
        return n + self.suit

    def __repr__(self): 
        return str(self)

    def __eq__(self, other):
        return self.suit == other.suit and self.number == other.number

class Deck:
    def __init__(self):
        cards = []
        for suit in SUITS:
            for n in range(1, 14):
                card = Card(n, suit)
                cards.append(card)
        r.shuffle(cards)

        self.cards = cards
    def draw(self):
        card = self.cards.pop()
        return card
    def draw4(self):
        deal = []
        for _ in range(4):
            deal.append(self.draw())
        return deal
    def replace(self, card):
        i = r.randint(1, len(self.cards))
        self.cards.insert(i, card) 


class Board:
    def __init__(self, starting_cards):
        self.cards = starting_cards

    def remove(self, card_list):
        self.cards = [c for c in self.cards if c not in card_list]
    def add(self, card):
        self.cards.append(card)

    def __str__(self):
        print(str(self.cards))

class Move():

    def __init__(self):
        self.played = None
        self.taken = []

    def add_card_played(self, card):
        self.played = card

    def add_card_taken(self, card):
        self.taken += card

    def get_card(self):
        return self.played

    def get_taken(self):
        return self.taken
    def __str__(self):
        return("Card Played: {0} \nCard(s) Taken: {1}".format(str(self.played), str(self.taken)))



class PasurJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return { 'number' : obj.number, 'suit' : obj.suit}
        if isinstance(obj, Move):
            return { 'played': obj.played, 'taken' : obj.taken}
        # TODO: finish for other objects
        return json.JSONEncoder.default(self, obj) # default, if not Card object. 

def get_move_from_json(move_json):
    card_json = move_json['played']
    taken_json = move_json['taken']
    card = Card(card_json['number'], card_json['suit'])
    taken = [Card(card['number'], card['suit']) for card in taken_json]
    move = Move()
    move.played = card
    move.taken = taken
    return move

