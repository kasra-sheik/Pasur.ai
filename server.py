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
        self.surs = 0
        self.points = 0

    def count_points(self):
        pts = 0
        clubs = 0
        for card in self.cards:
            if card.number == 11:
                pts += 1
            if card.number == 1:
                pts += 1
            if card.suit == "C":
                clubs +=1
            if card.suit == "C" and card.number == 2:
                pts += 2
            if card.suit == "D" and card.number == 10:
                pts += 3
        if clubs >= 7:
            pts += 7
        self.points += pts + (5 * self.surs)
        self.surs = 0
        return self.points


class Pasur():
    def __init__(self):
        self.ticker = 48 # how many moves left
        self.users = {} # map from uids to users
        self.uids = [] # list of uids to maintain order
        self.deck = Deck()
        self.board = None
        self.last_taken = None


    def add_users(self, uid):
        user = Player(uid)
        self.users[uid] = user
        self.uids.append(uid)
        if len(self.users) == 2:
            self.start_game()

        # TODO: randomize who goes first 

    def start_game(self):
        cards = self.deck.draw4()
        if REPALCE_JACKS:
            for card in cards:
                print(card)
                if card.number == 11:
                    self.deck.replace(card)
                    cards.remove(card)
                    cards.append(self.deck.draw())
        self.board = Board(cards)
        print(self.board.cards)
        self.prompt_action()
        pass

    def allocate_last_cards(self):
        self.last_taken.cards.extend(self.board.cards)

    def next_round(self):
        points = []
        threshold = False
        for i in self.uids:
            pts = self.users[uid].count_points()
            points.append(pts)
            if pts >= FINAL_SCORE:
                threshold = True
        if threshold and points[0] != points[1]:
            self.declare_winner(points)
        self.start_game()

    def declare_winner(self, points):
        # uids[0] has points[0] amount of points
        winner_index = points.index(max(points))
        loser_index = (winner_index + 1) % 2
        winner_uid = self.uids[winner_index]
        winner_pts = points[winner_index]
        loser_uid = self.uids[loser_index]
        loser_pts = points[loser_index]
        result ="Player {0} has won the game!\nFinal Score: {0}:{1}, {2}:{3}\n"
        result.format(winner_uid, winner_pts, loser_uid, loser_pts)
        socketio.emit("result", result, room=self.uids[0])
        socketio.emit("result", result, room=self.uids[1])

    def prompt_action(self): 
        print("ticker = {}".format(self.ticker))
        print(self.board.cards)
        if self.ticker % 8 == 0:
            self.deal()
        turn_data = json.loads(json.dumps((self.board.cards, True), cls=PasurJSONEncoder, indent=4))
        wait_data = json.loads(json.dumps((self.board.cards, False), cls=PasurJSONEncoder, indent=4))
        if self.ticker % 2 == 0:
            socketio.emit("action", turn_data, room=self.uids[0])
            socketio.emit("action", wait_data, room=self.uids[1])
        else:
            socketio.emit("action", turn_data, room=self.uids[1])
            socketio.emit("action", wait_data, room=self.uids[0])
        pass

    def deal(self):
        for user in self.uids:
            new_cards = self.deck.draw4()
            data = json.loads(json.dumps(new_cards, cls=PasurJSONEncoder, indent=4))
            socketio.emit("deal", data, room=user)

pasur = Pasur()
REPALCE_JACKS = True
FINAL_SCORE = 30

app = Flask(__name__)
app.json_encoder = PasurJSONEncoder
socketio = SocketIO(app)

@socketio.on('player_action')
def player_action(data): 
    move_json = json.loads(data)
    move = get_move_from_json(move_json)
    user_index = pasur.ticker % 2
    player = pasur.users[pasur.uids[user_index]]
    print(player.uid)
    if not move.taken:
        pasur.board.add(move.played)
    else:  
        pasur.board.remove(move.taken)
        pasur.last_taken = player
    print(move)
    if (move.played.number != 11 and not pasur.board.cards):
        player.surs += 1
    player.cards.extend(move.taken)
    socketio.emit('receive_move', (move_json, True), room=pasur.uids[user_index])
    socketio.emit('receive_move', (move_json, False), room=pasur.uids[(user_index+1)%2])
    pasur.ticker -= 1
    if pasur.ticker == 0:
        pasur.allocate_last_cards()
        pasur.next_round()
    else:
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


if __name__ == '__main__':
    socketio.run(app)