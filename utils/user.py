from socketIO_client import SocketIO
import sys 


# TODO: complete
def is_valid_turn(card, board, locations):
    if locations == []:
        # J
        if card.number == 11:
            return True

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
        print(new_hand)
        self.current_hand = new_hand

    def action(self, board, move, your_turn):
        pass
    def test(self, message):
        pass

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

    
human = HumanUser(sys.argv[1])
