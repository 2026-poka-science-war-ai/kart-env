from kart_env import KartEnvironment

if __name__ == "__main__":
    env = KartEnvironment()

    observations, infos = env.reset()

    for _ in range(5000):
        actions = {agent: env.action_space(agent).sample() for agent in env.agents}
        observations, rewards, terminations, truncations, infos = env.step(actions)

    env.close()
