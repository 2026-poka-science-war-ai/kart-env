from .enums import NEUTRAL_ACTION
from ..kart_environment import KartEnvironment


def free(env: KartEnvironment, num_frame: int = 1000):
    for _ in range(num_frame):
        env.step({})


def exec_cmd(env: KartEnvironment, command: str):
    env.conn.sendall(b"exec" + command.encode())


def launch_game(env: KartEnvironment):
    free(env, num_frame=100)
