from socketIO_client import SocketIO
import sys 
import os
import json

from pasur_state import *
from card_dictionary import card_dict

CARD_HEADER = "    ({})     "
INSTR_1 = "Input the index of the Card you want to play "
INSTR_2 = ("Input the location(s) you want to place it seperated by spaces \n"
           "or press enter to place in a new location ")

class User():
    def __init__(self, user_id):
        self.current_hand = []
        self.user_id = user_id

        self.socketio = SocketIO("localhost", 5000)
        self.socketio.emit("join_game", self.user_id)

        self.socketio.on("deal", self.deal)
        self.socketio.on("action", self.action)
        self.socketio.on("receive_move", self.receive_move)
        self.socketio.on("result", self.result)

        self.socketio.connect()
        self.socketio.wait()

        # call join game

    def result(self, data):
        print(data)

    def deal(self, hand):
        # accept cards and put into hand
        self.current_hand = [Card(card['number'], card['suit']) for card in hand]

    def action(self, data):
        pass

    def receive_move(self, move_json, my_move):
        pass

    def make_move(self, card, board, locations):
        move = Move()
        move.played = card
        if card.number == 11:
            move.taken = [c for c in board.cards if c.number < 12]
            move.taken.append(card)
        elif not locations: # placed card on board
            move.taken = []
        else: #not jack, not empty
            move.taken = [card]
            move.taken.extend([board.cards[loc] for loc in locations])
        return move

    def is_valid_turn(self, card, board, locations):
        # card is type Card
        # board is type Board
        # locations is a list
        if locations == []:
            # Jack
            if card.number == 11:
                return True

            # Q, K
            elif card.number > 11:
                # return fasle if that same card number is on the board
                return not card.number in [board_card.number for board_card in board.cards]

            # Numbered Card
            else:
                compliment = 11 - card.number 
                number_list = [board_card.number for board_card in board.cards if board_card.number < 11]
                return not self.checkSum(number_list, compliment, len(number_list))
        else:
            for loc in locations:
                if loc >= len(board.cards):
                    return False
            # J
            if card.number == 11:
                return False

            # Q, K
            elif card.number > 11:

                if len(locations) > 1:
                    return False
                else:
                    return card.number == board.cards[locations[0]].number

            # Numbered Card
            else:
                return 11 == card.number + sum(board.cards[loc].number for loc in locations)

    #subset sum problem
    def checkSum(self, number_list, sum, n):
        if sum == 0: # base case where we have reached sum
            return True
        elif n == 0: # base case where we did not reach sum
            return False 
        elif number_list[n-1] > sum: # number is larger than sum
            return self.checkSum(number_list, sum, n-1)
        else: 
            return self.checkSum(number_list, sum, n-1) or self.checkSum(number_list, sum - number_list[n-1], n-1)

class HumanUser(User):

    def deal(self, hand):

        self.current_hand = [Card(card['number'], card['suit']) for card in hand]
        # print("Your hand")
        # printAscii(self.current_hand)


    def receive_move(self, move_json, my_move):
        # receive previious move from server
        move = get_move_from_json(move_json)
        if not my_move:
            print("Opponent made move \n{}".format(str(move)))
        else:
            print("You made move \n{}".format(str(move)))
        print()

    def action(self, game_state):
        # make move
        # game_state[0] -> board.cards
        # game_state[1] -> your_turn

        board_cards = [Card(card['number'], card['suit']) for card in game_state[0]]
        board = Board(board_cards)
        print("Board")
        for i in range(len(board.cards)):
            print(CARD_HEADER.format(str(i)), end = '')
        print(CARD_HEADER.format(" "))
        printAscii(board_cards)
        print("Your hand")
        for i in range(len(self.current_hand)):
            print(CARD_HEADER.format(str(i)), end = '')
        print()
        printAscii(self.current_hand)
        if game_state[1]: 
            can_move = False
            while not can_move:
                try:
                    card_index = int(input(INSTR_1))
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    continue
                if card_index >= len(self.current_hand):
                    continue
                card = self.current_hand[card_index]
                try:
                    locs = input(INSTR_2)
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    continue
                locations = [int(x) for x in locs.split()]
                can_move = self.is_valid_turn(card, board, locations)
                if not can_move:
                    print("Invalid Move. Please try again")
                else:
                    print()
                    move = self.make_move(card, board, locations)
                    move_data = json.dumps(move, cls=PasurJSONEncoder, indent=4)
                    self.socketio.emit('player_action', move_data)
                    self.current_hand.remove(card)
            
# end of Human_User

def printAscii(cards):
    files = []
    for card in cards:
            file = card_dict[(card.number, card.suit)]
            path = "ascii-cards/{0}".format(file)
            files.append(open(path, "r"))
    for rows in zip(*files):
        for x in rows:
            print(x.strip("\n"), end = " ")
        print()
    for file in files:
        file.close()
  
if __name__ == '__main__':  
    human = HumanUser(sys.argv[1])
