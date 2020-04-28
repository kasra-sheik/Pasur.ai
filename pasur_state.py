'''
Kodiak Criprad
kconrad1@uw.edu
Passur Game State
'''

import random

SUITS = ["S", "H", "C", "D"]

class Card:

    def __init__(self, number, suit): # initialized with suit as index
        self.number = number # no 0
        self.suit = suit

    def __str__(self):
        n=""
        if self.number == 1: n = "A"
        elif self.number < 10:
            n = str(self.number)
        else:
            if self.number == 11: n = "J"
            if self.number == 12: n = "Q"
            if self.number == 13: n = "K"
        return n + " of " + self.suit

    def __repr__(self): 
        return str(self)

    def __eq__(self, other):
        return self.suit == other.suit and self.number == other.number

class Deck:
    def __init__(self):
        deck = []
        for suit in SUITS:
            for n in range(1, 14):
                card = Card(n, suit)
                deck.append(card)
        random.shuffle(deck)

        self.deck = deck
    def draw(self):
        card = self.deck.pop()
        return card
    def draw4(self):
        deal = []
        for _ in range(4):
            deal.append(self.draw())
        return deal

class Board:
    def __init__(self, starting_cards):
        self.cards = starting_cards

    def remove(self, card_list):
        for card in card_list:
            if not (card in self.cards):
                print("error")
            else:
                self.cards.remove(card)

    def add(self, card):
        self.cards += card

    def __str__(self):
        print(self.cards)

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




# class Passur_State:

#   def __init__(self, deck, board, players):
#       self.deck = deck
#       self.board = board
#       self.players = players

#   def __str__(self):
#       for x in board:
#           print(x)
#       print("There are " + str(len(self.deck)) + " cards left")

#   def __eq__(self, other):

#   def __hash__(self):

#   def copy(self):

#   def goal_test(s):

# class Operator:
#   def __init__(self, name, precond, state_transf):
#       self.name = name
#       self.precond = precond
#       self.state_transf = state_transf

#   def is_applicable(self, s):
#       return self.precond(s)

#   def apply(self, s):
#       return self.state_transf(s)

# GOAL_TEST = lambda s: goal_test(s)