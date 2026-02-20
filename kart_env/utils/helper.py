from .enums import NEUTRAL_ACTION
from ..kart_environment import KartEnvironment


def free(env: KartEnvironment, num_frame: int = 500):
    for _ in range(num_frame):
        env.step({i: NEUTRAL_ACTION for i in range(4)})


def exec_cmd(env: KartEnvironment, command: str):
    env.conn.sendall(b"exec" + command.encode())
