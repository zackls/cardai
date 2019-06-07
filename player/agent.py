import numpy as np

from util.helpers import getClosestObservedState, getValidActionsInState, compressAction, compressState, decompressAction

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
    "c" in a variable name typically stands for "compressed". Indexing into the q
        table should always be done with compressed objects
'''
class Agent:
    '''
    Initialize a new agent.
    memory: the agent's experience in the game
    q: the agent's q table. this is shared between agents
    params: an object with the following fields:
        learning_rate: how trusting an agent is of new information
        discount_factor: how long-sighted an agent is when calculating reward
        endgame_discount_factor: discount factor, but at the end of a game
        random_action_rate: how often an agent chooses an action randomly
        dyna_steps: how many "planning" steps the agent should take
        verbose: TODO make the agent talkative :)
    '''
    def __init__(self, memory, q, params):

        self.memory = []
        self.q = q

        self.learning_rate = params.learning_rate if "learning_rate" in params else 0.4
        self.discount_factor = params.discount_factor if "discount_factor" in params else 0.8
        self.endgame_discount_factor = params.endgame_discount_factor if "endgame_discount_factor" in params else 0.975
        self.random_action_rate = params.random_action_rate if "random_action_rate" in params else 0.1
        self.dyna_steps = params.dyna_steps if "dyna_steps" in params else 10
        self.verbose = params.verbose if "verbose" in params else False

        # Current state
        self.s = None
        self.c_s = None

        # Last action
        self.a = None
        self.c_a = None

    '''
    Set the initial state and return an uncompressed action
    '''
    def initialQuery(self, s):
        self.s = s
        self.c_s = compressState(self.s)

        recommended_c_a, _ = self._recommendAction(self.c_s)

        self.c_a = self._selectAction(recommended_c_a)
        self.a = decompressAction(self.c_a)

        return self.a

    '''
    Query the agent, returning its reward for its past action so that it can
    update its q table, update its state, append to its memory, and return a new
    action
    '''
    def query(self, new_s, reward, game_ended = False):
        new_c_s = compressState(new_s)
        # Update q table for reward
        closest_c_s, similarity = self._findClosestState(new_c_s)
        recommended_c_a, best_future_utility = self._recommendAction(closest_c_s)
        self._updateQ(self.c_s, self.c_a, reward, self.endgame_discount_factor if game_ended else self.discount_factor, similarity, best_future_utility)

        if self.dyna_steps:
            # If the game is over, update all past actions
            start = len(self.c_memory) - 1 if game_ended else len(self.c_memory) - min(self.dyna, len(self.c_memory)) - 1
            # Update q for past decisions
            for i in range(start, -1, -1):
                _, best_future_utility = self._recommendAction(self.c_memory[i]["s'"])
                self._updateQ(self.c_memory[i]["s"], self.c_memory[i]["a"], self.c_memory[i]["s'"], self.c_memory[i]["r"], self.endgame_discount_factor if game_ended else self.discount_factor, best_future_utility)

        # Remember this
        self.c_memory.append({
            "s": self.c_s,
            "a": self.c_a,
            "s'": new_c_s,
            "r": reward
        })

        # Update state
        self.c_s = new_c_s

        # Select new action
        self.c_a = self._selectAction(recommended_c_a)
        self.a = decompressAction(self.c_a)

        return self.a

    '''
    Determine the closest state to the given state
    '''
    def _findClosestState(self, to_c_s):
        if to_c_s not in self.q:
            return helpers.getClosestObservedState(to_c_s, q)
        else:
            return to_c_s, 1

    '''
    Determine the best possible compressed action in a given state from the q
    table
    '''
    def _recommendAction(self, in_c_s):
        # find the best action in the closest state
        recommended_c_a = None
        best_future_utility = 0
        for c_a, expected_reward in self.q[in_c_s].items():
            if expected_reward > best_future_utility:
                recommended_c_a = c_a
        return recommended_c_a, best_future_utility

    '''
    Update the q table with a reward
    '''
    def _updateQ(self, c_s, c_a, reward, discount_factor, similarity, best_future_utility):
        if c_s not in self.q:
            self.q[c_s] = {}

        # this is a typical q-learning except for "similarity," which is factored
        # in to help deal with how big the state space is
        self.q[c_s][c_a] = (1 - self.learning_rate) * self.q[c_s][c_a] + self.learning_rate * (reward + similarity * discount_factor * best_future_utility)

    '''
    Select the best compressed action, or a random one
    '''
    def _selectAction(self, recommended_c_a = None):
        # if no action is recommended or we randomly roll below our
        # random_action_rate, select a random action. TODO it might be a good idea
        # to have state similarity here to pick a closest observed action
        possible_actions = getValidActionsInState(self.s)
        if not recommended_c_a or np.random.random() < self.random_action_rate or decompressAction(recommended_c_a) not in possible_actions:
            return compressAction(possible_actions[np.random.randint(len(possible_actions))])
        else:
            return recommended_c_a
