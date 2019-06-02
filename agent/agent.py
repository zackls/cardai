import numpy as np

from helpers import getClosestObservedState, getValidActionsInState

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

        self.learning_rate = params.learning_rate if params.learning_rate else 0.4
        self.discount_factor = params.discount_factor if params.discount_factor else 0.8
        self.endgame_discount_factor = params.endgame_discount_factor if params.endgame_discount_factor else 0.95
        self.random_action_rate = params.random_action_rate if params.random_action_rate else 0.1
        self.dyna_steps = params.dyna_steps if params.dyna_steps else 10
        self.verbose = params.verbose if params.verbose else False

        # Current state
        self.s = None

        # Last action
        self.a = None

    '''
    Set the initial state and return an action
    '''
    def set_initial_state(self, s):
        self.s = s

        self._select_action()

        return self.a

    def query(self, new_s, reward, game_ended = False):
        # Update q table for reward
        recommended_action = self._update_q(s, a, new_s, reward, self.endgame_discount_factor if game_ended else self.discount_factor)

        if self.dyna_steps:
            # If the game is over, update all past actions
            start = len(self.memory) - 1 if game_ended else len(self.memory) - min(self.dyna, len(self.memory)) - 1
            # Update q for past decisions
            for i in xrange(start, -1, -1):
                self._update_q(memory['s'], memory['a'], memory['s\''], memory['r'], self.endgame_discount_factor if game_ended else self.discount_factor)

        # Remember this
        self.memory.append({
            's': self.s,
            'a': self.a,
            's\'': new_s,
            'r': reward
        })

        # Update state
        self.s = new_s

        # Select new action
        self._select_action(recommended_action)

        return self.a

    def _update_q(self, s, a, new_s, reward, discount_factor):
        if s not in self.q:
            self.q[s] = {}
        if a not in self.q[s]:
            self.q[s][a] = 0

        # similarity scales the future estimate by how similar new_s is to the
        # closest state
        closest_state = None
        similarity = None
        if new_s not in self.q:
            self.q[new_s] = {}
            # find best action in closest state
            closest_state, similarity = helpers.getClosestObservedState(new_s, q)
        else:
            closest_state = new_s
            similarity = 1

        # find the best action in the closest state
        recommended_action = None
        best_utility = 0
        for action, expected_reward in self.q[closest_state].items():
            if expected_reward > best_utility:
                recommended_action = action

        # this is a typical q-learning except for "similarity," which is factored
        # in to help deal with how big the state space is
        self.q[s][a] = (1 - self.learning_rate) * self.q[s][a] + self.learning_rate * (reward + similarity * discount_factor * best_utility)

        return recommended_action

    def _select_action(self, recommended_action = None):
        # if no action is recommended or we randomly roll below our
        # random_action_rate, select a random action. might be a good idea to
        # have state similarity here to pick a closest observed action
        possible_actions = getValidActionsInState(self.s)
        if not recommended_action or np.random.random() < self.random_action_rate or recommended_action not in possible_actions:
            self.a = possible_actions[np.random.randint(len(possible_actions))]
        else:
            self.a = recommended_action
