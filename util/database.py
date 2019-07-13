import sqlite3

from util.helpers import DatabaseHelpers

class Database:
	@classmethod
	def _tryExecute(cls, clause):
		try:
			cls.c.execute(clause)
		except Exception as e:
			print(clause)
			raise e

	"""
	STATES
	"""
	@classmethod
	def printStates(cls):
		cls._tryExecute("SELECT * FROM state")
		print(cls.c.fetchall())

	@classmethod
	def upsertState(cls, state):
		row_values = DatabaseHelpers.stateToRow(state)
		cls._tryExecute("""INSERT OR IGNORE INTO state ({}) VALUES (
			{}
		)""".format(
			DatabaseHelpers.stateFieldsListString,
			",".join(row_values),
		))
		cls._tryExecute("""SELECT id FROM state WHERE {} LIMIT 1""".format(
			" AND ".join(["{}={}".format(DatabaseHelpers.stateFieldsList[i], val) for i, val in enumerate(row_values)])
		))
		return cls.c.fetchone()[0]

	'''
	Finds the closest state to the state passed in.
	Works by selecting a random set of already-observed
	states from q and computing the closest.
	'''
	@classmethod
	def getClosestObservedStateId(cls, to_s_id):
		cls._tryExecute(DatabaseHelpers.buildClosestObservedStateQuery(to_s_id))
		row = cls.c.fetchone()
		state_id, similarity = row if row != None else (None, 0)
		return state_id, similarity


	"""
	ACTIONS
	"""
	@classmethod
	def getAction(cls, a_id):
		cls._tryExecute("SELECT {} FROM action WHERE id = {}".format(DatabaseHelpers.actionFieldsListString, a_id))
		return DatabaseHelpers.rowToAction(cls.c.fetchone())

	@classmethod
	def printActions(cls):
		cls._tryExecute("SELECT * FROM action")
		print(cls.c.fetchall())

	@classmethod
	def upsertAction(cls, action):
		row_values = DatabaseHelpers.actionToRow(action)
		cls._tryExecute("""INSERT OR IGNORE INTO action ({}) VALUES ({})""".format(
			DatabaseHelpers.actionFieldsListString,
			",".join(row_values),
		))
		cls._tryExecute("""SELECT id FROM action WHERE {} LIMIT 1""".format(
			" AND ".join(["{}={}".format(DatabaseHelpers.actionFieldsList[i], val) for i, val in enumerate(row_values)])
		))
		return cls.c.fetchone()[0]


	"""
	Q
	"""
	@classmethod
	def getQTable(cls):
		q = {}
		cls._tryExecute("SELECT state_id, action_id, q FROM q")
		for state_id, action_id, q_value in cls.c.fetchall():
			if state_id not in q:
				q[state_id] = {}
			q[state_id][action_id] = q_value
		return q

	@classmethod
	def updateQ(cls, s_id, a_id, q):
		# on conflict of unique keys, update q
		cls._tryExecute("""INSERT OR REPLACE INTO q (state_id, action_id, q) VALUES (
			{}
		)""".format(
			",".join([DatabaseHelpers._parseInt(s_id), DatabaseHelpers._parseInt(a_id), DatabaseHelpers._parseFloat(q)]),
		))


	"""
	MISC
	"""
	@classmethod
	def initialize(cls):
		cls.connection = sqlite3.connect("data/data.db")
		cls.c = cls.connection.cursor()

	@classmethod
	def destroy(cls):
		cls.connection.close()

	@classmethod
	def commit(cls):
		cls.connection.commit()

	@classmethod
	def createDatabase(cls):
		cls._tryExecute("""CREATE TABLE state(
			id INTEGER PRIMARY KEY,
			{},
			UNIQUE({})
		)""".format(
			",".join(["{} {} NOT NULL".format(field, datatype) for field, datatype in DatabaseHelpers.stateFields]),
			DatabaseHelpers.stateFieldsListString
		))

		cls._tryExecute("""CREATE TABLE action(
			id INTEGER PRIMARY KEY,
			{},
			UNIQUE({})
		)""".format(
			",".join(["{} {} NOT NULL".format(field, datatype) for field, datatype in DatabaseHelpers.actionFields]),
			DatabaseHelpers.actionFieldsListString
		))

		cls._tryExecute("""CREATE TABLE q(
			id INTEGER PRIMARY KEY,
			state_id INTEGER NOT NULL,
			action_id INTEGER NOT NULL,
			q REAL NOT NULL,
			UNIQUE(state_id, action_id),
			FOREIGN KEY(state_id) REFERENCES state(id),
			FOREIGN KEY(action_id) REFERENCES action(id)
		)""")

		cls.commit()

	@classmethod
	def destroyDatabase(cls):
		cls._tryExecute("DROP TABLE IF EXISTS state")
		cls._tryExecute("DROP TABLE IF EXISTS action")
		cls._tryExecute("DROP TABLE IF EXISTS q")
		cls.commit()
