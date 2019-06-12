import pickle
import json

from util.card_definitions import CardDefinitions

'''
Returns a list of valid actions given a state
'''
def getValidActionsInState(state):
	# can always do nothing
	actions = [{
		"action": "pass"
	}]

	# add drawing action based on SP
	if state.internal.status == "draw" and state.external.sp >= 2:
		actions.append({
			"action": "draw"
		})

	# add actions for playing cards based on SP
	for card in state.internal.cards:
		targets = []
		if card.type == "cocktail":
			targets = ["l", "r"]
		elif card.type == "snack":
			targets = ["s"]
		actions.extend([{
			"action": "card",
			"card_id": card.id,
			"target": target
		} for target in targets])

	return actions

'''
Finds the closest state to the state passed in.
Works by selecting a random set of already-observed
states from q and computing the closest.
'''
def getClosestObservedState(state, q, tries=100):
	# TODO implement
	pass

'''
Minify an action to a unique string
'''
def compressAction(action):
	return json.dumps({
		"a": action.action,
		"c": action.card_id,
		"t": {
			"d": action.target.direction,
			"p": action.target.p
		}
	})

'''
Decompress a compressed action
'''
def decompressAction(compressed_action):
	action = json.loads(compressed_action)
	return {
		"action": action.a,
		"card_id": action.c
		"target": {
			"direction": action.t.d,
			"p": action.t.p
		} if action.t else None
	}

'''
Minify a state object to a unique string. Leaves out player ids
TODO my god, use a database
'''
def compressState(state):
	def minifyGlobalState(global_state):
		return {
			"t": global_state.turn,
			"m": global_state.musician.id,
		}

	def minifyInternalState(internal_state):
		return {
			"s": internal_state.status
			"c": sorted([card.id for card in internal_state.cards]),
		}

	def minifyExternalState(external_state):
		return {
			"h": external_state.hp,
			"p": external_state.hp_until_max,
			"s": external_state.sp,
			"m": external_state.max_sp,
			"t": external_state.treasures,
			"a": external_state.answers,
			"c": 0 if external_state.has_secrets_in_hand else 1,
			"d": 0 if external_state.has_facedown_cards else 1,
			"f": 0 if external_state.is_friend else 1
		}

	return json.dumps({
		"g": minifyGlobalState(state.g),
		"i": minifyInternalState(state.internal),
		"e": minifyExternalState(state.external),
		"l": minifyExternalState(state.left),
		"r": minifyExternalState(state.right),
	}, separators=(',',':'))

'''
Decompress a compressed state
TODO my god, use a database
'''
def decompressState(compressed_state):
	# TODO implement
	pass

qTableFileLocation = "data/q"
'''
Load the q table from a file to memory
'''
def loadQTableFromFile():
	q = None
	try:
		with open(qTableFileLocation, "rb") as file:
			q = pickle.load(file)
	except FileNotFoundError:
		# qTableFileLocation doesnt't exist yet, return a new q table
		return {}
	return q
'''
Save the q table to a file
'''
def saveQTableToFile(q):
	with open(qTableFileLocation, "wb") as file:
		pickle.dump(q, file)

cardsTableFileLocation = "data/cards.json"
'''
Load the card definitions
'''
def loadCardDefinitions():
	cards = None
	with open(cardsTableFileLocation, "r") as file:
		cards = json.load(file)
	return cards

charactersArrayFileLocation = "data/characters.json"
'''
Load the character definitions
'''
def loadCharacterDefinitions():
	characters = None
	with open(charactersArrayFileLocation, "r") as file:
		characters = json.load(file)
	return characters
