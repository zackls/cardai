import matplotlib.pyplot as plt
import time

class Stats:
	start_time = None
	stats = {}

	@staticmethod
	def recordStat(key):
		if Stats.start_time == None:
			Stats.start_time = time.time()
		if key not in Stats.stats:
			Stats.stats[key] = []
		Stats.stats[key].append(time.time())

	@staticmethod
	def printStats():
		print("")
		print("--- STATS ----")
		for key in sorted(Stats.stats.keys()):
			print("{}: {}".format(key, len(Stats.stats[key])))
		print("")

	@staticmethod
	def graphChosenActionUsage(segments=250):
		increment = (time.time() - Stats.start_time) / segments
		columns = []
		for key in Stats.stats.keys():
			if "chosen_action" in key:
				columns.append(key)
				key_data = []
				current_max = Stats.start_time
				for ts in Stats.stats[key]:
					while ts >= current_max:
						key_data.append(0)
						current_max += increment
					key_data[-1] += 1
				while len(key_data) < 250:
					key_data.append(0)
				plt.plot(range(segments), key_data)
		plt.legend(columns)
		plt.title("Action usage over run")
		plt.show()

	@staticmethod
	def graphTurnCountPerGame():
		counts = []
		current_turn = 0
		for game_ts in Stats.stats["games"]:
			counts.append(0)
			while current_turn < len(Stats.stats["turns"]) and Stats.stats["turns"][current_turn] <= game_ts:
				counts[-1] += 1
				current_turn += 1
		plt.plot(range(len(Stats.stats["games"])), counts)
		plt.title("Turn count per game over run")
		plt.show()
