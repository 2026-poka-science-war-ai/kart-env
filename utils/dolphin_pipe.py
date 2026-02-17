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
        
        base_dir = pathlib.Path(os.path.abspath("./users/fixed_player"))
        pipe_dir = base_dir / "Pipes"
        
        self.pipe_path = pipe_dir / "pipe"
        
        pipe_dir.mkdir(parents=True, exist_ok=True)
        
        if self.pipe_path.exists():
            try:
                os.unlink(self.pipe_path)
            except OSError:
                pass

        os.mkfifo(self.pipe_path)
        
        print(f"[Pipe] 파이프 연결 대기 중... (경로: {self.pipe_path})")
        self.pipe = open(self.pipe_path, "w", buffering=1)
        print("[Pipe] 파이프 연결 성공!")

    def close(self):
        self.pipe.close()

    def press(self, button: Button):
        self.pipe.write(f"PRESS {button}\n")

    def release(self, button: Button):
        self.pipe.write(f"RELEASE {button}\n")

    def set(self, stick: Stick, x: float, y: float):
        assert 0 <= x <= 1 and 0 <= y <= 1, "Stick values must be between 0 and 1"
        self.pipe.write(f"SET {stick} {x} {y}\n")
