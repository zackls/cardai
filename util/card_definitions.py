
'''
The purpose of this class is mainly to make querying for cards easy.
'''
class CardDefinitions:
	@classmethod
	def setDefinitions(cls, main, treasures, answers):
		cls.cards = []
		cls.definitions = {
			"main": [],
			"treasures": [],
			"answers": []
		}
		for deck in [main, treasures, answers]:
			for card in deck:
				card.id = len(cls.defintions)
				cls.definitions.append(card)
				# cards which are duplicated are just multiple references to the same card
				cls.cards.append([card for _ in range(card.count)])

	@classmethod
	def getCardById(cls, card_id):
		if card_id == None:
			return None
		return cls.cards[card_id]

