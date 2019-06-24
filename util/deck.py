import numpy as np

'''
The Deck class holds logic related to storing, drawing, and shuffling cards.
'''
class Deck:
	'''
	Initialize a new deck. Cards is a list of card definitions
	'''
	def __init__(self, cards):
		# create shallow copy of cards
		self.cards = [card for card in cards]

	'''
	Return the top card from the deck.
	'''
	def draw(self):
		return self.cards.pop()

	'''
	Add a card to the top of the deck.
	'''
	def add(self, card):
		self.cards.append(card)

	'''
	Shuffle the deck to get an approximately random ordering.
	'''
	def shuffle(self):
		np.random.shuffle(self.cards)

	'''
	Return the top card from the deck.
	'''
	def topCardIsASecret(self):
		# TODO implement once secrets have been designed
		return False
