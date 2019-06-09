import numpy as np

from player.agent import Agent

from util.deck import Deck

'''
A Game sets up and handles state and actions for players. Helpful notes:
	`p` typically refers to a player index, `player` refers to a player object
	human players not yet implemented
'''
class Game:
	'''
	Initialize a new game.
	q: the q table agents should use
	game_params: an object with the following fields:
		num_agents: the number of agents playing the game
		num_humans: TODO the number of players playing the game
		max_turns: essentially a timeout
		verbose: TODO make the game talkative :)
	agent_params: an object specifying which params to use for agents. detailed in
		agent/agent.py
	deck_params: an object specifying the cards to use for the game. contains:
		main_cards: the cards in the main deck
		treasure_cards: the cards in the treasure deck
		answer_cards: the cards in the answer deck
	character_params: an object specifying the characters to use in the game:
		characters: a list of characters
	'''
	def __init__(self, q, game_params, agent_params, deck_params, character_params):
		self.verbose = game_params.verbose if "verbose" in game_params else False
		num_agents = game_params.num_agents if "num_agents" in game_params else 2
		num_humans = game_params.num_humans if "num_humans" in game_params else 0

		# create and shuffle players
		self.players = [self._createAgent(q, agent_params) for _ in range(num_agents)] + [self._createHuman(q, agent_params) for _ in range(num_agents)]
		np.random.shuffle(self.players)

		# create and shuffle decks
		self.decks = {
			"main": Deck(deck_params.main_cards, "main"),
			"treasure": Deck(deck_params.treasure_cards, "treasure"),
			"answer": Deck(deck_params.answer_cards, "answer"),
			"discard": Deck([], "discard")
		}
		self.decks.main.shuffle()
		self.decks.treasure.shuffle()
		self.decks.answer.shuffle()

		# randomly distribute characters. correspond to each player by their index
		self.characters = character_params.characters
		np.random.shuffle(self.characters)

		# set initial player states
		self.state = self._createInitialGlobalState()
		self.player_states = [self._selectStateForPlayer(p) for p in range(len(self.players))]
		self.max_turns = game_params.max_turns if "max_turns" in game_params else 500
		self.winning_player = None

	'''
	Initialize an agent
	'''
	def _createAgent(self, q, agent_params):
		# initialize agents with fresh memory, but the same q
		return Agent([], q, agent_params)
 
	def _createHuman(self):
		# maybe ill do this someday lol
		raise Exception("Human players not implemented")

	'''
	Initialize the global state
	'''
	def _createInitialGlobalState(self):
		# TODO implement
		return {
			"g": { # global state
				"turn": 1
			}
		}

	'''
	Create a permanent state object to give to a player. This object should never
	have to be recreated, ie never change the shallow references
	'''
	def _createInitialStateForP(self, p):
		# TODO implement
		return {
			"g": self.state.g
		}


	'''
	Runs the game! Returns the result as a string.
	'''
	def run():
		# kick things off
		while self.state.g.turn < self.max_turns:
			self._runTurn()
			if self.winning_player != None:
				# TODO return something more helpful
				return "Player won"
			self.state.g.turn += 1
		return "Game reached maximum number of turns"

	'''
	Runs through a turn for all players.
	'''
	def _runTurn(self):
		for p in range(len(self.players)):
			self._runActionsForP(p)
			if self.winning_player != None:
				return

	'''
	Runs through a players actions for a turn.
	'''
	def _runActionsForP(self, p):
		player = self.players[p]
		action = None
		if self.state.g.turn == 1:
			# get initial action
			action = player.initialQuery(self._createInitialStateForP(p))
		else:
			# update player with last reward and get a new action
			action = self._queryP(p) # TODO how to reward a player after a round of turns?

		# let the player act as long as they want
		while self._executeActionForP(action, p) and self.winning_player == None:
			# update player, get new action
			action = self._queryP(p) # TODO

	'''
	Reads an action and mutates state based on that action. Returns False if the
	player has ended their turn. Sets self.winning_player if the game has ended
	'''
	def _executeActionForP(self, action, p):
		# TODO implement
		return True

	'''
	Update the player with the reward for their last action, and get a new action
	'''
	def _queryP(self, p):
		# TODO implement
		return self.players[p].query()
