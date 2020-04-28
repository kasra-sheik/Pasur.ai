from socketIO_client import SocketIO
import sys 
import os
import json

from pasur_state import *
from card_dictionary import card_dict


class User():
    def __init__(self, user_id):
        self.current_hand = []
        self.user_id = user_id

        self.socketio = SocketIO("localhost", 5000)
        self.socketio.emit("join_game", self.user_id)

        self.socketio.on("deal", self.deal)
        self.socketio.on("action", self.action)
        self.socketio.on("test", self.test)

        self.socketio.connect()
        self.socketio.wait()

        # call join game

    def deal(self, new_hand):
        self.current_hand = new_hand
        hand = json.loads(new_hand)
        print(hand)
        for card in hand:
            print(card)
            tpl = (card["number"], card["suit"])
            getAscii(card_dict[tpl])


    def action(self, board, move, your_turn):
        pass
    def test(self, message):
        pass
        
    def is_valid_turn(card, board, locations):
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
     

class HumanUser(User):
    # TODO: grab chosen card + location + call is valid turn
    def make_move(self):
        index_chosen = input("choose a card")
        card_chosen = self.current_hand[index_chosen]
        return card_chosen

    def action(self, board, move, your_turn):
        if your_turn:            
            return self.make_move()
        else:
            print(board, move)

    def test(self, message):
        print(message)


def getAscii(file):
    path = "ascii-cards/{0}".format(file)
    f = open(path, "r")
    print(f.read())
    f.close()
    
human = HumanUser(sys.argv[1])
