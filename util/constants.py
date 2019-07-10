agent_constants = {
	"learning_rate": 0.4,
	"discount_factor": 0.8,
	"endgame_discount_factor": 0.975,
	"random_action_rate": 0.1,
	"dyna_steps": 10,
	"verbose": False,
}

run_constants = {
	"num_games": 1000,
	"verbose_mod": 1,
}

game_constants = {
	"num_agents": 2,
	"num_humans": 0,
	"sp_per_card": 2,
	"max_turns": 500,
	"win_reward": 1000,
	"verbose": False,
}

state_adjacency_constants = {
	"batch_size": 100
}

'''
Helper to use the default param if it doesnt exist in params
'''
def param_or_default(params, defaults, name):
	return params[name] if name in params else defaults[name]
