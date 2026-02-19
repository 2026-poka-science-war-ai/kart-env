import functools
from pettingzoo import ParallelEnv
from gymnasium import spaces
import pathlib
from typing import TypeVar
import subprocess
import os
import shutil
import time
import atexit

from .utils.kart_mem import KartMem
from .utils.dolphin_pipe import DolphinPipe
from .utils.enums import (
    vnc_base,
    novnc_base,
    user_base,
    dolphin_path,
    iso_path,
    dolphin_settings_path,
)

ObsType = TypeVar("ObsType")
ActionType = TypeVar("ActionType")
AgentID = TypeVar("AgentID")


class KartEnvironment(ParallelEnv):
    metadata = {"name": "kart_environment"}

    def __init__(self, env_id: int = 0):
        self.possible_agents = [i for i in range(4)]
        self.agents = self.possible_agents

        self.env_id = env_id
        self.vnc_port = vnc_base + env_id
        self.novnc_port = novnc_base + env_id
        self.user_dir = pathlib.Path(user_base) / str(env_id)

        if not self.user_dir.exists():
            shutil.copytree(dolphin_settings_path, self.user_dir)

        self.processes: list[subprocess.Popen] = []
        atexit.register(self.close)
        self._run_env()
        # TODO macro to start game
        # TODO save memory state to fast reset

    def reset(
        self, seed=None, options=None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:

        observations = {}
        # TODO load saved memory state
        for i, agent in enumerate(self.agents):
            observations[agent] = 1  # TODO get observation from felk dolphin
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

        for i, agent in enumerate(self.agents):
            # TODO send action and return obs from felk python
            observations[agent] = 1
            rewards[agent] = 0.0
            terminations[agent] = False
            truncations[agent] = False
            infos[agent] = {}
        return observations, rewards, terminations, truncations, infos

    def close(self):
        try:
            for proc in reversed(self.processes):
                proc.terminate()
                proc.wait()

            # TODO close dolphin pipe
        except Exception:
            pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):  # type: ignore
        return spaces.Discrete(1)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):  # type: ignore
        return spaces.Discrete(1)

    def _run_env(self):
        # TODO make dolphin pipe file

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
            dolphin_path,
            "--batch",
            f"--user={self.user_dir}",
            "-e",
            iso_path,
        ]
        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        dolphin_process = subprocess.Popen(dolphin_command, env=dolphin_env)
        self.processes.append(dolphin_process)
        self.mem = KartMem(dolphin_process.pid)
