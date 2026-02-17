import subprocess
import os
import atexit
import time
import shutil
import pathlib
from utils.kart_mem import KartMem
from utils.dolphin_pipe import DolphinPipe, Button

SETTINGS_DIR = "/kart_env/dolphin_settings/"
DOLPHIN_BIN = "/usr/local/bin/dolphin-emu"
ISO_PATH = "/kart_env/MarioKartWii.iso"


class KartInstance:
    def __init__(self, env_id: int, hard_reset: bool = False):
        self.env_id = env_id
        self.vnc_port = 5900 + env_id
        self.novnc_port = 6080 + env_id
        self.user_dir = pathlib.Path(f"/kart_env/users/{env_id}/")
        if hard_reset:
            shutil.rmtree(self.user_dir, ignore_errors=True)
        if not self.user_dir.exists():
            shutil.copytree(SETTINGS_DIR, self.user_dir)
        self.processes: list[subprocess.Popen] = []
        self._run_env()
        atexit.register(self.close)
        self.pipe = DolphinPipe(env_id)

    def _run_env(self):
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
            DOLPHIN_BIN,
            "--batch",
            f"--user={self.user_dir}",
            "-e",
            ISO_PATH,
        ]
        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        dolphin_process = subprocess.Popen(dolphin_command, env=dolphin_env)
        self.processes.append(dolphin_process)
        self.mem = KartMem(dolphin_process.pid)

    def close(self):
        try:
            self.pipe.close()
            for proc in reversed(self.processes):
                proc.terminate()
                proc.wait()
        except Exception:
            pass

    def click_button(self, button: Button, duration: float = 0.1):
        self.pipe.press(button)
        time.sleep(duration)
        self.pipe.release(button)
