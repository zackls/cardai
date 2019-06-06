import numpy as np

from util.helpers import getClosestObservedState, getValidActionsInState

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

        # Last action
        self.a = None

    '''
    Set the initial state and return an action
    '''
    def initialQuery(self, s):
        self.s = s

        recommended_action, _ = self._recommendAction(s)
        self.a = self._selectAction(recommended_action)

        return self.a

    '''
    Query the agent, returning its reward for its past action so that it can
    update its q table, update its state, append to its memory, and return a new
    action
    '''
    def query(self, new_s, reward, game_ended = False):
        # TODO condense state and actions before moving into table

        # Update q table for reward
        closest_state, similarity = self._findClosestState(new_s)
        recommended_action, best_future_utility = self._recommendAction(closest_state)
        self._updateQ(self.s, self.a, new_s, reward, self.endgame_discount_factor if game_ended else self.discount_factor, similarity, best_future_utility)

        if self.dyna_steps:
            # If the game is over, update all past actions
            start = len(self.memory) - 1 if game_ended else len(self.memory) - min(self.dyna, len(self.memory)) - 1
            # Update q for past decisions
            for i in range(start, -1, -1):
                _, best_future_utility = self._recommendAction(memory[i]["s'"])
                self._updateQ(memory[i]["s"], memory[i]["a"], memory[i]["s'"], memory[i]["r"], self.endgame_discount_factor if game_ended else self.discount_factor, best_future_utility)

        # Remember this
        self.memory.append({
            "s": self.s,
            "a": self.a,
            "s'": new_s,
            "r": reward
        })

        # Update state
        self.s = new_s

        # Select new action
        self.a = self._selectAction(recommended_action)

        return self.a

    '''
    Determine the closest state to the given state
    '''
    def _findClosestState(self, to_state):
        # similarity scales the future estimate by how similar new_s is to the
        # closest state
        closest_state = None
        similarity = None
        if to_state not in self.q:
            return helpers.getClosestObservedState(to_state, q)
        else:
            return to_state, 1

    '''
    Determine the best possible action in a given state from the q table
    '''
    def _recommendAction(self, in_state):
        # find the best action in the closest state
        recommended_action = None
        best_future_utility = 0
        for action, expected_reward in self.q[in_state].items():
            if expected_reward > best_future_utility:
                recommended_action = action
        return recommended_action, best_future_utility

    '''
    Update the q table with a reward
    '''
    def _updateQ(self, s, a, new_s, reward, discount_factor, similarity, best_future_utility):
        if s not in self.q:
            self.q[s] = {}

        # this is a typical q-learning except for "similarity," which is factored
        # in to help deal with how big the state space is
        self.q[s][a] = (1 - self.learning_rate) * self.q[s][a] + self.learning_rate * (reward + similarity * discount_factor * best_future_utility)

    '''
    Select the best action, or a random one
    '''
    def _selectAction(self, recommended_action = None):
        # if no action is recommended or we randomly roll below our
        # random_action_rate, select a random action. TODO it might be a good idea
        # to have state similarity here to pick a closest observed action
        possible_actions = getValidActionsInState(self.s)
        if not recommended_action or np.random.random() < self.random_action_rate or recommended_action not in possible_actions:
            return possible_actions[np.random.randint(len(possible_actions))]
        else:
            return recommended_action
