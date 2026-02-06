from utils.kart_instance import KartInstance

if __name__ == "__main__":
    envs = [KartInstance(env_id=i, hard_reset=True) for i in range(3)]
