from kart_env import KartEnvironment, OptionType

if __name__ == "__main__":
    options = OptionType(num_agents=4)
    env = KartEnvironment(options=options)

    observations, infos = env.reset()

    for _ in range(500):
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

    env.close()
