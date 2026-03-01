import functools
from pettingzoo import ParallelEnv
from gymnasium import spaces
import pathlib
from typing import Any, Dict
import subprocess
import os
import shutil
import time
import atexit
import socket
import struct
import numpy as np

from .utils.dolphin_mem import DolphinMem
from .utils.enums import *
from .utils.helper import launch_game
from .utils.macro_helper import OptionType

ObsType = Dict[str, Any]
ActionType = Dict[str, Any]
AgentID = int


class KartEnvironment(ParallelEnv):
    metadata = {"name": "kart_environment"}

    def __init__(self, env_id: int = 0, options: OptionType | None = None):
        self.options = options if options is not None else OptionType()

        # Agents are indexed from 1 to num_agents, index 0 is reserved for environment-level observations
        self.possible_agents = [i for i in range(self.options.num_agents + 1)]
        self.agents = self.possible_agents

        self.env_id = env_id
        self.vnc_port = VNC_BASE + env_id
        self.novnc_port = NOVNC_BASE + env_id
        self.sock_port = SOCK_BASE + env_id
        self.user_dir = pathlib.Path(USER_BASE) / str(env_id)

        if not self.user_dir.exists():
            shutil.copytree(DOLPHIN_SETTINGS_PATH, self.user_dir)

        self.processes: list[subprocess.Popen] = []
        atexit.register(self.close)
        self._run_env()
        launch_game(self, self.options)
        # TODO save memory state to fast reset

    def reset(
        self, seed=None, options=None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:

        observations = {}
        self.conn.sendall(b"reset")  # TODO load saved memory state
        assert self.conn.recv(1024) == b"reset_done"

        vector_obs = self.mem.read_obs()
        # TODO combine graphic_obs and vector_obs into a single observation dict
        return vector_obs  # type: ignore

        return ({}, {})

    def step(self, actions: dict[AgentID, ActionType]) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict],
    ]:

        observations = {}
        rewards = {}
        terminations = {}
        truncations = {}
        infos = {}

        self._send_actions(actions)

        vector_obs = self.mem.read_obs()
        # TODO combine graphic_obs and vector_obs into a single observation dict
        return vector_obs  # type: ignore

        return observations, rewards, terminations, truncations, infos

    def close(self):
        self.conn.sendall(b"close")
        self.conn.close()
        self.server_sock.close()

        try:
            for proc in reversed(self.processes):
                proc.terminate()
                proc.wait()

        except Exception:
            pass

    def click(self, actions: dict[AgentID, ActionType], num_frame: int = 250):
        self._send_actions(actions)
        for _ in range(num_frame):
            self._send_actions({})

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):  # type: ignore
        return spaces.Discrete(1)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):  # type: ignore
        if agent == 0:
            return spaces.Discrete(1)
        return spaces.Dict(
            {
                "A": spaces.Discrete(2),
                "B": spaces.Discrete(2),
                "X": spaces.Discrete(2),
                # "Y": spaces.Discrete(2),
                # "Z": spaces.Discrete(2),
                # "Start": spaces.Discrete(2),
                "Up": spaces.Discrete(2),
                "Down": spaces.Discrete(2),
                # "Left": spaces.Discrete(2),
                # "Right": spaces.Discrete(2),
                "L": spaces.Discrete(2),
                "R": spaces.Discrete(2),
                "StickX": spaces.Box(-1.0, 1.0, (), np.float32),
                # "StickY": spaces.Box(-1.0, 1.0, (), np.float32),
                # "CStickX": spaces.Box(-1.0, 1.0, (), np.float32),
                # "CStickY": spaces.Box(-1.0, 1.0, (), np.float32),
                # "TriggerLeft": spaces.Box(0.0, 1.0, (), np.float32),
                # "TriggerRight": spaces.Box(0.0, 1.0, (), np.float32),
            }
        )

    def _run_env(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_sock.bind(("localhost", self.sock_port))
        self.server_sock.listen(1)

        xvfb_command = ["Xvfb", f":{self.env_id}", "-screen", "0", "640x480x24"]
        self.processes.append(subprocess.Popen(xvfb_command))
        while not os.path.exists(f"/tmp/.X11-unix/X{self.env_id}"):
            time.sleep(0.1)

        x11vnc_command = [
            "x11vnc",
            "-display",
            f":{self.env_id}",
            "-forever",
            "-nopw",
            "-shared",
            "-rfbport",
            str(self.vnc_port),
        ]
        self.processes.append(subprocess.Popen(x11vnc_command))

        websockify_command = [
            "websockify",
            "--web",
            "/usr/share/novnc/",
            str(self.novnc_port),
            f"localhost:{self.vnc_port}",
        ]
        self.processes.append(subprocess.Popen(websockify_command))

        dolphin_command = [
            "vglrun",
            "-d",
            "egl0",
            DOLPHIN_PATH,
            "--batch",
            f"--user={self.user_dir}",
            "-e",
            ISO_PATH,
            "--script",
            f"{SCRIPT_PATH}",
        ]
        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        dolphin_process = subprocess.Popen(dolphin_command, env=dolphin_env)
        self.processes.append(dolphin_process)

        self.conn, _ = self.server_sock.accept()
        self.mem = DolphinMem(dolphin_process.pid)

    def _pack_actions(self, actions: dict[AgentID, ActionType]) -> bytes:
        data = []
        for i in range(1, 5):
            action = NEUTRAL_ACTION.copy()
            if i in actions:
                action.update(actions[i])

            button_mask = 0
            for j, btn in enumerate(GC_BUTTONS):
                if action[btn]:
                    button_mask |= 1 << j

            data.append(button_mask)
            data.extend(
                [
                    action["StickX"],
                    action["StickY"],
                    action["CStickX"],
                    action["CStickY"],
                    action["TriggerLeft"],
                    action["TriggerRight"],
                ]
            )

        return struct.pack("<" + "H6f" * 4, *data)

    def _send_actions(self, actions: dict[AgentID, ActionType]):
        payload = b"step" + self._pack_actions(actions)
        self.conn.sendall(payload)
        assert self.conn.recv(1024) == b"step_done"
