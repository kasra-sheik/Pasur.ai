class Move():

    def __init__(self):
        self.played = None
        self.taken = []

    def add_card_played(self, card):
        self.played = card

    def add_card_taken(self, card):
        self.taken += card

    def get_card(self):
        return self.played

    def get_taken(self):
        return self.taken

