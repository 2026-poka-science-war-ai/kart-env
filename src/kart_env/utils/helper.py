from __future__ import annotations

import hashlib
import json
import pathlib
from typing import TYPE_CHECKING

from .macro_helper import *

if TYPE_CHECKING:
    from ..kart_environment import KartEnvironment


def _options_to_dict(options: OptionType) -> dict:
    result = {}
    for key, value in options.__dict__.items():
        if isinstance(value, list):
            result[key] = [item.name for item in value]
        elif isinstance(value, Enum):
            result[key] = value.name
        else:
            result[key] = value
    return result


def launch_game(env: KartEnvironment, options: OptionType):
    options_dict = _options_to_dict(options)
    options_json = json.dumps(options_dict, sort_keys=True)
    options_hash = hashlib.md5(options_json.encode("utf-8")).hexdigest()
    states_dir = pathlib.Path("./states")
    states_dir.mkdir(parents=True, exist_ok=True)
    state_path = states_dir / f"kart_env_{options_hash}.state"
    if state_path.exists():
        env.load_file(str(state_path))
        return

    enter_main_menu(env)

    if not options.online_mode:
        match options.num_agents:
            case 1:
                _launch_game_1p(env, options)
            case 4:
                _launch_game_4p(env, options)
            case 12:
                raise NotImplementedError("12 players mode is not implemented yet.")
            case _:
                raise NotImplementedError("Only 1, 4, 12 agents are supported now.")
    else:
        _launch_game_wfc(env, options)

    env.save_file(str(state_path))


def enter_main_menu(env: KartEnvironment) -> None:
    all_A = {agent_id: {"A": 1} for agent_id in env.agents}
    env.click({}, num_frame=500)
    env.click(all_A, num_frame=500)

    if env.is_license_created:
        for _ in range(2):
            env.click(all_A)
    else:
        for _ in range(7):
            env.click(all_A)


def _launch_game_1p(env: KartEnvironment, options: OptionType):
    env.click({0: {"A": 1}}, num_frame=500)

    env.click({0: {"Down": 1}}, num_frame=10)
    env.click({0: {"Down": 1}}, num_frame=10)
    env.click({0: {"A": 1}}, num_frame=100)  # select VS Race in ["VS Race", "Battle"]

    # setting rules (CC, CPU, etc.)
    env.click({0: {"Up": 1}}, num_frame=10)
    env.click({0: {"A": 1}}, num_frame=100)
    select_rules(env, options)
    env.click({0: {"Down": 1}}, num_frame=10)

    if options.race == RaceChoice.SOLO_RACE:
        env.click({0: {"A": 1}})
    elif options.race == RaceChoice.TEAM_RACE:
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"A": 1}})

    select_character(env, options)

    if options.race == RaceChoice.TEAM_RACE:
        # Team select
        env.click({0: {"A": 1}})

    select_vehicle(env, options)

    if options.drift_modes[0] == DriftModeChoice.AUTOMATIC:
        env.click({0: {"Up": 1}}, num_frame=10)
        env.click({0: {"A": 1}}, num_frame=10)
    elif options.drift_modes[0] == DriftModeChoice.MANUAL:
        env.click({0: {"A": 1}}, num_frame=10)
    env.click({})

    select_cup(env, options)

    select_course(env, options)

    env.click({}, num_frame=1250)


def _launch_game_4p(env: KartEnvironment, options: OptionType):
    for _ in range(3):
        env.click({0: {"Right": 1}}, num_frame=10)
    env.click({0: {"A": 1}})

    env.click({1: {"A": 1}}, num_frame=10)
    env.click({2: {"A": 1}}, num_frame=10)
    env.click({3: {"A": 1}}, num_frame=10)
    env.click({}, num_frame=50)
    env.click({0: {"A": 1}}, num_frame=100)

    env.click({0: {"A": 1}}, num_frame=100)  # select VS Race in ["VS Race", "Battle"]

    # setting rules (CC, CPU, etc.)
    env.click({0: {"Up": 1}}, num_frame=10)
    env.click({0: {"A": 1}}, num_frame=100)
    select_rules(env, options)
    env.click({0: {"Down": 1}}, num_frame=10)

    if options.race == RaceChoice.SOLO_RACE:
        env.click({0: {"A": 1}})
    elif options.race == RaceChoice.TEAM_RACE:
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"A": 1}})

    select_character(env, options)

    if options.race == RaceChoice.TEAM_RACE:
        # Team select (1, 3p select red team, 2, 4p select green team)
        env.click({0: {"A": 1}, 1: {"A": 1}, 2: {"A": 1}, 3: {"A": 1}})
        env.click({0: {"A": 1}})

    select_vehicle(env, options)

    for i in range(options.num_agents):
        if options.drift_modes[i] == DriftModeChoice.AUTOMATIC:
            env.click({i: {"A": 1}}, num_frame=10)
        elif options.drift_modes[i] == DriftModeChoice.MANUAL:
            env.click({i: {"Down": 1}}, num_frame=10)
            env.click({i: {"A": 1}}, num_frame=10)
    env.click({})

    select_cup(env, options)

    select_course(env, options)

    env.click({}, num_frame=1250)


def _launch_game_wfc(env: KartEnvironment, options: OptionType):
    raise NotImplementedError("12 players mode is not implemented yet.")


def select_character(env: KartEnvironment, options: OptionType):
    if options.num_agents >= 4:
        env.click({3: {"Down": 1}}, num_frame=10)
        env.click({3: {"Down": 1}}, num_frame=10)
        env.click({3: {"Down": 1}}, num_frame=10)
        env.click({3: {"Down": 1}}, num_frame=10)
        env.click({3: {"Right": 1}}, num_frame=10)
    if options.num_agents >= 3:
        env.click({2: {"Right": 1}}, num_frame=10)
        env.click({2: {"Right": 1}}, num_frame=10)
        env.click({2: {"Down": 1}}, num_frame=10)
        env.click({2: {"Down": 1}}, num_frame=10)
        env.click({2: {"Down": 1}}, num_frame=10)
        env.click({2: {"Right": 1}}, num_frame=10)
    if options.num_agents >= 2:
        env.click({1: {"Right": 1}}, num_frame=10)
        env.click({1: {"Down": 1}}, num_frame=10)
        env.click({1: {"Down": 1}}, num_frame=10)
        env.click({1: {"Down": 1}}, num_frame=10)
        env.click({1: {"Down": 1}}, num_frame=10)
        env.click({1: {"Right": 1}}, num_frame=10)
    if options.num_agents >= 1:
        env.click({0: {"Right": 1}}, num_frame=10)
        env.click({0: {"Right": 1}}, num_frame=10)
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"Down": 1}}, num_frame=10)
        env.click({0: {"Right": 1}}, num_frame=10)

    selected_coordinate = []
    selected_choices = []
    for i in range(options.num_agents):
        selected_coordinate.append(CharacterPositionMap[options.character[i]])
        selected_choices.append(
            (i, selected_coordinate[i][0] * 4 + selected_coordinate[i][1])
        )

    for i, _ in sorted(selected_choices, key=lambda x: x[1]):
        row, col = selected_coordinate[i]
        for _ in range(6 - row):
            env.click({i: {"Up": 1}}, num_frame=10)
        for _ in range(3 - col):
            env.click({i: {"Left": 1}}, num_frame=10)
        env.click({i: {"A": 1}}, num_frame=10)

    env.click({})


def select_vehicle(env: KartEnvironment, options: OptionType):
    selected_class = coerce_choice(options.cc, CCChoice)

    for player_id in range(options.num_agents):
        selected_character = coerce_choice(
            options.character[player_id], CharacterChoice
        )
        selected_vehicle = coerce_choice(options.vehicle[player_id], VehicleChoice)

        selected_vehicle_info = VehicleInfoMap[selected_vehicle]
        target_size = get_character_size(selected_character)
        allowed_types = get_allowed_vehicle_types(selected_class)

        isGrandPrix = False
        if selected_vehicle_info.vehicle_type not in allowed_types and isGrandPrix:
            allowed_text = ", ".join(
                vehicle_type.value for vehicle_type in allowed_types
            )
            raise ValueError(
                f"{selected_vehicle.value} is {selected_vehicle_info.vehicle_type.value}, "
                f"but {selected_class.value} allows only: {allowed_text}."
            )

        is_grid = (
            True if options.num_agents == 1 or options.online_mode else False
        )  # relevant for single play. choose kart via grid
        if is_grid:
            start_row, start_col = (0, 0)
            target_row, target_col = VehiclePositionMap[selected_vehicle]
            row_shift = target_row - start_row
            col_shift = target_col - start_col

            vertical_move_key = "Up" if row_shift <= 0 else "Down"
            for _ in range(abs(row_shift)):
                env.click({player_id: {vertical_move_key: 1}}, num_frame=10)

            horizontal_move_key = "Left" if col_shift <= 0 else "Right"
            for _ in range(abs(col_shift)):
                env.click({player_id: {horizontal_move_key: 1}}, num_frame=10)
            env.click({player_id: {"A": 1}}, num_frame=150)

        else:
            success = False
            vehicle_queue = VehicleChoiceQueue[target_size]
            for vehicle in vehicle_queue:
                env.click({player_id: {}}, num_frame=10)
                if vehicle == selected_vehicle:
                    env.click({player_id: {"A": 1}}, num_frame=150)
                    success = True
                    break
                else:
                    env.click({player_id: {"Right": 1}}, num_frame=10)
            if not success:
                raise ValueError(
                    f"{selected_vehicle.value} not found in selection queue. Please check the vehicle choice and queue configuration."
                )


def select_cup(env: KartEnvironment, options: OptionType):
    target_row, target_col = CupPositionMap[Course2CupMap[options.course]]

    for _ in range(target_row):
        env.click({0: {"Down": 1}}, num_frame=10)

    for _ in range(target_col):
        env.click({0: {"Right": 1}}, num_frame=10)

    env.click({0: {"A": 1}}, num_frame=100)


def select_course(env: KartEnvironment, options: OptionType):
    target_index = CoursePositionMap[options.course]
    for _ in range(target_index):
        env.click({0: {"Down": 1}}, num_frame=10)
    env.click({0: {"A": 1}}, num_frame=100)
    env.click({0: {"A": 1}})


def select_rules(env: KartEnvironment, options: OptionType):
    selected_class = coerce_choice(options.cc, CCChoice)
    selected_cpu = coerce_choice(options.cpu, CPUChoice)
    selected_vehicle_rule = coerce_choice(options.vehicle_rule, VehicleRuleChoice)
    selected_course_rule = coerce_choice(options.course_rule, CourseRuleChoice)
    selected_item_rule = coerce_choice(options.item_rule, ItemRuleChoice)
    selected_races = coerce_choice(options.races, RacesChoice)

    start_col_map = {
        "class": 1,
        "cpu": 1,
        "vehicle_rule": 0,
        "course_rule": 0,
        "item_rule": 0,
        "races": 2,
    }
    selected_rule_map = {
        "class": selected_class,
        "cpu": selected_cpu,
        "vehicle_rule": selected_vehicle_rule,
        "course_rule": selected_course_rule,
        "item_rule": selected_item_rule,
        "races": selected_races,
    }

    # class
    for selected_rule_name in selected_rule_map.keys():
        selected_rule = selected_rule_map[selected_rule_name]

        start_col = start_col_map[selected_rule_name]
        _, target_col = RulesPositionMap[selected_rule]
        col_shift = target_col - start_col

        horizontal_move_key = "Left" if col_shift <= 0 else "Right"
        for _ in range(abs(col_shift)):
            env.click({0: {horizontal_move_key: 1}}, num_frame=40)
        env.click({0: {"A": 1}}, num_frame=40)

    env.click({0: {"A": 1}}, num_frame=100)
