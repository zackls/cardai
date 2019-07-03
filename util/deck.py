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
		self.original_cards = cards
		self.cards = []

	'''
	Return the top card from the deck, refilling the cards if necessary.
	'''
	def draw(self):
		if len(self.cards) == 0:
			self.cards = [card for card in self.original_cards]
			self.shuffle()
		return self.cards.pop()

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
