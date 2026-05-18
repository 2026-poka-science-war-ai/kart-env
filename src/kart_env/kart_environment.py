import functools
import os
import pathlib
import shutil
import socket
import struct
import subprocess
import time
from typing import Any, Dict

from gymnasium import spaces
import numpy as np
from pettingzoo import ParallelEnv

from .utils.dolphin_mem import DolphinMem
from .utils.kart_graphic_obs import KartGraphicObs
from .utils.helper import launch_game
from .utils.macro_helper import OptionType
from .utils.enums import (
    VNC_BASE,
    NOVNC_BASE,
    SOCK_BASE,
    DOLPHIN_PATH,
    GC_BUTTONS,
    NEUTRAL_ACTION,
)


class KartEnvironment(ParallelEnv):
    metadata = {"name": "kart_environment"}
    ObsType = Dict[str, Any]
    ActionType = Dict[str, Any]
    AgentID = int

    def __init__(self, env_id: int = 0, options: OptionType | None = None):
        self.env_id = env_id
        self.options = options if options is not None else OptionType()
        self._closed = False
        self.agents = [i for i in range(self.options.num_agents)]

        self.processes: list[subprocess.Popen] = []

        user_dir = pathlib.Path("users") / str(self.env_id)
        if not user_dir.exists():
            dolphin_settings_path = pathlib.Path(__file__).parent / "dolphin_settings"
            shutil.copytree(dolphin_settings_path, user_dir)
            self.is_license_created = False

        vnc_port = VNC_BASE + self.env_id
        novnc_port = NOVNC_BASE + self.env_id
        sock_port = SOCK_BASE + self.env_id

        stdout = None if self.options.verbose else subprocess.DEVNULL
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_sock.bind(("localhost", sock_port))
        self.server_sock.listen(1)

        xvfb_command = [
            "Xvfb",
            f":{self.env_id}",
            "-screen",
            "0",
            "640x480x24",
            "-extension",
            "GLX",
        ]
        self.processes.append(
            subprocess.Popen(xvfb_command, stdout=stdout, stderr=stdout)
        )
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
            str(vnc_port),
        ]
        self.processes.append(
            subprocess.Popen(x11vnc_command, stdout=stdout, stderr=stdout)
        )

        websockify_command = [
            "websockify",
            "--web",
            "/usr/share/novnc/",
            str(novnc_port),
            f"localhost:{vnc_port}",
        ]
        self.processes.append(
            subprocess.Popen(websockify_command, stdout=stdout, stderr=stdout)
        )

        script_path = pathlib.Path(__file__).parent / "script.py"
        dolphin_command = [
            "vglrun",
            "-d",
            "egl0",
            DOLPHIN_PATH,
            "--batch",
            f"--user={user_dir}",
            "-e",
            "MarioKartWii.iso",
            "--script",
            script_path,
        ]
        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        dolphin_env["ENV_ID"] = f"{self.env_id}"
        dolphin_env["NUM_AGENTS"] = f"{self.options.num_agents}"
        dolphin_process = subprocess.Popen(
            dolphin_command, env=dolphin_env, stdout=stdout, stderr=stdout
        )
        self.processes.append(dolphin_process)
        self.conn, _ = self.server_sock.accept()

        self.dolphin_mem = DolphinMem(dolphin_process.pid)
        self.graphic_obs = KartGraphicObs(self.env_id)

    def __del__(self):
        self.close()

    def close(self):
        if self._closed:
            return

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

        self._closed = True

    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:
        launch_game(self, self.options)

        return self._get_obs(), {agent_id: {} for agent_id in self.agents}

    def step(self, actions: dict[AgentID, ActionType]) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict],
    ]:
        self._send_actions(actions)

        observations = self._get_obs()
        rewards = {}
        terminations = {}
        truncations = {}
        infos = {}

        for agent_id in self.agents:
            reward = observations[agent_id]["PLAYER_INFO"]["CurrentRaceCompletion"]
            rewards[agent_id] = reward

            termination = bool(observations[agent_id]["PLAYER_INFO"]["StateBit"] & 32)
            terminations[agent_id] = termination

            truncations[agent_id] = False
            infos[agent_id] = {}

        return observations, rewards, terminations, truncations, infos

    def _get_obs(self) -> dict[AgentID, ObsType]:
        raw_vector_obs = self.dolphin_mem.read_obs(self.options.num_agents)
        raw_graphic_obs = self.graphic_obs.get()

        observations = {}
        for agent_id in self.agents:
            observation = {
                "RACE_INFO": raw_vector_obs["RACE_INFO"],
                "PLAYER_INFO": raw_vector_obs["PLAYER_INFO"][agent_id],
                "GRAPHIC_INFO": (
                    raw_graphic_obs[0],
                    raw_graphic_obs[1],
                    raw_graphic_obs[2],
                    raw_graphic_obs[3 + agent_id],
                ),
            }
            observations[agent_id] = observation

        return observations

    def _send_actions(self, actions: dict[AgentID, ActionType]):
        payload = b"step" + self._pack_actions(actions)
        self.conn.sendall(payload)
        assert self.conn.recv(1024) == b"step_done"

    def _pack_actions(self, actions: dict[AgentID, ActionType]) -> bytes:
        data = []
        for i in range(len(self.agents)):
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

        return struct.pack("<" + "H6f" * self.options.num_agents, *data)

    def click(self, actions: dict[AgentID, ActionType], num_frame: int = 250):
        for _ in range(3):
            self._send_actions(actions)
        for _ in range(num_frame):
            self._send_actions({})

    def save_file(self, path: str):
        self.conn.sendall(b"savefile" + path.encode())
        assert self.conn.recv(1024) == b"save_done"

    def save_slot(self, slot: int):
        self.conn.sendall(b"saveslot" + str(slot).encode())
        assert self.conn.recv(1024) == b"save_done"

    def load_file(self, path: str):
        self.conn.sendall(b"loadfile" + path.encode())
        assert self.conn.recv(1024) == b"load_done"

    def load_slot(self, slot: int):
        self.conn.sendall(b"loadslot" + str(slot).encode())
        assert self.conn.recv(1024) == b"load_done"

    # fmt: off
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent) -> spaces.Space:  # type: ignore
        max_h, max_w = 456, 608
        image_space = spaces.Box(low=0, high=255, shape=(max_h, max_w, 4), dtype=np.uint8)

        return spaces.Dict({
            "RACE_INFO": spaces.Dict({
                "StageID": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "FrameCount": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "PlayerCount": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "CourseID": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "EngineClass": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
            }),
            "PLAYER_INFO": spaces.Dict({
                "PlayerID": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "LocalPlayerNum": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "RealControllerID": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "KartID": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "CharacterID": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),

                "CurrentRaceCompletion": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "MaxRaceCompletion": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "FirstKcpLapCompletion": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "NextCheckpointLapCompletion": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "NextCheckpointLapCompletionMax": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),

                "CurrentLap": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "MaxLap": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "currentKCP": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "maxKCP": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "StateBit": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),

                "SoftSpeedLimit": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "HardSpeedLimit": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),

                "Position": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),
                "Velocity": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),
                "InternalVelocity": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),
                "ExternalVelocity": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),
                "AngularVelocity": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),
                "Acceleration": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),

                "MainRotation": spaces.Box(-np.inf, np.inf, shape=(4,), dtype=np.float32),

                "Speed": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "AccelerationKartMove": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),

                "DriftState": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "MiniturboCharge": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "SMiniturboCharge": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "OffroadInvincibilityTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),

                "WheelieFrameCount": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "WheelieCooldownCount": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "LeanRot": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),

                "BitField0": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "BitField1": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "BitField2": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "BitField3": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "SurfaceFlag": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),

                "Hop": spaces.Box(-np.inf, np.inf, shape=(3,), dtype=np.float32),

                "MTBoostTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "AllMTCharge": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "MushroomBoostTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "TrickableTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "TrickCooldown": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "AirtimeCount": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),

                "RacePosition": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "FloorCollisionCount": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "RespawnTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "WallCollideFlag": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),

                "Item": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "ItemNum": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "PassiveItem": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
                "PassiveItemNum": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),

                "StarTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "ShockTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "BlooperInkTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "BlooperStateFlag": spaces.Box(0, np.iinfo(np.uint8).max, shape=(), dtype=np.uint8),
                "CrushTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),
                "MegaTimer": spaces.Box(0, np.iinfo(np.uint16).max, shape=(), dtype=np.uint16),

                "startBoostCharge": spaces.Box(-np.inf, np.inf, shape=(), dtype=np.float32),
                "startBoostIdx": spaces.Box(0, np.iinfo(np.uint32).max, shape=(), dtype=np.uint32),
            }),
            "GRAPHIC_INFO": spaces.Tuple((
                image_space,
                image_space,
                image_space,
                image_space
            ))
        })
    # fmt: on

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
