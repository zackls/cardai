
from game.game import Game

from util.card_definitions import CardDefinitions
from util.constants import agent_constants, run_constants
from util.database import Database
from util.helpers import loadCardDefinitions, loadCharacterDefinitions
from util.stats import Stats

def main():
	# TODO implement command-line args

	# initialize database
	Database.initialize()
	q = Database.getQTable()

	cards = loadCardDefinitions()
	characters = loadCharacterDefinitions()

	# initialize card definitions for querying
	CardDefinitions.setDefinitions(cards["main"], cards["treasures"], cards["answers"])

	# how many games to play per run
	num_games = run_constants["num_games"]
	# every nth game will be verbose
	verbose_mod = run_constants["verbose_mod"]

	# game params as defined in game/game.py
	game_params = {
		# "num_agents"
		# "num_humans"
		# "max_turns"
	}

	# agent params as defined in player/agent.py
	agent_params = {
		"learning_rate": agent_constants["learning_rate"]
		# "discount_factor"
		# "endgame_discount_factor"
		# "random_action_rate"
		# "dyna_steps"
	}

	# deck params as defined in game/game.py
	deck_params = {
		"main_cards": CardDefinitions.cards["main"],
		"treasure_cards": CardDefinitions.cards["treasures"],
		"answer_cards": CardDefinitions.cards["answers"]
	}

	# character params as defined in game/game.py
	character_params = {
		"characters": characters
	}

	for game_number in range(num_games):
		verbose = game_number % verbose_mod == verbose_mod - 1
		game_params["verbose"] = verbose
		agent_params["verbose"] = verbose

		print("Running game {}".format(game_number + 1))
		game = Game(q, game_params, agent_params, deck_params, character_params)
		game.run()
		Stats.recordStat("games")

		agent_params["learning_rate"] *= 1 - agent_constants["learning_rate_decay"]

	# deinitialize database
	Database.destroy()

	Stats.printStats()
	Stats.printQStats(q)
	Stats.graphChosenActionUsage()
	Stats.graphTurnCountPerGame()

if __name__ == "__main__":
	main()
