from flask import Flask, jsonify
from flask.json import JSONEncoder
from flask_socketio import SocketIO, emit, join_room
import json

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from pasur_state import *

# GAME MANAGER

class Player():
    def __init__(self, uid):
        self.uid = uid
        self.cards = []

    def count_points(self):
        # TODO: implement
        pass


class Pasur():
    def __init__(self):
        self.ticker = 0 # how many moves left before new deal
        self.users = {} # map from uids to users
        self.uids = [] # list of uids to maintain order
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
    def add_users(self, uid):
        user = Player(uid)
        self.users[uid] = user
        self.uids.append(uid)
        if len(self.users) == 2:
            self.start_game()

        # TODO: randomize who goes first 

    def deal(self):
        for user in self.uids:
            new_cards = self.deck.draw4()
            data = json.loads(json.dumps(new_cards, cls=PasurJSONEncoder, indent=4))
            socketio.emit("deal", data, room=user)

    def start_game(self):
        cards = self.deck.draw4()
        # for card in cards:
        #     if card.number == 11:
        #         card = self.deck.replace(card)
        self.board = Board(cards)
        print(self.board.cards)
        self.prompt_action()
        pass

    def prompt_action(self): 
        print("ticker = {}".format(self.ticker))
        print(self.board.cards)
        if self.ticker == 0:
            self.deal()
            self.ticker = 8
        turn_data = json.loads(json.dumps((self.board.cards, self.last_move, True), cls=PasurJSONEncoder, indent=4))
        wait_data = json.loads(json.dumps((self.board.cards, self.last_move, False), cls=PasurJSONEncoder, indent=4))
        if self.ticker % 2 == 0:
            socketio.emit("action", turn_data, room=self.uids[0])
            socketio.emit("action", wait_data, room=self.uids[1])
        else:
            socketio.emit("action", turn_data, room=self.uids[1])
            socketio.emit("action", wait_data, room=self.uids[0])
            pass
        pass

pasur = Pasur()

app = Flask(__name__)
app.json_encoder = PasurJSONEncoder
socketio = SocketIO(app)

@socketio.on('player_action')
def player_action(data): 
    move_json = json.loads(data)
    print(move_json)
    move = get_move_from_json(move_json)
    if not move.taken:
        pasur.board.add(move.played)
    else:  
        pasur.board.remove(move.taken)
    pasur.last_move = move
    print(move)

    user_index = pasur.ticker % 2
    # first prompt was sent to index 0, so we want to update that users cards
    pasur.users[pasur.uids[user_index]].cards.extend(move.taken)
    socketio.emit('broadcast_move', (move_json, True), room=pasur.uids[user_index])
    socketio.emit('broadcast_move', (move_json, False), room=pasur.uids[(user_index+1)%2])
    pasur.ticker -= 1
    pasur.prompt_action()



@socketio.on('join_game')
def join_game(user):
    print("{} has connected!".format(user))
    if not user in pasur.users.keys():
        join_room(user)
        pasur.add_users(user)
    else:
        print("error, uid already exists")
        # implement rebraodcasting to change uid

@socketio.on('turn')
def turn(card):
    print("temp")


if __name__ == '__main__':
    socketio.run(app)