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


class DatabaseHelpers:
	"""
	STATES
	"""
	globalStateFields = [
		("turn", "TINYINT", "NOT NULL"),
		("musician_card_id", "TINYINT", ""),
	]
	internalStateFields = [
		("card_ids", "VARCHAR(64)", "NOT NULL"),
		("status", "VARCHAR(8)", "NOT NULL"),
	]
	externalStateFields = [
		("hp", "TINYINT", "NOT NULL"),
		("hp_until_max", "TINYINT", "NOT NULL"),
		("sp", "TINYINT", "NOT NULL"),
		("max_sp", "TINYINT", "NOT NULL"),
		("treasures", "TINYINT", "NOT NULL"),
		("answers", "TINYINT", "NOT NULL"),
		("has_secrets_in_hand", "BOOLEAN", "NOT NULL"),
		("has_facedown_cards", "BOOLEAN", "NOT NULL"),
		("num_cards", "TINYINT", "NOT NULL"),
		("is_friend", "BOOLEAN", "NOT NULL"),
	]
	stateFields = [
		*globalStateFields,
		*internalStateFields,
		*externalStateFields,
		*[("left_{}".format(field), datatype, constraints) for field, datatype, constraints in externalStateFields],
		*[("right_{}".format(field), datatype, constraints) for field, datatype, constraints in externalStateFields],
	]
	stateFieldsList = ",".join([field for field, _, _ in stateFields])

	@staticmethod
	def _globalStateToRow(global_state):
		return ",".join([
			global_state.turn,
			global_state.musician.id if global_state.musician else None,
		])
	@staticmethod
	def _internalStateToRow(internal_state):
		return ",".join([
			",".join(sorted([card.id for card in internal_state.cards])),
			internal_state.status,
		])
	@staticmethod
	def _externalStateToRow(external_state):
		return ",".join([
			external_state.hp,
			external_state.hp_until_max,
			external_state.sp,
			external_state.max_sp,
			external_state.treasures,
			external_state.answers,
			external_state.has_secrets_in_hand,
			external_state.has_facedown_cards,
			external_state.is_friend
		])
	@staticmethod
	def stateToRow(state):
		return ",".join([
			DatabaseHelpers._globalStateToRow(state.g),
			DatabaseHelpers._internalStateToRow(state.internal),
			DatabaseHelpers._externalStateToRow(state.external),
			DatabaseHelpers._externalStateToRow(state.left),
			DatabaseHelpers._externalStateToRow(state.right),
		])

	"""
	ACTIONS
	"""
	actionFields = [
		("action", "VARCHAR(4)", "NOT NULL"),
		("card_id", "TINYINT", ""),
		("target", "VARCHAR(1)", "")
	]
	actionFieldsList = ",".join([field for field, _, _ in actionFields])

	@staticmethod
	def actionToRow(action):
		return ",".join([
			action.action,
			action.card.id if action.card else None,
			action.target,
		])
	@staticmethod
	def rowToAction(row):
		return {
			"action": row[0],
			"card": CardDefinitions.getCardById(row[1]),
			"target": row[2]
		}