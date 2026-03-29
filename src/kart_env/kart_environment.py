import functools
from dataclasses import replace
from pettingzoo import ParallelEnv
from gymnasium import spaces
import pathlib
from typing import Any, Dict
import subprocess
import os
import shutil
import time
import socket
import struct
import numpy as np

from .utils.dolphin import Dolphin
from .utils.dolphin_mem import DolphinMem
from .utils.kart_graphic_obs import KartGraphicObs, save_graphic_obs
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
        self._closed = False

        self.dolphins: list[Dolphin] = []
        self.dolphins_mem: list[DolphinMem] = []
        self.graphic_obss: list[KartGraphicObs] = []

        self.agents = [i for i in range(self.options.num_agents)]

        if self.options.online_mode:
            self.agent_mapper = lambda x: (
                x,
                0,
            )  # agent_id corresponds directly to dolphin index
            """mapping function from global agent_id to (dolphin_idx, agent_id_within_dolphin)"""

            for i in range(self.options.num_agents):
                _options = replace(
                    self.options,
                    num_agents=1,
                    character=[self.options.character[i]],
                    vehicle=[self.options.vehicle[i]],
                    drift_modes=[self.options.drift_modes[i]],
                )
                dolphin = Dolphin(instance_id=12 * env_id + i, options=_options)
                assert dolphin.dolphin_proc_pid is not None

                self.dolphins.append(dolphin)
                self.dolphins_mem.append(DolphinMem(dolphin.dolphin_proc_pid))
        else:
            self.agent_mapper = lambda x: (0, x)  # dolphin_idx, agent_id_within_dolphin

            dolphin = Dolphin(instance_id=12 * env_id, options=self.options)
            assert dolphin.dolphin_proc_pid is not None

            self.dolphins.append(dolphin)
            self.dolphins_mem.append(DolphinMem(dolphin.dolphin_proc_pid))

        launch_game(self, self.options)
        for dolphin in self.dolphins:
            self.graphic_obss.append(KartGraphicObs(dolphin.env_id))
        self.save_slot(0)

    def __del__(self):
        self.close()

    def reset(
        self, seed=None, options: dict | None = {}
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict]]:
        if options is None:
            options = {}

        if options.get("slot") is not None:
            self.load_slot(options["slot"])
        elif options.get("file") is not None:
            self.load_file(options["file"])
        else:
            self.load_slot(0)

        observations = self._get_obs()
        infos = {}

        for agent_id in self.agents:
            infos[agent_id] = {}

        # TODO combine graphic_obs and vector_obs into a single observation dict

        return observations, infos

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

        observations = self._get_obs()

        for agent_id in self.agents:
            rewards[agent_id] = 0.0

            termination = bool(observations[agent_id]["PLAYER_INFO"]["StateBit"] & 32)
            terminations[agent_id] = termination

            truncations[agent_id] = False

            infos[agent_id] = {}

        return observations, rewards, terminations, truncations, infos

    def _get_obs(self) -> dict[AgentID, ObsType]:
        observations = {}

        if self.options.online_mode:
            for agent_id in self.agents:
                dolphin_idx, _ = self.agent_mapper(agent_id)
                raw_vector_obs = self.dolphins_mem[dolphin_idx].read_obs(0)
                raw_graphic_obs = self.graphic_obss[
                    dolphin_idx
                ].get()  # TODO give graphic obs correctly

                observation = {
                    "RACE_INFO": raw_vector_obs["RACE_INFO"],
                    "PLAYER_INFO": raw_vector_obs["PLAYER_INFO"][0],
                    "GRAPHIC_INFO": (
                        raw_graphic_obs[0],
                        raw_graphic_obs[1],
                        raw_graphic_obs[2],
                        raw_graphic_obs[3],
                    ),
                }
                observations[agent_id] = observation

        else:
            raw_vector_obs = self.dolphins_mem[0].read_obs(self.options.num_agents)
            raw_graphic_obs = self.graphic_obss[
                0
            ].get()  # TODO give graphic obs correctly
            # save_graphic_obs(raw_graphic_obs) # for DEBUG
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

    def close(self):
        if self._closed:
            return
        self._closed = True

        for graphic_obs in self.graphic_obss:
            graphic_obs.close()

        for dolphin in self.dolphins:
            dolphin.close()

    def click(self, actions: dict[AgentID, ActionType], num_frame: int = 250):
        self._send_actions(actions)
        for _ in range(num_frame - 1):
            self._send_actions({})

    def _send_actions(self, actions: dict[AgentID, ActionType]):
        self.async_send_actions(actions)
        self.await_send_actions()

    def async_send_actions(self, actions: dict[AgentID, ActionType]):
        new_actions = {
            idx: {} for idx in range(len(self.dolphins))
        }  # {dolphin_idx: {agent_id_within_dolphin: action}}
        for agent_id, action in actions.items():
            dolphin_idx, agent_id_within_dolphin = self.agent_mapper(agent_id)
            new_actions[dolphin_idx][agent_id_within_dolphin] = action

        for dolphin_idx, dolphin_actions in new_actions.items():
            self.dolphins[dolphin_idx].async_send_actions(dolphin_actions)

    def await_send_actions(self):
        for dolphin in self.dolphins:
            dolphin.await_send_actions()

    def await_step_done(self):
        for dolphin in self.dolphins:
            dolphin.await_send_actions()

    def async_save_file(self, path: str):
        for dolphin in self.dolphins:
            dolphin.async_save_file(path)

    def async_save_slot(self, slot: int):
        for dolphin in self.dolphins:
            dolphin.async_save_slot(slot)

    def await_save_done(self):
        for dolphin in self.dolphins:
            dolphin.await_save_done()

    def save_file(self, path: str):
        self.async_save_file(path)
        self.await_save_done()

    def save_slot(self, slot: int):
        self.async_save_slot(slot)
        self.await_save_done()

    def async_load_file(self, path: str):
        for dolphin in self.dolphins:
            dolphin.async_load_file(path)

    def async_load_slot(self, slot: int):
        for dolphin in self.dolphins:
            dolphin.async_load_slot(slot)

    def await_load_done(self):
        for dolphin in self.dolphins:
            dolphin.await_load_done()

    def load_file(self, path: str):
        self.async_load_file(path)
        self.await_load_done()

    def load_slot(self, slot: int):
        self.async_load_slot(slot)
        self.await_load_done()

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
