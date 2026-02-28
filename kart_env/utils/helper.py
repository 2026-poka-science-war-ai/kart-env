from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..kart_environment import KartEnvironment


def free(env: KartEnvironment, num_frame: int = 1000):
    for _ in range(num_frame):
        env._send_actions({})


def exec_cmd(env: KartEnvironment, command: str):
    env.conn.sendall(b"exec" + command.encode())


def launch_game(env: KartEnvironment):
    free(env, num_frame=500)
    env._send_actions({0: {"A": 1}})
    free(env, num_frame=250)
    env._send_actions({0: {"A": 1}})
    free(env, num_frame=250)
