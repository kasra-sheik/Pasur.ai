from socketIO_client import SocketIO
import sys 
import os
import json

from pasur_state import *
from user import *
from card_dictionary import card_dict


class AIUser(User):

    def __init__(self, uid):
        super().__init__(self, uid)
        self.my_cards = []
        self.other_cards = []

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
        loc_list = powerset(range(len(board.cards)))
        for card in self.current_hand:
            for loc in loc_list:
                if self.is_valid_turn(card, board, loc):
                    move_list.append(self.make_move(card, board, loc))
        return move_list

    def move_heurisitic(self, move):
        val = 0.0
        if move.taken = []:
            if move.played.suit == "C"
                val -= 0.5
                compliment = 11 - move.played.number
                if compliment in [card.number for card in self.current_hand]:
                    val += 0.2
        else: 
            for card in move.taken:
                if card.suit == "C":
                    val += self.value_clubs()
                if card.number == 10 and card.suit == "D":
                    val += 3
                if card.number == 2 and card.suit == "C":
                    val += 2



    @staticmethod
    def powerset(locs):
        length = len(locs)
        p_set = []
        for i in range(1 << length):
            p_set.append([locs[j] for j in range(length) if (i & (1 << j))])
        return p_set

    def action(self, data):
        # make move 

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
        pass

    def result(self, data):
        # receive result after game
        pass
if __name__ == '__main__':
    ai = AIUser(sys.argv[1])