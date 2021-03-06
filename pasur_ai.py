from socketIO_client import SocketIO
import sys 
import os
import json
from scipy import special

from pasur_state import *
from user import *
from card_dictionary import card_dict

PADDING = .1
EMPTY_BOARD_CONSTANT = 1.5
CARDS_TAKEN_CONSTANT = 0.1
PLAYED_JACK_CONSTANT = -0.8
HAVE_COMPLIMENT_CONSTANT = 0.8
CARD_EXISTS_CONSTANT = 0.3

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
            return 1.5

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

    def get_compliment(self, card):
        compliment = 0
        if card.number >= 12:
            compliment = card.number
        else:
            compliment = 11 - card.number
        return compliment

    def compliment_probability(self, compliment):
        prob = 0
        num_comps = 0
        n = len(self.current_hand)
        # TODO need to subtract 1 from n when other player went first
        cards_left = (len(self.deck.cards) + n)
        for card in self.deck.cards:
            if card.number == compliment:
                num_comps += 1
        p = num_comps / cards_left

        return n*(p*(1-p)**(n-1))

    def powerset(self, locs):
        length = len(locs)
        p_set = []
        for i in range(1 << length):
            p_set.append([locs[j] for j in range(length) if (i & (1 << j))])
        return p_set

    def get_all_moves(self, board):
        move_list = []
        loc_list = self.powerset(range(len(board.cards)))
        for card in self.current_hand:
            for loc in loc_list:
                if self.is_valid_turn(card, board, loc):
                    move_list.append(self.make_move(card, board, loc))
        return move_list

    # board is the board of cards on the board BEFORE the move
    def move_heurisitic(self, move, board):
        val = 0.0
        board_after_move = [c for c in board.cards if c not in move.taken]
        ##############
        # Move Logic #
        ##############

        if not move.taken:
            compliment = self.get_compliment(move.played)
            board_after_move.append(move.played)
            # subtract the expected value of the other player taking the card you played
            comp_value = 0
            for card in self.deck.cards:
                if card.number == compliment:
                    comp_value += self.card_value(card)
            val -= self.compliment_probability(compliment) * (self.card_value(move.played) + comp_value)
            if move.played.number < 11:
                val -= PADDING * self.card_value(move.played)
            # pad probability to account for jacks and multicard comps
            # face cards dont need padding
            for card in board.cards:
                if move.played.number == card.number:
                    val += CARD_EXISTS_CONSTANT
        
        else: 
            val += CARDS_TAKEN_CONSTANT
            if move.played.number == 11:
                val += PLAYED_JACK_CONSTANT
            for card in move.taken:
                val += self.card_value(card)

        # check the board for remaining compliments in hand
        for b_c in board_after_move:
            for card in self.current_hand:
                if card.number == self.get_compliment(b_c) and card != move.played:
                    val += HAVE_COMPLIMENT_CONSTANT * (self.card_value(b_c) +  self.card_value(card))

        #############
        # Sur Logic #
        #############
        if len(board_after_move) == 0 and move.played.number != 11:
            val += 5
        elif len(board_after_move) == 0:
            val += EMPTY_BOARD_CONSTANT
            # TODO: find better constant
        elif len(board_after_move) == 1:
            compliment = self.get_compliment(board_after_move[0])
            val -= self.compliment_probability(compliment) * 5
            pass
        else: # at least 2 cards on the board
            board_sum = 0
            for card in board_after_move:
                board_sum += card.number
            if board_sum < 11:
                val -= self.compliment_probability(11 - board_sum) * 5

        print("Move: {}".format(move))
        print("Board after move: {}".format(board_after_move))
        return val

    def action(self, game_state):
        # game_state[0] -> board.cards
        # game_state[1] -> last_move
        # game_state[2] -> your_turn

        board_cards = [Card(card['number'], card['suit']) for card in game_state[0]]
        board = Board(board_cards)

        # make move
        if game_state[1]:
            print("\n My turn \n My hand: {} \n".format(self.current_hand))
            move_list = self.get_all_moves(board)
            best_move = (-1.0, None)
            for move in move_list:
                val = self.move_heurisitic(move, board)
                print("Move Value: {} \n".format(val))
                if val > best_move[0]:
                    best_move  = (val, move)
            print("Made Move: {}".format(best_move[1]))
            move_data = json.dumps(best_move[1], cls=PasurJSONEncoder, indent=4)
            self.socketio.emit('player_action', move_data)
            self.current_hand.remove(best_move[1].played)
        else:
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