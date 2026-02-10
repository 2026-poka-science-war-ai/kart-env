from utils.kart_instance import KartInstance
from utils.macros import (
    ClassChoice,
    MainMenuChoice,
    SinglePlayerChoice,
    CharacterChoice,
    VehicleChoice,
    DriftModeChoice,
    CupChoice,
    enter_main_menu,
    select_class,
    select_main_menu,
    select_single_player,
    select_character,
    select_vehicle,
    select_cup,
    select_drift_mode,
)

if __name__ == "__main__":
    envs = [KartInstance(env_id=i, hard_reset=True) for i in range(3)]
    env = envs[0]
    
    enter_main_menu(env)
    
    select_main_menu(env, choice=MainMenuChoice.SINGLE_PLAYER)
    select_single_player(env, choice=SinglePlayerChoice.GRAND_PRIX)
    select_class(env, choice=ClassChoice.CC_150)
    select_character(env, choice=CharacterChoice.BABY_PEACH)
    select_vehicle(
        env,
        class_choice=ClassChoice.CC_150,
        character_choice=CharacterChoice.BABY_PEACH,
        vehicle_choice=VehicleChoice.NANOBIKE,
    )
    select_drift_mode(env, choice=DriftModeChoice.AUTOMATIC)
    select_cup(env, choice=CupChoice.LIGHTNING_CUP)