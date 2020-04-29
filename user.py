from socketIO_client import SocketIO
import sys 
import os
import json

from pasur_state import *
from card_dictionary import card_dict

CARD_HEADER = "    ({})     "
INSTR_1 = "Input the number of the Card you want to play"
INSTR_2 = ("Input the location(s) you want to put it seperated by spaces \n"
           "or press enter to place in a new location")

class User():
    def __init__(self, user_id):
        self.current_hand = []
        self.user_id = user_id

        self.socketio = SocketIO("localhost", 5000)
        self.socketio.emit("join_game", self.user_id)

        self.socketio.on("deal", self.deal)
        self.socketio.on("action", self.action)

        self.socketio.connect()
        self.socketio.wait()

        # call join game

    def deal(self, new_hand):
        pass

    def action(self, data):
        pass

class HumanUser(User):
    # TODO: grab chosen card + location + call is valid turn

    def make_move(self):
        index_chosen = input("choose a card")
        card_chosen = self.current_hand[index_chosen]
        return card_chosen

    def deal(self, new_hand):
        hand = json.loads(new_hand)
        self.current_hand = [Card(card['number'], card['suit']) for card in hand]
        # print("Your hand")
        # printAscii(self.current_hand)

    def action(self, data):
        game_state = json.loads(data)
        # game_state[0] -> board.cards
        # game_state[1] -> last_move
        # game_state[2] -> your_turn

        board_cards = [Card(card['number'], card['suit']) for card in game_state[0]]
        board = Board(board_cards)
        print("Board")
        for i in range(len(board.cards)):
            print(CARD_HEADER.format(str(i+1)), end = '')
        print(CARD_HEADER.format(" "))
        printAscii(board_cards)
        print("Your hand")
        for i in range(len(self.current_hand)):
            print(CARD_HEADER.format(str(i)), end = '')
        print()
        printAscii(self.current_hand)
        if game_state[2]: 
            print(INSTR_1)
            card_num = int(input())
            card = self.current_hand[card_num]
            print(INSTR_2)
            l = input()
            locs = [int(x) for x in l.split()]
            print(locs)
            print(is_valid_turn(card, board, locs))

        
def is_valid_turn(card, board, locations):
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
            return not checkSum(number_list, compliment, len(number_list))
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


#subset sum problem, finally get to use DP in real life!!!
def checkSum(number_list, sum, n):
    if sum == 0: # base case where we have reached sum
        return True
    elif n == 0: # base case where we did not reach sum
        return False 
    elif number_list[n-1] > sum: # number is larger than sum
        return checkSum(number_list, sum, n-1)
    else: 
        return checkSum(number_list, sum, n-1) or checkSum(number_list, sum - number_list[n-1], n-1)


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
    
human = HumanUser(sys.argv[1])
