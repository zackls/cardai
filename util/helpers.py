import pickle

'''
Returns a list of valid actions given a state
'''
def getValidActionsInState(state):
	# TODO implement
	pass

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
	# TODO implement
	pass

'''
Decompress a compressed action
'''
def decompressAction(compressed_action):
	# TODO implement
	pass

'''
Minify a state object to a unique string
'''
def compressState(state):
	# TODO implement
	pass

'''
Decompress a compressed state
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
