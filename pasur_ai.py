from socketIO_client import SocketIO
import sys 
import os
import json
from scipy import special

from pasur_state import *
from user import *
from card_dictionary import card_dict

PADDING = .02

class AIUser(User):

    def __init__(self, uid):
        self.my_cards = []
        self.other_cards = []
        self.deck = Deck()
        super().__init__(uid)

    def count_clubs(self):
        my_c = 0
        other_c = 0
        for card in self.my_cards:
            if card.suit == "C":
                my_c += 1
        for card in self.other_cards:
            if card.suit == "C":
                other_c += 1
        return [my_c, other_c]

    def value_clubs(self):
        # function that tells you how much a club is worth in the current game state
        num_clubs = self.count_clubs()
        if num_clubs[0] >= 7 or num_clubs[1] >= 7:
            return 0
        else:
            # TODO
            return 1


    def get_all_moves(self, board):
        move_list = []
        loc_list = self.powerset(range(len(board.cards)))
        for card in self.current_hand:
            for loc in loc_list:
                if self.is_valid_turn(card, board, loc):
                    move_list.append(self.make_move(card, board, loc))
        return move_list

    def move_heurisitic(self, move):
        val = 0.0
        if not move.taken:
            compliment = 0
            if move.played.number >=12:
                compliment = move.played.number
            else:
                compliment = 11 - move.played.number
            num_comps = 0
            # TODO need to subtract 1 from n when other player went first
            n = len(self.current_hand)
            cards_left = (len(self.deck.cards) + n)
            p = 1 / cards_left
            for card in self.deck.cards:
                if card.number == compliment:
                    num_comps += 1
                    val -= n*(p*(1-p)**(n-1))*(self.card_value(card))
            val -= (num_comps * p + PADDING)*self.card_value(move.played)
            # pad probability to account for jacks and multicard comps
            # in the case when there are no comps left in deck

            for card in self.current_hand:
                if card.number == compliment and card != move.played:
                    val += 0.2
                    # if card.suit == "C":
                    #     val += 0.8
                # TODO run a couple times and pick a better constant
        
        else: 
            val += 0.1 # TODO find better constant
            for card in move.taken:
                val += self.card_value(card)

        # TODO check Sur logic

        return val
                

    def card_value(self, card):
        val = 0
        if card.suit == "C" and card.number != 11:
            val += self.value_clubs()
        if card.number == 10 and card.suit == "D":
            val += 3
        if card.number == 2 and card.suit == "C":
            val += 2
        if card.number == 1:
            val += 1
        return val

    def powerset(self, locs):
        length = len(locs)
        p_set = []
        for i in range(1 << length):
            p_set.append([locs[j] for j in range(length) if (i & (1 << j))])
        return p_set


    def action(self, game_state):
        board_cards = [Card(card['number'], card['suit']) for card in game_state[0]]
        board = Board(board_cards)
        print(self.current_hand)
        # make move
        if game_state[1]:
            print("my move")
            move_list = self.get_all_moves(board)
            best_move = (-1.0, None)
            for move in move_list:
                val = self.move_heurisitic(move)
                print(move, val)
                if val > best_move[0]:
                    best_move  = (val, move)
            print(best_move)
            move_data = json.dumps(best_move[1], cls=PasurJSONEncoder, indent=4)
            self.socketio.emit('player_action', move_data)
            self.current_hand.remove(best_move[1].played)
        else:
            pass

        # game_state[0] -> board.cards
        # game_state[1] -> last_move
        # game_state[2] -> your_turn


        pass

    def receive_move(self, move_json, my_move):
        move = get_move_from_json(move_json)
        if my_move:
            self.my_cards.extend(move.taken)
        else:
            self.other_cards.extend(move.taken)
        self.deck.remove(move.taken)
        pass

    def deal(self, hand):
        # accept cards and put into hand
        self.current_hand = [Card(card['number'], card['suit']) for card in hand]
        self.deck.remove(self.current_hand)


    def result(self, data):
        # receive result after game
        pass
if __name__ == '__main__':
    ai = AIUser(sys.argv[1])