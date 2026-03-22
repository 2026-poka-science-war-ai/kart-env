from __future__ import annotations

import functools
import os
import pathlib
import shutil
import socket
import struct
import subprocess
import time
from typing import Any

import numpy as np
from gymnasium import spaces
from pettingzoo import ParallelEnv

from .utils.dolphin_mem import DolphinMem, ObservationDict
from .utils.enums import (
    DOLPHIN_PATH,
    GC_BUTTONS,
    GcAction,
    NEUTRAL_ACTION,
    NOVNC_BASE,
    SOCK_BASE,
    VNC_BASE,
)
from .utils.kart_graphic_obs import KartGraphicObs
from .utils.helper import launch_game
from .utils.macro_helper import OptionType

AgentID = int
ObsType = dict[str, Any]
ActionType = GcAction

# Pre-compiled struct for packing 4-player actions (H + 6f per player * 4)
_ACTION_STRUCT = struct.Struct("<" + "H6f" * 4)

# Pre-computed payload for neutral (no-input) frames — avoids packing on every idle frame
_NEUTRAL_STEP_PAYLOAD = b"step" + _ACTION_STRUCT.pack(
    *(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) * 4
)


class KartEnvironment(ParallelEnv):
    metadata = {"name": "kart_environment"}

    def __init__(self, env_id: int = 0, options: OptionType | None = None):
        self.options = options if options is not None else OptionType()
        self._closed = False

        self.possible_agents = list(range(self.options.num_agents))
        self.agents = self.possible_agents

        self.env_id = env_id
        self.vnc_port = VNC_BASE + env_id
        self.novnc_port = NOVNC_BASE + env_id
        self.sock_port = SOCK_BASE + env_id
        self.user_dir = pathlib.Path("users") / str(env_id)

        if not self.user_dir.exists():
            dolphin_settings_path = pathlib.Path(__file__).parent / "dolphin_settings"
            shutil.copytree(dolphin_settings_path, self.user_dir)
            self.options.is_license_created = False

        self.processes: list[subprocess.Popen] = []
        self._run_env()
        launch_game(self, self.options)
        self.graphic_obs = KartGraphicObs(self.env_id)
        self.save_slot(0)

    def __del__(self) -> None:
        self.close()

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None,
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        if options is None:
            options = {}

        if options.get("slot") is not None:
            self.load_slot(options["slot"])
        elif options.get("file") is not None:
            self.load_file(options["file"])
        else:
            self.load_slot(0)

        raw_vector_obs = self.mem.read_obs()
        raw_graphic_obs = self.graphic_obs.get()

        observations = self._build_observations(raw_vector_obs, raw_graphic_obs)
        infos: dict[AgentID, dict[str, Any]] = {aid: {} for aid in self.agents}

        return observations, infos

    def step(self, actions: dict[AgentID, ActionType]) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict],
    ]:
        self._send_actions(actions)

        raw_vector_obs = self.mem.read_obs()
        raw_graphic_obs = self.graphic_obs.get()

        observations = self._build_observations(raw_vector_obs, raw_graphic_obs)

        player_infos = raw_vector_obs["PLAYER_INFO"]
        rewards: dict[AgentID, float] = {}
        terminations: dict[AgentID, bool] = {}
        truncations: dict[AgentID, bool] = {}
        infos: dict[AgentID, dict] = {}

        for agent_id in self.agents:
            rewards[agent_id] = 0.0
            terminations[agent_id] = bool(player_infos[agent_id]["StateBit"] & 32)
            truncations[agent_id] = False
            infos[agent_id] = {}

        return observations, rewards, terminations, truncations, infos

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        self.graphic_obs.close()
        self.conn.sendall(b"close")
        self.conn.close()
        self.server_sock.close()

        try:
            for proc in reversed(self.processes):
                proc.terminate()
                proc.wait()

        except Exception:
            pass

    def click(self, actions: dict[AgentID, ActionType], num_frame: int = 250) -> None:
        self._send_actions(actions)
        # Fast path: send pre-computed neutral payload for idle frames
        sendall = self.conn.sendall
        recv = self.conn.recv
        neutral = _NEUTRAL_STEP_PAYLOAD
        for _ in range(num_frame):
            sendall(neutral)
            assert recv(1024) == b"step_done"

    def save_file(self, path: str) -> None:
        self.conn.sendall(b"savefile" + path.encode())
        assert self.conn.recv(1024) == b"save_done"

    def save_slot(self, slot: int) -> None:
        self.conn.sendall(b"saveslot" + str(slot).encode())
        assert self.conn.recv(1024) == b"save_done"

    def load_file(self, path: str) -> None:
        self.conn.sendall(b"loadfile" + path.encode())
        assert self.conn.recv(1024) == b"load_done"

    def load_slot(self, slot: int) -> None:
        self.conn.sendall(b"loadslot" + str(slot).encode())
        assert self.conn.recv(1024) == b"load_done"

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):  # type: ignore
        return spaces.Discrete(1)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):  # type: ignore
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

    def _run_env(self) -> None:
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

        script_path = pathlib.Path(__file__).parent / "script.py"
        dolphin_command = [
            "vglrun",
            "-d",
            "egl0",
            DOLPHIN_PATH,
            "--batch",
            f"--user={self.user_dir}",
            "-e",
            "MarioKartWii.iso",
            "--script",
            script_path,
        ]
        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        dolphin_env["ENV_ID"] = f"{self.env_id}"
        dolphin_process = subprocess.Popen(dolphin_command, env=dolphin_env)
        self.processes.append(dolphin_process)

        self.conn, _ = self.server_sock.accept()
        self.mem = DolphinMem(dolphin_process.pid)

    def _build_observations(
        self,
        raw_vector_obs: ObservationDict,
        raw_graphic_obs: list[Any],
    ) -> dict[AgentID, ObsType]:
        race_info = raw_vector_obs["RACE_INFO"]
        player_infos = raw_vector_obs["PLAYER_INFO"]
        shared_gfx = (raw_graphic_obs[0], raw_graphic_obs[1], raw_graphic_obs[2])
        return {
            agent_id: {
                "RACE_INFO": race_info,
                "PLAYER_INFO": player_infos[agent_id],
                "GRAPHIC_INFO": (*shared_gfx, raw_graphic_obs[3 + agent_id]),
            }
            for agent_id in self.agents
        }

    def _pack_actions(self, actions: dict[AgentID, ActionType]) -> bytes:
        data: list[int | float] = []
        for i in range(len(self.agents)):
            action: GcAction = {**NEUTRAL_ACTION}  # type: ignore[typeddict-item]
            if i in actions:
                action.update(actions[i])

            button_mask = 0
            for j, btn in enumerate(GC_BUTTONS):
                if action.get(btn):  # type: ignore[arg-type]
                    button_mask |= 1 << j

            data.append(button_mask)
            data.extend(
                [
                    action.get("StickX", 0.0),
                    action.get("StickY", 0.0),
                    action.get("CStickX", 0.0),
                    action.get("CStickY", 0.0),
                    action.get("TriggerLeft", 0.0),
                    action.get("TriggerRight", 0.0),
                ]
            )

        return _ACTION_STRUCT.pack(*data)

    def _send_actions(self, actions: dict[AgentID, ActionType]) -> None:
        payload = b"step" + self._pack_actions(actions)
        self.conn.sendall(payload)
        assert self.conn.recv(1024) == b"step_done"
