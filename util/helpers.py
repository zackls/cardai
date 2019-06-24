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
	if state["internal"]["status"] == "draw" and state["external"]["sp"] >= 2:
		actions.append({
			"action": "draw"
		})

	# add actions for playing cards based on SP
	for card in state["internal"]["cards"]:
		targets = []
		if card.type == "cocktail":
			targets = ["l", "r"]
		elif card.type == "snack":
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
		return str(n) if n != None else "NULL"
	@staticmethod
	def _extractInt(s):
		return int(s) if s != "NULL" else None

	@staticmethod
	def _parseBool(b):
		return "true" if b else "false"
	@staticmethod
	def _extractBool(s):
		return True if s == "true" else False

	@staticmethod
	def _parseStr(s):
		return s if s != None else "NULL"
	@staticmethod
	def _extractStr(s):
		return s if s != "NULL" else None

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
			DatabaseHelpers._parseInt(global_state["turn"]),
			DatabaseHelpers._parseInt(global_state["musician"]["id"]) if global_state["musician"] != None else "NULL",
		])
	@staticmethod
	def _internalStateToRow(internal_state):
		return ",".join([
			",".join(sorted([DatabaseHelpers._parseInt(card["id"]) for card in internal_state["cards"]])) if internal_state["cards"].count else "NULL",
			DatabaseHelpers._parseStr(internal_state["status"]),
		])
	@staticmethod
	def _externalStateToRow(external_state):
		return ",".join([
			DatabaseHelpers._parseInt(external_state["hp"]),
			DatabaseHelpers._parseInt(external_state["hp_until_max"]),
			DatabaseHelpers._parseInt(external_state["sp"]),
			DatabaseHelpers._parseInt(external_state["max_sp"]),
			DatabaseHelpers._parseInt(external_state["treasures"]),
			DatabaseHelpers._parseInt(external_state["answers"]),
			DatabaseHelpers._parseBool(external_state["has_secrets_in_hand"]),
			DatabaseHelpers._parseBool(external_state["has_facedown_cards"]),
			DatabaseHelpers._parseBool(external_state["is_friend"])
		])
	@staticmethod
	def stateToRow(state):
		return ",".join([
			DatabaseHelpers._globalStateToRow(state["g"]),
			DatabaseHelpers._internalStateToRow(state["internal"]),
			DatabaseHelpers._externalStateToRow(state["external"]),
			DatabaseHelpers._externalStateToRow(state["left"]),
			DatabaseHelpers._externalStateToRow(state["right"]),
		])

	@staticmethod
	def buildClosestObservedStateQuery(state_id, batch_size):
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
			("(r.status = s.status)", 0.1)
		]
		external_factors = [
			# SELF
			# difference in hp, divided by average of max hps
			("(2 * ABS(r.hp - s.hp) / (r.hp + r.hp_until_max + s.hp + s.hp_until_max))", 0.25),
			# difference in sp, divided by average of max sps
			("(2 * ABS(r.sp - s.sp) / (r.max_sp + s.max_sp))", 0.2),

			# LEFT mimics self, but weight is halved
			("(2 * ABS(r.left_hp - s.left_hp) / (r.left_hp + r.left_hp_until_max + s.left_hp + s.left_hp_until_max))", 0.125),
			("(2 * ABS(r.left_sp - s.left_sp) / (r.left_max_sp + s.left_max_sp))", 0.1),

			# RIGHT mimics self, but weight is halved
			("(2 * ABS(r.right_hp - s.right_hp) / (r.right_hp + r.right_hp_until_max + s.right_hp + s.right_hp_until_max))", 0.125),
			("(2 * ABS(r.right_sp - s.right_sp) / (r.right_max_sp + s.right_max_sp))", 0.1),

			# TODO treasures, answers, has_secrets_in_hand, has_facedown_cards, is_friend
		]
		factors = [
			*global_factors,
			*internal_factors,
			*external_factors
		]
		random_states_query = "SELECT * FROM state ORDER BY RANDOM() LIMIT {}".format(batch_size)
		state_query = "SELECT * FROM state WHERE id = {}".format(state_id)
		return """SELECT r.id, (
			{}
		) as similarity FROM ({}) r CROSS JOIN ({}) s ORDER BY similarity DESC LIMIT 1""".format(
			"*".join(["(1 - ({}) * {})".format(formula, weight) for formula, weight in factors]),
			random_states_query,
			state_query
		)

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
			DatabaseHelpers._parseStr(action["action"]),
			DatabaseHelpers._parseInt(["card"]["id"]) if "card" in action else "NULL",
			DatabaseHelpers._parseStr(action["target"]),
		])
	@staticmethod
	def rowToAction(row):
		return {
			"action": DatabaseHelpers._extractStr(row[0]),
			"card": DatabaseHelpers._extractInt(CardDefinitions.getCardById(int(row[1]))),
			"target": DatabaseHelpers._extractStr(row[2])
		}