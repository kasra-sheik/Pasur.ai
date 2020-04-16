#card_tester.py

from pasur_state import *

card1 = Card(2,2)
card2 = Card(12, 0)
card3 = Card(9,1)
card4 = Card(3, 2)

board = Board([card1, card2, card3, card4])

test_card_1 = Card(6, 2)
test_card_2 = Card(5, 2)
test_card_3 = Card(8, 3)
test_card_4 = Card(11, 1)
test_card_5 = Card(12, 0)


# is_valid_turn tests

#check jacks
print(is_valid_turn(test_card_4, board, []) == True)
print(is_valid_turn(test_card_4, board, [0]) == False)

#check if face card can go in empty slot 
print(is_valid_turn(test_card_5, board, []) == False)


#check if numbered card can go in empty spot
print(is_valid_turn(test_card_1, board, []) == False)
print(is_valid_turn(test_card_2, board, []) == True)
print(is_valid_turn(test_card_3, board, []) == False)


#check if face card can go in locations
print(is_valid_turn(test_card_5, board, [1]) == True)
print(is_valid_turn(test_card_5, board, [0]) == False)
print(is_valid_turn(test_card_5, board, [0, 1]) == False)


#check if numbered card can go in locations
print(is_valid_turn(test_card_1, board, [0, 3]) == True)
print(is_valid_turn(test_card_3, board, [3]) == True)
print(is_valid_turn(test_card_3, board, [0, 3]) == False)

