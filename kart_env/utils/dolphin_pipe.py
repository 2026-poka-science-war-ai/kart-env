import os
from enum import Enum
import pathlib


class Button(str, Enum):
    A = "A"
    B = "B"
    X = "X"
    Y = "Y"
    Z = "Z"
    START = "START"
    L = "L"
    R = "R"
    D_UP = "D_UP"
    D_DOWN = "D_DOWN"
    D_LEFT = "D_LEFT"
    D_RIGHT = "D_RIGHT"


class Stick(str, Enum):
    MAIN = "MAIN"
    C = "C"


class DolphinPipe:

    def __init__(self, env_id: int):
        self.env_id = env_id
        pipe_dir = pathlib.Path(f"/kart_env/users/{env_id}/Pipes")
        self.pipe_path = pipe_dir / "pipe1"
        pipe_dir.mkdir(parents=True, exist_ok=True)
        if not self.pipe_path.exists():
            os.mkfifo(self.pipe_path)
        self.pipe = open(self.pipe_path, "w", buffering=1)

    def close(self):
        self.pipe.close()

    def press(self, button: Button):
        self.pipe.write(f"PRESS {button}\n")

    def release(self, button: Button):
        self.pipe.write(f"RELEASE {button}\n")

    def set(self, stick: Stick, x: float, y: float):
        assert 0 <= x <= 1 and 0 <= y <= 1, "Stick values must be between 0 and 1"
        self.pipe.write(f"SET {stick} {x} {y}\n")
