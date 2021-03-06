import pickle
import json

from util.constants import game_constants, state_adjacency_constants

'''
Returns a list of valid actions given a state
'''
def getValidActionsInState(state):
	# can always do nothing
	actions = [{
		"action": "pass"
	}]

	# add drawing action based on SP
	if (state["internal"]["status"] == "draw" or state["internal"]["status"] == "wait") and state["external"]["sp"] >= game_constants["sp_per_card"]:
		actions.append({
			"action": "draw"
		})

	# add actions for playing cards based on SP
	for card in state["internal"]["cards"]:
		# check if the card can be paid for
		if card["sp"] <= state["external"]["sp"]:
			targets = []
			if card["type"] == "cocktail":
				targets = ["l", "r"]
			elif card["type"] == "snack":
				targets = ["s"]
			actions.extend([{
				"action": "card",
				"card_id": card["id"],
				"target": target
			} for target in targets])

	return actions

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
	HELPERS
	"""
	@staticmethod
	def _parseInt(n):
		return str(n) if n != None else "\"-1\""
	@staticmethod
	def _extractInt(s):
		return s if s != -1 else None

	@staticmethod
	def _parseFloat(n):
		return str(n) if n != None else "\"-1\""
	@staticmethod
	def _extractFloat(s):
		return s if s != -1 else None

	@staticmethod
	def _parseBool(b):
		return "1" if b else "0"
	@staticmethod
	def _extractBool(s):
		return True if s == 1 else False

	@staticmethod
	def _parseStr(s):
		return "\"{}\"".format(s) if s != None else "\"\""
	@staticmethod
	def _extractStr(s):
		return s if s != "" else None

	"""
	STATES
	"""
	globalStateFields = [
		("turn", "TINYINT"),
		# ("musician_card_id", "TINYINT", ""),
	]
	internalStateFields = [
		("card_ids", "VARCHAR(64)"),
		("status", "VARCHAR(8)"),
	]
	externalStateFields = [
		("hp", "TINYINT"),
		("hp_until_max", "TINYINT"),
		("sp", "TINYINT"),
		("max_sp", "TINYINT"),
		# ("treasures", "TINYINT"),
		# ("answers", "TINYINT"),
		# ("has_secrets_in_hand", "BOOLEAN"),
		# ("has_facedown_cards", "BOOLEAN"),
		# ("num_cards", "TINYINT"),
		# ("is_friend", "BOOLEAN"),
	]
	stateFields = [
		*globalStateFields,
		*internalStateFields,
		*externalStateFields,
		*[("left_{}".format(field), datatype) for field, datatype in externalStateFields],
		*[("right_{}".format(field), datatype) for field, datatype in externalStateFields],
	]
	stateFieldsList = [field for field, _ in stateFields]
	stateFieldsListString = ",".join([field for field, _ in stateFields])

	@staticmethod
	def _globalStateToRow(global_state):
		return [
			DatabaseHelpers._parseInt(global_state["turn"]),
			# DatabaseHelpers._parseInt(global_state["musician"]["id"]) if global_state["musician"] != None else "NULL",
		]
	@staticmethod
	def _internalStateToRow(internal_state):
		return [
			"\"{}\"".format(",".join(sorted([DatabaseHelpers._parseInt(card["id"]) for card in internal_state["cards"]]))) if internal_state["cards"].count else "NULL",
			DatabaseHelpers._parseStr(internal_state["status"]),
		]
	@staticmethod
	def _externalStateToRow(external_state):
		return [
			DatabaseHelpers._parseInt(external_state["hp"]),
			DatabaseHelpers._parseInt(external_state["hp_until_max"]),
			DatabaseHelpers._parseInt(external_state["sp"]),
			DatabaseHelpers._parseInt(external_state["max_sp"]),
			# DatabaseHelpers._parseInt(external_state["treasures"]),
			# DatabaseHelpers._parseInt(external_state["answers"]),
			# DatabaseHelpers._parseBool(external_state["has_secrets_in_hand"]),
			# DatabaseHelpers._parseBool(external_state["has_facedown_cards"]),
			# DatabaseHelpers._parseBool(external_state["is_friend"])
		]
	@staticmethod
	def stateToRow(state):
		return [
			*DatabaseHelpers._globalStateToRow(state["g"]),
			*DatabaseHelpers._internalStateToRow(state["internal"]),
			*DatabaseHelpers._externalStateToRow(state["external"]),
			*DatabaseHelpers._externalStateToRow(state["left"]),
			*DatabaseHelpers._externalStateToRow(state["right"]),
		]

	@staticmethod
	def buildClosestObservedStateQuery(state_id):
		# formulas for factors should be bounded between 0 and 1. 0 means the
		# states are as different as possible in this metric, 1 means the states
		# are identical in this metric. weights for factors also range from 0 to 1
		# and determine how important each factor is. a weight of 0 means the
		# factor is unimportant, 1 means the factor is extremely important
		global_factors = [
			# i dont think global factors are super important
		]
		internal_factors = [
			# TODO cards are important
			# TODO status should probably scale other factors
			("r.status = s.status", 0.1)
		]
		external_factors = [
			# SELF
			# difference in hp, divided by average of max hps
			("(2.0 * ABS(r.hp - s.hp) / (r.hp + r.hp_until_max + s.hp + s.hp_until_max))", 0.25),
			# difference in sp, divided by average of max sps
			("(2.0 * ABS(r.sp - s.sp) / (r.max_sp + s.max_sp))", 0.2),

			# LEFT mimics self, but weight is halved
			("(2.0 * ABS(r.left_hp - s.left_hp) / (r.left_hp + r.left_hp_until_max + s.left_hp + s.left_hp_until_max))", 0.125),
			("(2.0 * ABS(r.left_sp - s.left_sp) / (r.left_max_sp + s.left_max_sp))", 0.1),

			# RIGHT mimics self, but weight is halved
			("(2.0 * ABS(r.right_hp - s.right_hp) / (r.right_hp + r.right_hp_until_max + s.right_hp + s.right_hp_until_max))", 0.125),
			("(2.0 * ABS(r.right_sp - s.right_sp) / (r.right_max_sp + s.right_max_sp))", 0.1),

			# TODO treasures, answers, has_secrets_in_hand, has_facedown_cards, is_friend
		]
		factors = [
			*global_factors,
			*internal_factors,
			*external_factors
		]
		random_states_query = "SELECT * FROM state ORDER BY RANDOM() LIMIT {}".format(state_adjacency_constants["batch_size"])
		state_query = "SELECT * FROM state WHERE id = {}".format(DatabaseHelpers._parseInt(state_id))
		return """SELECT r.id, (
			{}
		) as similarity FROM ({}) r CROSS JOIN ({}) s ORDER BY similarity DESC LIMIT 1""".format(
			"*".join(["(1.0 - ({}) * {})".format(formula, weight) for formula, weight in factors]),
			random_states_query,
			state_query
		)

	"""
	ACTIONS
	"""
	actionFields = [
		("action", "VARCHAR(4)"),
		("card_id", "TINYINT"),
		("target", "VARCHAR(1)")
	]
	actionFieldsList = [field for field, _ in actionFields]
	actionFieldsListString = ",".join(actionFieldsList)

	@staticmethod
	def actionToRow(action):
		return [
			DatabaseHelpers._parseStr(action["action"]),
			DatabaseHelpers._parseInt(action["card_id"]) if "card_id" in action else "\"-1\"",
			DatabaseHelpers._parseStr(action["target"]) if "target" in action else "\"\"",
		]
	@staticmethod
	def rowToAction(row):
		return {
			"action": DatabaseHelpers._extractStr(row[0]),
			"card_id": DatabaseHelpers._extractInt(row[1]),
			"target": DatabaseHelpers._extractStr(row[2])
		}