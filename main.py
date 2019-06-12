
from game.game import Game

from util.card_definitions import CardDefinitions
from util.helpers import loadQTableFromFile, saveQTableToFile, loadCardDefinitions, loadCharacterDefinitions

def main():
	# TODO implement command-line args

	# load data
	q = loadQTableFromFile()
	cards = loadCardDefinitions()
	characters = loadCharacterDefinitions()

	# initialize card definitions for querying
	CardDefinitions.setDefinitions(cards["main"], cards["treasures"], cards["answers "])

	# how many games to play per run
	num_games = 1000
	# every nth game will be verbose
	verbose_mod = 100

	# game params as defined in game/game.py
	game_params = {
		# "num_agents"
		# "num_humans"
		# "max_turns"
	}

	# agent params as defined in player/agent.py
	agent_params = {
		# "learning_rate"
		# "discount_factor"
		# "endgame_discount_factor"
		# "random_action_rate"
		# "dyna_steps"
	}

	# deck params as defined in game/game.py
	deck_params = {
		"main_cards": cards["main"],
		"treasure_cards": cards["treasures"],
		"answer_cards": cards["answers"]
	}

	# character params as defined in game/game.py
	character_params = {
		characters: characters
	}

	for game_number in range(num_games):
		verbose = game_number % verbose_mod == verbose_mod - 1
		game_params.verbose = verbose
		agent_params.verbose = verbose

		print("Running game {}".format(game_number + 1))
		game = Game(q, game_params, agent_params, deck_params, character_params)
		game.run()

		# save q table after every game
		saveQTableToFile(q)
 

if __name__ == "__main__":
	main()
