import sqlite3

from util.helpers import DatabaseHelpers

class Database:
	"""
	STATES
	"""
	@classmethod
	def getState(cls, s_id):
		cls.c.execute("SELECT {} FROM state WHERE id = {}".format(DatabaseHelpers.stateFieldsList, s_id))
		return DatabaseHelpers.rowToState(cls.c.fetchone())

	@classmethod
	def upsertState(cls, state):
		cls.c.execute("""UPSERT INTO state VALUES ({}) (
			{}
		)""".format(
			DatabaseHelpers.stateFieldsList,
			DatabaseHelpers.stateToRow(state),
		))
		return cls.c.lastrowid

	'''
	Finds the closest state to the state passed in.
	Works by selecting a random set of already-observed
	states from q and computing the closest.
	'''
	@classmethod
	def getClosestObservedStateId(cls, to_s_id, batch_size=100):
		cls.c.execute(DatabaseHelpers.buildClosestObservedStateQuery(to_s_id, batch_size))
		state_id, similarity = cls.c.fetchone()
		return state_id, similarity


	"""
	ACTIONS
	"""
	@classmethod
	def getAction(cls, a_id):
		cls.c.execute("SELECT {} FROM action WHERE id = {}".format(DatabaseHelpers.actionFieldsList, a_id))
		return DatabaseHelpers.rowToAction(cls.c.fetchone())

	@classmethod
	def upsertAction(cls, action):
		cls.c.execute("""UPSERT INTO action VALUES ({}) (
			{}
		)""".format(
			DatabaseHelpers.actionFieldsList,
			DatabaseHelpers.actionToRow(action),
		))
		return cls.c.lastrowid


	"""
	Q
	"""
	@classmethod
	def getQTable(cls):
		q = {}
		cls.c.execute("SELECT state_id, action_id, q FROM q")
		for state_id, action_id, q_value in cls.c.fetchall():
			if state_id not in q:
				q[state_id] = {}
			q[state_id][action_id] = q_value
		return q

	@classmethod
	def updateQ(cls, s_id, a_id, q):
		# on conflict of unique keys, update q
		cls.c.execute("""INSERT INTO q VALUES (state_id, action_id, q) (
			{}
		) ON CONFLICT (state_id, action_id) DO UPDATE SET q = excluded.q""".format(
			",".join([s_id, a_id, q]),
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
		cls.c.execute("""CREATE TABLE state(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			{},
			UNIQUE({})
		)""".format(
			",".join(["{} {} {}".format(field, datatype, constraints) for field, datatype, constraints in DatabaseHelpers.stateFields]),
			DatabaseHelpers.stateFieldsList
		))

		cls.c.execute("""CREATE TABLE action(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			{},
			UNIQUE({})
		)""".format(
			",".join(["{} {} {}".format(field, datatype, constraints) for field, datatype, constraints in DatabaseHelpers.actionFields]),
			DatabaseHelpers.actionFieldsList
		))

		cls.c.execute("""CREATE TABLE q(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
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
		cls.c.execute("DROP TABLE IF EXISTS state")
		cls.c.execute("DROP TABLE IF EXISTS action")
		cls.c.execute("DROP TABLE IF EXISTS q")
		cls.commit()
