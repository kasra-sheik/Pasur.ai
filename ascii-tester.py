from pasur_state import *
from user import getAscii
from server import PasurJSONEncoder
import json
from card_dictionary import card_dict

card1 = Card(2,0)
card2 = Card(12, 1)
card3 = Card(9,2)
card4 = Card(3, 3)

c_list = [card1, card2, card3, card4]
data = json.loads(json.dumps(c_list, cls=PasurJSONEncoder, indent=4))


getAscii(data)