from flask import Flask
from flask_socketio import SocketIO, emit, join_room

from pasur_state import *

app = Flask(__name__)
socketio = SocketIO(app)

# @socketio.on('hello')
# def test_message(message):
#     print("hey we got a hello")
#     print(message)
#     emit({'response' : message})

# GAME MANAGER
class Pasur():
    def __init__(self):
        self.users = []
        self.deck = Deck()
        self.board = None



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
            socketio.emit("deal", new_cards, room=user)

    def start_game(self):
        #pull 12 cards, 
        self.deal()
        self.board = Board(self.deck.draw4())

        pass

pasur = Pasur()

@socketio.on('join_game')
def join_game(user):
    print("{} has connected!".format(user))
    join_room(user)
    pasur.add_users(user)
    # implement

    # if player length == 2 start the game 

@socketio.on('turn')
def turn(card):







if __name__ == '__main__':
    socketio.run(app)