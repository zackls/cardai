
'''
The Deck class holds logic related to storing, drawing, and shuffling cards.
'''
class Deck:
	'''
	Initialize a new deck. Cards is a list of card definitions
	'''
	def __init__(self, cards, name):
		self.cards = cards
		self.name = name

	'''
	Return the top card from the deck.
	'''
	def draw(self):
		# TODO implement
		pass

	'''
	Shuffle the deck to get an approximately random ordering.
	'''
	def shuffle(self):
		# TODO implement
		pass

	'''
	Return the top card from the deck.
	'''
	def topCardIsASecret(self):
		# TODO implement once secrets have been designed
		return False
