from flask import Flask, jsonify
from flask.json import JSONEncoder
from flask_socketio import SocketIO, emit, join_room
import json

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from pasur_state import *


class PasurJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return { "number" : obj.number, "suit" : obj.suit}
        if isinstance(obj, Move):
            return { "played" : obj.played, "taken" : obj.taken}
        # TODO: finish for other objects
        return json.JSONEncoder.default(self, obj) # default, if not Card object. 


# GAME MANAGER

class Pasur():
    def __init__(self):
        self.ticker = 0 # how many moves left before new deal
        self.users = []
        self.deck = Deck()
        self.board = None
        self.last_move = None



    #################
    # Game LOGIC   #
    ################# 
    def turn(self, card, locations):
        move = Move()
        move.add_card_played(card)
        move.add_card_taken(locations)


    #################
    # NETWORK LOGIC #
    #################
    def add_users(self, user_id):
        self.users.append(user_id)

        if len(self.users) == 2:
            self.start_game()
        # randomize who goes first 
        # if two players are joined.. start game

    def deal(self):
        for user in self.users:
            new_cards = self.deck.draw4()
            data = json.dumps(new_cards, cls=PasurJSONEncoder, indent=4)
            socketio.emit("deal", data, room=user)

    def start_game(self):
        self.board = Board(self.deck.draw4())
        print(self.board.cards)
        self.prompt_action()
        pass

    def prompt_action(self): 
        print("ticker = {}".format(self.ticker))
        if self.ticker == 0:
            self.deal()
            self.ticker = 8
        turn_data = json.dumps((self.board.cards, self.last_move, True), cls=PasurJSONEncoder, indent=4)
        wait_data = json.dumps((self.board.cards, self.last_move, False), cls=PasurJSONEncoder, indent=4)
        if self.ticker % 2 == 0:
            socketio.emit("action", turn_data, room=self.users[0])
            socketio.emit("action", wait_data, room=self.users[1])
        else:
            socketio.emit("action", turn_data, room=self.users[1])
            socketio.emit("action", wait_data, room=self.users[0])
            pass
        self.ticker -= 1
        pass

pasur = Pasur()

app = Flask(__name__)
app.json_encoder = PasurJSONEncoder
socketio = SocketIO(app)

@socketio.on('receive_action')
def receive_action(self): 
        # update game state
        pasur.board = ""
        pasur.last_move = ""
        pasur.prompt_action()


@socketio.on('join_game')
def join_game(user):
    print("{} has connected!".format(user))
    join_room(user)
    pasur.add_users(user)
    # implement

    # if player length == 2 start the game 

@socketio.on('turn')
def turn(card):
    print("temp")


if __name__ == '__main__':
    socketio.run(app)