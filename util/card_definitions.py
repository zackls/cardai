
'''
The purpose of this class is mainly to make querying for cards easy.
'''
class CardDefinitions:
	@classmethod
	def setDefinitions(cls, main, treasures, answers):
		cls.definitions = []
		cls.cards = {
			"main": [],
			"treasures": [],
			"answers": []
		}
		for deck, name in [(main, "main"), (treasures, "treasures"), (answers, "answers")]:
			for card in deck:
				card["id"] = len(cls.definitions)
				cls.definitions.append(card)
				# cards which are duplicated are just multiple references to the same card
				cls.cards[name].extend([card for _ in range(card["count"])])

	@classmethod
	def getCardById(cls, card_id):
		if card_id == None:
			return None
		return cls.definitions[card_id]

