from typing import Final, TypedDict

# Network / path constants
VNC_BASE: Final[int] = 5900
NOVNC_BASE: Final[int] = 6080
DOLPHIN_PATH: Final[str] = "/usr/local/bin/dolphin-emu"
SOCK_BASE: Final[int] = 9999

# Controller layout
GC_BUTTONS: Final[tuple[str, ...]] = (
    "A", "B", "X", "Y", "Z", "Start", "Up", "Down", "Left", "Right", "L", "R",
)
AGENT_STRUCT_FORMAT: Final[str] = "<H6f"


class GcAction(TypedDict, total=False):
    A: int
    B: int
    X: int
    Y: int
    Z: int
    Start: int
    Up: int
    Down: int
    Left: int
    Right: int
    L: int
    R: int
    StickX: float
    StickY: float
    CStickX: float
    CStickY: float
    TriggerLeft: float
    TriggerRight: float


NEUTRAL_ACTION: Final[GcAction] = {
    "A": 0,
    "B": 0,
    "X": 0,
    "Y": 0,
    "Z": 0,
    "Start": 0,
    "Up": 0,
    "Down": 0,
    "Left": 0,
    "Right": 0,
    "L": 0,
    "R": 0,
    "StickX": 0.0,
    "StickY": 0.0,
    "CStickX": 0.0,
    "CStickY": 0.0,
    "TriggerLeft": 0.0,
    "TriggerRight": 0.0,
}
