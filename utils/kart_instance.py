import os
import subprocess
import atexit
import time
import shutil
import pathlib
from utils.kart_mem import KartMem
from utils.dolphin_pipe import DolphinPipe, Button

DOLPHIN_BIN = os.path.abspath("./squashfs-root/AppRun")
ISO_PATH = os.path.abspath("./MarioKartWii.iso")

class KartInstance:
    def __init__(self, env_id: int, hard_reset: bool = False):
        self.env_id = env_id
        
        self.user_dir = pathlib.Path(os.path.abspath("./users/fixed_player"))

        self.processes: list[subprocess.Popen] = []

        self._run_env()
        
        atexit.register(self.close)
        
        self.pipe = DolphinPipe(env_id)

    def _run_env(self):
        xvfb_command = ["Xvfb", f":{self.env_id}", "-screen", "0", "640x480x24"]
        self.processes.append(subprocess.Popen(xvfb_command))
        
        wait_count = 0
        while not os.path.exists(f"/tmp/.X11-unix/X{self.env_id}"):
            time.sleep(0.1)
            wait_count += 1
            if wait_count > 50: 
                print(f"[Instance] Xvfb 실행이 지연되고 있습니다 (Display :{self.env_id})")
                break

        dolphin_command = [
            DOLPHIN_BIN,
            "--batch",
            f"--user={self.user_dir}",
            "-e",
            ISO_PATH,
            "--video_backend=Software" 
        ]
        
        print(f"[Instance] Dolphin 실행: {' '.join(str(x) for x in dolphin_command)}")

        dolphin_env = os.environ.copy()
        dolphin_env["DISPLAY"] = f":{self.env_id}"
        
        dolphin_process = subprocess.Popen(dolphin_command, env=dolphin_env)
        self.processes.append(dolphin_process)
        
        self.mem = KartMem(dolphin_process.pid)

    def close(self):
        try:
            if hasattr(self, 'pipe'):
                self.pipe.close()
            
            for proc in reversed(self.processes):
                if proc.poll() is None: 
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill() 
        except Exception as e:
            print(f"[Instance] 종료 중 오류 발생: {e}")

    def click_button(self, button: Button, duration: float = 0.1):
        self.pipe.press(button)
        time.sleep(duration)
        self.pipe.release(button)
