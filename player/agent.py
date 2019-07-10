import numpy as np

from util.constants import agent_constants, param_or_default
from util.database import Database
from util.helpers import getValidActionsInState

'''
The agent represents a player in the game. The purpose of this algorithm is to
determine if there is a strategy or character which is optimal or unbalanced, so
it makes sense for our agent to be an individual player and to observe their
actions. It also makes sense for agents to play against one-another as they learn
the game. Each agent, at the beginning of the game, will select a character (even
though they should be randomly assigned) to determine if any characters are
preferable and by how much, and then will progress through the game by taking
different actions and entering various states. We will be able to learn from the
agent by observing which actions they are likely to take in which situations.
Since our state and action space is so large, all agents will share their q
tables.

Helpful notes:
    Indexing into the q table should always be done with object ids
'''
class Agent:
    '''
    Initialize a new agent.
    q: the agent's q table. this is shared between agents
    params: an object with the following fields:
        learning_rate: how trusting an agent is of new information
        discount_factor: how long-sighted an agent is when calculating reward
        endgame_discount_factor: discount factor, but at the end of a game
        random_action_rate: how often an agent chooses an action randomly
        dyna_steps: how many "planning" steps the agent should take
        verbose: TODO make the agent talkative :)
    '''
    def __init__(self, q, params):

        self.memory = []
        self.q = q

        self.learning_rate = param_or_default(params, agent_constants, "learning_rate")
        self.discount_factor = param_or_default(params, agent_constants, "discount_factor")
        self.endgame_discount_factor = param_or_default(params, agent_constants, "endgame_discount_factor")
        self.random_action_rate = param_or_default(params, agent_constants, "random_action_rate")
        self.dyna_steps = param_or_default(params, agent_constants, "dyna_steps")
        self.verbose = param_or_default(params, agent_constants, "verbose")

        # Current state
        self.s = None
        self.s_id = None

        # Last action
        self.a = None
        self.a_id = None

    '''
    Set the initial state and return an action. The state passed here
    should be mutated in-place so that it never needs to be regenerated
    '''
    def initialQuery(self, s):
        self.s = s
        self.s_id = self._snapState()

        recommended_a_id, _ = self._recommendAction(self.s_id)

        self.a_id, self.a = self._selectAction(recommended_a_id)

        return self.a

    '''
    Query the agent, returning its reward for its past action so that it can
    update its q table, update its state, append to its memory, and return a new
    action
    '''
    def query(self, reward, game_ended = False):
        # its possible that another player won before initialQuery is called, just
        # return in this case
        if not self.s:
            return

        # The state should be mutated in place, so we don't actually need to be
        # queried with the new state, just check the new state against the old one
        old_s_id = self.s_id
        new_s_id = self._snapState()

        df = self.endgame_discount_factor if game_ended else self.discount_factor

        # Update q table for reward
        closest_s_id, similarity = self._findClosestState(old_s_id)
        recommended_a_id, best_future_utility = self._recommendAction(closest_s_id)
        self._updateQ(old_s_id, self.a_id, reward, df, similarity, best_future_utility)

        if self.dyna_steps:
            # If the game is over, update all past actions
            start = len(self.memory) - 1 if game_ended else len(self.memory) - min(self.dyna_steps, len(self.memory)) - 1
            # Update q for past decisions
            for i in range(start, -1, -1):
                _, best_future_utility = self._recommendAction(self.memory[i]["s'"])
                self._updateQ(self.memory[i]["s"], self.memory[i]["a"], self.memory[i]["s'"], self.memory[i]["r"], df, best_future_utility)

        # Remember this
        self.memory.append({
            "s": old_s_id,
            "a": self.a_id,
            "s'": new_s_id,
            "r": reward
        })

        # Update state
        self.s_id = new_s_id

        # Select new action
        self.a_id, self.a = self._selectAction(recommended_a_id)

        Database.commit()

        return self.a

    '''
    Determine the closest state to the given state
    '''
    def _findClosestState(self, to_s_id):
        if not any(self.q[to_s_id]):
            return Database.getClosestObservedStateId(to_s_id)
        else:
            return to_s_id, 1

    '''
    Determine the best possible action id in a given state from the q table
    '''
    def _recommendAction(self, in_s_id):
        # find the best action in the closest state
        recommended_a_id = None
        best_future_utility = 0
        # in_s_id could be None if no closest states were found, and it could not
        # be in q if the game ended before querying the agent with that state
        if in_s_id != None and in_s_id in self.q:
            for a_id, expected_reward in self.q[in_s_id].items():
                if expected_reward > best_future_utility:
                    recommended_a_id = a_id
        return recommended_a_id, best_future_utility

    '''
    Update the q table with a reward
    '''
    def _updateQ(self, s_id, a_id, reward, discount_factor, similarity, best_future_utility):
        if s_id not in self.q:
            self.q[s_id] = {}

        if a_id not in self.q[s_id]:
            self.q[s_id][a_id] = 0

        # this is a typical q-learning except for "similarity," which is factored
        # in to help deal with how big the state space is
        q_value = (1 - self.learning_rate) * self.q[s_id][a_id] + self.learning_rate * (reward + similarity * discount_factor * best_future_utility)
        self.q[s_id][a_id] = q_value
        Database.updateQ(s_id, a_id, q_value)

    '''
    Select the best (id, action), or a random one
    '''
    def _selectAction(self, recommended_a_id = None):
        # if no action is recommended or we randomly roll below our
        # random_action_rate, select a random action. TODO it might be a good idea
        # to have state similarity here to pick a closest observed action
        possible_actions = getValidActionsInState(self.s)
        possible_action_ids = [Database.upsertAction(action) for action in possible_actions]
        if not recommended_a_id or np.random.random() < self.random_action_rate or recommended_a_id not in possible_action_ids:
            random_action_index = np.random.randint(len(possible_action_ids))
            random_action_id = possible_action_ids[random_action_index]
            self._printIfVerbose("agent randomly chose", possible_actions[random_action_index])
            return random_action_id, possible_actions[random_action_index]
        else:
            action = Database.getAction(recommended_a_id)
            self._printIfVerbose("agent chose", action)
            return recommended_a_id, action

    def _snapState(self):
        s_id = Database.upsertState(self.s)
        if s_id not in self.q:
            self.q[s_id] = {}
        return s_id

    '''
    Print to the console if verbose is True
    '''
    def _printIfVerbose(self, *args):
        if self.verbose:
            print(*args)
