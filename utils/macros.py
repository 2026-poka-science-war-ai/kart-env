from enum import Enum
import time
from typing import NamedTuple, TypeVar
from utils.dolphin_pipe import Button
from utils.kart_instance import KartInstance


class MainMenuChoice(str, Enum):
    SINGLE_PLAYER = "single-player"
    MULTIPLAYER = "multiplayer"
    NINTENDO_WFC = "nintendo-wfc"
    MARIO_KART_CHANNEL = "mario-kart-channel"


class SinglePlayerChoice(str, Enum):
    GRAND_PRIX = "grand-prix"
    TIME_TRIALS = "time-trials"
    VS_RACE = "vs-race"
    BATTLE = "battle"


class ClassChoice(str, Enum):
    CC_50 = "50cc"
    CC_100 = "100cc"
    CC_150 = "150cc"
    MIRROR = "mirror"


class CharacterChoice(str, Enum):
    # --- Row 0 (Small) ---
    BABY_MARIO = "Baby Mario"
    BABY_LUIGI = "Baby Luigi"
    BABY_PEACH = "Baby Peach"
    BABY_DAISY = "Baby Daisy"

    # --- Row 1 (Small) ---
    TOAD = "Toad"
    TOADETTE = "Toadette"
    KOOPA_TROOPA = "Koopa Troopa"
    DRY_BONES = "Dry Bones"

    # --- Row 2 (Medium) ---
    MARIO = "Mario"
    LUIGI = "Luigi"
    PEACH = "Peach"
    DAISY = "Daisy"

    # --- Row 3 (Medium) ---
    YOSHI = "Yoshi"
    BIRDO = "Birdo"
    DIDDY_KONG = "Diddy Kong"
    BOWSER_JR = "Bowser Jr"

    # --- Row 4 (Large) ---
    WARIO = "Wario"
    WALUIGI = "Waluigi"
    DONKEY_KONG = "Donkey Kong"
    BOWSER = "Bowser"

    # --- Row 5 (Large) ---
    KING_BOO = "King Boo"
    ROSALINA = "Rosalina"
    FUNKY_KONG = "Funky Kong"
    DRY_BOWSER = "Dry Bowser"
    
    MII_A = "Mii A"
    MII_B = "Mii B"


CharacterPositionMap = {
    CharacterChoice.BABY_MARIO: (0, 0),
    CharacterChoice.BABY_LUIGI: (0, 1),
    CharacterChoice.BABY_PEACH: (0, 2),
    CharacterChoice.BABY_DAISY: (0, 3),
    
    CharacterChoice.TOAD: (1, 0),
    CharacterChoice.TOADETTE: (1, 1),
    CharacterChoice.KOOPA_TROOPA: (1, 2),
    CharacterChoice.DRY_BONES: (1, 3),
    
    CharacterChoice.MARIO: (2, 0),
    CharacterChoice.LUIGI: (2, 1),
    CharacterChoice.PEACH: (2, 2),
    CharacterChoice.DAISY: (2, 3),
    
    CharacterChoice.YOSHI: (3, 0),
    CharacterChoice.BIRDO: (3, 1),
    CharacterChoice.DIDDY_KONG: (3, 2),
    CharacterChoice.BOWSER_JR: (3, 3),
    
    CharacterChoice.WARIO: (4, 0),
    CharacterChoice.WALUIGI: (4, 1),
    CharacterChoice.DONKEY_KONG: (4, 2),
    CharacterChoice.BOWSER: (4, 3),
    
    CharacterChoice.KING_BOO: (5, 0),
    CharacterChoice.ROSALINA: (5, 1),
    CharacterChoice.FUNKY_KONG: (5, 2),
    CharacterChoice.DRY_BOWSER: (5, 3),
    
    CharacterChoice.MII_A: (6, 2),
    CharacterChoice.MII_B: (6, 3),
}


class VehicleType(str, Enum):
    KART = "kart"
    BIKE = "bike"

class VehicleSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class BikeStyle(str, Enum):
    DRIFT = "drift"
    HANG_ON = "hang-on"

class VehicleChoice(str, Enum):
    STANDARD_KART_S = "Standard Kart S"
    STANDARD_BIKE_S = "Standard Bike S"
    BABY_BOOSTER = "Baby Booster"
    BULLET_BIKE = "Bullet Bike"
    CONCERTO = "Concerto"
    NANOBIKE = "Nanobike"
    STANDARD_KART_M = "Standard Kart M"
    STANDARD_BIKE_M = "Standard Bike M"
    NOSTALGIA_1 = "Nostalgia 1"
    MACH_BIKE = "Mach Bike"
    WILD_WING = "Wild Wing"
    BON_BON = "Bon Bon"
    STANDARD_KART_L = "Standard Kart L"
    STANDARD_BIKE_L = "Standard Bike L"
    OFFROADER = "Offroader"
    BOWSER_BIKE = "Bowser Bike"
    FLAME_FLYER = "Flame Flyer"
    WARIO_BIKE = "Wario Bike"
    CHEEP_CHARGER = "Cheep Charger"
    QUACKER = "Quacker"
    RALLY_ROMPER = "Rally Romper"
    MAGIKRUISER = "Magikruiser"
    BLUE_FALCON = "Blue Falcon"
    BUBBLE_BIKE = "Bubble Bike"
    TURBO_BLOOPER = "Turbo Blooper"
    RAPIDE = "Rapide"
    ROYAL_RACER = "Royal Racer"
    NITROCYCLE = "Nitrocycle"
    B_DASHER_MK_2 = "B Dasher MK 2"
    DOLPHIN_DASHER = "Dolphin Dasher"
    PIRANHA_PROWLER = "Piranha Prowler"
    TWINKLE_STAR = "Twinkle Star"
    AERO_GLIDER = "Aero Glider"
    TORPEDO = "Torpedo"
    DRAGONETTI = "Dragonetti"
    PHANTOM = "Phantom"

class VehicleInfo(NamedTuple):
    vehicle_type: VehicleType
    size: VehicleSize
    speed: int
    weight: int
    acceleration: int
    handling: int
    drift: int
    off_road: int
    mini_turbo: int
    bike_style: BikeStyle | None = None
    unlock_method: str | None = None

VehicleInfoMap = {
    VehicleChoice.STANDARD_KART_S: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=41,
        weight=29,
        acceleration=48,
        handling=48,
        drift=51,
        off_road=40,
        mini_turbo=45,
    ),
    VehicleChoice.STANDARD_BIKE_S: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=39,
        weight=21,
        acceleration=51,
        handling=51,
        drift=54,
        off_road=43,
        mini_turbo=48,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.BABY_BOOSTER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=27,
        weight=27,
        acceleration=56,
        handling=64,
        drift=37,
        off_road=54,
        mini_turbo=59,
    ),
    VehicleChoice.BULLET_BIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=53,
        weight=24,
        acceleration=32,
        handling=35,
        drift=67,
        off_road=29,
        mini_turbo=67,
        bike_style=BikeStyle.HANG_ON,
    ),
    VehicleChoice.CONCERTO: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=55,
        weight=32,
        acceleration=29,
        handling=32,
        drift=64,
        off_road=27,
        mini_turbo=64,
    ),
    VehicleChoice.NANOBIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=25,
        weight=18,
        acceleration=59,
        handling=67,
        drift=40,
        off_road=56,
        mini_turbo=62,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.STANDARD_KART_M: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=46,
        weight=45,
        acceleration=40,
        handling=43,
        drift=45,
        off_road=35,
        mini_turbo=40,
    ),
    VehicleChoice.STANDARD_BIKE_M: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=43,
        weight=37,
        acceleration=43,
        handling=45,
        drift=48,
        off_road=37,
        mini_turbo=43,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.NOSTALGIA_1: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=37,
        weight=43,
        acceleration=59,
        handling=54,
        drift=54,
        off_road=40,
        mini_turbo=51,
    ),
    VehicleChoice.MACH_BIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=55,
        weight=37,
        acceleration=24,
        handling=32,
        drift=62,
        off_road=27,
        mini_turbo=62,
        bike_style=BikeStyle.HANG_ON,
    ),
    VehicleChoice.WILD_WING: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=57,
        weight=51,
        acceleration=21,
        handling=29,
        drift=59,
        off_road=24,
        mini_turbo=59,
    ),
    VehicleChoice.BON_BON: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=32,
        weight=32,
        acceleration=54,
        handling=62,
        drift=35,
        off_road=51,
        mini_turbo=56,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.STANDARD_KART_L: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=48,
        weight=59,
        acceleration=37,
        handling=40,
        drift=40,
        off_road=35,
        mini_turbo=35,
    ),
    VehicleChoice.STANDARD_BIKE_L: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=46,
        weight=54,
        acceleration=40,
        handling=43,
        drift=43,
        off_road=37,
        mini_turbo=37,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.OFFROADER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=39,
        weight=64,
        acceleration=48,
        handling=54,
        drift=18,
        off_road=43,
        mini_turbo=45,
    ),
    VehicleChoice.BOWSER_BIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=60,
        weight=54,
        acceleration=18,
        handling=24,
        drift=51,
        off_road=21,
        mini_turbo=51,
        bike_style=BikeStyle.HANG_ON,
    ),
    VehicleChoice.FLAME_FLYER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=62,
        weight=59,
        acceleration=16,
        handling=21,
        drift=48,
        off_road=18,
        mini_turbo=48,
    ),
    VehicleChoice.WARIO_BIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=37,
        weight=59,
        acceleration=51,
        handling=56,
        drift=21,
        off_road=45,
        mini_turbo=48,
        bike_style=BikeStyle.DRIFT,
    ),
    VehicleChoice.CHEEP_CHARGER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=34,
        weight=24,
        acceleration=64,
        handling=56,
        drift=59,
        off_road=45,
        mini_turbo=54,
        unlock_method="Rank 1 Star in all 50cc Retro Grand Prix Cups / Play 1,800 races",
    ),
    VehicleChoice.QUACKER: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=32,
        weight=17,
        acceleration=67,
        handling=60,
        drift=62,
        off_road=48,
        mini_turbo=57,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Win the 150cc Star Cup / Play 2,400 races",
    ),
    VehicleChoice.RALLY_ROMPER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=46,
        weight=35,
        acceleration=43,
        handling=43,
        drift=29,
        off_road=64,
        mini_turbo=40,
        unlock_method=(
            "Unlock an Expert Staff Ghost Data record in Time Trials / "
            "Play 1,200 races / Win 50 WFC races"
        ),
    ),
    VehicleChoice.MAGIKRUISER: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=43,
        weight=24,
        acceleration=45,
        handling=45,
        drift=32,
        off_road=67,
        mini_turbo=43,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Play Time Trials on 8 different courses / Play 900 races",
    ),
    VehicleChoice.BLUE_FALCON: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.SMALL,
        speed=60,
        weight=29,
        acceleration=35,
        handling=29,
        drift=43,
        off_road=24,
        mini_turbo=29,
        unlock_method="Win the Mirror Lightning Cup / Play 4,200 races",
    ),
    VehicleChoice.BUBBLE_BIKE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.SMALL,
        speed=48,
        weight=27,
        acceleration=40,
        handling=40,
        drift=45,
        off_road=35,
        mini_turbo=37,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Win the Mirror Leaf Cup / Play 3,900 races",
    ),
    VehicleChoice.TURBO_BLOOPER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=50,
        weight=40,
        acceleration=35,
        handling=37,
        drift=21,
        off_road=54,
        mini_turbo=35,
        unlock_method="Win the 50cc Leaf Cup / Play 300 races",
    ),
    VehicleChoice.RAPIDE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=41,
        weight=35,
        acceleration=45,
        handling=51,
        drift=29,
        off_road=62,
        mini_turbo=45,
        bike_style=BikeStyle.DRIFT,
        unlock_method="Win the 100cc Lightning Cup / Play 2,100 races",
    ),
    VehicleChoice.ROYAL_RACER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=34,
        weight=45,
        acceleration=51,
        handling=59,
        drift=32,
        off_road=48,
        mini_turbo=54,
        unlock_method="Win the 150cc Leaf Cup / Play 2,700 races",
    ),
    VehicleChoice.NITROCYCLE: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=62,
        weight=40,
        acceleration=29,
        handling=27,
        drift=40,
        off_road=24,
        mini_turbo=27,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Rank 1 Star in all 100cc Wii Grand Prix Cups / Play 3,300 races",
    ),
    VehicleChoice.B_DASHER_MK_2: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.MEDIUM,
        speed=64,
        weight=48,
        acceleration=27,
        handling=24,
        drift=37,
        off_road=21,
        mini_turbo=24,
        unlock_method=(
            "Unlock 24 Expert Staff Ghost Data Records in Time Trials / "
            "Play 4,650 races / Win 3,000 WFC races"
        ),
    ),
    VehicleChoice.DOLPHIN_DASHER: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.MEDIUM,
        speed=48,
        weight=43,
        acceleration=37,
        handling=40,
        drift=24,
        off_road=56,
        mini_turbo=37,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Win the Mirror Star Cup / Play 3,750 races",
    ),
    VehicleChoice.PIRANHA_PROWLER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=55,
        weight=67,
        acceleration=29,
        handling=35,
        drift=35,
        off_road=29,
        mini_turbo=27,
        unlock_method="Win the 50cc Special Cup / Play 600 races",
    ),
    VehicleChoice.TWINKLE_STAR: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=50,
        weight=48,
        acceleration=29,
        handling=32,
        drift=59,
        off_road=27,
        mini_turbo=59,
        bike_style=BikeStyle.DRIFT,
        unlock_method="Win the 100cc Star Cup / Play 1,500 races",
    ),
    VehicleChoice.AERO_GLIDER: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=69,
        weight=56,
        acceleration=21,
        handling=17,
        drift=27,
        off_road=16,
        mini_turbo=16,
        unlock_method="Rank 1 Star in all 150cc Retro Grand Prix Cups / Play 4,500 races",
    ),
    VehicleChoice.TORPEDO: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=67,
        weight=56,
        acceleration=24,
        handling=18,
        drift=29,
        off_road=18,
        mini_turbo=18,
        bike_style=BikeStyle.HANG_ON,
        unlock_method="Unlock 12 Expert Staff Ghost Data records in Time Trials / Play 3,600 races",
    ),
    VehicleChoice.DRAGONETTI: VehicleInfo(
        vehicle_type=VehicleType.KART,
        size=VehicleSize.LARGE,
        speed=53,
        weight=62,
        acceleration=27,
        handling=29,
        drift=56,
        off_road=24,
        mini_turbo=56,
        unlock_method="Win the 150cc Lightning Cup / Play 3,000 races",
    ),
    VehicleChoice.PHANTOM: VehicleInfo(
        vehicle_type=VehicleType.BIKE,
        size=VehicleSize.LARGE,
        speed=43,
        weight=51,
        acceleration=43,
        handling=48,
        drift=17,
        off_road=56,
        mini_turbo=40,
        bike_style=BikeStyle.DRIFT,
        unlock_method="Win the Mirror Special Cup / Play 4,050 races",
    ),
}

VehicleChoiceGrid = {
    VehicleSize.SMALL: {
        VehicleType.KART: (
            (VehicleChoice.STANDARD_KART_S, VehicleChoice.BABY_BOOSTER, VehicleChoice.CONCERTO),
            (VehicleChoice.CHEEP_CHARGER, VehicleChoice.RALLY_ROMPER, VehicleChoice.BLUE_FALCON),
        ),
        VehicleType.BIKE: (
            (VehicleChoice.STANDARD_BIKE_S, VehicleChoice.BULLET_BIKE, VehicleChoice.NANOBIKE),
            (VehicleChoice.QUACKER, VehicleChoice.MAGIKRUISER, VehicleChoice.BUBBLE_BIKE),
        ),
    },
    VehicleSize.MEDIUM: {
        VehicleType.KART: (
            (VehicleChoice.STANDARD_KART_M, VehicleChoice.NOSTALGIA_1, VehicleChoice.WILD_WING),
            (VehicleChoice.TURBO_BLOOPER, VehicleChoice.ROYAL_RACER, VehicleChoice.B_DASHER_MK_2),
        ),
        VehicleType.BIKE: (
            (VehicleChoice.STANDARD_BIKE_M, VehicleChoice.MACH_BIKE, VehicleChoice.BON_BON),
            (VehicleChoice.RAPIDE, VehicleChoice.NITROCYCLE, VehicleChoice.DOLPHIN_DASHER),
        ),
    },
    VehicleSize.LARGE: {
        VehicleType.KART: (
            (VehicleChoice.STANDARD_KART_L, VehicleChoice.OFFROADER, VehicleChoice.FLAME_FLYER),
            (VehicleChoice.PIRANHA_PROWLER, VehicleChoice.AERO_GLIDER, VehicleChoice.DRAGONETTI),
        ),
        VehicleType.BIKE: (
            (VehicleChoice.STANDARD_BIKE_L, VehicleChoice.BOWSER_BIKE, VehicleChoice.WARIO_BIKE),
            (VehicleChoice.TWINKLE_STAR, VehicleChoice.TORPEDO, VehicleChoice.PHANTOM),
        ),
    },
}

VehiclePositionMap = {
    vehicle_choice: (row, col)
    for size_grid in VehicleChoiceGrid.values()
    for type_grid in size_grid.values()
    for col, vehicle_col in enumerate(type_grid)
    for row, vehicle_choice in enumerate(vehicle_col)
}


class DriftModeChoice(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"


class CupChoice(str, Enum):
    MUSHROOM_CUP = "Mushroom Cup"
    FLOWER_CUP = "Flower Cup"
    STAR_CUP = "Star Cup"
    SPECIAL_CUP = "Special Cup"
    SHELL_CUP = "Shell Cup"
    BANANA_CUP = "Banana Cup"
    LEAF_CUP = "Leaf Cup"
    LIGHTNING_CUP = "Lightning Cup"

CupPositionMap = {
    CupChoice.MUSHROOM_CUP: (0, 0),
    CupChoice.FLOWER_CUP: (0, 1),
    CupChoice.STAR_CUP: (0, 2),
    CupChoice.SPECIAL_CUP: (0, 3),
    CupChoice.SHELL_CUP: (1, 0),
    CupChoice.BANANA_CUP: (1, 1),
    CupChoice.LEAF_CUP: (1, 2),
    CupChoice.LIGHTNING_CUP: (1, 3),
}


ChoiceEnum = TypeVar("ChoiceEnum", bound=Enum)


def _coerce_choice(
    choice: str | ChoiceEnum,
    enum_type: type[ChoiceEnum]
) -> ChoiceEnum:
    if isinstance(choice, enum_type):
        return choice
    try:
        return enum_type(choice)
    except ValueError as exc:
        valid_choices = ", ".join(item.value for item in enum_type)
        raise ValueError(
            f"{choice} is invalid. Valid choices: {valid_choices}"
        ) from exc


def _get_character_size(character_choice: CharacterChoice) -> VehicleSize:
    row, _ = CharacterPositionMap[character_choice]
    if row <= 1:
        return VehicleSize.SMALL
    if row <= 3:
        return VehicleSize.MEDIUM
    if row <= 5:
        return VehicleSize.LARGE
    raise ValueError(
        "Mii character size cannot be inferred from row index. "
        "Use a non-Mii character or extend this macro with explicit Mii size handling."
    )


def _get_allowed_vehicle_types(class_choice: ClassChoice) -> tuple[VehicleType, ...]:
    if class_choice is ClassChoice.CC_50:
        return (VehicleType.KART,)
    if class_choice is ClassChoice.CC_100:
        return (VehicleType.BIKE,)
    if class_choice in (ClassChoice.CC_150, ClassChoice.MIRROR):
        return (VehicleType.KART, VehicleType.BIKE)
    raise ValueError(f"Unsupported class choice: {class_choice.value}")


def get_available_vehicle_choices(
    class_choice: ClassChoice | str,
    character_choice: CharacterChoice | str,
) -> list[VehicleChoice]:
    selected_class = _coerce_choice(class_choice, ClassChoice)
    selected_character = _coerce_choice(character_choice, CharacterChoice)

    target_size = _get_character_size(selected_character)
    allowed_types = _get_allowed_vehicle_types(selected_class)

    available_choices: list[VehicleChoice] = []
    for vehicle_type in allowed_types:
        for vehicle_row in VehicleChoiceGrid[target_size][vehicle_type]:
            available_choices.extend(vehicle_row)

    return available_choices


# Todo: implement enter_main_menu to work more precisely
def enter_main_menu(
    env: KartInstance,
    step_delay_sec: float = 7.0,
    post_action_delay_sec: float = 7.0,
) -> None:
    REPEATS = 70
    
    time.sleep(10.0)
    
    for _ in range(8):
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    
    print("[Macro] Main menu entrance done")
    time.sleep(post_action_delay_sec)

def select_main_menu(
    env: KartInstance,
    choice: MainMenuChoice | str,
    step_delay_sec: float = 0.2,
    post_action_delay_sec: float = 7.0,
) -> None:
    selected_choice = _coerce_choice(choice, MainMenuChoice)

    if selected_choice is MainMenuChoice.SINGLE_PLAYER:
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    else:
        raise NotImplementedError(
            f"{selected_choice.value} is not implemented."
        )
    
    print("[Macro] Main menu selection done")
    time.sleep(post_action_delay_sec)

def select_single_player(
    env: KartInstance,
    choice: SinglePlayerChoice | str,
    step_delay_sec: float = 0.2,
    post_action_delay_sec: float = 7.0,
) -> None:
    selected_choice = _coerce_choice(choice, SinglePlayerChoice)

    if selected_choice is SinglePlayerChoice.GRAND_PRIX:
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    else:
        raise NotImplementedError(
            f"{selected_choice.value} is not implemented."
        )
    
    print("[Macro] Single player selection done")
    time.sleep(post_action_delay_sec)

def select_class(
    env: KartInstance,
    choice: ClassChoice | str,
    step_delay_sec: float = 0.2,
    post_action_delay_sec: float = 7.0,
) -> None:
    selected_choice = _coerce_choice(choice, ClassChoice)

    if selected_choice is ClassChoice.CC_50:
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    elif selected_choice is ClassChoice.CC_100:
        env.click_button(button=Button.D_DOWN.value, duration=0.1)
        time.sleep(step_delay_sec)
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    elif selected_choice is ClassChoice.CC_150:
        for _ in range(2):
            env.click_button(button=Button.D_DOWN.value, duration=0.1)
            time.sleep(step_delay_sec)
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    elif selected_choice is ClassChoice.MIRROR:
        for _ in range(3):
            env.click_button(button=Button.D_DOWN.value, duration=0.1)
            time.sleep(step_delay_sec)
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    
    print("[Macro] Class selection done")
    time.sleep(post_action_delay_sec)


def select_character(
    env: KartInstance,
    choice: CharacterChoice | str,
    step_delay_sec: float = 0.5,
    post_action_delay_sec: float = 9.0,
) -> None:
    selected_choice = _coerce_choice(choice, CharacterChoice)
    
    start_row, start_col = CharacterPositionMap[CharacterChoice.MARIO]
    target_row, target_col = CharacterPositionMap[selected_choice]
    row_shift = target_row - start_row
    col_shift = target_col - start_col

    
    vertical_move_key = Button.D_UP.value if row_shift <= 0 else Button.D_DOWN.value
    for _ in range(abs(row_shift)):
        env.click_button(button=vertical_move_key, duration=0.1)
        time.sleep(step_delay_sec)
    
    horizontal_move_key = Button.D_LEFT.value if col_shift <= 0 else Button.D_RIGHT.value
    for _ in range(abs(col_shift)):
        env.click_button(button=horizontal_move_key, duration=0.1)
        time.sleep(step_delay_sec)
        
    env.click_button(button=Button.A.value, duration=0.1)
    
    print("[Macro] Character selection done")
    time.sleep(post_action_delay_sec)


def select_vehicle(
    env: KartInstance,
    class_choice: ClassChoice | str,
    character_choice: CharacterChoice | str,
    vehicle_choice: VehicleChoice | str,
    step_delay_sec: float = 0.5,
    post_action_delay_sec: float = 7.0,
) -> None:
    selected_class = _coerce_choice(class_choice, ClassChoice)
    selected_character = _coerce_choice(character_choice, CharacterChoice)
    selected_vehicle = _coerce_choice(vehicle_choice, VehicleChoice)

    selected_vehicle_info = VehicleInfoMap[selected_vehicle]
    target_size = _get_character_size(selected_character)
    allowed_types = _get_allowed_vehicle_types(selected_class)

    if selected_vehicle_info.size is not target_size:
        raise ValueError(
            f"{selected_vehicle.value} is {selected_vehicle_info.size.value} size, "
            f"but {selected_character.value} is {target_size.value} size."
        )
    if selected_vehicle_info.vehicle_type not in allowed_types:
        allowed_text = ", ".join(vehicle_type.value for vehicle_type in allowed_types)
        raise ValueError(
            f"{selected_vehicle.value} is {selected_vehicle_info.vehicle_type.value}, "
            f"but {selected_class.value} allows only: {allowed_text}."
        )

    if len(allowed_types) == 2 and selected_vehicle_info.vehicle_type is VehicleType.BIKE:
        env.click_button(button=Button.D_RIGHT.value, duration=0.1)
        time.sleep(step_delay_sec)

    start_row, start_col = (0, 0)
    target_row, target_col = VehiclePositionMap[selected_vehicle]
    row_shift = target_row - start_row
    col_shift = target_col - start_col

    vertical_move_key = Button.D_UP.value if row_shift <= 0 else Button.D_DOWN.value
    for _ in range(abs(row_shift)):
        env.click_button(button=vertical_move_key, duration=0.1)
        time.sleep(step_delay_sec)

    horizontal_move_key = Button.D_LEFT.value if col_shift <= 0 else Button.D_RIGHT.value
    for _ in range(abs(col_shift)):
        env.click_button(button=horizontal_move_key, duration=0.1)
        time.sleep(step_delay_sec)

    env.click_button(button=Button.A.value, duration=0.1)

    print("[Macro] Vehicle selection done")
    time.sleep(post_action_delay_sec)


def select_drift_mode(
    env: KartInstance,
    choice: DriftModeChoice | str,
    step_delay_sec: float = 0.2,
    post_action_delay_sec: float = 7.0,
) -> None:
    selected_choice = _coerce_choice(choice, DriftModeChoice)
    
    if selected_choice is DriftModeChoice.AUTOMATIC:
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    elif selected_choice is DriftModeChoice.MANUAL:
        env.click_button(button=Button.D_DOWN.value, duration=0.1)
        time.sleep(step_delay_sec)
        env.click_button(button=Button.A.value, duration=0.1)
        time.sleep(step_delay_sec)
    
    print("[Macro] Drift mode selection done")
    time.sleep(post_action_delay_sec)


def select_cup(
    env: KartInstance,
    choice: CupChoice | str,
    step_delay_sec: float = 0.2,
    post_action_delay_sec: float = 3.0,
) -> None:
    selected_choice = _coerce_choice(choice, CupChoice)

    start_row, start_col = CupPositionMap[CupChoice.MUSHROOM_CUP]
    target_row, target_col = CupPositionMap[selected_choice]
    row_shift = target_row - start_row
    col_shift = target_col - start_col
    

    vertical_move_key = Button.D_UP.value if row_shift <= 0 else Button.D_DOWN.value
    for _ in range(abs(row_shift)):
        env.click_button(button=vertical_move_key, duration=0.1)
        time.sleep(step_delay_sec)
    
    horizontal_move_key = Button.D_LEFT.value if col_shift <= 0 else Button.D_RIGHT.value
    for _ in range(abs(col_shift)):
        env.click_button(button=horizontal_move_key, duration=0.1)
        time.sleep(step_delay_sec)
        
    env.click_button(button=Button.A.value, duration=0.1)
    time.sleep(post_action_delay_sec)
        
    env.click_button(button=Button.A.value, duration=0.1)
    
    
    print("[Macro] Cup selection done")
    time.sleep(post_action_delay_sec)